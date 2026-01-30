import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="TXT to CSV Advanced Converter", layout="centered")

st.title("📂 TXT → CSV 변환기 (모드 선택)")
st.write("변환 방식을 선택하고 파일을 업로드해 주세요.")

# 1. 변환 옵션 선택 (셀렉트박스)
mode = st.selectbox(
    "변환 모드 선택",
    ("탭 구조 유지 (원본과 동일한 칸 띄우기)", "2열 추출 (항목명 | 값)")
)

st.divider()

# 2. 파일 업로드
uploaded_files = st.file_uploader("TXT 파일을 선택하세요", type=['txt'], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        try:
            # 파일 읽기 (한글 인코딩 고려)
            content = uploaded_file.read().decode('cp949', errors='ignore')
            lines = content.splitlines()
            
            # 새 파일 이름 설정 (파일명.txt -> 파일명.csv)
            new_filename = f"{uploaded_file.name.rsplit('.', 1)[0]}.csv"
            
            if mode == "2열 추출 (항목명 | 값)":
                # --- 2열 추출 로직 ---
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
                # --- 탭 구조 유지 로직 (VBA 스타일) ---
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
                st.text(f"✅ {new_filename}") # 요청하신 파일명 형식 표시
            with col2:
                st.download_button(
                    label="다운로드",
                    data=csv_buffer.getvalue(),
                    file_name=new_filename,
                    mime='text/csv',
                    key=f"dl_{uploaded_file.name}_{mode}"
                )

        except Exception as e:
            st.error(f"❌ {uploaded_file.name} 변환 오류: {e}")

    st.success(f"'{mode}' 모드로 모든 변환이 준비되었습니다.")
