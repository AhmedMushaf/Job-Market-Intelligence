from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd
import os
import time

from config import ROLE, CITIES, MAX_PAGES, DELAY_RANGE
from utils import human_delay


def get_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    )
    # Disable location permission prompts
    prefs = {"profile.default_content_setting_values.geolocation": 2}
    options.add_experimental_option("prefs", prefs)

    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )


def build_search_url(role, city, page):
    role = role.replace(" ", "-")
    
    # Naukri uses composite city slugs
    city_slug_map = {
        "hyderabad": "hyderabad-secunderabad",
        "bengaluru": "bengaluru-bangalore",
        "mumbai": "mumbai"
    }

    city_slug = city_slug_map.get(city.lower(), city.lower())

    base = f"https://www.naukri.com/{role}-jobs-in-{city_slug}"

    if page == 1:
        return base

    return f"{base}-{page}?page={page}"




def scrape_search_results():
    driver = get_driver()
    results = []

    for city in CITIES:
        for page in range(1, MAX_PAGES + 1):
            url = build_search_url(ROLE, city, page)
            print(f"Scraping: {url}")
            driver.get(url)
            human_delay(DELAY_RANGE)

            # Close ad / extra tabs
            main_handle = driver.current_window_handle
            for handle in driver.window_handles:
                if handle != main_handle:
                    try:
                        driver.switch_to.window(handle)
                        driver.close()
                    except Exception:
                        pass
            driver.switch_to.window(main_handle)

            # Accept cookies if present
            try:
                WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept') "
                        "or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'got it')]"
                    ))
                ).click()
            except Exception:
                pass

            # Wait for job cards
            selectors = "div.cust-job-tuple, div.srp-job-promotion"
            try:
                job_cards = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, selectors))
                )
            except Exception:
                job_cards = driver.find_elements(By.CSS_SELECTOR, selectors)

            if not job_cards:
                print("No job cards found, stopping pagination.")
                break

            for card in job_cards:
                try:
                    # Job Title
                    try:
                        title = card.find_element(By.CSS_SELECTOR, "a.title").text
                    except Exception:
                        title = ""

                    # Company
                    try:
                        company = card.find_element(By.CSS_SELECTOR, "a.comp-name").text
                    except Exception:
                        company = ""

                    # Location
                    try:
                        location = card.find_element(By.CSS_SELECTOR, "span.locWdth").text
                    except Exception:
                        location = ""

                    # Experience
                    try:
                        experience = card.find_element(By.CSS_SELECTOR, "span.expwdth").text
                    except Exception:
                        experience = ""

                    # Posted time
                    try:
                        posted = card.find_element(By.CSS_SELECTOR, "span.job-post-day").text
                    except Exception:
                        posted = ""

                    # Job URL (ROBUST EXTRACTION)
                    job_url = ""
                    for selector in ["a.title", "a[href*='job-listings']"]:
                        try:
                            job_url = card.find_element(By.CSS_SELECTOR, selector).get_attribute("href")
                            if job_url:
                                break
                        except Exception:
                            continue

                    # Only append if job_url exists
                    if job_url:
                        results.append({
                            "job_title": title,
                            "company": company,
                            "location": location,
                            "experience": experience,
                            "posted_time": posted,
                            "job_url": job_url,
                            "city": city,
                            "page_no": page
                        })

                except Exception:
                    continue

    driver.quit()

    # ---------------- POST-PROCESSING (CRITICAL) ----------------
    df = pd.DataFrame(results)

    # Normalize empty strings
    df.replace("", pd.NA, inplace=True)

    # Deduplicate job URLs
    df.drop_duplicates(subset=["job_url"], inplace=True)

    return df


if __name__ == "__main__":
    df = scrape_search_results()

    # Ensure output directory exists
    os.makedirs("data/raw", exist_ok=True)

    df.to_csv("data/raw/job_urls.csv", index=False)
    print(f"Saved {len(df)} clean job URLs")
    print("Step 3 scraping completed successfully.")
