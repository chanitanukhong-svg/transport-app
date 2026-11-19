import streamlit as st
import pandas as pd
import requests
from datetime import date

st.set_page_config(page_title="ระบบขอใช้และจัดรถขนส่ง", layout="centered")

# วางลิงก์ Web App URL จาก Google Apps Script ตรงนี้
SHEET_API_URL = "https://script.google.com/macros/s/AKfycbxP5hOphVhr-931T4hU2ahUr8PynwJooel4Jm7Q5fvw4DMWEMMv8DiH0iuFVefTv6NSbg/exec"

st.title("ระบบขอใช้และจัดรถขนส่งอัตโนมัติ")
st.caption("กรณีศึกษา: การปรับปรุงประสิทธิภาพการจัดรถขนส่ง")

def recommend_vehicle(weight_kg: float, length_m: float, width_m: float) -> str:
    if weight_kg <= 750 and length_m <= 2.2 and width_m <= 1.5:
        return "รถกระบะ"
    elif weight_kg <= 6000 and length_m <= 6.5 and width_m <= 2.3:
        return "รถ 6 ล้อ"
    else:
        return "รถเทรลเลอร์"

def load_data():
    try:
        res = requests.get(SHEET_API_URL, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []

tab1, tab2 = st.tabs(["1. ฟอร์มขอใช้รถ (หน้างานสแกน QR)", "2. ฐานข้อมูลและอนุมัติจัดรถ (เจ้าหน้าที่)"])

with tab1:
    st.subheader("แบบฟอร์มขอข้อมูลการขนส่ง")
    with st.form("request_form", clear_on_submit=True):
        ship_date = st.date_input("วันที่ต้องการขนส่ง", value=date.today())
        job_details = st.text_input("รายละเอียดงาน / ชื่อสินค้า (Job Details)", placeholder="เช่น รับ Plate 15 mm. จำนวน 5 แผ่น")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            weight = st.number_input("น้ำหนักสินค้ารวม (กก.)", min_value=0.1, value=100.0, step=10.0)
        with col2:
            length = st.number_input("ความยาวสินค้า (เมตร)", min_value=0.1, value=1.2, step=0.1)
        with col3:
            width = st.number_input("ความกว้างสินค้า (เมตร)", min_value=0.1, value=1.0, step=0.1)
            
        submitted = st.form_submit_button("ส่งคำขอใช้รถขนส่ง")
        
        if submitted:
            if not job_details.strip():
                st.warning("กรุณากรอกรายละเอียดงานหรือชื่อสินค้า")
            else:
                vehicle = recommend_vehicle(weight, length, width)
                payload = {
                    "action": "add",
                    "ship_date": str(ship_date),
                    "job_details": job_details,
                    "weight": weight,
                    "length": length,
                    "width": width,
                    "vehicle": vehicle
                }
                with st.spinner("กำลังส่งข้อมูลไปยังเจ้าหน้าที่..."):
                    res = requests.post(SHEET_API_URL, json=payload, timeout=10)
                if res.status_code == 200:
                    st.success(f"ส่งข้อมูลสำเร็จ! ระบบประเมินประเภทรถที่เหมาะสมคือ: **{vehicle}**")
                else:
                    st.error("เกิดข้อผิดพลาดในการส่งข้อมูล กรุณาลองใหม่")

with tab2:
    st.subheader("ส่วนสำหรับเจ้าหน้าที่โลจิสติกส์")
    pin = st.text_input("กรอกรหัสผ่านเจ้าหน้าที่เพื่อเข้าดูและอนุมัติจัดรถ", type="password", placeholder="กรอกรหัสผ่าน...")
    
    if pin == "1234":
        if st.button("รีเฟรชข้อมูลล่าสุด"):
            st.rerun()
            
        records = load_data()
        if records:
            df = pd.DataFrame(records).drop(columns=["row"], errors="ignore")
            st.dataframe(df, use_container_width=True)
            
            pending = [r for r in records if r.get("สถานะ") == "รออนุมัติ"]
            if pending:
                st.markdown("### ตรวจสอบและอนุมัติคำขอ")
                selected_item = st.selectbox(
                    "เลือกรายการที่ต้องการอนุมัติ",
                    pending,
                    format_func=lambda r: f"แถวที่ {r['row']} | {r['รายละเอียดงาน (Job Details)']} ({r['ประเภทรถที่แนะนำ']})"
                )
                if st.button("อนุมัติและสั่งจัดรถ"):
                    with st.spinner("กำลังบันทึกการอนุมัติ..."):
                        requests.post(SHEET_API_URL, json={"action": "approve", "row": selected_item["row"]}, timeout=10)
                    st.success("อนุมัติจัดรถเรียบร้อยแล้ว!")
                    st.rerun()
            else:
                st.info("ไม่มีรายการที่รออนุมัติในขณะนี้")
                
            csv = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button("ดาวน์โหลดข้อมูลเป็นไฟล์ CSV / Excel", data=csv, file_name="transport_records.csv", mime="text/csv")
        else:
            st.info("ยังไม่มีข้อมูลการขอใช้รถในระบบ")
    elif pin != "":
        st.error("รหัสผ่านไม่ถูกต้อง")
