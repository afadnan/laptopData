import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()
API_TOKEN = os.getenv("SCRAPING_API_TOKEN")
API_BASE_URL = os.getenv("SCRAPE_DO_URL")

if not API_TOKEN or not API_BASE_URL:
    raise ValueError("Missing SCRAPING_API_TOKEN or SCRAPE_DO_URL in .env file")

def get_search_results(query, pages=1):
    product_links = []

    for page in range(1, pages + 1):
        amazon_search_url = f"https://www.amazon.com/s?k={quote(query)}&page={page}"
        proxy_url = f"{API_BASE_URL}?token={API_TOKEN}&url={quote(amazon_search_url, safe='')}"

        print(f"Crawling Search Page {page}...")

        try:
            response = requests.get(proxy_url, timeout=30)
        except requests.RequestException as e:
            print(f"Request error on page {page}: {e}")
            continue

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            # Target links by href pattern — resilient to class name changes
            links = soup.select("h2 a[href*='/dp/']")

            for link in links:
                href = link.get("href")
                if href:
                    full_url = "https://www.amazon.com" + href.split("?")[0]
                    product_links.append(full_url)
        else:
            print(f"Failed to fetch search page {page}: {response.status_code}")

    return list(set(product_links))

if __name__ == "__main__":
    links = get_search_results("laptops", pages=1)
    print(f"Found {len(links)} laptop links!")
    for l in links[:5]:
        print(f"Sample: {l}")