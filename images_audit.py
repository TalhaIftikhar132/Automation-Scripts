# from selenium import webdriver
# from selenium.webdriver.common.by import By
# import time
# import requests
# from urllib.parse import urljoin, urlparse
# from PIL import Image
# from io import BytesIO
# import pandas as pd
# from bs4 import BeautifulSoup

# # ---------------- CONFIG ----------------
# START_URL = "https://Example"   # Change this
# MAX_PAGES = 20
# OUTPUT_FILE = "images_data UK site.xlsx"
# # ---------------------------------------

# # Setup driver
# options = webdriver.ChromeOptions()
# options.add_argument("--headless")
# driver = webdriver.Chrome(options=options)

# visited = set()
# to_visit = [START_URL]
# image_data = []

# def get_image_info(img_url):
#     try:
#         response = requests.get(img_url, timeout=10)

#         status_code = response.status_code
#         is_broken = "Yes" if status_code != 200 else "No"

#         if status_code == 200:
#             size_kb = round(len(response.content) / 1024, 2)

#             try:
#                 image = Image.open(BytesIO(response.content))
#                 width, height = image.size
#                 format_type = image.format
#             except:
#                 width, height, format_type = None, None, None
#         else:
#             size_kb, width, height, format_type = None, None, None

#         return status_code, is_broken, size_kb, width, height, format_type

#     except Exception:
#         return "Error", "Yes", None, None, None, None


# while to_visit and len(visited) < MAX_PAGES:
#     url = to_visit.pop(0)

#     if url in visited:
#         continue

#     print(f"Scraping: {url}")
#     visited.add(url)

#     try:
#         driver.get(url)
#         time.sleep(2)

#         soup = BeautifulSoup(driver.page_source, "html.parser")

#         # -------- GET ALL IMAGES --------
#         images = soup.find_all("img")

#         for img in images:
#             img_src = img.get("src") or img.get("data-src")  # handle lazy load
#             alt_text = img.get("alt", "")

#             if not img_src:
#                 continue

#             img_url = urljoin(url, img_src)

#             status_code, is_broken, size_kb, width, height, format_type = get_image_info(img_url)

#             image_data.append({
#                 "Page URL": url,
#                 "Image URL": img_url,
#                 "Alt Text": alt_text,
#                 "Format": format_type,
#                 "Size (KB)": size_kb,
#                 "Width": width,
#                 "Height": height,
#                 "Status Code": status_code,
#                 "Broken Image": is_broken
#             })

#         # -------- GET INTERNAL LINKS --------
#         links = soup.find_all("a", href=True)

#         for link in links:
#             href = link["href"]
#             full_url = urljoin(url, href)

#             # Stay within same domain
#             if urlparse(full_url).netloc == urlparse(START_URL).netloc:
#                 if full_url not in visited:
#                     to_visit.append(full_url)

#     except Exception as e:
#         print(f"Error: {e}")

# driver.quit()

# # -------- SAVE TO EXCEL --------
# df = pd.DataFrame(image_data)

# # Optional: Remove duplicate image URLs
# df = df.drop_duplicates(subset=["Image URL", "Page URL"])

# df.to_excel(OUTPUT_FILE, index=False)

# print(f"\n✅ Data saved to {OUTPUT_FILE}")










from selenium import webdriver
import time
import requests
from urllib.parse import urljoin
from PIL import Image
from io import BytesIO
import pandas as pd
from bs4 import BeautifulSoup

# ---------------- CONFIG ----------------
# ADD ONLY SPECIFIC PAGES HERE
TARGET_PAGES = [
    "https:Example",
    "https://example"
]

OUTPUT_FILE = "OWR AU specific_pages_image_audit.xlsx"
# ---------------------------------------

# Setup Chrome
options = webdriver.ChromeOptions()
options.add_argument("--headless")

driver = webdriver.Chrome(options=options)

image_data = []

# ---------------------------------------
# IMAGE INFO FUNCTION
# ---------------------------------------
def get_image_info(img_url):
    try:
        response = requests.get(img_url, timeout=10)

        status_code = response.status_code
        is_broken = "Yes" if status_code != 200 else "No"

        if status_code == 200:
            size_kb = round(len(response.content) / 1024, 2)

            try:
                image = Image.open(BytesIO(response.content))
                width, height = image.size
                format_type = image.format
            except:
                width, height, format_type = None, None, None
        else:
            size_kb, width, height, format_type = None, None, None

        return status_code, is_broken, size_kb, width, height, format_type

    except:
        return "Error", "Yes", None, None, None, None

# ---------------------------------------
# MAIN LOOP FOR SPECIFIC PAGES
# ---------------------------------------
for url in TARGET_PAGES:

    print(f"Scraping: {url}")

    try:
        driver.get(url)
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        images = soup.find_all("img")

        for img in images:

            img_src = (
                img.get("src")
                or img.get("data-src")
                or img.get("data-lazy-src")
            )

            alt_text = img.get("alt", "")

            if not img_src:
                continue

            img_url = urljoin(url, img_src)

            status_code, is_broken, size_kb, width, height, format_type = get_image_info(img_url)

            image_data.append({
                "Page URL": url,
                "Image URL": img_url,
                "Alt Text": alt_text,
                "Format": format_type,
                "Size (KB)": size_kb,
                "Width": width,
                "Height": height,
                "Status Code": status_code,
                "Broken Image": is_broken
            })

    except Exception as e:
        print(f"Error on {url}: {e}")

# Close Browser
driver.quit()

# ---------------------------------------
# SAVE TO EXCEL
# ---------------------------------------
df = pd.DataFrame(image_data)

# Remove duplicates
df = df.drop_duplicates(subset=["Page URL", "Image URL"])

df.to_excel(OUTPUT_FILE, index=False)

print(f"\n✅ Audit completed. File saved as: {OUTPUT_FILE}")