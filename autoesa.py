from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fuzzywuzzy import fuzz
import re


def is_close_match(phrase, search_query, threshold=80):
    return fuzz.partial_ratio(phrase.lower(), search_query.lower()) >= threshold


def scrape_autoesa_car_details(driver):
    details = {}

    detail_elements = driver.find_elements(By.CSS_SELECTOR, "div.detail_attr_inner li")
    for element in detail_elements:
        try:
            label = element.find_element(By.TAG_NAME, "strong").text.strip()
            value = element.find_element(By.TAG_NAME, "span").text.strip()

            if label == "Rok":
                details['year'] = int(value)
            elif label == "Stav tachometru":
                details['mileage_km'] = int(value.replace(' km', '').replace('.', ''))
            elif label == "Výkon":
                details['power_output_kW'] = int(value.replace(' kW', ''))

        except Exception as e:
            pass  # To avoid an error where Selenium WebDriver is unable to locate an element with the specified selector

    return details


def scrape_autoesa_cars(search_url, search_query, threshold):
    driver = webdriver.Chrome()
    driver.get(search_url)

    all_cars = []

    listing_urls = [element.get_attribute('href') for element in driver.find_elements(By.CSS_SELECTOR, "a.car_item")]

    print("Prochazim auta na autoesa...")

    for url in listing_urls:
        if url and isinstance(url, str):
            driver.get(url)
        else:
            # Skips invalid url
            continue

        try:
            car_details = scrape_autoesa_car_details(driver)

            listing_name = driver.find_element(By.CSS_SELECTOR, "div.car_detail2__h1 h1").text
            price_text = driver.find_element(By.CSS_SELECTOR, "div.show-more-price-right strong").text
            price = int(price_text.replace("\xa0", "").replace(" ", "").replace("Kč", ""))

            if not is_close_match(listing_name, search_query, threshold) or not car_details:
                continue

            car_data = {
                "listing_name": listing_name,
                "price": price,
                "power_output_kW": car_details['power_output_kW'],
                "mileage_km": car_details['mileage_km'],
                "year": car_details['year'],
                "url": driver.current_url,
                "marketplace": "autoesa"
            }

            if not any(car['listing_name'] == car_data['listing_name'] for car in all_cars):
                all_cars.append(car_data)

        except Exception as e:
            print(f"Error occurred while accessing URL {url}: {e}")
            continue

    driver.quit()
    return all_cars


if __name__ == "__main__":
    # Example usage with hardcoded details
    search_url = 'https://www.autoesa.cz/hledani?q=Audi%20A6&razeni=6'
    car_listings = scrape_autoesa_cars(search_url, "Audi A6")
    for car in car_listings:
        print(car)
