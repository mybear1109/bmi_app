import json
import streamlit as st
import pandas as pd
from gemma2_recommender import get_gemma_recommendation

# ✅ AI 건강 코치 페이지
def display_ai_coach_page():
    st.header("🏋️‍♂️ AI 건강 코치")

    # ✅ 사용자 데이터 불러오기 및 처리
    user_data = load_user_data()
    user_info = process_user_info(user_data)

    # ✅ 사용자 입력 (알러지 및 제한된 운동)
    goal, excluded_foods, restricted_exercises = get_user_inputs()

    # ✅ 운동 및 식단 추천 버튼 (하나로 통합)
    if st.button("🏋️🥗 운동 및 식단 계획 추천 받기", key="recommend_button"):
        generate_recommendation(user_info, goal, excluded_foods)

# ✅ 사용자 데이터 불러오기
def load_user_data():
    user_data = st.session_state.get("user_data", {})
    if isinstance(user_data, str):
        try:
            return json.loads(user_data)
        except json.JSONDecodeError:
            return {}
    return user_data

# ✅ 사용자 건강 정보 처리
def process_user_info(user_data):
    return {
        key: user_data.get(key, "미측정") for key in [
            "BMI", "허리둘레", "수축기혈압(최고 혈압)", "이완기혈압(최저 혈압)", "혈압 차이",
            "총콜레스테롤", "고혈당 위험", "간 지표", "성별", "연령대", "비만 위험 지수", "흡연상태", "음주여부"
        ]
    }

# ✅ 사용자 입력 받기 (목표 + 알러지 및 제한된 운동)
def get_user_inputs():
    st.subheader("⚙️ 개인화 설정")
    
    goal = st.selectbox("🎯 목표 설정", ["체중 감량", "근력 향상", "혈압 관리", "일반 건강 관리"])

    excluded_foods = st.text_input("🍴 알러지 또는 못 먹는 음식 입력 (쉼표 구분)", "", key="excluded_foods")
    excluded_foods = [food.strip() for food in excluded_foods.split(',') if food.strip()]
    restricted_exercises = st.text_input("🏋️ 제한된 운동 입력 (쉼표 구분)", "", key="restricted_exercises")
    restricted_exercises = [exercise.strip() for exercise in restricted_exercises.split(',') if exercise.strip()]

    return goal, excluded_foods, restricted_exercises

# ✅ 운동 및 식단 추천 생성 (하나의 버튼에서 실행)
def generate_recommendation(user_info, goal, excluded_foods=None):
    with st.spinner("AI가 운동 및 식단 계획을 추천하는 중...⏳"):
        # ✅ 운동 및 식단 추천을 동시에 요청
        exercise_plan = get_gemma_recommendation("운동", user_info)
        diet_plan = get_gemma_recommendation("식단", user_info, excluded_foods)

    st.success("✅ 맞춤형 식단 & 운동 추천이 완료되었습니다!")
    st.table(diet_plan)
    

# ✅ Markdown 테이블을 DataFrame으로 변환 (빈 열 자동 제거)
def parse_markdown_table(content):
    """Markdown 형식의 표를 DataFrame으로 변환 (빈 열 자동 제거)"""
    lines = content.strip().split("\n")

    # ✅ 테이블 헤더 감지
    headers = [h.strip() for h in lines[0].split("|")[1:-1]]
    data = [row.split("|")[1:-1] for row in lines[2:]]

    # ✅ 빈 열 자동 제거
    filtered_data = [row for row in data if len(row) == len(headers)]
    if not filtered_data:
        return None

    df = pd.DataFrame(filtered_data, columns=headers)
    return df.to_dict(orient="records")

# ✅ 일반 텍스트를 리스트로 변환
def parse_text_based_response(content):
    """일반 텍스트에서 요일별 운동 및 식단 정보를 리스트로 변환"""
    lines = content.split("\n")
    result = []
    for line in lines:
        match = re.match(r"(\w+):\s*(.+)", line)
        if match:
            요일, 내용 = match.groups()
            result.append({"요일": 요일, "내용": 내용})
    return result if result else None

# ✅ JSON 형식의 응답을 파싱

def parse_response(response, category):
    """AI 응답이 JSON, Markdown, 일반 텍스트 등 다양한 형식일 경우 자동 변환"""
    if isinstance(response, dict) and "메시지" in response:
        response = response["메시지"]

    if isinstance(response, str):
        # ✅ JSON 변환 시도
        try:
            parsed_response = json.loads(response)
            if isinstance(parsed_response, list):
                return parsed_response
        except json.JSONDecodeError:
            pass  # JSON 변환 실패 시 계속 진행

        # ✅ Markdown 테이블 변환 시도
        if "|" in response:
            return parse_markdown_table(response)

        # ✅ 일반 텍스트 변환 시도
        return parse_text_based_response(response)

    elif isinstance(response, list):
        return response
    else:
        return None
