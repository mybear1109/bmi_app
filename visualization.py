import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

        # 데이터 타입 변환 & 결측치 처리
        df["나이"] = pd.to_numeric(df["나이"], errors="coerce").fillna(0).astype(int)
        df["운동 점수"] = pd.to_numeric(df["운동 점수"], errors="coerce").fillna(0)
        df["식단 점수"] = pd.to_numeric(df["식단 점수"], errors="coerce").fillna(0)
        df["BMI"] = pd.to_numeric(df["BMI"], errors="coerce").fillna(0)
        df.fillna(0, inplace=True)

        # 1) 성별별 평균 운동 점수 (Bar)
        st.subheader("🧑‍🤝‍🧑 성별에 따른 운동 가능성")
        gender_ex = df.groupby("성별")["운동 점수"].mean().reset_index()
        fig1 = px.bar(
            gender_ex,
            x="성별",
            y="운동 점수",
            color="성별",
            title="성별별 평균 운동 점수",
            labels={"운동 점수": "평균 운동 점수"}
        )
        st.plotly_chart(fig1, use_container_width=True)

        # 2) 연령대별 평균 식단 점수 (Line)
        st.subheader("👵👴 연령대에 따른 식단 개선 필요성")
        age_diet = df.groupby("연령대")["식단 점수"].mean().reset_index()
        # 연령대 순 정렬
        import re
        age_diet["order"] = age_diet["연령대"].apply(lambda x: int(re.search(r"(\d+)", x).group()))
        age_diet = age_diet.sort_values("order")
        fig2 = px.line(
            age_diet,
            x="연령대",
            y="식단 점수",
            title="연령대별 평균 식단 점수",
            markers=True,
            labels={"식단 점수": "평균 식단 점수"}
        )
        st.plotly_chart(fig2, use_container_width=True)

        # 3) BMI별 운동 & 식단 점수 비교 (Scatter)
        st.subheader("💪🥗 BMI에 따른 운동 및 식단 점수 비교")
        fig3 = px.scatter(
            df,
            x="BMI",
            y=["운동 점수", "식단 점수"],
            title="BMI별 운동/식단 점수",
            labels={"value": "점수", "variable": "구분"}
        )
        st.plotly_chart(fig3, use_container_width=True)

        # 4) 운동 점수 분포 (Histogram)
        st.subheader("🏃‍♂️ 운동 점수 분포")
        fig4 = px.histogram(
            df,
            x="운동 점수",
            nbins=10,
            title="운동 점수 분포",
            labels={"운동 점수": "운동 점수", "count": "빈도"}
        )
        st.plotly_chart(fig4, use_container_width=True)

        # 5) 식단 점수 분포 (Histogram)
        st.subheader("🍏 식단 점수 분포")
        fig5 = px.histogram(
            df,
            x="식단 점수",
            nbins=10,
            title="식단 점수 분포",
            labels={"식단 점수": "식단 점수", "count": "빈도"}
        )
        st.plotly_chart(fig5, use_container_width=True)

        # 추가 설명 마크다운
        st.markdown(
            """
            **시각화 요약**
            - **성별별 평균 운동 점수**: 남녀 간 운동 참여 수준 차이를 확인합니다.
            - **연령대별 평균 식단 점수**: 연령대별로 식단 개선 필요성을 파악합니다.
            - **BMI별 운동/식단 점수 비교**: 체질량지수에 따른 건강 지표 상관관계를 분석합니다.
            - **운동 점수 분포**: 전체 사용자 운동 점수의 퍼짐 정도를 보여줍니다.
            - **식단 점수 분포**: 전체 사용자 식단 점수 분포를 확인합니다.
            """
        )

        # 사용자 지정 시각화: 연령대 선택 (Selectbox)
        st.subheader("✨ 사용자 지정 시각화: 연령대별 데이터 보기")
        unique_ages = df["연령대"].dropna().unique().tolist()
        unique_ages.sort(key=lambda x: int(re.search(r"(\d+)", x).group()))
        selected_age = st.selectbox("연령대 선택", unique_ages)
        filtered = df[df["연령대"] == selected_age]
        if not filtered.empty:
            st.write(f"### 선택한 연령대: {selected_age}")
            st.dataframe(filtered)
        else:
            st.info("선택한 연령대의 데이터가 없습니다.")

    except FileNotFoundError:
        st.error("🚨 예측 데이터 파일이 없습니다. 먼저 예측을 실행해주세요.")
    except Exception as e:
        st.error(f"🚨 시각화 중 오류 발생: {e}")