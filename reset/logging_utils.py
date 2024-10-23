import os
import logging
from datetime import datetime

def setup_logging():
    """
    로그 설정을 초기화하는 함수. 파일 경로를 설정하고 로그 파일을 생성한다.
    """
    # 로깅 설정 파일 위치 설정 (파일 없으면 새로 생성)
    log_save_path = os.getenv("LOG_FILE_PATH", "./logs")  # 로그 파일 경로를 환경 변수로 설정
    if not os.path.exists(log_save_path):
        os.makedirs(log_save_path)

    #로그 파일 이름 설정
    log_filename = os.path.join(log_save_path, f"PasswordReset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    #로깅 설정 초기화
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_filename)
        ]
    )

#테스트 로그 결과값 메시징
def log_result(success, message):
    if success:
        logging.info(f"✅ {message}")
    else:
        logging.error(f"❌ {message}")
