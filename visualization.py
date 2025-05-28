import streamlit as st
import pandas as pd
import plotly.express as px

# 예측 데이터 저장 파일 경로
PREDICTION_FILE = "data/predictions.csv"

def display_visualization_page():
    """📊 예측 데이터 시각화 페이지"""
    st.header("📊 예측 데이터 시각화")

    try:
        df = pd.read_csv(PREDICTION_FILE)

        # 데이터가 없는 경우 메시지 표시
        if df.empty:
            st.warning("예측 데이터가 없습니다. 먼저 예측을 실행해주세요.")
            return

        # 🔥 데이터 타입 변환 (오류 방지)
        df["나이"]             = pd.to_numeric(df["나이"], errors="coerce").fillna(0).astype(int)
        df["운동 점수"]       = pd.to_numeric(df["운동 점수"], errors="coerce").fillna(0)
        df["식단 점수"]       = pd.to_numeric(df["식단 점수"], errors="coerce").fillna(0)
        df["BMI"]             = pd.to_numeric(df["BMI"], errors="coerce").fillna(0)

        # 🔥 결측치 처리 (오류 방지)
        df.fillna(0, inplace=True)  # 모든 NaN 값을 0으로 채움

        # ✅ 성별에 따른 운동 가능성 시각화
        st.subheader("🧑‍🤝‍🧑 성별에 따른 운동 가능성")
        gender_exercise = df.groupby("성별")["운동 점수"].mean().reset_index()
        fig_gender_exercise = px.bar(gender_exercise, x="성별", y="운동 점수", color="성별",
                                    title="성별별 평균 운동 점수", labels={"운동 점수": "평균 운동 점수"})
        st.plotly_chart(fig_gender_exercise, use_container_width=True)

        # ✅ 연령대에 따른 식단 개선 필요성 시각화
        st.subheader("👵👴 연령대에 따른 식단 개선 필요성")
        age_diet = df.groupby("연령대")["식단 점수"].mean().reset_index()
        fig_age_diet = px.line(age_diet, x="연령대", y="식단 점수", title="연령대별 평균 식단 개선 필요성",
                                labels={"식단 점수": "평균 식단 개선 필요성"})
        st.plotly_chart(fig_age_diet, use_container_width=True)

        # ✅ BMI에 따른 운동 및 식단 점수 비교
        st.subheader("💪🥗 BMI에 따른 운동 및 식단 점수 비교")
        fig_bmi = px.scatter(df, x="BMI", y=["운동 점수", "식단 점수"], title="BMI별 운동 및 식단 점수",
                            labels={"value": "확률", "variable": "구분"},
                            color_continuous_scale=px.colors.sequential.Viridis)
        st.plotly_chart(fig_bmi, use_container_width=True)

        # ✅ 사용자 지정 시각화: 연령대 선택
        st.subheader("✨ 사용자 지정 시각화")

        # 1) 연령대 고유값을 숫자형으로 추출, 정렬
        age_groups = sorted(df["연령대"].dropna().astype(int).unique())

        # 2) selectbox 에서는 숫자형을 그대로 사용하되, 화면에 '20대' 등의 레이블로 보이게 format_func 사용
        selected_age = st.selectbox(
            "연령대 선택",
            age_groups,
            format_func=lambda x: f"{x}대"
        )

        # 3) 필터링
        filtered = df[df["연령대"].astype(int) == selected_age]
        if not filtered.empty:
            st.write(f"선택한 연령대({selected_age}대)의 데이터:")
            st.dataframe(filtered)
        else:
            st.info("선택한 연령대의 데이터가 없습니다.")

    except FileNotFoundError:
        st.error("🚨 예측 데이터 파일이 없습니다. 먼저 예측을 실행해주세요.")
    except Exception as e:
        st.error(f"🚨 시각화 중 오류 발생: {e}")

