
# 🛰️ GDELT Downloader Bot

A powerful and automated Python-based bot to download **GDELT GKG datasets** with fine control over time intervals, weekday filters, retry handling, proxy rotation, and progress resumption.

---

## 🌍 About

This tool fetches GDELT GKG (Global Knowledge Graph) `.csv.zip` files from the official [GDELT Project](https://www.gdeltproject.org/) starting from **January 1, 2020** to today, with a customizable **time window** (e.g., 8 AM to 8 PM, Monday to Friday, every 60 minutes by default).

It’s particularly useful for:

- News analysis and sentiment tracking
- Macro-financial research (e.g., gold/USD correlations)
- Academic projects using global media signals

---

## ⚙️ Features

✅ Proxy support with rotation  
✅ Download resumption via progress tracking  
✅ Weekday and hour filtering  
✅ File size validation to avoid corrupted/incomplete downloads  
✅ Retry mechanism for small or failed files  
✅ Logging to both file and console  

---

## 🧰 Requirements

- Python 3.7+
- `requests`

You can install dependencies with:

```bash
pip install requests
```

---

## 📁 Directory Structure

```
gdelt_downloader/
│
├── downloader.py         # Main script to run the download
├── proxy_client.py       # Proxy logic and proxy list loader
├── proxies.txt           # Your proxy list file (http://ip:port)
├── downloader.log        # Log file generated automatically
├── progress.txt          # Auto-saved file for resume progress
└── gdelt_data/           # Folder where downloaded zip files are saved
```

---

## 🚀 How to Use

1. **Add your proxies to `proxies.txt`**:
   ```
   123.123.123.123:8080
   111.222.111.222:3128
   ```

2. **Run the downloader**:
   ```bash
   python downloader.py
   ```

3. **Stop and resume any time** — the script resumes from where it left off using `progress.txt`.

---

## 🔧 Configuration

You can customize several constants in `downloader.py`:

```python
USE_PROXY = True                # Enable or disable proxy
START_DATE = datetime.date(2020, 1, 1)
HOUR_START = 8
HOUR_END = 20
INTERVAL_MINUTES = 60
VALID_WEEKDAYS = set([0, 1, 2, 3, 4])  # Monday to Friday
```

---

## 🛡️ Proxy Handling

`proxy_client.py` handles proxy rotation:

- Loads from `proxies.txt`
- Automatically retries with the next proxy
- Falls back to direct connection if all proxies fail

---

## 📦 Download

👉 [**Download the project as ZIP**](https://github.com/mehdi-jahani/gdelt-downloader/archive/refs/heads/main.zip) *(replace with your actual GitHub link)*

Or clone it:

```bash
git clone https://github.com/mehdi-jahani/gdelt-downloader.git
```

---

## ✨ Example Use Case

Imagine you're researching media reactions to gold (XAU) and USD volatility — use this bot to grab all the relevant GDELT GKG data at 60-minute intervals, Monday to Friday, then parse it for keywords like "dollar", "inflation", and "interest rate".

Happy Downloading! 📊
