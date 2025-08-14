import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import sys, os
import time
last_detect_time = 0

# QR코드만 필터링
def detect_qr_opencv(frame):
    global last_data, last_detect_time
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(frame)

    # QR이 없거나 디코딩된 내용이 없으면 바로 원본 리턴
    if not data or bbox is None:
        return frame
    
    # 2초 이내에는 재감지하지 않음
    now = time.time()
    if data == last_data and now - last_detect_time < 2:
        return frame

    last_data = data
    last_detect_time = now

    bbox = bbox.astype(int)  # 꼭 int로 변환 (OpenCV 그리기 함수 호환)
    for i in range(len(bbox[0])):
            pt1 = tuple(bbox[0][i])
            pt2 = tuple(bbox[0][(i + 1) % len(bbox[0])])
            cv2.line(frame, pt1, pt2, (0, 255, 0), 2)

    top_left = tuple(bbox[0][0])
    print(f"[디코딩된 QR 내용] {data}")  # 콘솔 확인용
    frame = draw_text_opencv(frame, f"QR 내용: {data}", (top_left[0], top_left[1] - 20))
    return frame
        

def draw_text_opencv(img, text, position, font_size=20, color=(255, 255, 0)):
    """
    Pillow를 이용해 OpenCV 이미지에 한글 텍스트를 표시
    """
    # OpenCV 이미지를 PIL 이미지로 변환
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)

    # 한글 폰트 설정 (Windows 기본 H2GTRM.TTF 사용)
    try:
        font_path = "C:/Windows/Fonts/H2GTRM.TTF"  # 절대 경로 지정
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print("폰트를 불러올 수 없습니다. 경로를 확인하세요.")
        font = ImageFont.load_default()

    draw.text(position, text, font=font, fill=color)

    # 다시 OpenCV 이미지로 변환
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        return
    
    print("실시간 QR 코드 감지를 시작합니다. 종료하려면 'q'를 누르세요.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # OpenCV 기반 QR 감지 함수 호출
        frame_display = detect_qr_opencv(frame)

        cv2.imshow("QR Scanner", frame_display)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
