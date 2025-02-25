import streamlit as st


def display_home_page():
    """🏠 AI 건강 관리 홈 화면"""

    # ✅ 반응형 디자인 및 스타일 개선
    st.markdown(
        """
        <style>
        body {
            font-family: 'Helvetica Neue', sans-serif;
            background-color: #f0f2f5;
            color: #333;
        }
        
        /* 전체 레이아웃 컨테이너 */
        .container {
            max-width: 100%;
            margin: auto;
            padding: 20px;
        }

        /* 메인 타이틀 영역 */
        .main-title-container {
            background: linear-gradient(45deg, #6a11cb 0%, #2575fc 100%);
            padding: 3rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 3rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            width: 100%;
            max-width: 90%;
        }
        .main-title {
            color: white;
            font-size: 3.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .subtitle {
            color: rgba(255, 255, 255, 0.9);
            font-size: 2rem;
            font-style: italic;
        }

        /* 기능 섹션 스타일 */
        .features-section {
            display: flex; align-items: center;
            justify-content: space-around; flex-wrap: wrap;
            white-space: nowrap;
            word-wrap: break-word; overflow-wrap: break-word;        
            gap: 20px;
            flex-wrap: wrap;
            padding: 20px 0;
        }
        .feature-card {
            background: linear-gradient(135deg, #ff758c 0%, #ff7eb3 100%);
            border-radius: 15px;
            padding: 2.5rem;
            text-align: center;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
            border: 1px solid #ffffff;
            color: white;
            flex: 1 1 30%;
            min-width: 300px;
        }
        .feature-card:hover {
            transform: scale(1.05);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
        }
        .feature-icon {
            font-size: 4rem;
            margin-bottom: 1.5rem;
            display: block;
        }
        .feature-title {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        .feature-description {
            font-size: 1.3rem;
            line-height: 1.6;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ✅ 메인 타이틀
    st.markdown(
        """
        <div class='main-title-container'>
            <h1 class='main-title'>🔥 AI 피트니스 코치 - 당신의 건강을 위한 최고의 선택 🔥</h1>
            <h4 class='subtitle'>AI 기반 맞춤형 건강 관리로 더 나은 삶을 시작하세요!</h4>
        </div>
        <h1 class='main-title' style='text-align: center; color: #ff4081;'>💖 "당신의 오늘은 안녕하십니까?" 💖</h1>
        """,
        unsafe_allow_html=True
    )

    # ✅ 주요 기능 소개
    st.markdown(
        """
        <div class='features-section'>
            <div class='feature-card'>
                <i class='feature-icon'>🔬</i>
                <h3 class='feature-title'>AI 기반 건강 분석</h3>
                <p class='feature-description'>최첨단 AI가 건강 데이터를 분석하여 맞춤형 솔루션을 제공합니다.</p>
            </div>
            <div class='feature-card'>
                <i class='feature-icon'>💪</i>
                <h3 class='feature-title'>맞춤형 운동 루틴</h3>
                <p class='feature-description'>당신의 체력과 목표에 최적화된 운동 계획을 세워드립니다.</p>
            </div>
            <div class='feature-card'>
                <i class='feature-icon'>🥗</i>
                <h3 class='feature-title'>스마트 영양 관리</h3>
                <p class='feature-description'>균형 잡힌 식단과 영양 분석을 통해 건강한 식습관을 유지하세요.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 추가 정보
    st.markdown(
        """
        <div class='additional-info' style='max-width: 1200px; margin-left: auto; margin-right: auto;'>
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
