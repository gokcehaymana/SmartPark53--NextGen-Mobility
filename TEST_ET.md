# SmartPark53 — Siteyi test etme

## Seçenek 1: Docker ile (önerilen)

Terminalde proje klasörüne gidin ve:

```bash
docker-compose up -d --build
```

- İlk seferde image build birkaç dakika sürebilir.
- Bittikten sonra tarayıcıda açın: **http://localhost:5000**

Durdurmak için:

```bash
docker-compose down
```

---

## Seçenek 2: Yerel Python + PostgreSQL

1. **PostgreSQL** çalışıyor olmalı ve `.env` içindeki bağlantı geçerli:
   - `DATABASE_URL=postgresql://admin:password@localhost:5432/smartpark53`
   - Veritabanı `smartpark53` ve kullanıcı `admin` / şifre `password` (veya kendi ayarınız).

2. Gerekli paketleri kurun (henüz kurmadıysanız):

   ```bash
   pip install -r requirements.txt
   ```

3. Uygulamayı başlatın:

   ```bash
   python app.py
   ```

4. Tarayıcıda açın: **http://localhost:5000**

---

## Test akışı (kısa)

1. **Ana sayfa** — Dört kutu (Plaka kaydet, Borç sorgula, Ödeme yap, Harita) ve otopark listesi görünmeli.
2. **Plaka Kayıt** — Bir plaka (örn. `34 ABC 123`) ve otopark seçip “Kaydet”; başarı mesajı gelmeli.
3. **Borç Sorgula** — Aynı plakayı yazıp “Sorgula”; giriş saati ve borç görünmeli.
4. **Çıkış** — Aynı plakayı yazıp “Çıkış yap”; giriş/çıkış saati ve borç çıkmalı, “Ödeme yap” linki çalışmalı.
5. **Ödeme** — Plaka (ve isteğe bağlı tutar) girip “Ödeme yap”; çıkış sonrası bu plakayla ödeme sayfasına `?plaka=...` ile gidince alan dolu olmalı.
6. **Harita** — İlçe seçip “Göster”; harita ve otopark listesi güncellenmeli.

---

## API testi (isteğe bağlı)

- **Giriş:**  
  `POST http://localhost:5000/api/giris`  
  Body (JSON): `{"plaka": "34ABC123", "alan_id": "p1"}`

- **Çıkış:**  
  `POST http://localhost:5000/api/cikis`  
  Body (JSON): `{"plaka": "34ABC123"}`

- **Borç:**  
  `GET http://localhost:5000/api/borc?plaka=34ABC123`

Postman, curl veya tarayıcı eklentisi ile deneyebilirsiniz.
