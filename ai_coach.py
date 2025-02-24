import json
import re
import streamlit as st
import pandas as pd
from gemma2_recommender import get_gemma_recommendation
from user_data_utils import load_user_data
import os
import logging

# 로깅 설정 (관리자용 로그)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 사용자 데이터 불러오기 함수
def load_user_data():
    user_data = st.session_state.get("user_data", {})
    if isinstance(user_data, str):
        try:
            return json.loads(user_data)
        except json.JSONDecodeError:
            return {}
    return user_data

# 사용자 건강 정보 처리 함수
def process_user_info(user_data):
    keys = [
        "BMI", "허리둘레", "수축기혈압(최고 혈압)", "이완기혈압(최저 혈압)",
        "혈압 차이", "총콜레스테롤", "고혈당 위험", "간 지표",
        "성별", "나이", "비만 위험 지수", "흡연상태", "음주여부"
    ]
    return { key: user_data.get(key, "미측정") for key in keys }

# 원시 응답을 깔끔한 마크다운 형식으로 출력하는 함수 (디버깅용)
def display_raw_markdown(raw_text):
    st.markdown("---")
    st.markdown("**원시 응답 (마크다운):**")
    st.markdown(f"> {raw_text}")

# 식단 추천 결과 표시 함수
def display_diet_plan(diet_plan):
    if isinstance(diet_plan, dict) and "메시지" in diet_plan:
        logging.info("식단 추천 생성 중 문제가 발생했습니다. (관리자 로그 참조)")
        print("🚨 식단 추천 생성 중 문제가 발생했습니다. ")
        st.code(json.dumps(diet_plan, indent=4, ensure_ascii=False))
        return
    if isinstance(diet_plan, dict):
        diet_plan = [diet_plan]
    
    df = pd.DataFrame(diet_plan)
    expected_cols = ["요일", "아침", "점심","간식", "저녁","일일 총칼로리(kcal)","설명", "주간 총칼로리 (kcal)"]
    if all(col in df.columns for col in expected_cols):
        styled_df = (
            df[expected_cols]
            .style
            .set_properties(**{'text-align': 'center', 'font-size': '16px'})
            .background_gradient(cmap='Blues', subset=["주간 총칼로리 (kcal)"])
            .set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#4CAF50'), ('color', 'white')]}
            ])
        )
        st.dataframe(styled_df, use_container_width=True)
    else:
        # 대체 구조 (예: meals 배열) 처리
        if df.columns.str.contains("meals").any():
            transformed = []
            for item in diet_plan:
                if "meals" in item and isinstance(item["meals"], list):
                    for meal in item["meals"]:
                        meal_time = meal.get("time", "")
                        meal_food = meal.get("food", "")
                        if isinstance(meal_food, list):
                            meal_food = ", ".join(map(str, meal_food))
                        desc = meal.get("description", "")
                        if desc:
                            meal_food += f" / {desc}"
                        # 한글, 숫자, 기본 구두점만 남기기
                        meal_time = re.sub(r'[^가-힣0-9\s\.,:\(\)\[\]\-]+', '', meal_time)
                        meal_food = re.sub(r'[^가-힣0-9\s\.,:\(\)\[\]\-]+', '', meal_food)
                        transformed.append({
                            "시간": meal_time if meal_time else "(미정)",
                            "음식": meal_food if meal_food else "(내용 없음)"
                        })
            if transformed:
                st.markdown("### 식단 추천 (대체 구조로 변환)")
                df2 = pd.DataFrame(transformed)
                df2.reset_index(drop=True, inplace=True)
                styled_df2 = (
                    df2.style
                    .set_properties(**{'text-align': 'center', 'font-size': '16px'})
                    .set_table_styles([
                        {'selector': 'th', 'props': [('background-color', '#1976D2'), ('color', 'white')]}
                    ])
                )
                st.dataframe(styled_df2, use_container_width=True)
                return
        logging.info("예상하는 열이 모두 존재하지 않습니다. 아래는 원시 응답 데이터입니다.")
        print("예상하는 열이 모두 존재하지 않습니다. 아래는 원시 응답 데이터입니다.")
        
        # JSON 형식으로 보기 좋게 들여쓰기를 적용한 문자열 생성
        formatted_json = json.dumps(diet_plan, indent=4, ensure_ascii=False)
        st.code(formatted_json, language="json")


# 운동 추천 결과 표시 함수
def display_exercise_plan(exercise_plan):
    if isinstance(exercise_plan, dict) and "메시지" in exercise_plan:
        logging.info("🚨 운동 추천 생성 중 문제가 발생했습니다.")
        print("🚨 운동 추천 생성 중 문제가 발생했습니다.")
        st.code(json.dumps(exercise_plan, indent=4, ensure_ascii=False))
        return
    if isinstance(exercise_plan, dict):
        exercise_plan = [exercise_plan]
        st.table(exercise_plan)
    
    # "weekly_exercise_plan" 구조가 있다면 처리
    if (isinstance(exercise_plan, list) and exercise_plan and 
        isinstance(exercise_plan[0], dict) and "weekly_exercise_plan" in exercise_plan[0]):
        weekly_plan = exercise_plan[0].get("weekly_exercise_plan", [])
        transformed = []
        for day in weekly_plan:
            transformed.append({
                "요일": day.get("day", ""),
                "운동": day.get("focus", ""),
                "시간(분)": day.get("duration", ""),
                "종류": day.get("type", ""),
                "일일 칼로리 소모량(kcal)": day.get("daily_calories", ""),
                "설명": day.get("description", ""),
                "주간 총소모 칼로리(kcal)": day.get("weekly_calories", "")
            })
        exercise_plan = transformed
    
    if isinstance(exercise_plan, list):
        df = pd.DataFrame(exercise_plan)
        expected_cols = ["요일", "운동", "종류","시간(분)", "일일 칼로리 소모량(kcal)","설명","주간 총소모 칼로리(kcal)"]
        if all(col in df.columns for col in expected_cols):
            styled_df = (
                df[expected_cols]
                .style
                .set_properties(**{'text-align': 'center', 'font-size': '16px'})
                .background_gradient(cmap='Oranges', subset=["주간 총소모 칼로리(kcal)"])
                .set_table_styles([
                    {'selector': 'th', 'props': [('background-color', '#FF5722'), ('color', 'white')]}
                ])
            )
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.warning("예상하는 열이 모두 존재하지 않습니다. 아래는 원시 응답 데이터입니다.")
            st.json(exercise_plan)
            if len(exercise_plan) > 0:
                display_raw_markdown(str(exercise_plan[0]))
            st.code(json.dumps(exercise_plan, indent=4, ensure_ascii=False))
        return
    if isinstance(exercise_plan, dict):
        exercise_plan = [exercise_plan]
    
    else:
        logging.info("🚨 응답 형식 오류: 운동 추천 결과가 리스트 형식이 아닙니다.")
        print("🚨 응답 형식 오류: 운동 추천 결과가 리스트 형식이 아닙니다.")

def calculate_age_group(age):
    """
    나이를 10년 단위의 연령대로 변환하는 함수입니다.
    """
    try:
        age = int(age)
    except ValueError:
        return "알 수 없음"
    if age < 10:
        return "0-9세"
    elif age < 20:
        return "10대"
    elif age < 30:
        return "20대"
    elif age < 40:
        return "30대"
    elif age < 50:
        return "40대"
    elif age < 60:
        return "50대"
    elif age < 70:
        return "60대"
    else:
        return "70대 이상"

def display_ai_coach_page():
    st.header("🏋️‍♂️ AI 건강 코치")
    st.markdown("<br>", unsafe_allow_html=True)
    
    user_data = load_user_data()
    user_info = process_user_info(user_data)
    
    st.subheader("🎛️ 맞춤 건강 프로필 설정")
    st.markdown("<br>", unsafe_allow_html=True)
    goal = st.selectbox("🎯 건강 목표", ["체중 관리", "근력 증진", "심혈관 건강 개선", "전반적 웰빙 향상"])
    user_info["목표"] = goal
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        allergen_foods = st.text_input("🚫 식품 알레르기 및 기피 항목 (쉼표로 구분)", "", key="allergen_foods")
        allergen_foods = [food.strip() for food in allergen_foods.split(',') if food.strip()]
        st.markdown("<br>", unsafe_allow_html=True)
        preferred_foods = st.text_input("😋 선호하는 음식 (쉼표 구분)", "", key="preferred_foods")
        preferred_foods = [food.strip() for food in preferred_foods.split(',') if food.strip()]
        st.markdown("<br>", unsafe_allow_html=True)
        diet_restriction = st.selectbox("🍽️ 식이 요법 유형", ["선택 안함", "일반식", "채식", "육류 중심", "저탄수화물", "저지방", "글루텐 프리"])
    with col2:
        fitness_level = st.select_slider("💪 현재 체력 수준", options=["선택 안함", "매우 낮음", "낮음", "보통", "높음", "매우 높음"])
        st.markdown("<br>", unsafe_allow_html=True)
        restricted_exercises = st.text_input("⚠️ 운동 제한 사항 (쉼표로 구분)", "", key="restricted_exercises")
        restricted_exercises = [exercise.strip() for exercise in restricted_exercises.split(',') if exercise.strip()]
        st.markdown("<br>", unsafe_allow_html=True)
        exercise_preference = st.multiselect("🏃‍♀️ 선호하는 운동 유형", 
                                             ["유산소 운동", "근력 트레이닝", "유연성 운동", "균형 및 코어", 
                                              "고강도 인터벌 트레이닝", "요가", "필라테스"])
        st.markdown("<br>", unsafe_allow_html=True)
    
    user_info.update({
        "allergen_foods": allergen_foods,
        "preferred_foods": preferred_foods,
        "diet_restriction": diet_restriction,
        "restricted_exercises": restricted_exercises,
        "fitness_level": fitness_level,
        "exercise_preference": exercise_preference
    })
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🥗 식단 계획 추천", key="diet_button"):
            with st.spinner("AI가 식단을 추천하는 중...⏳"):
                additional_foods = []
                if allergen_foods:
                    additional_foods.append(("알레르기 및 기피 음식", allergen_foods))
                if preferred_foods:
                    additional_foods.append(("선호하는 음식", preferred_foods))
                if diet_restriction != "선택 안함":
                    additional_foods.append(("식이 요법", [diet_restriction]))
                diet_plan = get_gemma_recommendation("식단", user_info, additional_foods)
            display_diet_plan(diet_plan)
            st.write(user_info)
    with col2:
        if st.button("🏋️ 운동 계획 추천", key="workout_button"):
            with st.spinner("AI가 운동을 추천하는 중...⏳"):
                additional_exercises = []
                if fitness_level != "선택 안함":
                    additional_exercises.append(("체력 수준", [fitness_level]))
                if exercise_preference:
                    additional_exercises.append(("선호하는 운동 유형", exercise_preference))
                if restricted_exercises:
                    additional_exercises.append(("제한된 운동", restricted_exercises))
                exercise_plan = get_gemma_recommendation("운동", user_info, additional_exercises)
            display_exercise_plan(exercise_plan)
            st.write(exercise_plan)

def save_prediction_for_visualization(user_id, user_data, prob_exercise, prob_food):
    user_data["운동 점수"] = prob_exercise
    user_data["식단 점수"] = prob_food
    user_data["연령대"] = calculate_age_group(user_data.get("나이", 0))
    user_data["예측 날짜"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame([user_data])
    PREDICTION_FILE = "data/predictions.csv"
    if os.path.exists(PREDICTION_FILE):
        df = pd.read_csv(PREDICTION_FILE)
        df = pd.concat([df, new_data], ignore_index=True)
    else:
        df = new_data
    df.to_csv(PREDICTION_FILE, index=False)
    st.success("🎉 분석이 완료되었습니다! 아래 버튼을 클릭하여 상세한 맞춤 계획을 받아보세요.")
    if st.button("📋 맞춤 건강 계획 받기"):
        st.balloons()
        st.info("🚀 축하합니다! 당신만의 맞춤 건강 여정이 시작되었습니다. 함께 건강해져 봐요!")
    else:
        st.error("⚠️ 사용자 정보가 없습니다. 먼저 기본 정보를 입력해주세요.")

