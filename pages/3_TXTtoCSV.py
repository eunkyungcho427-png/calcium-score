import pandas as pd
import os
import glob

def convert_txt_to_csv(folder_path):
    # 폴더 존재 여부 확인
    if not os.path.exists(folder_path):
        print(f"Error: 폴더를 찾을 수 없습니다: {folder_path}")
        return

    # 1. 폴더 내 모든 .txt 파일 찾기
    txt_files = glob.glob(os.path.join(folder_path, "*.txt"))

    if not txt_files:
        print("지정된 폴더에 TXT 파일이 없습니다.")
        return

    print(f"총 {len(txt_files)}개의 파일을 변환합니다...")

    # 2. 각 TXT 파일 처리
    for txt_file in txt_files:
        try:
            # VBA의 vbTab 구분을 적용하여 읽기 (sep='\t')
            # 서버 환경에선 인코딩에 따라 'utf-8' 또는 'cp949' 선택
            try:
                df = pd.read_csv(txt_file, sep='\t', encoding='cp949')
            except:
                df = pd.read_csv(txt_file, sep='\t', encoding='utf-8')

            # CSV 파일 경로 생성
            csv_file = os.path.splitext(txt_file)[0] + ".csv"

            # CSV로 저장
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            print(f"성공: {os.path.basename(txt_file)}")
            
        except Exception as e:
            print(f"오류 발생 ({os.path.basename(txt_file)}): {e}")

    print("모든 작업이 완료되었습니다.")

if __name__ == "__main__":
    # 실행 환경에 맞는 경로를 입력하세요. 
    # 예: "C:/data" (로컬) 또는 "./data" (서버)
    path = input("TXT 파일이 저장된 폴더 경로를 입력하세요: ")
    convert_txt_to_csv(path)
