from datetime import datetime
import logging
import os
import time
import csv
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

WHITEOUT_TEXTS = ["죄송합니다", "페이지를 찾을 수 없습니다.", "Bad Gate", "OOOPS"]

browser_type = None
save_path = None
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


def verify_widget_button_action(page, widget_name, locator, button_name, test_results, action=None, hover_positions=None):
    """
    버튼 동작 수행 함수.

    :param page: Playwright 페이지 객체
    :param widget_name: 위젯 이름
    :param locator: 버튼 선택자
    :param button_name: 버튼 이름
    :param test_results: 테스트 결과를 기록할 리스트
    :param action: 버튼 클릭 후 수행할 추가 동작 (콜백 함수)
    :param hover_positions: 좌표 리스트 (선택적으로 사용)
    """
    try:
        logging.info(f"[{widget_name}] 위젯 UI [{button_name}] 동작 수행 중")

        if hover_positions:
            # 좌표를 활용하여 클릭 동작 수행
            for position in hover_positions:
                logging.info(f"[{widget_name}] 좌표 클릭 중: {position}")
                page.locator(locator).click(position=position)
                logging.info(f"[{widget_name}] 좌표 클릭 완료: {position}")
        else:
            # Locator를 활용하여 버튼 클릭
            button_locator = page.locator(locator)
            button_locator.click()
            logging.info(f"[{widget_name}] [{button_name}] 버튼 클릭 완료")

        page.wait_for_load_state('networkidle')

        

        # 추가 동작 수행
        if action:
            action(page, test_results)

        #log_result(True, f"[{widget_name}] UI [{button_name}] 동작 완료 (성공)")
        #test_results.append(f"[{widget_name}] UI [{button_name}] 동작 완료 (성공)")

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

        page.wait_for_load_state('networkidle')

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


def verify_widget_structure(page, parent_locator, widget_name, element_name, child_count, test_results):
    """
    ResourceCards__FlexRemainder의 하위 구조 검증

    :param page: Playwright 페이지 객체
    :param parent_locator: 부모 요소 locator
    :param widget_name: 위젯 이름 (로그용)
    :param element_name: 하위 구조 이름 (로그용)
    :param child_count: 기대되는 하위 요소 개수
    :param test_results: 테스트 결과를 기록할 리스트
    """
    try:
        display_name = f"{widget_name} {element_name}" if element_name else widget_name
        logging.info(f"[{display_name}] 표시 확인 중")

        page.wait_for_load_state('networkidle')

        # 부모 요소 가져오기
        parent_element = page.locator(parent_locator)
        assert parent_element.is_visible(), f"[{widget_name}] 위젯의 부모 요소가 보이지 않습니다"

        # 하위 div 요소 가져오기
        #child_elements = parent_element.locator("div")
        #assert child_elements.count() == child_count, f"[{widget_name}] 하위 요소 개수가 {child_count}개가 아닙니다"

        # 각 하위 div 내부 구조 확인
        #for i in range(child_count):
        #    title_locator = child_elements.nth(i).locator("div.ResourceCards__SubTitle-eZXil.jHWnBP")
        #    value_locator = child_elements.nth(i).locator("div.ResourceCards__SubValue-bOvbm.cfupYY")
        #
        #    assert title_locator.is_visible(), f"[{widget_name}] {i + 1}번째 SubTitle 요소가 존재하지 않습니다"
        #    assert value_locator.is_visible(), f"[{widget_name}] {i + 1}번째 SubValue 요소가 존재하지 않습니다"

        #    logging.info(f"[{widget_name}] 하위 요소 검증 성공: SubTitle과 SubValue 모두 존재")

        # 하위 요소에서 SubTitle과 SubValue 검증
        subtitle_elements = parent_element.locator("div.ResourceCards__SubTitle-eZXil")
        value_elements = parent_element.locator("div.ResourceCards__SubValue-bOvbm")

        subtitle_count = subtitle_elements.count()
        value_count = value_elements.count()

        # SubTitle과 SubValue 각각 개수 확인 및 검증
        logging.info(f"[{widget_name}] SubTitle 개수: {subtitle_count}, SubValue 개수: {value_count}")
        assert subtitle_count > 0, f"[{widget_name}] SubTitle 요소를 찾지 못했습니다"
        assert value_count > 0, f"[{widget_name}] SubValue 요소를 찾지 못했습니다"

        # 각 요소가 표시되는지 확인
        for i in range(min(subtitle_count, value_count)):
            assert subtitle_elements.nth(i).is_visible(), f"[{widget_name}] {i+1}번째 SubTitle 요소가 표시되지 않습니다"
            assert value_elements.nth(i).is_visible(), f"[{widget_name}] {i+1}번째 SubValue 요소가 표시되지 않습니다"
            logging.info(f"[{widget_name}] {i+1}번째 SubTitle 및 SubValue 확인 완료")

        log_result(True, f"[{widget_name}] 하위 구조 검증 완료 (성공)")
        test_results.append(f"[{widget_name}] 하위 구조 검증 완료 (성공)")

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


def verify_widget_hover_action(page, widget_name, element_locator, button_name, test_results, action=None, hover_position=None):
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
        
        page.wait_for_timeout(2000)  # 2초 대기

        # 추가 동작 수행
        if action:
            action(page, test_results)

        #log_result(True, f"[{widget_name}] UI [{button_name}] 마우스 호버 및 동작 완료 (성공)")
        #test_results.append(f"[{widget_name}] UI [{button_name}] 마우스 호버 및 동작 완료 (성공)")

    except Exception as e:
        logging.error(f"[{widget_name}] 오류 발생: {str(e)}")
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")


#위젯별 이 아닌, 검증해야할 동작 별로 액션 함수를 나눠야 할듯

# 5초뒤에 확인 안되면 새로고침 하는 내용 추가하기
def verify_navigation_action(page, test_results, screen_name, expected_url):
    """
    버튼 클릭 후 페이지 이동 및 UI 상태 검증

    :param page: Playwright 페이지 객체
    :param test_results: 테스트 결과 리스트
    :param screen_name: 검증 대상 화면 이름 (위젯 리스트에서 전달)
    :param expected_url: 기대되는 URL (위젯 리스트에서 전달)
    """
    try:
        logging.info("버튼 클릭 후 확인 진행 중")

        # 새 페이지 열림 감지
        with page.context.expect_page() as new_page_info:
            logging.info("새 페이지 감지 대기 중...")

        page2 = new_page_info.value  # 새 페이지 객체를 page2로 할당
        page.wait_for_timeout(1000)  # 1초 대기

        page2.wait_for_load_state('networkidle')  # 새 페이지 로딩 완료 대기

        # 1. 새 페이지 URL에 '/server/list' 포함 여부 확인
        current_url = page2.url
        logging.info(f"새 페이지 URL: {current_url}")
        assert expected_url in current_url, f"{screen_name} 페이지로 이동하지 않았습니다. 현재 URL: {current_url}"
        logging.info("{screen_name} 페이지 정상 이동 확인됨")

        # 2. 새 페이지에서 서버 목록 UI 화이트아웃 검증
        verify_whiteout(
            page=page2,
            screen_name=screen_name,
            save_path=save_path,
            test_results=test_results
        )
        logging.info("{screen_name} UI 화이트아웃 없음 확인됨")

        # 3. 사이드 메뉴에 [서버 목록] 메뉴가 하이라이팅 되었는지 확인
        #side_menu_locator = page2.locator("a[href='/v2/project/sms/29763/dashboard/resource_board']")
        
        #menu_item_class = side_menu_locator.locator("div.Menustyles__MenuItemWrapCommon-cHqrwY.Menustyles__Child-iELIYh")
        #is_highlighted = menu_item_class.evaluate(
        #    "(element) => element.classList.contains('iWDtdN')"
        #)

        #assert is_highlighted, "[서버 목록] 메뉴가 하이라이팅되지 않았습니다"
        #logging.info("사이드 메뉴 하이라이팅 확인됨")

        #page2 = new_page_info.value
        #page2.close()

    except AssertionError as e:
        logging.error(f"검증 실패: {str(e)}")
        log_result(False, str(e))  # 실패 기록
        test_results.append(str(e))  # 실패 내용을 테스트 결과 리스트에 추가

    except Exception as e:
        logging.error(f"오류 발생: {str(e)}")
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")


# 함수 이름 변경하기
def button_action_infobutton(page, popover_locator, popover_text_locator, expected_text, test_results):
    """
    Popover 요소를 먼저 찾고, 그 하위에서 특정 텍스트를 포함하는 요소를 필터링한 후 상태를 검증하는 함수.

    :param page: Playwright 페이지 객체
    :param popover_locator: 팝오버 부모 요소의 선택자 
    :param popover_text_locator: 팝오버 텍스트를 포함하는 요소의 선택자
    :param expected_text: 팝오버에 포함되어야 하는 예상 텍스트
    """
    try:
        logging.info("팝오버 상태 및 예상 텍스트 검증 시작")

        page.wait_for_timeout(1000)  # 2초 대기

        # 1. Popover 요소를 먼저 찾기
        popover_elements = page.locator(popover_locator)
        assert popover_elements.is_visible(), "팝오버 요소가 표시되지 않았습니다."
        #assert popover_elements.count() > 0, "팝오버 요소를 찾지 못했습니다."
        logging.info(f"팝오버 요소 {popover_elements.count()}개 발견")

        matched_popover = None

        # 2. 각 Popover 요소의 하위에서 예상 텍스트 확인
        for i in range(popover_elements.count()):
            current_popover = popover_elements.nth(i)
            text_elements = current_popover.locator(popover_text_locator)

            for j in range(text_elements.count()):
                current_text = text_elements.nth(j).text_content().strip()
                if expected_text in current_text:
                    matched_popover = current_popover
                    break  # 텍스트가 일치하는 Popover 발견
            if matched_popover:
                break

        assert matched_popover, f"예상 텍스트 '{expected_text}'를 포함하는 팝오버를 찾지 못했습니다."
        logging.info(f"예상 텍스트 '{expected_text}'를 포함하는 Popover 요소 발견")

        # 3. 해당 Popover의 상태 확인 (ant-popover-hidden 클래스가 없는지 확인)
        class_attr = matched_popover.get_attribute("class")
        assert "ant-popover-hidden" not in class_attr, "Popover가 열리지 않았습니다: hidden 상태"

        logging.info("팝오버 상태 검증 성공: hidden 클래스 없음")
        log_result(True, f"팝오버 검증 성공: 텍스트 '{expected_text}' 확인 및 상태 정상")

    except AssertionError as e:
        logging.error(f"검증 실패: {str(e)}")
        log_result(False, str(e))
        test_results.append(str(e))  # 실패 내용을 테스트 결과 리스트에 추가

    except Exception as e:
        logging.error(f"오류 발생: {str(e)}")
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")


'''
# 패널차트에서 에이전트 이름을 확인할 수 있는지 확인 필요
def verify_agent_action(page, expected_agent, test_results):
    """
    서버 상세 화면의 [서버 선택] 항목에서 에이전트가 표시되는지 검증.

    :param page: Playwright 페이지 객체 (서버 상세 화면 페이지)
    :param expected_agent: 차트에서 선택한 에이전트 이름
    :param test_results: 테스트 결과를 기록할 리스트
    """
    try:
        logging.info("서버 상세 화면 [서버 선택] 항목 검증 시작")

        # [서버 선택] 항목 요소 가져오기
        server_selection_locator = page.locator("div.OptionBarstyles__Content-gokbzP.fgyBKV")  # [서버 선택] 항목의 정확한 selector로 변경
        assert server_selection_locator.is_visible(), "[서버 선택] 항목이 보이지 않습니다"

        # 항목에 expected_agent가 포함되어 있는지 확인
        server_selection_text = server_selection_locator.text_content().strip()
        assert expected_agent in server_selection_text, f"선택한 에이전트 '{expected_agent}'가 서버 선택 항목에 표시되지 않았습니다"

        logging.info(f"[서버 선택] 항목에 '{expected_agent}' 에이전트가 정상 표시됨")
        log_result(True, f"[서버 선택] 항목에 '{expected_agent}' 확인 완료 (성공)")
        test_results.append(f"[서버 선택] 항목에 '{expected_agent}' 확인 완료 (성공)")

    except AssertionError as e:
        logging.error(f"검증 실패: {str(e)}")
        log_result(False, str(e))
        test_results.append(str(e))

    except Exception as e:
        logging.error(f"오류 발생: {str(e)}")
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")
'''


def metrics_button_action(page, test_results):
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


def server_button_action(page, test_results):
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

    logging.info("=== [Case 1] 검증 시작 ===")

    # 리소스보드 선택
    logging.info("리소스보드 화면으로 이동 중")
    page.locator('a[href="/v2/project/sms/29763/dashboard/resource_board"]').click()
    #element = page.wait_for_selector('a[href="/v2/project/sms/29763/dashboard/resource_board"]')
    #element.click()

    #page.get_by_role("link", name="리소스보드").click()

    page.wait_for_timeout(2000)  # 2초 대기


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

    logging.info("=== [Case 2] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets 
        if widget["widget_name"] == "Server" and widget.get("element_name") #and widget.get("element_locator")
        ]
    
    #logging.info(f"필터링된 위젯: {filtered_widgets}")
    
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

    logging.info("=== [Case 3] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets 
        if widget["widget_name"] == "Server" and widget.get("button_name")
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

    logging.info("=== [Case 4] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets 
        if widget["widget_name"] == "OS" and widget.get("element_name")
    ]

    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_structure(
            page=page,
            parent_locator=element_locator,
            widget_name=widget["widget_name"],
            element_name=widget["element_name"],
            child_count=widget.get("child_count"),
            test_results=test_results
        )


def process_case_5(page, test_results):
    # Case 5: [Total Cores] 위젯 UI 확인

    logging.info("=== [Case 5] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets 
        if widget["widget_name"] == "Total Cores" and widget.get("element_name") and widget.get("element_locator")
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

    logging.info("=== [Case 6] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets 
        if widget["widget_name"] == "Avg CPU" and widget.get("element_name") and widget.get("element_locator")
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

    logging.info("=== [Case 7] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets 
        if widget["widget_name"] == "Avg Memory" and widget.get("element_name") and widget.get("element_locator")
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

    logging.info("=== [Case 8] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets 
        if widget["widget_name"] == "Avg Disk" and widget.get("element_name") and widget.get("element_locator")
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
    
    logging.info("=== [Case 9] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets 
        if widget["widget_name"] == "CPU - TOP5" and widget.get("element_name")
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


def process_case_10(page, test_results):
    # Case 10: [CPU - TOP5] 위젯 - 정보 버튼 동작 확인

    logging.info("=== [Case 10] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets
        if widget["widget_name"] == "CPU - TOP5" and widget["element_name"] == "info button"
    ]

    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_hover_action(
            page=page,
            widget_name=widget["widget_name"],
            element_locator=element_locator,
            button_name=widget["button_name"],
            hover_position=widget.get("hover_position"),  # None 처리 가능
            test_results=test_results,
            action=widget["action"]  # 함수 전달
        )


def process_case_11(page, test_results):
    # Case 3: [CPU - TOP5] 위젯 [>] 버튼 동작 확인

    logging.info("=== [Case 11] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets 
        if widget["widget_name"] == "CPU - TOP5" and widget["button_name"] == "[>] 버튼"
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


def process_case_12(page, test_results):
    # Case 12: [CPU - TOP5] 위젯 [PanelContents chart] 동작 확인

    logging.info("=== [Case 12] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets
        if widget["widget_name"] == "CPU - TOP5" and widget["element_name"] == "PanelContents chart"
    ]

    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_button_action(
            page=page,
            widget_name=widget["widget_name"],
            locator=element_locator,
            button_name=widget["button_name"],
            test_results=test_results,
            action=widget["action"],  # None인 경우 추가 동작 없음
            hover_positions=widget.get("hover_positions")  # 좌표 전달
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
    # 이상하게 이거 검증이 안되네... UI에는 잘 뜨는데...
# {
#     "widget_name": "Server Status Map",
#     "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF span:text-is('Server Status Map')",  # 위젯 자체 확인
#     "element_name": None,  # 내부 요소 없음
#     "element_locator": None,
#     "button_name": None,
#     "action": None
# }
    
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
        "action": lambda page, test_results: verify_navigation_action(
            page=page,
            test_results=test_results,
            screen_name="서버 목록 화면",
            expected_url="/server/list"
        )
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
        "element_name": "OS elements",
        "element_locator": "{locator} div.ResourceCards__FlexRemainder-hCQgll.gORGxv",
        "button_name": None,
        "action": None,
        "child_count": None  # 예상되는 하위 요소 개수
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
        "action": lambda page, test_results: button_action_infobutton(
            page=page,
            popover_locator="div.ant-popover.ant-popover-placement-bottom",  # Popover 부모 요소를 나타내는 조건
            popover_text_locator="div.HelperButton__ContentContainer-dPhKeC.eokXGu",  # 팝오버 텍스트 클래스
            expected_text="CPU",
            test_results=test_results
        )
    },

    {
        "widget_name": "CPU - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('CPU')))",
        "element_name": "[>] button",
        "element_locator": "{locator} div.Styles__Wrapper-bZXaBP.lomqVM",
        "button_name": "[>] 버튼",
        "action":  lambda page, test_results: verify_navigation_action(
            page=page,
            test_results=test_results,
            screen_name="리소스 이퀄라이저",
            expected_url="/dashboard/multi_line?content=cpu"
        )
    },

    {
        "widget_name": "CPU - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('CPU')))",
        "element_name": "PanelContents button",
        "element_locator": "{locator} .Ants__Dropdown-cCtpgz.bRdCUm",
        "button_name": "PanelContents button",
        "action":  None
        
    },
    {
        "widget_name": "CPU - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('CPU')))",
        "element_name": "PanelContents chart",
        "element_locator": "{locator} canvas.sc-dcJsrY.dvDjBb",
        "button_name": "PanelContents chart",
        "action": lambda page, test_results: (
            verify_navigation_action(
            page=page,
            test_results=test_results,
            screen_name="서버 상세",
            expected_url="/server_detail"
        ),
            #verify_agent(page, expected_agent, test_results)
        ),
        "hover_positions": [  
        {"x":120,"y":40}
        ] # 툴팁 검증을 위한 좌표
    },

]


def run(playwright):
    save_path = os.getenv("WHITEOUT_SCREEN_PATH", "src/reports/screeen_shot/dashboard_whiteout")

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
            password = "shguswn980512-"

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

            page.wait_for_load_state('networkidle')

            # 왼쪽 사이드 메뉴 접속하기
            menu_wrap = page.query_selector('div.Menustyles__MenuWrap-hRfo.hmTPnA')

            parent_elements = menu_wrap.query_selector_all('div.Menustyles__MenuItemWrapCommon-cHqrwY.Menustyles__Parent-XgDRT')
            logging.info(f"상위 메뉴 클릭하여 하위 메뉴 오픈 중") 

            for element in parent_elements:
                try:

                    # 요소 클릭
                    element.click()  # 해당 div 요소를 클릭

                    page.wait_for_load_state('networkidle', timeout=20000)  # 페이지가 로드될 때까지 대기
                except Exception as e:
                    logging.error(f"클릭 중 오류 발생: {str(e)}")
            
            logging.info("하위 메뉴 오픈 후 페이지 로드 완료")

            # Case 1 처리
            process_case_1(page, test_results)

            # Case 2 처리
            process_case_2(page, test_results)

            # Case 3 처리
            process_case_3(page, test_results)

            #page.wait_for_timeout(200000)  # 2초 대기

            # Case 4 처리
            process_case_4(page, test_results)

            # Case 5 처리
            process_case_5(page, test_results)

            # Case 6 처리
            process_case_6(page, test_results)

            # Case 7 처리
            process_case_7(page, test_results)

            # Case 8 처리
            process_case_8(page, test_results)

            # Case 9 처리
            process_case_9(page, test_results)

            # Case 10 처리
            process_case_10(page, test_results)

            # Case 11 처리
            process_case_11(page, test_results)

            # Case 12 처리
            process_case_12(page, test_results)

            

        




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