# SmartPark53 - NextGen Mobility
# Flask web uygulaması

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from db import init_db, get_park_alanlari, get_son_kayit, kayit_ekle, cikis_yap, odeme_yap, RIZE_ILCELER
from tarife import hesapla_borc
# Yapay zeka plaka tanıma: plaka_tanima.plaka_tanimla() — şu an stub, model eklenecek
from plaka_tanima import plaka_tanimla

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "smartpark53-dev-key")


@app.context_processor
def inject_debug():
    """Şablonlarda cache önleme ve debug bilgisi."""
    return {"debug_mode": app.debug}


# Uygulama başlarken veritabanını hazırla
with app.app_context():
    init_db()


def plaka_norm(plaka: str) -> str:
    """Plakayı büyük harf ve boşluksuz normalize et."""
    return (plaka or "").upper().replace(" ", "").strip()


def _to_iso(val):
    """datetime veya string'i ISO string yap."""
    if val is None:
        return None
    if hasattr(val, "isoformat"):
        return val.isoformat()
    return str(val)


def kayit_to_dict(kayit):
    """Veritabanı kaydını şablonda kullanılacak formata çevirir (giris/cikis string)."""
    if not kayit:
        return None
    d = dict(kayit)
    giris = _to_iso(d.get("giris"))
    cikis = _to_iso(d.get("cikis"))
    d["giris"] = giris
    d["cikis"] = cikis
    odenen = float(d.get("odenen_tutar") or 0)
    borc_hesap = hesapla_borc(giris, cikis)
    d["borc"] = max(0, round(borc_hesap - odenen, 2))
    d["odenen_tutar"] = odenen
    return d


@app.route("/")
def index():
    return render_template("index.html", park_alanlari=get_park_alanlari())


@app.route("/plaka", methods=["GET", "POST"])
def plaka():
    if request.method == "POST":
        plaka_val = plaka_norm(request.form.get("plaka", ""))
        if not plaka_val or len(plaka_val) < 5:
            flash("Geçerli bir plaka girin (en az 5 karakter).", "error")
            return redirect(url_for("plaka"))
        if len(plaka_val) > 20:
            flash("Plaka en fazla 20 karakter olabilir.", "error")
            return redirect(url_for("plaka"))
        alan_id = (request.form.get("alan_id") or "p1").strip()
        park_alanlari = get_park_alanlari()
        if alan_id not in park_alanlari:
            flash("Geçersiz park alanı seçimi.", "error")
            return redirect(url_for("plaka"))
        try:
            kayit_ekle(plaka_val, alan_id)
        except ValueError as e:
            flash(str(e), "error")
            return redirect(url_for("plaka"))
        flash(f"Plaka {plaka_val} sisteme kaydedildi.", "success")
        return redirect(url_for("plaka"))
    return render_template("plaka.html", park_alanlari=get_park_alanlari())


@app.route("/borc", methods=["GET", "POST"])
def borc():
    if request.method == "POST":
        plaka_val = plaka_norm(request.form.get("plaka", ""))
        if not plaka_val:
            flash("Plaka girin.", "error")
            return redirect(url_for("borc"))
        if len(plaka_val) > 20:
            flash("Plaka en fazla 20 karakter olabilir.", "error")
            return redirect(url_for("borc"))
        kayit = get_son_kayit(plaka_val)
        kayit = kayit_to_dict(kayit)
        return render_template("borc_sonuc.html", plaka=plaka_val, kayit=kayit)
    return render_template("borc.html")


@app.route("/odeme", methods=["GET", "POST"])
def odeme():
    if request.method == "POST":
        plaka_val = plaka_norm(request.form.get("plaka", ""))
        tutar_str = request.form.get("tutar", "0").replace(",", ".")
        try:
            tutar = float(tutar_str)
        except ValueError:
            tutar = 0.0
        if not plaka_val:
            flash("Plaka girin.", "error")
            return redirect(url_for("odeme"))
        if len(plaka_val) > 20:
            flash("Plaka en fazla 20 karakter olabilir.", "error")
            return redirect(url_for("odeme"))
        if tutar < 0:
            flash("Tutar negatif olamaz.", "error")
            return redirect(url_for("odeme"))
        if tutar == 0:
            flash("Lütfen ödeme tutarını girin.", "error")
            return redirect(url_for("odeme"))
        if odeme_yap(plaka_val, tutar):
            flash("Ödeme alındı. Teşekkür ederiz.", "success")
            return redirect(url_for("odeme"))
        flash("Bu plaka için kayıt bulunamadı.", "error")
        return redirect(url_for("odeme", plaka=plaka_val))
    plaka_query = request.args.get("plaka", "").strip()
    return render_template("odeme.html", plaka_query=plaka_query)


@app.route("/cikis", methods=["GET", "POST"])
def cikis():
    """Çıkış gişesi: plaka girilir, çıkış saati yazılır, borç gösterilir, ödeme sayfasına link."""
    if request.method == "POST":
        plaka_val = plaka_norm(request.form.get("plaka", ""))
        if not plaka_val:
            flash("Plaka girin.", "error")
            return redirect(url_for("cikis"))
        if len(plaka_val) > 20:
            flash("Plaka en fazla 20 karakter olabilir.", "error")
            return redirect(url_for("cikis"))
        row = cikis_yap(plaka_val)
        if not row:
            flash("Bu plaka için aktif park kaydı bulunamadı.", "error")
            return redirect(url_for("cikis"))
        kayit = kayit_to_dict(row)
        return render_template(
            "cikis_sonuc.html",
            plaka=plaka_val,
            kayit=kayit,
        )
    return render_template("cikis.html")


@app.route("/harita")
def harita():
    ilce = request.args.get("ilce", "").strip() or None
    park_alanlari = get_park_alanlari(ilce=ilce)
    return render_template(
        "harita.html",
        park_alanlari=park_alanlari,
        ilceler=RIZE_ILCELER,
        secilen_ilce=ilce or "",
    )


@app.route("/api/plaka-tanimla", methods=["POST"])
def api_plaka_tanimla():
    """
    Yüklenen görüntüden plaka tanır (yapay zeka).
    Form: file = görsel dosyası.
    JSON döner: { "plaka": "34ABC123", "guven": 0.95 } veya plaka yoksa { "plaka": null, "guven": 0 }.
    """
    plaka, guven = None, 0.0
    if "file" in request.files:
        dosya = request.files["file"]
        if dosya.filename and dosya.filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            plaka, guven = plaka_tanimla(dosya.read())
    return jsonify({"plaka": plaka, "guven": round(guven, 2)})


# ---------- Kamera / cihaz entegrasyonu (BELEDIYE_AKIS_VE_API.md) ----------

@app.route("/api/giris", methods=["POST"])
def api_giris():
    """
    Giriş kaydı oluşturur (kamera plakayı okuduktan sonra çağrılır).
    JSON body: { "plaka": "34ABC123", "alan_id": "p1" }.
    Cevap: { "ok": true, "giris": "2025-02-22T10:00:00", "kayit_id": 123 } veya { "ok": false, "hata": "..." }.
    """
    data = request.get_json(silent=True) or {}
    plaka = plaka_norm((data.get("plaka") or "").strip())
    alan_id = (data.get("alan_id") or "").strip()
    if not plaka or len(plaka) < 5:
        return jsonify({"ok": False, "hata": "Geçerli plaka girin (en az 5 karakter)."}), 400
    if len(plaka) > 20:
        return jsonify({"ok": False, "hata": "Plaka en fazla 20 karakter olabilir."}), 400
    if not alan_id:
        return jsonify({"ok": False, "hata": "alan_id gerekli."}), 400
    park_alanlari = get_park_alanlari()
    if alan_id not in park_alanlari:
        return jsonify({"ok": False, "hata": "Geçersiz alan_id."}), 400
    try:
        giris_iso, kayit_id = kayit_ekle(plaka, alan_id)
        return jsonify({"ok": True, "giris": giris_iso, "kayit_id": kayit_id})
    except ValueError as e:
        return jsonify({"ok": False, "hata": str(e)}), 400
    except Exception as e:
        return jsonify({"ok": False, "hata": str(e)}), 500


@app.route("/api/cikis", methods=["POST"])
def api_cikis():
    """
    Çıkış işlemi: plakaya ait aktif kayda çıkış saati yazar, borcu hesaplar.
    JSON body: { "plaka": "34ABC123" }.
    Cevap: { "ok": true, "giris": "...", "cikis": "...", "borc_tl": 25.00, "odenen_tl": 0 }
    veya { "ok": false, "hata": "Aktif kayıt yok." }.
    """
    data = request.get_json(silent=True) or {}
    plaka = plaka_norm((data.get("plaka") or "").strip())
    if not plaka:
        return jsonify({"ok": False, "hata": "Plaka gerekli."}), 400
    if len(plaka) > 20:
        return jsonify({"ok": False, "hata": "Plaka en fazla 20 karakter olabilir."}), 400
    row = cikis_yap(plaka)
    if not row:
        return jsonify({"ok": False, "hata": "Bu plaka için aktif park kaydı yok."}), 404
    kayit = kayit_to_dict(row)
    borc = float(kayit.get("borc", 0))
    odenen = float(kayit.get("odenen_tutar", 0))
    return jsonify({
        "ok": True,
        "giris": kayit.get("giris"),
        "cikis": kayit.get("cikis"),
        "borc_tl": round(borc, 2),
        "odenen_tl": round(odenen, 2),
    })


@app.route("/api/borc", methods=["GET"])
def api_borc():
    """
    Plakaya göre güncel borç (son/aktif kayıt). Kiosk/ekran için.
    Query: ?plaka=34ABC123
    Cevap: { "plaka": "34ABC123", "giris": "...", "cikis": null, "borc_tl": 15.00, "odenen_tl": 0 }.
    """
    plaka = plaka_norm((request.args.get("plaka") or "").strip())
    if not plaka:
        return jsonify({"ok": False, "hata": "plaka parametresi gerekli."}), 400
    if len(plaka) > 20:
        return jsonify({"ok": False, "hata": "Plaka en fazla 20 karakter olabilir."}), 400
    kayit = get_son_kayit(plaka)
    kayit = kayit_to_dict(kayit) if kayit else None
    if not kayit:
        return jsonify({
            "plaka": plaka,
            "giris": None,
            "cikis": None,
            "borc_tl": 0.0,
            "odenen_tl": 0.0,
        })
    return jsonify({
        "plaka": plaka,
        "giris": kayit.get("giris"),
        "cikis": kayit.get("cikis"),
        "borc_tl": round(float(kayit.get("borc", 0)), 2),
        "odenen_tl": round(float(kayit.get("odenen_tutar", 0)), 2),
    })


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(debug=debug, host="0.0.0.0", port=5000)
