import requests
from bs4 import BeautifulSoup
import json
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

def parse_listing(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except:
        print(f"❌ Ошибка загрузки {url}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    name =  soup.select_one("div.fragment.ng-star-inserted")
    listing_id = soup.select_one("p.text-primary.fw-semibold.ng-star-inserted span.ng-star-inserted + span")
    price = soup.select_one("p.mat-display-2.fw-bold.mb-2.d-flex.ng-star-inserted")
    address = soup.select_one("div.col-lg-6.ng-star-inserted div.mb-3")
    description = soup.select_one("div.container-fluid.description-container")
    features = soup.select("div.row.g-4.g-lg-5")
    images = [img["src"] for img in soup.select("div.gallery-container img")]

    return {
        "url": url,
        "name": name.text.strip() if name else "нет данных",
        "id": listing_id.text.strip() if listing_id else "нет данных",
        "price": price.text.strip() if price else "нет данных",
        "address": address.text.strip() if address else "нет данных",
        "description": description.text.strip() if description else "нет данных",
        "features": [f.get_text(strip=True) for f in features] if features else [],
        "images": images
    }

def main():
    with open("cancun_listings_scraped.json", "r", encoding="utf-8") as f:
        links = json.load(f)


    listings = []

    # Максимальное число потоков (можно поменять)
    max_workers = 10

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(parse_listing, url): url for url in links}

        for idx, future in enumerate(as_completed(future_to_url), 1):
            url = future_to_url[future]
            try:
                data = future.result()
                if data:
                    listings.append(data)
            except Exception as e:
                print(f"❌ Ошибка обработки {url}: {e}")

            if idx % 10 == 0:
                print(f"✅ Уже спарсено: {idx}/{len(links)} объектов.")

    with open("cancun_listings.json", "w", encoding="utf-8") as f:
        json.dump(listings, f, ensure_ascii=False, indent=2)

    print(f"🎯 Готово! Спарсено всего: {len(listings)} объявлений.")

if __name__ == "__main__":
    main()
