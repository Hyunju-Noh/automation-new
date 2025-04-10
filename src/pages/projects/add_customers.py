import requests
import json
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
    

# 2️⃣ 현재 Jira에 존재하는 고객사 목록 가져오기 (중복 방지)
def get_existing_customers(context_id):
    url = f"{JIRA_URL}/rest/api/3/field/{CUSTOM_FIELD_ID}/context/{context_id}/option"
    response = requests.get(url, headers=HEADERS, auth=AUTH)

    existing_customers = set()
    if response.status_code == 200:
        options = response.json().get("values", [])
        for option in options:
            existing_customers.add(option["value"].strip().lower())  # 중복 방지를 위해 소문자로 변환
    else:
        print(f"❌ 오류: 기존 고객사 목록 가져오기 실패. 상태 코드: {response.status_code}, 응답: {response.text}")
    
    return existing_customers  # 기존 고객사 목록 반환


# 3️⃣ CSV 파일에서 고객사 목록 불러오기 (중복 제거)
def read_customers_from_csv(file_path):
    customers = set()  # 중복 제거를 위해 set 사용
    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)  # 첫 번째 줄을 헤더로 인식
            for row in reader:
                customers.add(row["고객사명"].strip())  # 공백 제거 후 중복 저장 방지
    except Exception as e:
        print(f"❌ CSV 파일 읽기 오류: {e}")
    return list(customers)  # set → list 변환하여 반환


# 4️⃣ 새로운 고객사 옵션 추가 (1,000개씩 나누어 요청 + 추가 개수 카운트)
def add_custom_field_options(context_id, new_options):
    url = f"{JIRA_URL}/rest/api/3/field/{CUSTOM_FIELD_ID}/context/{context_id}/option"

    total_added_customers = 0  # 추가된 고객사 수 추적

    # 1,000개 이하로 나누어 API 요청 보내기
    batch_size = 1000
    for i in range(0, len(new_options), batch_size):
        batch = new_options[i:i + batch_size]  # 1,000개 이하로 나누기
        data = {"options": [{"value": option} for option in batch]}

        print(f"🚀 추가 요청 보냄 (Batch {i // batch_size + 1}): {len(batch)}개")

        response = requests.post(url, headers=HEADERS, auth=AUTH, json=data)

        if response.status_code == 201:
            print(f"✅ 고객사 옵션 추가 완료: {len(batch)}개 추가됨")
            total_added_customers += len(batch)
        else:
            print(f"❌ 오류: 고객사 옵션 추가 실패. 상태 코드: {response.status_code}, 응답: {response.text}")

    return total_added_customers  # 추가된 고객사 개수 반환


# 5️⃣ CSV에서 고객사 불러와 중복되지 않은 고객사만 추가 실행
def add_new_customer_options_from_csv(csv_file_path):
    context_id = get_field_context_id()
    if not context_id:
        print("⚠️ 필드 컨텍스트 ID를 찾을 수 없어 고객사를 추가할 수 없습니다.")
        return

    # 현재 Jira에 존재하는 고객사 목록 가져오기
    existing_customers = get_existing_customers(context_id)

    # CSV 파일에서 고객사 목록 읽어오기
    new_customers = read_customers_from_csv(csv_file_path)

    # 중복되지 않은 고객사만 추가 (대소문자 비교 포함)
    unique_customers = [customer for customer in new_customers if customer.lower() not in existing_customers]

    if not unique_customers:
        print("⚠️ 추가할 새로운 고객사가 없습니다. (모두 이미 존재하는 고객사임)")
        return

    print(f"🔹 {len(unique_customers)}개의 고객사 추가 요청 시작...")

    # 새로운 고객사 추가 요청
    total_added = add_custom_field_options(context_id, unique_customers)

    # 최종 결과 출력
    print(f"\n🎯 최종 결과: 총 {total_added}개의 고객사가 Jira에 추가되었습니다.")
    print(f"✅ 기존 고객사: {len(existing_customers)}개")
    print(f"✅ 추가 요청한 고객사: {len(unique_customers)}개")
    print(f"✅ 실제 추가된 고객사: {total_added}개")

# 스크립트 실행
if __name__ == "__main__":
    csv_file_path = "/Users/nohhyunju/Downloads/customers.csv"  # CSV 파일의 절대 경로 설정
    add_new_customer_options_from_csv(csv_file_path)
