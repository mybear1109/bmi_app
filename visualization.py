import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

PREDICTION_FILE = "data/predictions.csv"

def display_visualization_page():
    st.header("📊 건강 데이터 종합 분석")

    try:
        df = pd.read_csv(PREDICTION_FILE)
        if df.empty:
            st.warning("예측 데이터가 없습니다. 먼저 예측을 실행해주세요.")
            return

        # 데이터 전처리
        numeric_columns = ['연령대', '허리둘레', "현재 체중", "목표 체중", '수축기혈압(최고 혈압)', '이완기혈압(최저 혈압)', 
                           '식전혈당(공복혈당)', 'HDL콜레스테롤', 'LDL콜레스테롤', '트리글리세라이드', 
                           'BMI', '혈압 차이', '간 지표', '고혈당 위험', '비만 위험 지수']
        
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df['BMI_등급'] = pd.cut(df['BMI'], bins=[0, 18.5, 25, 30, 100], labels=['저체중', '정상', '과체중', '비만'])
        df['체중_차이'] = df['현재 체중'] - df['목표 체중']

        # 1. BMI 분포 및 체중 목표 분석
        st.subheader("1. BMI 분포 및 체중 목표 분석")
        fig_bmi_weight = make_subplots(rows=1, cols=2, subplot_titles=("BMI 분포", "현재 체중 vs 목표 체중"))
        
        fig_bmi_weight.add_trace(go.Histogram(x=df['BMI'], name="BMI 분포"), row=1, col=1)
        fig_bmi_weight.add_trace(go.Scatter(x=df['현재 체중'], y=df['목표 체중'], mode='markers', 
                                            name="체중 목표", marker=dict(color=df['체중_차이'], colorscale='RdYlGn_r')), row=1, col=2)
        
        fig_bmi_weight.update_layout(height=500, title_text="BMI 분포 및 체중 목표 분석")
        st.plotly_chart(fig_bmi_weight, use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)  # 간격 추가
        st.markdown("""
        이 차트는 BMI 분포와 현재 체중 대비 목표 체중의 관계를 보여줍니다:
        - 왼쪽 그래프는 BMI의 분포를 히스토그램으로 나타냅니다.
        - 오른쪽 그래프는 현재 체중과 목표 체중의 관계를 산점도로 보여줍니다. 점의 색상은 체중 감량 목표를 나타냅니다.
        - 이를 통해 전반적인 BMI 분포와 체중 감량 목표의 경향을 파악할 수 있습니다.
        """)
        st.markdown("<br>", unsafe_allow_html=True)  # 간격 추가
        st.markdown("---")  # 구분선 추가

        # 2. 건강 지표 상관관계
        st.subheader("2. 건강 지표 상관관계")
        health_indicators = ['BMI', '허리둘레', '현재 체중', '수축기혈압(최고 혈압)', '이완기혈압(최저 혈압)', 
                             'HDL콜레스테롤', 'LDL콜레스테롤', '트리글리세라이드']
        corr_matrix = df[health_indicators].corr()
        fig_corr = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                             title="건강 지표 간 상관관계 히트맵")
        st.plotly_chart(fig_corr, use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)  # 간격 추가
        st.markdown("""
        이 히트맵은 주요 건강 지표들 간의 상관관계를 보여줍니다:
        - 색상이 진할수록 강한 상관관계를 나타냅니다. 붉은색은 양의 상관관계, 파란색은 음의 상관관계를 의미합니다.
        - BMI와 허리둘레, 현재 체중 간의 강한 양의 상관관계를 확인할 수 있습니다.
        - 수축기혈압과 이완기혈압 사이에도 강한 양의 상관관계가 있습니다.
        - HDL콜레스테롤(좋은 콜레스테롤)은 다른 지표들과 대체로 음의 상관관계를 보입니다.
        """)
        st.markdown("<br>", unsafe_allow_html=True)  # 간격 추가
        st.markdown("---")  # 구분선 추가
        
        # 3. 연령대별 건강 지표 추이
        st.subheader("3. 연령대별 건강 지표 추이")
        age_health = df.groupby('연령대')[['BMI', '허리둘레', '현재 체중', '수축기혈압(최고 혈압)', '식전혈당(공복혈당)']].mean().reset_index()
        fig_age_health = px.line(age_health, x='연령대', y=['BMI', '허리둘레', '현재 체중', '수축기혈압(최고 혈압)', '식전혈당(공복혈당)'],
                                 title="연령대별 주요 건강 지표 변화")
        st.plotly_chart(fig_age_health, use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)  # 간격 추가
        st.markdown("""
        이 선 그래프는 연령대에 따른 주요 건강 지표의 변화를 보여줍니다:
        - X축은 연령대를, Y축은 각 건강 지표의 평균값을 나타냅니다.
        - 대부분의 지표가 연령이 증가함에 따라 상승하는 경향을 보입니다.
        - 특히 수축기혈압과 식전혈당이 연령 증가에 따라 뚜렷한 상승세를 보입니다.
        - BMI와 허리둘레는 중년기까지 증가하다가 고령기에 약간 감소하는 경향을 보입니다.
        """)
        st.markdown("<br>", unsafe_allow_html=True)  # 간격 추가
        st.markdown("---")  # 구분선 추가
        
        # 4. 생활 습관과 건강 위험도
        st.subheader("4. 생활 습관과 건강 위험도")
        habit_risk = df.groupby(['흡연상태', '음주여부'])[['비만 위험 지수', '고혈당 위험', 'BMI']].mean().reset_index()
        fig_habit = px.scatter_3d(habit_risk, x='흡연상태', y='음주여부', z='BMI',
                                  size='비만 위험 지수', color='고혈당 위험',
                                  title="생활 습관에 따른 3D 건강 위험도 분석")
        st.plotly_chart(fig_habit, use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)  # 간격 추가
        st.markdown("""
        이 3D 산점도는 생활 습관(흡연, 음주)과 건강 위험도의 관계를 보여줍니다:
        - X축은 흡연 상태, Y축은 음주 여부, Z축은 BMI를 나타냅니다.
        - 점의 크기는 비만 위험 지수를, 색상은 고혈당 위험을 나타냅니다.
        - 이 그래프를 통해 흡연과 음주 습관이 BMI, 비만 위험, 고혈당 위험과 어떤 관계가 있는지 파악할 수 있습니다.
        - 일반적으로 흡연자와 음주자가 비흡연자와 비음주자에 비해 건강 위험도가 높은 경향을 볼 수 있습니다.
        """)
        st.markdown("<br>", unsafe_allow_html=True)  # 간격 추가
        st.markdown("---")  # 구분선 추가
        
        # 5. 체중 감량 목표 분석
        st.subheader("5. 체중 감량 목표 분석")
        df['체중감량목표'] = df['현재 체중'] - df['목표 체중']
        df['허리둘레'] = df['허리둘레'].fillna(df['허리둘레'].mean())  # NaN 값을 평균으로 대체

        fig_weight_loss = px.scatter(df, x='BMI', y='체중감량목표', color='연령대', size='허리둘레',
                             hover_data=['현재 체중', '목표 체중'],
                             title="BMI와 체중 감량 목표의 관계")
        # 마커 크기 조정
        fig_weight_loss = px.scatter(df, x='BMI', y='체중감량목표', color='연령대', 
                             size='허리둘레',  # 허리둘레에 따라 마커 크기 변경
                             size_max=30,  # 최대 마커 크기 설정
                             hover_data=['현재 체중', '목표 체중'],
                             title="BMI와 체중 감량 목표의 관계")

        st.plotly_chart(fig_weight_loss, use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)  # 간격 추가
        st.markdown("""
        이 차트는 BMI와 체중 감량 목표 사이의 관계를 보여줍니다:
        - X축은 BMI를, Y축은 체중 감량 목표(현재 체중 - 목표 체중)를 나타냅니다.
        - 점의 색상은 연령대를 구분하며, 허리둘레' 값에 따라 마커(동그라미 점) 크기가 달라집니다.
        - 이 차트를 통해 BMI가 높을수록 체중 감량 목표가 큰 경향을 볼 수 있으며, 연령대별로 어떤 차이가 있는지 파악할 수 있습니다.
        """)
        st.markdown("<br>", unsafe_allow_html=True)  # 간격 추가
        st.markdown("---")  # 구분선 추가
        


        # 6. 사용자 맞춤 건강 위험도 계산기
        st.subheader("6. 🔬 맞춤형 건강 위험도 계산기")
        st.markdown("<br>", unsafe_allow_html=True)  # 간격 추가
        st.markdown("""
            이 건강 위험도 계산기는 사용자의 개인 건강 정보를 바탕으로 전반적인 건강 위험도를 평가합니다:
            - 입력한 BMI, 허리둘레, 혈압, 혈당, 체중 정보를 종합하여 위험도를 계산합니다.
            - 게이지 차트는 계산된 위험도를 시각적으로 표현합니다.
            - 녹색 영역(0-80%)은 양호한 상태, 노란색 영역(80-100%)은 주의가 필요한 상태, 빨간색 영역(100% 이상)은 건강 관리가 시급한 상태를 나타냅니다.
            - 이 도구를 통해 사용자는 자신의 현재 건강 상태를 대략적으로 파악하고, 개선이 필요한 영역을 식별할 수 있습니다.
            """)
        st.markdown("<br>", unsafe_allow_html=True)  # 간격 추가
        col1, col2, col3 = st.columns(3)
        with col1:
            user_bmi = st.number_input("BMI 입력", min_value=10.0, max_value=50.0, value=25.0, step=0.1)
            user_waist = st.number_input("허리둘레 입력 (cm)", min_value=50, max_value=200, value=80)
        with col2:
            user_systolic = st.number_input("수축기 혈압(최고 혈압) 입력 (mmHg)", min_value=80, max_value=200, value=120)
            user_glucose = st.number_input("공복혈당(식전혈당) 입력 (mg/dL)", min_value=50, max_value=300, value=100)
        with col3:
            user_weight = st.number_input("현재 체중 (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.1)
            user_target_weight = st.number_input("목표 체중 (kg)", min_value=30.0, max_value=200.0, value=65.0, step=0.1)

        if st.button("건강 위험도 계산"):
            risk_score = (user_bmi / 25 + user_waist / 80 + user_systolic / 120 + user_glucose / 100 + (user_weight / user_target_weight)) / 5 * 100
            st.markdown(f"### 당신의 건강 위험도: {risk_score:.2f}%")
            
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = risk_score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "건강 위험도"},
                gauge = {
                    'axis': {'range': [None, 150]},
                    'steps': [
                        {'range': [0, 80], 'color': "lightgreen"},
                        {'range': [80, 100], 'color': "yellow"},
                        {'range': [100, 150], 'color': "red"}],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': risk_score}}))
            st.plotly_chart(fig_gauge, use_container_width=True)

            if risk_score < 80:
                st.success("양호한 상태입니다. 현재의 건강 관리를 유지하세요!")
            elif risk_score < 100:
                st.warning("주의가 필요합니다. 식습관과 운동 습관을 개선해보세요.")
            else:
                st.error("건강 관리가 시급합니다. 전문의와 상담을 권장합니다.")

    except FileNotFoundError:
        st.error("🚨 예측 데이터 파일이 없습니다. 먼저 예측을 실행해주세요.")
    except Exception as e:
        st.error(f"🚨 시각화 중 오류 발생: {e}")
