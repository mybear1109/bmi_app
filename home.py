import streamlit as st


def display_home_page():
    """🏠 AI 피트니스 코치 - 홈 화면"""

    # 페이지 스타일 설정 (CSS)
    st.markdown(
        """
        <style>
        /* 전체 배경 및 폰트 설정 */
        body {
            font-family: 'Helvetica Neue', sans-serif;
            background-color: #f4f4f4;
            color: #333;
        }

        /* 메인 타이틀 컨테이너 */
        .main-title-container {
            background: linear-gradient(45deg, #6a11cb 0%, #2575fc 100%);
            padding: 3rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 3rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            animation: fadeIn 1.5s ease-in-out;
        }

        .main-title {
            color: white;
            font-size: 3.8rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .subtitle {
            color: rgba(255, 255, 255, 0.9);
            font-size: 1.7rem;
            font-style: italic;
        }

        /* 주요 메시지 강조 */
        .highlight {
            font-size: 2.5rem;
            font-weight: bold;
            color: #ff4d4d;
            text-align: center;
            margin-top: 1rem;
            animation: pulse 2s infinite;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 메인 타이틀 및 주요 메시지
    st.markdown(
        """
        <div class='main-title-container'>
            <h1 class='main-title'>🔥 AI 피트니스 코치 - 당신의 건강을 위한 최고의 선택 🔥</h1>
            <h4 class='subtitle'>AI 기반 맞춤형 건강 관리로 더 나은 삶을 시작하세요!</h4>
        </div>
        <h1 class='highlight'>💖 "당신의 오늘은 안녕하십니까?" 💖</h1>
        """,
        unsafe_allow_html=True
    )

    # 주요 기능
    st.markdown(
        """
        <div class='features-section'>
            <div class='feature-card'>
                <i class='feature-icon'>🔬</i>
                <h3 class='feature-title'>AI 기반 정밀 건강 분석</h3>
                <p class='feature-description'>최첨단 AI 기술로 당신의 건강 데이터를 심층 분석하여, <strong>개인화된 건강 인사이트</strong>를 제공합니다.</p>
            </div>
            <div class='feature-card'>
                <i class='feature-icon'>💪</i>
                <h3 class='feature-title'>맞춤형 운동 설계</h3>
                <p class='feature-description'>AI가 당신의 체력, 목표, 선호도를 고려하여 <strong>최적화된 운동 루틴</strong>을 설계합니다.</p>
            </div>
            <div class='feature-card'>
                <i class='feature-icon'>🥗</i>
                <h3 class='feature-title'>스마트 영양 관리</h3>
                <p class='feature-description'>영양학적 균형과 개인의 건강 목표를 고려한 <strong>맞춤형 식단</strong>을 제안합니다.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 추가 정보
    st.markdown(
        """
        <div class='additional-info'>
            <h2 class='additional-title'>🏆 AI 피트니스 코치의 특별한 가치</h2>
            <ul class='additional-list'>
                <li class='additional-item'>24/7 실시간 건강 모니터링으로 언제나 당신 곁에서 건강을 지켜드립니다.</li>
                <li class='additional-item'>빅데이터와 AI의 만남으로 탄생한 초개인화 건강 솔루션을 경험하세요.</li>
                <li class='additional-item'>전문가 수준의 건강 조언을 AI를 통해 언제 어디서나 받아볼 수 있습니다.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )