================================================================================
                    VORNEX-MTOOL - EĞİTİM VE KULLANIM KLAVUZU
================================================================================
YASAL UYARI: Bu araç ve klavuz yalnızca eğitim amaçlı, sızdırma testi laboratuvarları 
ve açık yazılı izne sahip sistemlerin güvenliğini denetlemek için tasarlanmıştır. 
Yetkisiz sistemlerde kullanımı suçtur. Tüm sorumluluk kullanıcıya aittir.
================================================================================

1. PROXY HAVUZU (Proxy Manager)
--------------------------------------------------------------------------------
- Ne İşe Yarar: Hedef sistemlere atılan isteklerin IP adresini gizlemek ve tek bir 
  IP üzerinden engellenmeyi önlemek için dinamik proxy havuzu oluşturur.
- Nasıl Çalışır: Çeşitli çevrimiçi kaynaklardan HTTP, HTTPS, SOCKS4 ve SOCKS5 
  protokollerindeki proxy adreslerini asenkron olarak çeker. Toplanan her bir 
  proxy'yi test hedefinden geçirerek canlı (çalışır durumda) ve hızlı olanları 
  filtreleyip ortak bir havuza kaydeder.
- Olası Sonuçlar: 
  * Başarılı Durum: Aktif proxy sayısı ekrana yazdırılır ve tarama/saldırı 
    istekleri bu proxy'ler üzerinden rotasyonlu olarak gerçekleştirilir.
  * Başarısız Durum: İnternet kaynaklarına ulaşılamazsa veya tüm proxy'ler ölü 
    çıkarsa havuz boş kalır, araç yerel IP üzerinden devam etmek zorunda kalır.

2. OOB CALLBACK DİNLEYİCİ (Out-of-Band Listener)
--------------------------------------------------------------------------------
- Ne İşe Yarar: Kör (blind) zafiyet testlerinde, hedef sunucunun dış dünya ile 
  kurduğu bağlantıları yakalamak için kullanılır.
- Nasıl Çalışır: Yerel makinede hafif, asenkron bir HTTP sunucusu (listener) 
  ayağa kaldırır. Hedef sisteme gönderilen özel payload'lar (örneğin zararlı bir 
  link veya harici varlık isteği), hedef sunucu tarafından tetiklendiğinde bu 
  sunucuya bir HTTP isteği gönderilmesini sağlar.
- Olası Sonuçlar: 
  * Başarılı Durum: Hedef sistemden gelen istekler (IP adresi, istek atılan 
    endpoint, header bilgileri) konsola loglanır. Bu, hedefte XXE, SSRF veya 
    RCE olduğunun kesin kanıtıdır.
  * Başarısız Durum: Güvenlik duvarı (Firewall) dışarıya giden istekleri engelliyorsa 
    veya payload tetiklenmediyse hiçbir veri alınamaz.

3. SQLi - SQL ENJEKSİYONU (SQL Injection Tester)
--------------------------------------------------------------------------------
- Ne İşe Yarar: Veritabanı sorgularının manipüle edilip edilemediğini, hassas 
  verilerin okunup okunamayacağını test eder.
- Nasıl Çalışır: Hedef URL veya parametrelere tırnak işaretleri, mantıksal operatörler 
  ('OR '1'='1) ve SQL komutları enjekte eder. 
  * Hata Tabanlı: Veritabanı hata mesajlarını tetiklemeye çalışır.
  * Boolean/Time Blind: Yanıtın dönme süresini (`SLEEP` komutları) veya sayfa içeriğindeki 
    mantıksal değişimleri gözlemler.
  * Union Tabanlı: `UNION SELECT` ile veritabanı tablolarını birleştirip ek veri çeker.
- Olası Sonuçlar: 
  * Başarılı Durum: Veritabanı sürümü, tablo isimleri, kullanıcı adları veya hash'ler 
    ekrana dökülür (`dump` edilir). Zafiyetin varlığı doğrulanır.
  * Başarısız Durum: Girdiler filtreleniyorsa veya WAF (Web Application Firewall) 
    engelliyorsa sorgular başarısız olur ve "güvenli" çıktısı alınır.

4. CMDi - KOMUT ENJEKSİYONU (Command Injection)
--------------------------------------------------------------------------------
- Ne İşe Yarar: Web uygulamasının arkasındaki işletim sisteminde yetkisiz kabuk 
  (shell) komutları çalıştırılıp çalıştırılamayacağını test eder.
- Nasıl Çalışır: Girdi parametrelerine `;`, `&&`, `|` gibi komut ayırıcıları ve 
  `id`, `whoami`, `uname -a` gibi temel sistem komutlarını ekleyerek gönderir.
- Olası Sonuçlar: 
  * Başarılı Durum: Komut çıktısı (örneğin mevcut kullanıcı adı veya sistem mimarisi) 
    doğrudan web sitesinin yanıtında görünür hale gelir.
  * Başarısız Durum: Uygulama girdileri güvenli bir şekilde escape ediyorsa komutlar 
    çalışmaz, hata döner veya sayfa bozulur.

5. ASENKRON DDOS / YÜK TESTİ (Async DDoS & Stress Tester)
--------------------------------------------------------------------------------
- Ne İşe Yarar: Sunucuların veya ağ altyapısının yoğun trafik altındaki dayanıklılığını 
  ve performans sınırlarını test eder.
- Nasıl Çalışır: `asyncio` ve `aiohttp` kullanarak hedefe çok yüksek miktarda 
  eş zamanlı istek gönderir. HTTP Flood, Slowloris (bağlantıyı yavaş tutarak socket 
  tüketme), RUDY (yavaş POST gövdeleri) ve HTTP/2 Rapid Reset protokol açıklarını kullanır.
- Olası Sonuçlar: 
  * Başarılı Durum: Sunucu kaynakları (CPU/RAM) tüketilir, yanıt süreleri uzar 
    veya hizmet dışı kalır (Service Unavailable - 503).
  * Başarısız Durum: Hedefte güçlü bir Load Balancer, Cloudflare veya Rate Limiting 
    varsa istekler engellenir, test etkisiz kalır.

6. TOKEN KILLER (API Token & Webhook Auditor)
--------------------------------------------------------------------------------
- Ne İşe Yarar: Sızdırılmış veya halka açık yerlerde unutulmuş API anahtarlarının 
  ve webhook'ların geçerliliğini denetler.
- Nasıl Çalışır: Telegram bot tokenleri, Discord webhook/tokenleri ve Slack 
  webhook adreslerine test istekleri göndererek servislerin API uç noktalarıyla 
  iletişim kurar.
- Olası Sonuçlar: 
  * Başarılı Durum: Token'ın aktif olduğu, ilgili botun adı veya kanal bilgileri 
    doğrulanır (Yetki seviyesi raporlanır).
  * Başarısız Durum: Token geçersizse, silinmişse veya süresi dolmuşsa API 
    "Unauthorized" (401/403) hatası döndürür.

7. LFI - YEREL DOSYA OKUMA (Local File Inclusion)
--------------------------------------------------------------------------------
- Ne İşe Yarar: Sunucu dosya sistemindeki hassas konfigürasyon dosyalarına veya 
  şifre dosyalarına (`/etc/passwd` vb.) erişilip erişilemediğini test eder.
- Nasıl Çalışır: Parametrelere `../../` gibi dizin atlatma (path traversal) 
  karakterleri ve PHP sarmalayıcıları (`php://filter`) ekleyerek kaynak kodları okumaya çalışır.
- Olası Sonuçlar: 
  * Başarılı Durum: Sunucunun sistem dosyaları veya kaynak kodları ekrana yansır. 
    İleri aşamada Log Poisoning ile RCE kapısı aralanabilir.
  * Başarısız Durum: Uygulama dosya yollarını global bir dizine sabitliyorsa 
    veya filtreleme varsa dosya okunamaz.

8. SSTI - SUNUCU TARAFI ŞABLON ENJEKSİYONU (Template Injection)
--------------------------------------------------------------------------------
- Ne İşe Yarar: Modern web çatılarında kullanıcı girdilerinin şablon motorları 
  tarafından doğrudan çalıştırılıp çalıştırılmadığını analiz eder.
- Nasıl Çalışır: Jinja2, Twig, Freemarker gibi motorlara özel matematiksel ifadeler 
  (`{{7*7}}`) gönderir. Sunucunun bu ifadeyi hesaplayıp hesaplamadığını kontrol eder.
- Olası Sonuçlar: 
  * Başarılı Durum: Girdi `49` olarak dönerse şablon motorunun zafiyet barındırdığı 
    kesinleşir. Ardından motor bazlı RCE payload'ları çalıştırılabilir.
  * Başarısız Durum: Girdi olduğu gibi ekrana basılır (metin olarak işlenir), 
    herhangi bir hesaplama yapılmaz.

9. XXE - XML HARİCİ VARLIK ZAFİYETİ (XML External Entity)
--------------------------------------------------------------------------------
- Ne İşe Yarar: XML verilerini işleyen servislerin harici varlık referanslarını 
  güvensiz bir şekilde işleyip işlemediğini test eder.
- Nasıl Çalışır: İstek gövdesine kötü niyetli `<!ENTITY>` tanımları içeren XML 
  yapıları yerleştirir. Yerel dosyaları okumayı veya OOB dinleyicisine tetik atmayı dener.
- Olası Sonuçlar: 
  * Başarılı Durum: Sunucu harici varlığı çözümler ve istenen dosyayı yanıt içinde 
    döndürür ya da OOB sunucusuna bağlantı atar.
  * Başarısız Durum: XML parser harici varlıkları (Entity resolution) devre dışı 
    bıraktıysa saldırı başarısız olur.

10. SSRF - SUNUCU TARAFI İSTEK SAHTECİLİĞİ (Server-Side Request Forgery)
--------------------------------------------------------------------------------
- Ne İşe Yarar: Sunucunun kendi üzerinden dahili ağdaki servislere veya bulut 
  meta-veri adreslerine istek atıp atamadığını test eder.
- Nasıl Çalışır: URL alanlarına `127.0.0.1`, `localhost` veya AWS/GCP meta-veri 
  servis IP'lerini (`169.254.169.254`) yazarak istek yollar.
- Olası Sonuçlar: 
  * Başarılı Durum: Dahili servislerin yanıtları veya bulut ortamına ait gizli 
    erişim anahtarları (IAM credentials) dışarı sızdırılır.
  * Başarısız Durum: Uygulama dış kaynak URL'lerini whitelist (beyaz liste) ile 
    sınırlıyorsa istekler reddedilir.

11. JWT ANALİZ VE ATAK (JSON Web Token Security Auditor)
--------------------------------------------------------------------------------
- Ne İşe Yarar: Kimlik doğrulama mekanizmalarında kullanılan JWT'lerin imza 
  güvenliğini ve yapısal zayıflıklarını test eder.
- Nasıl Çalışır: Token'ı çözer (`decode`). İmza doğrulama algoritmasını `none` 
  yaparak bypass etmeye çalışır veya zayıf gizli anahtarları sözlük saldırısıyla 
  (brute-force) kırmaya çalışır.
- Olası Sonuçlar: 
  * Başarılı Durum: Token imzası olmadan kabul görürse kimlik doğrulama atlatılır 
    (Privilege Escalation); anahtar kırılırsa tokenler sahte olarak üretilebilir.
  * Başarısız Durum: Güçlü bir imza algoritması (RS256 vb.) ve karmaşık gizli 
    anahtar kullanılıyorsa saldırılar sonuçsuz kalır.

12. REVERSE SHELL ÜRETİCİ (Reverse Shell Payload Generator)
--------------------------------------------------------------------------------
- Ne İşe Yarar: Hedef sistemde komut çalıştırma zafiyeti doğrulandığında, saldırganın 
  kendi dinleyicisine bağlantı alabilmesi için hazır komut kalıpları üretir.
- Nasıl Çalışır: Kullanıcının belirttiği IP ve Port bilgilerini; Bash, Python, 
  Perl, PHP, PowerShell, Netcat gibi 15 farklı programlama diline entegre ederek 
  tek satırlık payload'lar hazırlar.
- Olası Sonuçlar: 
  * Başarılı Durum: Üretilen kod hedef sistemdeki CMDi veya RCE vektörüne yapıştırıldığında, 
    saldırganın terminaline aktif bir kabuk (shell) bağlantısı gelir.

13. FULL AUTO - ORKESTRA MODÜLÜ (Automated Multi-Vector Orchestrator)
--------------------------------------------------------------------------------
- Ne İşe Yarar: Yukarıda yer alan tüm test süreçlerini tek bir komutla sıraya 
  koyarak otomatize eder.
- Nasıl Çalışır: Belirlenen hedef adrese karşı sırasıyla tüm tarama ve zafiyet 
  modüllerini asenkron olarak koşturur. Elde gelen bulguları toplar.
- Olası Sonuçlar: 
  * Başarılı Durum: Hedef sistemin zafiyet haritası çıkarılır ve tüm sonuçlar 
    düzenli bir JSON formatında rapor dosyasına kaydedilir.
================================================================================