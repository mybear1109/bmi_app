import json
import re
import streamlit as st
import pandas as pd
from gemma2_recommender import get_gemma_recommendation
from user_data_utils import load_user_data
import os

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
        "성별", "연령대", "비만 위험 지수", "흡연상태", "음주여부"
    ]
    return { key: user_data.get(key, "미측정") for key in keys }

# 원시 응답을 깔끔한 마크다운 형식으로 출력하는 함수 (디버깅용)
def display_raw_markdown(raw_text):
    st.markdown("---")
    st.markdown("**원시 응답 (마크다운):**")
    st.markdown(f"> {raw_text}")

# 대체 구조(중첩된 식단 구조)를 평탄화하는 함수
def flatten_diet_plan(plan: dict) -> dict:
    """
    plan 예시:
    {
      "일일 총칼로리": 1300,
      "아침": {"메뉴": "계란 + 오트밀 (130g), 과일 1개, 생선 150g", "칼로리": 300},
      "점심": {"메뉴": "닭가슴살 샐러드 (150g), 콩나물 150g", "칼로리": 400},
      "저녁": {"메뉴": "구운 채소 + 연어 (150g), 랑치 150g, 주스 150ml", "칼로리": 450},
      "간식": {"메뉴": "그릭 요거트 (150g)", "칼로리": 150},
      "설명": "고단백 저탄수화물 식단으로 체지방 감소 도움"
    }
    평탄화 결과:
    {
      "일일 총칼로리": 1300,
      "아침 메뉴": "계란 + 오트밀 (130g), 과일 1개, 생선 150g",
      "아침 칼로리": 300,
      "점심 메뉴": "닭가슴살 샐러드 (150g), 콩나물 150g",
      "점심 칼로리": 400,
      "저녁 메뉴": "구운 채소 + 연어 (150g), 랑치 150g, 주스 150ml",
      "저녁 칼로리": 450,
      "간식 메뉴": "그릭 요거트 (150g)",
      "간식 칼로리": 150,
      "설명": "고단백 저탄수화물 식단으로 체지방 감소 도움"
    }
    """
    flat = {}
    for key, value in plan.items():
        if isinstance(value, dict):
            flat[f"{key} 메뉴"] = value.get("메뉴", "")
            flat[f"{key} 칼로리"] = value.get("칼로리", "")
        else:
            flat[key] = value
    return flat

# 식단 추천 결과 표시 함수
def display_diet_plan(diet_plan):
    # 오류 응답 처리
    if isinstance(diet_plan, dict) and "메시지" in diet_plan:
        st.error("🚨 식단 추천 생성 중 문제가 발생했습니다. (관리자 로그 참조)")
        st.code(json.dumps(diet_plan, indent=4, ensure_ascii=False))
        return
    if isinstance(diet_plan, dict):
        diet_plan = [diet_plan]
    
    df = pd.DataFrame(diet_plan)
    # 기본 예상 열 구조
    expected_cols = ["요일", "아침", "점심", "저녁", "총칼로리 (kcal)"]
    if all(col in df.columns for col in expected_cols):
        styled_df = (
            df[expected_cols]
            .style
            .set_properties(**{'text-align': 'center', 'font-size': '16px'})
            .background_gradient(cmap='Blues', subset=["총칼로리 (kcal)"])
            .set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#4CAF50'), ('color', 'white')]}
            ])
        )
        st.dataframe(styled_df, use_container_width=True)
    # 대체 구조 처리: 예를 들어 '일일 총칼로리' 키가 존재하는 경우
    elif "일일 총칼로리" in df.columns:
        # 평탄화하여 새로운 DataFrame 생성
        flat_data = [flatten_diet_plan(item) for item in diet_plan if isinstance(item, dict)]
        df2 = pd.DataFrame(flat_data)
        # 예상 대체 열 구조
        alt_expected = ["일일 총칼로리", "아침 메뉴", "아침 칼로리",
                        "점심 메뉴", "점심 칼로리",
                        "저녁 메뉴", "저녁 칼로리",
                        "간식 메뉴", "간식 칼로리", "설명"]
        missing = [col for col in alt_expected if col not in df2.columns]
        if missing:
            st.warning(f"대체 열 중 누락된 열: {', '.join(missing)}. 원시 응답 데이터를 확인하세요.")
            st.json(diet_plan)
            display_raw_markdown(str(diet_plan[0]))
        else:
            styled_df2 = (
                df2[alt_expected]
                .style
                .set_properties(**{'text-align': 'center', 'font-size': '16px'})
                .set_table_styles([
                    {'selector': 'th', 'props': [('background-color', '#1976D2'), ('color', 'white')]}
                ])
            )
            st.dataframe(styled_df2, use_container_width=True)
    else:
        st.warning("예상하는 열이 모두 존재하지 않습니다. 아래는 원시 응답 데이터입니다.")
        st.json(diet_plan)
        if len(diet_plan) > 0:
            display_raw_markdown(str(diet_plan[0]))

# 운동 추천 결과 표시 함수
def display_exercise_plan(exercise_plan):
    if isinstance(exercise_plan, dict) and "메시지" in exercise_plan:
        st.error("🚨 운동 추천 생성 중 문제가 발생했습니다. (관리자 로그 참조)")
        st.code(json.dumps(exercise_plan, indent=4, ensure_ascii=False))
        return
    if isinstance(exercise_plan, dict):
        exercise_plan = [exercise_plan]
    
    # weekly_exercise_plan 구조가 있으면 변환 처리
    if (isinstance(exercise_plan, list) and exercise_plan and 
        isinstance(exercise_plan[0], dict) and "weekly_exercise_plan" in exercise_plan[0]):
        weekly_plan = exercise_plan[0].get("weekly_exercise_plan", [])
        transformed = []
        for day in weekly_plan:
            transformed.append({
                "요일": day.get("day", ""),
                "운동": day.get("focus", ""),
                "시간(분)": day.get("duration", ""),
                "칼로리 소모량(kcal)": "정보 없음"
            })
        exercise_plan = transformed
    
    if isinstance(exercise_plan, list):
        df = pd.DataFrame(exercise_plan)
        expected_cols = ["요일", "운동", "시간(분)", "칼로리 소모량(kcal)"]
        if all(col in df.columns for col in expected_cols):
            styled_df = (
                df[expected_cols]
                .style
                .set_properties(**{'text-align': 'center', 'font-size': '16px'})
                .background_gradient(cmap='Oranges', subset=["칼로리 소모량(kcal)"])
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
    else:
        st.error("🚨 응답 형식 오류: 운동 추천 결과가 리스트 형식이 아닙니다.")

# --- 메인 페이지 표시 함수 ---
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

# 최종 예측 결과를 CSV 파일에 저장하는 함수
def save_prediction_for_visualization(user_id, user_data, prob_exercise, prob_food):
    user_data["운동 점수"] = prob_exercise
    user_data["식단 점수"] = prob_food
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
