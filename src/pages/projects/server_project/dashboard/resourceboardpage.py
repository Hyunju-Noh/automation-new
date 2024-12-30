from pages.projects.basepage import BasePage
from pages.projects.server_project.dashboard.resourceboard_widgets import all_widgets
from typing import List, Tuple
import logging

class ResourceBoardPage(BasePage):
    def __init__(self, page, whiteout_texts):
        super().__init__(page, whiteout_texts)
        self.widget_locator = "div.ResourceCards__CardDom-dzFtxX"  # 위젯 공통 선택자
        self.menu_wrap_selector = "div.Menustyles__MenuWrap-hRfo.hmTPnA"
        self.parent_elements_selector = "div.Menustyles__MenuItemWrapCommon-cHqrwY.Menustyles__Parent-XgDRT"
        self.widgets = all_widgets

    def get_widgets(self):
        """위젯 리스트 반환"""
        return self.widgets
    

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
    

    def processwidget_info_button_action(self, popover_locator: str, popover_text_locator: str, expected_text: str) -> Tuple[bool, List[str]]:
        """
        Popover 요소를 먼저 찾고, 그 하위에서 특정 텍스트를 포함하는 요소를 필터링한 후 상태를 검증하는 함수.

        :param popover_locator: 팝오버 부모 요소의 선택자 
        :param popover_text_locator: 팝오버 텍스트를 포함하는 요소의 선택자
        :param expected_text: 팝오버에 포함되어야 하는 예상 텍스트
        """
        success = True
        results = []

        try:
            logging.info("팝오버 상태 및 예상 텍스트 검증 시작")

            self.page.wait_for_timeout(1000)  # 1초 대기

            self.close_popups()

            # 1. Popover 요소를 먼저 찾기
            popover_elements = self.page.locator(popover_locator)
            if not popover_elements.count() > 0:
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
