import streamlit as st
import pandas as pd
import re
from io import BytesIO

# 1. 페이지 설정
st.set_page_config(page_title="EF Tool", page_icon="📊", layout="wide")

# 2. 홈으로 돌아가기 버튼
if st.sidebar.button("🏠 메인 화면으로 이동"):
    st.switch_page("app.py")

# 3. 로직 함수 정의
def clean_excel_data(df):
    """_x000D_ 이슈 해결 및 결측치 처리"""
    return df.replace('_x000D_', '', regex=True).fillna('')

def extract_latest_ef_value(text):
    text = str(text)
    # 3-0. pending 처리
    if "pending" in text.lower():
        return "pending"
        
    # 3-1. EF 또는 LVEF 위치 찾기
    pattern = re.compile(r'(LVEF|\bEF\b)', re.IGNORECASE)
    matches = list(pattern.finditer(text))
    
    if not matches:
        return "x"
    
    # 3-2. 가장 마지막에 등장하는 패턴부터 역순 분석
    for match in reversed(matches):
        start_pos = match.end()
        temp_result = text[start_pos:]
        
        # 줄바꿈 처리 (해당 라인만 분석)
        line_end = temp_result.find('\n')
        if line_end != -1:
            temp_result = temp_result[:line_end]
            
        # 숫자 추출
        numbers = re.findall(r'[0-9.]+', temp_result)
        
        for num_str in numbers:
            clean_num = num_str.strip('.')
            if clean_num:
                return clean_num # 발견 즉시 반환
                
    return "x"

# 4. UI 구성
st.title("🏥 EF(Ejection Fraction) 자동 추출 도구")
st.markdown("""
이 앱은 엑셀 파일 내의 텍스트에서 **EF 수치**를 자동으로 추출합니다.
* **작동원리**: 판독문 상 **가장 마지막**에 등장하는 EF 수치를 추출합니다.
* **출력값**: 수치가 없으면 `x`, pending 상태면 `pending`을 출력합니다.
""")

uploaded_file = st.file_uploader("분석할 엑셀 파일을 업로드하세요.", type=["xlsx"])

if uploaded_file:
    # 엑셀 읽기 및 정제
    df_raw = pd.read_excel(uploaded_file)
    df = clean_excel_data(df_raw)
    
    col_name = st.selectbox("데이터가 포함된 열(Column)을 선택하세요", df.columns)
    
    if st.button("🚀 분석 실행", use_container_width=True):
        with st.spinner('데이터를 분석 중입니다...'):
            # 분석 실행 및 결과 저장
            df['추출된_EF'] = df[col_name].apply(extract_latest_ef_value)
            st.session_state['result_df'] = df
            st.success("분석 완료!")

    # 결과가 세션에 존재할 때만 화면에 출력 (들여쓰기 주의)
    if 'result_df' in st.session_state:
        result_df = st.session_state['result_df']
        
        st.divider()
        st.subheader("📌 결과 미리보기 (상위 5행)")
        st.dataframe(result_df[[col_name, '추출된_EF']].head(), use_container_width=True)

        # 엑셀 다운로드 파일 생성
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            result_df.to_excel(writer, index=False, sheet_name='Result')
        
        processed_data = output.getvalue()
        
        st.download_button(
            label="📥 분석 결과 엑셀 다운로드",
            data=processed_data,
            file_name="EF_Analysis_Result.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
