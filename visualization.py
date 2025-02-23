import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# 데이터 파일 경로 설정
uploaded_file = "data/predictions.csv"

# 데이터 로드
df = pd.read_csv(uploaded_file)

# 데이터 전처리
numeric_columns = ['나이', '키', '현재 체중', '목표 체중', 'BMI', '허리둘레',
                   '수축기혈압(최고 혈압)', '이완기혈압(최저 혈압)', '혈압 차이', '콜레스테롤', 'HDL콜레스테롤',
                   'LDL콜레스테롤', '트리글리세라이드', '식전혈당(공복혈당)', '운동 가능성', '운동 점수', 
                   '식단 개선 필요성', '식단 점수', '비만 위험 지수']

df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

# NaN 값 처리
categorical_columns = ['성별', '연령대', '흡연상태', '음주여부', '고혈당 위험', '간 지표', '활동 수준']
for col in categorical_columns:
    df[col] = df[col].fillna('미상')

def display_visualization_page():   
    st.title("🏥 건강 데이터 분석 대시보드")
    st.markdown("<br>", unsafe_allow_html=True)

    # 1. 연령대별 BMI 분포 (히스토그램)
    st.header("📊 연령대별 BMI 분포")
    fig_age_bmi = px.histogram(df, x="BMI", color="연령대",
                                title="연령대별 BMI 분포",
                                labels={"BMI": "체질량지수 (BMI)"})
    st.plotly_chart(fig_age_bmi, use_container_width=True)
    st.markdown("""
        이 히스토그램은 연령대별 BMI 분포를 보여줍니다:
        - x축: 체질량지수 (BMI)를 나타냅니다. 일반적으로 18.5-24.9가 정상 범위입니다.
        - 색상: 연령대를 나타내어, 연령에 따른 BMI 분포의 차이를 시각화합니다.
        - 이를 통해 특정 연령대에서 BMI가 어떻게 분포되어 있는지 파악할 수 있습니다.
        """)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # 2. 성별에 따른 흡연 상태 (막대 차트)
    st.header("🚬 성별에 따른 흡연 상태")
    fig_gender_smoking = px.bar(df, x="성별", color="흡연상태",
                                title="성별에 따른 흡연 상태",
                                labels={"흡연상태": "흡연 상태", "성별": "성별"})
    st.plotly_chart(fig_gender_smoking, use_container_width=True)
    st.markdown("""
        이 막대 차트는 성별에 따른 흡연 상태를 보여줍니다:
        - x축: 성별을 나타냅니다 (남성, 여성).
        - 색상: 흡연 상태를 나타냅니다 (비흡연, 과거 흡연, 현재 흡연).
        - 이를 통해 성별에 따른 흡연율을 비교할 수 있습니다.
        """)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # 3. 활동 수준별 콜레스테롤 수치 (바이올린 플롯)
    st.header("❤️ 활동 수준별 콜레스테롤 수치")
    fig_activity_cholesterol = px.violin(df, x="활동 수준", y="콜레스테롤", color="활동 수준",
                                    title="활동 수준별 콜레스테롤 수치",
                                    labels={"활동 수준": "활동 수준", "콜레스테롤": "총 콜레스테롤 (mg/dL)"})
    st.plotly_chart(fig_activity_cholesterol, use_container_width=True)
    st.markdown("""
        이 바이올린 플롯은 활동 수준별 콜레스테롤 수치를 보여줍니다:
        - x축: 활동 수준을 나타냅니다 (낮음, 보통, 높음).
        - y축: 총 콜레스테롤 수치를 나타냅니다. 일반적으로 200mg/dL 이하가 바람직한 수준입니다.
        - 이 차트를 통해 활동 수준에 따른 콜레스테롤 분포를 파악할 수 있습니다.
        """)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # 4. 고혈당 위험에 따른 BMI 분포 (박스 플롯)
    st.header("🩸 고혈당 위험에 따른 BMI 분포")
    fig_glucose_bmi = px.box(df, x="고혈당 위험", y="BMI", color="고혈당 위험",
                            title="고혈당 위험에 따른 BMI 분포",
                            labels={"고혈당 위험": "고혈당 위험", "BMI": "체질량지수 (BMI)"})
    st.plotly_chart(fig_glucose_bmi, use_container_width=True)
    st.markdown("""
        이 박스 플롯은 고혈당 위험에 따른 BMI 분포를 보여줍니다:
        - x축: 고혈당 위험 수준을 나타냅니다 (낮음, 보통, 높음).
        - y축: 체질량지수 (BMI)를 나타냅니다. 일반적으로 18.5-24.9가 정상 범위입니다.
        - 이 차트를 통해 고혈당 위험 수준에 따른 BMI 분포를 파악할 수 있습니다.
        """)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # 5. 음주 여부에 따른 간 지표 (히스토그램)
    st.header("🍺 음주 여부에 따른 간 지표")
    fig_drinking_liver = px.histogram(df, x="간 지표", color="음주여부",
                                    title="음주 여부에 따른 간 지표",
                                    labels={"간 지표": "간 지표", "음주여부": "음주 여부"})
    st.plotly_chart(fig_drinking_liver, use_container_width=True)
    st.markdown("""
        이 히스토그램은 음주 여부에 따른 간 지표를 보여줍니다:
        - x축: 간 지표를 나타냅니다 (정상, 경계, 위험).
        - 색상: 음주 여부를 나타냅니다 (비음주, 가끔, 자주).
        - 이 차트를 통해 음주 여부에 따른 간 건강 상태를 비교할 수 있습니다.
        """)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")


