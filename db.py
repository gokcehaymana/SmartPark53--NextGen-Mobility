# SmartPark53 - Veritabanı (PostgreSQL)

import os
from datetime import datetime, timezone, timedelta
from contextlib import contextmanager

# Türkiye saati (Europe/Istanbul, UTC+3) — giriş/çıkış ve borç hesaplama için
try:
    from zoneinfo import ZoneInfo
    def now_turkey():
        return datetime.now(ZoneInfo("Europe/Istanbul")).replace(tzinfo=None)
except ImportError:
    _TURKEY_TZ = timezone(timedelta(hours=3))
    def now_turkey():
        return datetime.now(_TURKEY_TZ).replace(tzinfo=None)

# .env içinde DATABASE_URL=postgresql://kullanici:sifre@localhost:5432/smartpark53
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL tanımlı değil. .env dosyasına ekleyin: "
        "DATABASE_URL=postgresql://kullanici:sifre@localhost:5432/smartpark53"
    )


@contextmanager
def get_db():
    import psycopg2
    from psycopg2.extras import RealDictCursor
    conn = psycopg2.connect(DATABASE_URL)
    conn.cursor_factory = RealDictCursor
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Tabloları oluşturur ve örnek park alanlarını ekler."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS park_alani (
                id VARCHAR(20) PRIMARY KEY,
                ad TEXT NOT NULL,
                adres TEXT,
                kapasite INTEGER NOT NULL,
                dolu INTEGER NOT NULL DEFAULT 0,
                enlem DOUBLE PRECISION,
                boylam DOUBLE PRECISION,
                ilce VARCHAR(50) NOT NULL DEFAULT 'Rize Merkez'
            )
        """)
        cur.execute("ALTER TABLE park_alani ADD COLUMN IF NOT EXISTS ilce VARCHAR(50) NOT NULL DEFAULT 'Rize Merkez'")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS park_kayit (
                id SERIAL PRIMARY KEY,
                plaka VARCHAR(20) NOT NULL,
                alan_id VARCHAR(20) NOT NULL REFERENCES park_alani(id),
                giris TIMESTAMP NOT NULL,
                cikis TIMESTAMP,
                odenen_tutar NUMERIC(10,2) NOT NULL DEFAULT 0
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_plaka ON park_kayit(plaka)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_park_alani_ilce ON park_alani(ilce)")

        cur.execute("SELECT COUNT(*) AS n FROM park_alani")
        if cur.fetchone()["n"] == 0:
            # Rize ilçelerine göre 12 otopark. Merkez: Google Maps (41.028, 40.51) bölgesi + belediye kaynaklı gerçek isimler
            cur.executemany(
                """
                INSERT INTO park_alani (id, ad, adres, kapasite, dolu, enlem, boylam, ilce)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                [
                    # Rize Merkez — gerçek otoparklar (Rize Belediyesi / Google Maps bölgesi)
                    ("p1", "Rize Sahil Açık Otopark", "Sahil Dolgu Alanı, Rize Merkez", 300, 178, 41.0262, 40.5210, "Rize Merkez"),
                    ("p2", "Laleli Çarşısı Katlı Otopark", "Kültür Merkezi yanı, Laleli Mah. Rize Merkez", 300, 185, 41.0230, 40.5128, "Rize Merkez"),
                    ("p3", "Dalyan Kapalı Otopark", "Çamlıbel Mah. Dalyan Mevkii, Rize Merkez", 90, 42, 41.0185, 40.5085, "Rize Merkez"),
                    ("p4", "Rize Merkez Otopark", "Atatürk Cad., Rize Merkez", 60, 38, 41.0208, 40.5165, "Rize Merkez"),
                    ("p5", "Otopark Rize Merkez", "Merkez/Rize (sahil bandı)", 80, 52, 41.02796, 40.51369, "Rize Merkez"),
                    # Diğer ilçeler (Rize’nin 12 ilçesi)
                    ("p6", "Ardeşen Belediyesi Otopark", "Ardeşen Merkez", 50, 22, 41.1910, 40.9870, "Ardeşen"),
                    ("p7", "Çayeli Otopark", "Çayeli Merkez", 45, 18, 41.0890, 40.7420, "Çayeli"),
                    ("p8", "Pazar Otopark", "Pazar Merkez", 40, 25, 41.1790, 40.8870, "Pazar"),
                    ("p9", "İyidere Otopark", "İyidere Merkez", 35, 10, 41.0080, 40.3760, "İyidere"),
                    ("p10", "Derepazarı Otopark", "Derepazarı Merkez", 30, 12, 41.0160, 40.4180, "Derepazarı"),
                    ("p11", "Güneysu Otopark", "Güneysu Merkez", 35, 14, 40.9850, 40.6120, "Güneysu"),
                    ("p12", "Fındıklı Otopark", "Fındıklı Merkez", 40, 20, 41.2680, 41.1350, "Fındıklı"),
                ],
            )


# Rize ilçe listesi (resmi 12 ilçe)
RIZE_ILCELER = [
    "Rize Merkez", "Ardeşen", "Çamlıhemşin", "Çayeli", "Derepazarı",
    "Fındıklı", "Güneysu", "Hemşin", "İkizdere", "İyidere", "Kalkandere", "Pazar",
]


def get_park_alanlari(ilce=None):
    """Park alanlarını döner. ilce verilirse sadece o ilçedekiler."""
    with get_db() as conn:
        cur = conn.cursor()
        if ilce:
            cur.execute(
                "SELECT id, ad, adres, kapasite, dolu, enlem, boylam, ilce FROM park_alani WHERE ilce = %s ORDER BY id",
                (ilce,),
            )
        else:
            cur.execute("SELECT id, ad, adres, kapasite, dolu, enlem, boylam, ilce FROM park_alani ORDER BY ilce, id")
        rows = cur.fetchall()
        return {row["id"]: dict(row) for row in rows}


def get_aktif_kayit(plaka: str):
    """Plakaya ait çıkış yapılmamış (hala parkta) kaydı döner."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT id, plaka, alan_id, giris, cikis, odenen_tutar
               FROM park_kayit WHERE plaka = %s AND cikis IS NULL
               ORDER BY giris DESC LIMIT 1""",
            (plaka,),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def get_son_kayit(plaka: str):
    """Plakaya ait en son kaydı döner (aktif veya son çıkış yapılan)."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT id, plaka, alan_id, giris, cikis, odenen_tutar
               FROM park_kayit WHERE plaka = %s ORDER BY giris DESC LIMIT 1""",
            (plaka,),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def kayit_ekle(plaka: str, alan_id: str):
    """Yeni park girişi ekler. Giriş saati Türkiye (Europe/Istanbul) olarak kaydedilir. Kapasite doluysa ValueError. Döner: (giris_iso, kayit_id)."""
    giris = now_turkey()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT kapasite, dolu FROM park_alani WHERE id = %s",
            (alan_id,),
        )
        row_alani = cur.fetchone()
        if not row_alani:
            raise ValueError("Geçersiz park alanı.")
        if row_alani["dolu"] >= row_alani["kapasite"]:
            raise ValueError("Bu otopark şu an dolu. Lütfen başka alan seçin.")
        cur.execute(
            """INSERT INTO park_kayit (plaka, alan_id, giris, odenen_tutar)
               VALUES (%s, %s, %s, 0) RETURNING id""",
            (plaka, alan_id, giris),
        )
        row = cur.fetchone()
        kayit_id = row["id"] if row else None
        cur.execute("UPDATE park_alani SET dolu = dolu + 1 WHERE id = %s", (alan_id,))
    return (giris.isoformat(), kayit_id)


def cikis_yap(plaka: str):
    """
    Plakaya ait aktif (çıkış yapılmamış) kayda çıkış saati yazar ve otopark doluluk sayacını düşürür.
    Döner: güncellenmiş kayıt dict (giris, cikis ISO string) veya None (aktif kayıt yoksa).
    """
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT id, alan_id, giris, odenen_tutar
               FROM park_kayit WHERE plaka = %s AND cikis IS NULL
               ORDER BY giris DESC LIMIT 1""",
            (plaka,),
        )
        row = cur.fetchone()
        if not row:
            return None
        kayit_id = row["id"]
        alan_id = row["alan_id"]
        cikis_ts = now_turkey()
        cur.execute(
            """UPDATE park_kayit SET cikis = %s WHERE id = %s
               RETURNING id, plaka, alan_id, giris, cikis, odenen_tutar""",
            (cikis_ts, kayit_id),
        )
        updated = cur.fetchone()
        cur.execute("UPDATE park_alani SET dolu = GREATEST(0, dolu - 1) WHERE id = %s", (alan_id,))
        if updated:
            out = dict(updated)
            out["giris"] = out["giris"].isoformat() if hasattr(out["giris"], "isoformat") else str(out["giris"])
            out["cikis"] = out["cikis"].isoformat() if hasattr(out["cikis"], "isoformat") else str(out["cikis"])
            return out
    return None


def odeme_yap(plaka: str, tutar: float):
    """Plakanın en son park kaydına (çıkış yapılmış olsa da) ödeme ekler. Böylece çıkış yaptıktan sonra ödenen borç da kayda geçer."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT id FROM park_kayit WHERE plaka = %s ORDER BY giris DESC LIMIT 1""",
            (plaka,),
        )
        row = cur.fetchone()
        if not row:
            return False
        cur.execute(
            """UPDATE park_kayit SET odenen_tutar = odenen_tutar + %s WHERE id = %s""",
            (tutar, row["id"]),
        )
        return cur.rowcount > 0
