# IP-FINDER-V2.0
# 🌐 IP-FINDER-V2.0

> **Advanced DNS & IP Reconnaissance Tool for Security Research**

**IP-FINDER-V2.0** is a lightweight Python-based command-line reconnaissance tool designed to resolve hostnames, identify IP addresses, inspect DNS records, perform reverse DNS lookups, detect common CDN providers, process multiple targets, and export results as JSON.

Created by **ABHISHEK14677**.

---

## ✨ Features

* 🌐 **IPv4 & IPv6 Resolution**
* 🔎 **DNS Record Enumeration**
* 🔄 **Reverse DNS / PTR Lookup**
* 🛡️ **CDN Detection**
* ☁️ Detects common providers such as:

  * Cloudflare
  * AWS CloudFront
  * Google Cloud
  * Microsoft Azure
  * Fastly
* 📦 **Batch Hostname Processing**
* ⚡ **Multithreaded Resolution**
* 📄 **JSON Report Export**
* 🖥️ **Interactive CLI Menu**
* 🎨 Colored terminal output
* 🔧 Configurable DNS record types

---

## 📡 Supported DNS Records

The tool can query:

```text
A
AAAA
CNAME
MX
NS
TXT
SOA
```

The default CLI configuration queries:

```text
A, AAAA, CNAME, MX, NS, TXT
```

The interactive full DNS scan additionally checks `SOA`.

---

## 🧰 Requirements

* Python **3.x**
* Internet connection
* `dnspython`

Install the required dependency:

```bash
pip3 install dnspython
```

Or:

```bash
python3 -m pip install dnspython
```

---

## 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/ABHISHEK14677/IP-FINDER-V2.0.git
```

Enter the project directory:

```bash
cd IP-FINDER-V2.0
```

Install the dependency:

```bash
pip3 install dnspython
```

Run the tool:

```bash
python3 IP-FINDER-V2.0.py
```

---

# 🖥️ Interactive Mode

Run without arguments:

```bash
python3 IP-FINDER-V2.0.py
```

The interactive menu provides:

```text
1. Find IP address
2. Full DNS scan
3. Reverse lookup
4. Exit
```

### 1️⃣ Find IP Address

Enter a hostname:

```text
Hostname: example.com
```

The tool resolves the hostname and displays its IP address.

---

### 2️⃣ Full DNS Scan

The full scan checks:

```text
A
AAAA
MX
NS
TXT
CNAME
SOA
PTR
```

Example:

```text
Hostname: example.com
```

This provides a broader DNS overview of the target.

---

### 3️⃣ Reverse Lookup

Enter an IP address:

```text
IP address: 8.8.8.8
```

The tool attempts to retrieve the associated PTR/hostname record.

---

# ⚡ Command-Line Usage

You can also run the tool directly against one or more hosts.

### Single Host

```bash
python3 IP-FINDER-V2.0.py example.com
```

### Multiple Hosts

```bash
python3 IP-FINDER-V2.0.py example.com google.com cloudflare.com
```

---

## 🔍 Reverse DNS Lookup

Use:

```bash
python3 IP-FINDER-V2.0.py example.com -r
```

The `-r` / `--ptr` option performs PTR lookups for the resolved IP addresses.

---

## 📋 Custom DNS Record Types

Specify the DNS records you want to query:

```bash
python3 IP-FINDER-V2.0.py example.com -t A,AAAA,CNAME
```

Example:

```bash
python3 IP-FINDER-V2.0.py example.com -t MX,NS,TXT
```

---

# 📂 Batch Mode

Create a file containing hostnames:

```text
example.com
google.com
github.com
cloudflare.com
```

For example:

```bash
nano targets.txt
```

Then run:

```bash
python3 IP-FINDER-V2.0.py -f targets.txt
```

The tool processes multiple hosts concurrently.

---

# ⚡ Multithreading

Batch processing uses multiple worker threads.

Default:

```text
20 workers
```

Change the number of workers with:

```bash
python3 IP-FINDER-V2.0.py -f targets.txt -w 50
```

For example:

```bash
-w 10
```

uses 10 workers.

---

# 💾 JSON Output

Save results to a JSON file:

```bash
python3 IP-FINDER-V2.0.py example.com -o results.json
```

For multiple targets:

```bash
python3 IP-FINDER-V2.0.py -f targets.txt -o results.json
```

The generated JSON contains structured information such as:

```json
{
  "host": "example.com",
  "ip": [
    "93.184.216.34"
  ],
  "records": {},
  "cdn": null
}
```

---

# 🛡️ CDN Detection

IP-FINDER-V2.0 checks resolved IP addresses against a built-in collection of known network ranges.

Currently supported detection includes:

```text
Cloudflare
AWS CloudFront
Google Cloud
Azure
Fastly
```

If an IP matches a known CDN range, the tool reports that the hostname is behind the detected CDN.

> **Important:** CDN detection is based on the tool's built-in IP ranges and should be treated as an indication rather than definitive attribution.

---

# 🔧 Command Reference

| Option              | Description                        |
| ------------------- | ---------------------------------- |
| `host`              | One or more hostnames              |
| `-f, --file`        | Read hostnames from a file         |
| `-t, --types`       | DNS record types to query          |
| `-r, --ptr`         | Perform reverse PTR lookups        |
| `-o, --output`      | Save results as JSON               |
| `-w, --workers`     | Number of batch-processing threads |
| `-i, --interactive` | Interactive menu mode              |

---

## 📌 Examples

### Basic lookup

```bash
python3 IP-FINDER-V2.0.py example.com
```

### DNS enumeration

```bash
python3 IP-FINDER-V2.0.py example.com -t A,AAAA,MX,NS,TXT,CNAME
```

### Reverse lookup

```bash
python3 IP-FINDER-V2.0.py example.com -r
```

### Batch scanning

```bash
python3 IP-FINDER-V2.0.py -f targets.txt
```

### Batch + reverse lookup

```bash
python3 IP-FINDER-V2.0.py -f targets.txt -r
```

### Save JSON report

```bash
python3 IP-FINDER-V2.0.py -f targets.txt -o results.json
```

### Batch + custom workers

```bash
python3 IP-FINDER-V2.0.py -f targets.txt -w 50
```

### Show help

```bash
python3 IP-FINDER-V2.0.py --help
```

---

# 🔬 How It Works

The tool follows a simple reconnaissance workflow:

```text
                 ┌──────────────────┐
                 │    Hostname      │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ DNS Resolution   │
                 └────────┬─────────┘
                          │
                    ┌─────┴─────┐
                    ▼           ▼
                 IPv4         IPv6
                    │           │
                    └─────┬─────┘
                          ▼
                 ┌──────────────────┐
                 │ DNS Enumeration  │
                 └────────┬─────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
             CNAME        MX       NS/TXT/SOA
              │
              ▼
        ┌───────────────┐
        │ CDN Detection │
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │ Reverse PTR   │
        └───────┬───────┘
                │
                ▼
        ┌────────────────┐
        │ JSON / Terminal │
        │     Report     │
        └────────────────┘
```

---

# 🎯 Use Cases

IP-FINDER-V2.0 can be useful for:

* Cybersecurity learning
* DNS research
* Network reconnaissance
* Security lab environments
* Infrastructure discovery
* OSINT workflows
* DNS troubleshooting
* Understanding CDN infrastructure
* Authorized penetration-testing reconnaissance

---

# ⚠️ Disclaimer

This project is intended for **educational, research, and authorized security testing purposes only**.

Do not use this tool against systems, networks, domains, or infrastructure without appropriate authorization.

The author is not responsible for misuse, damage, or unauthorized activity performed using this software.

**Always obtain permission before performing security reconnaissance against infrastructure you do not own or administer.**

---

# 👨‍💻 Author

**ABHISHEK M**

GitHub:

[@ABHISHEK14677](https://github.com/ABHISHEK14677?utm_source=chatgpt.com)

Project:

[IP-FINDER-V2.0](https://github.com/ABHISHEK14677/IP-FINDER-V2.0?utm_source=chatgpt.com)

---

# ⭐ Support

If you find this project useful:

* ⭐ Star the repository
* 🍴 Fork the project
* 🐛 Report bugs
* 💡 Suggest improvements
* 🔧 Submit pull requests

---

## 📜 License

Add an appropriate open-source license to the repository before distributing the project publicly.

---

### IP-FINDER-V2.0

**DNS Resolution • Reverse Lookup • CDN Detection • Batch Reconnaissance**

> **Learn. Build. Test. Secure.**
