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

# אתחול מצב מצלמה - שלא תפתח לבד
if 'show_cam' not in st.session_state:
    st.session_state.show_cam = False

ADMIN_PASSWORD = st.secrets.get("admin_password", "2611")

role = st.sidebar.radio("תפקיד:", ["👷 עובד (דיווח)", "👨‍💼 מנהל (שליטה)"])

if role == "👷 עובד (דיווח)":
    st.header("דיווח על תקלה")
    
    # שדות הדיווח מחוץ לטופס כדי שהמצלמה תעבוד דינמית
    col1, col2 = st.columns(2)
    with col1:
        dept = st.selectbox("מחלקה", ["ייצור", "מחסן לוגסטי","נוזלים גליל","תדיראן","סבון","קפסולות","מגבונים", "אריזה", "פלסטיק"])
        machine = st.text_input("מכונה / מיקום")
    with col2:
        urgency = st.selectbox("דחיפות", ["אפשר לחכות", "דחוף", "קריטי"])
    
    desc = st.text_area("תיאור התקלה")

    # כפתור פתיחת מצלמה
    if st.button("📸 צירוף תמונה / וידאו"):
        st.session_state.show_cam = True

    pic = None
    if st.session_state.show_cam:
        pic = st.camera_input("צלם את התקלה")
        if st.button("ביטול צילום"):
            st.session_state.show_cam = False
            st.rerun()

    if st.button("🚀 שלח דיווח סופי"):
        if machine and desc:
            df = pd.read_csv(DATA_FILE)
            new_id = len(df) + 1
            time_now = datetime.now().strftime("%d/%m/%Y %H:%M")
            img_path = ""
            
            if pic:
                img_path = f"{IMAGE_FOLDER}/img_{new_id}.png"
                with open(img_path, "wb") as f:
                    f.write(pic.getbuffer())
            
            new_row = pd.DataFrame([{
                "מזהה": new_id, "זמן": time_now, "מחלקה": dept, "מכונה": machine,
                "תיאור": desc, "דחיפות": urgency, "סטטוס": "חדש", "הערת מנהל": "", "תמונה": img_path
            }])
            
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
            st.success(f"נשלח! מספר תקלה: {new_id}")
            st.session_state.show_cam = False # סגירת מצלמה אחרי שליחה
        else:
            st.error("נא למלא שדות חובה")

else:
    # --- חלק המנהל נשאר אותו דבר ---
    st.header("לוח בקרה למנהל")
    input_pw = st.sidebar.text_input("הכנס סיסמה", type="password")
    
    if input_pw == ADMIN_PASSWORD:
        df = pd.read_csv(DATA_FILE)
        tab = st.radio("סטטוס תצוגה:", ["תקלות פתוחות", "ארכיון"], horizontal=True)
        filtered = df[df["סטטוס"] != "טופל"] if tab == "תקלות פתוחות" else df[df["סטטוס"] == "טופל"]
        st.dataframe(filtered, use_container_width=True)
        
        st.divider()
        st.subheader("עדכון תקלה")
        u1, u2, u3 = st.columns(3)
        with u1:
            id_to_up = st.number_input("מזהה תקלה", min_value=1, step=1)
        with u2:
            new_status = st.selectbox("סטטוס", ["בביצוע", "טופל"])
        with u3:
            admin_note = st.text_input("הערה")
            
        if st.button("עדכן"):
            if id_to_up in df["מזהה"].values:
                df.loc[df["מזהה"] == id_to_up, "סטטוס"] = new_status
                df.loc[df["מזהה"] == id_to_up, "הערת מנהל"] = admin_note
                df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
                st.success("עודכן!")
                st.rerun()
        
        if id_to_up in df["מזהה"].values:
            img_file = df[df["מזהה"] == id_to_up]["תמונה"].values[0]
            if img_file and os.path.exists(str(img_file)):
                st.image(str(img_file), width=400)


