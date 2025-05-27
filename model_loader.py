import torch
import os
import streamlit as st
import logging
from model import ExercisePredictionModel, FoodPredictionModel  # 반드시 model.py에서 가져옴
from transformers import AutoTokenizer, AutoModelForCausalLM

# 관리자용 로깅 설정 (콘솔 또는 파일에 기록)
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# 모델 저장 경로
MODEL_EXERCISE_PATH = "models/model_exercise.pth"
MODEL_FOOD_PATH = "models/model_food.pth"

def load_model(model_path, model_class, input_dim=13):
    """
    PyTorch 모델 로드 함수.
    weights_only 옵션으로 시도하며, 실패 시 weights_only=False로 재시도합니다.
    """
    model = model_class(input_dim)
    if not os.path.exists(model_path):
        logging.error(f"🚨 모델 파일을 찾을 수 없습니다: {model_path}")
        return None
    try:
        checkpoint = torch.load(model_path, map_location=torch.device("cpu"), weights_only=True)
        model.load_state_dict(checkpoint, strict=False)
        model.eval()
        logging.info(f"✅ 모델 로드 성공: {model_path}")
        print(f"✅ 모델 로드 성공: {model_path}")
        return model
    except Exception as e:
        logging.error(f"🚨 모델 로드 중 오류 발생 (weights_only=True 실패): {e}")
        try:
            checkpoint = torch.load(model_path, map_location=torch.device("cpu"), weights_only=False)
            model.load_state_dict(checkpoint, strict=False)
            model.eval()
            logging.info(f"✅ 모델 로드 성공 (weights_only=False): {model_path}")
            print(f"✅ 모델 로드 성공 (weights_only=False): {model_path}")
            return model
        except Exception as e2:
            logging.error(f"🚨 모델 로드 중 오류 발생 (weights_only=False): {e2}")
    return None

# 모델 로드 실행
model_exercise = load_model(MODEL_EXERCISE_PATH, ExercisePredictionModel, input_dim=13)
model_food = load_model(MODEL_FOOD_PATH, FoodPredictionModel, input_dim=13)

# 환경 변수 또는 secrets.toml에서 API 키를 가져옵니다.
HF_API_KEY = os.getenv("HF_API_KEY")  # 미리 선언된 API 키 변수

@st.cache_resource
def load_gemma_model():
    """
    Gemma 모델과 토크나이저 로드 함수.
    `token` 인자를 사용하여 인증 토큰을 전달합니다.
    """
    model_name = "google/gemma-2-9b-it"
    try:
        hf_token = HF_API_KEY
        if not hf_token:
            logging.error("🚨 HF_API_KEY가 설정되지 않았습니다!")
            return None, None
        Gemma_tokenizer= AutoTokenizer.from_pretrained("google/gemma-2-9b-it", token=HF_API_KEY)
        print("✅ GemmaTokenizer 정상 로딩 완료!")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.float16,
            token=hf_token
        )
        logging.info("✅ Gemma 모델 로드 성공")
        print("✅ Gemma 모델 로드 성공")
        return Gemma_tokenizer, model
    except Exception as e:
        logging.error(f"🚨 Gemma 모델 로딩 중 오류 발생: {e}")
        print (f"🚨 Gemma 모델 로딩 중 오류 발생: {e}")
        return None, None

# Gemma 모델과 토크나이저 로드 (UI에 메시지 표시 X)
gemma_tokenizer, gemma_model = load_gemma_model()

