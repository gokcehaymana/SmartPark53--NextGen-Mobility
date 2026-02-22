# SmartPark53 — Belediyelere Satış: Akış ve API

Bu doküman, otopark kameraları ile otomatik plaka okuma ve giriş/çıkış borç hesaplama akışını tanımlar. Ürün belediyelere satılacak; kameralar girişte plakayı okuyup sisteme otomatik kayıt atacak, çıkışta süre hesaplanıp borç gösterilecek.

---

## 1. Ürün özeti

| Özellik | Açıklama |
|--------|----------|
| **Hedef** | Belediyeler (otopark yönetimi) |
| **Giriş** | Otopark girişindeki kamera plakayı okur → sisteme otomatik kayıt (plaka + alan + giriş saati) |
| **Çıkış** | Çıkıştaki kamera veya kiosk plakayı okur/girilir → çıkış saati yazılır → borç hesaplanır → ekranda/ödeme noktasında borç gösterilir |
| **Borç** | Giriş–çıkış süresine göre tarifeden hesaplanır; ödeme yapılabilir. |

---

## 2. Genel akış (metin)

```
[GİRİŞ]
  Kamera (giriş) → Görüntü → Plaka tanıma (AI/OCR) → Plaka metni
       → API: "giriş kaydı oluştur" (plaka, alan_id) → giriş saati = şimdi
  Araç otoparkta; kayıt "aktif" (çıkış saati yok).

[ÇIKIŞ]
  Kamera (çıkış) veya kiosk → Plaka (okuma veya manuel)
       → API: "çıkış yap" (plaka) → çıkış saati = şimdi
       → Borç hesapla (giriş–çıkış, tarife)
  Ekranda: "Borç: X TL" → Ödeme (nakit/kart/kiosk) → İsteğe bağlı bariyer açılır.
```

---

## 3. Ekranlar ve roller

| Sayfa / Ekran | Rol | Kullanım |
|---------------|-----|----------|
| **Ana sayfa** | Vatandaş / personel | Hızlı erişim: plaka kayıt, borç sorgula, ödeme, harita. |
| **Plaka kayıt** | Manuel giriş (kamera yokken veya yedek) | Plaka + otopark seçimi → giriş kaydı. İleride "fotoğraf yükle" ile kamera simülasyonu. |
| **Borç sorgula** | Vatandaş / çıkış gişesi | Plaka gir → giriş saati, hesaplanan/ödenen/kalan borç. |
| **Ödeme** | Gişe / kiosk | Plaka + tutar → ödeme kaydı. |
| **Harita** | Vatandaş | Otoparklar, ilçe filtresi, doluluk. |
| **Çıkış ekranı (önerilen)** | Çıkış gişesi / kiosk | Plaka okundu veya girildi → tek ekranda: giriş saati, çıkış saati, borç, "Öde" butonu. |
| **API (kamera / cihaz)** | Kapı kamerasi, bariyer sistemi | Giriş: plaka + alan_id → kayıt. Çıkış: plaka → cikis yaz, borç dön. |

---

## 4. API uçları

### 4.1 Mevcut API’ler

| Metot | URL | Açıklama |
|-------|-----|----------|
| `POST` | `/api/plaka-tanimla` | Görselden plaka tanıma. Form: `file` = görsel. Cevap: `{ "plaka": "34ABC123", "guven": 0.95 }`. |

### 4.2 Önerilen API’ler (kamera / cihaz entegrasyonu)

| Metot | URL | Açıklama |
|-------|-----|----------|
| `POST` | `/api/giris` | **Giriş kaydı.** Body (JSON): `{ "plaka": "34ABC123", "alan_id": "p1" }`. Cevap: `{ "ok": true, "giris": "2025-02-22T10:00:00", "kayit_id": 123 }`. Kamera plakayı okuduktan sonra bu uç çağrılır. |
| `POST` | `/api/cikis` | **Çıkış işlemi.** Body (JSON): `{ "plaka": "34ABC123" }`. Cevap: `{ "ok": true, "giris": "...", "cikis": "...", "borc_tl": 25.00, "odenen_tl": 0 }`. Çıkış kamerası veya kiosk plakayı gönderir; sistem çıkış saatini yazar ve borcu hesaplar. |
| `GET` | `/api/borc?plaka=34ABC123` | Plakaya göre güncel borç (son/aktif kayıt). Cevap: `{ "plaka": "34ABC123", "giris": "...", "cikis": null, "borc_tl": 15.00, "odenen_tl": 0 }`. Kiosk/ekran borç göstermek için kullanılır. |

Bu uçlar eklenince kamera tarafı sadece HTTP isteği atacak; ek geliştirme giriş/çıkış ekranları ve ödeme ile birleştirilebilir.

---

## 5. Veri modeli (özet)

- **park_alani:** Otoparklar (id, ad, adres, kapasite, dolu, ilce, enlem, boylam).
- **park_kayit:** Her giriş için bir kayıt: plaka, alan_id, **giris** (zorunlu), **cikis** (çıkışta doldurulur), odenen_tutar.  
  Çıkış yapılmamış kayıt: `cikis IS NULL`.
- **Borç:** `tarife.hesapla_borc(giris, cikis)` ile hesaplanır; `cikis` yoksa “şimdi” kullanılır. Ödenen tutar düşülür.

---

## 6. Mevcut kodla eşleşme

| Bileşen | Dosya | Durum |
|---------|--------|--------|
| Plaka tanıma | `plaka_tanima.py` | Harici API (`PLAKA_API_URL`) veya isteğe bağlı Tesseract; yoksa stub. |
| Giriş kaydı | `db.kayit_ekle(plaka, alan_id)` | Var. |
| Aktif kayıt | `db.get_aktif_kayit(plaka)` | Var (çıkış yapılmamış kayıt). |
| Son kayıt / borç | `db.get_son_kayit(plaka)` + `kayit_to_dict` + `tarife.hesapla_borc` | Var. |
| Ödeme | `db.odeme_yap(plaka, tutar)` | Var. |
| Çıkış saati yazma | `db.cikis_yap(plaka)` | Var. Çıkış saati yazılır, `park_alani.dolu` düşürülür. |

---

## 7. Yapılacaklar (kısa)

1. ~~**Çıkış kaydı:** `db.py` içinde `cikis_yap(plaka)`~~ ✅ **Yapıldı.** `db.cikis_yap(plaka)` çıkış saati yazar ve `park_alani.dolu` düşürür.
2. ~~**API:** `/api/giris`, `/api/cikis`, `/api/borc` uçları~~ ✅ **Yapıldı.** (Bkz. `app.py`.)
3. ~~**Çıkış ekranı (opsiyonel):**~~ ✅ **Yapıldı.** `/cikis`: plaka girişi → çıkış kaydı → borç özeti → “Öde” Ödeme yap linki (plaka dolu).
4. ~~**Plaka tanıma:**~~ ✅ **Hazır.** Harici API (`PLAKA_API_URL`) veya isteğe bağlı Pytesseract+Pillow; yoksa stub.

Bu doküman, belediye satışı ve kamera entegrasyonu için referans akış ve API taslağı olarak kullanılabilir.
