# ver.3 업데이트 - qr 보안 검사 기능 추가, 야간 모드 지원 추가.
import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import sys, os
import time

# ver.2에 추가된 모듈은 아래와 같음.
import webbrowser       # 웹브라우저 실행 모듈
import tkinter as tk    # 팝업창 모듈
from tkinter import messagebox
import threading        # tkinter 팝업이 메인 루프를 막지 않도록 스레드 사용.

# ver.3에 추가된 모듈은 아래와 같음.
import re                          # 정규식 검사용
from urllib.parse import urlparse  # URL 분석용
import platform                    # OS 구분용


# --- stderr 완전 무력화 (OpenCV 내부 경고 제거 목적) ---
class SuppressStderr:
    def __enter__(self):
        self.original_stderr_fd = sys.stderr.fileno()
        self.devnull_fd = os.open(os.devnull, os.O_RDWR)
        self.saved_stderr_fd = os.dup(self.original_stderr_fd)
        os.dup2(self.devnull_fd, self.original_stderr_fd)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.dup2(self.saved_stderr_fd, self.original_stderr_fd)
        os.close(self.devnull_fd)
        os.close(self.saved_stderr_fd)

last_data = None
last_detect_time = 0

# ver.3에 추가됨: 전역 QR 검출기 생성
qr_detector = cv2.QRCodeDetector()

# ver.3에 추가됨: 악성 QR 코드 탐지 함수
def is_suspicious_qr(data):
    """
    QR 데이터가 의심스럽거나 악성일 가능성이 있는지 검사
    ver.4에 추가됨: 아래 조건 중, 최소 2개 이상 조건이 충족되어야 악성으로 판단
    """
    suspicion_count = 0
    reasons = []

    if data.startswith("http://") or data.startswith("https://"):
        parsed = urlparse(data)
        domain = parsed.netloc.lower()

        suspicious_domains = ["bit.ly", "tinyurl.com", "t.co", "goo.gl"]
        dangerous_extensions = [".exe", ".apk", ".bat", ".sh"]

        if any(domain.endswith(sd) for sd in suspicious_domains):
            suspicion_count += 1
            return True, "짧은 URL 서비스 사용"

        if any(parsed.path.endswith(ext) for ext in dangerous_extensions):
            suspicion_count += 1
            return True, "위험 확장자 포함"

        if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", domain):
            suspicion_count += 1
            return True, "IP 주소 기반 URL"

        if len(data) > 200:
            suspicion_count += 1
            return True, "URL 길이 과도함"

    if data.strip().lower().startswith("javascript:"):
        suspicion_count += 1
        return True, "JavaScript 실행 코드 포함"

    if re.match(r"^[A-Za-z0-9+/=]{100,}$", data):
        suspicion_count += 1
        return True, "Base64 인코딩된 긴 문자열"
    
    if suspicion_count >= 2:
        return True, ", ".join(reasons)
    else:
        return False, ""

# ver.2에 추가됨: 사용자에게 실행 여부 묻고 URL 열기
def ask_open_url(url):
    def popup():
        root = tk.Tk()
        root.withdraw()  # 창 숨기기

        result = messagebox.askyesno("QR 코드 실행", "정말로 여시겠습니까?")
        if result:
            webbrowser.open(url)
        root.destroy()

    # tkinter 팝업은 별도 스레드에서 실행
    threading.Thread(target=popup, daemon=True).start() # ver.3에서 수정됨: daemon = True 추가.

# ver.3에 추가됨: 야간 환경 감지 함수
def is_dark_environment(frame, threshold=50):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return np.mean(gray) < threshold

# ver.3에 추가됨: 저조도 환경 대비 전처리 함수
def enhance_for_low_light(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

# QR코드만 필터링
def detect_qr_opencv(frame):
    global last_data, last_detect_time

    # ver.3에 추가됨: 야간 모드 여부 판단 및 전처리
    dark_env = is_dark_environment(frame)
    if dark_env:
        frame = enhance_for_low_light(frame)

    with SuppressStderr():  # stderr 강제 차단 (콘솔 출력 완벽 차단)
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
    
    # ver.3에 추가됨: 악성 QR 탐지 적용
    is_bad, reason = is_suspicious_qr(data)
    if is_bad:
        warning_text = f"⚠️ 악성 QR 의심: {reason}"
        print(warning_text)
        frame = draw_text_opencv(frame, warning_text, (30, 30), font_size=24, color=(0, 0, 255))
    else:
        frame = draw_text_opencv(frame, f"QR 내용: {data}", (top_left[0], top_left[1] - 20))
    
    # ver.3에 추가됨: 야간 모드 안내 텍스트
    if dark_env:
        frame = draw_text_opencv(frame, "🌙 야간 모드 적용됨", (30, 60), font_size=16, color=(200, 200, 255))
    
    # ver.2에 추가됨: URL이면 실행 여부 묻기
    if data.startswith("http://") or data.startswith("https://"):
        ask_open_url(data)
    
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
