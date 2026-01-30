import streamlit as st
import pandas as pd
import os
from datetime import datetime

# הגדרות קבצים
DATA_FILE = "factory_data.csv"
IMAGE_FOLDER = "fault_images"

if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["מזהה", "זמן", "מחלקה", "מכונה", "תיאור", "דחיפות", "סטטוס", "הערת מנהל", "תמונה"])
    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

st.set_page_config(page_title="מערכת תקלות - אברהים", layout="wide")
st.title("🛠️ ניהול תקלות המפעל")

# הגדרת סיסמה - מושך מה-Secrets של Streamlit או משתמש בברירת מחדל
# אם עדיין לא הגדרת Secrets, הסיסמה תהיה 1234
ADMIN_PASSWORD = st.secrets.get("admin_password", "1234")

role = st.sidebar.radio("תפקיד:", ["👷 עובד (דיווח)", "👨‍💼 מנהל (שליטה)"])

if role == "👷 עובד (דיווח)":
    st.header("דיווח על תקלה")
    with st.form("main_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            dept = st.selectbox("מחלקה", ["ייצור", "מחסן", "אריזה", "אחזקה"])
            machine = st.text_input("מכונה / מיקום")
        with col2:
            urgency = st.selectbox("דחיפות", ["אפשר לחכות", "דחוף", "קריטי"])
        
        desc = st.text_area("תיאור התקלה")
        
        # שינוי לבקשתך: המצלמה לא נפתחת אוטומטית
        add_photo = st.checkbox("📸 אני רוצה לצרף תמונה")
        pic = None
        if add_photo:
            pic = st.camera_input("צלם את התקלה")
        
        if st.form_submit_button("שלח דיווח"):
            if machine and desc:
                df = pd.read_csv(DATA_FILE)
                new_id = len(df) + 1
                time_now = datetime.now().strftime("%d/%m/%Y %H:%M")
                img_path = ""
                
                if pic:
                    img_path = f"{IMAGE_FOLDER}/img_{new_id}.png"
                    with open(img_path, "wb") as f:
                        f.write(pic.getbuffer())
                
                new_
