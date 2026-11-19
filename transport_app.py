import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="ระบบขอใช้และจัดรถขนส่ง", layout="centered")
st.title("ระบบขอใช้และจัดรถขนส่งอัตโนมัติ")
st.caption("กรณีศึกษา: การปรับปรุงประสิทธิภาพการจัดรถขนส่ง (ลดเวลาและป้องกันการจัดรถผิดประเภท)")

# ฟังก์ชันประเมินประเภทรถอัตโนมัติตามขนาดและน้ำหนัก
def recommend_vehicle(weight_kg: float, length_m: float, width_m: float) -> str:
    if weight_kg <= 750 and length_m <= 2.2 and width_m <= 1.5:
        return "รถกระบะ"
    elif weight_kg <= 6000 and length_m <= 6.5 and width_m <= 2.3:
        return "รถ 6 ล้อ"
    else:
        return "รถเทรลเลอร์"

# สร้างฐานข้อมูลจำลองใน Session (เริ่มต้นด้วยตัวอย่างข้อมูลจากรายงาน)
if "records" not in st.session_state:
    st.session_state.records = [
        {"วันที่ขนส่ง": "2026-10-16", "รายละเอียดงาน (Job Details)": "รับแผ่นเหล็กร้าน S-tech (Bay ตัด)", "น้ำหนัก (กก.)": 70.1, "ยาว (ม.)": 1.22, "กว้าง (ม.)": 1.22, "ประเภทรถที่แนะนำ": "รถกระบะ", "สถานะ": "อนุมัติแล้ว"},
        {"วันที่ขนส่ง": "2026-10-25", "รายละเอียดงาน (Job Details)": "คืน Pipe 18 นิ้ว PAE จำนวน 1 เส้น", "น้ำหนัก (กก.)": 440.0, "ยาว (ม.)": 6.00, "กว้าง (ม.)": 0.46, "ประเภทรถที่แนะนำ": "รถ 6 ล้อ", "สถานะ": "อนุมัติแล้ว"},
        {"วันที่ขนส่ง": "2026-10-28", "รายละเอียดงาน (Job Details)": "ขนส่งท่ออุตสาหกรรมขนาดใหญ่", "น้ำหนัก (กก.)": 16000.0, "ยาว (ม.)": 9.00, "กว้าง (ม.)": 0.60, "ประเภทรถที่แนะนำ": "รถเทรลเลอร์", "สถานะ": "รออนุมัติ"},
    ]

tab1, tab2 = st.tabs(["1. ฟอร์มขอใช้รถ (หน้างานสแกน QR)", "2. ฐานข้อมูลและอนุมัติจัดรถ (เจ้าหน้าที่)"])

# --- แท็บที่ 1: ผู้ขอใช้บริการกรอกข้อมูล ---
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
                st.session_state.records.append({
                    "วันที่ขนส่ง": str(ship_date),
                    "รายละเอียดงาน (Job Details)": job_details,
                    "น้ำหนัก (กก.)": weight,
                    "ยาว (ม.)": length,
                    "กว้าง (ม.)": width,
                    "ประเภทรถที่แนะนำ": vehicle,
                    "สถานะ": "รออนุมัติ"
                })
                st.success(f"บันทึกข้อมูลสำเร็จ! ระบบประเมินประเภทรถที่เหมาะสมคือ: **{vehicle}**")

# --- แท็บที่ 2: เจ้าหน้าที่โลจิสติกส์ตรวจสอบและอนุมัติ ---
with tab2:
    st.subheader("รายการขอใช้รถแบบ Real-time")
    df = pd.DataFrame(st.session_state.records)
    st.dataframe(df, use_container_width=True)
    
    # ส่วนอนุมัติรายการที่รออนุมัติ
    pending_indices = [i for i, r in enumerate(st.session_state.records) if r["สถานะ"] == "รออนุมัติ"]
    if pending_indices:
        st.markdown("### ตรวจสอบและอนุมัติคำขอ")
        selected_idx = st.selectbox(
            "เลือกรายการที่ต้องการอนุมัติ",
            pending_indices,
            format_func=lambda i: f"#{i+1} | {st.session_state.records[i]['รายละเอียดงาน (Job Details)']} ({st.session_state.records[i]['ประเภทรถที่แนะนำ']})"
        )
        if st.button("อนุมัติและสั่งจัดรถ"):
            st.session_state.records[selected_idx]["สถานะ"] = "อนุมัติแล้ว"
            st.rerun()
            
    # ปุ่มดาวน์โหลดรายงานเป็น Excel
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("ดาวน์โหลดข้อมูลเป็นไฟล์ CSV / Excel", data=csv, file_name="transport_records.csv", mime="text/csv")
