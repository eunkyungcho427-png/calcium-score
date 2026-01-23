import streamlit as st
import pandas as pd
import re
from io import BytesIO

# --- [디자인: Medical Clean CSS 적용] ---
st.set_page_config(page_title="CACS Analyzer", page_icon="🏥", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        background-color: #007bff;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    h1 { color: #1e3a8a; font-family: 'Segoe UI', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- [핵심 로직: VBA 변환 함수] ---
def extract_cacs_number(text):
    if pd.isna(text): return "x"
    text = str(text)
    patterns = ["CACS", "ca scoring", "ca score:", "calcium scoring:", "calcium score:", "CCS"]
    valid_status = ["pending", "none", "zero"]
    last_number = "x"

    for pattern in patterns:
        match = re.search(re.escape(pattern), text, re.IGNORECASE)
        if match:
            start_pos = match.end()
            line = text[start_pos:].split('\n')[0].split('\r')[0]
            clean_line = re.sub(r'[^A-Za-z0-9.]', ' ', line)
            words = clean_line.split()
            for word in words:
                clean_word = word.strip().lower()
                if re.match(r'^-?\d+(\.\d+)?$', clean_word):
                    last_number = clean_word
                elif clean_word in valid_status:
                    last_number = clean_word
                elif len(clean_word) > 1:
                    if last_number != "x": break
            if last_number != "x": break
    return last_number

# --- [화면 구성] ---
# 1. 사이드바 (설정 및 정보)
with st.sidebar:
    st.title("🏥 Medical 분석툴 by 조은경")
    st.info("이 도구는 의료 결과지에서 CACS 데이터를 정밀하게 추출합니다.")
    st.divider()
    st.caption("Version 1.0.0 | Contact: Admin")

# 2. 메인 헤더
st.title("Coronary Artery Calcium Score Analyzer")
st.write("안전한 데이터 처리를 위해 파일을 업로드해 주세요.")

# 3. 파일 업로드 구역
upload_card = st.container()
with upload_card:
    uploaded_file = st.file_uploader("엑셀 파일을 드래그하여 놓으세요 (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    # 분석 설정
    col_name = st.selectbox("분석할 텍스트 열(Column)을 선택하세요.", df.columns)
    
    if st.button("데이터 정밀 분석 시작"):
        # 프로그레스 바 시각화
        progress_bar = st.progress(0)
        df['추출된_CACS'] = df[col_name].apply(extract_cacs_number)
        progress_bar.progress(100)

        # 분석 요약 지표 (Metrics)
        st.divider()
        m1, m2, m3 = st.columns(3)
        total = len(df)
        success = len(df[df['추출된_CACS'] != 'x'])
        
        m1.metric("총 처리 건수", f"{total}건")
        m2.metric("데이터 추출 성공", f"{success}건")
        m3.metric("성공률", f"{(success/total)*100:.1f}%")

        # 결과 테이블
        st.subheader("📋 분석 결과 데이터")
        st.dataframe(df[[col_name, '추출된_CACS']].head(20), use_container_width=True)

        # 다운로드 버튼
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        
        st.download_button(
            label="📥 분석 완료 파일 다운로드 (Excel)",
            data=output.getvalue(),
            file_name="CACS_Analysis_Result.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.success("분석이 성공적으로 완료되었습니다!")
