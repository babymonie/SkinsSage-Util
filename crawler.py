import requests
from bs4 import BeautifulSoup
import hashlib
import json
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor


import time

URL = "https://www.counter-strike.net/news"
DATA_FILE = "data/cs2/updates_raw.json"

def fetch_blog_details_with_selenium(driver, link):
    """Fetch blog details using Selenium."""
    try:
        driver.get(link)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".blogentrypage_Title_2HW6u")))

        title = driver.find_element(By.CSS_SELECTOR, ".blogentrypage_Title_2HW6u").text.strip()
        date = driver.find_element(By.CSS_SELECTOR, ".blogentrypage_Date_2JNhX").text.strip()
        body = driver.find_element(By.CSS_SELECTOR, ".blogentrypage_Body_30GVv").text.strip()

        uid = hashlib.md5((date + title).encode("utf-8")).hexdigest()
        return {
            "id": uid,
            "timestamp": date,
            "link": link,
            "entry": f"{title}\n\n{body}"
        }
    except Exception as e:
        print(f"Failed to fetch details for {link}: {e}")
        return None

def fetch_updates():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # 1) Scrape list pages for link + image_url
    driver_list = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)
    entries_info = []
    try:
        driver_list.get(URL)
        WebDriverWait(driver_list, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.blogcapsule_BlogCapsule_3OBoG")))

        while True:
            caps = driver_list.find_elements(By.CSS_SELECTOR, "a.blogcapsule_BlogCapsule_3OBoG")
            for cap in caps:
                href = cap.get_attribute("href")
                if not href or not href.startswith("https://www.counter-strike.net"):
                    continue
                # extract image URL
                try:
                    style = cap.find_element(By.CSS_SELECTOR, ".blogcapsule_Image_Nh_xZ").get_attribute("style")
                    img = style.split('url("')[1].split('")')[0]
                except:
                    img = None
                entries_info.append({"link": href, "image_url": img})

            # next page?
            nav = driver_list.find_elements(By.CSS_SELECTOR, ".blogoverviewpage_PageNumber_FafYQ")
            if not nav or "Hidden" in nav[-1].get_attribute("class"):
                break
            nav[-1].click()
            WebDriverWait(driver_list, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.blogcapsule_BlogCapsule_3OBoG")))
    finally:
        driver_list.quit()

    # 2) Fetch details for each entry with a second driver
    driver_detail = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)
    updates = []
    try:
        for info in entries_info:
            details = fetch_blog_details_with_selenium(driver_detail, info["link"])
            if details:
                details["image_url"] = info["image_url"]
                updates.append(details)
    finally:
        driver_detail.quit()

    return updates

def load_existing_updates():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_updates(updates):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(updates, f, indent=2, ensure_ascii=False)

def main():
    new_updates = fetch_updates()
    existing_updates = load_existing_updates()


    existing_ids = {entry["id"] for entry in existing_updates}
    fresh_updates = [entry for entry in new_updates if entry["id"] not in existing_ids]

    if fresh_updates:

        all_updates = fresh_updates + existing_updates
        save_updates(all_updates)
    else:
        print("No new updates found.")

if __name__ == "__main__":
    main()
    print("Update check completed.")