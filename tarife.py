# SmartPark53 - Park ücreti hesaplama

import math
from datetime import datetime

from db import now_turkey

# Tarife (TL): ilk 10 dakika sabit, sonrası dakika başı
ILK_10_DK_TUTAR = 20.0      # İlk 10 dakikada çıkan araçlar: 20 TL
SONRAKI_DK_BASI_TUTAR = 3.0  # 10 dakikadan sonraki her dakika: 3 TL
# Örnek: 1 saat (60 dk) = 20 + (60-10)*3 = 20 + 150 = 170 TL


def hesapla_borc(giris_iso: str, cikis_iso: str = None) -> float:
    """
    Giriş ve çıkış zamanına göre borç hesaplar (giriş/çıkış Türkiye saati kabul edilir).
    - İlk 10 dakika: 20 TL (10 dakikada çıkan araçlar)
    - 10 dakikadan sonra: her dakika 3 TL (örn. 1 saat = 20 + 50*3 = 170 TL)
    """
    try:
        giris = datetime.fromisoformat(giris_iso.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return 0.0
    if hasattr(giris, "tzinfo") and giris.tzinfo:
        giris = giris.replace(tzinfo=None)
    if cikis_iso:
        try:
            cikis = datetime.fromisoformat(cikis_iso.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            cikis = now_turkey()
    else:
        cikis = now_turkey()
    if cikis.tzinfo:
        cikis = cikis.replace(tzinfo=None)
    if giris.tzinfo:
        giris = giris.replace(tzinfo=None)
    if cikis < giris:
        return 0.0
    fark = cikis - giris
    toplam_dakika = fark.total_seconds() / 60
    if toplam_dakika <= 0:
        return 0.0
    # İlk 10 dk: 20 TL; sonrası her tam/başlayan dakika 3 TL (kesirli dakika yukarı yuvarlanır)
    if toplam_dakika <= 10:
        return round(ILK_10_DK_TUTAR, 2)
    ek_dakika = math.ceil(toplam_dakika - 10)  # 10 dk 31 sn → 1 dakika sayılır
    return round(ILK_10_DK_TUTAR + ek_dakika * SONRAKI_DK_BASI_TUTAR, 2)
