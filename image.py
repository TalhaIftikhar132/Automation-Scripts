import time
import requests
import openpyxl
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter, Retry

# --------------------------
# CONFIGURATION
# --------------------------
DEVICES = {
    "Desktop": (1920, 1080),
    "Mobile": (375, 667),
}

START_URL = "https://technologyrental.sg/"  # Change to your website
MAX_PAGES = 300
MAX_WORKERS = 40
TIMEOUT = 10
PAGE_WAIT = 2

# --------------------------
# GLOBAL SESSION WITH RETRIES
# --------------------------
session = requests.Session()
retries = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retries)
session.mount("http://", adapter)
session.mount("https://", adapter)

# --------------------------
# DRIVER SETUP
# --------------------------
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# --------------------------
# IMAGE CHECKING
# --------------------------
def check_image_status(src):
    if not src:
        return "Missing src"
    try:
        response = session.head(src, timeout=TIMEOUT)
        if response.status_code == 405:
            response = session.get(src, timeout=TIMEOUT)
        if response.status_code == 200:
            return "OK"
        return f"Broken (Status {response.status_code})"
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

# --------------------------
# IMAGE EXTRACTION
# --------------------------
def extract_image_sources(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    images = driver.find_elements(By.TAG_NAME, "img")
    img_urls = set()

    for img in images:
        possible_attrs = [
            img.get_attribute("src"),
            img.get_attribute("data-src"),
            img.get_attribute("data-lazy"),
            img.get_attribute("data-original"),
            img.get_attribute("data-srcset"),
            img.get_attribute("srcset"),
        ]

        for attr in possible_attrs:
            if attr and attr.strip():
                attr = attr.strip()
                if attr.startswith("//"):
                    attr = "https:" + attr
                elif attr.startswith("/"):
                    attr = driver.current_url.rstrip("/") + attr
                if attr.startswith("http"):
                    img_urls.add(attr)
                break
    return list(img_urls)

# --------------------------
# IMAGE CHECK WRAPPER
# --------------------------
def check_images(driver, device):
    results = []
    img_srcs = extract_image_sources(driver)
    if not img_srcs:
        print(f"⚠️  No images found on {driver.current_url} [{device}]")
        return [(device, driver.current_url, "No Images Found", "N/A")]

    print(f"🔍 Checking images for {device} mode...")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        statuses = list(executor.map(check_image_status, img_srcs))

    valid = sum(1 for s in statuses if s == "OK")
    broken = len(statuses) - valid
    print(f"✅ {valid} valid images | ❌ {broken} broken images")

    for src, status in zip(img_srcs, statuses):
        results.append((device, driver.current_url, src, status))
    return results

# --------------------------
# LINK COLLECTION
# --------------------------
def get_links(driver, base_url):
    links = set()
    for el in driver.find_elements(By.TAG_NAME, "a"):
        href = el.get_attribute("href")
        if href and href.startswith(base_url):
            links.add(href.split("#")[0])
    return links

# --------------------------
# SAVE TO EXCEL
# --------------------------
def save_to_excel(results, filename="broken_images_fast_audit.xlsx"):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Broken Images Report"
    headers = ["Device", "Page URL", "Image URL", "Status"]
    ws.append(headers)
    for row in results:
        ws.append(row)
    wb.save(filename)
    print(f"\n📊 Results saved as: {filename}")

# --------------------------
# MAIN CRAWLER
# --------------------------
def crawl_site():
    all_results = []
    visited = set()
    queue = deque([START_URL])
    base_url = urlparse(START_URL).scheme + "://" + urlparse(START_URL).netloc
    driver = setup_driver()

    print("\n🚀 Starting Broken Image Crawler...\n")

    while queue and len(visited) < MAX_PAGES:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)

        print(f"\n🌍 Crawling {url} ({len(visited)}/{MAX_PAGES})")

        try:
            driver.get(url)
            time.sleep(PAGE_WAIT)

            for device, (width, height) in DEVICES.items():
                driver.set_window_size(width, height)
                time.sleep(0.5)
                results = check_images(driver, device)
                all_results.extend(results)

            links = get_links(driver, base_url)
            for link in links:
                if link not in visited and len(visited) + len(queue) < MAX_PAGES:
                    queue.append(link)

        except Exception as e:
            print(f"⚠️ Error on {url}: {e}")

    driver.quit()
    save_to_excel(all_results)

    # --------------------------
    # FINAL SUMMARY OUTPUT
    # --------------------------
    total_pages = len(visited)
    total_images = len(all_results)
    total_broken = sum(1 for _, _, _, s in all_results if s != "OK")

    print("\n📋 Summary Report")
    print(f"- Total Pages Crawled: {total_pages}")
    print(f"- Total Images Checked: {total_images}")
    print(f"- Total Broken Images Found: {total_broken}")
    print("✅ Script completed successfully!")

# --------------------------
# RUN SCRIPT
# --------------------------
if __name__ == "__main__":
    crawl_site()
