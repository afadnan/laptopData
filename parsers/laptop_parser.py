from bs4 import BeautifulSoup
import re

def parse_laptop_details(html_content):
    # Safe decode if bytes are passed
    if isinstance(html_content, bytes):
        html_content = html_content.decode("utf-8", errors="replace")

    soup = BeautifulSoup(html_content, "lxml")

    data = {
        "company": "N/A",
        "laptop_full_name": "N/A",
        "typeName": "N/A",
        "inches": "N/A",
        "screen_resolution": "N/A",
        "storage_capacity": "N/A",
        "cpu": "N/A",
        "gpu": "N/A",
        "ram": "N/A",
        "memory": "N/A",
        "operating_system": "N/A",
        "weight": "N/A",
        "price": "N/A"
    }

    # 1. Full Name & Company
    title_tag = soup.find("span", {"id": "productTitle"})
    if title_tag:
        full_name = title_tag.get_text(strip=True)
        data["laptop_full_name"] = full_name
        data["company"] = full_name.split()[0]

    # 2. Price
    price_span = soup.select_one(".a-price .a-offscreen")
    if price_span:
        data["price"] = price_span.get_text(strip=True)

    # 3. Label map — Amazon label → your field name
    label_map = {
        "Standing screen display size": "inches",
        "Max Screen Resolution":        "screen_resolution",
        "Processor":                    "cpu",
        "Graphics Coprocessor":         "gpu",
        "Video Card":                   "gpu",
        "RAM":                          "ram",
        "Hard Drive":                   "memory",
        "Flash Memory Size":            "storage_capacity",
        "Operating System":             "operating_system",
        "Item Weight":                  "weight",
        "Series":                       "typeName"
    }

    # 4. Parse both spec tables (Amazon splits them)
    table_ids = [
        "productDetails_techSpec_section_1",
        "productDetails_techSpec_section_2"
    ]
    for table_id in table_ids:
        spec_table = soup.find("table", {"id": table_id})
        if spec_table:
            for row in spec_table.find_all("tr"):
                th = row.find("th")
                td = row.find("td")
                if th and td:
                    amazon_label = th.get_text(strip=True)
                    value = td.get_text(strip=True)
                    if amazon_label in label_map:
                        data[label_map[amazon_label]] = value

    # 5. Fallback: bullet points with targeted regex extraction
    if data["ram"] == "N/A" or data["memory"] == "N/A":
        bullets = soup.select("#feature-bullets ul li span")
        for bullet in bullets:
            text = bullet.get_text()

            if data["ram"] == "N/A":
                ram_match = re.search(r'(\d+\s*GB)\s*RAM', text, re.IGNORECASE)
                if ram_match:
                    data["ram"] = ram_match.group(1)

            if data["memory"] == "N/A":
                ssd_match = re.search(r'(\d+\s*(?:GB|TB))\s*(?:SSD|HDD|Hard Drive)', text, re.IGNORECASE)
                if ssd_match:
                    data["memory"] = ssd_match.group(1)

    return data