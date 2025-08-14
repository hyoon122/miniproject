# Discord Nitro 무료 지급 사기 이미지 감지 코드

import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar

def detect_qr_and_text(image_path):
    img = cv2.imread(image_path)
    # QR코드 스캔
    decoded_objects = pyzbar.decode(img)
    for obj in decoded_objects:
        print(f"QR Detected: {obj.data.decode('utf-8')}")

    # 텍스트 영역 감지 (간단 버전: Canny + Contour)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    print(f"Detected {len(contours)} text-like areas.")

detect_qr_and_text("suspicious_image.png")
