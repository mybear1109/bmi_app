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
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            border: 1px solid #e0e0e0;
        }

        .feature-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
            border-color: #2575fc;
        }

        .feature-card:first-child {
            flex-basis: 100%;
            margin-bottom: 2rem;
        }

        .feature-card:not(:first-child) {
            flex-basis: calc(50% - 1rem);
        }

        .feature-icon {
            font-size: 4rem;
            color: #2575fc;
            margin-bottom: 1.5rem;
            display: block;
        }

        .feature-title {
            font-size: 2rem;
            color: #333;
            font-weight: bold;
            margin-bottom: 1rem;
        }

        .feature-description {
            font-size: 1.2rem;
            color: #555;
            line-height: 1.6;
        }

        /* 추가 정보 섹션 스타일 */
        .additional-info {
            background-color: #ffffff;
            padding: 3rem;
            border-radius: 12px;
            margin-top: 3rem;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
            border: 1px solid #e0e0e0;
        }

        .additional-title {
            font-size: 2.5rem;
            font-weight: bold;
            color: #2575fc;
            margin-bottom: 2rem;
            text-align: center;
        }

        .additional-list {
            list-style-type: none;
            padding-left: 0;
        }

        .additional-item {
            font-size: 1.3rem;
            color: #333;
            margin-bottom: 1.5rem;
            padding-left: 2.5rem;
            position: relative;
        }

        .additional-item:before {
            content: '✓';
            position: absolute;
            left: 0;
            color: #2575fc;
            font-weight: bold;
        }

        /* CTA 버튼 스타일 */
        .cta-button {
            background: linear-gradient(45deg, #11998e 0%, #38ef7d 100%);
            color: white;
            border: none;
            padding: 1.2rem 2.5rem;
            font-size: 1.5rem;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 3rem;
            display: block;
            width: fit-content;
            margin-left: auto;
            margin-right: auto;
            text-decoration: none;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }

        .cta-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 메인 타이틀
    st.markdown(
        """
        <style>
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
            color: #FAFAFA;  /* 흰색으로 변경 */
            font-size: 3.8rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .subtitle {
            color: #FAFAFA;  /* 흰색으로 변경 */
            font-size: 1.7rem;
            font-style: italic;
        }
        </style>

        <div class='main-title-container'>
            <h1 class='main-title'>💖 "당신의 오늘은 안녕하십니까?" 💖</h1>
            <h4 class='subtitle'>AI 피트니스 코치: 개인 맞춤형 건강 관리의 혁명 🚀</h4>
        </div>
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
                <p class='feature-description'>최첨단 AI 기술로 당신의 건강 데이터를 심층 분석하여, <strong>개인화된 건강 인사이트</strong>를 제공합니다. 당신만의 유니크한 건강 프로필을 만나보세요.</p>
            </div>
            <div class='feature-card'>
                <i class='feature-icon'>💪</i>
                <h3 class='feature-title'>맞춤형 운동 설계</h3>
                <p class='feature-description'>AI가 당신의 체력, 목표, 선호도를 고려하여 <strong>최적화된 운동 루틴</strong>을 설계합니다. 효과적이고 즐거운 운동으로 건강한 삶을 누리세요.</p>
            </div>
            <div class='feature-card'>
                <i class='feature-icon'>🥗</i>
                <h3 class='feature-title'>스마트 영양 관리</h3>
                <p class='feature-description'>영양학적 균형과 개인의 건강 목표를 고려한 <strong>맞춤형 식단</strong>을 제안합니다. 맛있게 먹으면서 건강해지는 식습관의 비결을 발견하세요.</p>
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
                <li class='additional-item'>복잡한 건강 정보를 쉽고 직관적으로 이해할 수 있는 스마트 대시보드를 제공합니다.</li>
                <li class='additional-item'>전문가 수준의 건강 조언을 AI를 통해 언제 어디서나 받아볼 수 있습니다.</li>
                <li class='additional-item'>지속적인 데이터 업데이트로 최신 건강 트렌드와 연구 결과를 반영합니다.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

