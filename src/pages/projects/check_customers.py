import requests
import json
import time

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

# 1️⃣ 필드 컨텍스트 ID 가져오기
def get_field_context_id():
    url = f"{JIRA_URL}/rest/api/3/field/{CUSTOM_FIELD_ID}/context"
    response = requests.get(url, headers=HEADERS, auth=AUTH)

    if response.status_code == 200:
        contexts = response.json().get("values", [])
        if contexts:
            return contexts[0].get("id")  # 첫 번째 컨텍스트 ID 반환
        else:
            print("❌ 오류: 필드 컨텍스트 ID를 찾을 수 없음")
            return None
    else:
        print(f"❌ 오류: 필드 컨텍스트 ID 가져오기 실패. 상태 코드: {response.status_code}, 응답: {response.text}")
        return None

# 2️⃣ 모든 고객사 옵션 개수 가져오기 (페이지네이션 적용)
def get_customer_count():
    context_id = get_field_context_id()
    if not context_id:
        print("⚠️ 필드 컨텍스트 ID를 찾을 수 없어 고객사 목록을 확인할 수 없습니다.")
        return

    total_customers = 0  # 전체 고객사 개수
    start_at = 0         # 페이지네이션 시작 위치
    max_results = 100    # 일부 Jira 인스턴스는 100이 최대값이므로 100으로 설정

    while True:
        url = f"{JIRA_URL}/rest/api/3/field/{CUSTOM_FIELD_ID}/context/{context_id}/option?startAt={start_at}&maxResults={max_results}"
        response = requests.get(url, headers=HEADERS, auth=AUTH)

        if response.status_code == 200:
            options = response.json().get("values", [])
            total_customers += len(options)  # 현재 페이지에서 가져온 개수 추가
            print(f"🔹 {len(options)}개 로드됨 (총 {total_customers}개)")

            if len(options) < max_results:
                # 마지막 페이지 도달
                break
            else:
                # 다음 페이지 요청을 위해 start_at 증가
                start_at += max_results
        else:
            print(f"❌ 오류: 고객사 옵션 목록을 가져올 수 없음. 상태 코드: {response.status_code}, 응답: {response.text}")
            return None

    print(f"✅ 현재 Jira에 등록된 고객사 옵션 개수: {total_customers}개")
    return total_customers

# 스크립트 실행
if __name__ == "__main__":
    get_customer_count()