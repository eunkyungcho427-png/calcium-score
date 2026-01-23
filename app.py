import streamlit as st

# 페이지 설정
st.set_page_config(page_title="Medical AI Workspace", page_icon="🏥", layout="wide")

# CSS로 Medical Clean 스타일 적용 (모든 페이지 공통으로 넣는 것이 좋습니다)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    h1 { color: #1e3a8a; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 Medical AI 업무 자동화 시스템")
st.write("---")

st.subheader("환영합니다! 원하시는 도구를 선택하세요.")
st.info("왼쪽 사이드바 메뉴에서 사용할 툴을 클릭해 주세요.")

# 대문 디자인 (선택 사항)
col1, col2 = st.columns(2)
with col1:
    st.success("#### 1️⃣ CACS 데이터 추출기\n판독문에서 칼슘 스코어를 자동 추출합니다.")
with col2:
    st.warning("#### 2️⃣ 업데이트 예정\n새로운 AI 도구가 준비 중입니다.")
