# src/testcases/project/server_project/dashboard/resource_board/test_resource_board.py

import logging
import pytest
import util_tools.failures_utils as failures_utils
from pages.projects.server_project.dashboard.resourceboardpage import ResourceBoardPage
from datetime import datetime


@pytest.mark.usefixtures("setup_playwright_context")
class Test_ResourceBoard:
    failures = []  # 실패 항목을 저장할 리스트 초기화


    @pytest.fixture(autouse=True)
    def set_resource_board_page(self, resource_board_page):
        """ResourceBoardPage 객체를 설정"""
        self.resource_board_page = resource_board_page


    # @pytest.fixture(scope="function")
    # def resource_board_page(base_page):
    #     """ResourceBoardPage 객체 생성 및 브라우저 컨텍스트 관리"""
    #     page = ResourceBoardPage(base_page.page, base_page.whiteout_texts, base_page.save_path)
    #     yield page  # 테스트 함수 실행
    #     # 테스트 함수 종료 후 브라우저 닫기
    #     if page.page.context.browser and page.page.context.browser.is_connected():
    #         logging.info("테스트 종료 후 브라우저 창 닫는 중...")
    #         try:
    #             page.page.context.browser.close()
    #         except Exception as e:
    #             logging.error(f"브라우저 닫기 중 오류 발생: {str(e)}")


    def setup_method(self):
        """ 각 테스트 메서드 전마다 초기화 작업 수행 """
        self.whiteout_detected = False  # 클래스 속성으로 정의하고 각 테스트마다 초기화


    def process_case_1(self, resource_board_page):
         # Case 1: 리소스보드 화면 UI 확인

        logging.info("=== [Case 1] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

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
                case_failures.append(str(e))


        return case_failures
                 

    def process_case_2(self, resource_board_page):
        # Case 2: [Server] 위젯 UI 확인

        logging.info("=== [Case 2] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

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
                case_failures.append(str(e))

        

        return case_failures


    def process_case_3(self, resource_board_page):
        # Case 3: [Server] 위젯 [>] 버튼 동작 확인

        logging.info("=== [Case 3] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

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
                    action=lambda: widget["action"] (resource_board_page)
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](resource_board_page)

                assert success, f"[{widget['widget_name']}] 버튼 클릭 실패: {results}"
                logging.info(f"[{widget['widget_name']}] 버튼 클릭 및 추가 액션 검증 성공")

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_4(self, resource_board_page):
         # Case 4: [OS] 위젯 UI 확인

        logging.info("=== [Case 4] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "OS" and widget["element_name"]
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
                case_failures.append(str(e))

        return case_failures


    def process_case_5(self, resource_board_page):
         # Case 5: [Total Cores] 위젯 UI 확인

        logging.info("=== [Case 5] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "Total Cores" and widget["element_name"]
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                is_visible = resource_board_page.verify_widget_ui(
                    locator=element_locator,
                    widget_name=widget["widget_name"],
                    element_name=widget["element_name"],
                )
                assert is_visible, f"위젯 {widget['widget_name']}이 표시되지 않음"

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures


    def process_case_6(self, resource_board_page):
         # Case 6: [Avg CPU] 위젯 UI 확인

        logging.info("=== [Case 6] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "Avg CPU" and widget["element_name"]
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                is_visible = resource_board_page.verify_widget_ui(
                    locator=element_locator,
                    widget_name=widget["widget_name"],
                    element_name=widget["element_name"],
                )
                assert is_visible, f"위젯 {widget['widget_name']}이 표시되지 않음"

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures
    

    def process_case_7(self, resource_board_page):
         # Case 7: [Avg Memory] 위젯 UI 확인

        logging.info("=== [Case 7] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "Avg Memory" and widget["element_name"]
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                is_visible = resource_board_page.verify_widget_ui(
                    locator=element_locator,
                    widget_name=widget["widget_name"],
                    element_name=widget["element_name"],
                )
                assert is_visible, f"위젯 {widget['widget_name']}이 표시되지 않음"

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_8(self, resource_board_page):
         # Case 8: [Avg Disk] 위젯 UI 확인

        logging.info("=== [Case 8] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "Avg Disk" and widget["element_name"]
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                is_visible = resource_board_page.verify_widget_ui(
                    locator=element_locator,
                    widget_name=widget["widget_name"],
                    element_name=widget["element_name"],
                )
                assert is_visible, f"위젯 {widget['widget_name']}이 표시되지 않음"

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_9(self, resource_board_page):
         # Case 9: [CPU - TOP5] 위젯 UI 확인

        logging.info("=== [Case 9] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "CPU - TOP5" and widget["element_name"]
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                is_visible = resource_board_page.verify_widget_ui(
                    locator=element_locator,
                    widget_name=widget["widget_name"],
                    element_name=widget["element_name"],
                )
                assert is_visible, f"위젯 {widget['widget_name']}이 표시되지 않음"

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_10(self, resource_board_page):
        # Case 10: [CPU - TOP5] 위젯 - 정보 버튼 동작 확인

        logging.info("=== [Case 10] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "CPU - TOP5" and widget["element_name"] == "info button"
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                resource_board_page.verify_widget_hover_action(
                    widget_name=widget["widget_name"],
                    element_locator=element_locator,
                    button_name=widget["button_name"],
                    hover_position=widget.get("hover_position"),  # None 처리 가능
                    action=lambda: widget["action"] (resource_board_page)
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](resource_board_page)

                assert success, f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 실패: {results}"
                logging.info(f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 및 추가 액션 검증 성공")

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_11(self, resource_board_page):
        # Case 11: [CPU - TOP5] 위젯 [>] 버튼 동작 확인

        logging.info("=== [Case 11] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "CPU - TOP5" and widget.get("button_name") == "[>] button"
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                # ResourceBoardPage의 is_widget_visible 메서드 호출
                resource_board_page.verify_widget_button_click(
                    locator=element_locator,
                    widget_name=widget["widget_name"],
                    button_name=widget["button_name"],
                    action=lambda: widget["action"] (resource_board_page)
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](resource_board_page)

                assert success, f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 실패: {results}"
                logging.info(f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 및 추가 액션 검증 성공")

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_12(self, resource_board_page):
        # Case 12: [CPU - TOP5] 위젯 [PanelContents chart] 동작 확인

        logging.info("=== [Case 12] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "CPU - TOP5" and widget["element_name"] == "PanelContents chart"
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                # ResourceBoardPage의 is_widget_visible 메서드 호출
                resource_board_page.verify_widget_button_click(
                    locator=element_locator,
                    widget_name=widget["widget_name"],
                    button_name=widget["button_name"],
                    action=lambda: widget["action"] (resource_board_page),
                    hover_positions=widget.get("hover_positions")  # 좌표 전달
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](resource_board_page)

                assert success, f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 실패: {results}"
                logging.info(f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 및 추가 액션 검증 성공")

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_13(self, resource_board_page):
        # Case 13: [CPU - TOP5] 위젯 - [PanelContents button] 동작 확인

        logging.info("=== [Case 13] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "CPU - TOP5" and widget["element_name"] == "PanelContents button"
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                resource_board_page.verify_widget_hover_action(
                    widget_name=widget["widget_name"],
                    element_locator=element_locator,
                    button_name=widget["button_name"],
                    hover_position=widget.get("hover_position"),  # None 처리 가능
                    action=lambda: widget["action"] (resource_board_page)
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](resource_board_page)

                assert success, f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 실패: {results}"
                logging.info(f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 및 추가 액션 검증 성공")

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_14(self, resource_board_page):
        # Case 14: [CPU - TOP5] 위젯 컨텐츠 옵션 목록 동작 확인

        logging.info("=== [Case 14] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "CPU - TOP5" and widget["element_name"] == "PanelContents dropdown"
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                resource_board_page.verify_widget_hover_action(
                    widget_name=widget["widget_name"],
                    element_locator=element_locator,
                    button_name=widget["button_name"],
                    hover_position=widget.get("hover_position"),  # None 처리 가능
                    action=lambda: widget["action"] (resource_board_page)
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](resource_board_page)

                assert success, f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 실패: {results}"
                logging.info(f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 및 추가 액션 검증 성공")

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_15(self, resource_board_page):
         # Case 15: [메모리 - TOP5] 위젯 UI 확인

        logging.info("=== [Case 15] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "memory - TOP5" and widget["element_name"]
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                is_visible = resource_board_page.verify_widget_ui(
                    locator=element_locator,
                    widget_name=widget["widget_name"],
                    element_name=widget["element_name"],
                )
                assert is_visible, f"위젯 {widget['widget_name']}이 표시되지 않음"

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_16(self, resource_board_page):
        # Case 16: [메모리 - TOP5] 위젯 - 정보 버튼 동작 확인

        logging.info("=== [Case 16] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "memory - TOP5" and widget["element_name"] == "info button"
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                resource_board_page.verify_widget_hover_action(
                    widget_name=widget["widget_name"],
                    element_locator=element_locator,
                    button_name=widget["button_name"],
                    hover_position=widget.get("hover_position"),  # None 처리 가능
                    action=lambda: widget["action"] (resource_board_page)
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](resource_board_page)

                assert success, f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 실패: {results}"
                logging.info(f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 및 추가 액션 검증 성공")

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_17(self, resource_board_page):
        # Case 17: [메모리 - TOP5] 위젯 [>] 버튼 동작 확인

        logging.info("=== [Case 17] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "memory - TOP5" and widget.get("button_name") == "[>] button"
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                # ResourceBoardPage의 is_widget_visible 메서드 호출
                resource_board_page.verify_widget_button_click(
                    locator=element_locator,
                    widget_name=widget["widget_name"],
                    button_name=widget["button_name"],
                    action=lambda: widget["action"] (resource_board_page)
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](resource_board_page)

                assert success, f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 실패: {results}"
                logging.info(f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 및 추가 액션 검증 성공")

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_18(self, resource_board_page):
        # Case 18: [메모리 - TOP5] 위젯 [PanelContents chart] 동작 확인

        logging.info("=== [Case 18] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "memory - TOP5" and widget["element_name"] == "PanelContents chart"
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                # ResourceBoardPage의 is_widget_visible 메서드 호출
                resource_board_page.verify_widget_button_click(
                    locator=element_locator,
                    widget_name=widget["widget_name"],
                    button_name=widget["button_name"],
                    action=lambda: widget["action"] (resource_board_page),
                    hover_positions=widget.get("hover_positions")  # 좌표 전달
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](resource_board_page)

                assert success, f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 실패: {results}"
                logging.info(f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 및 추가 액션 검증 성공")

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures  


    def process_case_19(self, resource_board_page):
        # Case 19: [메모리 - TOP5] 위젯 [PanelContents button] 동작 확인

        logging.info("=== [Case 19] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "memory - TOP5" and widget["element_name"] == "PanelContents button"
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                resource_board_page.verify_widget_hover_action(
                    widget_name=widget["widget_name"],
                    element_locator=element_locator,
                    button_name=widget["button_name"],
                    hover_position=widget.get("hover_position"),  # None 처리 가능
                    action=lambda: widget["action"] (resource_board_page)
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](resource_board_page)

                assert success, f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 실패: {results}"
                logging.info(f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 및 추가 액션 검증 성공")

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_20(self, resource_board_page):
        # Case 20: [메모리 - TOP5] 위젯 컨텐츠 옵션 목록 동작 확인

        logging.info("=== [Case 20] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "memory - TOP5" and widget["element_name"] == "PanelContents dropdown"
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                resource_board_page.verify_widget_hover_action(
                    widget_name=widget["widget_name"],
                    element_locator=element_locator,
                    button_name=widget["button_name"],
                    hover_position=widget.get("hover_position"),  # None 처리 가능
                    action=lambda: widget["action"] (resource_board_page)
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](resource_board_page)

                assert success, f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 실패: {results}"
                logging.info(f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 및 추가 액션 검증 성공")

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_21(self, resource_board_page):
         # Case 21: [디스크 I/O - TOP5] 위젯 UI 확인

        logging.info("=== [Case 21] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "disk I/O - TOP5" and widget["element_name"]
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                is_visible = resource_board_page.verify_widget_ui(
                    locator=element_locator,
                    widget_name=widget["widget_name"],
                    element_name=widget["element_name"],
                )
                assert is_visible, f"위젯 {widget['widget_name']}이 표시되지 않음"

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_22(self, resource_board_page):
        # Case 22: [디스크 I/O - TOP5] 위젯 - 정보 버튼 동작 확인

        logging.info("=== [Case 22] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)


        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "disk I/O - TOP5" and widget["element_name"] == "info button"
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                resource_board_page.verify_widget_hover_action(
                    widget_name=widget["widget_name"],
                    element_locator=element_locator,
                    button_name=widget["button_name"],
                    hover_position=widget.get("hover_position"),  # None 처리 가능
                    action=lambda: widget["action"] (resource_board_page)
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](resource_board_page)

                assert success, f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 실패: {results}"
                logging.info(f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 및 추가 액션 검증 성공")

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_23(self, resource_board_page):
        # Case 23: [디스크 I/O - TOP5] 위젯 [>] 버튼 동작 확인

        logging.info("=== [Case 23] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)


        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "disk I/O - TOP5" and widget.get("button_name") == "[>] button"
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                # ResourceBoardPage의 is_widget_visible 메서드 호출
                resource_board_page.verify_widget_button_click(
                    locator=element_locator,
                    widget_name=widget["widget_name"],
                    button_name=widget["button_name"],
                    action=lambda: widget["action"] (resource_board_page)
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](resource_board_page)

                assert success, f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 실패: {results}"
                logging.info(f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 및 추가 액션 검증 성공")

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_24(self, resource_board_page):
        # Case 24: [디스크 I/O - TOP5] 위젯 [PanelContents chart] 동작 확인

        logging.info("=== [Case 24] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "disk I/O - TOP5" and widget["element_name"] == "PanelContents chart"
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                # ResourceBoardPage의 is_widget_visible 메서드 호출
                resource_board_page.verify_widget_button_click(
                    locator=element_locator,
                    widget_name=widget["widget_name"],
                    button_name=widget["button_name"],
                    action=lambda: widget["action"] (resource_board_page),
                    hover_positions=widget.get("hover_positions")  # 좌표 전달
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](resource_board_page)

                assert success, f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 실패: {results}"
                logging.info(f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 및 추가 액션 검증 성공")

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_25(self, resource_board_page):
        # Case 25: [디스크 I/O - TOP5] 위젯 [PanelContents button] 동작 확인

        logging.info("=== [Case 19] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "disk I/O - TOP5" and widget["element_name"] == "PanelContents button"
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                resource_board_page.verify_widget_hover_action(
                    widget_name=widget["widget_name"],
                    element_locator=element_locator,
                    button_name=widget["button_name"],
                    hover_position=widget.get("hover_position"),  # None 처리 가능
                    action=lambda: widget["action"] (resource_board_page)
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](resource_board_page)

                assert success, f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 실패: {results}"
                logging.info(f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 및 추가 액션 검증 성공")

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_26(self, resource_board_page):
        # Case 26: [디스크 I/O - TOP5] 위젯 컨텐츠 옵션 목록 동작 확인

        logging.info("=== [Case 26] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "disk I/O - TOP5" and widget["element_name"] == "PanelContents dropdown"
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                resource_board_page.verify_widget_hover_action(
                    widget_name=widget["widget_name"],
                    element_locator=element_locator,
                    button_name=widget["button_name"],
                    hover_position=widget.get("hover_position"),  # None 처리 가능
                    action=lambda: widget["action"] (resource_board_page)
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](resource_board_page)

                assert success, f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 실패: {results}"
                logging.info(f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 및 추가 액션 검증 성공")

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_27(self, resource_board_page):
         # Case 27: [Server Status Map] 위젯 UI 확인

        logging.info("=== [Case 27] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "Server Status Map" and widget["element_name"]
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                is_visible = resource_board_page.verify_widget_ui(
                    locator=element_locator,
                    widget_name=widget["widget_name"],
                    element_name=widget["element_name"],
                )
                assert is_visible, f"위젯 {widget['widget_name']}이 표시되지 않음"

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_28(self, resource_board_page):
        # Case 28: [Server Status Map] 위젯 [Status Map chart] 동작 확인

        logging.info("=== [Case 28] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

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
                    action=lambda: widget["action"] (resource_board_page)
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](resource_board_page)

                assert success, f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 실패: {results}"
                logging.info(f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 및 추가 액션 검증 성공")

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_33(self, resource_board_page):
         # Case 33: [프로세스 CPU TOP5] 위젯 UI 확인

        logging.info("=== [Case 33] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "프로세스 CPU TOP5" and widget["element_name"]
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                is_visible = resource_board_page.verify_widget_ui(
                    locator=element_locator,
                    widget_name=widget["widget_name"],
                    element_name=widget["element_name"],
                )
                assert is_visible, f"위젯 {widget['widget_name']}이 표시되지 않음"

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_34(self, resource_board_page):
        # Case 34: [프로세스 CPU TOP5] 위젯 - 정보 버튼 동작 확인

        logging.info("=== [Case 34] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

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
                    action=lambda: widget["action"] (resource_board_page) # 함수 전달
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](resource_board_page)

                assert success, f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 실패: {results}"
                logging.info(f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 및 추가 액션 검증 성공")

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_35(self, resource_board_page):
        # Case 35: [프로세스 CPU TOP5] 위젯 - [>] 버튼 동작 확인

        logging.info("=== [Case 35] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "프로세스 CPU TOP5" and widget.get("button_name") == "[>] button"
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                # ResourceBoardPage의 is_widget_visible 메서드 호출
                resource_board_page.verify_widget_button_click(
                    locator=element_locator,
                    widget_name=widget["widget_name"],
                    button_name=widget["button_name"],
                    action=lambda: widget["action"] (resource_board_page)
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](resource_board_page)

                assert success, f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 실패: {results}"
                logging.info(f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 및 추가 액션 검증 성공")

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_36(self, resource_board_page):
        # Case 36: [프로세스 CPU TOP5] 위젯 프로세스 테이블 - [Name] 동작 확인

        logging.info("=== [Case 36] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "프로세스 CPU TOP5" and widget["button_name"] == "process table name column"
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                # ResourceBoardPage의 verify_widget_button_click 메서드 호출
                resource_board_page.verify_widget_button_click(
                    locator=element_locator,
                    widget_name=widget["widget_name"],
                    button_name=widget["button_name"],
                    action=lambda: widget["action"] (resource_board_page)
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](resource_board_page)

                assert success, f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 실패: {results}"
                logging.info(f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 및 추가 액션 검증 성공")

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 



    def process_case_37(self, resource_board_page):
        # Case 37: [프로세스 CPU TOP5] 위젯 프로세스 테이블 - [Servers] 동작 확인

        logging.info("=== [Case 36] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "프로세스 CPU TOP5" and widget["button_name"] == "process table server column"
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                # ResourceBoardPage의 verify_widget_button_click 메서드 호출
                resource_board_page.verify_widget_button_click(
                    locator=element_locator,
                    widget_name=widget["widget_name"],
                    button_name=widget["button_name"],
                    action=lambda: widget["action"] (resource_board_page)
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](resource_board_page)

                assert success, f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 실패: {results}"
                logging.info(f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 및 추가 액션 검증 성공")

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_38(self, resource_board_page):
         # Case 38: [프로세스 메모리 TOP5] 위젯 UI 확인

        logging.info("=== [Case 38] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "프로세스 메모리 TOP5" and widget["element_name"]
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                is_visible = resource_board_page.verify_widget_ui(
                    locator=element_locator,
                    widget_name=widget["widget_name"],
                    element_name=widget["element_name"],
                )
                assert is_visible, f"위젯 {widget['widget_name']}이 표시되지 않음"

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_39(self, resource_board_page):
        # Case 39: [프로세스 메모리 TOP5] 위젯 - 정보 버튼 동작 확인

        logging.info("=== [Case 39] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "프로세스 메모리 TOP5" and widget["element_name"] == "info button"
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
                    action=lambda: widget["action"] (resource_board_page) # 함수 전달
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](resource_board_page)

                assert success, f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 실패: {results}"
                logging.info(f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 및 추가 액션 검증 성공")

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_40(self, resource_board_page):
        # Case 40: [프로세스 메모리 TOP5] 위젯 - [>] 버튼 동작 확인

        logging.info("=== [Case 40] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "프로세스 메모리 TOP5" and widget.get("button_name") == "[>] button"
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                # ResourceBoardPage의 is_widget_visible 메서드 호출
                resource_board_page.verify_widget_button_click(
                    locator=element_locator,
                    widget_name=widget["widget_name"],
                    button_name=widget["button_name"],
                    action=lambda: widget["action"] (resource_board_page)
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](resource_board_page)

                assert success, f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 실패: {results}"
                logging.info(f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 및 추가 액션 검증 성공")

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_41(self, resource_board_page):
        # Case 41: [프로세스 메모리 TOP5] 위젯 프로세스 테이블 - [Name] 동작 확인

        logging.info("=== [Case 41] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)        

        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "프로세스 메모리 TOP5" and widget["button_name"] == "process table name column"
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                # ResourceBoardPage의 verify_widget_button_click 메서드 호출
                resource_board_page.verify_widget_button_click(
                    locator=element_locator,
                    widget_name=widget["widget_name"],
                    button_name=widget["button_name"],
                    action=lambda: widget["action"] (resource_board_page)
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](resource_board_page)

                assert success, f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 실패: {results}"
                logging.info(f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 및 추가 액션 검증 성공")

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    def process_case_42(self, resource_board_page):
        # Case 42: [프로세스 메모리 TOP5] 위젯 프로세스 테이블 - [Servers] 동작 확인

        logging.info("=== [Case 42] 검증 시작 ===")
        case_failures = []  # 개별 케이스 실패 리스트

        resource_board_page.navigate_to_project(project_type="sms", project_id="29763")

        resource_board_page.open_sub_menus()

        resource_board_page.navigate_to_menu(resource_board_page.resource_board_link)


        filtered_widgets = [
            widget for widget in resource_board_page.get_widgets()  
            if widget["widget_name"] == "프로세스 메모리 TOP5" and widget["button_name"] == "process table server column"
        ]

        for widget in filtered_widgets:
            element_locator = widget["element_locator"].format(locator=widget["locator"])

            try:
                # ResourceBoardPage의 verify_widget_button_click 메서드 호출
                resource_board_page.verify_widget_button_click(
                    locator=element_locator,
                    widget_name=widget["widget_name"],
                    button_name=widget["button_name"],
                    action=lambda: widget["action"] (resource_board_page)
                )

                # 추가 액션 결과 검증
                success, results = widget["action"](resource_board_page)

                assert success, f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 실패: {results}"
                logging.info(f"[{widget['widget_name']}] [{widget["element_name"]}] 동작 및 추가 액션 검증 성공")

            except AssertionError as e:
                case_failures.append(str(e))

        return case_failures 


    @pytest.mark.resourceboard
    @pytest.mark.order(1)
    def test_case_1(self, resource_board_page):
        """Test Case 1: 리소스보드 화면 UI 검증"""
        self.failures.extend(self.process_case_1(resource_board_page))
        # try:
        #     self.failures.extend(self.process_case_1(resource_board_page))
        # finally:
        #     if resource_board_page.page.context and not resource_board_page.page.context.browser.is_closed():
        #         logging.info("브라우저 창 닫는 중...")
        #         resource_board_page.page.context.browser.close()


    @pytest.mark.resourceboard
    @pytest.mark.order(2)
    def test_case_2(self, resource_board_page):
        """Test Case 2: [Server] 위젯 UI 검증"""
        self.failures.extend(self.process_case_2(resource_board_page))
        # try:
        #     self.failures.extend(self.process_case_2(resource_board_page))
        # finally:
        #     if resource_board_page.page.context and not resource_board_page.page.context.browser.is_closed():
        #         logging.info("브라우저 창 닫는 중...")
        #         resource_board_page.page.context.browser.close()


    @pytest.mark.resourceboard
    @pytest.mark.order(3)
    def test_case_3(self, resource_board_page):
        """Test Case 3: [Server] 위젯 [>] 버튼 동작 확인"""
        self.failures.extend(self.process_case_3(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(4)
    def test_case_4(self, resource_board_page):
        """Test Case 4: [OS] 위젯 UI 확인"""
        self.failures.extend(self.process_case_4(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(5)
    def test_case_5(self, resource_board_page):
        """Test Case 5: [Total Cores] 위젯 UI 확인"""
        self.failures.extend(self.process_case_5(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(6)
    def test_case_6(self, resource_board_page):
        """Test Case 6: [Avg CPU] 위젯 UI 확인"""
        self.failures.extend(self.process_case_6(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(7)
    def test_case_7(self, resource_board_page):
        """Test Case 7: [Avg Memory] 위젯 UI 확인"""
        self.failures.extend(self.process_case_7(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(8)
    def test_case_8(self, resource_board_page):
        """Test Case 8: [Avg Disk] 위젯 UI 확인"""
        self.failures.extend(self.process_case_8(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(9)
    def test_case_9(self, resource_board_page):
        """Test Case 9: [CPU - TOP5] 위젯 UI 확인"""
        self.failures.extend(self.process_case_9(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(10)
    def test_case_10(self, resource_board_page):
        """Test Case 10: [CPU - TOP5] 위젯 - 정보 버튼 동작 확인"""
        self.failures.extend(self.process_case_10(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(11)
    def test_case_11(self, resource_board_page):
        """Test Case 11: [CPU - TOP5] 위젯 [>] 버튼 동작 확인"""
        self.failures.extend(self.process_case_11(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(12)
    def test_case_12(self, resource_board_page):
        """Test Case 12: [CPU - TOP5] 위젯 [PanelContents chart] 동작 확인"""
        self.failures.extend(self.process_case_12(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(13)
    def test_case_13(self, resource_board_page):
        """Test Case 13: [CPU - TOP5] 위젯 [PanelContents button] 동작 확인"""
        self.failures.extend(self.process_case_13(resource_board_page))

    @pytest.mark.resourceboard
    @pytest.mark.order(14)
    def test_case_14(self, resource_board_page):
        """Test Case 14: [CPU - TOP5] 위젯 컨텐츠 옵션 목록 동작 확인"""
        self.failures.extend(self.process_case_14(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(15)
    def test_case_15(self, resource_board_page):
        """Test Case 15: [메모리 - TOP5] 위젯 UI 확인"""
        self.failures.extend(self.process_case_15(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(16)
    def test_case_16(self, resource_board_page):
        """Test Case 16: [메모리 - TOP5] 위젯 - 정보 버튼 동작 확인"""
        self.failures.extend(self.process_case_16(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(17)
    def test_case_17(self, resource_board_page):
        """Test Case 17: [메모리 - TOP5] 위젯 [>] 버튼 동작 확인"""
        self.failures.extend(self.process_case_17(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(18)
    def test_case_18(self, resource_board_page):
        """Test Case 18: [메모리 - TOP5] 위젯 [PanelContents chart] 동작 확인"""
        self.failures.extend(self.process_case_18(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(19)
    def test_case_19(self, resource_board_page):
        """Test Case 19: [메모리 - TOP5] 위젯 [PanelContents button] 동작 확인인"""
        self.failures.extend(self.process_case_19(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(20)
    def test_case_20(self, resource_board_page):
        """Test Case 20: [메모리 - TOP5] 위젯 컨텐츠 옵션 목록 동작 확인"""
        self.failures.extend(self.process_case_20(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(21)
    def test_case_21(self, resource_board_page):
        """Test Case 21: [디스크 I/O - TOP5] 위젯 UI 확인"""
        self.failures.extend(self.process_case_21(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(22)
    def test_case_22(self, resource_board_page):
        """Test Case 22: [디스크 I/O - TOP5] 위젯 - 정보 버튼 동작 확인"""
        self.failures.extend(self.process_case_22(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(23)
    def test_case_23(self, resource_board_page):
        """Test Case 23: [디스크 I/O - TOP5] 위젯 [>] 버튼 동작 확인"""
        self.failures.extend(self.process_case_23(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(24)
    def test_case_24(self, resource_board_page):
        """Test Case 24: [디스크 I/O - TOP5] 위젯 [PanelContents chart] 동작 확인"""
        self.failures.extend(self.process_case_24(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(25)
    def test_case_25(self, resource_board_page):
        """Test Case 25: [디스크 I/O - TOP5] 위젯 [PanelContents button] 동작 확인"""
        self.failures.extend(self.process_case_25(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(26)
    def test_case_26(self, resource_board_page):
        """Test Case 26: [디스크 I/O - TOP5] 위젯 컨텐츠 옵션 목록 동작 확인"""
        self.failures.extend(self.process_case_26(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(33)
    def test_case_33(self, resource_board_page):
        """Test Case 33: [프로세스 CPU TOP5] 위젯 UI 확인"""
        self.failures.extend(self.process_case_33(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(34)
    def test_case_34(self, resource_board_page):
        """Test Case 34: [프로세스 CPU TOP5] 위젯 - 정보 버튼 동작 확인"""
        self.failures.extend(self.process_case_34(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(35)
    def test_case_35(self, resource_board_page):
        """Test Case 35: [프로세스 CPU TOP5] 위젯 - [>] 버튼 동작 확인"""
        self.failures.extend(self.process_case_35(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(36)
    def test_case_36(self, resource_board_page):
        """Test Case 36: [프로세스 CPU TOP5] 위젯 프로세스 테이블 - [Name] 동작 확인"""
        self.failures.extend(self.process_case_36(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(37)
    def test_case_37(self, resource_board_page):
        """Test Case 37: [프로세스 CPU TOP5] 위젯 프로세스 테이블 - [Servers] 동작 확인"""
        self.failures.extend(self.process_case_37(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(38)
    def test_case_38(self, resource_board_page):
        """Test Case 38: [프로세스 메모리 TOP5] 위젯 UI 확인"""
        self.failures.extend(self.process_case_38(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(39)
    def test_case_39(self, resource_board_page):
        """Test Case 39: [프로세스 메모리 TOP5] 위젯 - 정보 버튼 동작 확인"""
        self.failures.extend(self.process_case_39(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(40)
    def test_case_6(self, resource_board_page):
        """Test Case 40: [프로세스 메모리 TOP5] 위젯 - [>] 버튼 동작 확인"""
        self.failures.extend(self.process_case_40(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(41)
    def test_case_41(self, resource_board_page):
        """Test Case 41: [프로세스 메모리 TOP5] 위젯 프로세스 테이블 - [Name] 동작 확인"""
        self.failures.extend(self.process_case_41(resource_board_page))


    @pytest.mark.resourceboard
    @pytest.mark.order(42)
    def test_case_42(self, resource_board_page):
        """Test Case 42: [프로세스 메모리 TOP5] 위젯 프로세스 테이블 - [Servers] 동작 확인"""
        self.failures.extend(self.process_case_42(resource_board_page))


    def teardown_class(self):
        """모든 테스트 실행 후 요약만 출력"""
        if self.failures:
            logging.info("전체 테스트 실패 요약:")
            for failure in self.failures:
                logging.error(failure)



if __name__ == "__main__":
    # 실행 시각에 따라 보고서 파일명 동적으로 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"src/reports/test_report_project_menu_{timestamp}.html"

    # pytest.main 호출로 pytest 실행 및 보고서 경로 설정
    pytest.main(["--html", report_path, "--self-contained-html"])