import streamlit as st
import pandas as pd
import io
import re

st.set_page_config(page_title="Texture Feature Converter", layout="centered")

st.title("📂 Texture Feature TXT → CSV 변환기")
st.info("데이터가 포함된 줄만 자동으로 추출하여 변환합니다.")

uploaded_files = st.file_uploader("TXT 파일을 선택하세요", type=['txt'], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        try:
            # 1. 파일 내용 읽기
            content = uploaded_file.read().decode('cp949', errors='ignore')
            lines = content.splitlines()
            
            extracted_data = []
            
            # 2. 한 줄씩 검사하여 데이터 추출
            for line in lines:
                # 탭(\t)으로 구분된 데이터 찾기
                parts = [p.strip() for p in line.split('\t') if p.strip()]
                
                # '항목명'과 '수치'가 모두 있는 경우만 리스트에 추가
                if len(parts) >= 2:
                    # 마지막 요소가 숫자인지 확인 (간단한 필터링)
                    name = " ".join(parts[:-1])
                    value = parts[-1]
                    extracted_data.append([name, value])
            
            # 3. 데이터프레임 생성
            df = pd.DataFrame(extracted_data, columns=['Feature_Name', 'Value'])

            if not df.empty:
                # CSV 변환 (메모리)
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
                
                # 다운로드 UI
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(f"✅ {uploaded_file.name} (추출됨: {len(df)} 행)")
                with col2:
                    st.download_button(
                        label="다운로드",
                        data=csv_buffer.getvalue(),
                        file_name=uploaded_file.name.replace(".txt", ".csv"),
                        mime='text/csv',
                        key=uploaded_file.name
                    )
            else:
                st.warning(f"⚠️ {uploaded_file.name}: 추출할 수 있는 데이터 형식이 없습니다.")

        except Exception as e:
            st.error(f"❌ {uploaded_file.name} 처리 중 오류: {e}")

    st.success("작업이 완료되었습니다.")
