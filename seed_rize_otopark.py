#!/usr/bin/env python3
"""
park_alani tablosunu boşaltıp Rize otoparklarını yeniden yükler.
Kullanım: python seed_rize_otopark.py

Docker ile çalışıyorsanız .env içinde:
  DATABASE_URL=postgresql://admin:password@localhost:5432/smartpark53
olmalı (konteyner admin/password kullanır).
"""

import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# db modülü DATABASE_URL ister; import etmeden önce .env yüklü olmalı
from db import get_db, init_db

def main():
    if not os.environ.get("DATABASE_URL"):
        print("HATA: .env dosyasında DATABASE_URL tanımlı değil.")
        sys.exit(1)

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM park_kayit")
        n_kayit = cur.rowcount
        cur.execute("DELETE FROM park_alani")
        n_alani = cur.rowcount

    print(f"park_kayit: {n_kayit} satır silindi.")
    print(f"park_alani: {n_alani} satır silindi.")

    init_db()
    print("Rize otoparkları (12 adet, ilçelere göre) yeniden yüklendi.")
    print("Uygulamayı yeniden başlatmanıza gerek yok; sayfayı yenileyin.")

if __name__ == "__main__":
    main()
