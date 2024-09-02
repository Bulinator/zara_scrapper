__author__ = "Bulinator"
__version__ = "0.1.0"
__license__ = "MIT"

import re

from currency_converter import CurrencyConverter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import json

# Prompt for user input
article_id = input("Enter the article ID: ")
if not article_id:
    article_id = "4387/249"


# Define the headers as a constant variable
user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")

# Add the desired option to disable the search engine choice screen
options = webdriver.ChromeOptions()
options.add_argument("--disable-search-engine-choice-screen")
options.add_argument(f"user-agent={user_agent}")

# Initialize the Selenium WebDriver (assuming Chrome)
driver = webdriver.Chrome(options=options)


# Maximize the browser window
# driver.maximize_window()

def is_valid_reference(reference):
    # Define the regex pattern for "number/number"
    pattern = r'^\d+/\d+$'

    # Use re.match to check if the reference matches the pattern
    if re.match(pattern, reference):
        return True

    return False

def handle_gdpr_cookie():
    try:
        gdpr = driver.find_elements(By.ID, "onetrust-accept-btn-handler")
        if gdpr:
            gdpr[0].click()
            time.sleep(2)
            print("GDPR handled")
    except Exception as e:
        print(f"No GDPR cookie to handle: {e}")


def handle_warning():
    try:
        # Find the warning button
        warning = driver.find_elements(By.CSS_SELECTOR, ".zds-button--primary > .zds-button__lines-wrapper")
        if warning:
            warning[0].click()  # Click the warning button to stay on the website
            time.sleep(2)  # Wait a moment for the warning to disappear
            print("Warning handled: Stayed on the website.")
    except Exception as e:
        print(f"No warning to handle: {e}")


def time_to_sleep_a_bit(sleeping_time=5):
    time.sleep(sleeping_time)


def convert_currency(amount, from_currency, to_currency="EUR"):
    c = CurrencyConverter()
    return c.convert(amount, from_currency, to_currency)


def get_price_and_name():
    name_element = driver.find_element(By.CSS_SELECTOR, ".product-detail-info__header-name")
    print(f"Article name: {name_element.text}")
    price_element = driver.find_element(
        By.XPATH,
        "//div[@class='product-detail-info__price-amount price']//span[@class='money-amount__main']"
    )
    if price_element.text:
        parts = price_element.text.split()
        if len(parts) != 2:
            raise ValueError("Input string must be in the format '<amount> <currency>'")

        # Extract the numeric part and the currency part
        amount, currency = parts
        # converted_amount = convert_currency(int(amount.replace(',', '')), currency)
        print(f"Price original: {price_element.text} is: [WORK IN PROGRESS] €")


def get_sizes_and_price(country_name):
    parent_element = driver.find_element(By.CSS_SELECTOR, ".size-selector-list__wrapper > ul")
    li_elements = parent_element.find_elements(By.TAG_NAME, "li")
    sizes = []
    for li in li_elements:
        # Find the <button> inside the <li>
        button = li.find_element(By.TAG_NAME, "button")

        # Check if the <button> has the required attribute
        if button.get_attribute("data-qa-action") == "size-in-stock":
            # Get the size text from the <div> inside the <button>
            size_div = button.find_element(By.CSS_SELECTOR, "div.product-size-info__main-label")
            size_text = size_div.text.strip()  # Use strip() to remove any surrounding whitespace
            sizes.append(size_text)

    # Join the list of sizes into a single string separated by commas
    sizes_string = ", ".join(sizes)
    if len(sizes_string) > 0:
        get_price_and_name()
        print("Sizes available:", sizes_string)
    else:
        print(f"Article not available in {country_name}")


# Function to search for an article and return details
def check_article_availability(countries, article_name):
    print(f"Loading zara websites: [{len(countries)}]")
    print(f"Article: {article_name}")

    for country in countries:
        the_country = country['name']
        print(f"Analyzing: {country['zara_url']} | Country: [{the_country}]")
        # Build url
        search_url = f"https://www.zara.com/{country['code'].lower()}/en/search"
        print(f"Search URL: {search_url}")
        # Load the search page
        driver.get(search_url)
        time_to_sleep_a_bit()
        # handle panel gdpr && warning country
        handle_gdpr_cookie()
        handle_warning()
        # time_to_sleep_a_bit()
        # Find the search input field
        search_input = driver.find_element(By.XPATH, "//input[@id='search-products-form-combo-input']")
        search_input.click()
        search_input.send_keys(article_name)
        search_input.send_keys(Keys.RETURN)
        time_to_sleep_a_bit(2)

        # extract information:
        div_result = driver.find_elements(By.CSS_SELECTOR, "._item > h2")
        if div_result:
            div_result[0].click()
            time_to_sleep_a_bit(3)
            # get price and article name
            get_sizes_and_price(the_country)

            time_to_sleep_a_bit(3)

        else:
            print(f"Impossible to find element for article [{article_name}]")


def main():
    filepath = "./data/zara_urls.json"
    with open(filepath, 'r') as file:
        countries = json.load(file)
    # Get user input for the article ID
    check_article_availability(countries, article_id)
    print("Process complete.")


if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()
