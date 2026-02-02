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

# יצירת קובץ עם שמות עמודות באנגלית (התצוגה תהיה בעברית)
cols = ["id", "time", "worker", "dept", "machine", "description", "urgency", "status", "admin_note", "image"]
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=cols)
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
st.title("🛠️ :blue[ניהול תקלות המפעל]")

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
    w_dept = st.selectbox("מחלקה", ["ייצור", "נוזלים גליל","פלסטיק","תדיראן","סלפונציה","סבון","מגבונים","קפסולות", "מחסן", "אריזה"])
    w_mach = st.text_input("מכונה / מיקום")
    w_urg = st.selectbox("דחיפות", ["אפשר לחכות", "דחוף", "קריטי"])
    w_desc = st.text_area("תיאור התקלה")

    if st.button("📸 צילום תמונה", use_container_width=True):
        st.session_state.show_cam = True
    
    pic = None
    if st.session_state.show_cam:
        pic = st.camera_input("צלם כאן")

    # שים לב: הכפתור הזה חייב להתחיל באותו קו של ה-if שמעליו
    if st.button("🚀 שלח דיווח", use_container_width=True, type="primary"):
        if w_mach and w_desc and w_name:
            df = pd.read_csv(DATA_FILE)
            new_id = int(df["id"].max() + 1) if not df.empty else 1
            time_now = datetime.now().strftime("%d/%m/%Y %H:%M")
            img_p = ""
            if pic:
                img_p = f"{IMAGE_FOLDER}/img_{new_id}.png"
                with open(img_p, "wb") as f:
                    f.write(pic.getbuffer())
            
            new_row = pd.DataFrame([{"id": new_id, "time": time_now, "worker": w_name, "dept": w_dept, "machine": w_mach, "description": w_desc, "urgency": w_urg, "status": "חדש", "admin_note": "", "image": img_p}])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
            send_telegram_msg(w_name, w_mach, w_desc, w_urg)
            st.session_state.show_cam = False
            st.success("✅ הדיווח נשלח בהצלחה!")
            st.rerun()
        else:
            st.error("⚠️ נא למלא את כל השדות (שם, מכונה ותיאור)")
else:
    st.header("לוח בקרה למנהל")
    input_pw = st.sidebar.text_input("הכנס סיסמה", type="password")
    
    if input_pw == ADMIN_PASSWORD:
        df = pd.read_csv(DATA_FILE)
        tab = st.radio("תצוגה:", ["תקלות פתוחות", "ארכיון"], horizontal=True)
        
        view_df = df[df["status"] != "טופל","ביצוע חלקי"] if tab == "תקלות פתוחות" else df[df["status"] == "טופל","ביצוע חלקי"]
        
        # הצגת הטבלה עם שמות בעברית
        st.dataframe(view_df.rename(columns=hebrew_columns), use_container_width=True)

        st.divider()
        st.subheader("⚙️ עדכון תקלה וצפייה בתמונה")
        
        col_act, col_img = st.columns([1, 1])
        
        with col_act:
            id_to_act = st.number_input("הזן מזהה תקלה (ID)", min_value=1, step=1)
            new_status = st.selectbox("שינוי סטטוס:", ["בביצוע", "ביצוע חלקי" , "טופל"])
            a_note = st.text_input("הערת מנהל")
            
            if st.button("✅ שמור עדכון"):
                if id_to_act in df["id"].values:
                    df.loc[df["id"] == id_to_act, "status"] = new_status
                    df.loc[df["id"] == id_to_act, "admin_note"] = a_note
                    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
                    st.rerun()
            
            if tab == "ארכיון" and st.button("🗑️ מחק לצמיתות"):
                df = df[df["id"] != id_to_act]
                df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
                st.rerun()

        with col_img:
            if id_to_act in df["id"].values:
                img_path = df.loc[df["id"] == id_to_act, "image"].values[0]
                if pd.notna(img_path) and img_path != "" and os.path.exists(str(img_path)):
                    st.image(str(img_path), caption=f"תמונה עבור מזהה {id_to_act}")
                else:
                    st.info("אין תמונה לתקלה זו")




