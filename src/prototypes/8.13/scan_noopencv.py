import requests
import re
import qrcode
import cv2
from pyzbar.pyzbar import decode

# ------------------------------
# 1. 피싱 사이트 DB (예시: 단순 리스트)
#    실제로는 PhishTank, Google Safe Browsing API 사용 가능
# ------------------------------
known_phishing_domains = [
    "malicious-example.com",
    "discord-fake-login.com",
    "phishingsite.net"
]

# ------------------------------
# 2. URL 위험도 체크 함수
# ------------------------------
def is_phishing_domain(url):
    # 도메인 추출
    domain_match = re.search(r"https?://([^/]+)", url)
    if not domain_match:
        return False
    domain = domain_match.group(1).lower()

    # DB와 비교
    if domain in known_phishing_domains:
        return True
    return False

# ------------------------------
# 3. QR코드에서 URL 추출
# ------------------------------
def scan_qr_image(image_path):
    img = cv2.imread(image_path)
    decoded_objects = decode(img)
    urls = []
    for obj in decoded_objects:
        data = obj.data.decode("utf-8")
        if re.match(r"https?://", data):
            urls.append(data)
    return urls

# ------------------------------
# 4. 실행 흐름
# ------------------------------
if __name__ == "__main__":
    print("=== 피싱 감지 프로그램 ===")
    mode = input("QR코드 이미지 스캔(1) / 도메인 직접 입력(2) 중 선택: ")

    if mode == "1":
        image_path = input("QR코드 이미지 경로 입력: ")
        urls = scan_qr_image(image_path)
        if not urls:
            print("QR코드에서 URL을 찾을 수 없습니다.")
        else:
            for url in urls:
                print(f"[스캔 결과] {url}")
                if is_phishing_domain(url):
                    print("⚠ 위험: 피싱 사이트로 의심됩니다!")
                else:
                    print("✅ 안전: 피싱 DB에 등록되지 않음")

    elif mode == "2":
        url = input("검사할 도메인/URL 입력: ")
        if is_phishing_domain(url):
            print("⚠ 위험: 피싱 사이트로 의심됩니다!")
        else:
            print("✅ 안전: 피싱 DB에 등록되지 않음")

    else:
        print("잘못된 선택입니다.")
