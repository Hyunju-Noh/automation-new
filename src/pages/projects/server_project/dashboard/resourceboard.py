from datetime import datetime
import logging
import os
import time
import csv
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

WHITEOUT_TEXTS = ["죄송합니다", "페이지를 찾을 수 없습니다.", "Bad Gate", "OOOPS"]

browser_type = None
#popup_detected = False

# 로깅 설정 파일 위치 따로 설정하기
log_save_path = os.getenv("LOG_FILE_PATH", "src/reports/logs/main_menu")  
if not os.path.exists(log_save_path):
    os.makedirs(log_save_path)


# 로깅 설정
log_filename = os.path.join(log_save_path, f"KUBER_WHITEOUT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_filename)
    ]
)


def log_result(success, message):
    if success:
        logging.info(f"✅ {message}")
    else:
        logging.error(f"❌ {message}")


def capture_screenshot(page, filename, save_path):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    screenshot_name = f"{filename}_{timestamp}.png"
    filepath = os.path.join(save_path, screenshot_name)
    page.screenshot(path=filepath)
    logging.error(f"스크린샷이 저장되었습니다: {os.path.abspath(filepath)}")
    return filepath


def login(page, email, password, test_results):

    try:
        logging.info(f"로그인 페이지로 이동 중...")
        page.goto("https://www.whatap.io/")
        page.get_by_role("link", name="로그인").click()
        page.get_by_placeholder("Company Email").fill(email)
        #logging.info(f"Password being inputted: {password}")
        page.get_by_placeholder("Password").type(password)

        page.wait_for_load_state('networkidle')

        page.get_by_role("button", name="로그인").click()

        # 페이지 로드 완료 후 URL 확인
        after_url = page.url
        logging.info(f"현재 URL: {after_url}")
        expected_value = "account/project"

         # 첫번째 조건: URL에 expected_value가 포함되면 성공
        assert expected_value in after_url, f"로그인 실패"
        
        log_result(True, f" 로그인 성공")
        test_results.append(f" 로그인 성공")

    except AssertionError as e:
        # Assertion 실패 시 로그 및 결과 기록
        log_result(False, str(e))
        test_results.append(str(e))
    
    except Exception as e:
        # 기타 예외 처리 로그 및 결과 기록
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")


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
            #logging.info("페이지 컨텐츠를 가져오는 중...")
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


''' 모달 팝업을 잡는 함수가 아님. 브라우저 팝업을 잡는 함수임
def handle_dialog(dialog):
    global popup_detected
    logging.info(f"팝업 감지됨: {dialog.message}")
    popup_detected = True
    dialog.accept()  # 팝업을 수락'''


def load_whiteout_texts(file_path):
    """CSV 파일에서 화이트아웃 텍스트 목록을 로드합니다."""
    file_path = os.getenv("WHITEOUT_TEXTS_PATH", "data/whiteout_texts.csv")

    texts = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                texts.append(row['text'])
    except FileNotFoundError:
        logging.error(f"{file_path} 파일을 찾을 수 없습니다.")
    return texts
        

def check_for_whiteout(page, button_text, save_path):
    try:
        page.wait_for_load_state('networkidle', timeout=10000)  

        #logging.info("페이지 컨텐츠 가져오기 시도 중...")        
        page_content = get_page_content_with_timeout(page, timeout=10000)  # 10초 동안 대기
        #logging.info("페이지 컨텐츠 가져오기 완료")

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


def close_modal_if_present(page):
    """
    페이지에서 다양한 유형의 모달 팝업이 나타나면 닫습니다.
    """
    try:
        # 다양한 팝업 닫기 버튼의 클래스 선택자를 리스트에 추가
        close_selectors = [
            ".Styles__Wrapper-bZXaBP.dZPSDU",  # 첫 번째 모달 유형 닫기 버튼
            ".__floater__open .Styles__Wrapper-bZXaBP.cdnUPE",  # 두 번째 모달 유형 닫기 버튼
            #".another-modal-close-class",  # 다른 팝업 유형의 닫기 버튼
            # 추가 팝업 닫기 버튼 클래스
        ]

        # 순차적으로 닫기 버튼을 찾고, 감지되면 클릭하여 닫음
        for selector in close_selectors:
            close_button = page.locator(selector)

            page.wait_for_load_state("domcontentloaded")

            if close_button.count() > 0:
                logging.info(f"모달 팝업 감지 - 닫기 버튼: {selector}")
                close_button.click()
                logging.info("모달 팝업 닫기 완료")
                return True

    except Exception as e:
        logging.error(f"모달 팝업을 닫는 중 오류 발생: {str(e)}")
    return False


def perform_action_with_modal_check(page, action_func, *args, **kwargs):
    """
    지정된 동작을 수행한 후 모달 팝업이 발생하면 닫고, 발생하지 않으면 그냥 넘어감.
    
    Args:
        page: Playwright의 페이지 객체
        action_func: 수행할 동작 함수 (예: button.click)
        *args, **kwargs: 동작 함수에 전달할 인자들
    """
    try:
        # 동작 수행
        action_func(*args, **kwargs)  # 예: button.click()

        #page.wait_for_load_state('networkidle')
        page.wait_for_timeout(1000)
        
        # 모달 팝업 닫기 시도
        close_modal_if_present(page)
        
    except Exception as e:
        logging.error(f"동작 수행 중 오류 발생: {str(e)}")


def verify_widget_button_action(page, widget_name, locator, button_name, test_results, action):
    """
    버튼 동작 수행 함수.

    :param page: Playwright 페이지 객체
    :param widget_name: 위젯 이름
    :param locator: 버튼 선택자
    :param button_name: 버튼 이름
    :param test_results: 테스트 결과를 기록할 리스트
    :param action: 버튼 클릭 후 수행할 추가 동작 (콜백 함수)
    """
    try:
        logging.info(f"[{widget_name}] 위젯 UI [{button_name}] 동작 수행 중")
        button_locator = page.locator(locator)

        # 버튼 클릭
        button_locator.click()

        # 추가 동작 수행
        if action:
            action(page)

        log_result(True, f"[{widget_name}] UI [{button_name}] 동작 완료 (성공)")
        test_results.append(f"[{widget_name}] UI [{button_name}] 동작 완료 (성공)")

    except Exception as e:
        logging.error(f"오류 발생: {str(e)}")
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")

def verify_widget_ui(page, locator, widget_name, test_results, element_name=None):
    """
    위젯 UI 표시 여부를 검증하는 공통 함수.

    :param page: Playwright 페이지 객체
    :param locator: UI 요소를 찾는 선택자
    :param widget_name: 위젯 이름 (로그용)
    :param test_results: 테스트 결과를 기록할 리스트
    :param element_name: UI 요소 이름 (옵션, 로그용)
    """
    try:
        display_name = f"{widget_name} {element_name}" if element_name else widget_name
        logging.info(f"[{display_name}] 표시 확인 중")
        element_locator = page.locator(locator)

        # UI 요소가 화면에 표시되는지 확인
        element_visible = element_locator.is_visible()
        assert element_visible, f"[{display_name}] 표시 확인 실패"

        log_result(True, f"[{display_name}] 표시 확인 완료 (성공)")
        test_results.append(f"[{display_name}] 표시 확인 완료 (성공)")

    except AssertionError as e:
        logging.error(f"검증 실패: {str(e)}")
        log_result(False, str(e))
        test_results.append(str(e))

    except Exception as e:
        logging.error(f"오류 발생: {str(e)}")
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")


def verify_whiteout(page, screen_name, save_path, test_results):
    """
    화이트아웃 검증 함수.

    :param page: Playwright 페이지 객체
    :param screen_name: 화면 이름 (로그용)
    :param save_path: 스크린샷 저장 경로
    :param test_results: 테스트 결과를 기록할 리스트
    """
    try:
        logging.info(f"[{screen_name}] 화이트아웃 발생 확인 중")
        page.wait_for_load_state('networkidle')
        whiteout_detected = check_for_whiteout(page, screen_name, save_path)
        assert not whiteout_detected, f"[{screen_name}] 화면에서 화이트아웃이 감지되었습니다"
        log_result(True, f"[{screen_name}] 화이트아웃 검증 완료: 문제 없음")
        test_results.append(f"[{screen_name}] 화이트아웃 검증 완료: 문제 없음")

    except AssertionError as e:
        logging.error(f"검증 실패: {str(e)}")
        log_result(False, str(e))
        test_results.append(str(e))

    except Exception as e:
        logging.error(f"오류 발생: {str(e)}")
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")


def verify_widget_hover_action(page, widget_name, element_locator, button_name, test_results, action, hover_position=None):
    """
    버튼 또는 요소에 마우스 호버 후 추가 동작 수행 함수.

    :param page: Playwright 페이지 객체
    :param widget_name: 위젯 이름
    :param locator: 버튼 또는 요소의 선택자 (없을 경우 hover_position 사용)
    :param button_name: 버튼 이름
    :param hover_position: 마우스 호버 좌표값 (생략 가능)
    :param test_results: 테스트 결과를 기록할 리스트
    :param action: 마우스 호버 후 수행할 추가 동작 (콜백 함수)
    """
    try:
        logging.info(f"[{widget_name}] 위젯 UI [{button_name}] 마우스 호버 동작 수행 중")

        if element_locator:
            # element_locator가 있을 경우 해당 요소에 마우스 호버
            element = page.locator(element_locator)
            element.hover()
            logging.info(f"[{widget_name}] [{button_name}] 요소에 마우스 호버 완료")
        elif hover_position:
            # hover_position이 있을 경우 캔버스 또는 화면 좌표에 마우스 호버
            page.mouse.move(hover_position['x'], hover_position['y'])
            logging.info(f"[{widget_name}] 좌표 ({hover_position['x']}, {hover_position['y']})에 마우스 호버 완료")
        else:
            raise ValueError("Element_locator 또는 hover_position 값이 필요합니다.")

        # 추가 동작 수행
        if action:
            action(page)

        log_result(True, f"[{widget_name}] UI [{button_name}] 마우스 호버 및 동작 완료 (성공)")
        test_results.append(f"[{widget_name}] UI [{button_name}] 마우스 호버 및 동작 완료 (성공)")

    except Exception as e:
        logging.error(f"[{widget_name}] 오류 발생: {str(e)}")
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")


#위젯별 이 아닌, 검증해야할 동작 별로 액션 함수를 나눠야 할듯
def button_action_serverwidget(page):
    try:
        logging.info("버튼 클릭 후 동작 수행")

        # 1. 서버 목록 화면으로 이동했는지 확ㅣ
        page.wait_for_url("**/server/list")
        assert page.url.endswith("/server/list"), "서버 목록 페이지로 이동하지 않았습니다"
        logging.info("서버 목록 페이지로 정상 이동 확인됨")

        # 2. 서버 목록 UI가 정상 표시되는지 확인 (화이트아웃 검증)
        verify_whiteout(
            page=page,
            screen_name="서버 목록 페이지",
            save_path=save_path,
            test_results=test_results
        )
        logging.info("서버 목록 UI 화이트아웃 없음 확인됨")

        # 3. 사이드 메뉴에 [서버 목록] 메뉴가 하이라이팅 되었는지 확인
        side_menu_locator = page.locator("a[href='/v2/project/sms/29763/dashboard/resource_board'] div.Menustyles__MenuItemWrapCommon-cHqrwY")
        is_highlighted = side_menu_locator.evaluate(
        "(element) => element.classList.contains('iWDtdN')"
        )
        assert is_highlighted, "[서버 목록] 메뉴가 하이라이팅되지 않았습니다"
        logging.info("사이드 메뉴 하이라이팅 확인됨")

    except AssertionError as e:
        logging.error(f"검증 실패: {str(e)}")
        log_result(False, str(e))  # 실패 기록
        test_results.append(str(e))  # 실패 내용을 테스트 결과 리스트에 추가

    except Exception as e:
        logging.error(f"오류 발생: {str(e)}")
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")


def button_action_infobutton(page):
    try:
        logging.info("info button 마우스 호버 후 동작 수행")

        # 팝업 표시 확인
        popup_locator = page.locator("div.popup-class")
        assert popup_locator.is_visible(), "팝업이 표시되지 않았습니다"
        logging.info("팝업이 정상적으로 표시됨")

    except AssertionError as e:
        logging.error(f"검증 실패: {str(e)}")
        log_result(False, str(e))
        test_results.append(str(e))

    except Exception as e:
        logging.error(f"오류 발생: {str(e)}")
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")


def metrics_button_action(page):
    try:
        logging.info("Metrics 버튼 클릭 후 동작 수행")

        # 팝업 표시 확인
        popup_locator = page.locator("div.popup-class")
        assert popup_locator.is_visible(), "팝업이 표시되지 않았습니다"
        logging.info("팝업이 정상적으로 표시됨")

    except AssertionError as e:
        logging.error(f"검증 실패: {str(e)}")
        log_result(False, str(e))
        test_results.append(str(e))

    except Exception as e:
        logging.error(f"오류 발생: {str(e)}")
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")


def server_button_action(page):
    try:
        logging.info("Server 버튼 클릭 후 동작 수행")
        # 페이지 전환 확인
        page.wait_for_url("**/server-details")
        assert page.url.endswith("/server-details"), "Server 상세 페이지로 이동하지 않았습니다"

        # 화이트아웃 검증 추가
        verify_whiteout(
            page=page,
            screen_name="Server 상세 페이지",
            save_path="path/to/save/screenshots",
            test_results=test_results
        )

        logging.info("Server 상세 페이지 검증 완료")

    except AssertionError as e:
        logging.error(f"검증 실패: {str(e)}")
        log_result(False, str(e))
        test_results.append(str(e))

    except Exception as e:
        logging.error(f"오류 발생: {str(e)}")
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")



def process_case_1(page, test_results):
    # Case 1: 리소스보드 화면 UI 확인

    # 리소스보드 선택
    logging.info("리소스보드 화면으로 이동 중")
    page.locator('a[href="/v2/project/sms/29763/dashboard/resource_board"]').click()

    # 화이트아웃 검증
    verify_whiteout(
            page=page,
            screen_name="리소스보드 화면",
            save_path=save_path,
            test_results=test_results
        )
    
    # 각 위젯 자체가 화면에 표시되는지 확인
    filtered_widgets = [
        widget for widget in all_widgets 
        if widget.get("element_name") is None and widget.get("element_locator") is None
    ]

    for widget in filtered_widgets:
        verify_widget_ui(
            page=page,
            locator=widget["locator"],
            widget_name=widget["widget_name"],
            test_results=test_results
        )


def process_case_2(page, test_results):
    # Case 2: [Server] 위젯 UI 확인

    filtered_widgets = [
        widget for widget in all_widgets 
        if ["widget_name"] == "Server" and widget.get("element_name") and widget.get("element_locator")
        ]
    
    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_ui(
            page=page,
            locator=element_locator,
            widget_name=widget["widget_name"],
            element_name=widget["element_name"],
            test_results=test_results
        )


def process_case_3(page, test_results):
    # Case 3: [Server] 위젯 [>] 버튼 동작 확인

    filtered_widgets = [
        widget for widget in all_widgets 
        if ["widget_name"] == "Server" and widget.get("button_name")
        ]
    
    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_button_action(
            page=page,
            locator=element_locator,
            widget_name=widget["widget_name"],
            button_name=widget["button_name"],
            test_results=test_results,
            action=widget["action"]
        )


def process_case_4(page, test_results):
    # Case 4: [OS] 위젯 UI 확인

    filtered_widgets = [
        widget for widget in all_widgets 
        if ["widget_name"] == "OS" and widget.get("element_name") and widget.get("element_locator")
        ]
    
    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_ui(
            page=page,
            locator=element_locator,
            widget_name=widget["widget_name"],
            element_name=widget["element_name"],
            test_results=test_results
        )


def process_case_5(page, test_results):
    # Case 5: [Total Cores] 위젯 UI 확인

    filtered_widgets = [
        widget for widget in all_widgets 
        if ["widget_name"] == "Total Cores" and widget.get("element_name") and widget.get("element_locator")
        ]
    
    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_ui(
            page=page,
            locator=element_locator,
            widget_name=widget["widget_name"],
            element_name=widget["element_name"],
            test_results=test_results
        )


def process_case_6(page, test_results):
    # Case 6: [Avg CPU] 위젯 UI 확인

    filtered_widgets = [
        widget for widget in all_widgets 
        if ["widget_name"] == "Avg CPU" and widget.get("element_name") and widget.get("element_locator")
        ]
    
    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_ui(
            page=page,
            locator=element_locator,
            widget_name=widget["widget_name"],
            element_name=widget["element_name"],
            test_results=test_results
        )


def process_case_7(page, test_results):
    # Case 7: [Avg Memory] 위젯 UI 확인

    filtered_widgets = [
        widget for widget in all_widgets 
        if ["widget_name"] == "Avg Memory" and widget.get("element_name") and widget.get("element_locator")
        ]
    
    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_ui(
            page=page,
            locator=element_locator,
            widget_name=widget["widget_name"],
            element_name=widget["element_name"],
            test_results=test_results
        )


def process_case_8(page, test_results):
    # Case 8: [Avg Disk] 위젯 UI 확인

    filtered_widgets = [
        widget for widget in all_widgets 
        if ["widget_name"] == "Avg Disk" and widget.get("element_name") and widget.get("element_locator")
        ]
    
    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_ui(
            page=page,
            locator=element_locator,
            widget_name=widget["widget_name"],
            element_name=widget["element_name"],
            test_results=test_results
        )


def process_case_9(page, test_results):
    # Case 9: [CPU - TOP5] 위젯 UI 확인

    filtered_widgets = [
        widget for widget in all_widgets 
        if ["widget_name"] == "CPU - TOP5" and widget.get("element_name") and widget.get("element_locator")
        ]
    
    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_ui(
            page=page,
            locator=element_locator,
            widget_name=widget["widget_name"],
            element_name=widget["element_name"],
            test_results=test_results
        )


#위젯 자체 별로 + 버튼 별로 리스트에 다 추가하기
all_widgets = [
    
    {
        "widget_name": "OS",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('OS'))",  # 위젯 자체 확인
        "element_name": None,  # 내부 요소 없음
        "element_locator": None,
        "button_name": None,
        "action": None
    },
    {
        "widget_name": "Server",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Server'))",  # 위젯 자체 확인
        "element_name": None,  # 내부 요소 없음
        "element_locator": None,
        "button_name": None,
        "action": None
    },
    {
        "widget_name": "Total Cores",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Total Cores'))",  # 위젯 자체 확인
        "element_name": None,  # 내부 요소 없음
        "element_locator": None,
        "button_name": None,
        "action": None
    },
    {
        "widget_name": "Avg CPU",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Avg CPU'))",  # 위젯 자체 확인
        "element_name": None,  # 내부 요소 없음
        "element_locator": None,
        "button_name": None,
        "action": None
    },
    {
        "widget_name": "Avg Memory",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Avg Memory'))",  # 위젯 자체 확인
        "element_name": None,  # 내부 요소 없음
        "element_locator": None,
        "button_name": None,
        "action": None
    },
    {
        "widget_name": "Avg Disk",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Avg Disk'))",  # 위젯 자체 확인
        "element_name": None,  # 내부 요소 없음
        "element_locator": None,
        "button_name": None,
        "action": None
    },
    {
        "widget_name": "CPU - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('CPU')))",  # 위젯 자체 확인
        "element_name": None,  # 내부 요소 없음
        "element_locator": None,
        "button_name": None,
        "action": None
    },
    {
        "widget_name": "메모리 - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('메모리')))",  # 위젯 자체 확인
        "element_name": None,  # 내부 요소 없음
        "element_locator": None,
        "button_name": None,
        "action": None
    },
    {
        "widget_name": "디스크 I/O - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('디스크 I/O')))",  # 위젯 자체 확인
        "element_name": None,  # 내부 요소 없음
        "element_locator": None,
        "button_name": None,
        "action": None
    },
    {
        "widget_name": "Server Status Map",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(span:text('Server Status Map'))",  # 위젯 자체 확인
        "element_name": None,  # 내부 요소 없음
        "element_locator": None,
        "button_name": None,
        "action": None
    },
    {
        "widget_name": "프로세스 CPU TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(span:text('프로세스 CPU TOP5'))",  # 위젯 자체 확인
        "element_name": None,  # 내부 요소 없음
        "element_locator": None,
        "button_name": None,
        "action": None
    },
    {
        "widget_name": "프로세스 메모리 TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(span:text('프로세스 메모리 TOP5'))",  # 위젯 자체 확인
        "element_name": None,  # 내부 요소 없음
        "element_locator": None,
        "button_name": None,
        "action": None
    },
    {
        "widget_name": "Server",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Server'))",  # 위젯 자체 확인
        "element_name": "[>] 버튼",
        "element_locator": "{locator} button.Styles__Button-bDBZvm",
        "button_name": "[>] 버튼",
        "action": button_action_serverwidget  # 버튼 동작 수행 함수
    },
    {
        "widget_name": "Server",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Server'))",  # 위젯 자체 확인
        "element_name": "Value Text",
        "element_locator": "{locator} span.ResourceCards__ValueText-jMQaIH.fZMedF",
        "button_name": None,  # 버튼이 없는 경우 None
        "action": None  # 동작 수행 함수 없음
    },
    {
        "widget_name": "Server",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Server'))",  # 위젯 자체 확인
        "element_name": "Progress Bar",
        "element_locator": "{locator} div.ant-progress.ant-progress-line.ant-progress-status-active.ant-progress-default",
        "button_name": None,  # 버튼이 없는 경우 None
        "action": None  # 동작 수행 함수 없음
    },
    {
        "widget_name": "Server",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Server'))",  # 위젯 자체 확인
        "element_name": "Progress Bar Text",
        "element_locator": "{locator} div.ResourceCards__ProgressLabels-jdjbop.bkmXSU",
        "button_name": None,  # 버튼이 없는 경우 None
        "action": None  # 동작 수행 함수 없음
    },
    {
        "widget_name": "OS",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('OS'))",  # 위젯 자체 확인
        "element_name": "Linux Value Text",
        "element_locator": "{locator} div:has(> div.ResourceCards__SubTitle-eZXil.jHWnBP:has-text('Linux')):has(> div.ResourceCards__SubValue-bOvbm.cfupYY)",
        "button_name": None,  # 버튼이 없는 경우 None
        "action": None  # 동작 수행 함수 없음
    },
    {
        "widget_name": "OS",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('OS'))",  # 위젯 자체 확인
        "element_name": "Windows Value",
        "element_locator": "{locator} div:has(> div.ResourceCards__SubTitle-eZXil.jHWnBP:has-text('Windows')):has(> div.ResourceCards__SubValue-bOvbm.cfupYY)",
        "button_name": None,  # 버튼이 없는 경우 None
        "action": None  # 동작 수행 함수 없음
    },
    {
        "widget_name": "OS",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('OS'))",  # 위젯 자체 확인
        "element_name": "Windows Value",
        "element_locator": "{locator} div:has(> div.ResourceCards__SubTitle-eZXil.jHWnBP:has-text('Unix')):has(> div.ResourceCards__SubValue-bOvbm.cfupYY)",
        "button_name": None,  # 버튼이 없는 경우 None
        "action": None  # 동작 수행 함수 없음
    },
    {
        "widget_name": "OS",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('OS'))",  # 위젯 자체 확인
        "element_name": "Windows Value",
        "element_locator": "{locator} div:has(> div.ResourceCards__SubTitle-eZXil.jHWnBP:has-text('Others')):has(> div.ResourceCards__SubValue-bOvbm.cfupYY)",
        "button_name": None,  # 버튼이 없는 경우 None
        "action": None  # 동작 수행 함수 없음
    },
    {
        "widget_name": "Total Cores",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Total Cores'))",  # 위젯 자체 확인
        "element_name": "Value Text",
        "element_locator": "{locator} span.ResourceCards__ValueText-jMQaIH.fZMedF",
        "button_name": None,  # 버튼이 없는 경우 None
        "action": None  # 동작 수행 함수 없음
    },
    {
        "widget_name": "Avg CPU",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Avg CPU'))",  # 위젯 자체 확인
        "element_name": "Value Text",
        "element_locator": "{locator} span.ResourceCards__ValueText-jMQaIH.fZMedF",
        "button_name": None,  # 버튼이 없는 경우 None
        "action": None  # 동작 수행 함수 없음
    },
    {
        "widget_name": "Avg CPU",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Avg CPU'))",  # 위젯 자체 확인
        "element_name": "PercentBar",
        "element_locator": "{locator} div.PercentBarstyle__PercentBarWrapper-fuDbrY",
        "button_name": None,  # 버튼이 없는 경우 None
        "action": None  # 동작 수행 함수 없음
    },
    {
        "widget_name": "Avg Memory",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Avg Memory'))",  # 위젯 자체 확인
        "element_name": "Value Text",
        "element_locator": "{locator} span.ResourceCards__ValueText-jMQaIH.fZMedF",
        "button_name": None,  # 버튼이 없는 경우 None
        "action": None  # 동작 수행 함수 없음
    },
    {
        "widget_name": "Avg Memory",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Avg Memory'))",  
        "element_name": "PercentBar",
        "element_locator": "{locator} div.PercentBarstyle__PercentBarWrapper-fuDbrY",
        "button_name": None,  # 버튼이 없는 경우 None
        "action": None  # 동작 수행 함수 없음
    },
    {
        "widget_name": "Avg Disk",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Avg Disk'))", 
        "element_name": "Value Text",
        "element_locator": "{locator} span.ResourceCards__ValueText-jMQaIH.fZMedF",
        "button_name": None,  # 버튼이 없는 경우 None
        "action": None  # 동작 수행 함수 없음
    },
    {
        "widget_name": "Avg Disk",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Avg Disk'))",  
        "element_name": "PercentBar",
        "element_locator": "{locator} div.PercentBarstyle__PercentBarWrapper-fuDbrY",
        "button_name": None,  # 버튼이 없는 경우 None
        "action": None  # 동작 수행 함수 없음
    },
    {
        "widget_name": "CPU - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('CPU')))",
        "element_name": "info button",  
        "element_locator": "{locator} div.Styles__Wrapper-bZXaBP.LPWtZ",
        "button_name": "info button",
        "action": #
    },


    {
        "widget_name": "CPU - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('CPU')))",
        "element_name": "[>] button",
        "element_locator": "{locator} div.Styles__Wrapper-bZXaBP.lomqVM",
        "button_name": "[>] 버튼",
        "action": #  # 버튼 동작 수행 함수
    },
    {
        "widget_name": "CPU - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('CPU')))",
        "element_name": "PanelContents button",
        "element_locator": "{locator} button.Styles__Button-bDBZvm.xlLVl.ant-dropdown-trigger"
        "button_name": "PanelContents button",
        "action": #  # 버튼 동작 수행 함수
    },
    {
        "widget_name": "CPU - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('CPU')))",
        "element_name": "PanelContents chart",
        "element_locator": "{locator} canvas.sc-dcJsrY.dvDjBb"
        "button_name": "PanelContents chart",
        "action": #  # 버튼 동작 수행 함수
        "hover_positions": [  
        {"x":120,"y":40}
        ] # 툴팁 검증을 위한 좌표
    },

]


def run(playwright):
    save_path = os.getenv("WHITEOUT_SCREEN_PATH", "src/reports/screeen_shot/kuber_whiteout")

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    global browser_type
    #global popup_detected
    all_results = {}
    test_results = []

    try:
        # Chromium, Firefox, WebKit을 동시에 시작합니다.
        for browser_type in [playwright.chromium, playwright.firefox, playwright.webkit]:
            logging.info(f"{browser_type.name} 브라우저 시작 중...")
            browser = browser_type.launch(headless=False)
            context = browser.new_context(
                locale="ko-KR",  # 브라우저 언어를 한국어로 설정
                storage_state={}
            )

            # 페이지 전체에 대한 기본 타임아웃 설정
            context.set_default_timeout(120000)  # 120초로 설정
            page = context.new_page()

            # 이거는 테스트케이스 코드에 들어가야함
            #page.on("load", lambda: close_modal_if_present(page))

            email_text = "hjnoh@whatap.io"
            password = "shguswn980512!"

            login (
                page=page,
                email=email_text,
                password=password,
                test_results=test_results
            )

            project_type = "sms"
            project_id = 29763

            project_url = f"https://service.whatap.io/v2/project/{project_type}/{project_id}"
            page.goto(project_url)

            # Case 1 처리
            process_case_1(page, test_results)

            # Case 2 처리
            process_case_2(page, test_results)

            # Case 3 처리
            process_case_3(page, test_results)
            

            # 리소스보드 선택
            page.locator('a[href="/v2/project/sms/29763/dashboard/resource_board"]').click()

            # 1-1. 대시보드_리소스보드
            # 1. 리소스보드 UI 확인

            # 리소스보드 화이트 아웃 감지
            try:
                logging.info("리소스보드 화이트 아웃 발생 확인 중")
                page.wait_for_load_state('networkidle')
                whiteout_detected = check_for_whiteout(page, f"리소스보드 화면 진입", save_path)

                # 화이트 아웃 감지 여부 검증
                assert not whiteout_detected, f"리소스보드 화면 화이트 아웃이 감지되었습니다"
                log_result(True, f"리소스보드 화면 검증 완료: 화이트 아웃 없음 (성공)")
                test_results.append(f"리소스보드 화면 검증 완료: 화이트 아웃 없음 (성공)")

            except AssertionError as e:
                # Assertion 실패 시 로그와 결과 기록, 코드 중단 없이 다음 항목으로 넘어감
                logging.error(f"검증 실패: {str(e)}")
                log_result(False, str(e))
                test_results.append(str(e))

            except Exception as e:
                # 기타 예외 처리, 코드 중단 없이 다음 항목으로 넘어감
                logging.error(f"오류 발생: {str(e)}")
                log_result(False, f"예외 발생: {str(e)}")
                test_results.append(f"예외 발생: {str(e)}")

            # [Server] 위젯 표시 확인
            verify_widget_visibility(
                page=page,  # Playwright 페이지 객체
                locator="div.ResourceCards__CardDom-dzFtxX:has(span:text('Server'))", # CSS 선택자
                widget_name="Server", # 위젯 이름
                test_results=test_results  # 결과 기록 리스트
            )

            # [OS] 위젯 표시 확인
            verify_widget_visibility(
                page=page,  # Playwright 페이지 객체
                locator="div.ResourceCards__CardDom-dzFtxX:has(span:text('OS'))", # CSS 선택자
                widget_name="OS", # 위젯 이름
                test_results=test_results  # 결과 기록 리스트
            )

            # [Total Cores] 위젯 표시 확인
            verify_widget_visibility(
                page=page,  # Playwright 페이지 객체
                locator="div.ResourceCards__CardDom-dzFtxX:has(span:text('Total Cores'))", # CSS 선택자
                widget_name="Total Cores", # 위젯 이름
                test_results=test_results  # 결과 기록 리스트
            )

            # [Avg CPU] 위젯 표시 확인
            verify_widget_visibility(
                page=page,  # Playwright 페이지 객체
                locator="div.ResourceCards__CardDom-dzFtxX:has(span:text('Avg CPU'))", # CSS 선택자
                widget_name="Avg CPU", # 위젯 이름
                test_results=test_results  # 결과 기록 리스트
            )

            # [Avg Memory] 위젯 표시 확인
            verify_widget_visibility(
                page=page,  # Playwright 페이지 객체
                locator="div.ResourceCards__CardDom-dzFtxX:has(span:text('Avg Memory'))", # CSS 선택자
                widget_name="Avg Memory", # 위젯 이름
                test_results=test_results  # 결과 기록 리스트
            )

            # [Avg Disk] 위젯 표시 확인
            verify_widget_visibility(
                page=page,  # Playwright 페이지 객체
                locator="div.ResourceCards__CardDom-dzFtxX:has(span:text('Avg Disk'))", # CSS 선택자
                widget_name="Avg Disk", # 위젯 이름
                test_results=test_results  # 결과 기록 리스트
            )

            # [CPU - TOP5] 위젯 표시 확인
            verify_widget_visibility(
                page=page,  # Playwright 페이지 객체
                locator="div.ResourceCards__CardDom-dzFtxX:has(span:text('CPU - TOP5'))", # CSS 선택자
                widget_name="CPU - TOP5", # 위젯 이름
                test_results=test_results  # 결과 기록 리스트
            )

            # [메모리 - TOP5] 위젯 표시 확인
            verify_widget_visibility(
                page=page,  # Playwright 페이지 객체
                locator="div.ResourceCards__CardDom-dzFtxX:has(span:text('메모리 - TOP5'))", # CSS 선택자
                widget_name="메모리 - TOP5", # 위젯 이름
                test_results=test_results  # 결과 기록 리스트
            )

            # [디스크 I/O - TOP5] 위젯 표시 확인
            verify_widget_visibility(
                page=page,  # Playwright 페이지 객체
                locator="div.ResourceCards__CardDom-dzFtxX:has(span:text('디스크 I/O - TOP5'))", # CSS 선택자
                widget_name="디스크 I/O - TOP5", # 위젯 이름
                test_results=test_results  # 결과 기록 리스트
            )

            # [CPU Resource Map] 위젯 표시 확인
            verify_widget_visibility(
                page=page,  # Playwright 페이지 객체
                locator="div.ResourceCards__CardDom-dzFtxX:has(span:text('CPU Resource Map'))", # CSS 선택자
                widget_name="CPU Resource Map", # 위젯 이름
                test_results=test_results  # 결과 기록 리스트
            )

            # [프로세스 CPU TOP5] 위젯 표시 확인
            verify_widget_visibility(
                page=page,  # Playwright 페이지 객체
                locator="div.ResourceCards__CardDom-dzFtxX:has(span:text('프로세스 CPU TOP5'))", # CSS 선택자
                widget_name="프로세스 CPU TOP5", # 위젯 이름
                test_results=test_results  # 결과 기록 리스트
            )

            # [프로세스 메모리 TOP5] 위젯 표시 확인
            verify_widget_visibility(
                page=page,  # Playwright 페이지 객체
                locator="div.ResourceCards__CardDom-dzFtxX:has(span:text('프로세스 메모리 TOP5'))", # CSS 선택자
                widget_name="프로세스 메모리 TOP5", # 위젯 이름
                test_results=test_results  # 결과 기록 리스트
            )

            # 2. [Server] 위젯 UI 확인

            #[>] 버튼 표시 확인
            try:
                logging.info("[Server] 위젯 UI [>] 버튼 표시 확인 중")
                inner_content_locator = page.locator("div.ResourceCards__CardDom-dzFtxX:has(span:text('Server')) button.Styles__Button-bDBZvm")

                # 위젯이 화면에 표시되는지 확인
                inner_content_visible = inner_content_locator.is_visible()

                assert inner_content_visible, f"[Server] 위젯 UI [>] 버튼 표시 확인 실패"
                log_result(True, f"[Server] 위젯 UI: 화면에 정상 표시됨 (성공)")
                test_results.append(f"[Server] 위젯 UI: 화면에 정상 표시됨 (성공)")

            except AssertionError as e:
                # Assertion 실패 시 로그와 결과 기록, 코드 중단 없이 다음 항목으로 넘어감
                logging.error(f"검증 실패: {str(e)}")
                log_result(False, str(e))
                test_results.append(str(e))

            except Exception as e:
                # 기타 예외 처리, 코드 중단 없이 다음 항목으로 넘어감
                logging.error(f"오류 발생: {str(e)}")
                log_result(False, f"예외 발생: {str(e)}")
                test_results.append(f"예외 발생: {str(e)}")

            
            #Value Text 버튼 표시 확인
            try:
                logging.info("[Server] 위젯 UI Value Text 표시 확인 중")
                inner_content_locator = page.locator("div.ResourceCards__CardDom-dzFtxX:has(span:text('Server')) span.ResourceCards__ValueText-jMQaIH.fZMedF")

                # 위젯이 화면에 표시되는지 확인
                inner_content_visible = inner_content_locator.is_visible()

                assert inner_content_visible, f"[Server] 위젯 UI [>] 버튼 표시 확인 실패"
                log_result(True, f"[Server] 위젯 UI: 화면에 정상 표시됨 (성공)")
                test_results.append(f"[Server] 위젯 UI: 화면에 정상 표시됨 (성공)")

            except AssertionError as e:
                # Assertion 실패 시 로그와 결과 기록, 코드 중단 없이 다음 항목으로 넘어감
                logging.error(f"검증 실패: {str(e)}")
                log_result(False, str(e))
                test_results.append(str(e))

            except Exception as e:
                # 기타 예외 처리, 코드 중단 없이 다음 항목으로 넘어감
                logging.error(f"오류 발생: {str(e)}")
                log_result(False, f"예외 발생: {str(e)}")
                test_results.append(f"예외 발생: {str(e)}")


            #Progress Bar 차트 표시 확인
            try:
                logging.info("[Server] 위젯 UI Value Text 표시 확인 중")
                inner_content_locator = page.locator("div.ResourceCards__CardDom-dzFtxX:has(span:text('Server')) div.ant-progress.ant-progress-line.ant-progress-status-active.ant-progress-default")

                # 위젯이 화면에 표시되는지 확인
                inner_content_visible = inner_content_locator.is_visible()

                assert inner_content_visible, f"[Server] 위젯 UI [>] 버튼 표시 확인 실패"
                log_result(True, f"[Server] 위젯 UI: 화면에 정상 표시됨 (성공)")
                test_results.append(f"[Server] 위젯 UI: 화면에 정상 표시됨 (성공)")

            except AssertionError as e:
                # Assertion 실패 시 로그와 결과 기록, 코드 중단 없이 다음 항목으로 넘어감
                logging.error(f"검증 실패: {str(e)}")
                log_result(False, str(e))
                test_results.append(str(e))

            except Exception as e:
                # 기타 예외 처리, 코드 중단 없이 다음 항목으로 넘어감
                logging.error(f"오류 발생: {str(e)}")
                log_result(False, f"예외 발생: {str(e)}")
                test_results.append(f"예외 발생: {str(e)}")


            #Progress Bar 텍스트 표시 확인
            try:
                logging.info("[Server] 위젯 UI Value Text 표시 확인 중")
                inner_content_locator = page.locator("div.ResourceCards__CardDom-dzFtxX:has(span:text('Server')) div.ResourceCards__ProgressLabels-jdjbop.bkmXSU")

                # 위젯이 화면에 표시되는지 확인
                inner_content_visible = inner_content_locator.is_visible()

                assert inner_content_visible, f"[Server] 위젯 UI [>] 버튼 표시 확인 실패"
                log_result(True, f"[Server] 위젯 UI: 화면에 정상 표시됨 (성공)")
                test_results.append(f"[Server] 위젯 UI: 화면에 정상 표시됨 (성공)")

            except AssertionError as e:
                # Assertion 실패 시 로그와 결과 기록, 코드 중단 없이 다음 항목으로 넘어감
                logging.error(f"검증 실패: {str(e)}")
                log_result(False, str(e))
                test_results.append(str(e))

            except Exception as e:
                # 기타 예외 처리, 코드 중단 없이 다음 항목으로 넘어감
                logging.error(f"오류 발생: {str(e)}")
                log_result(False, f"예외 발생: {str(e)}")
                test_results.append(f"예외 발생: {str(e)}")





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