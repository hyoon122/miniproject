import cv2
from pyzbar import pyzbar
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import warnings
import sys, os

# stderr를 잠시 리디렉션하여 ZBar 경고 무시
class DummyFile:
    def write(self, x): pass
    def flush(self): pass

sys.stderr = DummyFile()

# QR코드만 필터링
def detect_qr_from_frame(frame_color, frame_gray):
    """
    주어진 영상 프레임에서 QR 코드를 탐지하고 표시
    """
    qr_codes = pyzbar.decode(frame_gray)
    qr_codes = [qr for qr in qr_codes if qr.type == "QRCODE"]  # QR 코드만 선택

    for qr in enumerate(qr_codes):
        qr_data = qr.data.decode('utf-8')
        (x, y, w, h) = qr.rect
        cv2.rectangle(frame_color, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # 한글 지원 텍스트 표시
        frame_color = draw_text_opencv(frame_color, f"QR 내용: {qr_data}", (x, y - 30))

    return frame_color
        

def draw_text_opencv(img, text, position, font_path="malgun.ttf", font_size=20, color=(255, 255, 0)):
    """
    Pillow를 이용해 OpenCV 이미지에 한글 텍스트를 표시
    """
    # OpenCV 이미지를 PIL 이미지로 변환
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)

    # 한글 폰트 설정 (Windows 기본 Malgun Gothic 사용)
    font = ImageFont.truetype(font_path, font_size)
    draw.text(position, text, font=font, fill=color)

    # 다시 OpenCV 이미지로 변환
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def main():
    cap = cv2.VideoCapture(0)
    print("실시간 QR 코드 감지를 시작합니다. 종료하려면 'q'를 누르세요.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 컬러 프레임 사용
        frame_display = detect_qr_from_frame(frame)

        cv2.imshow("QR 코드 감지", frame_display)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
