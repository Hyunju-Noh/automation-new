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

# 2️⃣ 고객사 옵션 목록 가져오기
def get_custom_field_options(context_id):
    url = f"{JIRA_URL}/rest/api/3/field/{CUSTOM_FIELD_ID}/context/{context_id}/option"
    response = requests.get(url, headers=HEADERS, auth=AUTH)

    if response.status_code == 200:
        options = response.json().get("values", [])
        return options
    else:
        print(f"❌ 오류: 고객사 옵션을 가져올 수 없음. 상태 코드: {response.status_code}, 응답: {response.text}")
        return []

# 3️⃣ 고객사 옵션 삭제하기 (재시도 기능 추가)
def delete_custom_field_option(context_id, option_id):
    url = f"{JIRA_URL}/rest/api/3/field/{CUSTOM_FIELD_ID}/context/{context_id}/option/{option_id}"

    retry_count = 3  # 최대 3번 재시도
    for attempt in range(retry_count):
        response = requests.delete(url, headers=HEADERS, auth=AUTH)

        if response.status_code == 204:
            print(f"✅ 삭제 완료: 옵션 ID {option_id}")
            return True  # 삭제 성공
        else:
            print(f"❌ 오류: 옵션 ID {option_id} 삭제 실패 (시도 {attempt + 1}/{retry_count}). 상태 코드: {response.status_code}, 응답: {response.text}")
            time.sleep(1)  # 재시도 전에 1초 대기

    print(f"🚨 최종 삭제 실패: 옵션 ID {option_id}")
    return False  # 삭제 실패

# 4️⃣ 전체 옵션 삭제 실행 (반복 실행하여 모든 항목 삭제)
def delete_all_custom_field_options():
    context_id = get_field_context_id()
    if not context_id:
        print("⚠️ 필드 컨텍스트 ID를 찾을 수 없어 삭제할 수 없습니다.")
        return

    while True:  # 모든 옵션이 삭제될 때까지 반복 실행
        options = get_custom_field_options(context_id)
        
        if not options:
            print("🎯 모든 고객사 옵션이 삭제되었습니다!")
            break  # 옵션이 없으면 종료

        print(f"🔹 {len(options)}개의 고객사 옵션 삭제 시작...")

        # 옵션 삭제 진행
        for option in options:
            option_id = str(option.get("id"))  # 옵션 ID를 문자열로 변환
            option_value = option.get("value")
            #print(f"🗑️ 삭제 중: {option_value} (ID: {option_id})")
            success = delete_custom_field_option(context_id, option_id)

            if success:
                time.sleep(0.5)  # API 요청 속도를 조절하여 Rate Limit 방지

# 스크립트 실행
if __name__ == "__main__":
    delete_all_custom_field_options()
