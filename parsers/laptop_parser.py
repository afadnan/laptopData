from bs4 import BeautifulSoup
import re

def parse_laptop_details(html_content):
    soup = BeautifulSoup(html_content, "lxml")
    
    # Initialize dictionary with all your requested fields
    data = {
        "laptop_full_name": "N/A",
        "company": "N/A",
        "typeName": "N/A",
        "Inches": "N/A",
        "Screen_Resolution": "N/A",
        "CAP": "N/A", # Often refers to Storage Capacity
        "GPu": "N/A",
        "Ram": "N/A",
        "Memory": "N/A",
        "operating_system": "N/A",
        "weigt": "N/A",
        "price": "N/A"
    }

    # 1. Extract Full Name & Company
    title_tag = soup.find("span", {"id": "productTitle"})
    if title_tag:
        full_name = title_tag.get_text(strip=True)
        data["laptop_full_name"] = full_name
        # Simple logic: First word of title is usually the Brand
        data["company"] = full_name.split(' ')[0]

    # 2. Extract Price
    price_span = soup.select_one(".a-price .a-offscreen")
    if price_span:
        data["price"] = price_span.get_text(strip=True)

    # 3. Map Amazon Table Labels to your Specific Column Names
    # Amazon uses different names for the same thing. This map fixes that.
    label_map = {
        "Standing screen display size": "Inches",
        "Max Screen Resolution": "Screen_Resolution",
        "Processor": "CAP",           # Often contains CPU info
        "Graphics Coprocessor": "GPu",
        "Video Card": "GPu",
        "RAM": "Ram",
        "Hard Drive": "Memory",
        "Operating System": "operating_system",
        "Item Weight": "weigt",
        "Series": "typeName"
    }

    # Search in the "Technical Details" table
    spec_table = soup.find("table", {"id": "productDetails_techSpec_section_1"})
    if spec_table:
        for row in spec_table.find_all("tr"):
            th = row.find("th")
            td = row.find("td")
            if th and td:
                amazon_label = th.get_text(strip=True)
                value = td.get_text(strip=True)
                
                # If the label is in our map, save it to your specific key
                if amazon_label in label_map:
                    target_key = label_map[amazon_label]
                    data[target_key] = value

    # 4. Fallback: Search in "About this item" bullets if table is missing
    if data["Ram"] == "N/A":
        bullets = soup.select("#feature-bullets ul li span")
        for bullet in bullets:
            text = bullet.get_text()
            if "RAM" in text.upper():
                data["Ram"] = text.strip()
            if "SSD" in text.upper() or "HDD" in text.upper():
                data["Memory"] = text.strip()

    return data