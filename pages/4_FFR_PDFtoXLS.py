import streamlit as st
import pandas as pd
import pytesseract
from pdf2image import convert_from_bytes
import re
import io
import numpy as np
import cv2  # 이미지 처리를 위한 라이브러리
from PIL import Image, ImageOps, ImageEnhance

def preprocess_image(pil_img):
    """OCR 인식률을 높이기 위한 이미지 전처리"""
    # 1. 흑백 전환
    gray = ImageOps.grayscale(pil_img)
    # 2. 대비 증폭 (글자를 더 진하게)
    enhancer = ImageEnhance.Contrast(gray)
    gray = enhancer.enhance(2.0)
    # 3. OpenCV를 이용한 이진화 (배경은 하얗게, 글자는 검게)
    img_array = np.array(gray)
    _, thresh = cv2.threshold(img_array, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return Image.fromarray(thresh)

def extract_ffr_data_ocr(file_bytes):
    lad, lcx, rca = "", "", ""
    try:
        # DPI를 400으로 더 높임
        images = convert_from_bytes(file_bytes, dpi=400, first_page=2, last_page=2)
        if not images:
            images = convert_from_bytes(file_bytes, dpi=400, first_page=1, last_page=1)
        
        if images:
            processed_img = preprocess_image(images[0])
            
            # 디버깅용: 전처리된 이미지를 확인하고 싶다면 아래 주석 해제
            # st.image(processed_img, caption="OCR이 보고 있는 이미지")

            # [핵심] 숫자 전용 설정 적용
            # --psm 6: 균일한 텍스트 블록으로 간주
            # -c tessedit_char_whitelist: 지정된 문자만 인식하도록 강제
            custom_config = r'--psm 6 -c tessedit_char_whitelist=0123456789.LADRCX'
            page_text = pytesseract.image_to_string(processed_img, lang='eng', config=custom_config)

            # 텍스트 정제 (공백 제거 후 검색)
            clean_text = "".join(page_text.split())

            def find_value(target, text):
                # target(LAD 등) 바로 뒤나 근처에 오는 0.xx 패턴 추출
                pattern = re.compile(rf'{target}.*?([01][\.,]\d{{2}})', re.I)
                match = pattern.search(text)
                if match:
                    return match.group(1).replace(',', '.')
                
                # 패턴 매칭 실패 시 숫자만이라도 다 긁어오는 예외 처리
                # (LAD 0.85 구조가 깨졌을 경우를 대비)
                nums = re.findall(r'[01][\.,]\d{2}', text)
                # 이 부분은 리포트의 수치 순서(보통 LAD-LCX-RCA 순)에 따라 수동 매칭 필요 가능
                return ""

            lad = find_value("LAD", clean_text)
            lcx = find_value("LCX", clean_text)
            rca = find_value("RCA", clean_text)

    except Exception as e:
        st.error(f"OCR 분석 중 오류: {e}")
    return lad, lcx, rca

# (나머지 Streamlit UI 코드는 동일)
