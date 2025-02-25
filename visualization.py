# visualization.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def load_data():
    return pd.read_csv("data/predictions.csv")

def display_visualization_page():
    st.title("🏥 건강 데이터 분석 대시보드")
    df = load_data()

    numeric_columns = ['나이', '키', '현재 체중', '목표 체중', 'BMI', '허리둘레',
                       '수축기혈압(최고 혈압)', '이완기혈압(최저 혈압)', '혈압 차이', '총콜레스테롤', 'HDL콜레스테롤',
                       'LDL콜레스테롤', '트리글리세라이드', '식전혈당(공복혈당)', '운동 개선 필요성', '운동 점수', 
                       '식단 개선 필요성', '식단 점수', '비만 위험 지수']

    # 1. BMI 분포 히스토그램
    st.header("1. BMI 분포")
    fig_bmi = px.histogram(df, x="BMI", nbins=25, marginal="box", 
                        color_discrete_sequence=['#3366cc'])  # 파란색 계열로 변경
    # 막대 너비와 불투명도 조절
    fig_bmi.update_traces(marker=dict(line=dict(width=1.5, color='#ffffff')),  # 테두리 두께와 색상 조절
                        opacity=0.75)  # 불투명도 조절
    # 레이아웃 업데이트
    fig_bmi.update_layout(
        title="BMI 분포",
        xaxis_title="BMI",
        yaxis_title="빈도",
        width=800,  # 그래프 너비
        height=500,  # 그래프 높이
        bargap=0.1  # 막대 사이 간격
    )
    st.plotly_chart(fig_bmi)
    st.markdown("""
    이 히스토그램은 전체 사용자의 BMI 분포를 보여줍니다:
    - x축은 BMI 값을, y축은 각 BMI 값의 빈도를 나타냅니다.
    - 그래프 상단의 박스플롯은 BMI의 중앙값, 사분위수 범위, 이상치를 보여줍니다.
    - 대부분의 사용자가 어느 BMI 범위에 속하는지, 극단적인 값은 얼마나 있는지 파악할 수 있습니다.
    - 이 정보는 전반적인 사용자 건강 상태를 이해하고, 비만 관련 건강 정책을 수립하는 데 도움이 됩니다.
    """)

    # 2. 연령대별 BMI 박스플롯
    st.header("2. 연령대별 BMI 분포")
    fig_age_bmi = px.box(df, x="연령대", y="BMI", color="성별")
    fig_age_bmi.update_layout(title="연령대 및 성별에 따른 BMI 분포", xaxis_title="연령대", yaxis_title="BMI")
    st.plotly_chart(fig_age_bmi)
    st.markdown("""
    이 박스플롯은 연령대와 성별에 따른 BMI 분포를 보여줍니다:
    - x축은 연령대를, y축은 BMI 값을 나타냅니다. 색상은 성별을 구분합니다.
    - 각 박스는 해당 연령대와 성별의 BMI 중앙값, 사분위수 범위, 이상치를 보여줍니다.
    - 이를 통해 연령이 증가함에 따른 BMI 변화 추세, 성별 간 BMI 차이를 파악할 수 있습니다.
    - 특정 연령대나 성별에서 BMI가 높게 나타나는 경우, 해당 그룹에 대한 맞춤형 건강 관리 전략을 수립할 수 있습니다.
    """)

    # 3. 혈압과 콜레스테롤의 관계 산점도
    st.header("3. 혈압과 콜레스테롤의 관계")
    fig_bp_chol = px.scatter(df, x="수축기혈압(최고 혈압)", y="총콜레스테롤", color="연령대", size="BMI")
    fig_bp_chol.update_layout(title="혈압과 콜레스테롤의 관계", xaxis_title="수축기 혈압 (mmHg)", yaxis_title="총 콜레스테롤 (mg/dL)")
    st.plotly_chart(fig_bp_chol)
    st.markdown("""
    이 산점도는 수축기 혈압과 총 콜레스테롤의 관계를 보여줍니다:
    - x축은 수축기 혈압을, y축은 총 콜레스테롤 수치를 나타냅니다.
    - 점의 색상은 연령대를, 크기는 BMI를 나타냅니다.
    - 이 그래프를 통해 혈압, 콜레스테롤, 연령, BMI 간의 복합적인 관계를 파악할 수 있습니다.
    - 예를 들어, 고혈압과 고콜레스테롤이 동시에 나타나는 경향이 있는지, 이러한 경향이 특정 연령대나 BMI 범위에서 더 두드러지는지 확인할 수 있습니다.
    - 이는 심혈관 질환 위험 평가와 예방 전략 수립에 중요한 정보를 제공합니다.
    """)

    # 4. 운동 점수와 식단 점수의 상관관계
    st.header("4. 운동 점수와 식단 점수의 상관관계")
    fig_exercise_diet = px.scatter(df, x="운동 점수", y="식단 점수", color="BMI", hover_data=["나이"])
    fig_exercise_diet.update_layout(title="운동 점수와 식단 점수의 관계", xaxis_title="운동 점수", yaxis_title="식단 점수")
    st.plotly_chart(fig_exercise_diet)
    st.markdown("""
    이 산점도는 운동 점수와 식단 점수 간의 관계를 보여줍니다:
    - x축은 운동 점수를, y축은 식단 점수를 나타냅니다. 점의 색상은 BMI를 나타냅니다.
    - 마우스를 점 위에 올리면 해당 사용자의 나이 정보도 확인할 수 있습니다.
    - 이 그래프를 통해 운동 습관과 식습관 간의 상관관계를 파악할 수 있습니다.
    - 예를 들어, 운동 점수가 높은 사람들이 식단 점수도 높은 경향이 있는지, 또는 이러한 관계가 BMI나 나이에 따라 어떻게 달라지는지 확인할 수 있습니다.
    - 이 정보는 종합적인 건강 관리 프로그램 개발에 유용하게 활용될 수 있습니다.
    """)

    # 5. 비만 위험 지수와 고혈당 위험의 관계
    st.header("5. 비만 위험 지수와 고혈당 위험의 관계")
    fig_obesity_diabetes = px.box(df, x="고혈당 위험", y="비만 위험 지수", color="고혈당 위험")
    fig_obesity_diabetes.update_layout(title="비만 위험 지수와 고혈당 위험의 관계", xaxis_title="고혈당 위험", yaxis_title="비만 위험 지수")
    st.plotly_chart(fig_obesity_diabetes)
    st.markdown("""
    이 박스플롯은 비만 위험 지수와 고혈당 위험 간의 관계를 보여줍니다:
    - x축은 고혈당 위험 수준을, y축은 비만 위험 지수를 나타냅니다.
    - 각 박스는 해당 고혈당 위험 수준에 속하는 사람들의 비만 위험 지수 분포를 보여줍니다.
    - 이 그래프를 통해 고혈당 위험이 높아질수록 비만 위험 지수도 높아지는 경향이 있는지 확인할 수 있습니다.
    - 이는 비만과 당뇨병 사이의 연관성을 시각적으로 보여주며, 비만 관리가 당뇨병 예방에 중요할 수 있음을 시사합니다.
    - 이러한 정보는 비만과 당뇨병 예방을 위한 통합적 접근 방식의 필요성을 강조합니다.
    """)

    # 6. 활동 수준에 따른 건강 지표 비교
    st.header("6. 활동 수준에 따른 건강 지표 비교")
    health_indicators = ['BMI', '총콜레스테롤', '식전혈당(공복혈당)', '수축기혈압(최고 혈압)']
    fig_activity_health = go.Figure()
    for indicator in health_indicators:
        fig_activity_health.add_trace(go.Box(y=df[indicator], x=df['활동 수준'], name=indicator))
    fig_activity_health.update_layout(title="활동 수준에 따른 건강 지표 비교", xaxis_title="활동 수준", yaxis_title="수치")
    st.plotly_chart(fig_activity_health)
    st.markdown("""
    이 다중 박스플롯은 활동 수준에 따른 여러 건강 지표의 분포를 비교합니다:
    - x축은 활동 수준(저활동, 중간활동, 고활동)을, y축은 각 건강 지표의 수치를 나타냅니다.
    - 각 건강 지표(BMI, 총콜레스테롤, 식전혈당, 수축기혈압)별로 별도의 박스플롯이 그려져 있습니다.
    - 이 그래프를 통해 활동 수준이 다양한 건강 지표에 미치는 영향을 한눈에 비교할 수 있습니다.
    - 예를 들어, 고활동 그룹이 다른 그룹에 비해 전반적으로 더 좋은 건강 지표를 보이는지, 또는 특정 지표에서만 차이가 나는지 확인할 수 있습니다.
    - 이러한 정보는 신체 활동의 중요성을 강조하고, 맞춤형 운동 권장 사항을 개발하는 데 활용될 수 있습니다.
    """)

