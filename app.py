import streamlit as st

# 1. 페이지 설정
st.set_page_config(page_title="Medical AI Workspace", page_icon="🏥", layout="wide")

# 2. 디자인 (CSS) 적용
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    h1 { color: #1e3a8a; font-family: 'Segoe UI', sans-serif; }
    .tool-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 메인 헤더
# st.title("🏥 Medical AI 업무 자동화 포털")
st.write("사용하고자 하는 도구를 사이드바에서 선택하거나 아래 버튼을 클릭하세요.")
st.divider()

# 4. 툴 선택 구역 (버튼 방식)
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        <div class="tool-card">
            <h3>📊 CACS 데이터 추출기</h3>
            <p>엑셀 판독문에서 CACS(Calcium Score)수치를 자동으로 정밀 추출하고 정제합니다.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 수정된 버튼 부분
    if st.button("CACS 도구 실행하기", key="btn_move", use_container_width=True):
        try:
            # 경로에 'pages/'를 반드시 포함해야 합니다.
            st.switch_page("pages/1_CACS_Tool.py")
        except Exception as e:
            st.error("페이지를 찾을 수 없습니다. 파일이 'pages' 폴더 안에 있는지 확인해주세요.")

with col2:
    st.markdown("""
        <div class="tool-card">
            <h3>📊 EF 데이터 추출기</h3>
            <p>엑셀 판독문에서 EF(Ejection Fraction)수치를 자동으로 정밀 추출하고 정제합니다.</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("EF 도구 실행하기", key="btn_move", use_container_width=True):
        try:
            # 경로에 'pages/'를 반드시 포함해야 합니다.
            st.switch_page("pages/2_EF_Tool.py")
        except Exception as e:
            st.error("페이지를 찾을 수 없습니다. 파일이 'pages' 폴더 안에 있는지 확인해주세요.")


# 5. 하단 안내
st.divider()
st.caption("© 2026 Created by Cho Eunkyung from Seoul National University Bundang Hospital | 문의: eunkyungcho427@gmail.com")
