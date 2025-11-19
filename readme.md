
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Shodan](https://img.shields.io/badge/shodan-paid%20plan-green)
![License](https://img.shields.io/github/license/voidsshadows/hikvision-city-hunter)
![Stars](https://img.shields.io/github/stars/voidsshadows/hikvision-city-hunter?style=social)

> **The ultimate 2025 city-level reconnaissance & exploitation tool for Hikvision IP cameras, DVRs, and NVRs**  
> Live console output • DVRs/NVRs highlighted in **purple** • Cameras in **green** • Snapshot auto-download • Honeypot filtering
╔══════════════════════════════════════════════════════════╗
║         HIKVISION 2025 ULTIMATE CITY HUNTER              ║
║         Target: New York   | Key: admin:12345           ║
║         DVRs & NVRs = PURPLE | Cameras = Green        ║
╚══════════════════════════════════════════════════════════╝
text### Features
- City-targeted Shodan discovery (`hikvision city:"New York"`)
- Exploits the legendary `auth=YWRtaW46MTEK` backdoor (**admin:12345** – still king in 2025)
- Full device enumeration: Model • Serial • Firmware • MAC • Device Name
- **Automatic DVR/NVR detection** – highlighted in **purple** for instant jackpot recognition
- Live snapshot download (`/onvif-http/snapshot`)
- Honeypot filtering (skips devices with >12 open ports)
- Threaded high-speed scanning (safe concurrency 100–180)
- Real-time colorful console output
- Auto-retry on Shodan rate limits + credit check
- Clean hits file + timestamped snapshots folder
