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
    df = pd.DataFrame(columns=["מזהה", "זמן", "שם העובד", "מחלקה", "מכונה", "תיאור", "דחיפות", "סטטוס", "הערת מנהל", "תמונה"])
    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

st.set_page_config(page_title="מערכת תקלות - אברהים", layout="wide")
st.title("🛠️ ניהול תקלות המפעל")

if 'show_cam' not in st.session_state:
    st.session_state.show_cam = False

ADMIN_PASSWORD = st.secrets.get("admin_password", "1234")

role = st.sidebar.radio("תפקיד:", ["👷 עובד (דיווח)", "👨‍💼 מנהל (שליטה)"])

if role == "👷 עובד (דיווח)":
    st.header("דיווח על תקלה")
    
    col_name, col_dept = st.columns(2)
    with col_name:
        worker_name = st.text_input("שם העובד המדווח") # 2. הוספת שם
    with col_dept:
        dept = st.selectbox("מחלקה", ["ייצור", "מחסן", "אריזה", "אחזקה"])
        
    col_mach, col_urg = st.columns(2)
    with col_mach:
        machine = st.text_input("מכונה / מיקום")
    with col_urg:
        urgency = st.selectbox("דחיפות", ["אפשר לחכות", "דחוף", "קריטי"])
    
    desc = st.text_area("תיאור התקלה")

    if st.button("📸 צירוף תמונה / וידאו"):
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
            
            # 1. כאן אפשר להוסיף קוד לשליחת מייל/התראה
            # 3. במקום הודעה ירוקה - פשוט מרעננים
            st.session_state.show_cam = False
            st.rerun() 
        else:
            st.error("נא למלא את כל השדות (כולל שם)")

else:
    st.header("לוח בקרה למנהל")
    input_pw = st.sidebar.text_input("הכנס סיסמה", type="password")
    
    if input_pw == ADMIN_PASSWORD:
        df = pd.read_csv(DATA_FILE)
        tab = st.radio("סטטוס תצוגה:", ["תקלות פתוחות", "ארכיון"], horizontal=True)
        
        if tab == "תקלות פתוחות":
            filtered = df[df["סטטוס"] != "טופל"]
            st.dataframe(filtered, use_container_width=True)
        else:
            filtered = df[df["סטטוס"] == "טופל"]
            st.dataframe(filtered, use_container_width=True)
            
            # 4. כפתור מחיקה מהארכיון
            st.divider()
            id_to_del = st.number_input("מזהה תקלה למחיקה סופית מהארכיון", min_value=1, step=1)
            if st.button("🗑️ מחק תקלה לצמיתות"):
                df = df[df["מזהה"] != id_to_del]
                df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
                st.warning(f"תקלה {id_to_del} נמחקה מהמערכת")
                st.rerun()

        st.divider()
        st.subheader("עדכון סטטוס (לתקלות פתוחות)")
        u1, u2, u3 = st.columns(3)
        with u1: id_to_up = st.number_input("מזהה תקלה לעדכון", min_value=1, step=1)
        with u2: new_status = st.selectbox("סטטוס חדש", ["בביצוע", "טופל"])
        with u3: admin_note = st.text_input("הערת מנהל")
            
        if st.button("בצע עדכון"):
            if id_to_up in df["מזהה"].values:
                df.loc[df["מזהה"] == id_to_up, "סטטוס"] = new_status
                df.loc[df["מזהה"] == id_to_up, "הערת מנהל"] = admin_note
                df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
                st.rerun()
