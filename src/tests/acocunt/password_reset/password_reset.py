from utills.logging import log_result
from utils import bring_page_to_front, handle_dialog
from globals import popup_detected

import logging

@bring_page_to_front
def password_reset(page, test_name, inputs, button_name, expected_conditions, test_results, text_name=None, popup_expected=False):
    global popup_detected
    
    try:
        if popup_expected:
            page.once("dialog", handle_dialog)  # 팝업 처리 대기

        # 사전을 통해 필드에 대한 입력 방식을 매핑 (패스워드는 특수문자라 type으로 입력이 필요함)
        input_methods = {
            "Password": lambda field, value: field.type(value),
            "default": lambda field, value: field.fill(value),
        }

        # 입력 필드에 값 입력
        for placeholder, value in inputs.items():
            if value is not None:  # None 값은 입력하지 않음
                field = page.get_by_placeholder(placeholder, exact=True)
                # 'Password' 키워드를 포함하면 type(), 그렇지 않으면 fill() 사용
                method = input_methods.get("Password" if "Password" in placeholder else "default")
                method(field, value)

        # 버튼 클릭 또는 텍스트 클릭
        actions = {
            'button': lambda: page.get_by_role("button", name=button_name).click(),
            'text': lambda: page.get_by_text(text_name).click() if text_name is not None else None
        }
        actions['button']() if button_name else actions['text']()

        # 페이지 로드 상태 대기
        page.wait_for_load_state('networkidle')

        # 조건 검증
        condition_map = {
            "url_contains": lambda val: val in page.url,
            "text_present": lambda val: page.query_selector(f"text={val}") is not None,
            "element_present": lambda val: page.query_selector(val) is not None,
            "element_readonly": lambda val: page.query_selector(val).get_attribute("readonly") is not None,
            "popup_detected": lambda val: popup_detected == val
        }

        for condition_type, condition_value in expected_conditions.items():
            assert condition_map[condition_type](condition_value), f"{test_name} 실패: 조건 '{condition_type}' 검증 실패 - {condition_value}"

        # 성공 로그 기록
        log_result(True, f"{test_name} 성공: 입력값 - {inputs}")
        test_results.append(f"{test_name} 성공: 입력값 - {inputs}")
    
    except AssertionError as e:
        # Assertion 실패 로그 기록
        log_result(False, str(e))
        test_results.append(str(e))
    
    except Exception as e:
        # 기타 예외 처리 로그 기록
        log_result(False, f"예외 발생: {str(e)} - 입력값: {inputs}")
        test_results.append(f"예외 발생: {str(e)} - 입력값: {inputs}")