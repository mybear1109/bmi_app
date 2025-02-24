from openai import OpenAI
import json
import os

# 환경 변수 또는 secrets.toml에서 API 키를 가져옵니다.
HF_API_KEY = os.getenv("HF_API_KEY")

def get_recommendations(user_data):
    """
    사용자의 건강 데이터를 바탕으로 AI 모델을 활용하여 맞춤형 운동 및 식단을 추천합니다.
    """
    client = OpenAI(
        base_url="https://router.huggingface.co/novita",
        api_key=HF_API_KEY
    )

    prompt = f"""
    다음은 사용자의 건강 데이터입니다:
    {json.dumps(user_data, ensure_ascii=False, indent=4)}
    
    이 데이터를 바탕으로 다음 형식에 맞추어 일주일간의 운동 및 식단을 추천하세요:
    
    운동 추천 예시:
    [
        {{
            "요일": "월",
            "운동": [
                {{"종류": "달리기", "시간(분)": 30, "칼로리 소모": 300}},
                {{"종류": "스트레칭", "시간(분)": 15, "칼로리 소모": 50}}
            ],
            "일일 칼로리 소모량(kcal)": 350,
            "설명": "유산소 운동으로 체지방 감소, 스트레칭으로 유연성 향상"
        }}
    ]
    
    식단 추천 예시:
    [
        {{
            "요일": "월",
            "아침": {{"메뉴": "계란 + 오트밀", "칼로리": 300}},
            "점심": {{"메뉴": "닭가슴살 샐러드", "칼로리": 400}},
            "저녁": {{"메뉴": "구운 채소 + 연어", "칼로리": 450}},
            "간식": {{"메뉴": "그릭 요거트", "칼로리": 150}},
            "일일 총칼로리": 1300,
            "설명": "고단백 저탄수화물 식단으로 체지방 감소 도움"
        }}
    ]
    """
    
    messages = [{"role": "user", "content": prompt}]
    completion = client.chat.completions.create(
        model="google/gemma-2-9b-it",
        messages=messages,
        max_tokens=1000,
    )
    
    response_text = completion.choices[0].message.content
    
    return response_text