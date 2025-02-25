import streamlit as st


def display_home_page():
    """🏠 AI 건강 관리 홈 화면"""

    # ✅ 반응형 디자인 및 스타일 개선

    st.markdown("""
    <style>
        .title-container {
            text-align: center;
            background: linear-gradient(to right, #ff8c00, #ff5e62);
            padding: 30px;
            border-radius: 15px;
            color: white;
        }
        /* 박스 스타일 */
        .feature-container {
            display: flex; align-items: center;
            justify-content: space-around; flex-wrap: wrap;
            white-space: nowrap;
            word-wrap: break-word; overflow-wrap: break-word;        
            gap: 20px;
            flex-wrap: wrap;
            padding: 20px 0;
        }
                
        .feature-box {
            background-color: #fff;
            padding: 20px;
            border-radius: 12px;
            width: auto;
            max-width: 350px; /* 박스 크기 제한 */
            min-width: 250px;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            word-wrap: break-word;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease-in-out;
        }


        /* 제목 (h3) 스타일 */
        .feature-box-title {
            color: #2874a6 !important;  /* 색상 강제 적용 */
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 12px;
            white-space: nowrap; /* 제목은 줄바꿈 방지 */
      
        }

        /* 본문 (p) 스타일 */
        .feature-box-text {
            font-size: 16px;
            line-height: 1.5;
            text-align: center;
        }


        .feature-box:hover {
            transform: scale(1.05);
        }

        .extra-info {
            background: linear-gradient(to right, #6a11cb, #2575fc);
            padding: 20px;
            border-radius: 15px;
            color: white;
        }
        .stButton>button {
            background-color: #ff5e62;
            color: white;
            font-size: 18px;
            padding: 12px 24px;
            border-radius: 10px;
            border: none;
        }
        .stButton>button:hover {
            background-color: #ff3b42;
            transform: scale(1.05);
        }
    </style>
    """, unsafe_allow_html=True)
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
