import os
import datetime
import logging
from time import sleep

# Control variable for using proxy
USE_PROXY = False  

from proxy_client import get_with_proxy  

# Logger settings
logging.basicConfig(
    filename='downloader.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

START_DATE = datetime.date(2020, 1, 1)
END_DATE = datetime.date.today()

DOWNLOAD_DIR = "gdelt_data"
PROGRESS_FILE = "progress.txt"

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

HOUR_START = 8
HOUR_END = 20
INTERVAL_MINUTES = 60
VALID_WEEKDAYS = set([0, 1, 2, 3, 4])  # Monday to Friday

def build_gkg_url(dt: datetime.datetime):
    timestamp = dt.strftime("%Y%m%d%H%M%S")
    return f"http://data.gdeltproject.org/gdeltv2/{timestamp}.gkg.csv.zip"

def download_file(url, save_path, retry=True):
    MIN_SIZE_KB = 100
    AVG_EXPECTED_KB = 2048  # Average normal file size

    if os.path.exists(save_path):
        size_bytes = os.path.getsize(save_path)
        size_kb = size_bytes / 1024
        if size_kb < MIN_SIZE_KB or size_kb < 0.05 * AVG_EXPECTED_KB:
            logging.warning(f"File too small or corrupted: {save_path} ({size_kb:.2f} KB) — deleting and retrying...")
            os.remove(save_path)
        else:
            logging.info(f"File already downloaded: {save_path} ({size_kb:.2f} KB)")
            print(f"File already downloaded: {save_path} ({size_kb:.2f} KB)")
            return True

    try:
        logging.info(f"Downloading: {url}")
        if USE_PROXY:
            r = get_with_proxy(url, timeout=30, stream=True)
        else:
            import requests
            r = requests.get(url, timeout=30, stream=True)
        
        if r and r.status_code == 200:
            total_length = r.headers.get('content-length')
            if total_length is None:
                with open(save_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            else:
                total_length = int(total_length)
                downloaded = 0
                with open(save_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            done = int(50 * downloaded / total_length)
                            print(f"\r[{'=' * done}{' ' * (50 - done)}] {downloaded * 100 / total_length:.2f}%", end='')
                print()

            size_bytes = os.path.getsize(save_path)
            size_kb = size_bytes / 1024

            if size_kb < MIN_SIZE_KB or size_kb < 0.05 * AVG_EXPECTED_KB:
                logging.warning(f"Downloaded file is too small: {save_path} ({size_kb:.2f} KB)")
                os.remove(save_path)
                if retry:
                    logging.info("Retrying download due to small file size...")
                    return download_file(url, save_path, retry=False)
                else:
                    return False

            logging.info(f"Saved: {save_path} ({size_kb:.2f} KB)")
            print(f"Saved: {save_path} ({size_kb:.2f} KB)")
            
            sleep(2)  # Wait for 2 seconds after downloading
            
            return True
        else:
            status = r.status_code if r else "No response"
            logging.error(f"Error downloading: {url} - Status: {status}")
            print(f"Error downloading: {url} - Status: {status}")
            return False
    except Exception as e:
        logging.error(f"Error downloading: {url} - {e}")
        print(f"Error downloading: {url} - {e}")
        return False

def save_progress(dt: datetime.datetime):
    with open(PROGRESS_FILE, "w") as f:
        f.write(dt.strftime("%Y-%m-%d %H:%M:%S"))
    logging.info(f"Progress saved: {dt}")

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            dt_str = f.read().strip()
            try:
                logging.info("Loading progress...")
                return datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            except Exception as e:
                logging.warning(f"Error loading progress: {e}")
    return None

def main():
    logging.info("Starting download")
    progress_dt = load_progress()
    if progress_dt:
        logging.info(f"Continuing download from: {progress_dt}")
        current_dt = progress_dt
    else:
        current_dt = datetime.datetime.combine(START_DATE, datetime.time(HOUR_START, 0, 0))

    while current_dt.date() <= END_DATE:
        if current_dt.weekday() not in VALID_WEEKDAYS:
            logging.info(f"Invalid day: {current_dt.date()} (skipped)")
            current_dt = datetime.datetime.combine(current_dt.date() + datetime.timedelta(days=1), datetime.time(HOUR_START, 0, 0))
            continue

        if current_dt.hour > HOUR_END:
            current_dt = datetime.datetime.combine(current_dt.date() + datetime.timedelta(days=1), datetime.time(HOUR_START, 0, 0))
            continue

        url = build_gkg_url(current_dt)
        filename = os.path.basename(url)
        save_path = os.path.join(DOWNLOAD_DIR, filename)

        success = download_file(url, save_path)
        if success:
            save_progress(current_dt)
        else:
            logging.warning("Error downloading file, retrying after delay")

        current_dt += datetime.timedelta(minutes=INTERVAL_MINUTES)
        sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Download interrupted by user.")
        print("\n[!] Download interrupted by user.")
