================================================================================
                    VORNEX-MTOOL - EDUCATIONAL & USAGE GUIDE
================================================================================
LEGAL DISCLAIMER: This tool and guide are designed solely for educational purposes, 
penetration testing laboratories, and security audits of systems with explicit 
written permission. Unauthorized use on foreign systems is illegal. All liability 
belongs to the user.
================================================================================

1. PROXY POOL (Proxy Manager)
--------------------------------------------------------------------------------
- Purpose: Hides the IP address of outgoing requests sent to target systems and 
  prevents getting blocked by rotating through dynamic proxy pools.
- How It Works: Asynchronously fetches proxy addresses in HTTP, HTTPS, SOCKS4, 
  and SOCKS5 protocols from various online sources. Tests each collected proxy 
  against a target, filters out the live and fast ones, and saves them into a shared pool.
- Possible Outcomes: 
  * Success: The number of active proxies is printed to the screen, and scanning/attack 
    requests are executed rotationally through these proxies.
  * Failure: If online sources are unreachable or all proxies are dead, the pool remains 
    empty, forcing the tool to fall back to the local IP.

2. OOB CALLBACK LISTENER (Out-of-Band Listener)
--------------------------------------------------------------------------------
- Purpose: Used in blind vulnerability tests to capture outbound connections 
  initiated by the target server.
- How It Works: Spawns a lightweight, asynchronous HTTP server (listener) on the 
  local machine. Custom payloads sent to the target system (such as a malicious link 
  or external entity request) force the target server to send an HTTP request to this listener upon triggering.
- Possible Outcomes: 
  * Success: Requests coming from the target system (IP address, requested endpoint, 
    header info) are logged to the console. This is definitive proof of XXE, SSRF, or RCE in the target.
  * Failure: If the firewall blocks outbound requests or the payload fails to trigger, 
    no data is received.

3. SQLi - SQL INJECTION (SQL Injection Tester)
--------------------------------------------------------------------------------
- Purpose: Tests whether database queries can be manipulated and whether sensitive 
  data can be read.
- How It Works: Injects single quotes, logical operators ('OR '1'='1), and SQL commands 
  into target URLs or parameters. 
  * Error-based: Attempts to trigger database error messages.
  * Boolean/Time Blind: Observes response delays (`SLEEP` commands) or logical 
    changes in page content.
  * Union-based: Combines database tables using `UNION SELECT` to extract extra data.
- Possible Outcomes: 
  * Success: Database version, table names, usernames, or hashes are dumped to the 
    screen. The vulnerability is verified.
  * Failure: If inputs are filtered or blocked by a WAF (Web Application Firewall), 
    queries fail and a "safe" output is returned.

4. CMDi - COMMAND INJECTION (Command Injection)
--------------------------------------------------------------------------------
- Purpose: Tests whether unauthorized shell commands can be executed on the 
  operating system behind the web application.
- How It Works: Appends command separators like `;`, `&&`, `|` and basic system 
  commands such as `id`, `whoami`, `uname -a` into input parameters and sends them.
- Possible Outcomes: 
  * Success: Command output (e.g., current username or system architecture) 
    becomes directly visible in the web application's response.
  * Failure: If the application safely escapes inputs, commands do not execute, 
    return an error, or break the page.

5. ASYNC DDOS & STRESS TESTER (Async DDoS & Stress Tester)
--------------------------------------------------------------------------------
- Purpose: Tests server or network infrastructure endurance and performance limits 
  under heavy traffic.
- How It Works: Uses `asyncio` and `aiohttp` to send a high volume of concurrent 
  requests to the target. Employs HTTP Flood, Slowloris (exhausting sockets by keeping 
  connections open slowly), RUDY (slow POST bodies), and HTTP/2 Rapid Reset protocol flaws.
- Possible Outcomes: 
  * Success: Server resources (CPU/RAM) are exhausted, response times increase, 
    or the service goes down (Service Unavailable - 503).
  * Failure: If the target is protected by a strong Load Balancer, Cloudflare, 
    or Rate Limiting, requests are blocked, rendering the test ineffective.

6. TOKEN KILLER (API Token & Webhook Auditor)
--------------------------------------------------------------------------------
- Purpose: Audits the validity of leaked or publicly exposed API keys and webhooks.
- How It Works: Sends test requests to Telegram bot tokens, Discord webhook/tokens, 
  and Slack webhook addresses to communicate with the services' API endpoints.
- Possible Outcomes: 
  * Success: Confirms that the token is active, along with the associated bot 
    name or channel details (reports permission level).
  * Failure: If the token is invalid, deleted, or expired, the API returns an 
    "Unauthorized" (401/403) error.

7. LFI - LOCAL FILE INCLUSION (Local File Inclusion)
--------------------------------------------------------------------------------
- Purpose: Tests whether sensitive configuration files or password files (`/etc/passwd`, etc.) 
  on the server file system can be accessed.
- How It Works: Appends path traversal characters like `../../` and PHP wrappers 
  (`php://filter`) to parameters to attempt reading source code.
- Possible Outcomes: 
  * Success: System files or source codes of the server are reflected on the screen. 
    Can pave the way for RCE via Log Poisoning in later stages.
  * Failure: If the application locks file paths to a global directory or applies 
    filtering, files cannot be read.

8. SSTI - SERVER-SIDE TEMPLATE INJECTION (Template Injection)
--------------------------------------------------------------------------------
- Purpose: Analyzes whether user inputs are directly evaluated by template engines 
  in modern web frameworks.
- How It Works: Sends specific mathematical expressions (`{{7*7}}`) to engines 
  like Jinja2, Twig, and Freemarker. Checks if the server computes the expression.
- Possible Outcomes: 
  * Success: If the input returns as `49`, the template engine vulnerability is 
    confirmed. Engine-specific RCE payloads can then be executed.
  * Failure: Input is printed as-is (processed as plain text), with no calculations performed.

9. XXE - XML EXTERNAL ENTITY (XML External Entity)
--------------------------------------------------------------------------------
- Purpose: Tests whether services processing XML data handle external entity 
  references insecurely.
- How It Works: Inserts malicious XML structures containing `<!ENTITY>` definitions 
  into the request body. Attempts to read local files or trigger an OOB listener.
- Possible Outcomes: 
  * Success: The server resolves the external entity and returns the requested file 
    in the response or triggers a connection to the OOB server.
  * Failure: If the XML parser has external entity resolution disabled, the attack fails.

10. SSRF - SERVER-SIDE REQUEST FORGERY (Server-Side Request Forgery)
--------------------------------------------------------------------------------
- Purpose: Tests whether the server can make requests to internal network services 
  or cloud metadata addresses through itself.
- How It Works: Injects `127.0.0.1`, `localhost`, or AWS/GCP metadata service IPs 
  (`169.254.169.254`) into URL fields and dispatches requests.
- Possible Outcomes: 
  * Success: Responses from internal services or secret access keys (IAM credentials) 
    belonging to the cloud environment are leaked externally.
  * Failure: If the application limits external source URLs with a whitelist, 
    requests are rejected.

11. JWT ANALYSIS & ATTACK (JSON Web Token Security Auditor)
--------------------------------------------------------------------------------
- Purpose: Tests signature security and structural weaknesses of JWTs used in 
  authentication mechanisms.
- How It Works: Decodes the token. Attempts to bypass signature verification by 
  setting the algorithm to `none`, or tries to crack weak secret keys via dictionary 
  attacks (brute-force).
- Possible Outcomes: 
  * Success: If the token is accepted without a signature, authentication is bypassed 
    (Privilege Escalation); if the key is cracked, tokens can be forged.
  * Failure: If a strong signature algorithm (RS256, etc.) and a complex secret key 
    are used, attacks yield no results.

12. REVERSE SHELL GENERATOR (Reverse Shell Payload Generator)
--------------------------------------------------------------------------------
- Purpose: Generates ready-to-use command templates so the attacker can receive 
  a connection back to their listener once command execution is verified on the target system.
- How It Works: Integrates user-specified IP and Port details into shell payload 
  snippets across 15 different programming languages, including Bash, Python, Perl, PHP, 
  PowerShell, and Netcat.
- Possible Outcomes: 
  * Success: When the generated code is pasted into the target system's CMDi or 
    RCE vector, an active shell connection connects back to the attacker's terminal.

13. FULL AUTO - ORCHESTRATION MODULE (Automated Multi-Vector Orchestrator)
--------------------------------------------------------------------------------
- Purpose: Automates all testing processes sequentially using a single command.
- How It Works: Sequentially executes all scanning and vulnerability modules 
  asynchronously against the specified target address and collects the resulting findings.
- Possible Outcomes: 
  * Success: Generates a vulnerability map of the target system and logs all results 
    into a structured JSON report file.
================================================================================