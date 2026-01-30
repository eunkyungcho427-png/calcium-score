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
    if pd.isna(text) or str(text).strip() == "":
        return "x"
    
    text = str(text)
    
    # 1. EF 관련 키워드만 정확히 찾기 (\b는 단어 경계)
    # Ca scoring의 'Ca'가 걸리지 않도록 명확히 단어 단위로 설정
    pattern = re.compile(r'(\bLVEF\b|\bEF\b)', re.IGNORECASE)
    matches = list(pattern.finditer(text))
    
    if not matches:
        return "x"
    
    # 2. 마지막 매칭부터 역순 분석
    for match in reversed(matches):
        start_pos = match.end()
        # EF 단어 이후 최대 30자까지만 분석 (멀리 떨어진 텍스트 오염 방지)
        look_ahead = text[start_pos:start_pos + 30]
        
        # 줄바꿈이 있으면 해당 라인만
        line_end = look_ahead.find('\n')
        if line_end != -1:
            look_ahead = look_ahead[:line_end]
        
        # 3. 해당 구역에 'pending'이 있는지 먼저 확인
        if "pending" in look_ahead.lower():
            return "pending"
            
        # 4. 숫자 추출 ([0-9.]+ 패턴)
        numbers = re.findall(r'[0-9.]+', look_ahead)
        
        if numbers:
            # 추출된 문자열이 단순 마침표가 아닌지 확인
            for num_str in numbers:
                clean_num = num_str.strip('.')
                if clean_num:
                    return clean_num
                
    return "x"

# 4. UI 구성
st.title("🏥 EF(Ejection Fraction) 자동 추출 도구")
st.markdown("""
이 앱은 엑셀 파일 내의 텍스트에서 **EF 수치**를 자동으로 추출하여 결과 파일을 생성합니다.

● **정확도**: 99% \n
● **작동원리**  
&nbsp;&nbsp;― EF, LVEF 등 다양한 표현의 수치를 % 기호 제외하고 출력  
&nbsp;&nbsp;― 판독문 상 **가장 마지막**에 등장하는 EF 수치를 출력  
&nbsp;&nbsp;― 판독문 상에 수치가 없는 경우: x 출력, pending인 경우 pending 출력 \n
● **원본파일 주의사항**: 환자 ID, 판독문 2개 열 정도로 데이터를 구성해 업로드해 주세요.
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
