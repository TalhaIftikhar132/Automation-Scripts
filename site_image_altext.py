from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pandas as pd
from urllib.parse import urljoin, urlparse
import time

start_url = "https://Example "   # replace with your website    

visited = set()
to_visit = [start_url]

data = []

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

domain = urlparse(start_url).netloc

while to_visit:

    url = to_visit.pop(0)

    if url in visited:
        continue

    try:
        driver.get(url)
        time.sleep(2)

        visited.add(url)

        # Collect images
        images = driver.find_elements(By.TAG_NAME, "img")

        for img in images:
            img_src = img.get_attribute("src")
            alt_text = img.get_attribute("alt")

            if not img_src:
                continue

            status = "Missing ALT" if not alt_text else "ALT Present"

            data.append({
                "Page URL": url,
                "Image URL": img_src,
                "ALT Text": alt_text if alt_text else "",
                "Status": status
            })

        # Collect internal links
        links = driver.find_elements(By.TAG_NAME, "a")

        for link in links:
            href = link.get_attribute("href")

            if href and domain in href and href not in visited:
                to_visit.append(href)

    except Exception as e:
        print(f"Error processing {url}: {e}")

driver.quit()

# Save to Excel
df = pd.DataFrame(data)
df.to_excel("image_alt_audit.xlsx", index=False)

print("Audit Completed. File saved as image_alt_audit.xlsx")