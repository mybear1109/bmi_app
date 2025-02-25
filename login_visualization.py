import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def load_user_data(user_id):
    """💾 사용자 데이터를 불러오는 함수 (더미 데이터 사용)"""
    if not user_id:
        return None

    dates = [datetime.now() - timedelta(days=i * 30) for i in range(6)]
    data = {
        'date': dates,
        'weight': [75, 74, 73, 72, 71, 70],
        'BMI': [26, 25.5, 25, 24.5, 24, 23.5],
        'blood_pressure': [140, 138, 135, 132, 130, 128],
        'cholesterol': [220, 215, 210, 205, 200, 195],
        'exercise_score': [60, 65, 70, 75, 80, 85],
        'diet_score': [55, 60, 65, 70, 75, 80]
    }
    df = pd.DataFrame(data)
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')  # 날짜 형식 변환
    return df

def display_login_visualization():
    """📊 로그인한 사용자의 건강 데이터 분석 페이지"""
    if "nickname" not in st.session_state or not st.session_state.get("logged_in"):
        st.warning("⚠️ 로그인이 필요합니다. 로그인 후 다시 시도하세요.")
        return

    user_id = st.session_state["nickname"]
    st.title(f"🏋️‍♂️ {user_id}님의 건강 데이터 분석")

    # 사용자 데이터 불러오기
    user_data = load_user_data(user_id)
    if user_data is None or user_data.empty:
        st.error("❌ 사용자 데이터를 불러올 수 없습니다.")
        return

    # 체중 변화 그래프
    st.header("📉 체중 변화 추이")
    fig_weight = px.line(user_data, x='date', y='weight', markers=True, title="체중 변화")
    fig_weight.update_layout(xaxis_title="날짜", yaxis_title="체중 (kg)")
    st.plotly_chart(fig_weight)

    # BMI 변화 그래프
    st.header("📊 BMI 변화 추이")
    fig_bmi = px.line(user_data, x='date', y='BMI', markers=True, title="BMI 변화")
    fig_bmi.update_layout(xaxis_title="날짜", yaxis_title="BMI")
    fig_bmi.add_hline(y=23, line_dash="dash", line_color="green", annotation_text="정상 BMI 상한선")
    st.plotly_chart(fig_bmi)

    # 혈압과 콜레스테롤 변화
    st.header("🩺 혈압과 콜레스테롤 변화")
    fig_bp_chol = go.Figure()
    fig_bp_chol.add_trace(go.Scatter(x=user_data['date'], y=user_data['blood_pressure'], name="혈압", mode="lines+markers"))
    fig_bp_chol.add_trace(go.Scatter(x=user_data['date'], y=user_data['cholesterol'], name="콜레스테롤", mode="lines+markers"))
    fig_bp_chol.update_layout(title="혈압과 콜레스테롤 변화", xaxis_title="날짜", yaxis_title="수치")
    st.plotly_chart(fig_bp_chol)

    # 운동 점수와 식단 점수 변화
    st.header("💪 운동 점수 & 🍽️ 식단 점수 변화")
    fig_scores = go.Figure()
    fig_scores.add_trace(go.Bar(x=user_data['date'], y=user_data['exercise_score'], name="운동 점수", marker_color="blue"))
    fig_scores.add_trace(go.Bar(x=user_data['date'], y=user_data['diet_score'], name="식단 점수", marker_color="orange"))
    fig_scores.update_layout(title="운동 및 식단 점수 변화", xaxis_title="날짜", yaxis_title="점수", barmode="group")
    st.plotly_chart(fig_scores)

    # 건강 지표 요약 테이블
    st.header("📋 건강 지표 요약")
    summary = user_data.iloc[[0, -1]]  # 첫 번째와 마지막 데이터 선택
    summary = summary[['date', 'weight', 'BMI', 'blood_pressure', 'cholesterol', 'exercise_score', 'diet_score']]
    summary.columns = ['날짜', '체중 (kg)', 'BMI', '혈압', '콜레스테롤', '운동 점수', '식단 점수']
    st.table(summary)

    # 최종 분석 요약
    st.markdown("""
    **📌 분석 요약**
    - 체중이 점진적으로 감소하고 있습니다. 목표 체중까지 지속적으로 노력하세요! 🎯
    - BMI 값이 정상 범위(23)에 가까워지고 있습니다. 꾸준한 관리가 필요합니다. 🏆
    - 혈압과 콜레스테롤 수치가 안정적으로 개선되고 있습니다. 👍
    - 운동과 식단 점수가 꾸준히 상승하는 것은 좋은 신호입니다. 계속 유지하세요! 💪🔥
    """)

