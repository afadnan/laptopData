import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()
API_TOKEN = os.getenv("SCRAPING_API_TOKEN")
API_BASE_URL = os.getenv("SCRAPE_DO_URL")

amazon_url = "https://www.amazon.com/s?k=laptops&page=1"
proxy_url = f"{API_BASE_URL}?token={API_TOKEN}&url={quote(amazon_url, safe='')}"

print("Fetching Amazon page...")
response = requests.get(proxy_url, timeout=30)
soup = BeautifulSoup(response.text, "lxml")

# Save HTML so you can open it in browser
with open("debug_page.html", "w", encoding="utf-8") as f:
    f.write(response.text)
print("Saved debug_page.html — open this in your browser to inspect\n")

# Test every possible selector
selectors = [
    "h2 a[href*='/dp/']",
    "a[href*='/dp/']",
    ".s-result-item a[href*='/dp/']",
    "[data-asin] a[href*='/dp/']",
    ".s-search-results a[href*='/dp/']",
    "h2.a-size-mini a",
    ".a-link-normal[href*='/dp/']",
    "div[data-asin] h2 a",
]

print("Selector results:")
print("-" * 55)
for sel in selectors:
    results = soup.select(sel)
    print(f"{len(results):3d} results  →  {sel}")