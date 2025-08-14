import cv2
from pyzbar import pyzbar

# QR 코드 내용을 표시하는 창 관리용 딕셔너리
qr_windows = {}

def detect_qr_from_frame(frame):
    """
    주어진 영상 프레임에서 QR 코드를 탐지하고 표시
    """
    qr_codes = pyzbar.decode(frame)
    current_qr_ids = []

    for i, qr in enumerate(qr_codes):
        qr_data = qr.data.decode('utf-8')
        (x, y, w, h) = qr.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, f"QR 내용: {qr_data}", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        # 새로운 창에 QR 코드 내용 표시
        window_name = f"QR 내용 {i}"
        current_qr_ids.append(window_name)
        cv2.imshow(window_name, create_text_image(qr_data))

    # 이전에 열려있던 QR 창 중 현재 프레임에 없는 QR 내용 창 닫기
    for win in list(qr_windows.keys()):
        if win not in current_qr_ids:
            cv2.destroyWindow(win)
            del qr_windows[win]

    # 현재 QR 창 업데이트
    for win in current_qr_ids:
        qr_windows[win] = True

    return frame

def create_text_image(text, width=400, height=100):
    """
    텍스트를 OpenCV 이미지로 변환
    """
    import numpy as np
    img = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.putText(img, text, (10, height//2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    return img

def main():
    cap = cv2.VideoCapture(0)
    print("실시간 QR 코드 감지를 시작합니다. 종료하려면 'q'를 누르세요.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = detect_qr_from_frame(frame)
        cv2.imshow("QR 코드 감지", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
