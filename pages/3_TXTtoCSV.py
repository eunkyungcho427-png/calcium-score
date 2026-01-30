import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="TXT to CSV Multi-Converter", layout="centered")

st.title("📂 TXT → CSV 멀티 변환기")
st.write("파일을 업로드하면 두 가지 옵션의 결과물이 동시에 생성됩니다.")

# 1. 파일 업로드 (가장 먼저 표시)
uploaded_files = st.file_uploader("TXT 파일을 선택하세요", type=['txt'], accept_multiple_files=True)

st.divider()

if uploaded_files:
    for idx, uploaded_file in enumerate(uploaded_files):
        # 원본 파일 읽기 (메모리에 유지)
        content = uploaded_file.read().decode('cp949', errors='ignore')
        uploaded_file.seek(0) # 다음 루프나 처리를 위해 포인터 리셋
        lines = content.splitlines()
        base_name = uploaded_file.name.rsplit('.', 1)[0]

        st.subheader(f"📄 원본 파일: {uploaded_file.name}")

        # --- 옵션 1: 탭 구조 유지 (_structure) ---
        all_rows = []
        for line in lines:
            parts = [p.strip() for p in line.split('\t')]
            all_rows.append(parts)
        df_struct = pd.DataFrame(all_rows)
        
        csv_struct = io.StringIO()
        df_struct.to_csv(csv_struct, index=False, header=False, encoding='utf-8-sig')
        name_struct = f"{base_name}_structure.csv"

        # --- 옵션 2: 2열 추출 (_2cols) ---
        extracted_data = []
        for line in lines:
            parts = [p.strip() for p in line.split('\t') if p.strip()]
            if len(parts) >= 2:
                name = " ".join(parts[:-1])
                value = parts[-1]
                extracted_data.append([name, value])
        df_2cols = pd.DataFrame(extracted_data, columns=['Feature_Name', 'Value'])
        
        csv_2cols = io.StringIO()
        df_2cols.to_csv(csv_2cols, index=False, header=True, encoding='utf-8-sig')
        name_2cols = f"{base_name}_2cols.csv"

        # --- UI 출력: 2줄로 각각 표시 ---
        # 첫 번째 줄: 구조 유지
        col1_1, col1_2 = st.columns([3, 1])
        with col1_1:
            st.info(f"옵션 1 적용: {name_struct}")
        with col1_2:
            st.download_button(
                label="다운로드 (구조)",
                data=csv_struct.getvalue(),
                file_name=name_struct,
                mime='text/csv',
                key=f"struct_{idx}_{uploaded_file.name}"
            )

        # 두 번째 줄: 2열 추출
        col2_1, col2_2 = st.columns([3, 1])
        with col2_1:
            st.success(f"옵션 2 적용: {name_2cols}")
        with col2_2:
            st.download_button(
                label="다운로드 (2열)",
                data=csv_2cols.getvalue(),
                file_name=name_2cols,
                mime='text/csv',
                key=f"2cols_{idx}_{uploaded_file.name}"
            )
        
        st.write("---") # 파일 간 구분선

    st.balloons() # 완료 효과
