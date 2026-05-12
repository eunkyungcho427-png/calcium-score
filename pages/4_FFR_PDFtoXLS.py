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

# CSS로 UI 스타일링
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007BFF; color: white; }
    .stDownloadButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #28a745; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🫀 FFR Report Analyzer")
st.info("업로드한 PDF 리포트에서 LAD, LCX, RCA FFR 수치를 추출해서 엑셀 파일로 변환합니다.")

def extract_ffr_data_ocr(file_bytes):
    """
    이미지 형태의 PDF에서 OCR을 통해 LAD, LCX, RCA 수치를 추출하는 함수
    """
    lad, lcx, rca = "", "", ""
    try:
        # DPI를 300으로 높여 이미지 품질 확보
        images = convert_from_bytes(file_bytes, dpi=300)
        full_text = ""
        for img in images:
            # Tesseract OCR 실행
            text = pytesseract.image_to_string(img, lang='eng')
            full_text += text + "\n"

        # 수치 추출 로직 (유연한 정규표현식)
        def find_value(target, text):
            # target 단어 뒤에 오는 첫 번째 0.xx 형태의 숫자 추출
            pattern = re.compile(rf'{target}.*?(\d\.\d{{2}})', re.S | re.I)
            match = pattern.search(text)
            return match.group(1) if match else ""

        lad = find_value("LAD", full_text)
        lcx = find_value("LCX", full_text)
        rca = find_value("RCA", full_text)

    except Exception as e:
        st.error(f"OCR 분석 중 오류 발생: {e}")
    
    return lad, lcx, rca

# 파일 업로더
uploaded_files = st.file_uploader("PDF 리포트 파일들을 업로드하세요(최대 50개)", type="pdf", accept_multiple_files=True)

if uploaded_files:
    data_map = {}
    total_files = len(uploaded_files)
    
    # --- 진행 바 및 분석 상태 표시 추가 ---
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, f in enumerate(uploaded_files):
        # 현재 처리 중인 파일명 표시
        status_text.text(f"분석 중: {f.name} ({i+1}/{total_files})")
        
        # 파일명에서 ID와 퍼센트 추출
        name_match = re.search(r'(\d+)_(\d+)%', f.name)
        if name_match:
            pid, percent = name_match.group(1), int(name_match.group(2))
            
            # OCR 분석 실행
            lad, lcx, rca = extract_ffr_data_ocr(f.read())
            
            if pid not in data_map:
                data_map[pid] = {'S': ["", "", ""], 'D': ["", "", ""]}
            
            # 퍼센트 기준 분류 (60% 미만은 Sistolic, 이상은 Diastolic)
            if percent < 60:
                data_map[pid]['S'] = [lad, lcx, rca]
            else:
                data_map[pid]['D'] = [lad, lcx, rca]
        
        # 진행 바 업데이트
        progress_bar.progress((i + 1) / total_files)
    
    # 분석 완료 후 상태 메시지 삭제
    status_text.empty()
    # ------------------------------------

    # 데이터프레임 구성
    rows = []
    for pid in sorted(data_map.keys()):
        rows.append([pid] + data_map[pid]['S'] + data_map[pid]['D'])
    
    cols = ['ID', 'Sistolic LAD', 'Sistolic LCX', 'Sistolic RCA', 'Diastolic LAD', 'Diastolic LCX', 'Diastolic RCA']
    df = pd.DataFrame(rows, columns=cols)
    
    # 요청하신 행 수(51행) 맞추기
    if len(df) < 51:
        empty_needed = 51 - len(df)
        empty = pd.DataFrame([[""] * 7] * empty_needed, columns=cols)
        df = pd.concat([df, empty], ignore_index=True)

    st.success(f"총 {total_files}개의 파일 분석이 완료되었습니다!")
    st.dataframe(df, use_container_width=True)

    # 엑셀 변환 및 다운로드 버튼
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button(
        label="📥 결과 엑셀 다운로드",
        data=output.getvalue(),
        file_name="FFR_Analysis_Result.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
