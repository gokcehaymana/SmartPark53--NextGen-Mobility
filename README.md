# SmartPark53: NextGen Mobility

**Akıllı Algılama Teknolojisiyle Yeni Nesil Parkomat Platformu**

Rize Belediyesi için geliştirilen SmartPark53, belediye park alanlarının yapay zekâ destekli otonom yönetimini hedefleyen, mobil öncelikli web tabanlı bir platformdur. Harita ve örnek otoparklar Rize merkez koordinatlarına göre tanımlıdır.

---

## Proje Özeti

### Mevcut Durum ve Temel Sorunlar

Günümüzde belediye sınırları içerisinde sunulan parkomat hizmetleri büyük ölçüde **insan gücüne dayalı geleneksel yöntemlerle** yürütülmektedir. Bu yapı:

- **Yüksek personel maliyetleri** ve park alanlarının verimsiz kullanımına,
- Denetim süreçlerinde **ciddi aksama**lara,
- Park sürelerinin sağlıklı takip edilememesine ve **ödeme kaçakları**na,
- Yoğun bölgelerde araçların uzun süreli işgaliyle **trafik akışının olumsuz etkilenmesi**ne yol açmaktadır.

Geçmişte denenen kamera ve plaka tanıma çözümleri ise yüksek yazılım maliyetleri ve düşük doğruluk oranları nedeniyle sürdürülebilir bir model sunamamıştır.

---

### Teknolojik Çözüm ve İşleyiş

SmartPark53, **düşük maliyetli donanım** ile **yüksek performanslı derin öğrenme algoritmalarını** bir araya getiren otonom bir sistem sunar:

- Park alanlarının giriş ve çıkış noktalarına yerleştirilen **akıllı kameralar** ile araç plakaları otomatik tanımlanır.
- Giriş saati **milisaniyelik hassasiyetle** kaydedilir; çıkış anında park süresi müdahalesiz, dijital ortamda hesaplanır.

**Kullanıcı tarafında** herhangi bir uygulama indirme zorunluluğu yoktur. Platform **mobil öncelikli ve web tabanlıdır**:

| Özellik | Açıklama |
|--------|----------|
| Erişim | QR kod veya doğrudan web adresi |
| Plaka tanımlama | Araç plakalarının sisteme kaydı |
| Borç sorgulama | Güncel borçların anlık görüntülenmesi |
| Ödeme | Güvenli dijital altyapı üzerinden ödeme |
| Harita | Park alanlarının anlık doluluk durumu, en yakın uygun noktaya yönlendirme |

Böylece teknoloji, cihazlarda yer kaplayan maliyetli bir yük olmaktan çıkar; her an erişilebilir ve verimli bir işletme aracına dönüşür.

---

### Stratejik Hedefler ve Operasyonel Verimlilik

Ana hedef: Kentsel park yönetimini **insan gücüne dayalı yapıdan**, **yapay zekâ destekli otonom bir ekosisteme** dönüştürmek; belediye kaynaklarını optimize etmek ve 
şehir içi hareketliliği dijitalleştirmek.

**Alt hedefler:**

- Park operasyonlarındaki **personel bağımlılığını ve işletme maliyetlerini** minimize etmek.
- Yasaklı alan işgallerini ve süre ihlallerini **anlık tespit eden denetim mekanizması** kurmak.
- **Uygulama indirme zorunluluğu olmadan** web tabanlı erişimle park yeri arama süresini kısaltmak; yakıt israfı ve karbon salınımını azaltmak.
- Finansal süreçleri **%100 şeffaflıkla** dijital ortama taşıyarak gelir kaçaklarını önlemek ve vatandaş için güvenilir, hızlı bir hizmet standardı oluşturmak.

---

### Yarattığı Katma Değer ve Gelecek Vizyonu

Proje, operasyonel kolaylığın ötesinde **çok katmanlı bir veri ekosistemi** ve **stratejik karar destek mekanizması** sunar:

- **Veri analitiği:** Kullanım sıklığı, bölge bazlı doluluk oranları, yoğun saat analizleri ve gelir projeksiyonları ile şehir planlama süreçleri bilimsel verilere 
dayandırılabilir.
- **Belediye:** Otonom denetimle hata payı ve gelir kaçakları azaltılır; bütçeye ölçülebilir pozitif etki sağlanır.
- **Vatandaş:** Dijital ödeme ve canlı doluluk takibi ile park yeri arama stresi azalır; memnuniyet ve kurumsal güven artar.
- **Çevre:** Trafik dolaşım süresinin kısalması; karbon ayak izinin azalması ve yakıt tasarrufu ile ekolojik fayda sağlanır.

Sonuç olarak SmartPark53; **maliyeti düşüren**, **geliri artıran**, **çevreyi koruyan** ve **vatandaş deneyimini dijitalleştiren** bütünsel bir akıllı şehir dönüşümü 
hedefler.

---

## Web uygulaması (Python / Flask)

Proje, mobil öncelikli web arayüzü ile birlikte gelir. Uygulama indirme zorunluluğu yoktur.

### Gereksinimler

- **Docker + Docker Compose** (önerilen — tüm proje container’da çalışır, sunucuya taşımaya hazır)
- veya: Python 3.10+, pip, PostgreSQL (yerel geliştirme için)

### Çalıştırma — Docker (tüm proje)

Proje tamamen Docker’da çalışacak şekilde yapılandırıldı; birkaç ay sonra sunucuya taşındığında aynı yapı kullanılabilir.

```bash
docker-compose up -d
```

- **PostgreSQL** ve **web uygulaması** ayağa kalkar.  
- Tarayıcıda **http://localhost:5000** açın.  
- Tablolar ilk açılışta otomatik oluşturulur.  
- Durdurmak: `docker-compose down`

İsteğe bağlı: `.env` dosyasında `SECRET_KEY` tanımlayabilirsiniz; yoksa varsayılan kullanılır.

### Çalıştırma — Yerel (geliştirme)

**Yerel PostgreSQL kullanıyorsanız:**  
- `.env`: `DATABASE_URL=postgresql://admin:password@localhost:5432/smartpark53` (veya postgres/şifre)  
- `python create_db.py` → `python app.py`  
- **http://127.0.0.1:5000**

### Sayfalar

| Sayfa | Açıklama |
|-------|----------|
| Ana Sayfa | Hızlı erişim ve park alanları özeti |
| Plaka Kayıt | Araç plakası ve park alanı kaydı |
| Borç Sorgula | Plakaya göre güncel borç (süreye göre hesaplanan + ödenen) |
| Ödeme | Borç ödeme (kayıt güncellenir) |
| Harita | Park alanları doluluk haritası (OpenStreetMap) |

### Veritabanı (PostgreSQL)

- **Docker:** `docker-compose up -d` ile hem PostgreSQL hem web aynı ağda çalışır; veritabanı otomatik oluşturulur (admin/password, DB: smartpark53).
- **Yerel:** `.env` → `DATABASE_URL`. Docker’daki DB’ye yerelden script çalıştırıyorsanız `admin:password@localhost:5432/smartpark53` kullanın; yerel PostgreSQL ise `postgres/şifre` veya `admin/password`, sonra `python create_db.py` ile **smartpark53** oluşturun.
- Tablolar (`park_alani`, `park_kayit`) uygulama ilk açıldığında otomatik oluşturulur.
- **Rize otoparkları:** İlk kurulumda Rize merkeze uygun 4 örnek otopark (Sahil Açık, Merkez, Laleli Katlı, Dalyan Kapalı) yüklenir. Veritabanı daha önce oluşturulduysa yeni otoparkları almak için volume’u sıfırlayabilirsiniz: `python seed_rize_otopark.py` (yerel) veya `docker-compose down -v` sonra `docker-compose up -d` (Docker).
- **Tarife:** İlk 1 saat 15 TL, sonraki her saat 5 TL. `tarife.py` içinden değiştirilebilir.

### Sunucuya taşıma (birkaç ay sonra)

- Sunucuda Docker kurulu olmalı. Repoyu klonlayıp `docker-compose up -d` çalıştırmanız yeterli.
- Sunucuda `.env` ile `SECRET_KEY` ve gerekirse `DATABASE_URL` (harici PostgreSQL kullanacaksanız) tanımlayın.
- Trafik 80/443’e yönlendirmek için Nginx veya Caddy önüne alınabilir; uygulama 5000 portunda dinler.

### Yapay zeka ile plaka tanıma

- **Modül:** `plaka_tanima.py` — kamera veya yüklenen görüntüden plaka okuma için entegrasyon noktası.
- **API:** `POST /api/plaka-tanimla` — form ile `file` (görsel) gönderilir; yanıt `{ "plaka": "...", "guven": 0.95 }`.
- Şu an **stub** (her zaman `plaka: null`); gerçek model (OCR / YOLO / hazır API) bu modüle eklenecek. Giriş/çıkış kameralarından gelen görüntü bu API veya doğrudan `plaka_tanimla()` ile işlenebilir.

---

## Ekip

| Ad Soyad | Rol |
|----------|-----|
| **Gökçe Nur Haymana** | Bilgisayar Mühendisliği, 3. sınıf |
| **Hayrunnisa Birkan** | Bilgisayar Mühendisliği, 1. sınıf |

---

## Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.
