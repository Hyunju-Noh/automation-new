from playwright.sync_api import Page
from typing import List, Tuple
import logging
import util_tools.check_whiteout as whiteout

class BasePage:
    def __init__(self, page: Page, whiteout_texts: list):
        self.page = page
        self.whiteout_texts = whiteout_texts
        self.resource_board_link = 'a[href="/v2/project/sms/29763/dashboard/resource_board"]'

    def close_popups(self):
        """발생하는 팝업을 감지하고 닫음."""
        try:
            popup_locator = self.page.locator(".Toastify__toast")
            close_button_locator = self.page.locator(".Toastify__close-button")

            if popup_locator.is_visible():
                close_button_locator.click()
        except Exception as e:
            pass


    def wait_for_network_idle(self):
        """네트워크 안정 상태까지 대기."""
        self.page.wait_for_load_state('networkidle')


    def navigate_to_menu(self, menu_link: str):
        """메뉴 화면으로 이동.

        :param menu_link: 이동할 메뉴의 링크 (CSS 선택자 또는 XPath)
        """

        logging.info(f"메뉴 이동: {menu_link}")
        self.page.locator(menu_link).click()
        self.wait_for_network_idle()
        self.page.wait_for_timeout(2000)  # 2초 대기


    def close_modal_if_present(self):
        """모달 감지 및 닫기 후 페이지 로드 대기"""

        close_selectors = [
            ".Styles__Wrapper-bZXaBP.dZPSDU",  # 첫 번째 모달 유형 닫기 버튼
            ".__floater__open .Styles__Wrapper-bZXaBP.cdnUPE",  # 두 번째 모달 유형 닫기 버튼
            ".Styles__Wrapper-bZXaBP.bVsFlg svg g#ic-close",  # 세 번째 모달 유형 닫기 버튼
            ".anticon.anticon-close.ant-modal-close-icon",  # 네 번째 모달 유형 닫기 버튼

        ]

        for selector in close_selectors:
            close_button = self.page.locator(selector)
            if close_button.count() > 0:
                logging.info(f"모달 팝업 감지 - 닫기 버튼: {selector}")
                close_button.click()
                logging.info("모달 팝업 닫기 완료")
                break  # 모달이 닫혔으면 루프 탈출

        self.wait_for_network_idle()


    def verify_widget_ui(self, locator: str, widget_name: str, element_name: str = None) -> bool:
        """
        위젯 UI 표시 여부를 검증하는 공통 함수

        :param locator: 위젯의 CSS 선택자
        :param widget_name: 위젯 이름
        :param element_name: 세부 요소 이름 (옵션)
        :return: 위젯이 표시되면 True, 아니면 False
        """
        display_name = f"{widget_name} {element_name}" if element_name else widget_name
        logging.info(f"[{display_name}] 표시 여부 확인 중")

        self.close_popups()

        self.wait_for_network_idle()
        element_locator = self.page.locator(locator)

        # UI 요소가 표시되는지 여부 반환
        return element_locator.is_visible()


    def verify_widget_button_click(self, widget_name: str, locator: str, button_name: str, action=None, hover_positions: str =None):
        """
        버튼 동작 수행 함수.

        :param widget_name: 위젯 이름
        :param locator: 버튼 선택자
        :param button_name: 버튼 이름
        :param test_results: 테스트 결과를 기록할 리스트
        :param action: 버튼 클릭 후 수행할 추가 동작 (콜백 함수)
        :param hover_positions: 좌표 리스트 (선택적으로 사용)
        """
        logging.info(f"[{widget_name}] 위젯 UI [{button_name}] 동작 수행 중")

        self.close_popups()

        if hover_positions:
            # 좌표를 활용하여 클릭 동작 수행
            for position in hover_positions:
                logging.info(f"[{widget_name}] 좌표 클릭 중: {position}")
                self.page.locator(locator).click(position=position)
                logging.info(f"[{widget_name}] 좌표 클릭 완료: {position}")
        else:
            # Locator를 활용하여 버튼 클릭
            button_locator = self.page.locator(locator)
            button_locator.click()
            logging.info(f"[{widget_name}] [{button_name}] 버튼 클릭 완료")

        self.wait_for_network_idle()

        # 추가 동작 수행
        if action:
            action(self)


    def verify_widget_structure(self, parent_locator: str, widget_name: str, element_name: str, child_count: str,) -> Tuple[bool, List[str]]:
        """
        위젯의 하위 구조 검증
        ex) ResourceCards__FlexRemainder의 하위 구조 검증

        :param parent_locator: 부모 요소 locator
        :param widget_name: 위젯 이름 (로그용)
        :param element_name: 하위 구조 이름 (로그용)
        :param child_count: 기대되는 하위 요소 개수
        :param test_results: 테스트 결과를 기록할 리스트
        """
        results = []
        success = True

        display_name = f"{widget_name} {element_name}" if element_name else widget_name
        logging.info(f"[{display_name}] 표시 여부 확인 중")

        self.close_popups()

        # 부모 요소 가져오기
        parent_element = self.page.locator(parent_locator)
        if not parent_element.is_visible():
            success = False
            results.append(f"[{widget_name}] 위젯의 부모 요소가 보이지 않습니다")
        
        # SubTitle과 SubValue 검증
        subtitle_elements = parent_element.locator("div.ResourceCards__SubTitle-eZXil")
        value_elements = parent_element.locator("div.ResourceCards__SubValue-bOvbm")

        subtitle_count = subtitle_elements.count()
        value_count = value_elements.count()

        logging.info(f"[{widget_name}] SubTitle 개수: {subtitle_count}, SubValue 개수: {value_count}")

        if subtitle_count <= 0:
            success = False
            results.append(f"[{widget_name}] SubTitle 요소를 찾지 못했습니다")

        if value_count <= 0:
            success = False
            results.append(f"[{widget_name}] SubValue 요소를 찾지 못했습니다")

        # SubTitle과 SubValue의 개수 및 표시 여부 검증
        for i in range(min(subtitle_count, value_count)):
            if not subtitle_elements.nth(i).is_visible():
                success = False
                results.append(f"[{widget_name}] {i+1}번째 SubTitle 요소가 표시되지 않습니다")
            if not value_elements.nth(i).is_visible():
                success = False
                results.append(f"[{widget_name}] {i+1}번째 SubValue 요소가 표시되지 않습니다")
            if success:
                logging.info(f"[{widget_name}] {i+1}번째 SubTitle 및 SubValue 확인 완료")

        return success, results
        

    def verify_whiteout(self, screen_name: str, save_path: str) -> Tuple[bool, str]:
        """
        화이트아웃 검증 함수.

        :param screen_name: 화면 이름 (로그용)
        :param save_path: 스크린샷 저장 경로
        """
        logging.info(f"[{screen_name}] 화이트아웃 발생 확인 중")
        self.wait_for_network_idle()

        whiteout_detected = whiteout.check_for_whiteout(self.page, screen_name, save_path, self.whiteout_texts)
        return whiteout_detected, screen_name
    

    def verify_widget_hover_action(self, widget_name: str, element_locator: str, button_name: str, action=None, hover_position: str =None):
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
        logging.info(f"[{widget_name}] 위젯 UI [{button_name}] 마우스 호버 동작 수행 중")

        self.close_popups()

        if element_locator:
            # element_locator가 있을 경우 해당 요소에 마우스 호버
            element = self.page.locator(element_locator)
            element.hover()
            logging.info(f"[{widget_name}] [{button_name}] 요소에 마우스 호버 완료")
        elif hover_position:
            # hover_position이 있을 경우 캔버스 또는 화면 좌표에 마우스 호버
            self.page.mouse.move(hover_position['x'], hover_position['y'])
            logging.info(f"[{widget_name}] 좌표 ({hover_position['x']}, {hover_position['y']})에 마우스 호버 완료")
        else:
            raise ValueError("Element_locator 또는 hover_position 값이 필요합니다.")
        
        self.page.wait_for_timeout(2000)  # 2초 대기

        self.close_popups()

        # 추가 동작 수행
        if action:
            action(self)


    def verify_navigation_action(self, screen_name: str, expected_url: str):
        """
        버튼 클릭 후 페이지 이동 및 UI 상태 검증

        :param page: Playwright 페이지 객체
        :param test_results: 테스트 결과 리스트
        :param screen_name: 검증 대상 화면 이름 (위젯 리스트에서 전달)
        :param expected_url: 기대되는 URL (위젯 리스트에서 전달)
        """
#verify_navigation_action 함수부터 차례로 작성하고, 그 다음에는 verify_navigation_action 함수 사용하는 테스트 함수를 테스트 스크립트에 예제 하나 추가하기


