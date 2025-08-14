import cv2
from pyzbar import pyzbar
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# QR코드만 필터링
def detect_qr_from_frame(frame):
    """
    주어진 영상 프레임에서 QR 코드를 탐지하고 표시
    """
    qr_codes = pyzbar.decode(frame)
    qr_codes = [qr for qr in qr_codes if qr.type == "QRCODE"]  # QR 코드만 선택

    for qr in enumerate(qr_codes):
        qr_data = qr.data.decode('utf-8')
        (x, y, w, h) = qr.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # 한글 지원 텍스트 표시
        frame = draw_text_opencv(frame, f"QR 내용: {qr_data}", (x, y - 10), font_size=20, color=(255, 255, 0))

    return frame
        

def draw_text_opencv(img, text, position, font_path="malgun.ttf", font_size=20, color=(255, 255, 255)):
    """
    OpenCV 이미지에 한글 텍스트를 표시
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

        # 그레이스케일로 변환하여 인식 안정화
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = detect_qr_from_frame(gray)

        cv2.imshow("QR 코드 감지", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
