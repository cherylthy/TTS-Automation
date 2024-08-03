import requests
from bs4 import BeautifulSoup
import csv

# Base URL of the webpage
url = "https://privetts.privemanagers.com/privetts/scraper/verify"

def extract_strategy_keys(url):
    strategy_keys = []
    
    # Send HTTP request to the URL
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return strategy_keys

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Loop through all td elements with ids starting with 'keyList_'
    for i in range(574):  # Adjust the range as necessary
        td_id = f"keyList_{i}"
        td_element = soup.find('td', {'id': td_id})

        if td_element:
            # Extract the strategy key text and split by <br> elements
            strategy_key_text = td_element.decode_contents().split('<br/>')
            for key in strategy_key_text:
                strategy_keys.append(key.strip())

    return strategy_keys

# Extract strategy keys
strategy_keys = extract_strategy_keys(url)

# Save to a CSV file with each key on a new line
with open('strategy_keys.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Strategy Key'])  # Header row
    for key in strategy_keys:
        writer.writerow([key])  # Write each strategy key in a new row

print("Strategy keys have been saved to 'strategy_keys.csv'.")
