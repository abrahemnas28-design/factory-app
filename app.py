import streamlit as st
import pandas as pd
import os
from datetime import datetime

# הגדרות נתונים ותיקיית תמונות
DATA_FILE = "factory_data.csv"
IMAGE_FOLDER = "fault_images"

if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["מזהה", "זמן", "מחלקה", "מכונה", "תיאור", "דחיפות", "סטטוס", "הערת מנהל", "תמונה"])
    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

st.set_page_config(page_title="ניהול תקלות - מפעל", layout="wide")
st.title("🛠️ מערכת דיווח ובקרת תקלות")

role = st.sidebar.radio("בחר תפקיד:", ["👷 עובד (דיווח)", "👨‍💼 מנהל (שליטה)"])

if role == "👷 עובד (דיווח)":
    st.header("דיווח על תקלה חדשה")
    with st.form("worker_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            dept = st.selectbox("מחלקה", ["ייצור", "פלסטיק","מחסן לוגסטי", "אריזה", "נוזלים גליל", "תדיראן","בישול","סבון","מגבונים","קפסולות"])
            machine = st.text_input("שם המכונה / אזור")
        with col2:
            urgency = st.select_slider("רמת דחיפות", options=["אפשר לחכות", "דחוף", "קריטי"])
        
        description = st.text_area("תיאור התקלה")
        picture = st.camera_input("צלם תמונה של התקלה")
        
        submitted = st.form_submit_button("שלח דיווח")
        
        if submitted:
            if machine and description:
                df = pd.read_csv(DATA_FILE)
                new_id = len(df) + 1
                now = datetime.now().strftime("%d/%m/%Y %H:%M")
                img_path = ""
                
                if picture:
                    img_path = f"{IMAGE_FOLDER}/fault_{new_id}.png"
                    with open(img_path, "wb") as f:
                        f.write(picture.getbuffer())
                
                new_entry = {
                    "מזהה": new_id, "זמן": now, "מחלקה": dept, "מכונה": machine,
                    "תיאור": description, "דחיפות": urgency, "סטטוס": "חדש",
                    "הערת מנהל": "", "תמונה": img_path
                }
                
                df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
                st.success(f"נשלח! מספר תקלה: {new_id}")
            else:
                st.error("נא למלא מכונה ותיאור")

else:
    st.header("לוח בקרה למנהל")
    pw = st.sidebar.text_input("סיסמה", type="password")
    if pw == "1234":
        df = pd.read_csv(DATA_FILE)
        view = st.radio("הצג:", ["פתוחות", "ארכיון"], horizontal=True)
        
        display_df = df[df["סטטוס"] != "טופל"] if view == "פתוחות" else df[df["סטטוס"] == "טופל"]
        st.dataframe(display_df, use_container_width=True)
        
        st.divider()
        col_up1, col_up2, col_up3 = st.columns(3)
        with col_up1:
            id_edit = st.number_input("מזהה תקלה", min_value=1, step=1)
        with col_up2:
            new_stat = st.selectbox("סטטוס חדש", ["חדש", "בביצוע", "טופל"])
        with col_up3:
            note = st.text_input("הערת מנהל")
            
        if st.button("עדכן"):
            df.loc[df["מזהה"] == id_edit, "סטטוס"] = new_stat
            df.loc[df["מזהה"] == id_edit, "הערת מנהל"] = note
            df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
            st.success("עודכן!")
            st.rerun()
            
        # הצגת תמונה אם קיימת
        if id_edit in df["מזהה"].values:
            row = df[df["מזהה"] == id_edit].iloc[0]
            if pd.notna(row["תמונה"]) and row["תמונה"] != "":
                st.image(row["תמונה"], caption=f"תמונה מתקלה {id_edit}", width=400)