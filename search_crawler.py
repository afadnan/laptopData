import os
import re
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
        amazon_search_url = f"https://www.amazon.in/s?k={quote(query)}&page={page}"
        proxy_url = f"{API_BASE_URL}?token={API_TOKEN}&url={quote(amazon_search_url, safe='')}"

        print(f"Crawling Search Page {page}...")

        try:
            response = requests.get(proxy_url, timeout=30)
        except requests.RequestException as e:
            print(f"Request error on page {page}: {e}")
            continue

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            links = soup.select("[data-asin] a[href*='/dp/']")

            seen_asins = set()
            for link in links:
                href = link.get("href")
                if href:
                    # Extract ASIN to get one clean URL per product
                    match = re.search(r'/dp/([A-Z0-9]{10})', href)
                    if match:
                        asin = match.group(1)
                        if asin not in seen_asins:
                            seen_asins.add(asin)
                            full_url = "https://www.amazon.in/dp/" + asin
                            product_links.append(full_url)

            print(f"  Found {len(seen_asins)} unique products on page {page}")
        else:
            print(f"Failed to fetch search page {page}: {response.status_code}")

    return product_links  # Already deduplicated by ASIN

if __name__ == "__main__":
    links = get_search_results("laptops", pages=1)
    print(f"\nTotal: Found {len(links)} laptop links!")
    for l in links[:5]:
        print(f"  Sample: {l}")