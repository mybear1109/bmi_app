import streamlit as st

def display_home_page():
    """🏋️‍♂️ AI 피트니스 코치 - 홈 화면"""
    
    st.markdown("""
    <style>
        .title-container {
            text-align: center;
            width: auto;    
            background: linear-gradient(to right, #ff8c00, #ff5e62);
            padding: 30px;
            border-radius: 15px;
            color: white;
            margin-bottom: 30px;
        }

        .feature-container {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 20px;
            padding: 20px 0;
        }

        .feature-box {
            background-color: #fff;
            padding: 20px;
            border-radius: 12px;
            flex: 1;
            min-width: 250px;
            max-width: 350px;
            text-align: center;
            display: flex;
            justify-content: space-between;
            flex-direction: column;
            align-items: center;
            word-wrap: break-word;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease-in-out;
        }

        .feature-box:hover {
            transform: scale(1.05);
        }

        .feature-box-title {
            color: #2874a6 !important;
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 12px;
            white-space: nowrap;
        }

        .feature-box-text {
            font-size: 16px;
            line-height: 1.5;
            text-align: center;
        }

        .extra-info {
            background: linear-gradient(to right, #6a11cb, #2575fc);
            padding: 20px;
            border-radius: 15px;
            color: white;
            margin-top: 30px;
        }

        .testimonial {
            background-color: #f0f0f0;
            padding: 20px;
            border-radius: 15px;
            margin-top: 30px;
        }

        .testimonial-text {
            font-style: italic;
            font-size: 18px;
            color: #333;
        }

        .testimonial-author {
            font-weight: bold;
            text-align: right;
            margin-top: 10px;
        }

        .cta-button {
            background-color: #ff5e62;
            color: white;
            font-size: 18px;
            padding: 12px 24px;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s, transform 0.3s;
            display: block;
            margin: 30px auto;
            text-align: center;
        }

        .cta-button:hover {
            background-color: #ff3b42;
            transform: scale(1.05);
        }

        .stats-container {
            display: flex;
            justify-content: space-around;
            margin-top: 30px;
            text-align: center;
        }

        .stat-item {
            background-color: #e1f5fe;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        .stat-number {
            font-size: 24px;
            font-weight: bold;
            color: #0277bd;
        }

        .stat-label {
            font-size: 14px;
            color: #01579b;
        }
    </style>
    """, unsafe_allow_html=True)

    # 타이틀 섹션
    st.markdown("""
    <div class="title-container">
        <h1>🏋️‍♂️ AI 피트니스 코치</h1>
        <h3>🔎 맞춤형 건강 분석 & AI 기반 추천</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 주요 기능 섹션
    st.header("🌟 AI 피트니스 코치의 핵심 기능")
    col1, col2, col3 = st.columns(3)

    st.markdown('<div class="feature-container">', unsafe_allow_html=True)

    # 첫 번째 행
    with col1:
        st.markdown("""
        <div class="feature-box">
            <h3 class="feature-box-title">🔍 정밀 건강 분석</h3>
            <p class="feature-box-text">AI가 건강검진 데이터를 분석하여, 당신의 <strong>현재 건강 상태를 정확하게 파악</strong>합니다.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-box">
            <h3 class="feature-box-title">💪 맞춤형 운동 추천</h3>
            <p class="feature-box-text">당신의 체력과 건강 상태에 맞는 <strong>최적의 운동 계획</strong>을 AI가 설계합니다.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-box">
            <h3 class="feature-box-title">🥗 개인화된 식단 제안</h3>
            <p class="feature-box-text">영양 균형을 고려한 맞춤형 식단으로 <strong>건강한 식습관을 형성</strong>할 수 있습니다.</p>
        </div>
        """, unsafe_allow_html=True)

    # 두 번째 행
    with col1:
        st.markdown("""
        <div class="feature-box">
            <h3 class="feature-box-title">📊 진행 상황 추적</h3>
            <p class="feature-box-text">실시간으로 당신의 <strong>건강 개선 상황을 모니터링</strong>하고 피드백을 제공합니다.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-box">
            <h3 class="feature-box-title">🤖 AI 건강 상담</h3>
            <p class="feature-box-text">24/7 이용 가능한 <strong>AI 건강 상담 서비스</strong>로 언제든 궁금증을 해결할 수 있습니다.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-box">
        <h3 class="feature-box-title">✨ 습관 형성 완료</h3>
        <p class="feature-box-text">꾸준한 노력의 결실, <strong>맞춤형 선물</strong>로 특별하게 기념할 수 있습니다. </p>
        </div>
        """, unsafe_allow_html=True)    

    st.markdown("</div>", unsafe_allow_html=True)

    # 추가 정보 섹션
    st.markdown("""
    <div class="extra-info">
        <h3>🎯 왜 AI 피트니스 코치를 선택해야 하나요?</h3>
        <ul>
            <li>📊 <strong>데이터 기반</strong> 건강 분석으로 정확한 건강 상태 파악</li>
            <li>🤖 <strong>AI 추천</strong>으로 개인에게 최적화된 맞춤 계획 제공</li>
            <li>🚀 <strong>언제 어디서나</strong> 접근 가능한 편리한 모바일 서비스</li>
            <li>👨‍⚕️ 전문가 수준의 조언을 AI를 통해 실시간으로 제공</li>
            <li>📈 지속적인 <strong>데이터 업데이트</strong>로 최신 건강 트렌드 반영</li>
            <li>🔒 철저한 <strong>개인정보 보호</strong>로 안심하고 사용 가능</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

 


