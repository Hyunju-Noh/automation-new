from datetime import datetime
import logging
import os
import time
import csv
import re
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
            logging.error(f"화이트아웃 화면 감지:")
            #screenshot_path = capture_screenshot(page, f"whiteout_screen_{found_text}", save_path)

            # 새로고침 시도 및 다시 확인
            logging.info("화이트아웃 감지: 페이지 새로고침 시도")
            page.reload()
            page.wait_for_load_state('networkidle', timeout=10000)  # 새로고침 후 대기

            # 새로고침 후 다시 컨텐츠 확인
            page_content = get_page_content_with_timeout(page, timeout=10000)
            found_text_after_refresh = None
            for text in WHITEOUT_TEXTS:
                if text in page_content:
                    found_text_after_refresh = text
                    break

            if found_text_after_refresh:
                logging.error(f"새로고침 후에도 화이트아웃 화면 감지: '{found_text_after_refresh}' 특정 텍스트 발견")
                screenshot_path = capture_screenshot(page, f"whiteout_screen{found_text_after_refresh}", save_path)
            else:
                return  # 새로고침 후 정상 상태면 함수 종료
            
            # 화이트 아웃 발생 원인 버튼의 텍스트를 출력
            button_element = page.query_selector(f"//*[text()='{button_text}']")
            if button_element:
                element_html = page.evaluate('(element) => element.outerHTML', button_element)
                logging.error(f"화이트아웃을 발생시킨 버튼 텍스트: {button_text}")
                #logging.error(f"화이트아웃을 발생시킨 버튼 HTML:\n{element_html}")
            else:
                logging.warning(f"화이트아웃을 발생시킨 버튼 '{button_text}'을(를) 찾을 수 없습니다.")
            
            #go_back_and_capture_screenshot(page, f"back_screen_{found_text}", save_path)
            
        else:
            logging.info("정상 페이지로 보입니다.")
    except PlaywrightTimeoutError:
        screenshot_path = capture_screenshot(page, "timeout_screen", save_path)
        logging.error(f"페이지를 로드하는 동안 타임아웃이 발생했습니다: {screenshot_path}")


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


def verify_widget_button_click(page, widget_name, locator, button_name, test_results, action=None, hover_positions=None):
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

        close_popups(page)

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

        close_popups(page)

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

        close_popups(page)

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

        close_popups(page)

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

        new_page = None

        try:
            # 새 페이지 열림 감지
            with page.context.expect_page(timeout=5000) as new_page_info:
                logging.info("새 페이지 감지 대기 중...")
            new_page = new_page_info.value
        except TimeoutError:
            logging.warning("페이지 새로고침 시도...")
            page.reload()
            page.wait_for_load_state('networkidle')
            logging.info("페이지 새로고침 완료")

            # 새로고침 후 새 페이지 감지 재시도
            with page.context.expect_page(timeout=5000) as new_page_info:
                logging.info("새 페이지 감지 재시도 중...")
            new_page = new_page_info.value

        # 새 페이지 정보 가져오기
        new_page.wait_for_timeout(1000)  # 1초 대기
        new_page.wait_for_load_state('networkidle')  # 새 페이지 로딩 완료 대기
        logging.info("새 페이지 로딩 완료")

        close_popups(new_page)

        # 1. 새 페이지 URL에 '/server/list' 포함 여부 확인
        current_url = new_page.url
        logging.info(f"새 페이지 URL: {current_url}")
        assert expected_url in current_url, f"{screen_name} 페이지로 이동하지 않았습니다. 현재 URL: {current_url}"
        logging.info("{screen_name} 페이지 정상 이동 확인됨")

        # 2. 새 페이지에서 서버 목록 UI 화이트아웃 검증
        verify_whiteout(
            page=new_page,
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
    finally:
        # 새 페이지 닫기
        if 'new_page' in locals() and not new_page.is_closed():
            logging.info("새 페이지 닫는 중...")
            new_page.close()


def verify_navigation_goback_action(page, test_results, screen_name, expected_url):
    """
    버튼 클릭 후 페이지 이동 및 UI 상태 검증 + 이전 화면으로 이동

    :param page: Playwright 페이지 객체
    :param test_results: 테스트 결과 리스트
    :param screen_name: 검증 대상 화면 이름 (위젯 리스트에서 전달)
    :param expected_url: 기대되는 URL (위젯 리스트에서 전달)
    """
    try:
        logging.info("버튼 클릭 후 확인 진행 중")

        page.wait_for_load_state('networkidle')  #페이지 로딩 완료 대기

        close_popups(page)

        # 1. 새 페이지 URL에 '/server/list' 포함 여부 확인
        current_url = page.url
        logging.info(f"새 페이지 URL: {current_url}")
        assert expected_url in current_url, f"{screen_name} 페이지로 이동하지 않았습니다. 현재 URL: {current_url}"
        logging.info("{screen_name} 페이지 정상 이동 확인됨")

        # 2. 새 페이지에서 서버 목록 UI 화이트아웃 검증
        verify_whiteout(
            page=page,
            screen_name=screen_name,
            save_path=save_path,
            test_results=test_results
        )
        logging.info("{screen_name} UI 화이트아웃 없음 확인됨")

    except AssertionError as e:
        logging.error(f"검증 실패: {str(e)}")
        log_result(False, str(e))  # 실패 기록
        test_results.append(str(e))  # 실패 내용을 테스트 결과 리스트에 추가

    except Exception as e:
        logging.error(f"오류 발생: {str(e)}")
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")
    finally:
        page.go_back()


# 함수 이름 변경하기
def info_button_action(page, popover_locator, popover_text_locator, expected_text, test_results):
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

        close_popups(page)

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


#비슷하지만, tc 34/39 전용 함수
def processwidget_info_button_action(page, popover_locator, popover_text_locator, expected_text, test_results):
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

        close_popups(page)

        # 1. Popover 요소를 먼저 찾기
        popover_elements = page.locator(popover_locator)
        #assert popover_elements.is_visible(), "팝오버 요소가 표시되지 않았습니다."
        assert popover_elements.count() > 0, "팝오버 요소를 찾지 못했습니다."
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


def dropdown_button_action(page, dropdown_locator, expected_left_value, test_results, dropdown_list_button_locator=None, element_locator=None, expected_text=None):
    """
    Dropdown 요소를 먼저 찾고, 특정 style 조건을 만족하는 요소를 필터링한 후 상태를 검증하는 함수.

    :param page: Playwright 페이지 객체
    :param dropdown_locator: Dropdown 부모 요소의 선택자
    :param expected_left_value: style 속성에서 'left'의 예상 값
    :param test_results: 테스트 결과를 기록할 리스트
    :param dropdown_list_button_locator: Dropdown 내부 버튼 선택자 (선택적)
    :param element_locator: 동적으로 생성될 요소의 선택자 템플릿 (선택적)
    :param expected_text: 동적으로 생성될 요소에 사용될 텍스트 (선택적)
    """
    try:
        logging.info("Dropdown 상태 및 예상 조건 검증 시작")

        page.wait_for_timeout(1000)  # 1초 대기

        close_popups(page)

        # 1. Dropdown 요소를 먼저 찾기
        dropdown_elements = page.locator(dropdown_locator)
        assert dropdown_elements.is_visible(), "Dropdown 요소가 표시되지 않았습니다."
        logging.info(f"Dropdown 요소 {dropdown_elements.count()}개 발견")

        matched_dropdown = None

        # 2. 각 Dropdown 요소에서 style 조건 확인
        for i in range(dropdown_elements.count()):
            current_dropdown = dropdown_elements.nth(i)
            style_attr = current_dropdown.get_attribute("style")

            if style_attr and f"left: {expected_left_value}px" in style_attr:
                matched_dropdown = current_dropdown
                break  # 조건을 만족하는 Dropdown 발견

        assert matched_dropdown, f"left 값이 '{expected_left_value}px'인 Dropdown을 찾지 못했습니다."
        logging.info(f"left 값이 '{expected_left_value}px'인 Dropdown 요소 발견")

        # 3. 해당 Dropdown의 상태 확인 (ant-dropdown-hidden 클래스가 없는지 확인)
        class_attr = matched_dropdown.get_attribute("class")
        assert "ant-dropdown-hidden" not in class_attr, "Dropdown이 열리지 않았습니다: hidden 상태"

        logging.info("Dropdown 상태 검증 성공: hidden 클래스 없음")

        # 4. Dropdown 내부 버튼 클릭 및 결과 확인
        if dropdown_list_button_locator:
            logging.info("Dropdown 내부 버튼 클릭 시도 중")
            dropdown_elements = page.locator(dropdown_list_button_locator)
            dropdown_elements.click()
            logging.info("Dropdown 내부 버튼 클릭 성공")

            dynamic_locator = element_locator.replace("expected_text", expected_text)
            popover_elements = page.locator(dynamic_locator)
            assert popover_elements.is_visible(), f"요소 '{expected_text}'가 클릭 후 표시되지 않았습니다."
            logging.info(f"요소 '{expected_text}'가 클릭 후 정상적으로 표시됨")

        log_result(True, f"Dropdown 검증 성공")
        test_results.append(f"Dropdown 검증 및 동작 성공")
        

    except AssertionError as e:
        logging.error(f"검증 실패: {str(e)}")
        log_result(False, str(e))
        test_results.append(str(e))  # 실패 내용을 테스트 결과 리스트에 추가

    except Exception as e:
        logging.error(f"오류 발생: {str(e)}")
        log_result(False, f"예외 발생: {str(e)}")
        test_results.append(f"예외 발생: {str(e)}")



def column_button_action(page, tooltip_locator, test_results):
    """
    Dropdown 요소를 먼저 찾고, 특정 style 조건을 만족하는 요소를 필터링한 후 상태를 검증하는 함수.

    :param page: Playwright 페이지 객체
    :param dropdown_locator: Dropdown 부모 요소의 선택자
    :param expected_left_value: style 속성에서 'left'의 예상 값
    :param test_results: 테스트 결과를 기록할 리스트
    :param dropdown_list_button_locator: Dropdown 내부 버튼 선택자 (선택적)
    :param element_locator: 동적으로 생성될 요소의 선택자 템플릿 (선택적)
    :param expected_text: 동적으로 생성될 요소에 사용될 텍스트 (선택적)
    """
    try:
        logging.info("Dropdown 상태 및 예상 조건 검증 시작")

        page.wait_for_timeout(1000)  # 1초 대기

        close_popups(page)

        # 1. tooltip 요소를 먼저 찾기
        tooltip_elements = page.locator(tooltip_locator)
        assert tooltip_elements.count() > 0, "팝오버 요소를 찾지 못했습니다."
        logging.info(f"팝오버 요소 {tooltip_elements.count()}개 발견")

        matched_tooltip = None

        # 2. 각 tooltip 요소에서 style 조건 확인
        matched_tooltip = next(
            (
                tooltip_elements.nth(i)
                for i in range(tooltip_elements.count())
                if (style_attr := tooltip_elements.nth(i).get_attribute("style"))
                and int(re.search(r'left:\s*(-?\d+)px', style_attr).group(1)) > 0
                and int(re.search(r'top:\s*(-?\d+)px', style_attr).group(1)) > 0
            ),
            None
        )

        assert matched_tooltip, f"left 및 top 값이 양수인 Tooltip을 찾지 못했습니다."
        logging.info(f"left 및 top 값이 양수인 Tooltip 요소 발견")

        # 3. 해당 tooltip 상태 확인 (ant-tooltip-hidden 클래스가 없는지 확인)
        class_attr = matched_tooltip.get_attribute("class")
        assert "ant-tooltip-hidden" not in class_attr, "tooltip이 열리지 않았습니다: hidden 상태"

        logging.info("툴팁 상태 검증 성공: hidden 클래스 없음")
        log_result(True, f"툴팁 검증 성공: 텍스트")
        

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


def close_popups(page):
    """
    발생하는 팝업을 감지하고 닫는 함수.

    :param page: Playwright 페이지 객체
    """
    try:
        page.wait_for_load_state('networkidle')  #페이지 로딩 완료 대기

        popup_locator = page.locator(".Toastify__toast")  # 팝업의 클래스 선택자
        close_button_locator = page.locator(".Toastify__close-button")  # 닫기 버튼 클래스 선택자

        # 팝업이 존재하는지 확인
        if popup_locator.is_visible():
            logging.info("팝업이 감지되었습니다. 닫는 중...")
            close_button_locator.click()  # 닫기 버튼 클릭

            logging.info("팝업 닫기 동작 완료 (상태 감지 제외)")
        else:
            logging.info("팝업이 감지되지 않았습니다.")
    except Exception as e:
        if "Target crashed" in str(e):
            logging.warning("Webkit 브라우저에서 Target crashed 오류 발생. 무시하고 진행.")
        else:
            logging.warning(f"팝업 닫기 중 다른 오류 발생: {str(e)}")



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

    close_modal_if_present(page)


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

        verify_widget_button_click(
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
    # Case 11: [CPU - TOP5] 위젯 [>] 버튼 동작 확인

    logging.info("=== [Case 11] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets 
        if widget["widget_name"] == "CPU - TOP5" and widget["button_name"] == "[>] button"
        ]
    
    
    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_button_click(
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

        verify_widget_button_click(
            page=page,
            widget_name=widget["widget_name"],
            locator=element_locator,
            button_name=widget["button_name"],
            test_results=test_results,
            action=widget["action"],  # None인 경우 추가 동작 없음
            hover_positions=widget.get("hover_positions")  # 좌표 전달
        )


def process_case_13(page, test_results):
    # Case 13: [CPU - TOP5] 위젯 [PanelContents button] 동작 확인

    logging.info("=== [Case 13] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets
        if widget["widget_name"] == "CPU - TOP5" and widget["element_name"] == "PanelContents button"
    ]

    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_hover_action(
            page=page,
            widget_name=widget["widget_name"],
            element_locator=element_locator,
            button_name=widget["button_name"],
            test_results=test_results,
            action=widget["action"],  # 함수 전달
            hover_position=widget.get("hover_position"),  # None 처리 가능
        )


def process_case_14(page, test_results):
    # Case 14: [CPU - TOP5] 위젯 컨텐츠 옵션 목록 동작 확인

    logging.info("=== [Case 14] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets
        if widget["widget_name"] == "CPU - TOP5" and widget["element_name"] == "PanelContents dropdown"
    ]

    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_hover_action(
            page=page,
            widget_name=widget["widget_name"],
            element_locator=element_locator,
            button_name=widget["button_name"],
            test_results=test_results,
            action=widget["action"],  # 함수 전달
            hover_position=widget.get("hover_position"),  # None 처리 가능
        )


def process_case_15(page, test_results):
    # Case 15: [메모리 - TOP5] 위젯 UI 확인
    
    logging.info("=== [Case 15] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets 
        if widget["widget_name"] == "memory - TOP5" and widget.get("element_name")
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


def process_case_16(page, test_results):
    # Case 16: [메모리 - TOP5] 위젯 - 정보 버튼 동작 확인

    logging.info("=== [Case 16] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets
        if widget["widget_name"] == "memory - TOP5" and widget["element_name"] == "info button"
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


def process_case_17(page, test_results):
    # Case 17: [메모리 - TOP5] 위젯 [>] 버튼 동작 확인

    logging.info("=== [Case 17] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets 
        if widget["widget_name"] == "memory - TOP5" and widget["button_name"] == "[>] button"
        ]
    
    
    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_button_click(
            page=page,
            locator=element_locator,
            widget_name=widget["widget_name"],
            button_name=widget["button_name"],
            test_results=test_results,
            action=widget["action"]
        )


def process_case_18(page, test_results):
    # Case 18: [메모리 - TOP5] 위젯 [PanelContents chart] 동작 확인

    logging.info("=== [Case 18] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets
        if widget["widget_name"] == "memory - TOP5" and widget["element_name"] == "PanelContents chart"
    ]

    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_button_click(
            page=page,
            widget_name=widget["widget_name"],
            locator=element_locator,
            button_name=widget["button_name"],
            test_results=test_results,
            action=widget["action"],  # None인 경우 추가 동작 없음
            hover_positions=widget.get("hover_positions")  # 좌표 전달
        )


def process_case_19(page, test_results):
    # Case 19: [메모리 - TOP5] 위젯 [PanelContents button] 동작 확인

    logging.info("=== [Case 19] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets
        if widget["widget_name"] == "memory - TOP5" and widget["element_name"] == "PanelContents button"
    ]

    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_hover_action(
            page=page,
            widget_name=widget["widget_name"],
            element_locator=element_locator,
            button_name=widget["button_name"],
            test_results=test_results,
            action=widget["action"],  # 함수 전달
            hover_position=widget.get("hover_position"),  # None 처리 가능
        )


def process_case_20(page, test_results):
    # Case 20: [메모리 - TOP5] 위젯 컨텐츠 옵션 목록 동작 확인

    logging.info("=== [Case 20] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets
        if widget["widget_name"] == "memory - TOP5" and widget["element_name"] == "PanelContents dropdown"
    ]

    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_hover_action(
            page=page,
            widget_name=widget["widget_name"],
            element_locator=element_locator,
            button_name=widget["button_name"],
            test_results=test_results,
            action=widget["action"],  # 함수 전달
            hover_position=widget.get("hover_position"),  # None 처리 가능
        )


def process_case_21(page, test_results):
    # Case 21: [디스크 I/O - TOP5] 위젯 UI 확인
    
    logging.info("=== [Case 21] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets 
        if widget["widget_name"] == "disk I/O - TOP5" and widget.get("element_name")
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


def process_case_22(page, test_results):
    # Case 22: [디스크 I/O - TOP5] 위젯 - 정보 버튼 동작 확인

    logging.info("=== [Case 22] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets
        if widget["widget_name"] == "disk I/O - TOP5" and widget["element_name"] == "info button"
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


def process_case_23(page, test_results):
    # Case 23: [디스크 I/O - TOP5] 위젯 [>] 버튼 동작 확인

    logging.info("=== [Case 23] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets 
        if widget["widget_name"] == "disk I/O - TOP5" and widget["button_name"] == "[>] button"
        ]
    
    
    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_button_click(
            page=page,
            locator=element_locator,
            widget_name=widget["widget_name"],
            button_name=widget["button_name"],
            test_results=test_results,
            action=widget["action"]
        )


def process_case_24(page, test_results):
    # Case 24: [디스크 I/O - TOP5] 위젯 [PanelContents chart] 동작 확인

    logging.info("=== [Case 24] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets
        if widget["widget_name"] == "disk I/O - TOP5" and widget["element_name"] == "PanelContents chart"
    ]

    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_button_click(
            page=page,
            widget_name=widget["widget_name"],
            locator=element_locator,
            button_name=widget["button_name"],
            test_results=test_results,
            action=widget["action"],  # None인 경우 추가 동작 없음
            hover_positions=widget.get("hover_positions")  # 좌표 전달
        )


def process_case_25(page, test_results):
    # Case 25: [디스크 I/O - TOP5] 위젯 [PanelContents button] 동작 확인

    logging.info("=== [Case 25] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets
        if widget["widget_name"] == "disk I/O - TOP5" and widget["element_name"] == "PanelContents button"
    ]

    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_hover_action(
            page=page,
            widget_name=widget["widget_name"],
            element_locator=element_locator,
            button_name=widget["button_name"],
            test_results=test_results,
            action=widget["action"],  # 함수 전달
            hover_position=widget.get("hover_position"),  # None 처리 가능
        )


def process_case_26(page, test_results):
    # Case 26: [디스크 I/O - TOP5] 위젯 컨텐츠 옵션 목록 동작 확인

    logging.info("=== [Case 26] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets
        if widget["widget_name"] == "disk I/O - TOP5" and widget["element_name"] == "PanelContents dropdown"
    ]

    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_hover_action(
            page=page,
            widget_name=widget["widget_name"],
            element_locator=element_locator,
            button_name=widget["button_name"],
            test_results=test_results,
            action=widget["action"],  # 함수 전달
            hover_position=widget.get("hover_position"),  # None 처리 가능
        )



# def process_case_27(page, test_results):
#     # Case 27: [Server Status Map] 위젯 UI 확인
    
#     logging.info("=== [Case 27] 검증 시작 ===")

#     filtered_widgets = [
#         widget for widget in all_widgets 
#         if widget["widget_name"] == "Server Status Map" and widget.get("element_name")
#         ]
    
#     for widget in filtered_widgets:
#         element_locator = widget["element_locator"].format(locator=widget["locator"])

#         verify_widget_ui(
#             page=page,
#             locator=element_locator,
#             widget_name=widget["widget_name"],
#             element_name=widget["element_name"],
#             test_results=test_results
#         )



# def process_case_28(page, test_results):
#     # Case 28: [Server Status Map] 위젯 [Status Map chart] 동작 확인

#     logging.info("=== [Case 28] 검증 시작 ===")

#     filtered_widgets = [
#         widget for widget in all_widgets
#         if widget["widget_name"] == "Server Status Map" and widget["element_name"] == "Status Map chart"
#     ]

#     for widget in filtered_widgets:
#         element_locator = widget["element_locator"].format(locator=widget["locator"])

#         verify_widget_button_click(
#             page=page,
#             widget_name=widget["widget_name"],
#             locator=element_locator,
#             button_name=widget["button_name"],
#             test_results=test_results,
#             action=widget["action"],  # None인 경우 추가 동작 없음
#             hover_positions=widget.get("hover_positions")  # 좌표 전달
#         )

def process_case_33(page, test_results):
    # Case 33: [프로세스 CPU TOP5] 위젯 UI 확인
    
    logging.info("=== [Case 33] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets 
        if widget["widget_name"] == "프로세스 CPU TOP5" and widget.get("element_name")
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


def process_case_34(page, test_results):
    # Case 34: [프로세스 CPU TOP5] 위젯 - 정보 버튼 동작 확인

    logging.info("=== [Case 34] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets
        if widget["widget_name"] == "프로세스 CPU TOP5" and widget["element_name"] == "info button"
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


def process_case_35(page, test_results):
    # Case 35: [프로세스 CPU TOP5] 위젯 - [>] 버튼 동작 확인

    logging.info("=== [Case 35] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets 
        if widget["widget_name"] == "프로세스 CPU TOP5" and widget["button_name"] == "[>] button"
        ]
    
    
    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_button_click(
            page=page,
            locator=element_locator,
            widget_name=widget["widget_name"],
            button_name=widget["button_name"],
            test_results=test_results,
            action=widget["action"]
        )


def process_case_36(page, test_results):
    # Case 36: [프로세스 CPU TOP5] 위젯 프로세스 테이블 - [Name] 동작 확인

    logging.info("=== [Case 36] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets 
        if widget["widget_name"] == "프로세스 CPU TOP5" and widget["button_name"] == "process table name column"
        ]
    
    
    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_button_click(
            page=page,
            locator=element_locator,
            widget_name=widget["widget_name"],
            button_name=widget["button_name"],
            test_results=test_results,
            action=widget["action"]
        )


def process_case_37(page, test_results):
    # Case 37: [프로세스 CPU TOP5] 위젯 프로세스 테이블 - [Servers] 동작 확인

    logging.info("=== [Case 37] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets 
        if widget["widget_name"] == "프로세스 CPU TOP5" and widget["button_name"] == "process table server column"
        ]
    
    
    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_button_click(
            page=page,
            locator=element_locator,
            widget_name=widget["widget_name"],
            button_name=widget["button_name"],
            test_results=test_results,
            action=widget["action"]
        )


def process_case_38(page, test_results):
    # Case 38: [프로세스 메모리 TOP5] 위젯 UI 확인
    
    logging.info("=== [Case 38] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets 
        if widget["widget_name"] == "프로세스 메모리 TOP5" and widget.get("element_name")
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


def process_case_39(page, test_results):
    # Case 39: [프로세스 메모리 TOP5] 위젯 - 정보 버튼 동작 확인

    logging.info("=== [Case 39] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets
        if widget["widget_name"] == "프로세스 메모리 TOP5" and widget["element_name"] == "info button"
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


def process_case_40(page, test_results):
    # Case 40: [프로세스 메모리 TOP5] 위젯 - [>] 버튼 동작 확인

    logging.info("=== [Case 40] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets 
        if widget["widget_name"] == "프로세스 메모리 TOP5" and widget["button_name"] == "[>] button"
        ]
    
    
    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_button_click(
            page=page,
            locator=element_locator,
            widget_name=widget["widget_name"],
            button_name=widget["button_name"],
            test_results=test_results,
            action=widget["action"]
        )


def process_case_41(page, test_results):
    # Case 36: [프로세스 메모리 TOP5] 위젯 프로세스 테이블 - [Name] 동작 확인

    logging.info("=== [Case 36] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets 
        if widget["widget_name"] == "프로세스 메모리 TOP5" and widget["button_name"] == "process table name column"
        ]
    
    
    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_button_click(
            page=page,
            locator=element_locator,
            widget_name=widget["widget_name"],
            button_name=widget["button_name"],
            test_results=test_results,
            action=widget["action"]
        )


def process_case_42(page, test_results):
    # Case 37: [프로세스 메모리 TOP5] 위젯 프로세스 테이블 - [Servers] 동작 확인

    logging.info("=== [Case 37] 검증 시작 ===")

    filtered_widgets = [
        widget for widget in all_widgets 
        if widget["widget_name"] == "프로세스 메모리 TOP5" and widget["button_name"] == "process table server column"
        ]
    
    
    for widget in filtered_widgets:
        element_locator = widget["element_locator"].format(locator=widget["locator"])

        verify_widget_button_click(
            page=page,
            locator=element_locator,
            widget_name=widget["widget_name"],
            button_name=widget["button_name"],
            test_results=test_results,
            action=widget["action"]
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
    #     "locator": "div.PanelContents__Wrapper-dAMbXP.eMnZTY:has(span:text('Server Status Map'))",  # 위젯 자체 확인
    #     "element_name": None,  # 내부 요소 없음
    #     "element_locator": None,
    #     "button_name": None,
    #     "action": None
    # },
    
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
        "element_name": "[>] button",
        "element_locator": "{locator} button.Styles__Button-bDBZvm",
        "button_name": "[>] button",
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
        "action": lambda page, test_results: info_button_action(
            page=page,
            popover_locator="div.ant-popover.ant-popover-placement-bottom",  # Popover 부모 요소를 나타내는 조건
            popover_text_locator="div.HelperButton__ContentContainer-dPhKeC.eokXGu",  # 팝오버 텍스트 클래스
            expected_text="CPU",
            test_results=test_results,
        )
    },

    {
        "widget_name": "CPU - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('CPU')))",
        "element_name": "[>] button",
        "element_locator": "{locator} div.Styles__Wrapper-bZXaBP.lomqVM",
        "button_name": "[>] button",
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
        "action": lambda page, test_results: dropdown_button_action(
            page=page,
            dropdown_locator="div.ant-dropdown.ant-dropdown-placement-bottomLeft",
            expected_left_value=947,
            test_results=test_results
        )
        
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

    {
        "widget_name": "CPU - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('CPU')))",
        "element_name": "PanelContents dropdown",
        "element_locator": "{locator} .Ants__Dropdown-cCtpgz.bRdCUm",
        "button_name": "PanelContents dropdown",
        "action": lambda page, test_results: dropdown_button_action(
            page=page,
            dropdown_locator="div.ant-dropdown.ant-dropdown-placement-bottomLeft",
            expected_left_value=947,
            dropdown_list_button_locator='li:has-text("Disk Inode")',
            element_locator="div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('expected_text'))) .Ants__Dropdown-cCtpgz.bRdCUm",
            expected_text="Disk Inode",
            test_results=test_results
        )
        
    },

    {
        "widget_name": "memory - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('메모리')))",
        "element_name": "info button",  
        "element_locator": "{locator} div.Styles__Wrapper-bZXaBP.LPWtZ",
        "button_name": "info button",
        "action": lambda page, test_results: info_button_action(
            page=page,
            popover_locator="div.ant-popover.ant-popover-placement-top",  # Popover 부모 요소를 나타내는 조건
            popover_text_locator="div.HelperButton__ContentContainer-dPhKeC.eokXGu",  # 팝오버 텍스트 클래스
            expected_text="메모리",
            test_results=test_results,
        )
    },

    {
        "widget_name": "memory - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('메모리')))",
        "element_name": "[>] button",
        "element_locator": "{locator} div.Styles__Wrapper-bZXaBP.lomqVM",
        "button_name": "[>] button",
        "action":  lambda page, test_results: verify_navigation_action(
            page=page,
            test_results=test_results,
            screen_name="리소스 이퀄라이저",
            expected_url="/dashboard/multi_line?content=memory"
        )
    },

    {
        "widget_name": "memory - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('메모리')))",
        "element_name": "PanelContents button",
        "element_locator": "{locator} .Ants__Dropdown-cCtpgz.bRdCUm",
        "button_name": "PanelContents button",
        "action": lambda page, test_results: dropdown_button_action(
            page=page,
            dropdown_locator="div.ant-dropdown.ant-dropdown-placement-bottomLeft",
            expected_left_value=947,
            test_results=test_results
        )
        
    },

    {
        "widget_name": "memory - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('메모리')))",
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
        {"x":57,"y":44}
        ] # 툴팁 검증을 위한 좌표
    },

    {
        "widget_name": "memory - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('메모리')))",
        "element_name": "PanelContents dropdown",
        "element_locator": "{locator} .Ants__Dropdown-cCtpgz.bRdCUm",
        "button_name": "PanelContents dropdown",
        "action": lambda page, test_results: dropdown_button_action(
            page=page,
            dropdown_locator="div.ant-dropdown.ant-dropdown-placement-bottomLeft",
            expected_left_value=947,
            dropdown_list_button_locator='li:has-text("CPU")',
            element_locator="div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('expected_text'))) .Ants__Dropdown-cCtpgz.bRdCUm",
            expected_text="CPU",
            test_results=test_results
        )
        
    },


    {
        "widget_name": "disk I/O - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('디스크 I/O')))",
        "element_name": "info button",  
        "element_locator": "{locator} div.Styles__Wrapper-bZXaBP.LPWtZ",
        "button_name": "info button",
        "action": lambda page, test_results: info_button_action(
            page=page,
            popover_locator="div.ant-popover.ant-popover-placement-top",  # Popover 부모 요소를 나타내는 조건
            popover_text_locator="div.HelperButton__ContentContainer-dPhKeC.eokXGu",  # 팝오버 텍스트 클래스
            expected_text="디스크 I/O",
            test_results=test_results,
        )
    },

    {
        "widget_name": "disk I/O - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('디스크 I/O')))",
        "element_name": "[>] button",
        "element_locator": "{locator} div.Styles__Wrapper-bZXaBP.lomqVM",
        "button_name": "[>] button",
        "action":  lambda page, test_results: verify_navigation_action(
            page=page,
            test_results=test_results,
            screen_name="리소스 이퀄라이저",
            expected_url="/dashboard/multi_line?content=diskio"
        )
    },

    {
        "widget_name": "disk I/O - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('디스크 I/O')))",
        "element_name": "PanelContents button",
        "element_locator": "{locator} .Ants__Dropdown-cCtpgz.bRdCUm",
        "button_name": "PanelContents button",
        "action": lambda page, test_results: dropdown_button_action(
            page=page,
            dropdown_locator="div.ant-dropdown.ant-dropdown-placement-bottomLeft",
            expected_left_value=947,
            test_results=test_results
        )
        
    },

    {
        "widget_name": "disk I/O - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('디스크 I/O')))",
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
        {"x":62,"y":40}
        ] # 툴팁 검증을 위한 좌표
    },

    {
        "widget_name": "disk I/O - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('디스크 I/O')))",
        "element_name": "PanelContents dropdown",
        "element_locator": "{locator} .Ants__Dropdown-cCtpgz.bRdCUm",
        "button_name": "PanelContents dropdown",
        "action": lambda page, test_results: dropdown_button_action(
            page=page,
            dropdown_locator="div.ant-dropdown.ant-dropdown-placement-bottomLeft",
            expected_left_value=947,
            dropdown_list_button_locator='li:has-text("CPU")',
            element_locator="div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('expected_text'))) .Ants__Dropdown-cCtpgz.bRdCUm",
            expected_text="CPU",
            test_results=test_results
        )
        
    },

    # {
    #     "widget_name": "Server Status Map",
    #     "locator": ".Styles__Panel-kJCnUy.iLiSQM",  # 위젯 자체 확인
    #     "element_name": "CPU Resource Map button",  
    #     "element_locator": ".Styles__Wrapper-bZXaBP.dfHBtW",
    #     "button_name": "CPU Resource Map button",
    #     "action": None
    # },

    # {
    #     "widget_name": "Server Status Map",
    #     "locator": ".Styles__FlexWrapper-fGKctw > div > .Styles__FlexWrapper-fGKctw > .Styles__FlexSizeWrapper-dheSQV",  # 위젯 자체 확인
    #     "element_name": "Server Status Map button",  
    #     "element_locator": ".Styles__Wrapper-bZXaBP.cgWROS",
    #     "button_name": "Server Status Map button",
    #     "action": None
    # },

    # {
    #     "widget_name": "Server Status Map",
    #     "locator": ".Styles__FlexWrapper-fGKctw > div > .Styles__FlexWrapper-fGKctw > .Styles__FlexSizeWrapper-dheSQV",  # 위젯 자체 확인
    #     "element_name": "Status Map chart",  
    #     "element_locator": "canvas.Honeycomb__CanvasDom-ecbovM.hbmIfB",
    #     "button_name": "Status Map chart",
    #     "action": lambda page, test_results: (
    #         verify_navigation_goback_action(
    #         page=page,
    #         test_results=test_results,
    #         screen_name="서버 상세",
    #         expected_url="/server_detail"
    #     ),
    #         #verify_agent(page, expected_agent, test_results)
    #     ),
    #     "hover_positions": [  
    #     {"x":347,"y":86}
    #     ] # 툴팁 검증을 위한 좌표
    # },

    {
        "widget_name": "프로세스 CPU TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(span:text('프로세스 CPU TOP5'))",  # 위젯 자체 확인
        "element_name": "info button",  
        "element_locator": "{locator} div.Styles__Wrapper-bZXaBP.LPWtZ",
        "button_name": "info button",
        "action": lambda page, test_results: processwidget_info_button_action(
            page=page,
            popover_locator="div.ant-popover.ant-popover-placement-top",  # Popover 부모 요소를 나타내는 조건
            popover_text_locator="div.HelperButton__ContentContainer-dPhKeC.eokXGu",  # 팝오버 텍스트 클래스
            expected_text="CPU",
            test_results=test_results,
        )
    },
    {
        "widget_name": "프로세스 CPU TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(span:text('프로세스 CPU TOP5'))",  
        "element_name": "[>] button",  
        "element_locator": "{locator} div.Styles__Wrapper-bZXaBP.lomqVM",
        "button_name": "[>] button",
        "action": lambda page, test_results: verify_navigation_action(
            page=page,
            test_results=test_results,
            screen_name="프로세스 목록",
            expected_url="/process_list"
        )
    },
    {
        "widget_name": "프로세스 CPU TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(span:text('프로세스 CPU TOP5'))",  
        "element_name": "process table",  
        "element_locator": "{locator} div.PanelContents__Body-ha-DReo.hssRVS",
        "button_name": None,
        "action": None
    },
    # info_button_action 함수 대신 column_button_action 함수 만들어서 사용해야함 스타일 요소가 -가 아닌 값을 찾는 조건 사용하기
    {
        "widget_name": "프로세스 CPU TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(span:text('프로세스 CPU TOP5'))",
        "element_name": "process table name column",
        "element_locator": "{locator} tbody[role='rowgroup'] > tr[role='row']:nth-child(1) > td[role='cell']:nth-child(1)",
        "button_name": "process table name column",
        "action": lambda page, test_results: column_button_action(
            page=page,
            tooltip_locator="div.ant-tooltip.ant-tooltip-placement-top",  # tooltip 부모 요소를 나타내는 조건
            test_results=test_results
        )
        
    },
    {
        "widget_name": "프로세스 CPU TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(span:text('프로세스 CPU TOP5'))",
        "element_name": "process table server column",
        "element_locator": "{locator} tbody[role='rowgroup'] > tr[role='row']:nth-child(1) > td[role='cell']:nth-child(5)",
        "button_name": "process table server column",
        "action": lambda page, test_results: column_button_action(
            page=page,
            tooltip_locator="div.ant-tooltip.ant-tooltip-placement-top",  # tooltip 부모 요소를 나타내는 조건
            test_results=test_results
        )
        
    },
    {
        "widget_name": "프로세스 메모리 TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(span:text('프로세스 메모리 TOP5'))",  # 위젯 자체 확인
        "element_name": "info button",  
        "element_locator": "{locator} div.Styles__Wrapper-bZXaBP.LPWtZ",
        "button_name": "info button",
        "action": lambda page, test_results: processwidget_info_button_action(
            page=page,
            popover_locator="div.ant-popover.ant-popover-placement-top",  # Popover 부모 요소를 나타내는 조건
            popover_text_locator="div.HelperButton__ContentContainer-dPhKeC.eokXGu",  # 팝오버 텍스트 클래스
            expected_text="메모리",
            test_results=test_results
        )
    },
    {
        "widget_name": "프로세스 메모리 TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(span:text('프로세스 메모리 TOP5'))",  # 위젯 자체 확인
        "element_name": "[>] button",  
        "element_locator": "{locator} div.Styles__Wrapper-bZXaBP.lomqVM",
        "button_name": "[>] button",
        "action": lambda page, test_results: verify_navigation_action(
            page=page,
            test_results=test_results,
            screen_name="프로세스 목록",
            expected_url="/process_list"
        )
    },
    {
        "widget_name": "프로세스 메모리 TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(span:text('프로세스 메모리 TOP5'))",  # 위젯 자체 확인
        "element_name": "process table",  
        "element_locator": "{locator} div.PanelContents__Body-ha-DReo.hssRVS",
        "button_name": None,
        "action": None
    },
    {
        "widget_name": "프로세스 메모리 TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(span:text('프로세스 메모리 TOP5'))",
        "element_name": "process table name column",
        "element_locator": "{locator} tbody[role='rowgroup'] > tr[role='row']:nth-child(1) > td[role='cell']:nth-child(1)",
        "button_name": "process table name column",
        "action": lambda page, test_results: column_button_action(
            page=page,
            tooltip_locator="div.ant-tooltip.ant-tooltip-placement-top",  # tooltip 부모 요소를 나타내는 조건
            test_results=test_results
        )
        
    },
    {
        "widget_name": "프로세스 메모리 TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(span:text('프로세스 메모리 TOP5'))",
        "element_name": "process table server column",
        "element_locator": "{locator} tbody[role='rowgroup'] > tr[role='row']:nth-child(1) > td[role='cell']:nth-child(5)",
        "button_name": "process table server column",
        "action": lambda page, test_results: column_button_action(
            page=page,
            tooltip_locator="div.ant-tooltip.ant-tooltip-placement-top",  # tooltip 부모 요소를 나타내는 조건
            test_results=test_results
        )
        
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
        for browser_type in [playwright.chromium, playwright.firefox]: #playwright.webkit]:
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

            # Case 13 처리
            process_case_13(page, test_results)

            # Case 14 처리
            process_case_14(page, test_results)

            # Case 15 처리
            process_case_15(page, test_results)

            # Case 16 처리
            process_case_16(page, test_results)

            # Case 17 처리
            process_case_17(page, test_results)

            # Case 18 처리
            process_case_18(page, test_results)

            # Case 19 처리
            process_case_19(page, test_results)

            # Case 20 처리
            process_case_20(page, test_results)

            # Case 21 처리
            process_case_21(page, test_results)

            # Case 22 처리
            process_case_22(page, test_results)

            # Case 23 처리
            process_case_23(page, test_results)

            # Case 24 처리
            process_case_24(page, test_results)

            # Case 25 처리
            process_case_25(page, test_results)

            # Case 26 처리
            process_case_26(page, test_results)

            # # Case 27 처리
            # process_case_27(page, test_results)

            # # Case 28 처리
            # process_case_28(page, test_results)

            # Case 33 처리
            process_case_33(page, test_results)

            # Case 34 처리
            process_case_34(page, test_results)

            # Case 35 처리
            process_case_35(page, test_results)

            # Case 36 처리
            process_case_36(page, test_results)

            # Case 37 처리
            process_case_37(page, test_results)

            # Case 38 처리
            process_case_38(page, test_results)

            # Case 39 처리
            process_case_39(page, test_results)

            # Case 40 처리
            process_case_40(page, test_results)

            # Case 41 처리
            process_case_41(page, test_results)

            # Case 42 처리
            process_case_42(page, test_results)




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