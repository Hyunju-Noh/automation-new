from logging_utils import log_result
from globals import popup_detected
import logging

#실행중인 페이지가 앞으로 발생하도록 설정
def bring_page_to_front(func):
    def wrapper(*args, **kwargs):
        page = kwargs.get('page', None)
        if page:
            page.bring_to_front()  # 항상 페이지를 앞으로 가져오기
        return func(*args, **kwargs)
    return wrapper

#팝업 발생 시, 팝업 감지
def handle_dialog(dialog):
    global popup_detected
    logging.info(f"팝업 감지됨: {dialog.message}")
    popup_detected = True
    dialog.accept()  # 팝업을 수락
