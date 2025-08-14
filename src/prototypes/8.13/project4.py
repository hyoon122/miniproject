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
    입력: URL 문자열
    출력: (안전 여부(Boolean), 메시지 문자열)
    """
    try:
        # URL을 파싱하여 도메인 부분만 추출
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()  # 소문자로 변환하여 비교

        # www. 제거 (www.example.com == example.com)
        if domain.startswith("www."):
            domain = domain[4:]

        # 블랙리스트 도메인인지 확인
        if domain in BLACKLISTED_DOMAINS:
            return False, f"[경고] 블랙리스트 도메인 발견: {domain}"
        else:
            return True, f"[안전] 도메인: {domain}"
    except Exception as e:
        # URL 분석 중 오류 발생 시
        return False, f"[오류] URL 분석 실패: {e}"

def detect_qr_from_frame(frame):
    """
    주어진 영상 프레임에서 QR 코드를 탐지하고 분석
    입력: OpenCV 프레임 (numpy 배열)
    출력: QR 코드 표시 및 분석 메시지가 포함된 프레임
    """
    qr_codes = pyzbar.decode(frame)  # 프레임에서 QR 코드 디코딩
    for qr in qr_codes:
        qr_data = qr.data.decode('utf-8')  # QR 코드 내용 문자열로 변환
        (x, y, w, h) = qr.rect  # QR 코드 위치와 크기 가져오기
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # QR 코드 위치 표시

        if qr_data.startswith("http"):
            # URL이면 블랙리스트 검사
            safe, message = check_domain_safety(qr_data)
            color = (0, 0, 255) if not safe else (0, 255, 0)  # 안전 여부에 따라 색상 변경
            cv2.putText(frame, message, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        else:
            # 단순 텍스트 QR 코드
            cv2.putText(frame, f"QR 내용: {qr_data}", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    return frame

def main():
    cap = cv2.VideoCapture(0)  # 기본 웹캠 열기
    print("실시간 QR 코드 감지를 시작합니다. 종료하려면 'q'를 누르세요.")

    while True:
        ret, frame = cap.read()  # 프레임 읽기
        if not ret:
            break  # 프레임 읽기 실패 시 종료

        # 프레임에서 QR 코드 탐지 및 표시
        frame = detect_qr_from_frame(frame)

        # 화면에 프레임 표시
        cv2.imshow("QR 코드 감지", frame)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 종료 시 리소스 해제
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
