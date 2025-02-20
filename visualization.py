import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

PREDICTION_FILE = "data/predictions.csv"

def display_visualization_page():
    st.header("📊 건강 데이터 종합 분석")

    try:
        df = pd.read_csv(PREDICTION_FILE)
        if df.empty:
            st.warning("예측 데이터가 없습니다. 먼저 예측을 실행해주세요.")
            return

        # 데이터 전처리
        numeric_columns = ['연령대', '허리둘레', '수축기혈압(최고 혈압)', '이완기혈압(최저 혈압)', '식전혈당(공복혈당)',
                           'HDL콜레스테롤', 'LDL콜레스테롤', '트리글리세라이드', '혈청지오티(AST)',
                           '혈청지피티(ALT)', '감마지티피', 'BMI', '혈압 차이', '간 지표', '고혈당 위험', '비만 위험 지수']
        
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df['BMI_등급'] = pd.cut(df['BMI'], bins=[0, 18.5, 25, 30, 100], labels=['저체중', '정상', '과체중', '비만'])

        # 1. BMI 분포 및 건강 지표 상관관계
        st.subheader("1. BMI 분포 및 건강 지표 상관관계")
        fig_bmi = px.histogram(df, x="BMI", color="BMI_등급", marginal="box", 
                               title="BMI 분포 및 등급별 분류")
        st.plotly_chart(fig_bmi, use_container_width=True)

        health_indicators = ['BMI', '허리둘레', '수축기혈압(최고 혈압)', '이완기혈압(최저 혈압)', 
                             'HDL콜레스테롤', 'LDL콜레스테롤', '트리글리세라이드']
        corr_matrix = df[health_indicators].corr()
        fig_corr = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                             title="건강 지표 간 상관관계 히트맵")
        st.plotly_chart(fig_corr, use_container_width=True)

        # 2. 연령대별 건강 지표 추이
        st.subheader("2. 연령대별 건강 지표 추이")
        age_health = df.groupby('연령대')[['BMI', '허리둘레', '수축기혈압(최고 혈압)', '식전혈당(공복혈당)']].mean().reset_index()
        fig_age_health = px.line(age_health, x='연령대', y=['BMI', '허리둘레', '수축기혈압(최고 혈압)', '식전혈당(공복혈당)'],
                                 title="연령대별 주요 건강 지표 변화")
        st.plotly_chart(fig_age_health, use_container_width=True)

        # 3. 생활 습관과 건강 위험도
        st.subheader("3. 생활 습관과 건강 위험도")
        habit_risk = df.groupby(['흡연상태', '음주여부'])[['비만 위험 지수', '고혈당 위험']].mean().reset_index()
        fig_habit = px.bar(habit_risk, x='흡연상태', y=['비만 위험 지수', '고혈당 위험'], 
                           color='음주여부', barmode='group',
                           title="흡연 및 음주 습관에 따른 건강 위험도")
        st.plotly_chart(fig_habit, use_container_width=True)

        # 4. 콜레스테롤 프로필 분석
        st.subheader("4. 콜레스테롤 프로필 분석")
        chol_profile = df[['HDL콜레스테롤', 'LDL콜레스테롤', '트리글리세라이드']].mean()
        fig_chol = go.Figure(data=[go.Pie(labels=chol_profile.index, values=chol_profile.values, hole=.3)])
        fig_chol.update_layout(title_text="평균 콜레스테롤 구성 비율")
        st.plotly_chart(fig_chol, use_container_width=True)

        # 5. 사용자 맞춤 건강 위험도 계산기
        st.subheader("5. 🔬 맞춤형 건강 위험도 계산기")
        col1, col2 = st.columns(2)
        with col1:
            user_bmi = st.number_input("BMI 입력", min_value=10.0, max_value=50.0, value=25.0, step=0.1)
            user_waist = st.number_input("허리둘레 입력 (cm)", min_value=50, max_value=200, value=80)
        with col2:
            user_systolic = st.number_input("수축기 혈압 입력 (mmHg)", min_value=80, max_value=200, value=120)
            user_glucose = st.number_input("공복혈당 입력 (mg/dL)", min_value=50, max_value=300, value=100)

        if st.button("건강 위험도 계산"):
            risk_score = (user_bmi / 25 + user_waist / 80 + user_systolic / 120 + user_glucose / 100) / 4 * 100
            st.markdown(f"### 당신의 건강 위험도: {risk_score:.2f}%")
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
