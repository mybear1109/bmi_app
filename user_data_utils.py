import json
import os

USER_DATA_FILE = "data/user_data.json"

def load_user_data():
    """📌 사용자 데이터를 불러오기"""
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user_data(data):
    """📌 사용자 데이터를 저장하기"""
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
