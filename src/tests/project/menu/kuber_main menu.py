from datetime import datetime
import logging
import os
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

WHITEOUT_TEXTS = ["죄송합니다", "페이지를 찾을 수 없습니다.", "Bad Gate", "OOOPS"]

# 로깅 설정
log_filename = f"KUBER_WHITEOUT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_filename)
    ]
)


def capture_screenshot(page, filename, save_path):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    screenshot_name = f"{filename}_{timestamp}.png"
    filepath = os.path.join(save_path, screenshot_name)
    page.screenshot(path=filepath)
    logging.error(f"스크린샷이 저장되었습니다: {os.path.abspath(filepath)}")
    return filepath


def go_back_and_capture_screenshot(page, filename, save_path):
    page.go_back()
    page.wait_for_load_state('networkidle')
    logging.error(f"뒤로가기 후 스크린샷 저장됨: {filename}")
    return capture_screenshot(page, filename, save_path)


def get_page_content_with_timeout(page, timeout):
    start_time = time.time()
    while True:
        try:
            # 페이지 콘텐츠를 가져오는 시도
            logging.info("페이지 컨텐츠를 가져오는 중...")
            page_content = page.content()
            return page_content
        except PlaywrightTimeoutError:
            # 타임아웃 발생 시
            logging.warning(f"페이지 컨텐츠 불러오기 재시도 중,,,")
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                raise PlaywrightTimeoutError("페이지 콘텐츠를 가져오는 도중 타임아웃이 발생했습니다.")
            # 잠시 대기 후 재시도
            time.sleep(1)
        

def check_for_whiteout(page, button_text, save_path):
    try:
        page.wait_for_load_state('networkidle', timeout=10000)  

        #logging.info("페이지 컨텐츠 가져오기 시도 중...")        
        page_content = get_page_content_with_timeout(page, timeout=10000)  # 10초 동안 대기
        logging.info("페이지 컨텐츠 가져오기 완료")

        found_text = None
        for text in WHITEOUT_TEXTS:
            if text in page_content:
                found_text = text
                break
        
        if found_text:
            logging.error(f"화이트아웃 화면 감지: '{found_text}' 특정 텍스트 발견")
            screenshot_path = capture_screenshot(page, f"whiteout_screen_{found_text}", save_path)
            
            # 화이트 아웃 발생 원인 버튼의 텍스트를 출력
            button_element = page.query_selector(f"//*[text()='{button_text}']")
            if button_element:
                element_html = page.evaluate('(element) => element.outerHTML', button_element)
                logging.error(f"화이트아웃을 발생시킨 버튼 텍스트: {button_text}")
                logging.error(f"화이트아웃을 발생시킨 버튼 HTML:\n{element_html}")
            else:
                logging.warning(f"화이트아웃을 발생시킨 버튼 '{button_text}'을(를) 찾을 수 없습니다.")
            
            go_back_and_capture_screenshot(page, f"back_screen_{found_text}", save_path)
            
        else:
            logging.info("정상 페이지로 보입니다.")
    except PlaywrightTimeoutError:
        screenshot_path = capture_screenshot(page, "timeout_screen", save_path)
        logging.error(f"페이지를 로드하는 동안 타임아웃이 발생했습니다: {screenshot_path}")


def extract_and_resolve_all_links(page, display_controls):
    
    resolved_links = []  # 링크와 절대 URL을 저장할 리스트

    for display in display_controls:
        inner_html = display.inner_html()  # 각 DisplayControl 요소의 HTML을 가져옴
        soup = BeautifulSoup(inner_html, 'html.parser')
        links = soup.find_all('a', href=True)
        
        current_url = page.url  # 현재 페이지의 URL을 가져옴
        
        for link in links:
            href = link['href']
            absolute_url = urljoin(current_url, href)  # 절대 URL로 변환
            resolved_links.append((href, absolute_url))
    
    return resolved_links  # 모든 링크의 절대 URL 리스트 반환


def run(playwright):
    save_path = os.getenv("WHITEOUT_SCREEN_PATH", "./whiteout_screen")

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    try:
        # Chromium, Firefox, WebKit을 동시에 시작합니다.
        for browser_type in [playwright.chromium, playwright.firefox, playwright.webkit]:
            logging.info(f"{browser_type.name} 브라우저 시작 중...")
            browser = browser_type.launch(headless=False)
            context = browser.new_context(storage_state={})
            page = context.new_page()

            # 페이지 전체에 대한 기본 타임아웃 설정
            context.set_default_timeout(120000)  # 120초로 설정

            logging.info(f"{browser_type.name} - https://www.whatap.io/ 페이지로 이동 중...")
            page.goto("https://www.whatap.io/")

            # 화이트 아웃 확인
            page.wait_for_load_state('networkidle')
            check_for_whiteout(page, "https://whatap.io/", save_path)

            logging.info(f"{browser_type.name} - 로그인 페이지로 이동 중...")
            page.get_by_role("link", name="로그인").click()

            # 화이트 아웃 확인
            page.wait_for_load_state('networkidle')
            check_for_whiteout(page, "로그인 화면", save_path)

            logging.info(f"{browser_type.name} - 이메일 및 비밀번호 입력 중...")
            page.get_by_placeholder("Company Email").fill("hjnoh.automation@gmail.com")
            page.get_by_placeholder("Password").fill("shguswn980512-")  
            logging.info(f"{browser_type.name} - 로그인 버튼 클릭 중...")
            page.locator('#btn_login').click()

            # 화이트 아웃 확인
            page.wait_for_load_state('networkidle')
            check_for_whiteout(page, "로그인 버튼 누름", save_path)

            logging.info(f"{browser_type.name} - 쿠버 프로젝트 선택 중...")
            page.goto("https://service.whatap.io/v2/project/cpm/33194/containerMap")

            page.wait_for_load_state('networkidle') 

            # 화이트 아웃 확인
            
            check_for_whiteout(page, "쿠버네티스 메인 화면", save_path)
            

            # 왼쪽 사이드 메뉴 접속하기
            menu_wrap = page.query_selector('div.Menustyles__MenuWrap-hRfo.hmTPnA')

            display_controls = []

            if menu_wrap:

                # 내부에 있는 DisplayControl 찾기
                display_controls = menu_wrap.query_selector_all('div.Menustyles__DisplayControl-etKSwa')

            else:
                logging.warning("MenuWrap 요소를 찾을 수 없습니다.")

            page.wait_for_load_state('networkidle')

            resolved_links = extract_and_resolve_all_links(page, display_controls)

            logging.info("전체 절대 URL 리스트:")
            for href, absolute_url in resolved_links:
                logging.info(f"링크: {href} | 절대 URL: {absolute_url}")

            # 절대 URL 리스트에서 하나씩 클릭
            
            for _, absolute_url in resolved_links:
                attempt = 0
                max_attempts = 5  # 최대 시도 횟수 설정
                while attempt < max_attempts:
                    try:
                        attempt += 1
                        logging.info(f"시도 {attempt}: 클릭할 URL: {absolute_url}")
                        page.goto(absolute_url)
                        #logging.info("페이지 로드 시도 중...")
                        page.wait_for_load_state('networkidle', timeout=20000)  # 'networkidle' 대신 다른 로드 상태 사용 고려
                        #logging.info("페이지 로드 완료")
                        check_for_whiteout(page, f"링크 클릭: {absolute_url}", save_path)
                        break  

                    except PlaywrightTimeoutError:
                        logging.warning(f"{attempt * 10}초 동안 페이지가 로드되지 않았습니다. {absolute_url} 재시도 중...")
                        page.wait_for_timeout(10000)  # 10초 대기
                    
                    except Exception as e:
                        logging.error(f"페이지 로드 중 예외 발생: {str(e)}")
                        break  # 예외 발생 시 while 루프 종료

                if attempt == max_attempts:
                    logging.error(f"최대 시도 횟수({max_attempts}) 초과: {absolute_url} 링크 접속을 실패했습니다.")
            
            #사이트맵 메뉴 접속
            page.locator("button:nth-child(3)").first.click()

            sitemap_menu_wrap = page.query_selector('div.SitemapLgStyles__Body-deZNSA.gdxkRY')

            MenuUl_sitemaps = []

            if sitemap_menu_wrap:

                MenuUl_sitemaps = sitemap_menu_wrap.query_selector_all('div.SitemapLgStyles__MenuUl-jezJaq.iRxdMi')
            
            else:
                logging.warning("sitemap_menu_wrap 요소를 찾을 수 없습니다.")

            page.wait_for_load_state('networkidle')

            resolved_links = extract_and_resolve_all_links(page, MenuUl_sitemaps)

            logging.info("site_map 전체 절대 URL 리스트:")
            for href, absolute_url in resolved_links:
                logging.info(f"링크: {href} | 절대 URL: {absolute_url}")

            for _, absolute_url in resolved_links:
                attempt = 0
                max_attempts = 5  # 최대 시도 횟수 설정
                while attempt < max_attempts:
                    attempt += 1
                    try:
                        
                        logging.info(f"시도 {attempt}: 클릭할 URL: {absolute_url}")
                        page.goto(absolute_url)
                        #logging.info("페이지 로드 시도 중...")
                        page.wait_for_load_state('networkidle', timeout=20000)  # 'networkidle' 대신 다른 로드 상태 사용 고려
                        #page.wait_for_timeout(5000)
                        #logging.info("페이지 로드 완료")
                        check_for_whiteout(page, f"링크 클릭: {absolute_url}", save_path)
                        #logging.info("화이트아웃 확인 완료")
                        break  

                    except PlaywrightTimeoutError:
                        logging.warning(f"{attempt * 10}초 동안 페이지가 로드되지 않았습니다. {absolute_url} 재시도 중...")
                        page.wait_for_timeout(10000)  # 10초 대기
                    
                    except Exception as e:
                        logging.error(f"페이지 로드 중 예외 발생: {str(e)}")
                        break  # 예외 발생 시 while 루프 종료

                if attempt == max_attempts:
                    logging.error(f"최대 시도 횟수({max_attempts}) 초과: {absolute_url} 링크 접속을 실패했습니다.")

            context.close()
            browser.close()

    except Exception as e:
        logging.error(f"오류 발생: {str(e)}")

    finally: 
                    
        logging.info(f"{browser_type.name}_Test complete")  # 각 브라우저 작업 완료 메시지 출력
        
with sync_playwright() as playwright:

    run(playwright)
