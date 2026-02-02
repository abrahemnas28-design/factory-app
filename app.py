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

# יצירת קובץ אם לא קיים
cols = ["id", "time", "worker", "dept", "machine", "description", "urgency", "status", "admin_note", "image"]
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=cols)
    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

# --- 1. מערכת הגנה וכניסה (Login) ---
# הסיסמה תימשך מה-Secrets או תהיה ברירת מחדל
SITE_PASSWORD = st.secrets.get("site_password", "1234") 

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 כניסה למערכת המפעל")
    pw = st.text_input("הכנס סיסמת גישה", type="password")
    if st.button("כניסה"):
        if pw == SITE_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("סיסמה שגויה")
    st.stop() # עוצר כאן למי שלא התחבר

# --- 2. פונקציות עזר ---
def send_telegram_msg(worker, machine, desc, urgency):
    try:
        token = st.secrets["telegram_token"]
        chat_id = st.secrets["telegram_chat_id"]
        message = f"⚠️ דיווח חדש!\n👤 עובד: {worker}\n🏗️ מכונה: {machine}\n🚨 דחיפות: {urgency}\n📝 תיאור: {desc}"
        url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
        requests.get(url)
    except:
        pass

# הגדרות דף
st.set_page_config(page_title="מערכת תקלות - אברהים", layout="wide")
st.title("🛠️ :blue[ניהול תקלות המפעל]")

if 'show_cam' not in st.session_state:
    st.session_state.show_cam = False

ADMIN_PASSWORD = st.secrets.get("admin_password", "1111")
role = st.sidebar.radio("בחר תפקיד:", ["👷 עובד (דיווח)", "👨‍💼 מנהל (שליטה)"])

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
            st.error("⚠️ נא למלא את כל השדות")
else:
    st.header("לוח בקרה למנהל")
    input_pw = st.sidebar.text_input("הכנס סיסמה", type="password")
    
    if input_pw == ADMIN_PASSWORD:
        df = pd.read_csv(DATA_FILE)
        tab = st.radio("תצוגה:", ["תקלות פתוחות", "ארכיון"], horizontal=True)
        
        # --- תיקון השגיאה מהתמונות: לוגיקת ארכיון תקינה ---
        archive_statuses = ["טופל", "ביצוע חלקי"]
        
        if tab == "תקלות פתוחות":
            view_df = df[~df["status"].isin(archive_statuses)]
        else:
            view_df = df[df["status"].isin(archive_statuses)]
        
        st.dataframe(view_df.rename(columns=hebrew_columns), use_container_width=True)

        st.divider()
        st.subheader("⚙️ עדכון תקלה")
        
        col_act, col_img = st.columns([1, 1])
        with col_act:
            id_to_act = st.number_input("הזן מזהה תקלה (ID)", min_value=1, step=1)
            # הוספת "ביצוע חלקי" לאפשרויות
            new_status = st.selectbox("שינוי סטטוס:", ["בביצוע", "טופל", "ביצוע חלקי"])
            a_note = st.text_input("הערת מנהל")
            
            if st.button("✅ שמור עדכון"):
                if id_to_act in df["id"].values:
                    df.loc[df["id"] == id_to_act, "status"] = new_status
                    df.loc[df["id"] == id_to_act, "admin_note"] = a_note
                    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
                    st.rerun()

        with col_img:
            if id_to_act in df["id"].values:
                img_path = df.loc[df["id"] == id_to_act, "image"].values[0]
                if pd.notna(img_path) and img_path != "" and os.path.exists(str(img_path)):
                    st.image(str(img_path))
