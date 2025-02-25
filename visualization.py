import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# 데이터 파일 경로 설정 및 로드
uploaded_file = "data/predictions.csv"
df = pd.read_csv(uploaded_file)

# 데이터 전처리
numeric_columns = ['나이', '키', '현재 체중', '목표 체중', 'BMI', '허리둘레',
                   '수축기혈압(최고 혈압)', '이완기혈압(최저 혈압)', '혈압 차이', '총콜레스테롤', 'HDL콜레스테롤',
                   'LDL콜레스테롤', '트리글리세라이드', '식전혈당(공복혈당)', '운동 개선 필요성', '운동 점수', 
                   '식단 개선 필요성', '식단 점수', '비만 위험 지수']

df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

categorical_columns = ['성별', '연령대', '흡연상태', '음주여부', '고혈당 위험', '간 지표', '활동 수준']
for col in categorical_columns:
    df[col] = df[col].fillna('미상')

df['연령대'] = df['연령대'].astype('category')
df['BMI'] = pd.to_numeric(df['BMI'], errors='coerce')
df = df.dropna(subset=['BMI', '연령대'])

def display_visualization_page():
    st.title("🏥 건강 데이터 분석 대시보드")
    st.markdown("<br>", unsafe_allow_html=True)

    # 1. BMI 분포와 연령대별 비교 (히트맵)
    st.header("📊 BMI 분포와 연령대별 비교")
    fig_bmi_age = px.density_heatmap(df, x="BMI", y="연령대", 
                                     color_continuous_scale="Viridis",
                                     nbinsx=20, nbinsy=10)
    fig_bmi_age.update_layout(title="BMI와 연령대의 분포",
                              xaxis_title="BMI (체질량지수)",
                              yaxis_title="연령대")
    st.plotly_chart(fig_bmi_age, use_container_width=True)

    st.markdown("""
    이 히트맵은 BMI와 연령대의 관계를 시각화합니다:
    - x축은 BMI 값을 나타내며, 일반적으로 18.5-23.9가 정상 범위로 간주됩니다.
    - y축은 연령대를 보여줍니다.
    - 색상의 강도는 각 BMI와 연령대 조합의 빈도를 나타냅니다. 진한 색상일수록 해당 조합의 빈도가 높습니다.
    - 이 차트를 통해 연령대별 BMI 분포의 차이를 쉽게 파악할 수 있습니다. 예를 들어, 특정 연령대에서 BMI가 높게 나타나는 경향이 있는지 확인할 수 있습니다.
    - 또한, 전체적인 BMI 분포 패턴을 관찰하여 비만이나 저체중의 연령대별 경향성을 분석할 수 있습니다.
    """)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # 2. 성별과 흡연 상태에 따른 BMI 분포 (박스플롯)
    st.header("🚬 성별과 흡연 상태에 따른 BMI 분포")
    fig_gender_smoking = px.box(df, x="성별", y="BMI", color="흡연상태",
                                title="성별과 흡연 상태에 따른 BMI 분포",
                                labels={"BMI": "체질량지수 (BMI)", "성별": "성별", "흡연상태": "흡연 상태"},
                                category_orders={"흡연상태": ["비흡연", "과거 흡연", "현재 흡연"]})
    st.plotly_chart(fig_gender_smoking, use_container_width=True)

    st.markdown("""
    이 박스플롯은 성별과 흡연 상태에 따른 BMI 분포를 보여줍니다:
    - x축은 성별(남성, 여성)을 나타냅니다.
    - y축은 BMI 값을 나타냅니다.
    - 각 박스의 색상은 흡연 상태(비흡연, 과거 흡연, 현재 흡연)를 구분합니다.
    - 박스의 중앙선은 중앙값을, 박스의 하단과 상단은 각각 1사분위수와 3사분위수를 나타냅니다.
    - 박스 밖의 점들은 이상치(outlier)를 표시합니다.
    - 이 차트를 통해 성별과 흡연 여부에 따른 BMI 분포의 차이를 한눈에 파악할 수 있습니다. 예를 들어, 흡연자와 비흡연자 간의 BMI 차이, 또는 남성과 여성 간의 BMI 차이를 비교할 수 있습니다.
    - 또한, 각 그룹 내의 BMI 분포 범위와 중앙값을 쉽게 비교할 수 있어, 건강 관리 정책 수립에 유용한 정보를 제공합니다.
    """)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # 3. 활동 수준과 콜레스테롤의 관계 (바이올린 플롯)
    st.header("❤️ 활동 수준과 콜레스테롤의 관계")
    fig_activity_cholesterol = px.violin(df, x="활동 수준", y="총콜레스테롤", color="활동 수준",
                                         box=True, points="all",
                                         title="활동 수준과 총콜레스테롤의 관계",
                                         labels={"활동 수준": "활동 수준", "총콜레스테롤": "총 콜레스테롤 (mg/dL)"},
                                         category_orders={"활동 수준": ["저활동", "중간활동", "고활동"]})
    st.plotly_chart(fig_activity_cholesterol, use_container_width=True)

    st.markdown("""
    이 바이올린 플롯은 활동 수준과 총콜레스테롤의 관계를 시각화합니다:
    - x축은 활동 수준(저활동, 중간활동, 고활동)을 나타냅니다.
    - y축은 총콜레스테롤 수치(mg/dL)를 나타냅니다.
    - 각 바이올린의 너비는 해당 콜레스테롤 수치의 빈도를 나타냅니다. 넓을수록 해당 수치의 빈도가 높습니다.
    - 각 바이올린 내부의 박스플롯은 중앙값과 사분위수 범위를 보여줍니다.
    - 점들은 개별 데이터 포인트를 나타냅니다.
    - 이 차트를 통해 활동 수준에 따른 콜레스테롤 분포의 차이를 쉽게 비교할 수 있습니다. 예를 들어, 고활동 그룹의 콜레스테롤 분포가 다른 그룹과 어떻게 다른지 관찰할 수 있습니다.
    - 또한, 각 활동 수준 그룹 내에서 콜레스테롤 수치의 분포 형태와 이상치의 존재 여부도 파악할 수 있어, 건강 관리 전략 수립에 유용한 정보를 제공합니다.
    """)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # 4. 고혈당 위험과 BMI의 관계 (그룹화된 막대 차트)
    st.header("🩸 고혈당 위험과 BMI의 관계")
    df['BMI_범주'] = pd.cut(df['BMI'], bins=[0, 18.5, 23, 25, 30, 100], 
                          labels=['저체중', '정상', '과체중', '비만', '고도비만'])
    fig_glucose_bmi = px.histogram(df, x="BMI_범주", color="고혈당 위험",
                                   barmode="group",
                                   title="BMI 범주별 고혈당 위험 분포",
                                   labels={"BMI_범주": "BMI 범주", "고혈당 위험": "고혈당 위험"},
                                   category_orders={"BMI_범주": ['저체중', '정상', '과체중', '비만', '고도비만'],
                                                    "고혈당 위험": ["낮음", "보통", "높음"]})
    st.plotly_chart(fig_glucose_bmi, use_container_width=True)

    st.markdown("""
    이 그룹화된 막대 차트는 BMI 범주와 고혈당 위험의 관계를 보여줍니다:
    - x축은 BMI 범주(저체중, 정상, 과체중, 비만, 고도비만)를 나타냅니다.
    - y축은 각 범주의 빈도를 나타냅니다.
    - 각 BMI 범주 내에서 색상으로 구분된 막대는 고혈당 위험 수준(낮음, 보통, 높음)을 나타냅니다.
    - 이 차트를 통해 BMI 범주별로 고혈당 위험의 분포를 비교할 수 있습니다. 예를 들어, 비만 범주에서 고혈당 위험이 높은 사람의 비율이 다른 범주에 비해 어떻게 다른지 확인할 수 있습니다.
    - 또한, 각 BMI 범주 내에서 고혈당 위험의 상대적 비율을 파악할 수 있어, BMI와 당뇨병 위험 간의 관계를 이해하는 데 도움이 됩니다.
    - 이 정보는 비만과 당뇨병 예방 프로그램 개발에 중요한 인사이트를 제공할 수 있습니다.
    """)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # 5. 음주 여부와 간 지표의 관계 (스택 막대 차트)
    st.header("🍺 음주 여부와 간 지표의 관계")
    fig_drinking_liver = px.histogram(df, x="음주여부", color="간 지표",
                                      title="음주 여부에 따른 간 지표 분포",
                                      labels={"음주여부": "음주 여부", "간 지표": "간 지표"},
                                      category_orders={"간 지표": ["정상", "경계", "위험"],
                                                       "음주여부": ["비음주", "가끔", "자주"]})
    fig_drinking_liver.update_layout(legend_title_text='간 지표')
    st.plotly_chart(fig_drinking_liver, use_container_width=True)

    st.markdown("""
    이 스택 막대 차트는 음주 여부와 간 지표의 관계를 시각화합니다:
    - x축은 음주 여부(비음주, 가끔, 자주)를 나타냅니다.
    - y축은 각 음주 여부 카테고리의 총 빈도를 나타냅니다.
    - 각 막대는 간 지표 상태(정상, 경계, 위험)에 따라 색상으로 구분되어 있습니다.
    - 막대의 각 부분의 높이는 해당 간 지표 상태의 빈도를 나타냅니다.
    - 이 차트를 통해 음주 빈도에 따른 간 건강 상태의 분포를 한눈에 파악할 수 있습니다. 예를 들어, 자주 음주하는 그룹에서 간 지표가 '위험'인 비율이 다른 그룹에 비해 어떻게 다른지 확인할 수 있습니다.
    - 또한, 각 음주 빈도 그룹 내에서 간 지표 상태의 상대적 비율을 비교할 수 있어, 음주와 간 건강 간의 관계를 이해하는 데 도움이 됩니다.
    - 이 정보는 음주가 간 건강에 미치는 영향을 평가하고, 건강한 음주 습관에 대한 가이드라인을 제시하는 데 유용할 수 있습니다.
    """)
    st.markdown("<br>", unsafe_allow_html=True)
