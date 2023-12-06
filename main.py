from sbazar import scrape_sbazar_cars
from bazos import scrape_bazos_cars
from autoesa import scrape_autoesa_cars
import sys


def get_user_input():
    car = input("Zadej model auta (ve formatu \"Audi A6\" / \"BMW Rada 3\", bez diakritiky): ")
    car_words = car.split()
    car_brand = car_words[0]
    car_model = ' '.join(car_words[1:])
    try:
        user_threshold = int(input("(Nepovinny udaj) Zadejte Vasi preferovanou prahovou hodnotu pro presnost shody (0-100): "))
        if not 0 <= user_threshold <= 100:
            raise ValueError
    except ValueError:
        print("Neplatny vstup. Pouziva se vychozi prahova hodnota 80.")
        user_threshold = 80 # Default threshold
    print(
        f"Program ted projede nejnovejsi inzerce na prednich ceskych bazarech a vypise vam 10 nejlepsich aut znacky {car_brand} modelu {car_model} s nejlepsim pomerem cena/vykon.")
    return car_brand, car_model, user_threshold


if __name__ == "__main__":

    car_brand, car_model, user_threshold = get_user_input()

    search_url = f"https://www.sbazar.cz/hledej/{car_brand.replace(' ', '%20')}%20{car_model.replace(' ', '%20')}/170-osobni-auta"
    car_listings_sbazar = scrape_sbazar_cars(search_url, car_model, user_threshold)

    search_url = f"https://auto.bazos.cz/inzeraty/{car_brand.replace(' ', '-')}-{car_model.replace(' ', '-')}/"
    car_listings_bazos = scrape_bazos_cars(search_url, car_model, user_threshold)

    search_url = f"https://www.autoesa.cz/hledani?q={car_brand.replace(' ', '%20')}%20{car_model.replace(' ', '%20')}&razeni=6"
    car_listings_autoesa = scrape_autoesa_cars(search_url, car_model, user_threshold)

    all_car_listings = car_listings_sbazar + car_listings_bazos + car_listings_autoesa

    if not all_car_listings:
        print(f"Nebylo nalezeno zadne auto znacky {car_brand} modelu {car_model}. Zkuste snizit prahovou hodnotu pro presnost shody.")
        sys.exit()

    # Normalize the data
    max_year = max(car['year'] for car in all_car_listings)
    min_year = min(car['year'] for car in all_car_listings)  # Adding minimum year
    max_mileage = max(car['mileage_km'] for car in all_car_listings)
    min_mileage = min(car['mileage_km'] for car in all_car_listings)
    max_power_output = max(car['power_output_kW'] for car in all_car_listings)

    for car in all_car_listings:
        car['norm_year'] = (car['year'] - min_year) / (max_year - min_year)
        car['norm_mileage'] = (max_mileage - car['mileage_km']) / (max_mileage - min_mileage)
        car['norm_power_output'] = car['power_output_kW'] / max_power_output

    # Assign weights
    weight_year = 0.4
    weight_mileage = 0.3
    weight_power_output = 0.3

    # Calculate score
    for car in all_car_listings:
        car['score'] = (car['norm_year'] * weight_year) + (car['norm_mileage'] * weight_mileage) + (
                    car['norm_power_output'] * weight_power_output)

    # Sort the cars based on the score
    all_car_listings.sort(key=lambda x: x['score'], reverse=True)

    # Print only the top 10 cars, ranked
    print(
        "Auta s nejlepsim pomerem cena/vykon:\n(Pokud program nasel mene nez 10 aut, pravdepodobne to znamena, ze se jedna o model,\nktery se tak casto v ceskych bazarech nevyskytuje nebo je nazev modelu zadan nepresne a proto je treba snizit prahovou hodnotu pro presnost shody.\nPaklize to zobrazuje i jine modely, je treba prahovou hodnotu zvysit.)")
    for index, car in enumerate(all_car_listings[:10], start=1):
        print(
            f"{index}. Nazev inzeratu: {car['listing_name']}, Cena: {car['price']}, Vykon: {car['power_output_kW']} kW, Najezd: {car['mileage_km']} km, Rok: {car['year']}, Skore: {car['score']:.2f}, URL: {car['url']}")
