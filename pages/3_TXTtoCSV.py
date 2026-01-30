import pandas as pd
import os
import glob
from tkinter import Tk, filedialog, messagebox

def convert_txt_to_csv():
    # 1. 폴더 경로 선택 (VBA의 InputBox 대신 GUI 폴더 선택창 사용)
    root = Tk()
    root.withdraw()  # 메인 창 숨기기
    folder_path = filedialog.askdirectory(title="TXT 파일이 저장된 폴더를 선택하세요")
    
    if not folder_path:
        print("작업이 취소되었습니다.")
        return

    # 2. 폴더 내 모든 .txt 파일 찾기
    txt_files = glob.glob(os.path.join(folder_path, "*.txt"))

    if not txt_files:
        messagebox.showwarning("경고", "지정된 폴더에 TXT 파일이 없습니다.")
        return

    # 3. 각 TXT 파일 처리
    for txt_file in txt_files:
        try:
            # VBA의 vbTab 구분을 적용하여 읽기 (sep='\t')
            # encoding은 시스템에 따라 'utf-8' 혹은 'cp949'(한글)를 사용합니다.
            df = pd.read_csv(txt_file, sep='\t', encoding='cp949')

            # CSV 파일 경로 생성 (.txt를 .csv로 변경)
            csv_file = os.path.splitext(txt_file)[0] + ".csv"

            # CSV로 저장 (인덱스 제외, 한글 깨짐 방지를 위해 utf-8-sig 권장)
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            print(f"변환 완료: {os.path.basename(txt_file)} -> {os.path.basename(csv_file)}")
            
        except Exception as e:
            print(f"오류 발생 ({os.path.basename(txt_file)}): {e}")

    messagebox.showinfo("완료", "모든 TXT 파일이 CSV 파일로 변환되었습니다.")

if __name__ == "__main__":
    convert_txt_to_csv()
