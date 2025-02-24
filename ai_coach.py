import json
from gemma2_recommender import get_recommendations

def extract_required_data(user_data):
    """
    사용자 데이터에서 필요한 건강 정보를 추출합니다.
    """
    required_keys = [
        "BMI", "허리둘레", "수축기혈압(최고 혈압)", "이완기혈압(최저 혈압)",
        "혈압 차이", "총콜레스테롤", "간 지표", "성별", "나이", "비만 위험 지수", "흡연상태", "음주여부"
    ]
    
    return {key: user_data.get(key, None) for key in required_keys}

def generate_health_plan(user_data):
    """
    사용자의 건강 데이터를 바탕으로 운동과 식단을 추천합니다.
    """
    extracted_data = extract_required_data(user_data)
    recommendations = get_recommendations(extracted_data)
    
    return recommendations