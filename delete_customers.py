import requests
import json

# Jira 인증 정보
JIRA_URL = "https://whatap-labs.atlassian.net"
JIRA_EMAIL = "hjnoh@whatap.io"
JIRA_API_TOKEN = "ATATT3xFfGF0YAZpY6uayvK5Nnmhdf8hDyN1ndVjJBapnapujnWrtu2tA9-ebvBKRneFWGEp5IQvZKZtDYROXlNojCbdFjHgB4KAt31Vus7eyICkDANZg_R9I3NhWnuChVTbJYo4xvKntRbpfyxiGn-mWqMv513ac2Cis7ZrkSTuYKLq5kEwXjg=B1D94046"

# 삭제할 Jira 사용자 정의 필드 ID (고객사 필드)
CUSTOM_FIELD_ID = "10380"

# Jira API 엔드포인트 설정
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}
AUTH = (JIRA_EMAIL, JIRA_API_TOKEN)

# 1️⃣ 고객사 옵션 목록 가져오기
def get_custom_field_options():
    url = f"{JIRA_URL}/rest/api/3/customField/{CUSTOM_FIELD_ID}/option"
    response = requests.get(url, headers=HEADERS, auth=AUTH)
    
    if response.status_code == 200:
        options = response.json().get("values", [])
        return options
    else:
        print(f"❌ 오류: 고객사 옵션을 가져올 수 없음. 상태 코드: {response.status_code}")
        return []

# 2️⃣ 고객사 옵션 삭제하기
def delete_custom_field_option(option_id):
    url = f"{JIRA_URL}/rest/api/3/customField/{CUSTOM_FIELD_ID}/option/{option_id}"
    response = requests.delete(url, headers=HEADERS, auth=AUTH)
    
    if response.status_code == 204:
        print(f"✅ 삭제 완료: 옵션 ID {option_id}")
    else:
        print(f"❌ 오류: 옵션 ID {option_id} 삭제 실패. 상태 코드: {response.status_code}")

# 3️⃣ 전체 옵션 삭제 실행
def delete_all_custom_field_options():
    options = get_custom_field_options()
    
    if not options:
        print("ℹ️ 삭제할 옵션이 없습니다.")
        return

    for option in options:
        option_id = option.get("id")
        option_value = option.get("value")
        print(f"🗑️ 삭제 중: {option_value} (ID: {option_id})")
        delete_custom_field_option(option_id)

# 스크립트 실행
if __name__ == "__main__":
    delete_all_custom_field_options()
