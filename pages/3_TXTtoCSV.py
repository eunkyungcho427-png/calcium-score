import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Tab Structure Preserver", layout="centered")

st.title("📂 계층 구조 유지 TXT → CSV 변환")
st.info("TXT의 탭(들여쓰기) 위치를 엑셀 열(Column)로 그대로 변환합니다.")

uploaded_files = st.file_uploader("TXT 파일을 선택하세요", type=['txt'], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        try:
            # 1. 파일 읽기 (인코딩 대응)
            content = uploaded_file.read().decode('cp949', errors='ignore')
            lines = content.splitlines()
            
            all_rows = []
            max_cols = 0
            
            # 2. 한 줄씩 분석하여 탭 위치에 따라 데이터 분산
            for line in lines:
                # 탭으로 분리하되 빈 문자열도 위치 파악을 위해 유지
                parts = line.split('\t')
                # 공백만 있는 요소 제거 및 정리
                cleaned_parts = [p.strip() for p in parts]
                all_rows.append(cleaned_parts)
                # 최대 열 개수 파악
                max_cols = max(max_cols, len(cleaned_parts))
            
            # 3. 데이터프레임 생성 (열 개수 맞추기)
            df = pd.DataFrame(all_rows)

            # CSV 변환
            csv_buffer = io.StringIO()
            # 탭 구조를 유지한 채 콤마(,)로 구분된 CSV 생성
            df.to_csv(csv_buffer, index=False, header=False, encoding='utf-8-sig')
            
            # 다운로드 UI
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(f"✅ {uploaded_file.name}")
            with col2:
                st.download_button(
                    label="다운로드",
                    data=csv_buffer.getvalue(),
                    file_name=uploaded_file.name.replace(".txt", ".csv"),
                    mime='text/csv',
                    key=f"dl_{uploaded_file.name}"
                )

        except Exception as e:
            st.error(f"❌ {uploaded_file.name} 변환 실패: {e}")

    st.success("모든 파일의 구조가 유지된 채 변환되었습니다.")
