
from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
import pandas as pd
import time

# -------------------------------
# CONFIG
# -------------------------------
BASE_URL = "https://oneworldrental.com.au/"
MAX_PAGES =300
OUTPUT_FILE = "font_audit_fixed AU.xlsx"

# -------------------------------
# SETUP DRIVER (FIXED VIEWPORT)
# -------------------------------
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")  # modern headless
options.add_argument("--window-size=1920,1080")  # ✅ critical fix

driver = webdriver.Chrome(options=options)
driver.set_window_size(1920, 1080)  # extra safety

# -------------------------------
# HELPERS
# -------------------------------
visited = set()
to_visit = [BASE_URL]

def normalize_url(url):
    url = url.split("#")[0]
    url = url.split("?")[0]
    return url.rstrip("/")

def is_internal(url):
    return urlparse(url).netloc == urlparse(BASE_URL).netloc

def is_valid(url):
    if not url:
        return False
    if any(x in url for x in ["mailto:", "tel:", "javascript:"]):
        return False
    return True

# -------------------------------
# CRAWLER
# -------------------------------
def crawl():
    urls = []

    while to_visit and len(visited) < MAX_PAGES:
        url = normalize_url(to_visit.pop(0))

        if url in visited:
            continue

        print(f"Crawling: {url}")
        visited.add(url)
        urls.append(url)

        try:
            driver.get(url)
            time.sleep(2)

            links = driver.find_elements(By.XPATH, "//a[@href]")

            for link in links:
                href = link.get_attribute("href")

                if not is_valid(href):
                    continue

                href = normalize_url(href)

                if is_internal(href) and href not in visited:
                    to_visit.append(href)

        except Exception as e:
            print(f"Error crawling {url}: {e}")

    return urls

# -------------------------------
# GET TRUE COMPUTED STYLE (FIX)
# -------------------------------
def get_font_style(element):
    return driver.execute_script("""
        const el = arguments[0];
        const style = window.getComputedStyle(el);
        return {
            fontFamily: style.fontFamily,
            fontSize: style.fontSize,
            fontWeight: style.fontWeight
        };
    """, element)

# -------------------------------
# FONT EXTRACTION
# -------------------------------
def extract_fonts(url):
    data = []

    try:
        driver.get(url)
        time.sleep(2)

        elements = driver.find_elements(
            By.XPATH, "//h1 | //h2 | //h3 | //h4 | //h5 | //h6 | //p | //a | //button"
        )

        for el in elements:
            try:
                text = el.text.strip()
                if not text:
                    continue

                style = get_font_style(el)  # ✅ accurate method

                data.append({
                    "url": url,
                    "tag": el.tag_name,
                    "text_sample": text[:40],
                    "font_family": style["fontFamily"],
                    "font_size": style["fontSize"],
                    "font_weight": style["fontWeight"]
                })

            except:
                continue

    except Exception as e:
        print(f"Error extracting {url}: {e}")

    return data

# -------------------------------
# MAIN EXECUTION
# -------------------------------
all_data = []

urls = crawl()
print(f"\nTotal Crawled URLs: {len(urls)}\n")

for i, url in enumerate(urls):
    print(f"Extracting {i+1}/{len(urls)}: {url}")
    all_data.extend(extract_fonts(url))

driver.quit()

# -------------------------------
# DATA PROCESSING
# -------------------------------
df = pd.DataFrame(all_data)

if df.empty:
    print("No data collected.")
    exit()

# -------------------------------
# BASELINE (HOMEPAGE)
# -------------------------------
baseline_url = urls[0]
baseline = df[df['url'] == baseline_url]

merged = df.merge(
    baseline,
    on="tag",
    suffixes=('_current', '_baseline')
)

# -------------------------------
# FIND MISMATCHES
# -------------------------------
mismatch = merged[
    (merged['font_family_current'] != merged['font_family_baseline']) |
    (merged['font_size_current'] != merged['font_size_baseline']) |
    (merged['font_weight_current'] != merged['font_weight_baseline'])
]

# -------------------------------
# ADD PRIORITY (QA LEVEL)
# -------------------------------
def get_priority(tag):
    if tag == "h1":
        return "High"
    elif tag in ["h2", "h3"]:
        return "Medium"
    else:
        return "Low"

mismatch["priority"] = mismatch["tag"].apply(get_priority)

# -------------------------------
# EXPORT
# -------------------------------
with pd.ExcelWriter(OUTPUT_FILE) as writer:
    df.to_excel(writer, sheet_name="All Data", index=False)
    mismatch.to_excel(writer, sheet_name="Font Issues", index=False)

print(f"\n✅ Done! File saved: {OUTPUT_FILE}")