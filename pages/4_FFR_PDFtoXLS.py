import streamlit as st
import pandas as pd
import pytesseract
from pdf2image import convert_from_bytes
import re
import io

# 페이지 설정
st.set_page_config(page_title="FFR Report Analyzer", layout="wide")

st.title("🫀 FFR Report Analyzer (OCR 정밀 모드)")
st.info("2페이지에 위치한 이미지 형식의 수치를 정밀 분석합니다.")

def extract_ffr_data_ocr(file_bytes):
    lad, lcx, rca = "", "", ""
    try:
        # 2페이지(index 1)만 고해상도로 변환
        images = convert_from_bytes(file_bytes, dpi=300, first_page=2, last_page=2)
        if not images:
            # 2페이지가 없는 경우 1페이지 분석
            images = convert_from_bytes(file_bytes, dpi=300, first_page=1, last_page=1)
        
        if images:
            # OCR 실행
            page_text = pytesseract.image_to_string(images[0], lang='eng')

            # 정규표현식 함수
            def find_value(target, text):
                # 혈관명 뒤에 나타나는 첫 번째 0.xx 형식의 숫자 추출
                pattern = re.compile(rf'{target}.*?(\d\.\d{{2}})', re.S | re.I)
                match = pattern.search(text)
                return match.group(1) if match else ""

            lad = find_value("LAD", page_text)
            lcx = find_value("LCX", page_text)
            rca = find_value("RCA", page_text)

    except Exception as e:
        st.error(f"OCR 분석 중 오류: {e}")
    return lad, lcx, rca

uploaded_files = st.file_uploader("PDF 리포트들을 업로드하세요", type="pdf", accept_multiple_files=True)

if uploaded_files:
    data_map = {}
    total = len(uploaded_files)
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, f in enumerate(uploaded_files):
        status_text.text(f"분석 중: {f.name} ({i+1}/{total})")
        
        # 파일명에서 ID와 퍼센트 추출
        name_match = re.search(r'(\d+)_(\d+)%', f.name)
        if name_match:
            pid, percent = name_match.group(1), int(name_match.group(2))
            
            # f.read()를 하기 전 포인터 확인 및 읽기
            file_bytes = f.read()
            f.seek(0) # 다음 사용을 위해 포인터 초기화
            
            lad, lcx, rca = extract_ffr_data_ocr(file_bytes)
            
            if pid not in data_map:
                data_map[pid] = {'S': ["", "", ""], 'D': ["", "", ""]}
            
            # 60% 기준으로 Sistolic/Diastolic 분류
            if percent <= 60:
                data_map[pid]['S'] = [lad, lcx, rca]
            else:
                data_map[pid]['D'] = [lad, lcx, rca]
        
        progress_bar.progress((i + 1) / total)

    status_text.empty()

    # 데이터프레임 구성
    rows = []
    for pid in sorted(data_map.keys()):
        rows.append([pid] + data_map[pid]['S'] + data_map[pid]['D'])
    
    cols = ['ID', 'Sistolic LAD', 'Sistolic LCX', 'Sistolic RCA', 'Diastolic LAD', 'Diastolic LCX', 'Diastolic RCA']
    df = pd.DataFrame(rows, columns=cols)
    
    # 51행 맞추기 (요청하신 사항)
    if len(df) < 51:
        empty_rows = pd.DataFrame([[""] * 7] * (51 - len(df)), columns=cols)
        df = pd.concat([df, empty_rows], ignore_index=True)

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
