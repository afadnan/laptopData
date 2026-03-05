import os
import time
import random
import pandas as pd
from datetime import datetime
from curl_cffi import requests as curl_requests
from dotenv import load_dotenv
from urllib.parse import quote
from utils.headers import get_headers
from parsers.laptop_parser import parse_laptop_details, is_laptop  # ✅ import is_laptop

load_dotenv()
API_TOKEN = os.getenv("SCRAPING_API_TOKEN")
API_BASE_URL = os.getenv("SCRAPE_DO_URL")

def main():
    urls = get_search_results("laptops", pages=1)

    if not urls:
        print("No URLs found. Exiting.")
        return

    processed_dir = "data/processed"
    os.makedirs(processed_dir, exist_ok=True)

    all_laptops = []
    skipped = 0
    print(f"Starting scrape of {len(urls)} products...")

    for url in urls:
        try:
            proxy_url = f"{API_BASE_URL}?token={API_TOKEN}&url={quote(url, safe='')}"
            response = curl_requests.get(
                proxy_url,
                headers=get_headers(),
                impersonate="chrome120",
                timeout=30
            )

            if response.status_code == 200:
                laptop_data = parse_laptop_details(response.content)
                laptop_data['URL'] = url

                # ✅ Filter out non-laptop products
                if not is_laptop(laptop_data['laptop_full_name']):
                    print(f"Skipped (not a laptop): {laptop_data['laptop_full_name'][:40]}...")
                    skipped += 1
                else:
                    all_laptops.append(laptop_data)
                    print(f"Successfully parsed: {laptop_data['laptop_full_name'][:40]}...")

            elif response.status_code == 404:
                print(f"Product not found (404): {url}")
            else:
                print(f"Blocked or Error: Status {response.status_code} for {url}")

        except Exception as e:
            print(f"Request failed for {url}: {e}")

        sleep_time = random.uniform(5, 10)
        print(f"Sleeping for {sleep_time:.1f}s...")
        time.sleep(sleep_time)

    if all_laptops:
        df = pd.DataFrame(all_laptops)
        timestamp = datetime.now().strftime("%Y_%m_%d")
        filename = f"{processed_dir}/laptops_{timestamp}.csv"
        df.to_csv(filename, index=False)
        print(f"\nDone! {len(all_laptops)} laptops saved, {skipped} non-laptops skipped.")
        print(f"File: {filename}")
    else:
        print("No data collected.")

if __name__ == "__main__":
    from search_crawler import get_search_results
    main()