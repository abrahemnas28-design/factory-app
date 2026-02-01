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
    cols = ["id", "time", "worker", "dept", "machine", "description", "urgency", "status", "admin_note", "image"]
    pd.DataFrame(columns=cols).to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

def send_telegram_msg(worker, machine, desc, urgency):
    try:
        token = st.secrets["telegram_token"]
        chat_id = st.secrets["telegram_chat_id"]
        msg = f"⚠️ דיווח חדש!\n👤 עובד: {worker}\n🏗️ מכונה: {machine}\n🚨 דחיפות: {urgency}\n📝 תיאור: {desc}"
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": msg})
    except:
        pass

st.set_page_config(page_title="מערכת תקלות אברהים", layout="wide")
st.title("🛠️ :blue[מערכת ניהול תקלות]")

role = st.sidebar.radio("בחר תפקיד:", ["👷 עובד (דיווח)", "👨‍💼 מנהל (שליטה)"])

if role == "👷 עובד (דיווח)":
    st.header("דיווח על תקלה")
    w_name = st.text_input("שם העובד")
    w_dept = st.selectbox("מחלקה", ["ייצור", "נוזלים גליל", "פלסטיק", "תדיראן", "סלפונציה", "סבון", "מגבונים", "קפסולות", "מחסן", "אריזה"])
    w_mach = st.text_input("מכונה / מיקום")
    w_urg = st.selectbox("דחיפות", ["אפשר לחכות", "דחוף", "קריטי"])
    w_desc = st.text_area("תיאור התקלה")
    pic = st.camera_input("צלם תקלה (אופציונלי)")

    if st.button("🚀 שלח דיווח", use_container_width=True, type="primary"):
        if w_name and w_mach and w_desc:
            df = pd.read_csv(DATA_FILE)
            new_id = int(df["id"].max() + 1) if not df.empty else 1
            img_p = ""
            if pic:
                img_p = f"{IMAGE_FOLDER}/img_{new_id}.png"
                with open(img_p, "wb") as f:
                    f.write(pic.getbuffer())
            
            new_row = {"id": new_id, "time": datetime.now().strftime("%d/%m/%Y %H:%M"), "worker": w_name, "dept": w_dept, "machine": w_mach, "description": w_desc, "urgency": w_urg, "status": "חדש", "admin_note": "", "image": img_p}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
            send_telegram_msg(w_name, w_mach, w_desc, w_urg)
            st.success("✅ נשלח בהצלחה!")
            st.rerun()
        else:
            st.error("נא למלא שדות חובה")
else:
    st.header("ניהול")
    if st.sidebar.text_input("סיסמה", type="password") == st.secrets.get("admin_password", "1111"):
        df = pd.read_csv(DATA_FILE)
        st.dataframe(df, use_container_width=True)
        id_to_act = st.number_input("מספר תקלה לטיפול/מחיקה", min_value=1, step=1)
        if id_to_act in df["id"].values:
            if st.button("🗑️ מחק תקלה זו"):
                df = df[df["id"] != id_to_act]
                df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
                st.rerun()
