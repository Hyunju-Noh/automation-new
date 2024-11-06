# src/util_tools/check_whiteout.py
import os
import csv
import time
import logging
from datetime import datetime
from playwright.sync_api import Page, TimeoutError

def load_whiteout_texts(file_path=None):
    """CSV 파일에서 화이트아웃 텍스트 목록을 로드합니다."""
    # file_path가 None인 경우 환경 변수에서 경로를 가져오고, 기본값이 설정되어 있지 않으면 "data/whiteout_texts.csv"로 설정
    file_path = file_path or os.getenv("WHITEOUT_TEXTS_PATH", "src/data/whiteout_texts.csv")

    texts = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                texts.append(row['text'])
    except FileNotFoundError:
        logging.error(f"{file_path} 파일을 찾을 수 없습니다.")
    return texts

#이런식으로 불러와서 사용하기 (이건 테스트 케이스에 추가될 내용)
#WHITEOUT_TEXTS = load_whiteout_texts()

def get_whiteout_save_path():
    """화이트아웃 스크린샷의 저장 경로"""
    base_path = os.getenv("WHITEOUT_SCREEN_PATH", "src/reports/screen_shot/whiteout")

    # 저장 경로가 없으면 생성
    os.makedirs(base_path, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"whiteout_{timestamp}.png"

    # 전체 경로 반환
    return os.path.join(base_path, file_name)

        

def check_for_whiteout(page, button_text, save_path, whiteout_texts):
    try:
        page.wait_for_load_state('networkidle', timeout=10000)  

        #logging.info("페이지 컨텐츠 가져오기 시도 중...")        
        page_content = get_page_content_with_timeout(page, timeout=10000)  # 10초 동안 대기
        #logging.info("페이지 컨텐츠 가져오기 완료")

        found_text = None
        for text in whiteout_texts:
            if text in page_content:
                found_text = text
                break
        
        if found_text:
            logging.error(f"화이트아웃 화면 감지: '{found_text}' 특정 텍스트 발견")
            screenshot_path = capture_screenshot(page, f"whiteout_screen_{found_text}.png", save_path)
            
            # 화이트 아웃 발생 원인 버튼의 텍스트를 출력
            button_element = page.query_selector(f"//*[text()='{button_text}']")
            if button_element:
                element_html = page.evaluate('(element) => element.outerHTML', button_element)
                logging.error(f"화이트아웃을 발생시킨 버튼 텍스트: {button_text}")
                logging.error(f"화이트아웃을 발생시킨 버튼 HTML:\n{element_html}")
            else:
                logging.warning(f"화이트아웃을 발생시킨 버튼 '{button_text}'을(를) 찾을 수 없습니다.")
            
            #go_back_and_capture_screenshot(page, f"back_screen_{found_text}.png", save_path)

            return True  # 화이트아웃 발생 시 True 반환
            
        else:
            logging.info("정상 페이지로 보입니다.")
            return False  # 화이트아웃 미발생 시 False 반환
    except TimeoutError:
        screenshot_path = capture_screenshot(page, f"timeout_screen.png", save_path)
        logging.error(f"페이지를 로드하는 동안 타임아웃이 발생했습니다: {screenshot_path}")
        return True  # 타임아웃 발생 시 True 반환


def capture_screenshot(page, filename, save_path):
    """
    스크린샷 저장 경로 지정
    """
    # save_path와 filename을 이용하여 전체 파일 경로 생성
    full_file_path = os.path.join(save_path, filename)
    # 스크린샷 저장
    page.screenshot(path=full_file_path)
    logging.error(f"스크린샷이 저장되었습니다: {os.path.abspath(full_file_path)}")
    return full_file_path

# def go_back_and_capture_screenshot(page, filename, save_path):
#     page.go_back()
#     page.wait_for_load_state('networkidle')
#     logging.error(f"뒤로가기 후 스크린샷 저장됨: {filename}")
#     return capture_screenshot(page, filename, save_path)


def get_page_content_with_timeout(page, timeout):
    start_time = time.time()
    while True:
        try:
            # 페이지 콘텐츠를 가져오는 시도
            #logging.info("페이지 컨텐츠를 가져오는 중...")
            page_content = page.content()
            return page_content
        except TimeoutError:
            # 타임아웃 발생 시
            logging.warning(f"페이지 컨텐츠 불러오기 재시도 중,,,")
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                raise TimeoutError("페이지 콘텐츠를 가져오는 도중 타임아웃이 발생했습니다.")
            # 잠시 대기 후 재시도
            time.sleep(1)