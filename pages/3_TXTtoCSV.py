import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="TXT to CSV Converter", layout="centered")

st.title("📂 TXT를 CSV로 변환하기")
st.write("탭(Tab)으로 구분된 TXT 파일을 업로드하면 CSV로 변환해 드립니다.")

# 1. 파일 업로드 (여러 개 가능)
uploaded_files = st.file_uploader("TXT 파일을 선택하세요", type=['txt'], accept_multiple_files=True)

if uploaded_files:
    st.divider()
    st.subheader(f"총 {len(uploaded_files)}개의 파일이 선택됨")

    for uploaded_file in uploaded_files:
        try:
            # 파일 읽기 (인코딩 처리)
            # 한국어 환경을 고려하여 cp949 시도 후 실패 시 utf-8 시도
            try:
                df = pd.read_csv(uploaded_file, sep='\t', encoding='cp949')
            except:
                uploaded_file.seek(0) # 파일 포인터 초기화
                df = pd.read_csv(uploaded_file, sep='\t', encoding='utf-8')

            # 파일명 변경 (.txt -> .csv)
            new_filename = uploaded_file.name.replace(".txt", ".csv")

            # 메모리 내에서 CSV 파일 생성 (실제 서버에 저장하지 않음)
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
            csv_data = csv_buffer.getvalue()

            # UI 구성 (파일명과 다운로드 버튼)
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(f"📄 {uploaded_file.name}")
            with col2:
                st.download_button(
                    label="다운로드",
                    data=csv_data,
                    file_name=new_filename,
                    mime='text/csv',
                    key=uploaded_file.name # 중복 방지용 키
                )

        except Exception as e:
            st.error(f"❌ {uploaded_file.name} 처리 중 오류 발생: {e}")

    st.success("모든 변환 작업이 준비되었습니다!")
