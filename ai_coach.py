import json
import streamlit as st
import pandas as pd
from gemma2_recommender import get_gemma_recommendation
import re

def parse_text_to_dict(response_text):
    """📌 응답 텍스트를 JSON 구조의 딕셔너리로 변환"""
    structured_data = {"운동": [], "식단": []}
    current_section = None
    current_day = None

    # 줄 단위로 텍스트 파싱
    for line in response_text.split("\n"):
        line = line.strip()

        # 📌 운동 및 식단 섹션 감지
        if "**운동 추천:**" in line:
            current_section = "운동"
        elif "**식단 추천:**" in line:
            current_section = "식단"

        # 📌 운동 데이터 처리
        elif current_section == "운동" and re.match(r"\* \*\*.*:\*\*", line):
            current_day, content = re.findall(r"\*\*\s?(.*?):\*\*", line)[0], line.split(":")[1].strip()
            structured_data["운동"].append({"요일": current_day, "운동 내용": content})

        # 📌 식단 데이터 처리
        elif current_section == "식단" and re.match(r"\* \*\*.*:\*\*", line):
            meal_type, meal_content = re.findall(r"\*\*\s?(.*?):\*\*", line)[0], line.split(":")[1].strip()
            if len(structured_data["식단"]) == 0 or structured_data["식단"][-1]["요일"] != current_day:
                structured_data["식단"].append({"요일": current_day, meal_type: meal_content})
            else:
                structured_data["식단"][-1][meal_type] = meal_content

    return structured_data




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
def generate_recommendation(user_info, goal, excluded_foods):
    with st.spinner("AI가 운동 및 식단 계획을 추천하는 중...⏳"):
        # ✅ 운동 및 식단 추천을 동시에 요청
        exercise_plan = get_gemma_recommendation("운동", user_info)
        diet_plan = get_gemma_recommendation("식단", user_info, excluded_foods)
        all_excluded_foods = exercise_plan, diet_plan
        
    st.success("✅ 맞춤형 식단 & 운동 추천이 완료되었습니다!")
    st.table(all_excluded_foods)

        
def clean_and_format_data(data):
    # 불필요한 마크다운 구문 제거
    cleaned_data = re.sub(r'[*#\-_|]', '', data)
    
    # 여러 줄의 공백을 하나의 줄바꿈으로 대체
    cleaned_data = re.sub(r'\n\s*\n', '\n', cleaned_data)
    
    # 콜론 뒤의 공백 제거
    cleaned_data = re.sub(r':\s+', ': ', cleaned_data)
    
    return cleaned_data.strip()

def display_formatted_data(data):
    cleaned_data = clean_and_format_data(data)
    
    # 데이터를 줄 단위로 분할
    lines = cleaned_data.split('\n')
    
    # 데이터프레임 생성
    all_excluded_foods = pd.DataFrame(lines, columns=['내용'])
    
    # 스타일이 적용된 테이블로 표시
    st.markdown("""
    <style>
    .dataframe {
        font-size: 14px;
        color: #333;
        border-collapse: collapse;
        width: 100%;
    }
    .dataframe th, .dataframe td {
        padding: 8px;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }
    .dataframe tr:hover {background-color: #f5f5f5;}
    </style>
    """, unsafe_allow_html=True)
    
    st.table(all_excluded_foods)

# 예시 사용
all_excluded_foods = """
## 사용자 맞춤형 건강 가이드
안녕하세요! 당신의 건강 상태를 바탕으로 당신에게 가장 적합한 7일 운동 계획과 식단을 제시해 드리겠습니다.

**현재 건강 상태 기반 점수:**
* **운동 추천 점수:** 65/100
* **식단 추천 점수:** 75/100

**7일 운동 계획:**
| 요일 | 운동 | 칼로리 소모 | 설명 |
|---|---|---|---|
| 월 | 달리기 30분 | 300kcal | 심폐 건강 개선 및 지방 연소 효과 |
| 화 | 웨이트 트레이닝 (상체) | 400kcal | 근력 강화 및 신진대사 촉진 |
| 수 | 수영 30분 | 350kcal | 전신 근력 강화 및 체력 증진 |
| 목 | 휴식 | 0kcal | 근육 회복 및 지치지 않기 위한 휴식 |
| 금 | 웨이트 트레이닝 (하체) | 450kcal | 하체 근력 강화 및 골밀도 증가 |
| 토 | 요가 45분 | 250kcal | 유연성 향상 및 스트레스 완화 |
| 일 | 자전거 45분 | 400kcal | 심폐 기능 향상 및 근력 강화 |

**참고:**
* 각 운동 전후 스트레칭 필수.
* 운동 강도는 개인의 체력 수준에 맞게 조절 가능.
* 부상 예방을 위해 올바른 자세 유지.
"""

display_formatted_data(all_excluded_foods)

