# login_visualization.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def load_user_data(user_id):
    # 실제 구현에서는 데이터베이스에서 사용자 데이터를 불러오는 로직이 필요합니다.
    # 여기서는 예시로 더미 데이터를 생성합니다.
    dates = [datetime.now() - timedelta(days=i*30) for i in range(6)]
    data = {
        'date': dates,
        'weight': [75, 74, 73, 72, 71, 70],
        'BMI': [26, 25.5, 25, 24.5, 24, 23.5],
        'blood_pressure': [140, 138, 135, 132, 130, 128],
        'cholesterol': [220, 215, 210, 205, 200, 195],
        'exercise_score': [60, 65, 70, 75, 80, 85],
        'diet_score': [55, 60, 65, 70, 75, 80]
    }
    return pd.DataFrame(data)

def display_login_visualization(user_id):
    st.title(f"🏋️‍♀️ {user_id}님의 건강 데이터 분석")
    
    user_data = load_user_data(user_id)
    
    # 1. 체중 변화 그래프
    st.header("1. 체중 변화 추이")
    fig_weight = px.line(user_data, x='date', y='weight', markers=True)
    fig_weight.update_layout(title="체중 변화", xaxis_title="날짜", yaxis_title="체중 (kg)")
    st.plotly_chart(fig_weight)
    st.markdown("""
    이 선 그래프는 귀하의 체중 변화 추이를 보여줍니다:
    - x축은 날짜를, y축은 체중(kg)을 나타냅니다.
    - 그래프의 기울기를 통해 체중 감량 속도를 파악할 수 있습니다.
    - 목표 체중에 얼마나 근접했는지, 체중 감량이 일정하게 진행되고 있는지 확인할 수 있습니다.
    """)

    # 2. BMI 변화 그래프
    st.header("2. BMI 변화 추이")
    fig_bmi = px.line(user_data, x='date', y='BMI', markers=True)
    fig_bmi.update_layout(title="BMI 변화", xaxis_title="날짜", yaxis_title="BMI")
    fig_bmi.add_hline(y=23, line_dash="dash", line_color="green", annotation_text="정상 BMI 상한선")
    st.plotly_chart(fig_bmi)
    st.markdown("""
    이 그래프는 귀하의 BMI 변화를 보여줍니다:
    - x축은 날짜를, y축은 BMI 값을 나타냅니다.
    - 녹색 점선은 정상 BMI의 상한선(23)을 나타냅니다.
    - BMI가 정상 범위에 도달했는지, 또는 얼마나 가까워지고 있는지 확인할 수 있습니다.
    """)

    # 3. 혈압과 콜레스테롤 변화 그래프
    st.header("3. 혈압과 콜레스테롤 변화")
    fig_bp_chol = go.Figure()
    fig_bp_chol.add_trace(go.Scatter(x=user_data['date'], y=user_data['blood_pressure'], name="혈압"))
    fig_bp_chol.add_trace(go.Scatter(x=user_data['date'], y=user_data['cholesterol'], name="콜레스테롤"))
    fig_bp_chol.update_layout(title="혈압과 콜레스테롤 변화", xaxis_title="날짜", yaxis_title="수치")
    st.plotly_chart(fig_bp_chol)
    st.markdown("""
    이 그래프는 혈압과 콜레스테롤 수치의 변화를 함께 보여줍니다:
    - x축은 날짜를, y축은 각각의 수치를 나타냅니다.
    - 두 지표의 변화 추이를 비교하여 전반적인 심혈관 건강 상태를 파악할 수 있습니다.
    - 운동과 식단 개선이 이 두 지표에 미치는 영향을 확인할 수 있습니다.
    """)

    # 4. 운동 점수와 식단 점수 변화 그래프
    st.header("4. 운동 점수와 식단 점수 변화")
    fig_scores = go.Figure()
    fig_scores.add_trace(go.Bar(x=user_data['date'], y=user_data['exercise_score'], name="운동 점수"))
    fig_scores.add_trace(go.Bar(x=user_data['date'], y=user_data['diet_score'], name="식단 점수"))
    fig_scores.update_layout(title="운동 점수와 식단 점수 변화", xaxis_title="날짜", yaxis_title="점수", barmode='group')
    st.plotly_chart(fig_scores)
    st.markdown("""
    이 그래프는 운동 점수와 식단 점수의 변화를 보여줍니다:
    - x축은 날짜를, y축은 각 점수를 나타냅니다.
    - 두 점수의 변화 추이를 비교하여 생활 습관 개선의 균형을 확인할 수 있습니다.
    - 점수가 지속적으로 상승하고 있는지, 어느 영역에 더 집중해야 하는지 파악할 수 있습니다.
    """)

    # 5. 건강 지표 요약 테이블
    st.header("5. 건강 지표 요약")
    summary = user_data.iloc[[0, -1]]  # 첫 번째와 마지막 데이터 선택
    summary = summary[['date', 'weight', 'BMI', 'blood_pressure', 'cholesterol', 'exercise_score', 'diet_score']]
    summary.columns = ['날짜', '체중', 'BMI', '혈압', '콜레스테롤', '운동 점수', '식단 점수']
    summary['날짜'] = summary['날짜'].dt.strftime('%Y-%m-%d')
    st.table(summary)
    st.markdown("""
    이 테이블은 귀하의 건강 지표 변화를 요약하여 보여줍니다:
    - 첫 번째 행은 초기 측정값을, 두 번째 행은 최근 측정값을 나타냅니다.
    - 각 지표의 개선 정도를 한눈에 파악할 수 있습니다.
    - 이를 통해 어느 영역에서 가장 큰 진전이 있었는지, 또는 더 관심을 기울여야 할 영역이 무엇인지 확인할 수 있습니다.
    """)

