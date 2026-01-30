import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime

# הגדרות קבצים
DATA_FILE = "factory_data.csv"
IMAGE_FOLDER = "fault_images"

if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["מזהה", "זמן", "שם העובד", "מחלקה", "מכונה", "תיאור", "דחיפות", "סטטוס", "הערת מנהל", "תמונה"])
    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

def send_telegram_msg(worker, machine, desc, urgency):
    try:
        token = st.secrets["telegram_token"]
        chat_id = st.secrets["telegram_chat_id"]
        message = f"⚠️ דיווח חדש!\n👤 עובד: {worker}\n🏗️ מכונה: {machine}\n🚨 דחיפות: {urgency}\n📝 תיאור: {desc}"
        url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
        requests.get(url)
    except:
        pass

st.set_page_config(page_title="מערכת תקלות - אברהים", layout="wide")
st.title("🛠️ ניהול תקלות המפעל")

if 'show_cam' not in st.session_state:
    st.session_state.show_cam = False

ADMIN_PASSWORD = st.secrets.get("admin_password", "261197")
role = st.sidebar.radio("בחר תפקיד:", ["👷 עובד (דיווח)", "👨‍💼 מנהל (שליטה)"])

if role == "👷 עובד (דיווח)":
    st.header("דיווח על תקלה")
    worker_name = st.text_input("שם העובד המדווח")
    dept = st.selectbox("מחלקה", ["ייצור", "נוזלים גליל","פלסטיק","תדיראן","סלפונציה","סבון","מגבונים","קפסולות", "מחסן", "אריזה"])
    machine = st.text_input("מכונה / מיקום")
    urgency = st.selectbox("דחיפות", ["אפשר לחכות", "דחוף", "קריטי"])
    desc = st.text_area("תיאור התקלה")

    if st.button("📸 צילום תמונה"):
        st.session_state.show_cam = True
    
    pic = None
    if st.session_state.show_cam:
        pic = st.camera_input("צלם כאן")

    if st.button("🚀 שלח דיווח"):
        if machine and desc and worker_name:
            df = pd.read_csv(DATA_FILE)
            new_id = len(df) + 1
            time_now = datetime.now().strftime("%d/%m/%Y %H:%M")
            img_path = ""
            if pic:
                img_path = f"{IMAGE_FOLDER}/img_{new_id}.png"
                with open(img_path, "wb") as f:
                    f.write(pic.getbuffer())
            
            new_row = pd.DataFrame([{"מזהה": new_id, "ז
