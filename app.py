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
    dept = st.selectbox("מחלקה", ["ייצור", "מחסן", "אריזה", "אחזקה"])
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
            img_path = f"{IMAGE_FOLDER}/img_{new_id}.png" if pic else ""
            if pic:
                with open(img_path, "wb") as f:
                    f.write(pic.getbuffer())
            
            new_row = pd.DataFrame([{"מזהה": new_id, "זמן": time_now, "שם העובד": worker_name, "מחלקה": dept, "מכונה": machine, "תיאור": desc, "דחיפות": urgency, "סטטוס": "חדש", "הערת מנהל": "", "תמונה": img_path}])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
            send_telegram_msg(worker_name, machine, desc, urgency)
            st.session_state.show_cam = False
            st.rerun()
        else:
            st.error("נא למלא שם, מכונה ותיאור")

else:
    st.header("לוח בקרה למנהל")
    input_pw = st.sidebar.text_input("הכנס סיסמה", type="password")
    
    if input_pw == ADMIN_PASSWORD:
        df = pd.read_csv(DATA_FILE)
        tab = st.radio("תצוגה:", ["תקלות פתוחות", "ארכיון"], horizontal=True)
        
        view_df = df[df["סטטוס"] != "טופל"] if tab == "תקלות פתוחות" else df[df["סטטוס"] == "טופל"]
        st.dataframe(view_df, use_container_width=True)

        st.divider()
        st.subheader("⚙️ פעולות מנהל")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            id_to_act = st.number_input("מזהה תקלה (ID)", min_value=1, step=1)
        with col2:
            new_status = st.selectbox("שינוי סטטוס ל:", ["בביצוע", "טופל"])
        with col3:
            admin_note = st.text_input("הערת מנהל")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ עדכן סטטוס והערה", use_container_width=True):
                if id_to_act in df["מזהה"].values:
                    df.loc[df["מזהה"] == id_to_act, "סטטוס"] = new_status
                    df.loc[df["מזהה"] == id_to_act, "הערת מנהל"] = admin_note
                    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
                    st.rerun()
        with c2:
            if tab == "ארכיון":
                if st.button("🗑️ מחק תקלה לצמיתות", use_container_width=True):
                    df = df[df["מזהה"] != id_to_act]
                    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
                    st.rerun()
    else:
        st.info("נא להזין סיסמה נכונה כדי לראות נתונים")

