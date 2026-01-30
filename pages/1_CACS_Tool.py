import streamlit as st
import pandas as pd
import re
from io import BytesIO

# 1. 페이지 설정 (반드시 최상단에 한 번만!)
st.set_page_config(page_title="CACS Tool", page_icon="📊", layout="wide")

# 2. 홈으로 돌아가기 버튼
if st.sidebar.button("🏠 메인 화면으로 이동"):
    st.switch_page("app.py")

# 3. 로직 함수 정의
def clean_excel_data(df):
    """_x000D_ 이슈 해결을 위한 정제 함수"""
    return df.replace('_x000D_', '', regex=True)

def extract_cacs_number(text):
    if pd.isna(text): return "x"
    text = str(text)
    # VBA 로직을 반영한 패턴들
    patterns = ["CACS", "ca scoring", "ca score:", "calcium scoring:", "calcium score:", "calcium score ", "calc. score:", "calc. scoring", "ca score :", "ca score ;", "ca. score", "ca. scoring", "ca socring;", "CCS"]
    valid_status = ["pending", "none", "zero"]
    last_number = "x"

    for pattern in patterns:
        match = re.search(re.escape(pattern), text, re.IGNORECASE)
        if match:
            start_pos = match.end()
            # 한 줄만 추출
            line = text[start_pos:].split('\n')[0].split('\r')[0]
            # 특수문자 제거
            clean_line = re.sub(r'[^A-Za-z0-9.]', ' ', line)
            words = clean_line.split()
            for word in words:
                clean_word = word.strip().lower()
                # 숫자 판별
                if re.match(r'^-?\d+(\.\d+)?$', clean_word):
                    last_number = clean_word
                # 허용 상태 판별
                elif clean_word in valid_status:
                    last_number = clean_word
                # 방어 로직: 일반 단어를 만나면 중단
                elif len(clean_word) > 1:
                    if last_number != "x": break
            if last_number != "x": break
    return last_number

# 4. UI 구성
st.title("🏥 CACS(Calcium Score) 자동 추출 도구")
st.markdown("""
이 앱은 엑셀 파일 내의 텍스트에서 **CACS 수치**를 자동으로 추출하여 결과 파일을 생성합니다.
VBA의 복잡한 로직이 파이썬 엔진으로 구현되어 있습니다.

● **정확도**: 97%\n
● **작동원리**\n
- CACS, calcium score 등 다양한 표현의 수치를 % 기호 제외하고 출력\n
- Calcium Score: 37.00 -> 41.45 인 경우, 41.45 를 출력\n
- 판독문 상에 수치가 없는 경우: x 출력, pending인 경우 pending 출력\n
● **원본파일 주의사항**\n
- 환자 ID, 판독문 열 정도로 데이터를 구성해 업로드해 주세요.
""")

uploaded_file = st.file_uploader("분석할 엑셀 파일을 업로드하세요.", type=["xlsx"])

if uploaded_file:
    # 엑셀 읽기
    df = pd.read_excel(uploaded_file)
    # 데이터 정제 (_x000D_ 제거)
    df = clean_excel_data(df)
    
    col_name = st.selectbox("데이터가 포함된 열(Column)을 선택하세요", df.columns)
    
    if st.button("분석 실행"):
        with st.spinner('데이터를 분석 중입니다...'):
            # 분석 실행
            df['추출된_CACS'] = df[col_name].apply(extract_cacs_number)
            
            st.success("분석 및 추출 완료!")
            
            # 결과 미리보기
            st.subheader("📌 결과 미리보기 (상위 5행)")
            st.dataframe(df[[col_name, '추출된_CACS']].head())

            # 엑셀 다운로드 파일 생성
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Result')
            
            processed_data = output.getvalue()
            
            st.download_button(
                label="📥 분석 결과 엑셀 다운로드",
                data=processed_data,
                file_name="CACS_Analysis_Result.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
