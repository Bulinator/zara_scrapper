# Zara Tool v1.0
# __author__ = "Bulinator"
# __version__ = "0.1.0"
# __license__ = "MIT"

import os
import json
import re
import time
from datetime import datetime, timedelta
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from currency_converter import CurrencyConverter

# Define the headers as a constant variable
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 "
                  "Safari/537.36"
}


# ASCII Art logo
def display_logo():
    logo = r"""
              .-')                ('-.         .-') _    .-') _  
             ( OO ).             ( OO ).-.    ( OO ) )  (  OO) ) 
            (_)---\_)   .-----.  / . --. /,--./ ,--,' ,(_)----.  
            /    _ |   '  .--./  | \-.  \ |   \ |  |\ |       |  
            \  :` `.   |  |('-..-'-'  |  ||    \|  | )'--.   /   
             '..`''.) /_) |OO  )\| |_.'  ||  .     |/ (_/   /    
            .-._)   \ ||  |`-'|  |  .-.  ||  |\    |   /   /___  
            \       /(_'  '--'\  |  | |  ||  | \   |  |        | 
             `-----'    `-----'  `--' `--'`--'  `--'  `--------' 
                                                    by Bulinator
    """
    print(logo)


# Menu
def display_menu():
    print("Choose an action:")
    print("1. Generate Zara URLs for countries")
    print("2. Scrape Zara for article availability")
    print("3. Exit")


# Function to load the initial JSON data
def load_initial_json(filepath):
    with open(filepath, 'r') as file:
        data = json.load(file)
    print(f"Loaded initial country JSON file with {len(data)} entries.")
    return data


# Function to check if a URL exists
def check_url_exists(url):
    try:
        response = requests.head(url, headers=HEADERS, allow_redirects=True, timeout=5)
        if response.status_code in range(200, 302):
            return True
        print(f"URL does not exist or is not accessible: {url} (Status: {response.status_code})")
        return False
    except requests.RequestException as e:
        print(f"Error checking URL {url}: {e}")
        return False


# Function to generate Zara URLs based on country data
def generate_zara_urls(country_data):
    base_url = "https://zara.com/"
    updated_country_data = []
    print("Loading Zara URLs...")

    for country in country_data:
        country_code = country['code'].lower()
        zara_url = f"{base_url}{country_code}/"
        if check_url_exists(zara_url):
            country['zara_url'] = zara_url
            updated_country_data.append(country)

    return updated_country_data


# Function to check if a file is older than one month
def is_file_older_than_one_month(filepath):
    if not os.path.exists(filepath):
        return True
    file_mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
    return datetime.now() - file_mod_time > timedelta(days=30)


def ensure_folder_exists(folder_path):
    """Ensure the folder exists, and if not, create it."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder {folder_path} created.")
    else:
        print(f"Folder {folder_path} already exists.")


# Function to generate or load the Zara URL data
def run_main():
    data_folder = "./data"
    initial_json_filepath = os.path.join(data_folder, "world.json")
    zara_json_filepath = os.path.join(data_folder, "zara_urls.json")

    # Ensure the 'data' folder exists
    ensure_folder_exists(data_folder)

    if is_file_older_than_one_month(zara_json_filepath):
        print("The Zara URL file is older than one month or does not exist. Updating it.")
        country_data = load_initial_json(initial_json_filepath)
        updated_country_data = generate_zara_urls(country_data)

        with open(zara_json_filepath, 'w') as outfile:
            json.dump(updated_country_data, outfile, indent=4)
            print(f"Saved updated JSON with URLs to {zara_json_filepath}")
    else:
        print(f"The Zara URL file {zara_json_filepath} is up to date. Nothing to do dude!")
        with open(zara_json_filepath, 'r') as infile:
            updated_country_data = json.load(infile)
    return updated_country_data


# Scraper Functions
def handle_gdpr_cookie(driver):
    try:
        gdpr = driver.find_elements(By.ID, "onetrust-accept-btn-handler")
        if gdpr:
            gdpr[0].click()
            time.sleep(2)
            print("GDPR handled")
    except Exception as e:
        print(f"No GDPR cookie to handle: {e}")


def handle_warning(driver):
    try:
        warning = driver.find_elements(By.CSS_SELECTOR, ".zds-button--primary > .zds-button__lines-wrapper")
        if warning:
            warning[0].click()
            time.sleep(2)
            print("Warning handled: Stayed on the website.")
    except Exception as e:
        print(f"No warning to handle: {e}")


def convert_currency(amount, from_currency, to_currency="EUR"):
    c = CurrencyConverter()
    try:
        return c.convert(amount, from_currency, to_currency)
    except ValueError:
        # raise ValueError(f"{from_currency} is not a supported currency")
        return None


def get_price_and_name(driver):
    name_element = driver.find_element(By.CSS_SELECTOR, ".product-detail-info__header-name")
    print(f"Article name: {name_element.text}")
    price_element = driver.find_element(
        By.XPATH,
        "//div[@class='product-detail-info__price-amount price']//span[@class='money-amount__main']"
    )
    if price_element.text:
        parts = price_element.text.split()
        amount, currency = parts
        # Remove commas from the amount string
        amount = amount.replace(',', '')
        priceConverted = None
        if currency != 'EUR':
            priceConverted = convert_currency(int(float(amount)), currency)

        if priceConverted:
            print(f"Original price: {price_element.text} | Price: [{priceConverted:.2f}] €")
        else:
            print(f"Original price: {price_element.text} / N.A")


def get_sizes_and_price(driver, country_name):
    parent_element = driver.find_element(By.CSS_SELECTOR, ".size-selector-list__wrapper > ul")
    li_elements = parent_element.find_elements(By.TAG_NAME, "li")
    sizes = [li.find_element(By.TAG_NAME, "button").find_element(By.CSS_SELECTOR,
                                                                 "div.product-size-info__main-label").text.strip() for
             li in li_elements if
             li.find_element(By.TAG_NAME, "button").get_attribute("data-qa-action") == "size-in-stock"]
    sizes_string = ", ".join(sizes)

    if sizes_string:
        get_price_and_name(driver)
        print("Sizes available:", sizes_string)
    else:
        print(f"Article not available in {country_name}")


# Function to search for an article and return details
def check_article_availability(driver, countries, article_name):
    print(f"Loading Zara websites: [{len(countries)}]")
    print(f"Article: {article_name}")

    for country in countries:
        the_country = country['name']
        print(f"Analyzing: {country['zara_url']} | Country: [{the_country}]")
        search_url = f"https://www.zara.com/{country['code'].lower()}/en/search"
        print(f"Search URL: {search_url}")
        driver.get(search_url)
        time.sleep(5)
        handle_gdpr_cookie(driver)
        handle_warning(driver)
        search_input = driver.find_element(By.XPATH, "//input[@id='search-products-form-combo-input']")
        search_input.click()
        search_input.send_keys(article_name)
        search_input.send_keys(Keys.RETURN)
        time.sleep(3)
        div_result = driver.find_elements(By.CSS_SELECTOR, "._item > h2")
        if div_result:
            div_result[0].click()
            time.sleep(3)
            get_sizes_and_price(driver, the_country)
            time.sleep(3)
        else:
            print(f"Impossible to find element for article [{article_name}]")


def is_valid_reference(reference):
    """Check if the article ID is in the format number/number."""
    pattern = r'^\d+/\d+$'
    return re.match(pattern, reference)


# Scraping function that runs after Zara URL generation
def run_scraper():
    filepath = "./data/zara_urls.json"
    while True:
        article_id = (input("Enter the article ID (or press Enter for default [4387/249], or 'q' for exit): ")
                      or "4387/249")

        if article_id == "q":
            exit()
        elif is_valid_reference(article_id):
            break
        else:
            print("Invalid format. Please enter the article ID in the format <numbers>/<numbers>, e.g: 4387/2492")

    with open(filepath, 'r') as file:
        countries = json.load(file)

    user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-search-engine-choice-screen")
    options.add_argument(f"user-agent={user_agent}")

    driver = webdriver.Chrome(options=options)

    check_article_availability(driver, countries, article_id)
    driver.quit()


# Main program loop
def main():
    display_logo()

    while True:
        display_menu()
        choice = input("Enter your choice (1-3): ")

        if choice == "1":
            # Generate Zara URLs
            run_main()
        elif choice == "2":
            # Scrape Zara for article availability
            run_scraper()
        elif choice == "3":
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    main()
