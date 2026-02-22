# SmartPark53 - Yapay zeka ile plaka tanıma (entegrasyon modülü)
#
# Hedef: Giriş/çıkış noktalarındaki kameralardan gelen görüntüden
# plakayı otomatik okumak (OCR / nesne tespiti).
#
# Öncelik sırası:
# 1) PLAKA_API_URL ortam değişkeni tanımlıysa harici API çağrılır.
# 2) Pytesseract + Pillow kuruluysa yerel OCR dener (isteğe bağlı).
# 3) Hiçbiri yoksa (None, 0.0) döner — kamera manuel giriş veya başka sistemle beslenir.

from typing import Optional, Tuple, Union
import os
import re
import base64

# Türk plaka: rakam + harf + rakam (ör. 34ABC123, 06A1234)
def _normalize_plaka(raw: str) -> str:
    """Ham metni plaka formatına çevirir: büyük harf, sadece harf/rakam."""
    if not raw:
        return ""
    s = "".join(c for c in raw.upper() if c.isalnum())
    return s.strip()


def _call_external_api(image_bytes: bytes) -> Tuple[Optional[str], float]:
    """
    PLAKA_API_URL ile harici plaka tanıma API'sini çağırır.
    Beklenen: POST ile görsel (multipart/form-data file veya JSON base64), cevap { "plaka": "...", "guven": 0.9 }.
    """
    url = os.environ.get("PLAKA_API_URL", "").strip()
    if not url:
        return None, 0.0
    try:
        import urllib.request
        import urllib.error
        import json as _json

        # Base64 ile JSON body (çoğu API bunu kabul eder)
        b64 = base64.b64encode(image_bytes).decode("ascii")
        data = _json.dumps({"image": b64}).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            out = _json.loads(body)
            plaka = (out.get("plaka") or "").strip()
            guven = float(out.get("guven", 0) or 0)
            if plaka:
                plaka = _normalize_plaka(plaka)
                if len(plaka) >= 5:
                    return plaka, min(1.0, max(0.0, guven))
        return None, 0.0
    except Exception:
        return None, 0.0


def _ocr_tesseract(image_bytes: bytes) -> Tuple[Optional[str], float]:
    """
    Pytesseract + Pillow ile görsel üzerinde OCR dener (isteğe bağlı bağımlılık).
    Sistemde tesseract-ocr kurulu olmalı; yoksa veya hata olursa (None, 0.0).
    """
    try:
        import pytesseract
        from PIL import Image
        import io
    except ImportError:
        return None, 0.0
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode != "RGB":
            img = img.convert("RGB")
        text = pytesseract.image_to_string(img, lang="eng")
        # Plaka benzeri parça ara (2-3 rakam, 2-3 harf, 2-4 rakam)
        for part in text.replace("\n", " ").split():
            part = _normalize_plaka(part)
            if len(part) >= 5 and any(c.isdigit() for c in part) and any(c.isalpha() for c in part):
                # Türk plakası formatına yaklaştır: rakam+harf+rakam
                cleaned = re.sub(r"[^A-Z0-9]", "", part.upper())
                if 5 <= len(cleaned) <= 11:
                    return cleaned, 0.6  # Düşük güven; manuel doğrulama önerilir
        return None, 0.0
    except Exception:
        return None, 0.0


def plaka_tanimla(gorsel_yolu_veya_byte: Union[str, bytes]) -> Tuple[Optional[str], float]:
    """
    Görüntüden plaka metnini tanır.

    Args:
        gorsel_yolu_veya_byte: Görsel dosya yolu (str) veya ham görüntü bytes.

    Returns:
        (plaka_metni, güven_skoru) — tanınamadıysa (None, 0.0).

    Ortam değişkeni:
        PLAKA_API_URL: Tanımlıysa görsel bu URL'ye POST edilir; cevap {"plaka": "...", "guven": 0.9} beklenir.
    """
    if isinstance(gorsel_yolu_veya_byte, str):
        if os.path.isfile(gorsel_yolu_veya_byte):
            with open(gorsel_yolu_veya_byte, "rb") as f:
                image_bytes = f.read()
        else:
            return None, 0.0
    else:
        image_bytes = gorsel_yolu_veya_byte

    if not image_bytes or len(image_bytes) < 100:
        return None, 0.0

    # 1) Harici API
    plaka, guven = _call_external_api(image_bytes)
    if plaka:
        return plaka, guven

    # 2) Yerel Tesseract (isteğe bağlı)
    plaka, guven = _ocr_tesseract(image_bytes)
    if plaka:
        return plaka, guven

    # 3) Stub
    return None, 0.0


def plaka_tanimla_dosyadan(dosya_yolu: str) -> Tuple[Optional[str], float]:
    """Dosya yolundan görüntü okuyup plaka tanır."""
    if not os.path.isfile(dosya_yolu):
        return None, 0.0
    with open(dosya_yolu, "rb") as f:
        return plaka_tanimla(f.read())
