import streamlit as st
import pandas as pd
import pytesseract
from pdf2image import convert_from_bytes
import re
import io

# 1. 페이지 설정 (반드시 최상단에 한 번만!)
st.set_page_config(page_title="FFR Report Analyzer", layout="centered")

# 2. 홈으로 돌아가기 버튼
if st.sidebar.button("🏠 메인 화면으로 이동"):
    st.switch_page("app.py")

# CSS로 UI 스타일링 (Calcium Score 앱 느낌)
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007BFF; color: white; }
    .stDownloadButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #28a745; color: white; }
    </style>
    """, unsafe_allow_html=True)


st.title("🫀 FFR Report Analyzer")
st.info("업로드한 PDF리포트에서 LAD, LCX, RCA FFR 수치를 추출해서 엑셀 파일로 변환합니다.")

def extract_ffr_data_ocr(file_bytes):
    lad, lcx, rca = "", "", ""
    try:
        # PDF를 이미지로 변환 (300 DPI 권장)
        images = convert_from_bytes(file_bytes, dpi=300)
        full_text = ""
        for img in images:
            text = pytesseract.image_to_string(img, lang='eng')
            full_text += text + "\n"

        # 수치 추출 (유연한 정규표현식 적용)
        lad_m = re.search(r'LAD\s*.*?(\d\.\d{2})', full_text, re.S | re.I)
        lcx_m = re.search(r'LCX\s*.*?(\d\.\d{2})', full_text, re.S | re.I)
        rca_m = re.search(r'RCA\s*.*?(\d\.\d{2})', full_text, re.S | re.I)

        lad = lad_m.group(1) if lad_m else ""
        lcx = lcx_m.group(1) if lcx_m else ""
        rca = rca_m.group(1) if rca_m else ""
    except Exception as e:
        st.error(f"OCR 처리 중 오류: {e}")
    return lad, lcx, rca

uploaded_files = st.file_uploader("PDF 리포트 파일들을 업로드하세요(최대50개)", type="pdf", accept_multiple_files=True)

if uploaded_files:
    data_map = {}
    for f in uploaded_files:
        name_match = re.search(r'(\d+)_(\d+)%', f.name)
        if name_match:
            pid, percent = name_match.group(1), int(name_match.group(2))
            lad, lcx, rca = extract_ffr_data_ocr(f.read())
            
            if pid not in data_map:
                data_map[pid] = {'S': ["", "", ""], 'D': ["", "", ""]}
            
            if percent < 60:
                data_map[pid]['S'] = [lad, lcx, rca]
            else:
                data_map[pid]['D'] = [lad, lcx, rca]

    rows = []
    for pid in sorted(data_map.keys()):
        rows.append([pid] + data_map[pid]['S'] + data_map[pid]['D'])
    
    cols = ['ID', 'Sistolic LAD', 'Sistolic LCX', 'Sistolic RCA', 'Diastolic LAD', 'Diastolic LCX', 'Diastolic RCA']
    df = pd.DataFrame(rows, columns=cols)
    
    # 51행 맞추기
    if len(df) < 51:
        empty = pd.DataFrame([[""]*7]*(37-len(df)), columns=cols)
        df = pd.concat([df, empty], ignore_index=True)

    st.success("분석이 완료되었습니다.")
    st.dataframe(df, use_container_width=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button(label="📥 결과 엑셀 다운로드", data=output.getvalue(), 
                       file_name="FFR_Analysis.xlsx", 
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
