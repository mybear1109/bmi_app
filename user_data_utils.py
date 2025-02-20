import json
import os
import streamlit as st

# 사용자 데이터 파일 경로 정의
USER_DATA_FILE = "data/user_data.json"

def load_user_data(user_id):
    """📌 사용자 데이터 로드"""
    try:
        if not os.path.exists(USER_DATA_FILE):
            return None  # 파일이 없으면 None 반환

        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get(str(user_id), None)  # user_id는 문자열로 저장될 가능성이 있음
    except json.JSONDecodeError:
        st.warning(f"🚨 사용자 데이터 파일({USER_DATA_FILE})이 손상되었습니다. 기본값을 사용합니다.")
        return None
    except Exception as e:
        st.error(f"🚨 사용자 데이터 로드 중 오류 발생: {e}")
        return None

def save_user_data(user_id, data):
    """📌 사용자 데이터 저장"""
    try:
        os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
        
        # 기존 데이터 로드 또는 빈 딕셔너리
        existing_data = load_existing_data()

        # 새 데이터 추가 또는 업데이트
        existing_data[str(user_id)] = data

        # 수정된 데이터를 파일에 저장
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=4, ensure_ascii=False)
        st.success("✅ 사용자 정보가 저장되었습니다!")
  
    except IOError as e:
        st.error(f"❌ 사용자 정보 저장 중 오류 발생: {e}")
    except Exception as e:
        st.error(f"❌ 사용자 정보 저장 중 예기치 않은 오류 발생: {e}")

def load_existing_data():
    """📌 기존 데이터를 로드하거나 빈 딕셔너리를 반환"""
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except json.JSONDecodeError:
        st.warning(f"⚠️ 사용자 데이터 파일({USER_DATA_FILE})이 손상되어 초기화합니다.")
    return {}  # 파일이 없거나 손상되었으면 빈 딕셔너리 반환

def get_safe_value(value, default, value_type=int):
    """📌 안전하게 값을 변환"""
    try:
        if value is None:
            return default
        if isinstance(value, list) and len(value) > 0:
            value = value[0]  # 리스트인 경우 첫 번째 요소 사용
        return value_type(value)
    except (ValueError, TypeError):
        st.warning(f"⚠️ 값 변환 실패 (타입: {value_type.__name__}), 기본값 사용: {default}")
        return default
    except Exception as e:
        st.error(f"❌ 값 변환 중 오류 발생: {e}, 기본값 사용: {default}")
        return default

def calculate_bmi(weight, height):
    """📌 BMI 계산"""
    if not isinstance(height, (int, float)) or not isinstance(weight, (int, float)):
        st.error("🚨 키와 체중은 숫자 값이어야 합니다.")
        return None

    if height <= 0 or weight <= 0:
        st.error("🚨 키와 체중은 0보다 커야 합니다.")
        return None

    height_m = height / 100  # cm를 m로 변환
    return round(weight / (height_m ** 2), 2)

def calculate_age_group(age):
    """📌 5세 단위 연령대 계산"""
    if not isinstance(age, int):
        st.error("🚨 나이는 정수 값이어야 합니다.")
        return None

    if age < 0:
        st.error("🚨 나이는 0보다 커야 합니다.")
        return None
    return (age // 5) * 5

def display_user_info_table(user_info):
    """📌 사용자 정보를 테이블 형식으로 표시"""
    if not user_info:
        st.warning("⚠️ 표시할 사용자 정보가 없습니다.")
        return

    # 표시할 정보 선택 및 정렬
    display_info = {
        "성별": user_info.get("성별", "미입력"),
        "연령대": user_info.get("연령대", "미입력"),
        "키 (cm)": user_info.get("키 (cm)", "미입력"),
        "현재 체중 (kg)": user_info.get("현재 체중", "미입력"),
        "목표 체중 (kg)": user_info.get("목표 체중", "미입력"),
        "BMI": user_info.get("BMI", "미입력"),
        "활동 수준": user_info.get("활동 수준", "미입력"),
    }
    
    # DataFrame 생성 및 표시
    df_info = pd.DataFrame(list(display_info.items()), columns=["항목", "정보"])
    st.table(df_info)
