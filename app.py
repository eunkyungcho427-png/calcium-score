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
st.title("🏥 Medical AI 업무 자동화 포털")
st.write("사용하고자 하는 도구를 사이드바에서 선택하거나 아래 버튼을 클릭하세요.")
st.divider()

# 4. 툴 선택 구역 (버튼 방식)
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        <div class="tool-card">
            <h3>📊 CACS 데이터 추출기</h3>
            <p>엑셀 판독문에서 Calcium Score를 자동으로 정밀 추출하고 정제합니다.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 버튼 클릭 시 페이지 이동 (파일명과 경로가 정확해야 합니다)
    if st.button("CACS 도구 실행하기", key="btn_cacs", use_container_width=True):
        try:
            # 경로를 명확히 지정 (pages/파일명)
            st.switch_page("calcium/pages/1_CACS_Tool.py")
        except Exception as e:
            st.error(f"페이지 이동 중 오류가 발생했습니다. 파일명을 확인해 주세요.")
            st.info("현재 설정된 경로: pages/1_CACS_Tool.py")


with col2:
    st.markdown("""
        <div class="tool-card">
            <h3>🤖 AI 소견서 요약 (준비 중)</h3>
            <p>Gemini AI를 활용하여 복잡한 판독문을 한 줄로 요약합니다.</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("준비 중...", key="btn_ai", disabled=True, use_container_width=True):
        pass

# 5. 하단 안내
st.divider()
st.caption("© 2024 Medical Data Automation Team | 문의: 내선번호 0000")
