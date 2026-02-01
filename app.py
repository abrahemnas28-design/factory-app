import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime

# הגדרות קבצים - שמות פנימיים באנגלית למניעת שגיאות
DATA_FILE = "factory_data.csv"
IMAGE_FOLDER = "fault_images"

if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

# יצירת קובץ עם שמות עמודות
cols = ["id", "time", "worker", "dept", "machine", "description", "urgency", "status", "admin_note", "image"]
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=cols)
    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

def send_telegram_msg(worker, machine, desc, urgency):
    try:
        # שליכה מה-Secrets של Streamlit
        token = st.secrets["telegram_token"]
        chat_id = st.secrets["telegram_chat_id"]
        
        message = f"⚠️ דיווח חדש!\n👤 עובד: {worker}\n🏗️ מכונה: {machine}\n🚨 דחיפות: {urgency}\n📝 תיאור: {desc}"
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        requests.post(url, data=payload)
    except Exception as e:
        st.sidebar.error(f"שגיאת טלגרם: {e}")

st.set_page_config(page_title="מערכת תקלות - אברהים", layout="wide")
st.title("🛠️ :blue[ניהול תקלות המפעל - אברהים]")

if 'show_cam' not in st.session_state:
    st.session_state.show_cam = False

ADMIN_PASSWORD = st.secrets.get("admin_password", "1111")
role = st.sidebar.radio("בחר תפקיד:", ["👷 עובד (דיווח)", "👨‍💼 מנהל (שליטה)"])

# מיפוי שמות עמודות לתצוגה בעברית
hebrew_columns = {
    "id": "מזהה", "time": "זמן", "worker": "שם העובד", "dept": "מחלקה",
    "machine": "מכונה", "description": "תיאור", "urgency": "דחיפות",
    "status": "סטטוס", "admin_note": "הערת מנהל", "image": "תמונה"
}

if role == "👷 עובד (דיווח)":
    st.header("דיווח על תקלה")
    w_name = st.text_input("שם העובד המדווח")
    w_dept = st.selectbox("מחלקה", ["ייצור", "נוזלים גליל", "פלסטיק", "תדיראן", "סלפונציה", "סבון", "מגבונים", "קפסולות", "מחסן", "אריזה"])
    w_mach = st.text_input("מכונה / מיקום")
    w_urg = st.selectbox("דחיפות", ["אפשר לחכות", "דחוף", "קריטי"])
    w_desc = st.text_area("תיאור התקלה")

    if st.button("📸 צילום תמונה", use_container_width=True):
        st.session
