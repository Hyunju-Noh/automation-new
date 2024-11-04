import os
import logging
from datetime import datetime

def setup_logging():
    """공통 로그 설정 초기화 함수."""
    os.makedirs(log_save_path, exist_ok=True)
    log_filename = os.path.join(log_save_path, custom_log_filename)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_filename)
        ]
    )


def setup_logging_password_reset():
    """Password reset 로그 설정."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_save_path = "src/reports/logs/password_reset"
    custom_log_filename = f"PasswordReset_{timestamp}.log"
    setup_logging(log_save_path, custom_log_filename)


def setup_logging_projectpage():
    """Project page 로그 설정."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_save_path = "src/reports/logs/project_page"
    custom_log_filename = f"ProjectPage_{timestamp}.log"
    setup_logging(log_save_path, custom_log_filename)


#테스트 로그 결과값 메시징
def log_result(success, message):
    if success:
        logging.info(f"✅ {message}")
    else:
        logging.error(f"❌ {message}")
