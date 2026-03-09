from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Correct path to ChromeDriver
CHROME_DRIVER_PATH = "C:/Correct/Path/to/chromedriver.exe"
service = Service(CHROME_DRIVER_PATH)

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=service, options=options)


options = Options()
options.add_argument("--start-maximized")  # Open browser visibly
driver = webdriver.Chrome(service=service, options=options)
driver.get("https://Example")

# Scroll to load all exhibitors
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Extract exhibitor data
exhibitor_elements = driver.find_elements(By.CLASS_NAME, "efp-entity-item")

exhibitor_data = []
for exhibitor in exhibitor_elements:
    try:
        name = exhibitor.find_element(By.CLASS_NAME, "efp-entity-item__header").text
        booth = exhibitor.find_element(By.CSS_SELECTOR, ".efp-entity-item__details li").text
        exhibitor_data.append([name, booth])
    except Exception as e:
        print("Error extracting data from an exhibitor:", e)

# Save to CSV
with open("exhibitors.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["Company Name", "Booth Number"])
    writer.writerows(exhibitor_data)

driver.quit()
print("Scraping complete. Data saved to exhibitors.csv")
