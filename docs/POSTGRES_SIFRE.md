# PostgreSQL kullanıcı adı ve şifre

## Kullanıcı adı

- **Varsayılan:** Neredeyse her kurulumda süper kullanıcı adı **`postgres`** dir.
- Farklı bir kullanıcı oluşturduysanız onu kullanırsınız; yoksa `.env` içinde `postgres` yazın.

## Şifreyi hatırlamıyorsanız

PostgreSQL şifreyi şifreli saklar; **sistemden “şifreyi göster” diye okuyamazsınız.** İki yolunuz var:

### 1) Eski projede kullandığınız şifre

Başka bir web projesinde PostgreSQL kullandıysanız, o projenin klasöründeki **`.env`** veya **`config`** dosyasında `DATABASE_URL` veya `POSTGRES_PASSWORD` gibi bir satır olabilir. Oradaki şifreyi SmartPark53 projesindeki `.env` dosyasında kullanmayı deneyin.

### 2) Şifreyi sıfırlama (Windows)

Şifreyi hiç hatırlamıyorsanız, aşağıdaki adımlarla **yeni bir şifre** belirleyebilirsiniz.

#### Adım 1: pg_hba.conf dosyasını bulun

- Kurulum genelde: `C:\Program Files\PostgreSQL\16\data\pg_hba.conf` (16 yerine kendi sürüm numaranız olabilir: 14, 15, 16).
- Veya **pgAdmin** açın → sol tarafta sunucuya sağ tık → **Properties** → **Connection** sekmesinde **Configuration file** yolunu görebilirsiniz; aynı klasörde `pg_hba.conf` vardır.

#### Adım 2: Geçici olarak şifresiz girişe izin verin

1. **Not Defteri’ni yönetici olarak** açın, `pg_hba.conf` dosyasını açın.
2. İçinde `METHOD` yazan satırları bulun. Örnek:
   ```
   # IPv4 local connections:
   host    all    all    127.0.0.1/32    scram-sha-256
   ```
3. Son kısımdaki **`scram-sha-256`** (veya `md5`) ifadesini **`trust`** yapın:
   ```
   host    all    all    127.0.0.1/32    trust
   ```
4. Dosyayı kaydedin.

#### Adım 3: PostgreSQL servisini yeniden başlatın

- **services.msc** açın (Win + R → `services.msc`) → **postgresql-x64-16** (veya sürümünüz) → Sağ tık → **Yeniden Başlat**.

#### Adım 4: Yeni şifre belirleyin

PowerShell veya CMD’de:

```bash
psql -U postgres -h localhost
```

Şifre sorulmadan girmeniz gerekir. Girdikten sonra:

```sql
ALTER USER postgres PASSWORD 'YeniBelirlediginizSifre';
\q
```

`YeniBelirlediginizSifre` yerine kullanmak istediğiniz şifreyi yazın.

#### Adım 5: pg_hba.conf’u eski haline getirin

1. `pg_hba.conf` dosyasında **`trust`** yaptığınız yeri tekrar **`scram-sha-256`** (veya önceden ne yazıyorsa) yapın.
2. Dosyayı kaydedin.
3. PostgreSQL servisini tekrar **Yeniden Başlat**ın.

#### Adım 6: .env dosyasını güncelleyin

SmartPark53 projesindeki `.env` dosyasında:

```env
DATABASE_URL=postgresql://postgres:YeniBelirlediginizSifre@localhost:5432/smartpark53
```

Bu şekilde kaydedin. Sonra `python check_db.py` ile bağlantıyı test edin.

---

## Özet

| Soru | Cevap |
|------|--------|
| Kullanıcı adı ne? | Genelde **postgres**. Başka kullanıcı oluşturduysanız onu kullanın. |
| Şifreyi nereden öğrenirim? | Öğrenemezsiniz; sadece eski projedeki .env’e bakabilir veya yukarıdaki adımlarla **yeni şifre** belirlersiniz. |
