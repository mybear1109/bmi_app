import torch
import os
import streamlit as st
import logging
from model import ExercisePredictionModel, FoodPredictionModel  # 모델 클래스 가져오기
from transformers import AutoTokenizer, AutoModelForCausalLM # Hugging Face 모델 가져오기

# 로깅 설정 (관리자용 로그)
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# 모델 저장 경로
MODEL_EXERCISE_PATH = "models/model_exercise.pth"
MODEL_FOOD_PATH = "models/model_food.pth"

def load_model(model_path, model_class, input_dim=13):
    """
    PyTorch 모델 로드 함수.
    weights_only 옵션 대신 기본 설정(weights_only=False)으로 모델을 안전하게 로드합니다.
    (파일이 신뢰할 수 있는 경우에만 사용하세요.)
    내부 오류는 로깅하며, UI에는 간단한 메시지로 처리합니다.
    """
    model = model_class(input_dim)
    if not os.path.exists(model_path):
        logging.error(f"🚨 모델 파일을 찾을 수 없습니다: {model_path}")
        st.error("모델 파일이 존재하지 않습니다.")
        return None
    try:
        # weights_only=True 사용 시 오류가 발생하므로 weights_only=False로 로드
        checkpoint = torch.load(model_path, map_location=torch.device("cpu"), weights_only=False)
        model.load_state_dict(checkpoint, strict=False)
        model.eval()
        logging.info(f"✅ 모델 로드 성공: {model_path}")
        return model
    except Exception as e:
        logging.error(f"🚨 모델 로드 중 오류 발생: {e}")
        st.error("모델 로드에 문제가 발생했습니다. 관리자에게 문의하세요.")
    return None

# 모델 로드 실행 (UI에는 성공/실패 메시지 최소화)
model_exercise = load_model(MODEL_EXERCISE_PATH, ExercisePredictionModel, input_dim=13)
model_food = load_model(MODEL_FOOD_PATH, FoodPredictionModel, input_dim=13)

# 환경 변수 또는 secrets.toml에서 API 키를 가져옵니다.
HF_API_KEY = os.getenv("HF_API_KEY")  # 미리 선언된 API 키 변수

@st.cache_resource
def load_gemma_model():
    """
    Gemma 모델과 토크나이저 로드 함수.
    오류 발생 시 내부 로깅만 하고, 사용자에게는 간단한 메시지를 표시합니다.
    """
    model_name = "google/gemma-2b-it"
    try:
        hf_token = HF_API_KEY
        if not hf_token:
            logging.error("🚨 HF_API_KEY가 설정되지 않았습니다!")
            return None, None
        # use_auth_token 대신 token 사용 (또는 최신 버전에서는 token 매개변수 사용)
        tokenizer = AutoTokenizer.from_pretrained(model_name, token=hf_token)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.float16,
            token=hf_token
        )
        logging.info("✅ Gemma 모델 로드 성공")
        return tokenizer, model
    except Exception as e:
        logging.error(f"🚨 Gemma 모델 로딩 중 오류 발생: {e}")
        # 사용자에게 자세한 오류는 표시하지 않음
        st.error("Gemma 모델 로드 중 문제가 발생했습니다. (관리자 로그 참조)")
        return None, None

# Gemma 모델과 토크나이저 로드 (UI에서는 관련 메시지 최소화)
gemma_tokenizer, gemma_model = load_gemma_model()
