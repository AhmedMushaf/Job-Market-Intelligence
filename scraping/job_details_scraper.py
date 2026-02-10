from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd
import time
import os
import re

from utils import human_delay
from config import DELAY_RANGE


# ---------------- FIELD EXTRACTORS (IMPROVED) ---------------- #

def extract_company(driver):
    """Extract company name using multiple selector strategies."""
    selectors = [
        (By.CSS_SELECTOR, 'a.comp-name, div.comp-name, span.comp-name'),
        (By.XPATH, "//a[contains(@href,'/company/') or contains(@href,'/cmp/')][1]"),
        (By.XPATH, "//*[contains(@class,'companyName') or contains(@class,'comp-name')][1]"),
        (By.XPATH, "//*[contains(text(),'Company:')]/following-sibling::*[1]")
    ]
    for by, sel in selectors:
        try:
            text = driver.find_element(by, sel).text.strip()
            if text and len(text) < 100:
                # Remove review ratings and extra text
                company = text.split('\n')[0].strip()
                company = re.sub(r'\d+\.\d+\s*\d+\s*Reviews|Reviews|Employees.*choice', '', company).strip()
                if company and len(company) > 1:
                    return company
        except Exception:
            continue
    return None

def extract_location(driver):
    """Extract location using multiple selector strategies."""
    selectors = [
        (By.CSS_SELECTOR, 'span.loc, div.loc, span.location, div.location'),
        (By.XPATH, "//*[contains(@class,'loc') or contains(@class,'location')][1]"),
        (By.XPATH, "//*[contains(text(),'Location:')]/following-sibling::*[1]")
    ]
    for by, sel in selectors:
        try:
            text = driver.find_element(by, sel).text.strip()
            if text and len(text) < 100:
                return text
        except Exception:
            continue
    return None

def extract_experience(driver):
    """Extract experience using multiple selector strategies."""
    selectors = [
        (By.XPATH, "//*[contains(text(),'Experience')]/following-sibling::*[1]"),
        (By.XPATH, "//*[contains(@class,'exp') or contains(@class,'experience')][1]")
    ]
    for by, sel in selectors:
        try:
            text = driver.find_element(by, sel).text.strip()
            if text and len(text) < 50:
                return text
        except Exception:
            continue
    # Try to find patterns in the body text as fallback
    try:
        body = driver.find_element(By.TAG_NAME, "body").text
        exp = re.search(r'(\d+\s*-\s*\d+\s*years|\d+\+\s*years)', body, re.I)
        if exp:
            return exp.group()
    except Exception:
        pass
    return None

def extract_salary(driver):
    """Extract salary using multiple selector strategies."""
    # 1) Look for explicit Salary label nodes and inspect their nearby siblings
    try:
        # nodes that explicitly mention 'salary'
        label_nodes = driver.find_elements(
            By.XPATH,
            "//*[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'salary')]"
        )
        for node in label_nodes:
            try:
                # Check node text and nearby siblings (next 4 following nodes)
                text = node.text or ''
                candidates = [text]
                following = node.find_elements(By.XPATH, 'following::*')[:6]
                for f in following:
                    try:
                        ft = f.text
                        if ft:
                            candidates.append(ft)
                    except Exception:
                        continue

                # Inspect candidates for salary-like patterns first
                for c in candidates:
                    if not c:
                        continue
                    # split lines and examine each
                    for part in [p.strip() for p in str(c).splitlines() if p.strip()]:
                        low = part.lower()
                        # prefer explicit salary formats
                        if any(k in low for k in ('lacs', 'lakhs', 'lpa', '₹')):
                            # ensure part is not just experience
                            if 'year' in low or 'yrs' in low:
                                continue
                            return part
                        # capture numeric range with Lacs following
                        m = re.search(r'\d+\s*[-–]\s*\d+\s*(?:lacs|lakhs|lpa)', low, re.I)
                        if m:
                            return m.group().strip()

            except Exception:
                continue
    except Exception:
        pass

    # 2) Try common selectors used on job sites
    selectors = [
        (By.XPATH, "//*[contains(@class,'salary') or contains(@class,'ctc') or contains(@class,'pay')]")
    ]
    for by, sel in selectors:
        try:
            elements = driver.find_elements(by, sel)
            for el in elements:
                try:
                    text = el.text or ''
                    for part in [p.strip() for p in text.splitlines() if p.strip()]:
                        low = part.lower()
                        if any(k in low for k in ('lacs', 'lakhs', 'lpa', '₹')) and 'year' not in low:
                            return part
                except Exception:
                    continue
        except Exception:
            continue

    # 3) Fallback: regex search in body for salary-like patterns, prefer Lacs/LPA over ranges of years
    try:
        body = driver.find_element(By.TAG_NAME, "body").text
        # find all salary-like patterns
        matches = re.findall(r'(?:₹\s*[\d.,\-]+\s*(?:Lacs|Lakhs|LPA|P\.A\.)?|\d+\s*[-–]\s*\d+\s*(?:Lacs|Lakhs|LPA))', body, re.I)
        for s in matches:
            if 'year' in s.lower():
                continue
            return s.strip()
    except Exception:
        pass

    # If nothing found, return None (leave blank)
    return None


# ---------------- DRIVER ---------------- #

def get_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    prefs = {"profile.default_content_setting_values.geolocation": 2}
    options.add_experimental_option("prefs", prefs)

    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )


# ---------------- SAFE TEXT ---------------- #

def safe_text(driver, by, selector):
    try:
        return driver.find_element(by, selector).text.strip()
    except Exception:
        return None


# ---------------- READ MORE (JD ONLY) ---------------- #

def expand_job_description_only(driver):
    try:
        jd_heading = driver.find_element(
            By.XPATH,
            "//h2[normalize-space()='Job description'] | //h3[normalize-space()='Job description']"
        )
    except Exception:
        return

    try:
        read_more = jd_heading.find_element(
            By.XPATH,
            "following::a[normalize-space()='read more'][1]"
        )
    except Exception:
        return

    try:
        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", read_more
        )
        time.sleep(0.4)
        driver.execute_script("arguments[0].click();", read_more)
        time.sleep(0.6)
    except Exception:
        pass


# ---------------- JOB DESCRIPTION ---------------- #

def extract_job_description(driver):
    """
    Extract job description by getting body text, finding 'Key Skills' marker,
    and extracting meaningful content before it while filtering metadata.
    """
    try:
        body_text = driver.find_element(By.TAG_NAME, "body").text
        
        if not body_text:
            return None
        
        # Find where "Key Skills" appears (case-insensitive)
        key_skills_lower = body_text.lower().find('key skills')
        preferred_keyskills_lower = body_text.lower().find('preferred keyskills')
        
        # Use whichever comes first
        cutoff = None
        if key_skills_lower >= 0 and preferred_keyskills_lower >= 0:
            cutoff = min(key_skills_lower, preferred_keyskills_lower)
        elif key_skills_lower >= 0:
            cutoff = key_skills_lower
        elif preferred_keyskills_lower >= 0:
            cutoff = preferred_keyskills_lower
        
        # Extract text before Key Skills
        if cutoff is not None:
            text_before_skills = body_text[:cutoff]
        else:
            text_before_skills = body_text
        
        # Split into lines and filter
        lines = [line.strip() for line in text_before_skills.split('\n') if line.strip()]
        
        # Metadata keywords to skip (these are job posting structure, not description)
        metadata_keywords = {
            'role:', 'industry type:', 'department:', 'employment type:',
            'role category:', 'education', 'ug:', 'pg:', 'doctorate:',
            'skills:', 'experience', 'skills highlighted', 'are preferred',
            'skills required:', 'basic qualifications:', 'preferred qualifications:',
            'beware of imposters', 'about the company', 'salary insights',
            'reviews', 'posted:', 'applicants:', 'company:',
            'read more', 'share', 'home', 'about us', 'careers'
        }
        
        # Filter lines: keep only meaningful content
        description_lines = []
        for line in lines:
            line_lower = line.lower()
            
            # Skip metadata lines
            if any(keyword in line_lower for keyword in metadata_keywords):
                continue
            
            # Skip very short lines (< 20 chars)
            if len(line) < 20:
                continue
            
            # Skip lines that are mostly special characters or punctuation
            if not any(c.isalnum() for c in line):
                continue
            
            # Skip lines that are just numbers, dates, or navigation text
            if line_lower in {'home', 'apply', 'read all', 'connect with us', 
                             'security guidelines', 'terms and conditions',
                             'terms & conditions', 'privacy policy', 'fraud alert',
                             'trust & safety'}:
                continue
            
            description_lines.append(line)
        
        # Join lines and return if long enough
        jd = " ".join(description_lines).strip()
        
        # Clean up multiple spaces
        jd = " ".join(jd.split())
        
        return jd if len(jd) > 150 else None

    except Exception:
        return None


def _is_valid_description_block(text):
    """Helper function to validate if text is meaningful job description content."""
    if not text:
        return False
    
    low = text.lower()
    
    # Skip noise/navigation elements
    if any(x in low for x in [
        "beware of imposters", "about the company", "reviews", "salary insights",
        "read more", "home", "contact us", "privacy policy", "terms and conditions",
        "security guidelines", "fraud alert"
    ]):
        return False
    
    # Skip if only punctuation or special characters
    if not any(c.isalnum() for c in text):
        return False
    
    # Skip single words or very short text
    if len(text.split()) < 3:
        return False
    
    # Skip if too short
    if len(text) < 50:
        return False
    
    # Ensure minimum word count
    if len(text.split()) < 5:
        return False
    
    return True


# ---------------- KEY SKILLS ---------------- #

def extract_key_skills(driver):
    try:
        headings = driver.find_elements(
            By.XPATH,
            "//*[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'key skills')]"
        )

        skills = []
        # Noise words to filter out
        noise_words = {
            'read more', 'home', 'security guidelines', 'terms and conditions',
            'connect with us', 'about us', 'careers', 'employer', 'sitemap',
            'credits', 'help center', 'summons', 'notices', 'grievances',
            'report issue', 'privacy policy', 'fraud alert', 'trust & safety',
            'hyderabad', 'reviews', 'website', 'employee', 'naukri'
        }

        for h in headings:
            anchors = h.find_elements(By.XPATH, "following::a")
            for a in anchors:
                txt = a.text.strip()
                if 1 < len(txt) < 40 and txt.lower() not in noise_words:
                    skills.append(txt)
            if skills:
                break

        # Return unique skills, filtered
        unique_skills = list(dict.fromkeys(skills))[:15]  # Limit to 15 skills
        return ", ".join(unique_skills) if unique_skills else None

    except Exception:
        return None


# ---------------- METADATA (CRITICAL FIX) ---------------- #

def extract_metadata_block(driver):
    try:
        return driver.find_element(By.TAG_NAME, "body").text
    except Exception:
        return ""


def parse_job_metadata(text):
    data = {
        "company": None,
        "location": None,
        "experience": None,
        "salary": None,
        "posted_time": None,
        "applicants": None
    }

    if not text:
        return data

    # Company (usually near top)
    comp = re.search(r'Company\s*:\s*(.+)', text)
    if comp:
        data["company"] = comp.group(1).strip()

    # Experience
    exp = re.search(r'(\d+\s*-\s*\d+\s*years|\d+\+\s*years)', text, re.I)
    if exp:
        data["experience"] = exp.group()

    # Location
    loc = re.search(
        r'\b(Hyderabad|Bengaluru|Bangalore|Chennai|Mumbai|Pune|Delhi|Gurgaon|Noida|Remote|Hybrid)\b',
        text,
        re.I
    )
    if loc:
        data["location"] = loc.group()

    # Salary
    sal = re.search(r'₹\s*[\d.,]+\s*(Lacs|Lakhs|LPA)?|Not Disclosed', text, re.I)
    if sal:
        data["salary"] = sal.group()

    # Posted time
    post = re.search(r'Posted\s*:\s*([^\n|]+)', text, re.I)
    if post:
        data["posted_time"] = post.group(1).strip()

    # Applicants
    app = re.search(r'Applicants\s*:\s*(\d+\+?)', text, re.I)
    if app:
        data["applicants"] = app.group(1)

    return data


# ---------------- MAIN SCRAPER ---------------- #

def scrape_job_details():
    urls_df = pd.read_csv("data/raw/job_urls.csv")
    driver = get_driver()
    records = []

    for idx, row in urls_df.iterrows():
        job_url = row["job_url"]
        print(f"[{idx+1}/{len(urls_df)}] Scraping job detail")

        try:
            driver.get(job_url)

            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            human_delay(DELAY_RANGE)

            expand_job_description_only(driver)

            # Prefer company name from the source CSV (more reliable), fall back to extractor
            try:
                src_company = row.get("company") if hasattr(row, 'get') else row["company"]
            except Exception:
                src_company = None

            company = src_company if pd.notna(src_company) and str(src_company).strip() else extract_company(driver)
            location = extract_location(driver)
            experience = extract_experience(driver)
            salary = extract_salary(driver)

            # Fallback: parse from metadata block if any field is missing
            meta_text = extract_metadata_block(driver)
            meta = parse_job_metadata(meta_text)
            company = company or meta["company"]
            location = location or meta["location"]
            experience = experience or meta["experience"]
            salary = salary or meta["salary"]
            posted_time = meta["posted_time"]
            applicants = meta["applicants"]

            job_data = {
                "job_title": safe_text(driver, By.TAG_NAME, "h1"),
                "company": company,
                "location": location,
                "experience": experience,
                "salary": salary,
                "posted_time": posted_time,
                "applicants": applicants,
                "job_description": extract_job_description(driver),
                "key_skills": extract_key_skills(driver),
                "job_url": job_url
            }

            records.append(job_data)

        except Exception as e:
            print(f"❌ Failed for {job_url}: {e}")
            continue

    driver.quit()
    return pd.DataFrame(records)


# ---------------- RUN ---------------- #

if __name__ == "__main__":
    df = scrape_job_details()
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv("data/processed/job_details.csv", index=False)
    print(f"✅ Saved {len(df)} job detail records")
