import torch
import os
import streamlit as st
import logging
import pickle
import model  # 모델 모듈 전체를 불러와서 model.ExercisePredictionModel 등으로 접근
from transformers import AutoTokenizer, AutoModelForCausalLM

# 관리자용 로깅 설정 (콘솔에만 출력)
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# 모델 저장 경로
MODEL_EXERCISE_PATH = "models/model_exercise.pth"
MODEL_FOOD_PATH = "models/model_food.pth"

# 커스텀 언피클러: __main__에서 찾으려는 클래스명을 'model' 모듈로 매핑
class MyUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == '__main__':
            module = 'model'
        return super().find_class(module, name)

def load_model_custom(model_path, model_class, input_dim=13):
    """
    PyTorch 모델을 로드합니다.
    checkpoint가 dict 형식이면 load_state_dict를 사용하고,
    그렇지 않으면 checkpoint를 그대로 모델 인스턴스로 사용합니다.
    (파일이 신뢰할 수 있는 경우에만 사용하세요.)
    """
    # 모델 클래스의 인스턴스를 미리 생성 (model 모듈 내 클래스로 접근)
    model_instance = model_class(input_dim)
    if not os.path.exists(model_path):
        logging.error(f"🚨 모델 파일을 찾을 수 없습니다: {model_path}")
        st.error("모델 파일이 존재하지 않습니다.")
        return None
    try:
        with open(model_path, 'rb') as f:
            checkpoint = MyUnpickler(f).load()
        
        if isinstance(checkpoint, dict):
            model_instance.load_state_dict(checkpoint, strict=False)
        else:
            # checkpoint가 이미 모델 인스턴스인 경우
            model_instance = checkpoint
        
        model_instance.eval()
        logging.info(f"✅ 모델 로드 성공: {model_path}")
        return model_instance
    except Exception as e:
        logging.error(f"🚨 모델 로드 중 오류 발생: {e}")
        st.error("모델 로드에 문제가 발생했습니다. 관리자에게 문의하세요.")
    return None

# 모델 로드 실행 (UI에는 상세 오류 메시지 표시하지 않음)
model_exercise = load_model_custom(MODEL_EXERCISE_PATH, model.ExercisePredictionModel, input_dim=13)
model_food = load_model_custom(MODEL_FOOD_PATH, model.FoodPredictionModel, input_dim=13)

# 환경 변수 또는 secrets.toml에서 API 키를 가져옵니다.
HF_API_KEY = os.getenv("HF_API_KEY")  # 미리 선언된 API 키 변수

@st.cache_resource
def load_gemma_model():
    """
    Gemma 모델과 토크나이저 로드 함수.
    내부 오류는 관리자 로그로 기록되며, 사용자에게는 간단한 메시지만 표시합니다.
    """
    model_name = "google/gemma-2b-it"
    try:
        hf_token = HF_API_KEY
        if not hf_token:
            logging.error("🚨 HF_API_KEY가 설정되지 않았습니다!")
            return None, None
        # 최신 transformers에서는 token 매개변수와 trust_remote_code 옵션을 사용합니다.
        tokenizer = AutoTokenizer.from_pretrained("google/gemma-2b-it", token=HF_API_KEY)
        model_instance = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.float16,
            token=hf_token,
            trust_remote_code=True
        )
        logging.info("✅ Gemma 모델 로드 성공")
        return tokenizer, model_instance
    except Exception as e:
        logging.error(f"🚨 Gemma 모델 로딩 중 오류 발생: {e}")
        st.error("Gemma 모델 로드 중 문제가 발생했습니다. (관리자 로그 참조)")
        return None, None

# Gemma 모델과 토크나이저 로드 (UI에서는 관련 메시지 최소화)
gemma_tokenizer, gemma_model = load_gemma_model()
