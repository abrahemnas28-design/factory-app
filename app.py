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

# פונקציה לשליחת הודעה לטלגרם
def send_telegram_msg(worker, machine, desc, urgency):
    token = st.secrets["telegram_token"]
    chat_id = st.secrets["telegram_chat_id"]
    text = f"⚠️ *דיווח על תקלה חדשה*\n\n👤 *עובד:* {worker}\n🏗️ *מכונה:* {machine}\n🚨 *דחיפות:* {urgency}\n📝 *תיאור:* {desc}"
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}&parse_mode=Markdown"
    requests.get(url)

st.set_page_config(page_title="מערכת תקלות - אברהים", layout="wide")
st.title("🛠️ ניהול תקלות המפעל")

if 'show_cam' not in st.session_state:
    st.session_state.show_cam = False

ADMIN_PASSWORD = st.secrets.get("admin_password", "1234")
role = st.sidebar.radio("תפקיד:", ["👷 עובד (דיווח)", "👨‍💼 מנהל (שליטה)"])

if role == "👷 עובד (דיווח)":
    st.header("דיווח על תקלה")
    
    worker_name = st.text_input("שם העובד המדווח")
    dept = st.selectbox("מחלקה", ["ייצור", "מחסן", "אריזה", "אחזקה"])
    machine = st.text_input("מכונה / מיקום")
    urgency = st.selectbox("דחיפות", ["אפשר לחכות", "דחוף", "קריטי"])
    desc = st.text_area("תיאור התקלה")

    if st.button("📸 צירוף תמונה"):
        st.session_state.show_cam = True

    pic = None
    if st.session_state.show_cam:
        pic = st.camera_input("צלם את התקלה")

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
            
            new_row = pd.DataFrame([{
                "מזהה": new_id, "זמן": time_now, "שם העובד": worker_name, "מחלקה": dept, 
                "מכונה": machine, "תיאור": desc, "דחיפות": urgency, "סטטוס": "חדש", 
                "הערת מנהל": "", "תמונה": img_path
            }])
            
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
            
            # שליחת ההתראה לטלגרם
            try:
                send_telegram_msg(worker_name, machine, desc, urgency)
            except:
                pass
            
            st.session_state.show_cam = False
            st.rerun() 
        else:
            st.error("נא למלא את כל השדות")
else:
    # --- חלק מנהל נשאר אותו דבר ---
    st.header("לוח בקרה למנהל")
    input_pw = st.sidebar.text_input("הכנס סיסמה", type="password")
    if input_pw == ADMIN_PASSWORD:
        df = pd.read_csv(DATA_FILE)
        tab = st.radio("סטטוס:", ["תקלות פתוחות", "ארכיון"])
        filtered = df[df["סטטוס"] != "טופל"] if tab == "תקלות פתוחות" else df[df["סטטוס"] == "טופל"]
        st.dataframe(filtered, use_container_width=True)
        
        # מחיקה מארכיון
        if tab == "ארכיון":
            id_to_del = st.number_input("מזהה למחיקה", min_value=1, step=1)
            if st.button("🗑️ מחק לצמיתות"):
                df = df[df["מזהה"] != id_to_del]
                df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
                st.rerun()
