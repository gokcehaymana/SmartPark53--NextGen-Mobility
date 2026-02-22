#!/usr/bin/env python3
"""
SmartPark53 - PostgreSQL veritabanını oluşturur.
.env içindeki DATABASE_URL kullanır; veritabanı yoksa ekler.

Kullanım: python create_db.py
"""

import os
import sys
from urllib.parse import urlparse, unquote

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def parse_database_url(url):
    """postgresql://user:pass@host:port/dbname -> (user, password, host, port, dbname)"""
    url = url.strip()
    if not url.startswith("postgresql://") and not url.startswith("postgres://"):
        return None
    # urlparse ile güvenli ayrıştırma
    p = urlparse(url)
    if p.hostname is None:
        return None
    host = p.hostname
    port = p.port or 5432
    path = (p.path or "/smartpark53").strip("/")
    dbname = path.split("?")[0] or "smartpark53"
    user = (p.username or "postgres")
    password = unquote(p.password) if p.password else ""
    return (user, password, host, port, dbname)


def main():
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("HATA: .env dosyasında DATABASE_URL tanımlı değil.")
        print("Örnek: DATABASE_URL=postgresql://postgres:SIFRE@localhost:5432/smartpark53")
        sys.exit(1)

    parsed = parse_database_url(url)
    if not parsed:
        print("HATA: DATABASE_URL geçersiz. Örnek: postgresql://postgres:SIFRE@localhost:5432/smartpark53")
        sys.exit(1)
    user, password, host, port, dbname = parsed

    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

    # Önce 'postgres' veritabanına bağlan (varsayılan)
    from urllib.parse import quote_plus
    safe_pass = quote_plus(password) if password else ""
    conn_url = f"postgresql://{user}:{safe_pass}@{host}:{port}/postgres"
    try:
        conn = psycopg2.connect(conn_url)
    except Exception as e:
        print(f"Bağlantı hatası (postgres): {e}")
        print("Kullanıcı adı ve şifrenizi kontrol edin. Varsayılan kullanıcı genelde 'postgres'tir.")
        sys.exit(1)

    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
    if cur.fetchone():
        print(f"Veritabanı '{dbname}' zaten mevcut.")
    else:
        cur.execute(f'CREATE DATABASE "{dbname}"')
        print(f"Veritabanı '{dbname}' oluşturuldu.")

    cur.close()
    conn.close()
    print("Tamamlandı. Uygulamayı başlatmak için: python app.py")

if __name__ == "__main__":
    main()
