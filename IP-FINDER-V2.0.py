#!/usr/bin/env python3
"""
IP-FINDER v2 — DNS resolution, reverse lookup, CDN detection, batch mode.
Requires: pip3 install dnspython
"""

import argparse
import ipaddress
import json
import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import dns.resolver
    import dns.reversename
    import dns.exception
    HAS_DNSPYTHON = True
except ImportError:
    HAS_DNSPYTHON = False

BANNER = r"""
 ██████   ███    ███  ███    ██  ██            █████  ██████   ██   ██  ██
██    ██  ████  ████  ████   ██  ██           ██   ██ ██   ██  ██   ██  ██
██    ██  ██ ████ ██  ██ ██  ██  ██    ████   ███████ ██████   ███████  ██
██    ██  ██  ██  ██  ██ ██  ██  ██           ██   ██ ██   ██  ██   ██  ██
 ██████   ██      ██  ██   ████  ██           ██   ██ ██████   ██   ██  ██
                                                ~ O M N I - A B H I
  CREATED BY : https://github.com/ABHISHEK14677
  v2 : multi-record + reverse + CDN detection + batch mode
"""

# ---------------------------------------------------------------- resolvers

RESOLVER = None
if HAS_DNSPYTHON:
    RESOLVER = dns.resolver.Resolver(configure=False)
    RESOLVER.nameservers = ["1.1.1.1", "8.8.8.8"]
    RESOLVER.lifetime = 3  # don't hang forever on a dead resolver


def query_records(hostname, rtype):
    """Query one DNS record type via dnspython, return list of strings."""
    if not HAS_DNSPYTHON:
        return []
    try:
        return [r.to_text() for r in RESOLVER.resolve(hostname, rtype)]
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer,
            dns.resolver.NoNameservers, dns.exception.Timeout, dns.resolver.LifetimeTimeout):
        return []
    except Exception as e:  # noqa: BLE001
        return [f"ERROR: {e}"]


def resolve_all(hostname):
    """Resolve a hostname to a set of IPs (IPv4 + IPv6) via the OS resolver."""
    results = set()
    try:
        for _, _, _, _, sockaddr in socket.getaddrinfo(hostname, None):
            results.add(sockaddr[0])
    except socket.gaierror:
        # fallback: try A records via dnspython in case the OS resolver failed
        if HAS_DNSPYTHON:
            results.update(query_records(hostname, "A"))
    if not results:
        raise ValueError(f"could not resolve {hostname}")
    return results


def reverse_lookup(ip):
    """PTR record for an IP."""
    if not HAS_DNSPYTHON:
        return []
    try:
        return query_records(str(dns.reversename.from_address(ip)), "PTR")
    except dns.exception.DNSException:
        return []

# ------------------------------------------------------------ CDN detection

CDN_RANGES = {
    "Cloudflare": ["173.245.48.0/20", "103.21.244.0/22", "103.22.200.0/22",
                   "103.31.4.0/22", "104.16.0.0/13", "104.24.0.0/14",
                   "108.162.192.0/18", "131.0.72.0/22", "141.101.64.0/18",
                   "162.158.0.0/15", "172.64.0.0/13", "190.93.240.0/20"],
    "AWS CloudFront": ["13.32.0.0/12", "13.35.0.0/16", "52.46.0.0/18",
                       "52.82.0.0/15", "52.222.0.0/16", "54.230.0.0/16",
                       "54.239.0.0/16", "99.84.0.0/16", "205.251.192.0/18"],
    "Google Cloud": ["34.64.0.0/10", "35.184.0.0/13", "130.211.0.0/16",
                     "142.250.0.0/15", "172.217.0.0/16"],
    "Azure": ["20.0.0.0/8", "40.64.0.0/10", "52.224.0.0/11"],
    "Fastly": ["23.235.32.0/20", "43.249.72.0/22", "103.244.50.0/24",
               "146.75.0.0/16", "151.101.0.0/16", "167.82.0.0/17",
               "185.31.16.0/22", "199.232.0.0/16"],
}


def detect_cdn(ip):
    """Return CDN name if the IP belongs to a known provider range."""
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return None
    for name, cidrs in CDN_RANGES.items():
        for cidr in cidrs:
            try:
                if addr in ipaddress.ip_network(cidr):
                    return name
            except ValueError:
                continue
    return None

# ------------------------------------------------------------------ lookups


def lookup_host(hostname, rtypes):
    """Full report for one hostname."""
    report = {"host": hostname, "ip": [], "records": {}, "cdn": None}
    try:
        report["ip"] = sorted(resolve_all(hostname))
    except ValueError as e:
        report["error"] = str(e)
        return report

    for ip in report["ip"]:
        cdn = detect_cdn(ip)
        if cdn:
            report["cdn"] = cdn
            break

    if HAS_DNSPYTHON:
        for rtype in rtypes:
            recs = query_records(hostname, rtype)
            if recs:
                report["records"][rtype] = recs

    # CNAME chain is the fastest CDN tell
    if report["records"].get("CNAME"):
        report["cname"] = report["records"]["CNAME"]

    return report


def print_report(report, ptr=False):
    host = report["host"]
    if report.get("error"):
        print(f"\033[1;31m[-] {host}: {report['error']}\033[0m")
        return

    for ip in report["ip"]:
        print(f"\033[1;32m[+] {host} -> {ip}\033[0m")

    if report.get("cdn"):
        print(f"\033[1;33m[!] Behind CDN: {report['cdn']} "
              f"(origin IP is hidden — try subdomain/historical DNS recon)\033[0m")
    if report.get("cname"):
        print(f"[~] CNAME: {', '.join(report['cname'])}")

    for rtype, recs in report["records"].items():
        if rtype == "CNAME":
            continue
        print(f"[~] {rtype}: {', '.join(recs)}")

    if ptr:
        for ip in report["ip"]:
            ptrs = reverse_lookup(ip)
            label = f"PTR for {ip}" if ptrs else f"PTR for {ip}: none"
            print(f"[~] {label}: {', '.join(ptrs) if ptrs else 'none'}")

# -------------------------------------------------------------- CLI + menu


def run_cli(args):
    rtypes = [t.strip().upper() for t in args.types.split(",") if t.strip()]
    hosts = args.host or []
    if args.file:
        with open(args.file) as fh:
            hosts += [line.strip() for line in fh if line.strip()]

    if not hosts:
        print("No targets. Pass hostnames or -f file.txt")
        sys.exit(1)

    reports = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(lookup_host, h, rtypes): h for h in hosts}
        for fut in as_completed(futures):
            report = fut.result()
            reports.append(report)
            print_report(report, ptr=args.ptr)
            print("-" * 50)

    if args.output:
        with open(args.output, "w") as fh:
            json.dump(reports, fh, indent=2)
        print(f"[+] Results saved to {args.output}")


def interactive():
    print(BANNER)
    while True:
        print("\nOptions:")
        print("1. Find IP address")
        print("2. Full DNS scan (A, AAAA, MX, NS, TXT, CNAME, SOA)")
        print("3. Reverse lookup (IP -> hostname)")
        print("4. Exit")
        choice = input("Select an option (1-4): ").strip()

        try:
            if choice == "1":
                h = input("Hostname: ").strip()
                if h:
                    report = lookup_host(h, [])
                    print_report(report)
            elif choice == "2":
                h = input("Hostname: ").strip()
                if h:
                    report = lookup_host(h, ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"])
                    print_report(report, ptr=True)
            elif choice == "3":
                ip = input("IP address: ").strip()
                if ip:
                    ptrs = reverse_lookup(ip)
                    if ptrs:
                        print(f"\033[1;32m[+] {ip} -> {', '.join(ptrs)}\033[0m")
                    else:
                        print(f"\033[1;31m[-] No PTR record for {ip}\033[0m")
            elif choice == "4":
                print("Exiting the tool. Goodbye!")
                break
            else:
                print("Invalid option.")
        except KeyboardInterrupt:
            print()
            continue


def main():
    parser = argparse.ArgumentParser(description="IP-FINDER v2")
    parser.add_argument("host", nargs="*", help="hostname(s) to resolve")
    parser.add_argument("-f", "--file", help="file with hostnames, one per line")
    parser.add_argument("-t", "--types", default="A,AAAA,CNAME,MX,NS,TXT",
                        help="record types, comma separated (default: A,AAAA,CNAME,MX,NS,TXT)")
    parser.add_argument("-r", "--ptr", action="store_true", help="reverse lookup results")
    parser.add_argument("-o", "--output", help="save JSON report to file")
    parser.add_argument("-w", "--workers", type=int, default=20, help="threads for batch mode")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="interactive menu mode (default if no args)")
    args = parser.parse_args()

    if args.host or args.file:
        run_cli(args)
    else:
        interactive()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. Goodbye!")
