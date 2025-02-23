import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt


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

# 추가 전처리
df['연령대'] = df['연령대'].astype('category')
df['BMI'] = pd.to_numeric(df['BMI'], errors='coerce')
df = df.dropna(subset=['BMI', '연령대'])

def display_visualization_page():
    st.title("🏥 건강 데이터 분석 대시보드")
    st.markdown("<br>", unsafe_allow_html=True)

def display_visualization_page():
    st.title("🏥 건강 데이터 분석 대시보드")
    st.markdown("<br>", unsafe_allow_html=True)

    # 1. BMI 분포와 연령대별 비교 (2D 히스토그램)
    st.header("📊 BMI 분포와 연령대별 비교")
    try:
        fig_bmi_age = go.Figure(go.Histogram2d(
                        x=df["BMI"],
                        y=df["연령대"],
                        colorscale="Deep",
                    ))
        fig_bmi_age.update_xaxes(title="BMI (체질량지수)")
        fig_bmi_age.update_yaxes(title="연령대")
        fig_bmi_age.update_layout(coloraxis_colorbar=dict(title="빈도"))
        st.plotly_chart(fig_bmi_age, use_container_width=True)
    except Exception as e:
        st.error(f"BMI 분포와 연령대별 비교 차트 생성 중 오류 발생: {e}")
    
    st.markdown("""
    이 2D 히스토그램은 BMI와 연령대의 관계를 보여줍니다:
    - x축: BMI 값을 나타냅니다. 일반적으로 18.5-24.9가 정상 범위입니다.
    - y축: 연령대를 나타냅니다.
    - 색상 강도: 각 BMI와 연령대 조합의 빈도를 나타냅니다. 진할수록 빈도가 높습니다.
    - 이를 통해 연령대별 BMI 분포의 차이를 파악할 수 있습니다.
    """)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")


    # 2. 성별과 흡연 상태에 따른 BMI 분포 (바이올린 플롯)
    st.header("🚬 성별과 흡연 상태에 따른 BMI 분포")
    try:
        fig_gender_smoking = px.violin(df, x="성별", y="BMI", color="흡연상태", box=True, points="all",
                                       title="성별과 흡연 상태에 따른 BMI 분포",
                                       labels={"BMI": "체질량지수 (BMI)", "성별": "성별", "흡연상태": "흡연 상태"},
                                       category_orders={"흡연상태": ["비흡연", "과거 흡연", "현재 흡연"]})
        st.plotly_chart(fig_gender_smoking, use_container_width=True)
    except Exception as e:
        st.error(f"성별과 흡연 상태에 따른 BMI 분포 차트 생성 중 오류 발생: {e}")
    
    st.markdown("""
    이 바이올린 플롯은 성별과 흡연 상태에 따른 BMI 분포를 보여줍니다:
    - x축: 성별을 나타냅니다 (남성, 여성).
    - y축: BMI 값을 나타냅니다. 
    - 색상: 흡연 상태를 나타냅니다 (비흡연, 과거 흡연, 현재 흡연).
    - 바이올린 모양: BMI의 분포를 나타냅니다. 넓을수록 해당 BMI 값의 빈도가 높습니다.
    - 이를 통해 성별과 흡연 여부에 따른 BMI 분포의 차이를 파악할 수 있습니다.
    """)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # 3. 활동 수준과 콜레스테롤의 관계 (산점도)
    st.header("❤️ 활동 수준과 콜레스테롤의 관계")
    try:
        fig_activity_cholesterol = px.scatter(df, x="활동 수준", y="콜레스테롤", color="연령대", size="BMI",
                                              hover_data=["성별", "흡연상태"],
                                              title="활동 수준과 콜레스테롤의 관계",
                                              labels={"활동 수준": "활동 수준", "콜레스테롤": "총 콜레스테롤 (mg/dL)"},
                                              category_orders={"활동 수준": ["낮음", "보통", "높음"]})
        fig_activity_cholesterol.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
        st.plotly_chart(fig_activity_cholesterol, use_container_width=True)
    except Exception as e:
        st.error(f"활동 수준과 콜레스테롤의 관계 차트 생성 중 오류 발생: {e}")
    
    st.markdown("""
    이 산점도는 활동 수준과 콜레스테롤의 관계를 보여줍니다:
    - x축: 활동 수준을 나타냅니다 (낮음, 보통, 높음).
    - y축: 총 콜레스테롤 수치를 나타냅니다. 200mg/dL 이하가 바람직한 수준입니다.
    - 점 크기: BMI 값을 나타냅니다. 크기가 클수록 BMI가 높습니다.
    - 색상: 연령대를 나타냅니다.
    - 이를 통해 활동 수준, 콜레스테롤, BMI, 연령대 간의 관계를 파악할 수 있습니다.
    """)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # 4. 고혈당 위험과 BMI의 관계 (히트맵)
    st.header("🩸 고혈당 위험과 BMI의 관계")
    try:
        df['BMI_범주'] = pd.cut(df['BMI'], bins=[0, 18.5, 25, 30, 100], labels=['저체중', '정상', '과체중', '비만'])
        heatmap_data = df.groupby(['고혈당 위험', 'BMI_범주']).size().unstack(fill_value=0, observed=False)
        fig_glucose_bmi = px.imshow(heatmap_data, x=heatmap_data.columns, y=heatmap_data.index,
                                    color_continuous_scale="YlOrRd",
                                    labels=dict(x="BMI 범주", y="고혈당 위험", color="빈도"),
                                    title="고혈당 위험과 BMI의 관계")
        fig_glucose_bmi.update_xaxes(side="top")
        st.plotly_chart(fig_glucose_bmi, use_container_width=True)
    except Exception as e:
        st.error(f"고혈당 위험과 BMI의 관계 차트 생성 중 오류 발생: {e}")
    
    st.markdown("""
    이 히트맵은 고혈당 위험과 BMI의 관계를 보여줍니다:
    - x축: BMI 범주를 나타냅니다 (저체중, 정상, 과체중, 비만).
    - y축: 고혈당 위험 수준을 나타냅니다.
    - 색상 강도: 각 조합의 빈도를 나타냅니다. 진할수록 빈도가 높습니다.
    - 이를 통해 BMI 범주와 고혈당 위험 간의 관계를 파악할 수 있습니다.
    """)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # 5. 음주 여부와 간 지표의 관계 (그룹화된 막대 차트)
    st.header("🍺 음주 여부와 간 지표의 관계")
    try:
        fig_drinking_liver = px.histogram(df, x="간 지표", color="음주여부", barmode="group",
                                          title="음주 여부와 간 지표의 관계",
                                          labels={"간 지표": "간 지표", "음주여부": "음주 여부", "count": "빈도"},
                                          category_orders={"간 지표": ["정상", "경계", "위험"]})
        fig_drinking_liver.update_layout(legend_title_text='음주 여부')
        st.plotly_chart(fig_drinking_liver, use_container_width=True)
    except Exception as e:
        st.error(f"음주 여부와 간 지표의 관계 차트 생성 중 오류 발생: {e}")
    
    st.markdown("""
    이 그룹화된 막대 차트는 음주 여부와 간 지표의 관계를 보여줍니다:
    - x축: 간 지표를 나타냅니다. 정상, 경계, 위험으로 구분됩니다.
    - y축: 각 그룹의 빈도를 나타냅니다. 높을수록 해당 조합의 사람이 많다는 의미입니다.
    - 색상: 음주 여부를 나타냅니다. 비음주, 가끔, 자주로 구분됩니다.
    - 이를 통해 음주 습관에 따른 간 건강 상태의 차이를 파악할 수 있습니다.
    """)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # 6. 혈압 차이와 혈당 수치의 관계 (산점도)
    st.header("🩸 혈압 차이와 혈당 수치의 관계")
    try:
        fig_bp_glucose = px.scatter(df, x="혈압 차이", y="식전혈당(공복혈당)", 
                                    color="연령대", size="BMI",
                                    hover_data=["성별", "고혈당 위험"],
                                    labels={"혈압 차이": "혈압 차이 (mmHg)", 
                                            "식전혈당(공복혈당)": "식전혈당 (mg/dL)",
                                            "BMI": "체질량지수"},
                                    title="혈압 차이와 식전혈당의 관계")
        
        fig_bp_glucose.update_layout(
            xaxis_title="혈압 차이 (수축기 - 이완기) (mmHg)",
            yaxis_title="식전혈당 (mg/dL)"
        )
        
        fig_bp_glucose.add_shape(
            type="line", line=dict(dash="dash"),
            x0=40, x1=60, y0=0, y1=200,  # 정상 혈압 차이 범위
            line_color="#088A08"
        )
        fig_bp_glucose.add_shape(
            type="line", line=dict(dash="dash"),
            x0=0, x1=200, y0=100, y1=100,  # 정상 혈당 기준선
            line_color="#DF0101"
        )
        
        st.plotly_chart(fig_bp_glucose, use_container_width=True)
    except Exception as e:
        st.error(f"혈압 차이와 혈당 수치의 관계 차트 생성 중 오류 발생: {e}")

    st.markdown("""
    이 산점도는 혈압 차이와 식전혈당 수치의 관계를 보여줍니다:
    - x축: 혈압 차이 (수축기 혈압 - 이완기 혈압)를 나타냅니다. 일반적으로 40-60 mmHg가 정상 범위입니다 (녹색 점선).
    - y축: 식전혈당 수치를 나타냅니다. 100 mg/dL 이하가 정상 범위입니다 (빨간색 점선).
    - 점 크기: BMI 값을 나타냅니다. 크기가 클수록 BMI가 높습니다.
    - 색상: 연령대를 나타냅니다.
    - 이 차트를 통해 혈압 차이, 혈당 수치, BMI, 연령대 간의 관계를 파악할 수 있습니다.
    - 우측 상단에 위치한 데이터 포인트들은 혈압 차이가 크고 혈당 수치가 높은, 잠재적 위험군을 나타냅니다.
    """)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")


