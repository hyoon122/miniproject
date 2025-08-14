import cv2
from pyzbar import pyzbar
from urllib.parse import urlparse

# 블랙리스트 예시 (실제 사용 시 확장 가능)
BLACKLISTED_DOMAINS = [
    "example-phish.com",
    "malicious-site.net",
    "fake-login.org"
]

def check_domain_safety(url):
    """
    주어진 URL이 블랙리스트에 있는지 확인하는 함수
    """
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()

        if domain.startswith("www."):
            domain = domain[4:]

        if domain in BLACKLISTED_DOMAINS:
            return False, f"[경고] 블랙리스트 도메인 발견: {domain}"
        else:
            return True, f"[안전] 도메인: {domain}"
    except Exception as e:
        return False, f"[오류] URL 분석 실패: {e}"

def detect_qr_from_frame(frame):
    """
    주어진 프레임에서 QR 코드 탐지 및 분석
    """
    qr_codes = pyzbar.decode(frame)
    for qr in qr_codes:
        qr_data = qr.data.decode('utf-8')
        (x, y, w, h) = qr.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if qr_data.startswith("http"):
            safe, message = check_domain_safety(qr_data)
            color = (0, 0, 255) if not safe else (0, 255, 0)
            cv2.putText(frame, message, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        else:
            cv2.putText(frame, f"QR 내용: {qr_data}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    return frame

def main():
    cap = cv2.VideoCapture(0)  # 웹캠 열기
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
