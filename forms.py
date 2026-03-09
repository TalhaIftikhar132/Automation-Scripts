# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time

# # Start browser
# driver = webdriver.Chrome()

# # Open website
# driver.get("https://oneworldrental.com/contact-us")

# driver.maximize_window()

# wait = WebDriverWait(driver, 10)

# # Fill Name
# name = wait.until(EC.presence_of_element_located((By.ID, "name_home")))
# name.send_keys("Talha Iftikhar")

# # Fill Email
# email = driver.find_element(By.ID, "email_home")
# email.send_keys("muhammad.talha@owrdigital.com")

# # Fill Phone
# phone = driver.find_element(By.ID, "phone_home")
# phone.send_keys("030012345678")

# # Fill Company
# company = driver.find_element(By.ID, "company_home")
# company.send_keys("OWR ")

# # Fill Location
# location = driver.find_element(By.ID, "location_home")
# location.send_keys("Pakistan")

# # Select Checkbox (example: iPad and Tablets)
# checkbox = driver.find_element(By.ID, "ipad-tablet")
# driver.execute_script("arguments[0].click();", checkbox)

# # Fill Other State
# other = driver.find_element(By.ID, "otherstate2_home")
# other.send_keys("Testing devices")

# # Fill Tell Us More
# message = driver.find_element(By.ID, "tellusmore_home")
# message.send_keys("This is automated testing.")

# print("Please solve the CAPTCHA manually...")

# time.sleep(20)  # Time to solve captcha manually

# # Submit Form
# submit = driver.find_element(By.ID, "submitBtn_home")
# submit.click()

# time.sleep(5)

# print("Form submitted")

# driver.quit()


#  wordpress forms Test Script 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()

driver.get("https://ipadrental.us/contact-us/")

driver.maximize_window()

wait = WebDriverWait(driver, 15)

# Fill Name
driver.find_element(By.ID,"form-field-Name").send_keys("Talha Iftikhar")

# Fill Email
driver.find_element(By.ID,"form-field-Email").send_keys("muhammad.talha@owrdigital.com")

# Fill Phone
driver.find_element(By.ID,"form-field-Phone").send_keys("030012345678")

# Fill Company
driver.find_element(By.ID,"form-field-Company").send_keys("OWR Test")

# Fill Location
driver.find_element(By.ID,"form-field-Address").send_keys("Pakistan")

# Fill Message
driver.find_element(By.ID,"form-field-Message").send_keys("Testing WordPress Elementor form.")

# Wait for reCAPTCHA token generation
time.sleep(5)

captcha_token = driver.execute_script(
    "return document.getElementById('g-recaptcha-response').value;"
)

if captcha_token:
    print("reCAPTCHA token generated successfully")
else:
    print("reCAPTCHA token NOT generated")

# Submit form
driver.find_element(By.XPATH,"//button[@type='submit']").click()

# Verify success message
try:
    success = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME,"elementor-message-success"))
    )
    print("Form submitted successfully:", success.text)
except:
    print("Submission response not detected")

driver.quit()