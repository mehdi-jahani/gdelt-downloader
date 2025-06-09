import requests

USE_PROXY = True  # Its value can be controlled in the main file

# Load the list of proxies from a file
def load_proxies_from_file(filename="proxies.txt"):
    proxies_list = []
    try:
        with open(filename, "r") as f:
            for line in f:
                proxy_ip = line.strip()
                if proxy_ip and not proxy_ip.startswith("#"):
                    proxies_list.append({
                        "http": f"http://{proxy_ip}",
                        "https": f"http://{proxy_ip}"
                    })
    except FileNotFoundError:
        print(f"[!] File {filename} not found. No proxies loaded.")
    return proxies_list

PROXIES_LIST = load_proxies_from_file()
current_proxy_index = 0

def get_next_working_proxy():
    global current_proxy_index
    if not PROXIES_LIST:
        return None
    proxy = PROXIES_LIST[current_proxy_index]
    return proxy

def get_with_proxy(url, **kwargs):
    global current_proxy_index

    if 'timeout' not in kwargs:
        kwargs['timeout'] = 10

    if USE_PROXY and PROXIES_LIST:
        max_tries = len(PROXIES_LIST)
        tries = 0
        while tries < max_tries:
            proxy = get_next_working_proxy()
            try:
                print(f"[~] Trying proxy: {proxy}")
                response = requests.get(url, proxies=proxy, **kwargs)
                response.raise_for_status()
                print(f"[+] Proxy success: {proxy}")
                return response
            except requests.RequestException as e:
                print(f"[x] Proxy failed: {proxy} - {e}")
                current_proxy_index = (current_proxy_index + 1) % len(PROXIES_LIST)
                tries += 1

        # If all proxies failed
        print("[!] All proxies failed. Trying without proxy.")
    
    # Fallback to direct connection
    try:
        print("[~] Trying direct connection (no proxy)...")
        response = requests.get(url, **kwargs)
        response.raise_for_status()
        print("[+] Direct connection successful.")
        return response
    except requests.RequestException as e:
        print(f"[x] Direct connection failed: {e}")
        return None
