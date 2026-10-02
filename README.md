# ⚡ VORNEX-MTOOL – Gelişmiş Güvenlik Denetim & Sızdırma Testi Aracı

![Version](https://img.shields.io/badge/version-3.0-red)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Platform](https://img.shields.io/badge/platform-Termux%20%7C%20Linux%20%7C%20macOS%20%7C%20Windows-brightgreen)
![License](https://img.shields.io/badge/license-MIT-orange)

**VORNEX-MTOOL**, asenkron mimarisi ve tek dosya (`main.py`) üzerinden yönetilebilen yapısıyla, sızdırma testi ve güvenlik denetimi süreçlerini tek bir çatı altında toplamak amacıyla geliştirilmiş gelişmiş bir otomasyon ve güvenlik analiz aracıdır[cite: 2].

---

## 🔥 Özellikler ve Modüller

- 🌐 **Proxy Havuzu (Proxy Manager)** – HTTP, HTTPS, SOCKS4 ve SOCKS5 proxy'lerini dinamik olarak toplar, test eder ve rotasyonlu havuz kurar[cite: 2].
- 🎯 **OOB Callback Dinleyici** – Kör (blind) zafiyetler için dış dünya bağlantılarını yakalayan yerleşik HTTP sunucusu[cite: 2].
- 💉 **SQL Injection Testi** – Hata tabanlı, boolean/time blind ve union yöntemleriyle veritabanı zafiyet analizi[cite: 2].
- ⚙ **Command Injection Testi** – Sunucu tarafı komut çalıştırma açıklarını ve reverse shell tetikleyicilerini test eder[cite: 2].
- 🚀 **Asenkron DDoS & Yük Testi** – HTTP Flood, Slowloris, RUDY ve HTTP/2 Rapid Reset vektörleriyle performans/dayanıklılık testi[cite: 2].
- 🤖 **Token Killer** – Telegram, Discord ve Slack platformlarına ait API anahtarları ile webhook'ların geçerliliğini denetler[cite: 2].
- 📁 **LFI (Yerel Dosya Okuma)** – Dizin atlatma ve sarmalayıcılar (`php://filter`) ile hassas dosya erişim kontrolü[cite: 2].
- ⚡ **SSTI (Template Injection)** – Şablon motorlarında (Jinja2, Twig vb.) kod çalıştırma risklerini inceler[cite: 2].
- 🛡️ **XXE (XML External Entity)** – Harici varlık işleme zafiyetleri üzerinden dosya okuma ve OOB testleri[cite: 2].
- 🔗 **SSRF (Server-Side Request Forgery)** – Dahili ağlara ve bulut meta-veri servislerine yönelik istek sızdırma analizi[cite: 2].
- 🔑 **JWT Analiz Aracı** – İmza doğrulama bypass'ları (`none` algoritması) ve zayıf anahtar brute-force denemeleri[cite: 2].
- 💻 **Reverse Shell Üreteci** – 15 farklı dilde hazır kabuk (shell) bağlantı komutları üretir[cite: 2].
- 🤖 **Full Auto (Orkestra Modülü)** – Tüm tarama ve test modüllerini tek komutla sırayla koşturarak JSON formatında raporlar[cite: 2].
- 🎨 **Terminal Arayüzü** – Colorama destekli renkli ve menü tabanlı terminal deneyimi[cite: 2].

---

## ⚠️ Yasal Uyarı

Bu araç yalnızca **güvenlik testleri, eğitim ve izinli sistem analizleri** için geliştirilmiştir. İzin alınmayan hedef sistemler üzerinde kullanılması yasal sorumluluk doğurabilir. Kullanıcı, aracın kullanımından doğan tüm hukuki sorumluluğu kabul etmiş sayılır[cite: 2].

---

## 📦 Gereksinimler

- Python 3.8 veya üzeri[cite: 2]
- `pip` (Python Paket Yöneticisi)[cite: 2]
- Aktif İnternet Bağlantısı[cite: 2]

---

## 🚀 Tüm Platformlar İçin Kurulum (Tek Kod Bloğu)

```bash
# ----------------------------------------------------
# 1️⃣ TERMUX (ANDROID)
# ----------------------------------------------------
pkg update -y && pkg upgrade -y
pkg install -y python python-pip git
termux-setup-storage
pip install --upgrade pip
git clone https://github.com/VornexxBaba/VORNEX-MTOOL.git
cd VORNEX-MTOOL
pip install aiohttp colorama aiohttp-socks requests pyjwt h2 PySocks
python3 main.py

# ----------------------------------------------------
# 2️⃣ DEBIAN / UBUNTU LINUX
# ----------------------------------------------------
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip git
git clone https://github.com/VornexxBaba/VORNEX-MTOOL.git
cd VORNEX-MTOOL
pip3 install aiohttp colorama aiohttp-socks requests pyjwt h2 PySocks
python3 main.py

# ----------------------------------------------------
# 3️⃣ ARCH LINUX
# ----------------------------------------------------
sudo pacman -Syu
sudo pacman -S --needed python python-pip git
git clone https://github.com/VornexxBaba/VORNEX-MTOOL.git
cd VORNEX-MTOOL
pip install aiohttp colorama aiohttp-socks requests pyjwt h2 PySocks
python main.py

# ----------------------------------------------------
# 4️⃣ MACOS
# ----------------------------------------------------
brew update
brew install python git
git clone https://github.com/VornexxBaba/VORNEX-MTOOL.git
cd VORNEX-MTOOL
pip3 install aiohttp colorama aiohttp-socks requests pyjwt h2 PySocks
python3 main.py

# ----------------------------------------------------
# 5️⃣ WINDOWS (CMD / PowerShell)
# ----------------------------------------------------
git clone https://github.com/VornexxBaba/VORNEX-MTOOL.git
cd VORNEX-MTOOL
pip install aiohttp colorama aiohttp-socks requests pyjwt h2 PySocks
python main.py
