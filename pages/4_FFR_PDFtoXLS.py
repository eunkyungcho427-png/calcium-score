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
        # DPI를 300으로 높여 인식률 향상
        images = convert_from_bytes(file_bytes, dpi=300)
        full_text = ""
        for img in images:
            # 글자 인식을 더 정확하게 하기 위해 --psm 6 옵션 추가 가능
            text = pytesseract.image_to_string(img, lang='eng')
            full_text += text + "\n"

        # 수치 추출 로직 강화 (숫자 앞뒤 공백 및 줄바꿈 허용)
        # 예: "LAD"와 "0.67" 사이의 모든 텍스트 무시하고 첫 번째 소수점 숫자 찾기
        def find_value(target, text):
            # target 뒤에 오는 0.xx 형태의 숫자 매칭
            pattern = re.compile(rf'{target}.*?(\d\.\d{{2}})', re.S | re.I)
            match = pattern.search(text)
            return match.group(1) if match else ""

        lad = find_value("LAD", full_text) # [cite: 23, 24]
        lcx = find_value("LCX", full_text) # [cite: 23, 27]
        rca = find_value("RCA", full_text) # [cite: 25, 26]

        # 디버깅용: 텍스트가 아예 안 읽히는지 확인하고 싶다면 아래 주석 해제
        # st.write(full_text) 

    except Exception as e:
        st.error(f"오류 발생: {e}")
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
