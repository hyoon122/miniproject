# QR코드와 도메인을 스캔하여 검사하는 알고리즘
import cv2
import numpy as np
import re
import requests
from pyzbar.pyzbar import decode

# 설정
SUSPICIOUS_DOMAINS = ["discord-gift.com", "free-nitro.com", "discord-airdrop.com"]  # 의심 도메인 리스트

# URL에서 도메인 추출 함수
def extract_domain(url):
    domain_pattern = re.compile(r"https?://([^/]+)/?")
    match = domain_pattern.search(url)
    return match.group(1) if match else None

# 의심 도메인인지 확인
def is_suspicious_domain(domain):
    return domain in SUSPICIOUS_DOMAINS

# 이미지에서 QR 코드 탐지
def scan_qr_code(image_path):
    img = cv2.imread(image_path)
    detected_qrs = decode(img)
    results = []

    for qr in detected_qrs:
        qr_data = qr.data.decode("utf-8")
        domain = extract_domain(qr_data)
        is_suspicious = is_suspicious_domain(domain) if domain else False
        results.append({
            "data": qr_data,
            "domain": domain,
            "suspicious": is_suspicious
        })
    return results

# 이미지에서 텍스트 기반 URL 탐지
def scan_text_for_urls(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 이미지 전처리 (노이즈 제거)
    gray = cv2.medianBlur(gray, 3)

    # pytesseract 불러오기 (OCR)
    try:
        import pytesseract
    except ImportError:
        print("[!] pytesseract 모듈이 필요합니다. 설치: pip install pytesseract")
        return []

    text = pytesseract.image_to_string(gray)
    urls = re.findall(r"https?://[\w./-]+", text)

    results = []
    for url in urls:
        domain = extract_domain(url)
        is_suspicious = is_suspicious_domain(domain) if domain else False
        results.append({
            "url": url,
            "domain": domain,
            "suspicious": is_suspicious
        })
    return results

# 메인 실행부
def main(image_path):
    print(f"[+] {image_path} 파일 분석 시작...")

    qr_results = scan_qr_code(image_path)
    if qr_results:
        print("\n[QR 코드 분석 결과]")
        for r in qr_results:
            print(f" QR 데이터: {r['data']}")
            print(f" 도메인: {r['domain']}")
            print(f" 의심 여부: {'⚠️ 의심' if r['suspicious'] else '✅ 안전'}\n")
    else:
        print("[QR 코드 없음]")
    
    text_results = scan_text_for_urls(image_path)
    if text_results:
        print("\n[텍스트 URL 분석 결과]")
        for r in text_results:
            print(f" URL: {r['url']}")
            print(f" 도메인: {r['domain']}")
            print(f" 의심 여부: {'⚠️ 의심' if r['suspicious'] else '✅ 안전'}\n")
    else:
        print("[텍스트 URL 없음]")

if __name__ == "__main__":
    test_image = "test.png"  # 분석할 이미지 파일 경로
    main(test_image)
