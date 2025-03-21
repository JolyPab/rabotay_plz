from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
# options.add_argument("--headless")  # Отключаем headless для отладки

browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(browser, 20)

urls = [
    "https://www.century21global.com/en/l/homes-for-sale/mexico,quintana-roo,cancún:benito-juárez",
    "https://www.century21global.com/en/l/homes-for-rent/mexico,quintana-roo,cancún:benito-juárez",
    "https://www.century21global.com/en/l/commercial-for-sale/mexico,quintana-roo,cancún:benito-juárez",
    "https://www.century21global.com/en/l/commercial-for-rent/mexico,quintana-roo,cancún:benito-juárez",
    "https://www.century21global.com/en/l/land-for-sale/mexico,quintana-roo,cancún:benito-juárez",
    "https://www.century21global.com/en/l/land-for-rent/mexico,quintana-roo,cancún:benito-juárez"
]

listings = set()

def close_cookie_banner():
    try:
        cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'ХОРОШО')]")))
        cookie_button.click()
        print("✅ Куки-баннер закрыт")
    except:
        print("ℹ️ Куки-баннер не найден")

def scrape_listings():
    for url in urls:
        page = 1
        while True:
            full_url = f"{url}?max=40&page={page}"
            print(f"🔄 Загружаем страницу {page}: {full_url}")
            browser.get(full_url)
            time.sleep(6)
            close_cookie_banner()
            time.sleep(4)

            with open("debug_latest_page.html", "w", encoding="utf-8") as f:
                f.write(browser.page_source)

            items = browser.find_elements(By.XPATH, "//a[contains(@href, '/en/p/')]")
            if not items:
                print(f"⛔ Объявления закончились на {full_url}")
                break

            for item in items:
                href = item.get_attribute("href")
                if href and "/en/p/" in href:
                    listings.add(href)

            print(f"✅ Найдено {len(items)} объявлений на стр. {page}")
            page += 1

scrape_listings()

print(f"✅ Найдено {len(listings)} уникальных ссылок")

with open("cancun_listings_scraped.json", "w", encoding="utf-8") as f:
    json.dump(list(listings), f, ensure_ascii=False, indent=2)

print(f"✅ Сохранено {len(listings)} уникальных ссылок в cancun_listings_scraped.json")

browser.quit()
