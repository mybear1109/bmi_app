import streamlit as st

# ✅ 홈 화면 스타일 설정
st.markdown("""
    <style>
        .big-title {
            font-size: 36px;
            font-weight: bold;
            color: #007BFF;
            text-align: center;
            padding: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        .subtitle {
            font-size: 20px;
            font-weight: bold;
            color: #343A40;
            text-align: center;
            padding: 10px;
        }
        .centered {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
        }
        .btn-container {
            display: flex;
            justify-content: space-around;
            margin-top: 20px;
        }
        .stButton > button {
            width: 90%;
            font-size: 18px;
            padding: 12px;
            border-radius: 10px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #0056b3;
            color: white;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
    </style>
""", unsafe_allow_html=True)

# ✅ 페이지 제목
st.markdown('<p class="big-title">🏠 AI 건강 관리 홈</p>', unsafe_allow_html=True)

# ✅ 설명
st.markdown("""
    **AI 건강 관리 플랫폼**에 오신 것을 환영합니다! 🎉  
    당신의 건강을 관리하고 맞춤형 피트니스 및 식단 추천을 받아보세요.  
    아래 기능을 통해 건강 데이터를 입력하고, AI 분석을 활용할 수 있습니다.
""")

# ✅ 홈 화면 레이아웃 설정 (2개 컬럼으로 구성)
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="centered">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/2983/2983065.png", width=150)
    st.markdown('<p class="subtitle">📝 건강 정보 입력</p>', unsafe_allow_html=True)
    st.write("건강 정보를 입력하여 AI 건강 분석을 시작하세요.")
    if st.button("건강 정보 입력하기", key="btn_health_info"):
        st.session_state["menu_option"] = "건강 정보 입력"
        st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="centered">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/1040/1040219.png", width=150)
    st.markdown('<p class="subtitle">🏋️ AI 건강 코치</p>', unsafe_allow_html=True)
    st.write("AI가 추천하는 맞춤형 운동 및 식단을 확인하세요.")
    if st.button("AI 건강 코치 시작", key="btn_ai_coach"):
        st.session_state["menu_option"] = "AI 건강 코치"
        st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ✅ 추가 기능 버튼 (3개 컬럼 활용)
st.markdown('<div class="btn-container">', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("📊 데이터 시각화", key="btn_visualization"):
        st.session_state["menu_option"] = "데이터 시각화" 
        st.experimental_rerun()

with col2:
    if st.button("🔍 예측하기", key="btn_prediction"):
        st.session_state["menu_option"] = "예측하기"
        st.experimental_rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ✅ 푸터 정보
st.markdown("---")
st.markdown("""
    🚀 **AI 건강 관리 플랫폼**은 건강 데이터를 기반으로 맞춤형 추천을 제공합니다.  
    🤖 AI 기술을 활용하여 운동 및 식단을 최적화하세요!  
    📢 더 나은 기능을 원하시면 피드백을 남겨주세요. 감사합니다! 🎉
""", unsafe_allow_html=True)
