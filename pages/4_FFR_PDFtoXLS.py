import streamlit as st
import pandas as pd
import pytesseract
from pdf2image import convert_from_bytes
import re
import io

# 1. 페이지 설정
st.set_page_config(page_title="FFR Report Analyzer", layout="centered")

# CSS 스타일링
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007BFF; color: white; }
    .stDownloadButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #28a745; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🫀 FFR Report Analyzer")
st.info("이미지로 된 2페이지의 수치를 OCR로 정밀 분석합니다.")

def extract_ffr_data_ocr(file_bytes):
    lad, lcx, rca = "", "", ""
    try:
        # [최적화] 2페이지(index 1)만 이미지로 변환하여 속도와 메모리 절약
        # 만약 1페이지만 있는 파일일 경우를 대비해 예외처리 포함
        images = convert_from_bytes(file_bytes, dpi=300, first_page=2, last_page=2)
        if not images: # 2페이지가 없는 경우 1페이지라도 분석
            images = convert_from_bytes(file_bytes, dpi=300, first_page=1, last_page=1)
        
        # OCR 실행 (이미지 품질이 중요하므로 DPI 300 유지)
        page_text = pytesseract.image_to_string(images[0], lang='eng')

        # 수치 추출 함수: 혈관명 뒤에 나타나는 0.xx 형태의 숫자를 추적
        def find_value(target, text):
            # re.S (점 부호가 줄바꿈 포함), re.I (대소문자 무시)
            # 혈관명(target) 뒤에 어떤 문자가 오든 상관없이 가장 먼저 나오는 0.xx 숫자를 찾음
            pattern = re.compile(rf'{target}.*?(\d\.\d{{2}})', re.S | re.I)
            match = pattern.search(text)
            return match.group(1) if match else ""

        lad = find_value("LAD", page_text)
        lcx = find_value("LCX", page_text)
        rca = find_value("RCA", page_text)

        # (선택 사항) 디버깅용: OCR이 읽은 텍스트를 보고 싶다면 주석 해제
        # st.text(page_text)

    except Exception as e:
        st.error(f"OCR 분석 중 오류: {e}")
    return lad, lcx, rca

uploaded_files = st.file_uploader("PDF 리포트 파일들을 업로드하세요 (파일명 형식: ID_00%.pdf, 최대 50개)", type="pdf", accept_multiple_files=True)

if uploaded_files:
    data_map = {}
    total = len(uploaded_files)
    
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, f in enumerate(uploaded_files):
        status_text.text(f"분석 중: {f.name} ({i+1}/{total})")
        
        # 파일명에서 ID와 퍼센트 추출 (기존 로직 유지)
        name_match = re.search(r'(\d+)_(\d+)%', f.name)
        if name_match:
            pid, percent = name_match.group(1), int(name_match.group(2))
            
            # 파일 데이터 읽기 (OCR 함수 호출)
            lad, lcx, rca = extract_ffr_data_ocr(f.read())
            
            if pid not in data_map:
                data_map[pid] = {'S': ["", "", ""], 'D': ["", "", ""]}
            
            # 60% 기준으로 Sistolic/Diastolic 분류
            if percent < 60:
                data_map[pid]['S'] = [lad, lcx, rca]
            else:
                data_map[pid]['D'] = [lad, lcx, rca]
        
        progress_bar.progress((i + 1) / total)

    status_text.empty()

    # 데이터프레임 생성
    rows = []
    for pid in sorted(data_map.keys()):
        rows.append([pid] + data_map[pid]['S'] + data_map[pid]['D'])
    
    cols = ['ID', 'Sistolic LAD', 'Sistolic LCX', 'Sistolic RCA', 'Diastolic LAD', 'Diastolic LCX', 'Diastolic RCA']
    df = pd.DataFrame(rows, columns=cols)
    
    # 51행 맞추기
    if len(df) < 51:
        empty = pd.DataFrame([[""]*7]*(51-len(df)), columns=cols)
        df = pd.concat([df, empty], ignore_index=True)

    st.success("모든 파일의 OCR 분석이 완료되었습니다.")
    st.dataframe(df, use_container_width=True)

    # 엑셀 다운로드
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button(label="📥 결과 엑셀 다운로드", data=output.getvalue(), 
                       file_name="FFR_OCR_Report.xlsx", 
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
