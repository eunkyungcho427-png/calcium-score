import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="TXT to CSV Converter", layout="centered")

st.title("📂 TXT → CSV 맞춤 변환기")

# 1. 파일 업로드 (가장 상단)
uploaded_files = st.file_uploader("TXT 파일을 선택하세요", type=['txt'], accept_multiple_files=True)

st.divider()

# 2. 변환 옵션 선택 (스크롤다운 목록)
# 파일을 먼저 업로드해야 옵션 선택창이 의미가 있으므로 순서를 조정했습니다.
mode = st.selectbox(
    "변환 옵션을 선택하세요",
    ("탭 구조 유지 (원본 형식 보존)", "2열 추출 (항목명과 값만 정리)"),
    index=0
)

st.write("") # 간격 조절

if uploaded_files:
    st.subheader("📥 변환 결과 및 다운로드")
    
    for idx, uploaded_file in enumerate(uploaded_files):
        try:
            # 파일 읽기
            content = uploaded_file.read().decode('cp949', errors='ignore')
            lines = content.splitlines()
            
            # 확장자를 제외한 기본 파일명 추출
            base_name = uploaded_file.name.rsplit('.', 1)[0]
            
            # --- 옵션별 로직 분기 ---
            if mode == "탭 구조 유지 (원본 형식 보존)":
                # 옵션 1: 구조 유지 (_structure)
                all_rows = []
                for line in lines:
                    parts = [p.strip() for p in line.split('\t')]
                    all_rows.append(parts)
                df = pd.DataFrame(all_rows)
                
                suffix = "_structure"
                header_option = False
                color_theme = "info" # 파란색 계열
                
            else:
                # 옵션 2: 2열 추출 (_2cols)
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
                color_theme = "success" # 초록색 계열

            # 최종 파일명 결정
            new_filename = f"{base_name}{suffix}.csv"

            # CSV 변환 (메모리 내 StringIO 사용)
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, header=header_option, encoding='utf-8-sig')
            
            # --- 3. 결과 파일명과 다운로드 버튼 표시 ---
            col1, col2 = st.columns([3, 1])
            with col1:
                if color_theme == "info":
                    st.info(f"📄 {new_filename}")
                else:
                    st.success(f"📄 {new_filename}")
            with col2:
                st.download_button(
                    label="다운로드",
                    data=csv_buffer.getvalue(),
                    file_name=new_filename,
                    mime='text/csv',
                    key=f"btn_{idx}_{mode}_{uploaded_file.name}" # 고유 키 설정
                )

        except Exception as e:
            st.error(f"❌ {uploaded_file.name} 처리 중 오류 발생: {e}")

    st.toast(f"'{mode}' 모드로 변환 준비 완료!")
else:
    st.warning("먼저 TXT 파일을 업로드해 주세요.")
