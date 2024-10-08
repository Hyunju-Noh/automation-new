from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import requests
from PIL import ImageGrab
import time
import os
import cv2
import glob
import re
from bs4 import BeautifulSoup

def capture_screenshot(page, filename, save_path):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    screenshot_name = f"{filename}_{timestamp}.png"
    filepath = os.path.join(save_path, screenshot_name)
    page.screenshot(path=filepath)
    print(f"스크린샷이 저장되었습니다: {os.path.abspath(filepath)}")
    return filepath

def check_for_whiteout(page, button_text, save_path):
    whiteout_texts = ["죄송합니다", "페이지를 찾을 수 없습니다.", "Bad Gate", "OOOPS"]
    
    try:
        page_content = page.content()
        found_text = None
        for text in whiteout_texts:
            if text in page_content:
                found_text = text
                break
        
        if found_text:
            print(f"화이트아웃 화면 감지: '{found_text}' 특정 텍스트 발견")
            screenshot_path = capture_screenshot(page, f"whiteout_screen_{found_text}", save_path)
            print(f"화이트아웃 스크린샷 저장됨: {screenshot_path}")
            
            # 화이트 아웃 발생 원인 버튼의 텍스트를 출력
            button_element = page.query_selector(f"//*[text()='{button_text}']")
            if button_element:
                button_text = page.evaluate('(element) => element.textContent', button_element)
                element_html = page.evaluate('(element) => element.outerHTML', button_element)
                print(f"화이트아웃을 발생시킨 버튼 텍스트: {button_text}")
                print(f"화이트아웃을 발생시킨 버튼 HTML:\n{element_html}")
            else:
                print(f"화이트아웃을 발생시킨 버튼 '{button_text}'을(를) 찾을 수 없습니다.")
            
            # 뒤로가기 동작 후의 스크린샷 저장
            page.go_back()
            time.sleep(2)  # 페이지 로딩 대기
            back_screenshot_path = capture_screenshot(page, f"back_screen_{found_text}", save_path)
            print(f"뒤로가기 후 스크린샷 저장됨: {back_screenshot_path}")
            
            raise Exception("화이트아웃 화면 감지됨")
        else:
            print("정상 페이지로 보입니다.")
    except PlaywrightTimeoutError:
        screenshot_path = capture_screenshot(page, "timeout_screen", save_path)
        print(f"페이지를 로드하는 동안 타임아웃이 발생했습니다: {screenshot_path}")

def extract_button_selectors(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # 스타일 조건과 클래스 조건을 모두 만족하는 요소를 찾습니다.
    buttons = soup.find_all('span', class_='ant-typography ant-typography-ellipsis ant-typography-single-line Ants__Text-hTSPyx iSwFCK')
    filtered_buttons = [button for button in buttons if 'inline-flex' in button.get('style', '')]

    button_info = []
    for button in filtered_buttons:
        text = button.get_text().strip()
        style = button.get('style', '')
        
        # CSS 선택자 생성
        selector = f"span.ant-typography.ant-typography-ellipsis.ant-typography-single-line.Ants__Text-hTSPyx.iSwFCK[style*='{style}']:has-text('{text}')"
        button_info.append((text, selector))

    return button_info

#def extract_sitemap_button_selectors(html):
#    soup = BeautifulSoup(html, 'html.parser')
#    
    # 사이트맵 버튼 추출
#    sitemap_buttons = soup.find_all('a', class_='SitemapLgStyles__Link-hUYvxU bRMctN')
#    sitemap_button_info = []
#    
#    for button in sitemap_buttons:
#        text = button.get_text().strip()
#        href = button.get('href', '')
#        
        # CSS 선택자 생성
#        selector = f"a.SitemapLgStyles__Link-hUYvxU.bRMctN[href='{href}']"
#        sitemap_button_info.append((text, selector))
#    
#    return sitemap_button_info

def find_sitemap_button_ids(html):

    # ID 선택자를 찾기 위해 BeautifulSoup을 사용할 수 있습니다.
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # 사이트맵 버튼의 ID를 수집합니다.
    ids = set()
    for tag in soup.find_all('a', class_='SitemapLgStyles__Link-hUYvxU bRMctN'):
        if tag.get('id'):
            ids.add(tag['id'])

    return ids

def run(playwright):
    save_path = "/Users/nohhyunju/Documents/whiteout_screen"  # 지정한 저장 경로

    try:
        # Chromium, Firefox, WebKit을 동시에 시작합니다.
        for browser_type in [playwright.chromium, playwright.firefox, playwright.webkit]:
            print(f"{browser_type.name} 브라우저 시작 중...")
            browser = browser_type.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            # 페이지 전체에 대한 기본 타임아웃 설정
            context.set_default_timeout(120000)  # 120초로 설정

            print(f"{browser_type.name} - https://www.whatap.io/ 페이지로 이동 중...")
            page.goto("https://www.whatap.io/")
            time=3000

            # 화이트 아웃 확인
            page.wait_for_timeout(time)
            check_for_whiteout(page, "https://whatap.io/", save_path)

            print(f"{browser_type.name} - 로그인 페이지로 이동 중...")
            page.get_by_role("link", name="로그인").click()

            # 화이트 아웃 확인
            page.wait_for_timeout(time)
            check_for_whiteout(page, "로그인 화면", save_path)

            print(f"{browser_type.name} - 이메일 및 비밀번호 입력 중...")
            page.get_by_placeholder("Company Email").click()
            page.get_by_placeholder("Company Email").fill("hjnoh@whatap.io")
            page.get_by_placeholder("Password").click()
            page.get_by_placeholder("Password").fill("shguswn980512-")
            print(f"{browser_type.name} - 로그인 버튼 클릭 중...")
            page.locator('#btn_login').click()

            # 화이트 아웃 확인
            page.wait_for_timeout(time)
            check_for_whiteout(page, "로그인 버튼 누름", save_path)

            print(f"{browser_type.name} - 자바 프로젝트 선택 중...")
            page.locator("a").filter(has_text="Created with Sketch. Java APM").click()

            # 화이트 아웃 확인
            page.wait_for_timeout(time)
            check_for_whiteout(page, "자바 프로젝트 선택", save_path)

            # 페이지의 전체 HTML 가져오기
            print("전체 html 불러오는 중...")
            html = page.content()
            print("전체 html 코드 로드 완료.")

            #하위 메뉴 오픈
            indices = [3, 5, 7, 9, 12, 14, 16]

            for index in indices:
                selector = f"div:nth-child({index}) > .Menustyles__MenuItemInnerWrap-WxBhn > div:nth-child(3) > .SVGInline > .SVGInline-svg"
                page.locator(selector).click()


            button_info = extract_button_selectors(html)
            print(f"추출된 버튼 정보: {button_info}")


            for button_name, selector in button_info:
                 #시간 많이 지나면 재선택 하는 코드 추가하기
                print(f"{browser_type.name} - 버튼 '{button_name}'  클릭 중...")
                # '트랜잭션'이라는 텍스트를 정확히 매칭해서 클릭
                
                #    try: 
                #        page.get_by_role("link", name="에이전트 설정 Old", exact=True).click()
                #        print("에이전트 설정 Old 클릭 성공")
                #        page.wait_for_timeout(time)
                #        check_for_whiteout(page, button_name, save_path)
                #    except Exception as e:
                #        print("에이전트 설정 Old 클릭 실패:", e)

                #    try:
                #        page.get_by_role("link", name="에이전트 설정", exact=True).click()
                #        print("에이전트 설정 클릭 성공")
                #    except Exception as e:
                #        print("에이전트 설정 클릭 실패:", e)
                try:
                    if button_name == "일자별 애플리케이션 현황":
                        print(f"{browser_type.name} - '일자별 애플리케이션 현황' 버튼을 선택 중...")
                        link_locator = page.get_by_role("link", name="일자별 애플리케이션 현황", exact=True)
                        if link_locator.is_visible(timeout=10000):  # 10초 타임아웃
                            link_locator.click()
                        else:
                            print(f"{browser_type.name} - '일자별 애플리케이션 현' 버튼을 대신 선택 중...")
                            # 대체 버튼 클릭
                            link_locator = page.get_by_role("link", name="일자별 애플리케이션 현", exact=True)
                            if link_locator.is_visible(timeout=10000):
                                link_locator.click()
                            else:
                                print(f"{browser_type.name} - '일자별 애플리케이션 현' 버튼도 보이지 않습니다.")
                    elif button_name == "트랜잭션":
                        page.get_by_role("link", name=button_name, exact=True).click()
                    elif button_name == "에이전트 설정":

                        link_locator = page.get_by_role("link", name="에이전트 설정", exact=True)
                        if link_locator.is_visible(timeout=10000):
                            link_locator.click()
                        else:
                            print(f"에이전트 설정 선택 실패")

                    else:
                        page.locator(selector).click(timeout=10000)
                except PlaywrightTimeoutError:
                    print(f"'{button_name}' 클릭 시 10초 내에 완료되지 않아 타임아웃 발생, 재시도 중...")
                    try:
                        # 재시도 클릭: 타임아웃 없이 재시도
                        page.locator(selector).click()
                    except Exception as e:
                        print(f"'{button_id}' 클릭 재시도 실패: {e}")

                # 화이트 아웃 확인
                page.wait_for_timeout(time)
                check_for_whiteout(page, button_name, save_path)

                try:
                    # 1초 대기하여 팝업이 나타날 수 있도록 함
                    page.wait_for_timeout(1000)
                    
                    # 팝업 닫기 버튼이 존재하는지 확인
                    close_button = page.get_by_label("Close").get_by_role("button")
                    if close_button.is_visible():
                        close_button.click()
                        print("팝업이 감지되어 닫습니다.")
                    else:
                        print("팝업이 없습니다.")
                except PlaywrightTimeoutError:
                    print("팝업이 감지되지 않았습니다.")

            print(f"{browser_type.name} - 사이트맵 클릭 중...")
            page.locator("button:nth-child(3)").first.click()

            page.wait_for_timeout(time)

            # 페이지의 전체 HTML 가져오기
            print("전체 html 불러오는 중...")
            html = page.content()
            print("전체 html 코드 로드 완료.")

            ids = find_sitemap_button_ids(html)
            print(f"사이트맵에서 발견된 ID 선택자: {ids}")

            page.locator(".SitemapLgStyles__CloseButton-fwIwOQ").click()

            for button_id in ids:
                try:
                    #시간 많이 지나면 재선택 하는 코드 추가하기
                    print(f"{browser_type.name} - 사이트맵 클릭 중...")
                    page.locator("button:nth-child(3)").first.click()

                    print(f"ID '{button_id}' 클릭 중...")
                
                    if button_id == "SitemapLg_agentSetting":
                        try:
                            page.get_by_role("dialog").get_by_role("link", name="에이전트 설정 Old").click()
                            print("에이전트 설정 Old 클릭 성공")
                            page.wait_for_timeout(time)
                            check_for_whiteout(page, button_id, save_path)
                        except Exception as e:
                            print("에이전트 설정 Old 클릭 실패:", e)

                        print(f"{browser_type.name} - 사이트맵 클릭 중...")
                        page.locator("button:nth-child(3)").first.click()
                        
                         # 이후 "에이전트 설정" 링크 클릭 시도
                        try:
                            page.get_by_role("dialog").get_by_role("link", name="에이전트 설정", exact=True).click()
                            print("에이전트 설정 클릭 성공")
                        except Exception as e:
                            print("에이전트 설정 클릭 실패:", e)

                    else:
                        page.locator(f"#{button_id}").click(timeout=10000)
                except PlaywrightTimeoutError:
                    print(f"'{button_id}' 클릭 시 10초 내에 완료되지 않아 타임아웃 발생, 재시도 중...")
                    try:
                        # 재시도 클릭: 타임아웃 없이 재시도
                        page.locator(f"#{button_id}").click()
                    except Exception as e:
                        print(f"'{button_id}' 클릭 재시도 실패: {e}")

                #화이트 아웃 확인
            
                page.wait_for_timeout(time)
                check_for_whiteout(page, button_id, save_path)

                try:
                    page.wait_for_timeout(1000)
                    close_button = page.get_by_label("Close").get_by_role("button")
                    if close_button.is_visible():
                        close_button.click()
                        print("팝업이 감지되어 닫습니다.")
                    else:
                        print("팝업이 없습니다.")
                except PlaywrightTimeoutError:
                    print("팝업이 감지되지 않았습니다.")

    except Exception as e:
        print(f"오류 발생: {str(e)}")

    finally: 
        
        print(f"{browser_type.name}_Test complete")  # 각 브라우저 작업 완료 메시지 출력
        

with sync_playwright() as playwright:

    run(playwright)
