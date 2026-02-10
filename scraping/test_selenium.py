# Selenium driver initialization includes retry logic to handle
# transient network or driver setup failures during automation setup.
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

options = Options()
options.add_argument("--start-maximized")

max_retries = 5
for attempt in range(max_retries):
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        break
    except Exception as e:
        if attempt < max_retries - 1:
            print(f"Attempt {attempt + 1} failed, retrying in 5 seconds...")
            time.sleep(5)
        else:
            raise

driver.get("https://www.google.com")
print("Selenium setup successful!")

driver.quit()