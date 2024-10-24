from datetime import datetime
import logging
import os
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from useraccount_actions import login

WHITEOUT_TEXTS = ["죄송합니다", "페이지를 찾을 수 없습니다.", "Bad Gate", "OOOPS"]

# 로깅 설정 파일 위치 따로 설정하기
log_save_path = os.getenv("LOG_FILE_PATH", "./reports/logs/main_menu")  
if not os.path.exists(log_save_path):
    os.makedirs(log_save_path)


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
    save_path = os.getenv("WHITEOUT_SCREEN_PATH", "./reports/screeen_shot/kuber_whiteout")

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    global browser_type
    all_results = {}

    try:
        # Chromium, Firefox, WebKit을 동시에 시작합니다.
        for browser_type in [playwright.chromium, playwright.firefox, playwright.webkit]:
            logging.info(f"{browser_type.name} 브라우저 시작 중...")
            test_results = []
            browser = browser_type.launch(headless=False)
            context = browser.new_context(
                locale="ko-KR",  # 브라우저 언어를 한국어로 설정
                storage_state={}
            )

            # 페이지 전체에 대한 기본 타임아웃 설정
            context.set_default_timeout(120000)  # 120초로 설정
            page = context.new_page()

            email_text = "hjnoh@whatap.io"
            password = "shguswn980512-"

            login (
                page=page,
                email=email_text,
                password=password,
                test_results=test_results
            )

            # 화이트 아웃 확인
            page.wait_for_load_state('networkidle')
            check_for_whiteout(page, "로그인 이후 화면", save_path)

            project_type = "cpm"
            project_id = 33194

            project_url = f"https://service.whatap.io/v2/project/{project_type}/{project_id}"
            page.goto(project_url)

            # 화이트 아웃 확인
            page.wait_for_load_state('networkidle') 
            check_for_whiteout(page, f"{project_type} {project_id} 메인 화면", save_path)
            

            # 왼쪽 사이드 메뉴 접속하기
            menu_wrap = page.query_selector('div.Menustyles__MenuWrap-hRfo.hmTPnA')

            #display_controls = []

            # 하위 메뉴를 UI에 표출하기 위해 상위 메뉴 클릭해서 오픈하기
            if menu_wrap:
                # 상위 메뉴 클래스를 가진 요소 찾기
                parent_elements = menu_wrap.query_selector_all('div.Menustyles__MenuItemWrapCommon-cHqrwY.Menustyles__Parent-XgDRT')

                if parent_elements:
                    for element in parent_elements:
                        try:
                            logging.info(f"상위 메뉴 클릭하여 하위 메뉴 오픈 중") 

                            # 요소 클릭
                            element.click()  # 해당 div 요소를 클릭

                            page.wait_for_load_state('networkidle', timeout=20000)  # 페이지가 로드될 때까지 대기
                            logging.info("하위 메뉴 오픈 후 페이지 로드 완료")
                        except Exception as e:
                            logging.error(f"클릭 중 오류 발생: {str(e)}")
                else:
                    logging.error("상위 메뉴 요소를 찾을 수 없습니다.")
            else:
                logging.error("MenuWrap 요소를 찾을 수 없습니다.")

            # 메뉴 화면 진입 후 화이트아웃 확인
            try:
                # MenuWrap 요소가 없는 경우 early return으로 처리
                if not menu_wrap:
                    logging.warning("MenuWrap 요소를 찾을 수 없습니다.")
                    return

                # menu_wrap 내부에서 하위 메뉴에 해당하는 태그 선택
                elements = menu_wrap.locator('a[href^="/v2/project/"]')  # 'locator'로 변경

                if elements.count() == 0:
                    logging.warning("해당하는 링크를 찾을 수 없습니다.")
                    return

                # 하위 메뉴 클릭 및 화이트아웃 검증
                for i in range(elements.count()):
                    element = elements.nth(i)
                    href_value = element.get_attribute('href')
                    logging.info(f"선택할 버튼의 href 속성 값: {href_value}")

                    try:
                        # <a> 태그 내부의 버튼 클릭
                        button = element.locator('div')  # 'locator'로 내부 요소 접근
                        logging.info(f"선택한 버튼: {button}")

                        button.click()  # 해당 버튼 클릭

                        logging.info(f"{href_value} 메뉴로 이동 중...")

                        # 페이지 로드 대기
                        page.wait_for_load_state('networkidle', timeout=20000)

                        # 화이트 아웃 감지
                        logging.info("화이트 아웃 발생 확인 중")
                        whiteout_detected = check_for_whiteout(page, f"{href_value} 버튼 클릭", save_path)

                        # 화이트 아웃 감지 여부 검증
                        assert not whiteout_detected, f"화이트 아웃이 감지되었습니다: {href_value}"
                        logging.info(f"{href_value} 검증 완료: 화이트 아웃 없음 (성공)")

                    except AssertionError as e:
                        # Assertion 실패 시 로그와 결과 기록, 코드 중단 없이 다음 항목으로 넘어감
                        logging.error(f"검증 실패: {str(e)}")
                        log_result(False, str(e))
                        test_results.append(str(e))

                    except Exception as e:
                        # 기타 예외 처리, 코드 중단 없이 다음 항목으로 넘어감
                        logging.error(f"{href_value} 클릭 중 오류 발생: {str(e)}")
                        log_result(False, f"{href_value} 클릭 중 예외 발생: {str(e)}")
                        test_results.append(f"{href_value} 클릭 중 예외 발생: {str(e)}")

            except Exception as e:
                logging.error(f"전체 실행 중 오류 발생: {str(e)}")



            '''if menu_wrap:

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
                    logging.error(f"최대 시도 횟수({max_attempts}) 초과: {absolute_url} 링크 접속을 실패했습니다.")'''
            
            #사이트맵 메뉴 접속
            page.locator("button:nth-child(3)").first.click()

            sitemap_menu_wrap = page.query_selector('div.SitemapLgStyles__Body-deZNSA.gdxkRY')

            # 사이트맵 - 메뉴 화면 진입 후 화이트아웃 확인
            try:
                if not sitemap_menu_wrap:
                    logging.warning("Sitemap 메뉴 요소를 찾을 수 없습니다.")
                    return

                # sitemap_menu_wrap 내부에서 <a> 태그 선택 (id가 'SitemapLg_'로 시작하는 모든 링크 선택)
                elements = sitemap_menu_wrap.locator('a[id^="SitemapLg"][href^="/v2/project/"]')  # 'id'와 'href' 조건 모두 사용

                if elements.count() == 0:
                    logging.warning("해당하는 링크를 찾을 수 없습니다.")
                    return

                # 하위 메뉴 클릭 및 화이트아웃 검증
                for i in range(elements.count()):
                    element = elements.nth(i)
                    href_value = element.get_attribute('href')
                    logging.info(f"선택할 버튼의 href 속성 값: {href_value}")

                    try:
                        # <a> 태그 내부의 버튼 클릭
                        button = element.locator('div')  # 'locator'로 내부 요소 접근
                        logging.info(f"선택한 버튼: {button}")

                        button.click()  # 해당 버튼 클릭

                        logging.info(f"{href_value} 메뉴로 이동 중...")

                        # 페이지 로드 대기
                        page.wait_for_load_state('networkidle', timeout=20000)

                        # 화이트 아웃 감지
                        logging.info("화이트 아웃 발생 확인 중")
                        whiteout_detected = check_for_whiteout(page, f"{href_value} 버튼 클릭", save_path)

                        # 화이트 아웃 감지 여부 검증
                        assert not whiteout_detected, f"화이트 아웃이 감지되었습니다: {href_value}"
                        logging.info(f"{href_value} 검증 완료: 화이트 아웃 없음 (성공)")

                    except AssertionError as e:
                        # Assertion 실패 시 로그와 결과 기록, 코드 중단 없이 다음 항목으로 넘어감
                        logging.error(f"검증 실패: {str(e)}")
                        log_result(False, str(e))
                        test_results.append(str(e))

                    except Exception as e:
                        # 기타 예외 처리, 코드 중단 없이 다음 항목으로 넘어감
                        logging.error(f"{href_value} 클릭 중 오류 발생: {str(e)}")
                        log_result(False, f"{href_value} 클릭 중 예외 발생: {str(e)}")
                        test_results.append(f"{href_value} 클릭 중 예외 발생: {str(e)}")

            except Exception as e:
                logging.error(f"전체 실행 중 오류 발생: {str(e)}")

                

            '''MenuUl_sitemaps = []

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
                    logging.error(f"최대 시도 횟수({max_attempts}) 초과: {absolute_url} 링크 접속을 실패했습니다.")'''

            all_results[browser_type.name] = test_results
            

    except Exception as e:
        logging.error(f"오류 발생: {str(e)}")

    finally: 

        logging.info(f"{browser_type.name}_Test complete")  # 각 브라우저 작업 완료 메시지 출력

        for browser_name, results in all_results.items():
            logging.info(f"\n=== {browser_name} 테스트 결과 ===")
            for result in results:
                logging.info(f"[{browser_name}] {result}")
        
with sync_playwright() as playwright:

    run(playwright)
