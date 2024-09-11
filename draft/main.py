__author__ = "Bulinator"
__version__ = "0.1.0"
__license__ = "MIT"

import json
import os

import requests
from datetime import datetime, timedelta

# Define the headers as a constant variable
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}


def load_initial_json(filepath):
    with open(filepath, 'r') as file:
        data = json.load(file)
    print(f"Loaded initial country JSON file with {len(data)} entries.")
    return data


def check_url_exists(url):
    try:
        response = requests.head(url, headers=HEADERS, allow_redirects=True, timeout=5)
        # A successful response (status code 200-299) means the URL exists
        if response.status_code in range(200, 302):
            return True

        print(f"URL does not exist or is not accessible: {url} (Status: {response.status_code})")
        return False
    except requests.RequestException as e:
        print(f"Error checking URL {url}: {e}")
        return False


def generate_zara_urls(country_data):
    base_url = "https://zara.com/"
    updated_country_data = []
    print("Loading zara urls...")

    for country in country_data:
        country_code = country['code'].lower()
        zara_url = f"{base_url}{country_code}/"
        if check_url_exists(zara_url):
            country['zara_url'] = f"{zara_url}"
            updated_country_data.append(country)
            # print(f"Generated URL: {zara_url} for {country['name']}")
        # else:
        #     print(f"URL does not exist: {zara_url} for {country['name']}")

    return updated_country_data


def is_file_older_than_one_month(filepath):
    if not os.path.exists(filepath):
        return True  # If the file does not exist, consider it as "older" so we can create it

    file_mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
    if datetime.now() - file_mod_time > timedelta(days=30):
        return True

    return False


def main():
    initial_json_filepath = "../data/world.json"
    zara_json_filepath = "../data/zara_urls.json"
    if is_file_older_than_one_month(zara_json_filepath):
        print("The Zara URL file is older than one month or does not exist. Updating it.")
        country_data = load_initial_json(initial_json_filepath)
        # Generate Zara URLs
        updated_country_data = generate_zara_urls(country_data)

        with open(zara_json_filepath, 'w') as outfile:
            json.dump(updated_country_data, outfile, indent=4)
            print(f"Saved updated JSON with URLs to updated_countries.json")
    else:
        print(f"The Zara URL file {zara_json_filepath} is up to date.")
        with open(zara_json_filepath, 'r') as infile:
            updated_country_data = json.load(infile)

    print("Process complete.")


if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()
