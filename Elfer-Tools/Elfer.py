import sys
import os
import time
import socket
import subprocess
import whois
import requests
import shutil
import ipaddress
from colorama import init, Fore, Style

# Optional: Use speedtest-cli for speed test
try:
    import speedtest
except ImportError:
    speedtest = None

# Initialize colorama
init(autoreset=True)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def spinner_animation(duration=2):
    spinner = ['|', '/', '-', '\\']
    end_time = time.time() + duration
    while time.time() < end_time:
        for symbol in spinner:
            print(Fore.YELLOW + f'\rLoading Elfer Tools... {symbol}', end='', flush=True)
            time.sleep(0.1)
    print('\r' + ' ' * 30 + '\r', end='')  # Clear line

def print_centered_text(text, color=Fore.GREEN):
    lines = text.splitlines()
    width = shutil.get_terminal_size((80, 20)).columns
    for line in lines:
        padding = max((width - len(line)) // 2, 0)
        print(' ' * padding + color + line)

def show_banner():
    clear_screen()
    banner = r"""
▄▀▀█▄▄▄▄  ▄▀▀▀▀▄     ▄▀▀▀█▄    ▄▀▀█▄▄▄▄  ▄▀▀▄▀▀▀▄ 
▐  ▄▀   ▐ █    █     █  ▄▀  ▀▄ ▐  ▄▀   ▐ █   █   █ 
  █▄▄▄▄▄  ▐    █     ▐ █▄▄▄▄     █▄▄▄▄▄  ▐  █▀▀█▀  
  █    ▌      █       █    ▐     █    ▌   ▄▀    █  
 ▄▀▄▄▄▄     ▄▀▄▄▄▄▄▄▀ █         ▄▀▄▄▄▄   █     █   
 █    ▐     █        █          █    ▐   ▐     ▐   
 ▐          ▐        ▐          ▐                 
    """
    width = shutil.get_terminal_size((80, 20)).columns
    green_banner_lines = [Fore.GREEN + line.center(width) for line in banner.splitlines()]
    print('\n'.join(green_banner_lines))
    url = "https://github.com/lodnz/Elfer-Tools"
    print(Fore.WHITE + url.center(width))
    print()

def show_menu(page=0):
    white = Fore.WHITE
    green = Fore.GREEN

    def fmt_option(num, text):
        return f"{green}[{white}{num}{green}] {text}"

    pages = [
        {
            "🔧 Tools": [
                fmt_option(1, "Ping"),
                fmt_option(2, "Port Scan"),
                fmt_option(3, "Whois")
            ],
            "📁 Info": [
                fmt_option(4, "IP Lookup"),
                fmt_option(5, "DNS Records"),
                fmt_option(6, "GeoIP")
            ],
            "⚙️ Utilities": [
                fmt_option(7, "Help"),
                fmt_option(8, "Settings"),
                fmt_option(9, "Exit")
            ]
        },
        {
            "🛠 Extra Tools": [
                fmt_option(10, "Traceroute"),
                fmt_option(11, "Reverse DNS"),
                fmt_option(12, "SSL Checker")
            ],
            "📡 Network": [
                fmt_option(13, "ARP Scan"),
                fmt_option(14, "MAC Lookup"),
                fmt_option(15, "Subnet Info")
            ],
            "🔍 Analysis": [
                fmt_option(16, "Header Check"),
                fmt_option(17, "Breach Check"),
                fmt_option(18, "Speed Test")
            ]
        }
    ]

    width = shutil.get_terminal_size((80, 20)).columns
    nav_prompt = white + "Please choose an option (or 'N' for next, 'B' for back):"
    print(nav_prompt.center(width))
    print()

    current = pages[page % len(pages)]
    categories = list(current.keys())
    options_list = list(current.values())

    max_options = max(len(opts) for opts in options_list)
    col_width = 30
    spacing = 6

    columns = []
    for opts, cat in zip(options_list, categories):
        col_lines = [green + cat]
        for i, opt in enumerate(opts):
            line_char = '│' if i < len(opts) - 1 else ' '
            col_lines.append(f" {line_char}-- {opt}")
        while len(col_lines) < max_options + 1:
            col_lines.append('')
        columns.append(col_lines)

    for i in range(max_options + 1):
        left_col = columns[0][i].ljust(col_width)
        center_col = columns[1][i].center(col_width)
        right_col = columns[2][i].rjust(col_width)
        print(f"{left_col}{' ' * spacing}{center_col}{' ' * spacing}{right_col}")

def menu_loop():
    current_page = 0
    while True:
        show_banner()
        show_menu(current_page)
        choice = input(Fore.WHITE + "\nYour choice: ").strip().upper()
        if choice == 'N':
            current_page += 1
        elif choice == 'B':
            current_page -= 1
        elif choice.isdigit():
            handle_choice(choice)
            input(Fore.GREEN + "\nPress Enter to return to the main menu...")
        else:
            print(Fore.RED + "Invalid input. Please enter a number or 'N'/'B'.")
            input(Fore.GREEN + "\nPress Enter to return to the main menu...")

# --- [COMMAND IMPLEMENTATIONS] ---

def ping_host():
    target = input("Enter host to ping: ").strip()
    param = "-n" if sys.platform.startswith("win") else "-c"
    try:
        response = subprocess.run(["ping", param, "4", target], capture_output=True, text=True)
        if response.returncode == 0:
            print(Fore.GREEN + f"\nPing to {target} successful:\n{response.stdout}")
        else:
            print(Fore.RED + f"\nPing failed:\n{response.stderr}")
    except Exception as e:
        print(Fore.RED + f"Error running ping: {e}")

def port_scan():
    target = input("Enter target IP or hostname: ").strip()
    ports_input = input("Enter ports to scan (comma-separated): ").strip()
    ports = [p.strip() for p in ports_input.split(',') if p.strip().isdigit()]
    for port in ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((target, int(port)))
                if result == 0:
                    print(Fore.GREEN + f"Port {port} is open on {target}")
                else:
                    print(Fore.RED + f"Port {port} is closed on {target}")
        except Exception as e:
            print(Fore.RED + f"Error scanning port {port}: {e}")

def whois_lookup():
    domain = input("Enter domain to lookup: ").strip()
    try:
        domain_info = whois.whois(domain)
        print(Fore.GREEN + f"\nWhois information for {domain}:\n{domain_info}")
    except Exception as e:
        print(Fore.RED + f"Error retrieving Whois: {e}")

def ip_lookup():
    ip = input("Enter IP address to lookup: ").strip()
    try:
        r = requests.get(f"https://ipinfo.io/{ip}/json")
        if r.status_code == 200:
            print(Fore.GREEN + f"\nIP info:\n{r.json()}")
        else:
            print(Fore.RED + f"Failed to fetch info: {r.text}")
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Request failed: {e}")

def dns_records():
    domain = input("Enter domain: ").strip()
    try:
        r = requests.get(f"https://dns.google/resolve?name={domain}")
        if r.status_code == 200:
            print(Fore.GREEN + f"\nDNS info:\n{r.json()}")
        else:
            print(Fore.RED + f"Failed: {r.text}")
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Request failed: {e}")

def geoip_lookup():
    ip = input("Enter IP for GeoIP lookup: ").strip()
    try:
        r = requests.get(f"https://ipinfo.io/{ip}/json")
        print(Fore.GREEN + f"\nGeoIP info:\n{r.json()}")
    except Exception as e:
        print(Fore.RED + f"GeoIP lookup failed: {e}")

def show_help():
    print(Fore.WHITE + "\nHelp:\nUse numbers to choose a tool, 'N' for next, 'B' for back.")

def show_settings():
    print(Fore.GREEN + "\nSettings menu is coming soon.")

def exit_program():
    print(Fore.GREEN + "\nGoodbye!")
    sys.exit()

def traceroute():
    host = input("Enter host: ").strip()
    try:
        cmd = ["tracert", host] if sys.platform.startswith("win") else ["traceroute", host]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(Fore.GREEN + f"\nTraceroute output:\n{res.stdout}")
        else:
            print(Fore.RED + f"\nTraceroute failed:\n{res.stderr}")
    except Exception as e:
        print(Fore.RED + f"Traceroute error: {e}")

def reverse_dns():
    ip = input("Enter IP: ").strip()
    try:
        name, _, _ = socket.gethostbyaddr(ip)
        print(Fore.GREEN + f"Reverse DNS: {name}")
    except Exception as e:
        print(Fore.RED + f"Reverse DNS error: {e}")

def ssl_checker():
    domain = input("Domain to check SSL: ").strip()
    import ssl
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.settimeout(3)
            s.connect((domain, 443))
            cert = s.getpeercert()
            print(Fore.GREEN + f"\nSSL cert:\n{cert}")
    except Exception as e:
        print(Fore.RED + f"SSL check failed: {e}")

def arp_scan():
    print(Fore.YELLOW + "\nARP scan feature not yet available.")

def mac_lookup():
    mac = input("Enter MAC: ").strip()
    try:
        r = requests.get(f"https://api.macvendors.com/{mac}")
        if r.status_code == 200:
            print(Fore.GREEN + f"Vendor: {r.text}")
        else:
            print(Fore.RED + "MAC not found")
    except Exception as e:
        print(Fore.RED + f"MAC lookup error: {e}")

def subnet_info():
    subnet = input("Enter CIDR subnet: ").strip()
    try:
        net = ipaddress.ip_network(subnet, strict=False)
        print(Fore.GREEN + f"\nNetwork: {net.network_address}\nBroadcast: {net.broadcast_address}\nHosts: {net.num_addresses}\nMask: {net.netmask}")
    except Exception as e:
        print(Fore.RED + f"Invalid subnet: {e}")

def header_check():
    url = input("Enter URL: ").strip()
    try:
        r = requests.head(url)
        print(Fore.GREEN + f"\nHeaders:\n{r.headers}")
    except Exception as e:
        print(Fore.RED + f"Header check error: {e}")

def breach_check():
    email = input("Enter email: ").strip()
    print(Fore.YELLOW + f"\nBreach check requires API key for haveibeenpwned.com.")

def speed_test():
    if not speedtest:
        print(Fore.RED + "speedtest module not installed. Use: pip install speedtest-cli")
        return
    try:
        st = speedtest.Speedtest()
        print(Fore.YELLOW + "Testing download speed...")
        down = st.download()
        print(Fore.YELLOW + "Testing upload speed...")
        up = st.upload()
        print(Fore.GREEN + f"Download: {down / 1_000_000:.2f} Mbps\nUpload: {up / 1_000_000:.2f} Mbps")
    except Exception as e:
        print(Fore.RED + f"Speed test failed: {e}")

def handle_choice(choice):
    choice_map = {
        '1': ping_host,
        '2': port_scan,
        '3': whois_lookup,
        '4': ip_lookup,
        '5': dns_records,
        '6': geoip_lookup,
        '7': show_help,
        '8': show_settings,
        '9': exit_program,
        '10': traceroute,
        '11': reverse_dns,
        '12': ssl_checker,
        '13': arp_scan,
        '14': mac_lookup,
        '15': subnet_info,
        '16': header_check,
        '17': breach_check,
        '18': speed_test
    }
    func = choice_map.get(choice)
    if func:
        clear_screen()
        func()
    else:
        print(Fore.RED + "Invalid choice.")

if __name__ == "__main__":
    spinner_animation()
    menu_loop()