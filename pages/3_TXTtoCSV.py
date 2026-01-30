import streamlit as st
import pandas as pd
import io
import zipfile

st.set_page_config(page_title="TXT to CSV Multi-Downloader", layout="centered")

st.title("📂 TXT → CSV 맞춤 변환기")

# 1. 파일 업로드 (상단)
uploaded_files = st.file_uploader("TXT 파일을 선택하세요", type=['txt'], accept_multiple_files=True)

st.divider()

# 2. 변환 옵션 선택 (스크롤다운)
mode = st.selectbox(
    "변환 옵션을 선택하세요",
    ("탭 구조 유지 (원본 형식 보존)", "2열 추출 (항목명과 값만 정리)"),
    index=0
)

# 세션 상태(session_state) 초기화
if 'converted_files' not in st.session_state:
    st.session_state.converted_files = []

# 변환 실행 버튼
if st.button("선택한 옵션으로 변환 리스트에 추가"):
    if uploaded_files:
        for uploaded_file in uploaded_files:
            content = uploaded_file.read().decode('cp949', errors='ignore')
            uploaded_file.seek(0)
            lines = content.splitlines()
            base_name = uploaded_file.name.rsplit('.', 1)[0]
            
            if mode == "탭 구조 유지 (원본 형식 보존)":
                all_rows = [line.split('\t') for line in lines]
                df = pd.DataFrame(all_rows)
                suffix = "_structure"
                header_option = False
                color = "info"
            else:
                extracted_data = []
                for line in lines:
                    parts = [p.strip() for p in line.split('\t') if p.strip()]
                    if len(parts) >= 2:
                        name = " ".join(parts[:-1])
                        value = parts[-1]
                        extracted_data.append([name, value])
                df = pd.DataFrame(extracted_data, columns=['Feature_Name', 'Value'])
                suffix = "_2cols"
                header_option = True
                color = "success"

            new_filename = f"{base_name}{suffix}.csv"
            
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, header=header_option, encoding='utf-8-sig')
            
            file_data = {
                "filename": new_filename,
                "data": csv_buffer.getvalue(),
                "color": color,
                "key": f"{new_filename}_{mode}"
            }
            
            # 리스트에 추가 (중복 방지)
            if not any(f['filename'] == new_filename for f in st.session_state.converted_files):
                st.session_state.converted_files.append(file_data)
    else:
        st.warning("먼저 파일을 업로드해 주세요.")

st.divider()

# 3. 결과 파일 목록 및 ZIP 다운로드 표시
if st.session_state.converted_files:
    st.subheader("📥 생성된 파일 목록")
    
    # 상단에 리스트 비우기 버튼 배치
    if st.button("목록 전체 삭제"):
        st.session_state.converted_files = []
        st.rerun()

    for item in st.session_state.converted_files:
        col1, col2 = st.columns([3, 1])
        with col1:
            if item['color'] == "info":
                st.info(f"📄 {item['filename']}")
            else:
                st.success(f"📄 {item['filename']}")
        with col2:
            st.download_button(
                label="다운로드",
                data=item['data'],
                file_name=item['filename'],
                mime='text/csv',
                key=item['key']
            )
    
    st.divider()
    
    # --- 전체 ZIP 다운로드 로직 ---
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for file_info in st.session_state.converted_files:
            zf.writestr(file_info['filename'], file_info['data'])
    
    st.download_button(
        label="🎁 모든 결과물 ZIP으로 한꺼번에 받기",
        data=zip_buffer.getvalue(),
        file_name="converted_files_all.zip",
        mime="application/zip",
        use_container_width=True # 버튼을 가득 채워 강조
    )
