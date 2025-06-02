import sys
import os
import time
import socket
import subprocess
import whois
import requests
import shutil
import ipaddress
import uuid
import random
import tempfile
import webbrowser
import phonenumbers
from colorama import init, Fore, Style

try:
    import speedtest
except ImportError:
    speedtest = None

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
    print('\r' + ' ' * 30 + '\r', end='')

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
    url = "https://github.com/lodnz/Elfer-Tools"
    width = shutil.get_terminal_size((80, 20)).columns
    lines = banner.splitlines()
    for line in lines:
        print(Fore.GREEN + line.center(width))
        time.sleep(0.05)
    print()
    print(Fore.WHITE + url.center(width))
    print()

def show_menu(page=0):
    import re
    white = Fore.WHITE
    green = Fore.GREEN
    reset = Style.RESET_ALL

    def fmt_option(num, text):
        return f"{green}[{white}{num}{green}]{white} {text}"

    def strip_ansi(text):
        return re.sub(r'\x1b\[[0-9;]*m', '', text)

    def visible_len(s):
        return len(strip_ansi(s))

    def pad_to_visible(s, width):
        pad = width - visible_len(s)
        return s + '\u200B' * pad

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
        },
        {
            "🔐 Security": [
                fmt_option(19, "Password Strength Checker"),
                fmt_option(20, "Strong Password Generator"),
                fmt_option(21, "UUID Generator")
            ],
            "🕵️ OSINT": [
                fmt_option(22, "Useful OSINT Sites"),
                fmt_option(23, "Email Validation"),
                fmt_option(24, "User-Agent Parser")
            ],
            "⚡ Miscellaneous": [
                fmt_option(25, "Random Quote Generator")
            ]
        }
    ]

    term_width = shutil.get_terminal_size((80, 20)).columns
    nav_prompt = white + "Please choose an option (or 'N' for next, 'B' for back):"
    print(nav_prompt.center(term_width))
    print()

    current = pages[page % len(pages)]
    categories = list(current.keys())
    option_sets = list(current.values())

    col_width = 28
    spacing = 2

    columns = []
    max_col_height = 0

    for cat, opts in zip(categories, option_sets):
        col = [green + cat]
        max_opt_len = max(visible_len(o) for o in opts)
        for i, o in enumerate(opts):
            connector = "├──" if i < len(opts) - 1 else "└──"
            line = f"{green}{connector} {pad_to_visible(o, max_opt_len)}"
            col.append(line)
        max_col_height = max(max_col_height, len(col))
        columns.append(col)

    for col in columns:
        while len(col) < max_col_height:
            col.append('\u200B' * col_width)

    total_width = (col_width * len(columns)) + (spacing * (len(columns) - 1))
    left_padding = max((term_width - total_width) // 2, 0)

    for row_idx in range(max_col_height):
        row_parts = []
        for col in columns:
            cell = col[row_idx]
            padded = pad_to_visible(cell, col_width)
            row_parts.append(padded)
        row_str = (" " * spacing).join(row_parts)
        print(" " * left_padding + row_str)


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

# --- [COMMAND IMPLEMENTATIONS] ---import sys
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
    url = "https://github.com/lodnz/Elfer-Tools"
    width = shutil.get_terminal_size((80, 20)).columns
    lines = banner.splitlines()

    for line in lines:
        print(Fore.GREEN + line.center(width))
        time.sleep(0.05)  # Delay for fade-in effect

    print()
    print(Fore.WHITE + url.center(width))
    print()

def show_menu(page=0):
    import re

    white = Fore.WHITE
    green = Fore.GREEN
    reset = Style.RESET_ALL

    def fmt_option(num, text):
        return f"{green}[{white}{num}{green}]{white} {text}"

    def strip_ansi(text):
        return re.sub(r'\x1b\[[0-9;]*m', '', text)

    def visible_len(s):
        return len(strip_ansi(s))

    def pad_to_visible(s, width):
        pad = width - visible_len(s)
        return s + '\u200B' * pad

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
        },
        {
     	   "🕵️ OSINT Tools": [
               fmt_option(19, "Username Lookup"),
               fmt_option(20, "Email Finder"),
               fmt_option(21, "Social Media Check"),
               fmt_option(22, "Google Dork Scanner")
        ],
    	    "🌐 Public Data": [
               fmt_option(23, "Phone Number Info"),
               fmt_option(24, "Public IP Info"),
               fmt_option(25, "Leaked Paste Search")
        ],
    	    "📂 Metadata": [
               fmt_option(26, "File Metadata Viewer"),
               fmt_option(27, "Image EXIF Reader"),
               fmt_option(28, "Clear Cache & Temp")
        ]
    }
]


    term_width = shutil.get_terminal_size((80, 20)).columns
    nav_prompt = white + "Please choose an option (or 'N' for next, 'B' for back):"
    print(nav_prompt.center(term_width))
    print()

    current = pages[page % len(pages)]
    categories = list(current.keys())
    option_sets = list(current.values())

    col_width = 28
    spacing = 2

    columns = []
    max_col_height = 0
    for cat, opts in zip(categories, option_sets):
        col = [green + cat]
        max_opt_len = max(visible_len(o) for o in opts)
        for i, o in enumerate(opts):
            connector = "├──" if i < len(opts) - 1 else "└──"
            line = f"{green}{connector} {pad_to_visible(o, max_opt_len)}"
            col.append(line)
        max_col_height = max(max_col_height, len(col))
        columns.append(col)

    for col in columns:
        while len(col) < max_col_height:
            col.append('\u200B' * col_width)

    # Compute full row width to center layout
    total_width = (col_width * len(columns)) + (spacing * (len(columns) - 1))
    left_padding = max((term_width - total_width) // 2, 0)

    for row_idx in range(max_col_height):
        row_parts = []
        for col in columns:
            cell = col[row_idx]
            padded = pad_to_visible(cell, col_width)
            row_parts.append(padded)
        row_str = (" " * spacing).join(row_parts)
        print(" " * left_padding + row_str)

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

def username_lookup():
    username = input("Enter the username to search: ").strip()
    try:
        subprocess.run(['python3', 'sherlock/sherlock.py', username])
    except Exception as e:
        print(Fore.RED + f"Error during username lookup: {e}")

def email_finder():
    name = input("Enter full name: ").strip()
    domain = input("Enter possible domain (e.g. example.com): ").strip()
    print("Coming Soon")

def social_media_check():
    email = input("Enter the email to check: ").strip()
    try:
        subprocess.run(['python3', 'social-analyzer/analyzer.py', '--email', email])
    except Exception as e:
        print(Fore.RED + f"Error during social media check: {e}")

def google_dork_scanner():
    domain = input("Enter target domain (e.g. example.com): ").strip()
    dorks = [
        f'site:{domain} intitle:"index of"',
        f'site:{domain} ext:log',
        f'site:{domain} ext:sql | ext:db',
        f'site:{domain} inurl:admin',
        f'site:{domain} ext:env',
        f'site:{domain} "phpinfo()"',
        f'site:{domain} "Warning: mysqli"'
    ]

    print(Fore.GREEN + f"\nGenerated Dorks for {domain}:")
    for dork in dorks:
        url = f"https://www.google.com/search?q={requests.utils.quote(dork)}"
        print(Fore.YELLOW + dork)
        webbrowser.open_new_tab(url)

from phonenumbers import geocoder, carrier

def phone_number_info():
    number = input("Enter the phone number with country code (e.g., +441632960961): ").strip()
    try:
        parsed_number = phonenumbers.parse(number)
        location = geocoder.description_for_number(parsed_number, "en")
        service_provider = carrier.name_for_number(parsed_number, "en")
        print(Fore.GREEN + f"Location: {location}")
        print(Fore.GREEN + f"Carrier: {service_provider}")
    except Exception as e:
        print(Fore.RED + f"Error retrieving phone number info: {e}")

def public_ip_info():
    try:
        r = requests.get("https://ipinfo.io/json")
        print(Fore.GREEN + f"\nYour public IP info:\n{r.json()}")
    except Exception as e:
        print(Fore.RED + f"Failed to get public IP info: {e}")

def leaked_paste_search():
    keyword = input("Enter the keyword to search in pastes: ").strip()
    try:
        subprocess.run(['python3', 'pastehunter/pastehunter.py', '--search', keyword])
    except Exception as e:
        print(Fore.RED + f"Error during leaked paste search: {e}")

def file_metadata_viewer():
    filepath = input("Enter file path: ").strip()
    if not os.path.isfile(filepath):
        print(Fore.RED + "File not found.")
        return
    try:
        import mimetypes
        print(Fore.GREEN + f"\nFile: {filepath}")
        print("Type:", mimetypes.guess_type(filepath)[0])
        print("Size:", os.path.getsize(filepath), "bytes")
        print("Created:", time.ctime(os.path.getctime(filepath)))
        print("Modified:", time.ctime(os.path.getmtime(filepath)))
    except Exception as e:
        print(Fore.RED + f"Error reading file metadata: {e}")

def image_exif_reader():
    filepath = input("Enter image file path: ").strip()
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
        image = Image.open(filepath)
        exif_data = image._getexif()
        if not exif_data:
            print(Fore.RED + "No EXIF data found.")
            return
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            print(f"{tag_name}: {value}")
    except Exception as e:
        print(Fore.RED + f"EXIF reading failed: {e}")

def clear_temp():
    temp_dir = tempfile.gettempdir()
    try:
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(Fore.RED + f"Failed to delete {file_path}. Reason: {e}")
        print(Fore.GREEN + "Temporary files cleared successfully.")
    except Exception as e:
        print(Fore.RED + f"Error clearing temporary files: {e}")

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
        '18': speed_test,
        '19': username_lookup,
        '20': email_finder,
        '21': social_media_check,
        '22': google_dork_scanner,
        '23': phone_number_info,
        '24': public_ip_info,
        '25': leaked_paste_search,
        '26': file_metadata_viewer,
        '27': image_exif_reader,
        '28': clear_temp
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

def password_strength_checker():
    pwd = input("Enter a password to check strength: ").strip()
    length = len(pwd)
    has_upper = any(c.isupper() for c in pwd)
    has_lower = any(c.islower() for c in pwd)
    has_digit = any(c.isdigit() for c in pwd)
    has_special = any(c in string.punctuation for c in pwd)

    score = sum([length >= 8, has_upper, has_lower, has_digit, has_special])

    if score <= 2:
        strength = "Weak"
        color = Fore.RED
    elif score == 3 or score == 4:
        strength = "Moderate"
        color = Fore.YELLOW
    else:
        strength = "Strong"
        color = Fore.GREEN

    print(color + f"Password strength: {strength}")
    print(f"Details: Length={length}, Uppercase={has_upper}, Lowercase={has_lower}, Digit={has_digit}, Special Char={has_special}")

def strong_password_generator():
    length = input("Enter desired password length (min 8): ").strip()
    if not length.isdigit() or int(length) < 8:
        print(Fore.RED + "Invalid length. Must be an integer >= 8.")
        return
    length = int(length)

    chars = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(chars) for _ in range(length))
    print(Fore.GREEN + f"Generated strong password: {password}")

def uuid_generator():
    u = uuid.uuid4()
    print(Fore.GREEN + f"Generated UUID4: {u}")

def useful_osint_sites():
    sites = [
        "https://inteltechniques.com/",
        "https://osintframework.com/",
        "https://haveibeenpwned.com/",
        "https://www.shodan.io/",
        "https://censys.io/"
    ]
    print(Fore.GREEN + "Useful OSINT Sites:")
    for site in sites:
        print(f" - {site}")

def email_validation():
    import re
    email = input("Enter email to validate: ").strip()
    regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if re.match(regex, email):
        print(Fore.GREEN + "Valid email format.")
    else:
        print(Fore.RED + "Invalid email format.")

def user_agent_parser():
    ua = input("Enter User-Agent string: ").strip()
    # Simple checks for example purposes:
    if "Firefox" in ua:
        print(Fore.GREEN + "Browser: Firefox")
    elif "Chrome" in ua:
        print(Fore.GREEN + "Browser: Chrome")
    elif "Safari" in ua:
        print(Fore.GREEN + "Browser: Safari")
    else:
        print(Fore.YELLOW + "Browser: Unknown")

def random_quote_generator():
    quotes = [
        "The best way to get started is to quit talking and begin doing. – Walt Disney",
        "Don't let yesterday take up too much of today. – Will Rogers",
        "You learn more from failure than from success. – Unknown",
        "It's not whether you get knocked down, it's whether you get up. – Vince Lombardi",
        "If you are working on something exciting, it will keep you motivated. – Unknown"
    ]
    print(Fore.CYAN + random.choice(quotes))

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
        '18': speed_test,
        '19': password_strength_checker,
        '20': strong_password_generator,
        '21': uuid_generator,
        '22': useful_osint_sites,
        '23': email_validation,
        '24': user_agent_parser,
        '25': random_quote
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