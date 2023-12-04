from selenium import webdriver
from selenium.webdriver.common.by import By
from fuzzywuzzy import fuzz
import re


def is_close_match(phrase, search_query, threshold=80):
    return fuzz.partial_ratio(phrase.lower(), search_query.lower()) >= threshold


def extract_mileage(description):
    # Define a more specific regex pattern for mileage
    mileage_pattern = r'\b(\d{1,3}(?:[.,\s]?\d{3})+)\s*(km|KM|Km)\b'
    matches = re.findall(mileage_pattern, description, re.IGNORECASE)

    valid_mileages = []
    for m in matches:
        try:
            # Convert the extracted string to an integer, cleaning it up first
            mileage = int(m[0].replace(' ', '').replace('.', '').replace(',', ''))
            if mileage > 1000:
                valid_mileages.append(mileage)
        except ValueError:
            # Ignore values that cannot be converted to an integer
            continue

    return max(valid_mileages, default=None)


def extract_details(description, pattern):
    match = re.search(pattern, description, re.IGNORECASE)
    return match.group(1) if match else None


def scrape_bazos_cars(search_url, search_query, threshold):
    driver = webdriver.Chrome()
    driver.get(search_url)

    all_cars = []

    listing_urls = list(set(
        element.get_attribute('href') for element in
        driver.find_elements(By.CSS_SELECTOR, "div.inzeratynadpis a")
    ))

    print("Prochazim auta na bazosi...")

    for url in listing_urls:
        if url and isinstance(url, str):
            driver.get(url)
        else:
            # Skips invalid url
            continue

        try:
            listing_name = driver.find_element(By.CSS_SELECTOR, "h1.nadpisdetail").text
            description = driver.find_element(By.CSS_SELECTOR, "div.popisdetail").text
            price_text = driver.find_element(By.XPATH, "//td[text()='Cena:']/following-sibling::td/b").text
        except Exception as e:
            # Want to skip if I cant access these details
            continue

        if not is_close_match(listing_name, search_query, threshold):
            continue

        if not re.search(r'\d', price_text):
            continue
        try:
            price = int(re.sub(r'\D', '', price_text))
        except ValueError:
            continue
        if price < 20000:
            continue

        power_output_pattern = r'(\d{2,3})\s*(kW|kw)'
        year_pattern = r'(\b(19|20)\d{2}\b)'

        power_output = extract_details(description, power_output_pattern)
        mileage = extract_mileage(description)
        year = extract_details(description, year_pattern)

        if power_output is None or mileage is None or year is None:
            continue

        if int(year) < 2000 or int(year) > 2023:
            continue

        car_data = {
            "listing_name": listing_name,
            "price": price,
            "power_output_kW": int(power_output),
            "mileage_km": mileage,
            "year": int(year),
            "url": driver.current_url,
            "marketplace": "bazos"
        }

        if not any(car['url'] == car_data['url'] for car in all_cars):
            all_cars.append(car_data)

    driver.quit()
    return all_cars


if __name__ == "__main__":
    # Example usage with hardcoded details
    search_url = 'https://auto.bazos.cz/inzeraty/audi-a6/'
    car_listings = scrape_bazos_cars(search_url, "Audi A6")
    for car in car_listings:
        print(car)
