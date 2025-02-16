
import streamlit as st
from data_loader import load_data
from model_loader import load_models
from prediction import predict_exercise, predict_food
from visualization import show_visualizations

# 앱 타이틀
st.title("🏋️‍♂️ AI 건강 분석 시스템")

# 데이터 로드
df = load_data()

# 모델 로드
model_exercise, model_food = load_models()

# 사이드바 메뉴
menu = st.sidebar.selectbox("메뉴 선택", ["🏠 홈", "📊 데이터 시각화", "🏋️‍♂️ 운동 예측", "🍽️ 음식 섭취 예측"])

if menu == "🏠 홈":
    st.write("### AI 기반 건강 분석 플랫폼입니다.")
    st.write("운동 및 음식 섭취 패턴을 분석하여 건강한 생활 습관을 지원합니다.")

elif menu == "📊 데이터 시각화":
    show_visualizations(df)

elif menu == "🏋️‍♂️ 운동 예측":
    predict_exercise(df, model_exercise)

elif menu == "🍽️ 음식 섭취 예측":
    predict_food(df, model_food)
