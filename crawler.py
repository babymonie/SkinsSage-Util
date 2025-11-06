import os
import json
import hashlib
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

URL = "https://www.counter-strike.net/news"
DATA_FILE = "data/cs2/updates_raw.json"

def fetch_blog_details_with_selenium(link):
    """Fetch blog post title, date, and body from detail page."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get(link)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "._2HW6u-IlsL50KUqJyif8Ls"))
        )

        title = driver.find_element(By.CSS_SELECTOR, "._2HW6u-IlsL50KUqJyif8Ls").text.strip()
        date = driver.find_element(By.CSS_SELECTOR, "._2JNhX05chbmg2pDcad3NuT").text.strip()
        body = driver.find_element(By.CSS_SELECTOR, "._30GVvAUcc-I1luXxmzjBYK").text.strip()

        uid = hashlib.md5((date + title).encode("utf-8")).hexdigest()
        return {
            "id": uid,
            "timestamp": date,
            "link": link,
            "entry": f"{title}\n\n{body}"
        }
    except Exception as e:
        print(f"[!] Failed: {link} | {e}")
        return None
    finally:
        driver.quit()

def fetch_updates():
    """Scrape all article links + preview images from CS2 news."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    updates = []

    try:
        driver.get(URL)
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a._3OBoG7TZb8gxM8NbILzAan"))
        )

        articles = driver.find_elements(By.CSS_SELECTOR, "a._3OBoG7TZb8gxM8NbILzAan")
        entries_info = []

        for art in articles:
            href = art.get_attribute("href")
            if not href.startswith("https://www.counter-strike.net"):
                href = "https://www.counter-strike.net" + href

            try:
                style = art.find_element(By.CSS_SELECTOR, ".Nh_xZMN_Sujrqhv-aCKHt").get_attribute("style")
                img = style.split('url("')[1].split('")')[0]
            except:
                img = None

            entries_info.append({"link": href, "image_url": img})

        # Fetch each article content concurrently
        with ThreadPoolExecutor(max_workers=3) as ex:
            for result in ex.map(lambda x: fetch_blog_details_with_selenium(x["link"]), entries_info):
                if result:
                    match = next((e for e in entries_info if e["link"] == result["link"]), None)
                    if match:
                        result["image_url"] = match["image_url"]
                    updates.append(result)
    finally:
        driver.quit()

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
    print("[*] Fetching new updates...")
    new_updates = fetch_updates()
    existing_updates = load_existing_updates()

    existing_ids = {e["id"] for e in existing_updates}
    fresh = [u for u in new_updates if u["id"] not in existing_ids]

    if fresh:
        print(f"[+] {len(fresh)} new updates found.")
        all_updates = fresh + existing_updates
        save_updates(all_updates)
    else:
        print("[-] No new updates found.")

if __name__ == "__main__":
    main()
    print("✅ Update check completed.")
