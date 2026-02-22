#!/usr/bin/env python3
"""
PostgreSQL şifresini ve bağlantıyı test eder.
.env içindeki DATABASE_URL kullanır; sadece bağlanıp kapatır.

Kullanım: python check_db.py
"""

import os
import sys
import socket
import subprocess
from urllib.parse import urlparse, unquote, quote_plus

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def main():
    url = os.environ.get("DATABASE_URL")
    if not url or not url.strip().startswith(("postgresql://", "postgres://")):
        print("HATA: .env dosyasında DATABASE_URL tanımlı değil veya geçersiz.")
        sys.exit(1)

    p = urlparse(url.strip())
    if not p.hostname:
        print("HATA: DATABASE_URL ayrıştırılamadı.")
        sys.exit(1)

    user = p.username or "postgres"
    password = unquote(p.password) if p.password else ""
    host = p.hostname
    port = int(p.port or 5432)

    # 1) Port 5432 açık mı? (servis dinliyor mu?)
    try:
        with socket.create_connection((host, port), timeout=3) as sock:
            sock.close()
        print(f"Port {port} açık — PostgreSQL dinliyor.")
    except (socket.timeout, socket.error, OSError) as port_err:
        print(f"Port {port} kapalı veya erişilemiyor: {port_err}")
        print("PostgreSQL servisini başlatın (services.msc → postgresql) veya farklı port kullanıyorsanız .env'de belirtin.")
        if sys.platform == "win32":
            try:
                out = subprocess.run(
                    ["powershell", "-NoProfile", "-Command",
                     "Get-Service -Name '*postgres*' -ErrorAction SilentlyContinue | Select-Object Name, Status | Format-Table -AutoSize"],
                    capture_output=True, text=True, timeout=5
                )
                if out.returncode == 0 and out.stdout.strip():
                    print("\nPostgreSQL servis durumu:")
                    print(out.stdout.strip())
            except Exception:
                pass
        sys.exit(1)

    conn_url = f"postgresql://{user}:{quote_plus(password)}@{host}:{port}/postgres"

    # 2) Şifre ve oturum kontrolü
    try:
        import psycopg2
        conn = psycopg2.connect(conn_url)
        conn.close()
        print("PostgreSQL bağlantısı başarılı. Şifre doğru.")
        return
    except Exception as e:
        err = str(e).lower()
        print()
        if "password authentication failed" in err or "no password supplied" in err:
            print(">>> ŞİFRE YANLIŞ <<<")
            print("PostgreSQL kullanıcı adı/şifresi kabul edilmedi.")
            print(".env dosyasındaki DATABASE_URL içinde şifreyi kontrol edin.")
        elif "connection refused" in err or "could not connect" in err:
            print(">>> SERVİS KAPALI VEYA ERİŞİLEMİYOR <<<")
            print("PostgreSQL çalışmıyor olabilir veya port (5432) yanlış.")
            print("Kontrol: Hizmetler (services.msc) → 'postgresql' servisini 'Çalışıyor' yapın.")
            print("Veya PowerShell: Get-Service -Name '*postgres*'")
        elif "timeout" in err or "timed out" in err:
            print(">>> ZAMAN AŞIMI <<<")
            print("PostgreSQL yanıt vermiyor; servis kapalı veya güvenlik duvarı engelliyor olabilir.")
        else:
            print(">>> BAĞLANTI HATASI <<<")
            print("Aşağıdaki hata mesajına göre .env veya PostgreSQL ayarlarını kontrol edin.")
        print()
        print(f"Teknik hata: {e}")
        # Windows: PostgreSQL servis durumunu göster
        if sys.platform == "win32":
            try:
                out = subprocess.run(
                    ["powershell", "-NoProfile", "-Command",
                     "Get-Service -Name '*postgres*' -ErrorAction SilentlyContinue | Select-Object Name, Status | Format-Table -AutoSize"],
                    capture_output=True, text=True, timeout=5
                )
                if out.returncode == 0 and out.stdout.strip():
                    print("PostgreSQL servis durumu (Windows):")
                    print(out.stdout.strip())
                elif out.returncode == 0 and not out.stdout.strip():
                    print("PostgreSQL servisi bulunamadı (farklı isimle kurulmuş olabilir).")
            except Exception:
                pass
        sys.exit(1)


if __name__ == "__main__":
    main()
