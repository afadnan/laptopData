import os
import time
import random
import pandas as pd
from datetime import datetime
from curl_cffi import requests  # Best for 2026 anti-bot bypass
from utils.headers import get_headers
from parsers.laptop_parser import parse_laptop_details

def main():
    # Setup paths
    processed_dir = "data/processed"
    os.makedirs(processed_dir, exist_ok=True)

    # Example: List of Amazon ASINs (Product IDs)
    # You can also build a 'search_crawler' to get these automatically
    urls = [
        "https://www.amazon.com/dp/B0CX25V7S1",
        "https://www.amazon.com/dp/B0CSB22F9C"
    ]

    all_laptops = []

    print(f"Starting scrape of {len(urls)} laptops...")

    for url in urls:
        print(f"Fetching: {url}")
        
        try:
            # impersonate="chrome120" makes curl_cffi mimic a real browser's handshake
            response = requests.get(
                url, 
                headers=get_headers(), 
                impersonate="chrome120",
                timeout=30
            )

            if response.status_code == 200:
                laptop_data = parse_laptop_details(response.content)
                laptop_data['URL'] = url
                all_laptops.append(laptop_data)
                print(f"Successfully parsed: {laptop_data['Title'][:30]}...")
            elif response.status_code == 404:
                print("Product not found (404).")
            else:
                print(f"Blocked or Error: Status {response.status_code}")

        except Exception as e:
            print(f"Request failed: {e}")

        # Vital: Random sleep to avoid detection
        sleep_time = random.uniform(5, 10)
        time.sleep(sleep_time)

    # Save to CSV
    if all_laptops:
        df = pd.DataFrame(all_laptops)
        timestamp = datetime.now().strftime("%Y_%m_%d")
        filename = f"{processed_dir}/laptops_{timestamp}.csv"
        df.to_csv(filename, index=False)
        print(f"\nDone! Data saved to {filename}")
    else:
        print("No data collected.")

if __name__ == "__main__":
    main()