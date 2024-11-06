import os
import csv
import logging

def load_project_data():
    """CSV 파일에서 프로젝트 데이터를 로드합니다."""
    file_path = os.getenv("PROJECT_DATA_PATH", "data/project_data.csv")  # 환경 변수로 경로 설정

    projects = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                projects.append(row)
    except FileNotFoundError:
        logging.error(f"{file_path} 파일을 찾을 수 없습니다.")
    return projects
