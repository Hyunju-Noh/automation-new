import logging
import pytest
import util_tools.login_utils as login_utils
import util_tools.check_whiteout as whiteout
import util_tools.load_project_data as project_data
import util_tools.logging as log_utils
import util_tools.failures_utils as failures_utils
from pages.account.loginpage import LoginPage
from pages.projects.server_project.dashboard.resourceboardpage import ResourceBoardPage
from datetime import datetime


@pytest.mark.usefixtures("setup_playwright_context")
class Test_ResourceBoard:

    def setup_method(self):
        """ 각 테스트 메서드 전마다 whiteout_detected를 초기화 """
        self.whiteout_detected = False  # 클래스 속성으로 정의하고 각 테스트마다 초기화


    def process_case_1(self, resource_board_page):
         # Case 1: 리소스보드 화면 UI 확인

        logging.info("=== [Case 1] 검증whiteout_textswhiteout_textswhiteout_textswhiteout_textswhiteout_texts 시작 ===")

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        resource_board_page.close_modal_if_present()

        try:
            is_whiteout_detected, screen_name = resource_board_page.verify_whiteout(
                screen_name="리소스보드 화면",
                save_path=self.save_path
            )
            assert not is_whiteout_detected, f"[{screen_name}] 화면에서 화이트아웃이 감지되었습니다"

        except AssertionError as e:
                    failures.append(str(e))  # 실패 내용을 기록하고 계속 진행 

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget.get("element_name") is None and widget.get("element_locator") is None 
        ]

        for widget in filtered_widgets:
            try:
                is_visible = resource_board_page.verify_widget_ui(
                    locator=widget["locator"],
                    widget_name=widget["widget_name"],
                )
                assert is_visible, f"위젯 {widget['widget_name']}이 표시되지 않음"
            except AssertionError as e:
                    failures.append(str(e))  # 실패 내용을 기록하고 계속 진행
                 

    def process_case_2(resource_board_page):
        # Case 2: [Server] 위젯 UI 확인

        logging.info("=== [Case 2] 검증 시작 ===")

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "Server" and widget.get("element_name") 
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                # ResourceBoardPage의 is_widget_visible 메서드 호출
                is_visible = resource_board_page.verify_widget_ui(
                    locator=element_locator,
                    widget_name=widget["widget_name"],
                    element_name=widget["element_name"],
                )
                assert is_visible, f"위젯 {widget['widget_name']}이 표시되지 않음"
            except AssertionError as e:
                    failures.append(str(e))  # 실패 내용을 기록하고 계속 진행 


    def process_case_3(resource_board_page):
        # Case 3: [Server] 위젯 [>] 버튼 동작 확인

        logging.info("=== [Case 3] 검증 시작 ===")

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "Server" and widget.get("button_name") 
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                # ResourceBoardPage의 is_widget_visible 메서드 호출
                resource_board_page.verify_widget_button_click(
                    locator=element_locator,
                    widget_name=widget["widget_name"],
                    button_name=widget["button_name"],
                    action=widget["action"] (page=resource_board_page)
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](
                    screen_name="서버 목록 화면",
                    expected_url="/server/list",
                    save_path=resource_board_page.save_path,
                )

                assert success, f"[{widget['widget_name']}] 버튼 클릭 실패: {results}"
                logging.info(f"[{widget['widget_name']}] 버튼 클릭 및 추가 액션 검증 성공")

            except AssertionError as e:
                    failures.append(str(e))  # 실패 내용을 기록하고 계속 진행 


    def process_case_4(resource_board_page):
         # Case 4: [OS] 위젯 UI 확인

        logging.info("=== [Case 4] 검증 시작 ===")

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "OS" and widget.get("element_name") 
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                success, results = resource_board_page.verify_widget_structure(
                    parent_locator=element_locator,
                    widget_name=widget["widget_name"],
                    element_name=widget["element_name"],
                    child_count=widget.get("child_count"),
                )
                assert success, f"위젯 구조 검증 실패: {', '.join(results)}"

            except AssertionError as e:
                    failures.append(str(e))  # 실패 내용을 기록하고 계속 진행 


    def process_case_10(resource_board_page):
        # Case 10: [CPU - TOP5] 위젯 - 정보 버튼 동작 확인

        logging.info("=== [Case 10] 검증 시작 ===")

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "CPU - TOP5" and widget.get("element_name") == "info button"
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                resource_board_page.verify_widget_hover_action(
                    widget_name=widget["widget_name"],
                    element_locator=element_locator,
                    button_name=widget["button_name"],
                    hover_position=widget.get("hover_position"),  # None 처리 가능
                    action=widget["action"] (page=resource_board_page)
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](
                    popover_locator="div.ant-popover.ant-popover-placement-bottom",  # Popover 부모 요소를 나타내는 조건
                    popover_text_locator="div.HelperButton__ContentContainer-dPhKeC.eokXGu",  # 팝오버 텍스트 클래스
                    expected_text="CPU",
                )

                assert success, f"[{widget['widget_name']}] 호버 동작 실패: {results}"
                logging.info(f"[{widget['widget_name']}] 호버 동작 및 추가 액션 검증 성공")

            except AssertionError as e:
                    failures.append(str(e))  # 실패 내용을 기록하고 계속 진행 


    def process_case_28(resource_board_page):
        # Case 28: [Server Status Map] 위젯 [Status Map chart] 동작 확인

        logging.info("=== [Case 28] 검증 시작 ===")

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "Server Status Map" and widget["element_name"] == "Status Map chart"
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                # ResourceBoardPage의 verify_widget_button_click 메서드 호출
                resource_board_page.verify_widget_button_click(
                    locator=element_locator,
                    widget_name=widget["widget_name"],
                    button_name=widget["button_name"],
                    action=widget["action"] (page=resource_board_page)
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](
                    screen_name="서버 목록 화면",
                    expected_url="/server/list",
                    save_path=resource_board_page.save_path,
                )

                assert success, f"[{widget['widget_name']}] 버튼 클릭 실패: {results}"
                logging.info(f"[{widget['widget_name']}] 버튼 클릭 및 추가 액션 검증 성공")

            except AssertionError as e:
                    failures.append(str(e))  # 실패 내용을 기록하고 계속 진행 


    def process_case_34(resource_board_page):
        # Case 34: [프로세스 CPU TOP5] 위젯 - 정보 버튼 동작 확인

        logging.info("=== [Case 34] 검증 시작 ===")

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "프로세스 CPU TOP5" and widget["element_name"] == "info button"
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                # ResourceBoardPage의 verify_widget_hover_action 메서드 호출
                resource_board_page.verify_widget_hover_action(
                     widget_name=widget["widget_name"],
                    element_locator=element_locator,
                    button_name=widget["button_name"],
                    hover_position=widget.get("hover_position"),  # None 처리 가능
                    action=widget["action"] (page=resource_board_page) # 함수 전달
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](
                popover_locator="div.ant-popover.ant-popover-placement-top",  # Popover 부모 요소를 나타내는 조건
                popover_text_locator="div.HelperButton__ContentContainer-dPhKeC.eokXGu",  # 팝오버 텍스트 클래스
                expected_text="CPU",
                )

                assert success, f"[{widget['widget_name']}] 호버 동작 실패: {results}"
                logging.info(f"[{widget['widget_name']}] 호버 동작 및 추가 액션 검증 성공")

            except AssertionError as e:
                    failures.append(str(e))  # 실패 내용을 기록하고 계속 진행


    # 태그 값은 나중에 tc에 고유 번호 생성해서, 생성된 고유번호 넣어도 됨
    @pytest.mark.resourceboard
    @pytest.mark.order(1)
    def test_resource_board_page(self):
        """프로젝트 메뉴 검증"""
        failures = []  # 실패 항목을 저장할 리스트 초기화