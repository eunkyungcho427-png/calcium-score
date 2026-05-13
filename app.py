import streamlit as st
import pandas as pd
import pytesseract
from pdf2image import convert_from_bytes
import re
import io
from PIL import Image, ImageOps

st.set_page_config(page_title="FFR Report Analyzer", layout="wide")
st.title("🫀 FFR Report Analyzer (이미지 수치 추출 모드)")

def extract_ffr_data_ocr(file_bytes):
    lad, lcx, rca = "", "", ""
    try:
        # 1. 고해상도 이미지 변환 (DPI를 300 이상으로 해야 숫자가 깨지지 않음)
        images = convert_from_bytes(file_bytes, dpi=350, first_page=2, last_page=2)
        if not images:
            images = convert_from_bytes(file_bytes, dpi=350, first_page=1, last_page=1)
        
        if images:
            img = images[0]
            # 2. 이미지 전처리: 흑백 전환 (OCR 인식률 대폭 상승)
            img = img.convert('L') 
            
            # 3. OCR 실행 (숫자와 영문 위주 설정)
            # config 설정: --psm 6 (가변적인 텍스트 블록 인식)
            page_text = pytesseract.image_to_string(img, lang='eng', config='--psm 6')

            # 4. 수치 추출 로직 (줄바꿈/공백 무시)
            def find_value(target, text):
                # 혈관명(LAD 등) 뒤에 나오는 0.xx 혹은 .xx 숫자를 찾음
                # [01]? : 0 또는 1이 있을 수도 없을 수도 있음 (OCR 오차 대비)
                # [\.,] : 점(.)을 콤마(,)로 오인해도 잡히게 함
                pattern = re.compile(rf'{target}.*?([01]?[\.,]\d{{2}})', re.S | re.I)
                match = pattern.search(text)
                if match:
                    val = match.group(1).replace(',', '.')
                    # 혹시 .85 처럼 앞에 0이 빠진 경우 보정
                    if val.startswith('.'): val = '0' + val
                    return val
                return ""

            lad = find_value("LAD", page_text)
            lcx = find_value("LCX", page_text)
            rca = find_value("RCA", page_text)

    except Exception as e:
        st.error(f"OCR 분석 중 오류: {e}")
    return lad, lcx, rca

uploaded_files = st.file_uploader("PDF 리포트를 업로드하세요", type="pdf", accept_multiple_files=True)

if uploaded_files:
    data_map = {}
    for f in uploaded_files:
        name_match = re.search(r'(\d+)_(\d+)%', f.name)
        if name_match:
            pid, percent = name_match.group(1), int(name_match.group(2))
            
            # 파일 읽기
            file_bytes = f.read()
            f.seek(0)
            
            lad, lcx, rca = extract_ffr_data_ocr(file_bytes)
            
            if pid not in data_map:
                data_map[pid] = {'S': ["", "", ""], 'D': ["", "", ""]}
            
            if percent <= 60:
                data_map[pid]['S'] = [lad, lcx, rca]
            else:
                data_map[pid]['D'] = [lad, lcx, rca]

    # 결과 출력 및 엑셀 생성 (기존 로직 동일)
    rows = [[pid] + data_map[pid]['S'] + data_map[pid]['D'] for pid in sorted(data_map.keys())]
    cols = ['ID', 'Sistolic LAD', 'Sistolic LCX', 'Sistolic RCA', 'Diastolic LAD', 'Diastolic LCX', 'Diastolic RCA']
    df = pd.DataFrame(rows, columns=cols)
    
    st.success("분석이 완료되었습니다!")
    st.dataframe(df)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    st.download_button("📥 엑셀 다운로드", output.getvalue(), "FFR_Result.xlsx")
