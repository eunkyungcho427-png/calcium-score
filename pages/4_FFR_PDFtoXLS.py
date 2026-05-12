import streamlit as st
import pandas as pd
import pytesseract
from pdf2image import convert_from_bytes
import re
import io

st.set_page_config(page_title="FFR Report Analyzer", layout="wide")

st.title("🫀 FFR Report Analyzer (OCR 개선 버전)")

# 디버깅용 옵션
debug_mode = st.checkbox("OCR 추출 원문 보기 (수치가 안 나올 때 체크)")

def extract_ffr_data_ocr(file_bytes):
    lad, lcx, rca = "", "", ""
    try:
        # 300 DPI로 고해상도 변환
        images = convert_from_bytes(file_bytes, dpi=300, first_page=2, last_page=2)
        if not images:
            images = convert_from_bytes(file_bytes, dpi=300, first_page=1, last_page=1)
        
        if images:
            # OCR 실행
            page_text = pytesseract.image_to_string(images[0], lang='eng')
            
            if debug_mode:
                with st.expander("OCR 원문 데이터 확인"):
                    st.text(page_text)

            # [개선된 매칭 로직] 
            # 1. 텍스트에서 불필요한 줄바꿈을 공백으로 치환
            clean_text = re.sub(r'\s+', ' ', page_text)

            def find_value(target, text):
                # target(LAD 등) 뒤에 오는 가장 가까운 0.xx 또는 .xx 형태의 숫자 찾기
                # 숫자가 인식 오류로 'O'로 찍히는 경우 등을 고려해 패턴 유연화
                pattern = re.compile(rf'{target}.*?([01][\.,]\d{{2}})', re.I)
                match = pattern.search(text)
                if match:
                    val = match.group(1).replace(',', '.') # 콤마를 점으로 교체
                    return val
                return ""

            lad = find_value("LAD", clean_text)
            lcx = find_value("LCX", clean_text)
            rca = find_value("RCA", clean_text)

    except Exception as e:
        st.error(f"OCR 분석 중 오류: {e}")
    return lad, lcx, rca

uploaded_files = st.file_uploader("PDF 리포트들을 업로드하세요", type="pdf", accept_multiple_files=True)

if uploaded_files:
    data_map = {}
    total = len(uploaded_files)
    progress_bar = st.progress(0)

    for i, f in enumerate(uploaded_files):
        # 파일명 분석
        name_match = re.search(r'(\d+)_(\d+)%', f.name)
        if name_match:
            pid, percent = name_match.group(1), int(name_match.group(2))
            
            file_bytes = f.read()
            f.seek(0)
            
            lad, lcx, rca = extract_ffr_data_ocr(file_bytes)
            
            if pid not in data_map:
                data_map[pid] = {'S': ["", "", ""], 'D': ["", "", ""]}
            
            if percent <= 60:
                data_map[pid]['S'] = [lad, lcx, rca]
            else:
                data_map[pid]['D'] = [lad, lcx, rca]
        
        progress_bar.progress((i + 1) / total)

    # 결과 표 생성
    rows = []
    for pid in sorted(data_map.keys()):
        rows.append([pid] + data_map[pid]['S'] + data_map[pid]['D'])
    
    cols = ['ID', 'Sistolic LAD', 'Sistolic LCX', 'Sistolic RCA', 'Diastolic LAD', 'Diastolic LCX', 'Diastolic RCA']
    df = pd.DataFrame(rows, columns=cols)
    
    st.success("분석 완료!")
    st.dataframe(df)

    # 엑셀 다운로드
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button(
        label="📥 결과 엑셀 다운로드",
        data=output.getvalue(),
        file_name="FFR_Result.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
