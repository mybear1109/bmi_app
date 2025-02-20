from transformers import pipeline, AutoTokenizer
import torch
import json
import os
import warnings

warnings.filterwarnings('ignore')  # 경고 메시지 무시

HF_API_KEY = os.getenv("HF_API_KEY")

def load_gemma_model(model_name):
    """모델을 로드하는 함수"""
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name, token=HF_API_KEY)
        pipe = pipeline(
            "text-generation",
            model=model_name,
            tokenizer=tokenizer,
            model_kwargs={"torch_dtype": torch.float32},
            device="cpu",
            token=HF_API_KEY
        )
        print(f"✅ {model_name} 모델 로드 성공")
        return pipe
    except Exception as e:
        print(f"🚨 {model_name} 모델 로드 실패: {e}")
        return None

def parse_json_response(response_text):
    """📌 모델 응답을 JSON 형식으로 변환"""
    try:
        json_start = response_text.find("[{")
        json_end = response_text.rfind("}]")
        if json_start != -1 and json_end != -1:
            json_output = response_text[json_start:json_end + 2]
            return json.loads(json_output)
        else:
            return [{"메시지": "🚨 JSON 데이터 변환 실패, 모델 응답을 확인하세요."}]
    except json.JSONDecodeError:
        return [{"메시지": "🚨 JSON 변환 오류 발생, 모델 응답을 확인하세요."}]

def get_gemma_recommendation(category, user_info, excluded_foods=[]):
    """📌 Google Gemma 모델을 이용한 맞춤형 운동 & 식단 추천"""
    user_info_text = json.dumps(user_info, ensure_ascii=False) if isinstance(user_info, dict) else str(user_info)
    prompt = f"사용자 건강 상태: {user_info_text}\n"

    if category == "운동":
        prompt += "사용자의 건강 상태와 목표에 맞는 7일 운동 계획을 JSON 형식으로 제공해 주세요."
    elif category == "식단":
        prompt += "사용자의 건강 상태를 고려한 7일 식단을 JSON 형식으로 제공해 주세요."
        if excluded_foods:
            prompt += f"\n🚨 **다음 음식은 제외해주세요: {', '.join(excluded_foods)}**"

    system_content = (
        "당신은 전문적인 AI 피트니스 코치이며, 개인 맞춤형 건강 관리 전문가입니다. "
        "사용자의 건강 정보를 기반으로 최적의 운동 및 식단 계획을 작성해 주세요. "
        "일반적인 조언이 아니라, 사용자의 현재 건강 상태와 목표에 맞춘 상세한 가이드를 제공해야 합니다.\n\n"
        "운동 추천 시:\n"
        "- 사용자의 신체 상태(BMI, 체중, 활동 수준 등)에 따라 운동 강도를 조정하세요.\n"
        "- 매일 수행할 운동을 추천하고, 각 운동의 시간(분)과 예상 소모 칼로리를 포함하세요.\n"
        "- 운동 부위(상체, 하체, 코어 등)를 균형 있게 고려하세요.\n"
        "- 사용자가 피해야 할 운동(부상 위험, 건강 상태 고려)을 주의하세요.\n"
        "- 7일 운동 계획을 제공하세요.\n\n"
        "식단 추천 시:\n"
        "- 사용자의 건강 목표(체중 감량, 근육 증가, 혈압 관리 등)에 따라 식단을 맞춤 구성하세요.\n"
        "- 아침, 점심, 저녁 3끼를 추천하며, 각 식사의 영양 균형을 고려하세요.\n"
        "- 사용자가 알러지 반응을 보이거나 피해야 하는 음식은 포함하지 마세요.\n"
        "- 음식의 영양적 이점과 섭취 이유를 간략히 설명하세요.\n"
        "- 7일 식단 계획을 제공하세요.\n\n"
        "🚨 **모든 응답은 JSON 형식으로 제공해야 합니다!**\n"
        "운동 예시:\n"
        '[{"요일": "월요일", "운동": "러닝", "운동 시간(분)": 30, "칼로리 소모량(kcal)": 250}]\n'
        "식단 예시:\n"
        '[{"요일": "월요일", "아침": "현미밥 + 나물반찬", "점심": "닭가슴살 샐러드", "저녁": "구운 연어와 채소"}]\n'
    )
    
    prompt = system_content + prompt

    pipe = load_gemma_model("google/gemma-2-9b-it")
    if not pipe:
        return [{"메시지": "🚨 모델 로딩 실패"}]

    outputs = pipe(prompt, max_length=512, num_return_sequences=1)
    response_text = outputs[0]['generated_text']
    
    return parse_json_response(response_text)

