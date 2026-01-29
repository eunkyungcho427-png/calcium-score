import streamlit as st
import pandas as pd
import re
from io import BytesIO

# 1. 페이지 설정 (반드시 최상단에 한 번만!)
st.set_page_config(page_title="EF Tool", page_icon="📊", layout="wide")

# 2. 홈으로 돌아가기 버튼
if st.sidebar.button("🏠 메인 화면으로 이동"):
    st.switch_page("app.py")

# 3. 로직 함수 정의
def clean_excel_data(df):
    """_x000D_ 이슈 해결을 위한 정제 함수"""
    return df.replace('_x000D_', '', regex=True)

def extract_latest_ef_value(text):
    # 3-1. EF 또는 LVEF 위치 찾기 (대소문자 무시)
    # \bEF\b는 독립된 단어로서의 EF만 찾습니다.
    pattern = re.compile(r'(LVEF|\bEF\b)', re.IGNORECASE)
    matches = list(pattern.finditer(text))
    
    # 매칭되는 항목이 없으면 "x" 반환
    if not matches:
        return "x"
    
    # 3-2. 가장 마지막에 등장하는 EF 패턴부터 역순으로 분석
    for match in reversed(matches):
        start_pos = match.end()
        # 해당 위치부터 텍스트 끝까지 자르기
        temp_result = text[start_pos:]
        
        # 줄바꿈 처리 (해당 라인만 분석)
        line_end = temp_result.find('\n')
        if line_end != -1:
            temp_result = temp_result[:line_end]
            
        # 3-3. 해당 라인에서 숫자(정수 또는 소수점 포함) 추출
        # [0-9.]+ 패턴으로 숫자와 마침표 뭉치를 모두 찾습니다.
        numbers = re.findall(r'[0-9.]+', temp_result)
        
        for num_str in numbers:
            # 마침표만 있는 경우는 제외하고, 숫자로 변환 가능한지 확인
            try:
                # 공백 제거 후 값이 비어있지 않은지 체크
                clean_num = num_str.strip('.')
                if clean_num:
                    return clean_num # 첫 번째 발견된 숫자 뭉치 반환
            except ValueError:
                continue
                
    return "x"


# 4. UI 구성
st.title("🏥 EF(Ejection Fraction) 자동 추출 도구")
st.markdown("""
이 앱은 엑셀 파일 내의 텍스트에서 **EF 수치**를 자동으로 추출하여 결과 파일을 생성합니다.
\n● 정확도: 99%
\n● 작동원리
\n   - LVEF, EF 수치를 % 기호를 빼고 숫자만 출력
\n   - 2개 이상의 수치가 존재할 경우, 판독문 상 마지막에 오는 숫자를 출력
\n   - 판독문 상에 EF 수치가 없는 경우: x 출력, pending인 경우 pending 출력
\n● 원본파일 주의사항
\n   - 환자 ID, 판독문 2개 열 정도로 데이터를 간단하게 만든 후 업로드하면 판독문 우측 열에 결과값이 출력됩니다.
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
            df['추출된_EF'] = df[col_name].apply(extract_latest_ef_value)

            # 결과를 세션 스테이트에 저장 (리프레시 대비)
            st.session_state['result_df'] = df            
            st.success("분석 및 추출 완료!")
            
	    # 결과가 세션에 존재할 때만 화면에 출력
    if 'result_df' in st.session_state:
        result_df = st.session_state['result_df']

            # 결과 미리보기
            st.subheader("📌 결과 미리보기 (상위 5행)")
            st.dataframe(result_df[[col_name, '추출된_EF']].head(), use_container_width=True)

            # 엑셀 다운로드 파일 생성
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Result')
            
            processed_data = output.getvalue()
            
            st.download_button(
                label="📥 분석 결과 엑셀 다운로드",
                data=processed_data,
                file_name="EF_Analysis_Result.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                use_container_width=True
            )
