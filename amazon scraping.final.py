import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/116.0.0.0 Safari/537.36",
    "Accept-Language": "en-IN, en;q=0.9"
}

# ----------- Extract SPECIFIC DETAILS from text -----------
def extract_brand(title):
    return title.split()[0] if title else ""

def extract_ram(text):
    match = re.search(r"(\d+GB|\d+\s?GB)", text, re.IGNORECASE)
    return match.group(1) if match else ""

def extract_storage(text):
    match = re.search(r"(\d+TB|\d+GB SSD|\d+GB HDD|\d+GB|\d+TB SSD)", text, re.IGNORECASE)
    return match.group(1) if match else ""

def extract_processor(text):
    match = re.search(r"(Intel\s?[iI]\d|Ryzen\s?\d|\bAMD\b|Core\s?i\d)", text, re.IGNORECASE)
    return match.group(1) if match else ""

def extract_generation(text):
    match = re.search(r"(\d{1,2}th\s?Gen|\d{1,2}th\s?generation)", text, re.IGNORECASE)
    return match.group(1) if match else ""

def extract_gpu(text):
    match = re.search(r"(RTX\s?\d+|GTX\s?\d+|RTX|GTX|Integrated|Graphics)", text, re.IGNORECASE)
    return match.group(1) if match else ""

# ----------------------------------------------------------

def parse_search_page(url):
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        print("Request failed:", r.status_code, " — ", url)
        return []

    soup = BeautifulSoup(r.content, "lxml")
    items = soup.find_all("div", {"data-component-type": "s-search-result"})
    results = []

    for item in items:

        # Title
        title = item.h2.text.strip() if item.h2 else ""

        # Price
        price_whole = item.find("span", class_="a-price-whole")
        price_frac = item.find("span", class_="a-price-fraction")
        price = ""
        if price_whole:
            price = price_whole.text.strip()
            if price_frac:
                price += price_frac.text.strip()

        # Rating
        rating_span = item.find("span", class_="a-icon-alt")
        rating = rating_span.text.strip() if rating_span else ""

        # Specs block
        spec_div = item.find("div", class_="a-row a-size-base a-color-secondary")
        specs = spec_div.text.strip().replace("\n", " | ") if spec_div else ""

        # ========== NEW EXTRACTIONS ==========
        combined_text = title + " " + specs

        brand = extract_brand(title)
        ram = extract_ram(combined_text)
        storage = extract_storage(combined_text)
        processor = extract_processor(combined_text)
        generation = extract_generation(combined_text)
        gpu = extract_gpu(combined_text)

        results.append({
            "Product Name": title,
            "Brand": brand,
            "Price (INR)": price,
            "Rating": rating,
            "RAM": ram,
            "Storage": storage,
            "Processor": processor,
            "Generation": generation,
            "GPU": gpu,
            "Specs / Description": specs
        })

    return results


def scrape_amazon(max_pages=10, delay=(2, 5)):
    all_data = []
    base_url = "https://www.amazon.in/s?k=laptop+under+50k"

    for page in range(1, max_pages + 1):
        url = f"{base_url}&page={page}"
        print("Scraping:", url)

        page_data = parse_search_page(url)
        all_data.extend(page_data)

        time.sleep(random.uniform(*delay))

    df = pd.DataFrame(all_data)
    df.to_csv("amazon_laptops_under_50k.csv", index=False)
    print("Saved", len(df), "records to amazon_laptops_under_50k.csv")


if __name__ == "__main__":
    scrape_amazon(max_pages=15)
