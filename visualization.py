import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import colorsys

# 예측 데이터 파일 경로 설정
PREDICTION_FILE = "data/predictions.csv"

@st.cache_data
def load_prediction_data():
    """CSV 파일에서 예측 데이터를 로드하는 함수"""
    if os.path.exists(PREDICTION_FILE):
        df = pd.read_csv(PREDICTION_FILE)
        if df.empty:
            return None
        
        numeric_columns = ["운동 확률", "식단 확률", "BMI", "현재 체중 (kg)", "목표 체중 (kg)"]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.rstrip("%"), errors="coerce")
        
        df = df.dropna(subset=numeric_columns)
        return df
    return None

def create_summary_metrics(data):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="평균 운동 확률", value=f"{data['운동 확률'].mean():.2%}")
    with col2:
        st.metric(label="평균 식단 개선 필요성", value=f"{data['식단 확률'].mean():.2%}")
    with col3:
        st.metric(label="평균 BMI", value=f"{data['BMI'].mean():.2f}")

def create_scatter_plot(data):
    fig = px.scatter(
        data, x="운동 확률", y="식단 확률", color="BMI", hover_name="이름",
        size="BMI", size_max=15, opacity=0.7,
        labels={"운동 확률": "운동 확률 (%)", "식단 확률": "식단 개선 필요성 (%)", "BMI": "BMI"},
        title="운동 확률과 식단 개선 필요성의 관계"
    )
    return fig

def create_bmi_distribution(data):
    fig = px.violin(data, y="BMI", box=True, points="all", title="BMI 분포 (바이올린 플롯)")
    return fig

def create_weight_tracker(data):
    current_weight = data["현재 체중 (kg)"].mean()
    target_weight = data["목표 체중 (kg)"].mean()
    mid_point = (current_weight + target_weight) / 2
    checkpoint_1 = current_weight - (current_weight - mid_point) / 3
    checkpoint_2 = current_weight - (current_weight - mid_point) * 2 / 3

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=["시작", "중간 1", "중간 2", "현재", "목표"], 
        y=[current_weight, checkpoint_1, checkpoint_2, mid_point, target_weight],
        mode='lines+markers', 
        name='체중 변화',
        line=dict(color='blue', width=2),
        marker=dict(size=10)
    ))

    fig.add_trace(go.Scatter(
        x=["시작", "목표"],
        y=[current_weight, target_weight],
        mode='lines',
        name='전체 추세',
        line=dict(color='red', dash='dash')
    ))

    fig.add_annotation(
        x="중간 1",
        y=checkpoint_1,
        text="첫 번째 목표 달성!",
        showarrow=True,
        arrowhead=2
    )

    fig.update_layout(
        title="상세 체중 변화 추적",
        xaxis_title="진행 단계",
        yaxis_title="체중 (kg)",
        legend_title="데이터 유형",
        hovermode="x unified"
    )

    y_min = min(target_weight, current_weight) - 2
    y_max = max(target_weight, current_weight) + 2
    fig.update_yaxes(range=[y_min, y_max])

    return fig, current_weight, target_weight



def display_visualization_page():
    st.header("📊 데이터 시각화")

    data = load_prediction_data()

    if data is None or data.empty:
        st.warning("🚨 저장된 예측 데이터가 없거나 모든 데이터가 NaN입니다. 예측을 실행한 후 다시 확인해주세요!")
        return

    st.subheader("🎯 예측 결과 요약")
    create_summary_metrics(data)

    st.header("🔍 운동 확률 vs 식단 개선 필요성")
    st.plotly_chart(create_scatter_plot(data))

    st.header("📊 BMI 분포")
    st.plotly_chart(create_bmi_distribution(data))

    st.header("⚖️ 체중 변화 트래커")
    weight_fig, current_weight, target_weight = create_weight_tracker(data)
    st.plotly_chart(weight_fig)

    weight_change = target_weight - current_weight
    st.success(f"현재 평균 체중에서 목표 체중까지 {abs(weight_change):.1f}kg의 변화가 필요합니다.")
    if weight_change < 0:
        st.info("체중 감량이 목표입니다. 건강한 식단과 규칙적인 운동으로 목표를 달성해보세요!")
    elif weight_change > 0:
        st.write("체중 증가가 목표입니다. 균형 잡힌 영양 섭취와 근력 운동으로 건강하게 체중을 늘려보세요!")
    else:
        st.write("현재 체중을 유지하는 것이 목표입니다. 건강한 생활 습관을 지속해주세요!")

    st.header("📋 상세 예측 결과 (최근 8개)")
    columns_to_display = ['BMI', '현재 체중 (kg)', '목표 체중 (kg)', '운동 확률', '식단 확률']
    data_display = data[columns_to_display].sort_index(ascending=False).head(8)
    st.dataframe(data_display.style.format({
        "성별" : "{:.2f}",
        "BMI": "{:.2f}",
        "현재 체중 (kg)": "{:.1f}",
        "목표 체중 (kg)": "{:.1f}",
        "운동 확률": "{:.2%}",
        "식단 확률": "{:.2%}"
    }).set_properties(**{
        'text-align': 'center',
        'font-size': '14px'
    }).set_table_styles([
        {"selector": "th", "props": [("text-align", "center"), ("font-size", "16px"), ("font-weight", "bold")]}
    ]))

    st.header("🏋️‍♂️ 운동 가능성 분포")
    exercise_fig = create_exercise_distribution(data)
    if exercise_fig:
        st.plotly_chart(exercise_fig, use_container_width=True)
    else:
        st.write("운동 가능성 데이터가 없습니다.")

def create_exercise_distribution(data):
    """Creates a pie chart visualizing the distribution of '운동 가능성' (exercise potential)."""
    
    if "운동 가능성" not in data.columns:
        st.warning("운동 가능성 열이 데이터에 없습니다. 시각화를 생성할 수 없습니다.")
        return None
    
    exercise_counts = data["운동 가능성"].value_counts().sort_index()
    
    # Custom labels for better readability, using a dictionary for flexibility
    labels_mapping = {
        "❗ 운동이 매우 부족합니다.": "매우 부족",
        "❌ 현재 운동이 부족합니다.": "현재 부족",
        "⚠️ 운동량을 조금 더 늘려보세요.": "늘려보세요",
        "💪 훌륭해요!": "훌륭해요",
        "🏆 최고의 운동 습관!": "최고 습관",
    }
    
    # Apply mapping, handling cases where a value might not be in the mapping
    labels = [labels_mapping.get(item, item) for item in exercise_counts.index]

    # Define a color palette (more accessible and visually appealing)
    colors = px.colors.qualitative.Pastel

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=exercise_counts.values,
        hole=0.3,
        marker_colors=colors[:len(exercise_counts)], # Ensure enough colors
        textinfo='percent',
        insidetextorientation='radial',
        sort=False # Keep original order
    )])
    
    fig.update_layout(
        title={
            'text': "운동 가능성 분포",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=20, color='#264e86') # Softer title color
        },
        font=dict(family="Arial", size=12),
        showlegend=False, # Hide legend since labels are on the pie chart
        
        # Annotation in the center of the pie chart
        annotations=[dict(text='운동\n가능성', x=0.5, y=0.5, font_size=14, showarrow=False)], # Centered multi-line annotation

        margin=dict(l=20, r=20, b=10, t=50), # Tighten margins
        uniformtext_minsize=12, uniformtext_mode='hide' # Hide small labels
    )
    
    return fig

def display_exercise_distribution(data):
    """Displays the exercise distribution pie chart in Streamlit."""
    
    # Check if 'data' is None or empty
    if data is None or data.empty:
        st.warning("⚠️ 데이터가 없습니다. 먼저 사용자 정보를 입력하고 예측을 실행해주세요.")
        return

    exercise_fig = create_exercise_distribution(data)
    if exercise_fig:
        st.plotly_chart(exercise_fig, use_container_width=True)
    else:
        st.warning("운동 가능성 데이터를 표시할 수 없습니다. 필요한 열이 데이터에 있는지 확인해주세요.")
  

 