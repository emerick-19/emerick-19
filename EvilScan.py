import socket
import threading
import subprocess
import requests
import signal
import sys
from queue import Queue
from colorama import Fore, Style, init

init(autoreset=True)

print_lock = threading.Lock()
open_ports = []

def banner():
    print(Fore.RED + Style.BRIGHT + r"""
 ______      _ _     _____                                 
|  ____|    | | |   / ____|                                
| |__  __  _| | |_ | (___   ___ _ ____   _____ _ __ _   _  
|  __| \ \/ / | __| \___ \ / _ \ '__\ \ / / _ \ '__| | | | 
| |____ >  <| | |_  ____) |  __/ |   \ V /  __/ |  | |_| | 
|______/_/\_\_|\__||_____/ \___|_|    \_/ \___|_|   \__, | 
                                                    __/ | 
                                                   |___/  
""" + Fore.YELLOW + Style.BRIGHT + """
        EvilScan - Interactive Offensive Scanner
        ⚔️  By Evil_ridder19
""" + Style.RESET_ALL)

def signal_handler(sig, frame):
    print(Fore.YELLOW + "\n[!] Interruption reçue. Fermeture propre...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def yes_or_no(question):
    return input(f"{question} (y/n) : ").strip().lower().startswith("y")

# =============================== PORT SCAN ===============================
def get_banner(ip, port):
    try:
        with socket.socket() as s:
            s.settimeout(1)
            s.connect((ip, port))
            return s.recv(1024).decode().strip()
    except:
        return None

def scan_port(ip, port):
    try:
        sock = socket.socket()
        sock.settimeout(0.5)
        sock.connect((ip, port))
        banner = get_banner(ip, port)

        with print_lock:
            result = f"[+] Port {port} OPEN"
            if banner:
                result += f" - Banner: {banner}"
            print(Fore.GREEN + result)
            open_ports.append((port, banner or ""))
        sock.close()

    except:
        pass

def threader(ip, q):
    while True:
        port = q.get()
        scan_port(ip, port)
        q.task_done()

def get_ports_input():
    ports_str = input("[?] Plage de ports (ex: 1-1000 ou 22,80,443) [défaut 1-1024] : ").strip() or "1-1024"
    if "-" in ports_str:
        start, end = map(int, ports_str.split("-"))
        return list(range(start, end + 1))
    else:
        return list(map(int, ports_str.split(",")))

def port_scan(ip, ports, thread_count=100):
    q = Queue()

    print(Fore.CYAN + f"\n[!] Scan des ports TCP sur {ip} avec {thread_count} threads...\n")
    for _ in range(thread_count):
        t = threading.Thread(target=threader, args=(ip, q), daemon=True)
        t.start()

    for port in ports:
        q.put(port)

    q.join()

# =============================== NIKTO ===============================
def run_nikto(target):
    print(Fore.CYAN + f"\n[!] Lancement de Nikto sur http://{target} ...")
    try:
        subprocess.run(["nikto", "-h", f"http://{target}"])
    except FileNotFoundError:
        print(Fore.RED + "[X] Nikto non trouvé sur le système.")

# =============================== WPSCAN ===============================
def run_wpscan(target):
    print(Fore.CYAN + f"\n[!] Lancement de WPScan sur http://{target} ...")
    try:
        subprocess.run(["wpscan", "--url", f"http://{target}", "--disable-tls-checks", "--no-update"])
    except FileNotFoundError:
        print(Fore.RED + "[X] WPScan non trouvé sur le système.")

# =============================== DIR FUZZING ===============================
def fuzz_dir(target, wordlist="/usr/share/wordlists/dirb/common.txt", threads=10):
    print(Fore.CYAN + f"\n[!] Fuzzing de répertoires sur {target} avec {threads} threads...")

    found = []

    with open(wordlist, "r") as f:
        paths = [line.strip() for line in f if line.strip()]

    def fuzz(path):
        url = f"{target}/{path}"
        try:
            r = requests.get(url, timeout=2)
            if r.status_code < 400:
                print(Fore.GREEN + f"[+] Trouvé : {url} - Code {r.status_code}")
                found.append(url)
        except:
            pass

    def worker():
        while True:
            path = q.get()
            fuzz(path)
            q.task_done()

    q = Queue()
    for _ in range(threads):
        threading.Thread(target=worker, daemon=True).start()

    for path in paths:
        q.put(path)

    q.join()

# =============================== MAIN ===============================
def save_results(ip):
    file = f"scan_{ip.replace('.', '_')}.txt"
    with open(file, "w") as f:
        for port, banner in open_ports:
            f.write(f"{ip}:{port} - {banner}\n")
    print(Fore.CYAN + f"[✓] Résultats sauvegardés dans {file}")

def main():
    banner()
    target = input("[?] Entrez l'adresse IP ou le domaine cible : ").strip()
    ports = get_ports_input()

    do_portscan = yes_or_no("[?] Voulez-vous effectuer un scan de ports ?")
    use_nikto = yes_or_no("[?] Voulez-vous lancer un scan Nikto ?")
    use_wpscan = yes_or_no("[?] Voulez-vous lancer un scan WPScan ?")
    use_fuzz = yes_or_no("[?] Voulez-vous lancer un fuzzing de répertoires ?")

    thread_count = input("[?] Nombre de threads pour le scan (défaut 100) : ").strip()
    thread_count = int(thread_count) if thread_count.isdigit() else 100

    if use_fuzz:
        try:
            fuzz_threads = int(input("[?] Nombre de threads pour le fuzzing (défaut 10) : ") or "10")
        except ValueError:
            fuzz_threads = 10
    else:
        fuzz_threads = 0

    print(Fore.CYAN + "\n[!] Démarrage du scan...")

    if do_portscan:
        port_scan(target, ports, thread_count)

    if use_nikto:
        run_nikto(target)

    if use_wpscan:
        run_wpscan(target)

    if use_fuzz:
        fuzz_dir(f"http://{target}", threads=fuzz_threads)

    if do_portscan and open_ports:
        save = yes_or_no("\n[?] Voulez-vous sauvegarder les résultats dans un fichier ?")
        if save:
            save_results(target)

    print(Fore.GREEN + "\n[✓] Scan terminé.\n")

if __name__ == "__main__":
    main()
