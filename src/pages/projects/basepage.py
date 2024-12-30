from playwright.sync_api import Page
from typing import List, Tuple
import logging
import re
import util_tools.check_whiteout as whiteout

class BasePage:
    def __init__(self, page: Page, whiteout_texts: list):
        self.page = page
        self.whiteout_texts = whiteout_texts
        self.resource_board_link = 'a[href="/v2/project/sms/29763/dashboard/resource_board"]'
        self.menu_wrap_selector = 'div.Menustyles__MenuWrap-hRfo.hmTPnA'
        self.parent_elements_selector = 'div.Menustyles__MenuItemWrapCommon-cHqrwY.Menustyles__Parent-XgDRT'

    def close_popups(self):
        """발생하는 팝업을 감지하고 닫음."""
        try:
            popup_locator = self.page.locator(".Toastify__toast")
            close_button_locator = self.page.locator(".Toastify__close-button")

            if popup_locator.is_visible():
                close_button_locator.click()
        except Exception as e:
            pass


    def open_side_menus(self):
        """왼쪽 메뉴의 상위 메뉴 클릭."""
        menu_wrap = self.page.query_selector(self.menu_wrap_selector)
        parent_elements = menu_wrap.query_selector_all(self.parent_elements_selector)

        for element in parent_elements:
            element.click()
            self.wait_for_network_idle()    


    def wait_for_network_idle(self):
        """네트워크 안정 상태까지 대기."""
        self.page.wait_for_load_state('networkidle')


    def get_menu_wrap(self):
        """menu_wrap 요소 가져오기"""
        menu_wrap = self.page.query_selector(self.menu_wrap_selector)
        if not menu_wrap:
            raise Exception("menu_wrap 요소를 찾을 수 없습니다.")
        return menu_wrap


    def get_parent_elements(self):
        """menu_wrap 내의 모든 상위 메뉴 요소를 가져오는 메서드"""
        menu_wrap = self.get_menu_wrap()  # 이미 menu_wrap 존재 여부는 get_menu_wrap에서 확인함
        parent_elements = menu_wrap.query_selector_all(self.parent_elements_selector)
        
        if not parent_elements:
            raise Exception("상위 메뉴 요소를 찾을 수 없습니다.")
        return parent_elements


    def open_sub_menus(self):
        """상위 메뉴 클릭하여 하위 메뉴 열기"""
        parent_elements = self.get_parent_elements()
        logging.info("상위 메뉴 클릭하여 하위 메뉴 오픈 중") 

        for element in parent_elements:
            element.click()  # 요소 클릭
            self.page.wait_for_load_state('networkidle', timeout=20000)  # 페이지 로드 대기

        logging.info("하위 메뉴 오픈 후 페이지 로드 완료")


    def url(self, project_type, project_id):
        """프로젝트 페이지 URL 반환"""
        return f"https://service.whatap.io/v2/project/{project_type}/{project_id}"
    

    def navigate_to_project(self, project_type: str, project_id: str):
        """
        특정 프로젝트 페이지로 이동.

        :param project_type: 프로젝트 타입 (예: "sms")
        :param project_id: 프로젝트 ID (예: "12345")
        """
        # URL 생성
        project_url = self.url(project_type, project_id)

        logging.info(f"프로젝트로 이동: {project_url}")

        # 페이지 이동
        self.page.goto(project_url)
        self.wait_for_network_idle()



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


    def verify_navigation_action(self, screen_name: str, expected_url: str, save_path: str) -> Tuple[bool, List[str]]:
        """
        버튼 클릭 후 새로운 탭의 페이지 이동 및 UI 상태 검증

        :param screen_name: 검증 대상 화면 이름 (위젯 리스트에서 전달)
        :param expected_url: 기대되는 URL (위젯 리스트에서 전달)
        :param save_path: 스크린샷 저장 경로
        :return: (성공 여부, 에러 메시지 리스트)
        """
        logging.info("버튼 클릭 후 확인 진행 중")

        success = True
        results = []
        new_page = None

        try:

            # 새 페이지 열림 감지
            try:
                with self.page.context.expect_page(timeout=5000) as new_page_info:
                    logging.info("새 페이지 감지 대기 중...")
                new_page = new_page_info.value
            except TimeoutError:
                logging.warning("페이지 새로고침 시도...")
                self.page.reload()
                self.page.wait_for_load_state('networkidle')
                logging.info("페이지 새로고침 완료")

                # 새로고침 후 새 페이지 감지 재시도
                with self.page.context.expect_page(timeout=5000) as new_page_info:
                    logging.info("새 페이지 감지 재시도 중...")
                new_page = new_page_info.value

            # 새 페이지 정보 가져오기
            new_page.wait_for_timeout(1000)  # 1초 대기
            new_page.wait_for_load_state('networkidle')  # 새 페이지 로딩 완료 대기
            logging.info("새 페이지 로딩 완료")

            # 팝업 닫기
            self.close_popups()

            # 1. 새 페이지 URL 검증
            current_url = new_page.url
            logging.info(f"새 페이지 URL: {current_url}")
            if expected_url not in current_url:
                success = False
                results.append(f"{screen_name} 페이지로 이동하지 않았습니다. 현재 URL: {current_url}")
            else:
                logging.info(f"{screen_name} 페이지 정상 이동 확인됨")

            # 2. 새 페이지에서 UI 화이트아웃 검증
            whiteout_detected, _ = self.verify_whiteout(
                screen_name=screen_name,
                save_path=save_path,
            )
            if whiteout_detected:
                success = False
                results.append(f"{screen_name} 페이지에서 화이트아웃이 감지되었습니다.")
            else:
                logging.info(f"{screen_name} UI 화이트아웃 없음 확인됨")

        except Exception as e:
            success = False
            results.append(f"예외 발생: {str(e)}")

        finally:
        # 새 페이지 닫기
            if new_page and not new_page.is_closed():
                logging.info("새 페이지 닫는 중...")
                new_page.close()

        return success, results
    

    def verify_navigation_goback_action(self, screen_name: str, expected_url: str, save_path: str) -> Tuple[bool, List[str]]:
        """
        버튼 클릭 후 페이지 이동 및 UI 상태 검증 + 이전 화면으로 이동

        :param screen_name: 검증 대상 화면 이름 (위젯 리스트에서 전달)
        :param expected_url: 기대되는 URL (위젯 리스트에서 전달)
        :return: (성공 여부, 에러 메시지 리스트)
        """
        success = True
        results = []

        try:
            logging.info("버튼 클릭 후 확인 진행 중")

            self.wait_for_network_idle()

            self.close_popups()

            # 1. 새 페이지 URL에 '/server/list' 포함 여부 확인
            current_url = self.page.url
            logging.info(f"새 페이지 URL: {current_url}")
            if expected_url not in current_url:
                success = False
                results.append(f"{screen_name} 페이지로 이동하지 않았습니다. 현재 URL: {current_url}")
            else:
                logging.info(f"{screen_name} 페이지 정상 이동 확인됨")

            # 2. 새 페이지에서 UI 화이트아웃 검증
            whiteout_detected, _ = self.verify_whiteout(
                screen_name=screen_name,
                save_path=save_path,
            )
            if whiteout_detected:
                success = False
                results.append(f"{screen_name} 페이지에서 화이트아웃이 감지되었습니다.")
            else:
                logging.info(f"{screen_name} UI 화이트아웃 없음 확인됨")

        except Exception as e:
            success = False
            results.append(f"예외 발생: {str(e)}")

        finally:
            self.page.go_back()

        return success, results
    

    def info_button_action(self, popover_locator: str, popover_text_locator: str, expected_text: str) -> Tuple[bool, List[str]]:
        """
        Popover 요소를 먼저 찾고, 그 하위에서 특정 텍스트를 포함하는 요소를 필터링한 후 상태를 검증하는 함수.

        :param popover_locator: 팝오버 부모 요소의 선택자 
        :param popover_text_locator: 팝오버 텍스트를 포함하는 요소의 선택자
        :param expected_text: 팝오버에 포함되어야 하는 예상 텍스트
        """
        logging.info("팝오버 상태 및 예상 텍스트 검증 시작")

        success = True
        results = []

        try:
            self.page.wait_for_timeout(1000)  # 1초 대기

            self.close_popups()

            # 1. Popover 요소를 먼저 찾기
            popover_elements = self.page.locator(popover_locator)
            if not popover_elements.is_visible():
                success = False
                results.append("팝오버 요소가 표시되지 않았습니다.")
                return success, results

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

            if not matched_popover:
                success = False
                results.append(f"예상 텍스트 '{expected_text}'를 포함하는 팝오버를 찾지 못했습니다.")
                return success, results

            logging.info(f"예상 텍스트 '{expected_text}'를 포함하는 Popover 요소 발견")

            # 3. 해당 Popover의 상태 확인 (ant-popover-hidden 클래스가 없는지 확인)
            class_attr = matched_popover.get_attribute("class")
            if "ant-popover-hidden" in class_attr:
                success = False
                results.append("Popover가 열리지 않았습니다: hidden 상태")
                return success, results

            logging.info("팝오버 상태 검증 성공: hidden 클래스 없음")

        except Exception as e:
            success = False
            results.append(f"예외 발생: {str(e)}")

        return success, results
    

#드롭다운 함수 basepage에 추가하고 관련 테스트 함수 테스트 스크립트에 추가하기
    def dropdown_button_action(self, dropdown_locator: str, expected_left_value: str, dropdown_list_button_locator: str =None, element_locator: str =None, expected_text: str =None) -> Tuple[bool, List[str]]:
        """
        Dropdown 요소를 먼저 찾고, 특정 style 조건을 만족하는 요소를 필터링한 후 상태를 검증하는 함수.

        :param dropdown_locator: Dropdown 부모 요소의 선택자
        :param expected_left_value: style 속성에서 'left'의 예상 값
        :param test_results: 테스트 결과를 기록할 리스트
        :param dropdown_list_button_locator: Dropdown 내부 버튼 선택자 (선택적)
        :param element_locator: 동적으로 생성될 요소의 선택자 템플릿 (선택적)
        :param expected_text: 동적으로 생성될 요소에 사용될 텍스트 (선택적)
        """
        success = True
        results = []

        logging.info("Dropdown 상태 및 예상 조건 검증 시작")

        self.page.wait_for_timeout(1000)  # 1초 대기

        self.close_popups()

        try:
            # 1. Dropdown 요소 찾기
            dropdown_elements = self.page.locator(dropdown_locator)
            if not dropdown_elements.is_visible():
                success = False
                results.append("Dropdown 요소가 표시되지 않았습니다.")

            logging.info(f"Dropdown 요소 {dropdown_elements.count()}개 발견")
            matched_dropdown = None

            # 2. 각 Dropdown 요소에서 style 조건 확인
            for i in range(dropdown_elements.count()):
                current_dropdown = dropdown_elements.nth(i)
                style_attr = current_dropdown.get_attribute("style")

                if style_attr and f"left: {expected_left_value}px" in style_attr:
                    matched_dropdown = current_dropdown
                    break  # 조건을 만족하는 Dropdown 발견

            if not matched_dropdown:
                success = False
                results.append(f"left 값이 '{expected_left_value}px'인 Dropdown을 찾지 못했습니다.")

            logging.info(f"left 값이 '{expected_left_value}px'인 Dropdown 요소 발견")

            # 3. 해당 Dropdown의 상태 확인
            class_attr = matched_dropdown.get_attribute("class")
            if "ant-dropdown-hidden" in class_attr:
                success = False
                results.append("Dropdown이 열리지 않았습니다: hidden 상태")

            logging.info("Dropdown 상태 검증 성공: hidden 클래스 없음")

            # 4. Dropdown 내부 버튼 클릭 및 결과 확인
            if dropdown_list_button_locator:
                logging.info("Dropdown 내부 버튼 클릭 시도 중")
                dropdown_elements = self.page.locator(dropdown_list_button_locator)
                dropdown_elements.click()
                logging.info("Dropdown 내부 버튼 클릭 성공")

                dynamic_locator = element_locator.replace("expected_text", expected_text)
                popover_elements = self.page.locator(dynamic_locator)
                if not popover_elements.is_visible():
                    success = False
                    results.append(f"요소 '{expected_text}'가 클릭 후 표시되지 않았습니다.")

                logging.info(f"요소 '{expected_text}'가 클릭 후 정상적으로 표시됨")

            results.append("Dropdown 검증 및 동작 성공")
        
        except Exception as e:
            success = False
            results.append(f"예외 발생: {str(e)}")

        return success, results
    

    def column_button_action(self, tooltip_locator: str) -> Tuple[bool, List[str]]:
        """
        Dropdown 요소를 먼저 찾고, 특정 style 조건을 만족하는 요소를 필터링한 후 상태를 검증하는 함수.

        :param tooltip_locator: tooltip 요소의 선택자
        """
        success = True
        results = []

        logging.info("Dropdown 상태 및 예상 조건 검증 시작")

        self.page.wait_for_timeout(1000)  # 1초 대기

        self.close_popups()

        try:
            # 1. tooltip 요소를 먼저 찾기
            tooltip_elements = self.page.locator(tooltip_locator)
            if not tooltip_elements.count() > 0:
                success = False
                results.append("팝오버 요소를 찾지 못했습니다.")

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
                None,
            )
            if not matched_tooltip:
                success = False
                results.append("left 및 top 값이 양수인 Tooltip을 찾지 못했습니다.")

            logging.info(f"left 및 top 값이 양수인 Tooltip 요소 발견")

            # 3. 해당 tooltip 상태 확인 (ant-tooltip-hidden 클래스가 없는지 확인)
            class_attr = matched_tooltip.get_attribute("class")
            if "ant-tooltip-hidden" in class_attr:
                success = False
                results.append("tooltip이 열리지 않았습니다: hidden 상태")

            logging.info("툴팁 상태 검증 성공: hidden 클래스 없음")

        except Exception as e:
            success = False
            results.append(f"예외 발생: {str(e)}")

        return success, results






                                        




