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
            background: linear-gradient(to right, #6a82fb, #fc5c7d);
            padding: 3rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 3rem;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
        }

        .main-title {
            color: white;
            font-size: 3.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }

        .subtitle {
            color: rgba(255, 255, 255, 0.8);
            font-size: 1.5rem;
            font-style: italic;
        }

        /* 기능 섹션 스타일 */
        .features-section {
            display: flex;
            flex-wrap: wrap;
            gap: 2rem;
            justify-content: center;
        }

        .feature-card {
            background-color: #fff;
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            flex: 1 1 300px; /* 최소 너비 설정 및 비율 유지 */
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }

        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 7px 15px rgba(0, 0, 0, 0.2);
        }

        .feature-icon {
            font-size: 3rem;
            color: #6a82fb;
            margin-bottom: 1rem;
        }

        .feature-title {
            font-size: 1.75rem;
            color: #333;
            font-weight: bold;
            margin-bottom: 0.75rem;
        }

        .feature-description {
            font-size: 1.1rem;
            color: #555;
            line-height: 1.6;
        }
        

        /* 추가 정보 섹션 스타일 */
        .additional-info {
            background-color: #e9ecef;
            padding: 2rem;
            border-radius: 12px;
            margin-top: 3rem;
            box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
        }

        .additional-title {
            font-size: 2rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 1.5rem;
        }

        .additional-list {
            list-style-type: disc;
            padding-left: 2rem;
        }

        .additional-item {
            font-size: 1.1rem;
            color: #555;
            margin-bottom: 0.75rem;
        }

        /* CTA 버튼 스타일 */
        .cta-button {
            background-color: #28a745;
            color: white;
            border: none;
            padding: 1rem 2rem;
            font-size: 1.25rem;
            border-radius: 8px;
            cursor: pointer;
            transition: background-color 0.3s ease;
            margin-top: 2rem;
            display: inline-block;
            text-decoration: none;
        }

        .cta-button:hover {
            background-color: #218838;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 메인 타이틀
    st.markdown(
        """
        <div class='main-title-container'>
            <h1 class='main-title'>💖 "당신의 오늘은 안녕하십니까?" 💖</h1>
            <h4 p class='subtitle'> AI 피트니스 코치 : 개인 맞춤형 건강 관리 솔루션 😎</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 주요 기능
    st.header("🌟 AI 피트니스 코치의 핵심 기능")
    st.markdown(
        """
        <div class='features-section'>
            <div class='feature-card'>
                <i class='feature-icon'>🔍</i>
                <h3 class='feature-title'>정밀 건강 분석</h3>
                <p class='feature-description'>AI가 건강검진 데이터를 분석하여, 당신의 <strong>현재 건강 상태를 정확하게 파악</strong>합니다.</p>
            </div>
            <div class='feature-card'>
                <i class='feature-icon'>💪</i>
                <h3 class='feature-title'>맞춤형 운동 추천</h3>
                <p class='feature-description'>당신의 체력과 건강 상태에 맞는 <strong>최적의 운동 계획</strong>을 AI가 설계합니다.</p>
            </div>
            <div class='feature-card'>
                <i class='feature-icon'>🥗</i>
                <h3 class='feature-title'>개인화된 식단 제안</h3>
                <p class='feature-description'>영양 균형을 고려한 맞춤형 식단으로 <strong>건강한 식습관을 형성</strong>할 수 있습니다.</p>
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)  # 간격 추가  # 간격 추가
    # 추가 정보
    st.header("🏵️ 왜 AI 피트니스 코치를 선택해야 할까요?")
    st.markdown(
        """
        <div class='additional-info'>
            <h2 class='additional-title'>주요 장점</h2>
            <ul class='additional-list'>
                <li class='additional-item'>📊<strong>데이터 기반</strong> 건강 분석으로 정확한 건강 상태 파악</li>
                <li class='additional-item'>🤖 <strong>AI 추천</strong>으로 개인에게 최적화된 맞춤 계획 제공</li>
                <li class='additional-item'>🚀 <strong>언제 어디서나</strong> 접근 가능한 편리한 모바일 서비스</li>
                <li class='additional-item'>👨‍⚕️ 전문가 수준의 조언을 AI를 통해 <strong>실시간으로 제공</strong></li>
                <li class='additional-item'>📈 지속적인 <strong>데이터 업데이트</strong>로 최신 건강 트렌드 반영</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

