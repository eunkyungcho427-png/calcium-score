import streamlit as st
import pandas as pd
import re
from io import BytesIO

# 페이지 설정
st.set_page_config(page_title="CACS Tool", page_icon="📊", layout="wide")

# 홈으로 돌아가기 버튼 (사이드바 상단)
if st.sidebar.button("🏠 메인 화면으로 이동"):
    st.switch_page("app.py")

st.title("📊 CACS 데이터 추출 도구")
st.info("사이드바의 '메인 화면으로 이동' 버튼을 누르면 처음으로 돌아갑니다.")

# --- 로직 부분 (VBA 변환 함수 등 동일하게 작성) ---
def clean_excel_data(df):
    """_x000D_ 이슈 해결을 위한 정제 함수"""
    return df.replace('_x000D_', '', regex=True)

def extract_cacs_number(text):

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

# --- UI 부분 ---
st.set_page_config(page_title="CACS 데이터 추출기", layout="wide")
st.title("🏥 CACS(Calcium Score) 자동 추출 앱")
st.markdown("""
이 앱은 엑셀 파일 내의 텍스트에서 **CACS 수치**를 자동으로 분류하여 결과 파일을 만들어줍니다.
VBA의 복잡한 로직이 그대로 적용되어 있습니다.
""")


uploaded_file = st.file_uploader("분석할 엑셀 파일을 업로드하세요.", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    # 데이터 정제 (읽어오자마자 수행)
    df = clean_excel_data(df)
    
    col_name = st.selectbox("데이터 열 선택", df.columns)
    
    if st.button("분석 실행"):
        df['추출된_CACS'] = df[col_name].apply(extract_cacs_number)
        st.success("추출 완료!")
        st.dataframe(df.head())

            # 엑셀 다운로드 파일 생성
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Result')
            
            st.download_button(
                label="📥 분석 결과 엑셀 다운로드",
                data=output.getvalue(),
                file_name="CACS_Result.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
