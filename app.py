import streamlit as st

# 사이드바에서 툴 선택
tool = st.sidebar.selectbox("사용할 툴을 선택하세요", ["CACS 추출기", "환자 요약 비서", "데이터 통계"])

if tool == "CACS 추출기":
    st.header("🏥 CACS 데이터 추출기")
    # 여기에 CACS 관련 코드 작성
    
elif tool == "환자 요약 비서":
    st.header("📝 제미나이 환자 요약")
    # 여기에 제미나이 API 연동 코드 작성
