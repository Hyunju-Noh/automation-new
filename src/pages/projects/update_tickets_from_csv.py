import requests
import json
import time
import csv

# Jira 인증 정보
JIRA_URL = "https://whatap-labs.atlassian.net"
JIRA_EMAIL = "hjnoh@whatap.io"
JIRA_API_TOKEN = "ATATT3xFfGF0YAZpY6uayvK5Nnmhdf8hDyN1ndVjJBapnapujnWrtu2tA9-ebvBKRneFWGEp5IQvZKZtDYROXlNojCbdFjHgB4KAt31Vus7eyICkDANZg_R9I3NhWnuChVTbJYo4xvKntRbpfyxiGn-mWqMv513ac2Cis7ZrkSTuYKLq5kEwXjg=B1D94046"

# 삭제할 Jira 사용자 정의 필드 ID (고객사 필드)
#CUSTOM_FIELD_ID = "customfield_10380" 테스트 고객시
CUSTOM_FIELD_ID = "customfield_10060"

# Jira API 엔드포인트 설정
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}
AUTH = (JIRA_EMAIL, JIRA_API_TOKEN)


# 1️⃣ CSV 파일에서 티켓 ID와 고객사 정보를 로드하는 함수
def load_ticket_customer_map_from_csv(csv_file_path):
    """
    CSV 파일에서 티켓 ID와 고객사 정보를 읽어 딕셔너리 형태로 반환.
    """
    ticket_customer_map = {}
    try:
        with open(csv_file_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                ticket_id = row["티켓 ID"].strip()  # 티켓 ID
                customer_name = row["고객사명"].strip()  # 고객사명
                
                if ticket_id and customer_name:
                    ticket_customer_map[ticket_id] = customer_name
    except Exception as e:
        print(f"❌ CSV 파일 읽기 오류: {e}")
    
    return ticket_customer_map

# 2️⃣ 특정 티켓의 고객사 정보를 업데이트하는 함수
def update_ticket_customer(issue_key, customer_name):
    """
    특정 티켓(issue_key)의 고객사 정보를 업데이트하는 함수.
    """
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}"

    payload = {
        "fields": {
            CUSTOM_FIELD_ID: {"value": customer_name}  # 새 고객사 값 입력
        }
    }

    response = requests.put(url, headers=HEADERS, auth=AUTH, json=payload)

    if response.status_code == 204:
        print(f"✅ 업데이트 성공: 티켓 {issue_key} -> 고객사: {customer_name}")
        return True
    else:
        print(f"❌ 업데이트 실패: 티켓 {issue_key}. 상태 코드: {response.status_code}, 응답: {response.text}")
        return False

# 3️⃣ CSV에서 로드한 티켓 목록을 업데이트하는 함수
def update_multiple_tickets_from_csv(csv_file_path):
    """
    CSV 파일에서 티켓 ID와 고객사 정보를 로드한 후 업데이트 실행.
    """
    ticket_customer_map = load_ticket_customer_map_from_csv(csv_file_path)

    if not ticket_customer_map:
        print("⚠️ 업데이트할 티켓이 없습니다. CSV 파일을 확인하세요.")
        return

    total_tickets = len(ticket_customer_map)
    print(f"🔹 {total_tickets}개의 티켓을 업데이트 시작...")

    updated_count = 0
    for issue_key, customer_name in ticket_customer_map.items():
        success = update_ticket_customer(issue_key, customer_name)

        if success:
            updated_count += 1
            time.sleep(0.5)  # API Rate Limit 방지 (0.5초 딜레이 추가)

    print(f"\n🎯 최종 결과: 총 {updated_count}/{total_tickets}개의 티켓이 성공적으로 업데이트되었습니다.")

# 4️⃣ 실행: CSV 파일에서 티켓 ID & 고객사 정보 불러와 업데이트
if __name__ == "__main__":
    csv_file_path = "/Users/nohhyunju/Downloads/tickets_to_update 2_조달청.csv"  # CSV 파일의 절대 경로 설정
    update_multiple_tickets_from_csv(csv_file_path)