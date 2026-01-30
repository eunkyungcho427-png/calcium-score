import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="TXT to CSV Converter", layout="centered")

st.title("📂 TXT → CSV 변환기")
st.write("변환 방식을 선택하면 파일명에 자동으로 해당 옵션이 표시됩니다.")

# 1. 변환 옵션 선택
mode = st.selectbox(
    "변환 모드 선택",
    ("탭 구조 유지", "2열 추출")
)

st.divider()

# 2. 파일 업로드
uploaded_files = st.file_uploader("TXT 파일을 선택하세요", type=['txt'], accept_multiple_files=True)

if uploaded_files:
    for idx, uploaded_file in enumerate(uploaded_files):
        try:
            # 파일 읽기
            content = uploaded_file.read().decode('cp949', errors='ignore')
            lines = content.splitlines()
            
            # --- 파일명 설정 로직 ---
            # 원본 파일명에서 확장자 제거 (예: data.txt -> data)
            base_name = uploaded_file.name.rsplit('.', 1)[0]
            
            # 선택된 모드에 따라 접미사 결정
            suffix = "_structure" if mode == "탭 구조 유지" else "_2cols"
            
            # 최종 파일명 (예: data_structure.csv 또는 data_2cols.csv)
            new_filename = f"{base_name}{suffix}.csv"
            
            # --- 변환 로직 ---
            if mode == "2열 추출":
                extracted_data = []
                for line in lines:
                    parts = [p.strip() for p in line.split('\t') if p.strip()]
                    if len(parts) >= 2:
                        name = " ".join(parts[:-1])
                        value = parts[-1]
                        extracted_data.append([name, value])
                df = pd.DataFrame(extracted_data, columns=['Feature_Name', 'Value'])
                header_option = True
            
            else:
                # 탭 구조 유지 로직
                all_rows = []
                for line in lines:
                    parts = [p.strip() for p in line.split('\t')]
                    all_rows.append(parts)
                df = pd.DataFrame(all_rows)
                header_option = False

            # CSV 변환 (메모리)
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, header=header_option, encoding='utf-8-sig')
            
            # 3. UI 결과 표시 및 다운로드
            col1, col2 = st.columns([3, 1])
            with col1:
                # 변환될 파일명을 화면에 미리 보여줌
                st.info(f"📄 {new_filename}") 
            with col2:
                st.download_button(
                    label="다운로드",
                    data=csv_buffer.getvalue(),
                    file_name=new_filename,
                    mime='text/csv',
                    key=f"btn_{idx}_{new_filename}" # key에도 모드 정보가 포함되게 설정
                )

        except Exception as e:
            st.error(f"❌ {uploaded_file.name} 변환 오류: {e}")

    st.success(f"선택하신 '{mode}' 모드로 변환 파일명이 생성되었습니다.")
