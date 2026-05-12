import streamlit as st
import pandas as pd
import pdfplumber
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

st.title("🫀 FFR Report to Excel")
st.write("PDF 리포트들을 업로드하면 Sistolic/Diastolic 수치를 분류하여 엑셀로 만들어 드립니다.")

def extract_info(filename):
    match = re.search(r'(\d+)_(\d+)%', filename)
    return (match.group(1), int(match.group(2))) if match else (None, None)

def get_ffr_data(file):
    lad, lcx, rca = "", "", ""
    try:
        with pdfplumber.open(file) as pdf:
            # 2페이지 우선 탐색
            page = pdf.pages[1] if len(pdf.pages) > 1 else pdf.pages[0]
            text = page.extract_text()
            if text:
                lad_m = re.search(r'LAD\s*.*?(\d\.\d+)', text, re.S)
                lcx_m = re.search(r'LCX\s*.*?(\d\.\d+)', text, re.S)
                rca_m = re.search(r'RCA\s*.*?(\d\.\d+)', text, re.S)
                lad = lad_m.group(1) if lad_m else ""
                lcx = lcx_m.group(1) if lcx_m else ""
                rca = rca_m.group(1) if rca_m else ""
    except:
        pass
    return lad, lcx, rca

# 파일 업로드 섹션
uploaded_files = st.file_uploader("PDF 리포트 파일들을 선택하세요 (다중 선택 가능)", type="pdf", accept_multiple_files=True)

if uploaded_files:
    data_map = {}
    
    with st.spinner('리포트를 분석 중입니다...'):
        for uploaded_file in uploaded_files:
            pid, percent = extract_info(uploaded_file.name)
            if not pid: continue
            
            lad, lcx, rca = get_ffr_data(uploaded_file)
            
            if pid not in data_map:
                data_map[pid] = {'S': ["", "", ""], 'D': ["", "", ""]}
            
            if percent < 60:
                data_map[pid]['S'] = [lad, lcx, rca]
            else:
                data_map[pid]['D'] = [lad, lcx, rca]

    # 결과 데이터프레임 생성
    rows = []
    for pid in sorted(data_map.keys()):
        rows.append([pid] + data_map[pid]['S'] + data_map[pid]['D'])
    
    cols = ['ID', 'Sistolic LAD', 'Sistolic LCX', 'Sistolic RCA', 'Diastolic LAD', 'Diastolic LCX', 'Diastolic RCA']
    df = pd.DataFrame(rows, columns=cols)
    
    # 37행 맞추기
    if len(df) < 37:
        empty_df = pd.DataFrame([[""] * 7 for _ in range(37 - len(df))], columns=cols)
        df = pd.concat([df, empty_df], ignore_index=True)
    else:
        df = df.head(37)

    st.success(f"분석 완료! 총 {len(uploaded_files)}개의 파일이 처리되었습니다.")
    st.dataframe(df.head(10)) # 상위 10개 미리보기

    # 엑셀 다운로드 버튼
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='FFR_Data')
    
    st.download_button(
        label="📥 결과 엑셀 파일 다운로드",
        data=output.getvalue(),
        file_name="FFR_Analysis_Result.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
