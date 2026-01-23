import streamlit as st
import pandas as pd
import re
from io import BytesIO

# 페이지 설정 (각 파일마다 상단에 써줘야 합니다)
st.set_page_config(page_title="CACS Tool", page_icon="📊")

st.title("📊 CACS 데이터 추출 도구")

# --- 로직 부분 (VBA 변환 함수 등 동일하게 작성) ---
def clean_excel_data(df):
    """_x000D_ 이슈 해결을 위한 정제 함수"""
    return df.replace('_x000D_', '', regex=True)

def extract_cacs_number(text):

# --- [VBA 로직의 파이썬 구현] ---
def extract_cacs_number(text):
    if pd.isna(text):
        return "x"
    
    text = str(text)
    patterns = [
        "CACS", "ca scoring", "ca score:", "calcium scoring:", "calcium score:", 
        "calcium score ", "calc. score:", "calc. scoring", "ca score :", 
        "ca score ;", "ca. score", "ca. scoring", "ca socring;", "CCS"
    ]
    valid_status = ["pending", "none", "zero"]
    last_number = "x"

    for pattern in patterns:
        # 1. 패턴 위치 찾기 (대소문자 구분 없음)
        match = re.search(re.escape(pattern), text, re.IGNORECASE)
        if match:
            # 패턴 이후의 텍스트 한 줄만 가져오기
            start_pos = match.end()
            line = text[start_pos:].split('\n')[0].split('\r')[0]

            # 2. 특수문자 제거 (숫자, 점, 영문 외 공백 처리)
            clean_line = re.sub(r'[^A-Za-z0-9.]', ' ', line)
            words = clean_line.split()

            # 3. 단어별 순회하며 수치 추출
            for word in words:
                clean_word = word.strip().lower()
                
                # 끝에 마침표 제거 (숫자가 아닐 때만)
                if clean_word.endswith('.') and not re.match(r'^\d+\.\d+$', clean_word):
                    clean_word = clean_word[:-1]

                # (A) 숫자인 경우
                if re.match(r'^-?\d+(\.\d+)?$', clean_word):
                    last_number = clean_word
                # (B) 허용된 상태값인 경우
                elif clean_word in valid_status:
                    last_number = clean_word
                # (C) 핵심 방어 로직: 일반 단어를 만나면 중단
                elif len(clean_word) > 1:
                    if last_number != "x":
                        break
            
            if last_number != "x":
                break
                
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
