# SmartPark53 — Backend, Frontend ve Veritabanı İnceleme Raporu

Bu doküman, projenin backend (Flask), frontend (şablonlar) ve veritabanı katmanlarında yapılan inceleme ve düzeltmeleri özetler.

---

## 1. Yapılan düzeltmeler (bu incelemede uygulandı)

### Backend (app.py, db.py)

| Konu | Sorun | Çözüm |
|------|--------|--------|
| **Plaka kayıt – alan_id** | Formda geçersiz/olmayan alan_id gönderilirse FK hatası ve 500. | `alan_id` get_park_alanlari içinde kontrol ediliyor; geçersizse flash ve redirect. |
| **Plaka uzunluğu** | DB'de plaka VARCHAR(20); uzun plaka hata veya kesintiye yol açabilirdi. | Tüm form ve API'larda plaka 5–20 karakter kısıtı; aşanlarda anlamlı hata mesajı. |
| **Ödeme – tutar** | Negatif veya 0 tutar kabul ediliyordu; 0'da "Ödeme alındı" mesajı yanıltıcıydı. | Negatif tutar reddediliyor; 0'da "Lütfen ödeme tutarını girin."; sadece tutar > 0 ve kayıt varsa "Ödeme alındı". |
| **Ödeme – kayıt yok** | Plaka kayıtlı değilse odeme_yap False döner, kullanıcıya bilgi verilmiyordu. | False dönünce "Bu plaka için kayıt bulunamadı." flash mesajı. |
| **Otopark kapasitesi** | dolu >= kapasite iken yeni giriş kabul ediliyordu. | kayit_ekle öncesi kapasite kontrolü; doluysa ValueError("Bu otopark şu an dolu..."). |
| **API /api/giris** | Kapasite dolu iken 500. | ValueError yakalanıp 400 + hata mesajı dönülüyor. |

### Frontend (şablonlar)

| Konu | Sorun | Çözüm |
|------|--------|--------|
| **Plaka input** | Uzun metin girilebiliyordu. | Tüm plaka input'lara `maxlength="20"` eklendi. |
| **Tutar input** | Metin alanı; negatif veya geçersiz değer girilebiliyordu. | `type="number"`, `min="0"`, `step="0.01"` ile sadece geçerli tutar girilebilir. |

---

## 2. Veritabanı – mevcut durum ve notlar

- **Parametreli sorgular:** Tüm SQL parametreli (%s); SQL enjeksiyon riski yok.
- **İndeksler:** `park_kayit(plaka)`, `park_alani(ilce)` mevcut; plaka ile son kayıt sorguları makul hızda.
- **İşlemler:** get_db() ile commit/rollback doğru kullanılıyor.
- **dolu sayacı:** Çıkışta GREATEST(0, dolu-1) ile negatife düşme engelleniyor; girişte artık kapasite kontrolü var.

**İsteğe bağlı iyileştirmeler (ileride):**

- `park_alani` için CHECK (dolu >= 0 AND dolu <= kapasite) eklenebilir.
- Aynı plakanın aynı anda iki aktif girişi (cikis IS NULL) engellemek istenirse: unique kısıt veya uygulama tarafında “zaten parkta” kontrolü.

---

## 3. Güvenlik ve production notları

| Konu | Durum | Öneri |
|------|--------|--------|
| **SECRET_KEY** | .env'den okunuyor. | Production'da güçlü, rastgele key kullanın. |
| **CSRF** | Formlar CSRF token kullanmıyor. | Production'da Flask-WTF veya CSRF koruması ekleyin. |
| **API kimlik doğrulama** | /api/giris, /api/cikis, /api/borc açık. | Kamera/cihaz için API key veya token ile sınırlandırma düşünün. |
| **XSS** | Jinja2 varsayılan escape açık; kullanıcı girdisi escape ediliyor. | Ekstra HTML içerik göstermiyorsanız mevcut hali yeterli. |

---

## 4. Eksik veya ileride ele alınabilecekler

- **Rate limiting:** API ve form POST için istek sınırı yok; istenirse Flask-Limiter eklenebilir.
- **API /api/plaka-tanimla:** Yüklenen dosya boyutu sınırı yok; büyük dosyada bellek/süre riski. MAX_CONTENT_LENGTH veya boyut kontrolü eklenebilir.
- **Giriş/çıkış saat formatı:** Şu an ISO (örn. 2026-02-22T21:07:29). İstenirse şablonlarda "22.02.2026 21:07" gibi kısa format kullanılabilir.
- **Mobil / erişilebilirlik:** Formlar temel HTML; ARIA ve klavye kullanımı iyileştirilebilir.

---

## 5. Özet

- **Backend:** Plaka/alan doğrulama, kapasite kontrolü, ödeme kuralları ve API hata cevapları güçlendirildi.
- **Frontend:** Plaka ve tutar alanları sınırlandı ve türle uyumlu hale getirildi.
- **Veritabanı:** Mevcut tasarım ve kullanım tutarlı; kapasite kuralları uygulama tarafında uygulanıyor.

Yeni eklenen kontrollerle uygulama daha tutarlı ve hata durumlarında daha anlaşılır davranıyor. Production öncesi CSRF ve API kimlik doğrulama eklenmesi önerilir.
