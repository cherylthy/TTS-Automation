import requests
import re
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

# Function to scrape dates from the website
def scrape_dates_from_website(strategy_key):

    strategy_key = str(strategy_key)

    # Scrape the website for date
    website_url = "https://privetts.privemanagers.com/privetts/scraper/verify"
    response = requests.get(website_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the Strategy Key element
    strategy_key_element = soup.find(string=re.compile(r'\b{}\b'.format(re.escape(strategy_key))))

    results = {
        'Strategy Key': strategy_key,
        'ISIN': 'N/A',
        'Extracted Date from TTS DB': 'Date not found in the paragraph',
        'Extracted Date from PDF File': 'Date not found in the paragraph',
        'Days since last updated from TTS DB': 'N/A',
        'Days since last updated from PDF File': 'N/A',
        'Update Needed?': 'N/A'
    }

    if strategy_key_element:
        # Extract the id attribute of the Strategy Key element
        strategy_key_id = strategy_key_element.parent.get('id')

        # Extract the value after "List" in the id
        strategy_key_value = re.sub(r'.', '', strategy_key_id, count=8)

        if strategy_key_value:
            # Create the ids for both English and Chinese paragraph elements
            english_paragraph_id = f"editTtsTextEn_{strategy_key_value}"

            # Locate the English paragraph element using the created id
            english_paragraph_element = soup.find("td", {"id": english_paragraph_id})

            if english_paragraph_element:
                # Extract and print the text content of the English paragraph element
                english_paragraph_text = english_paragraph_element.get_text().strip()

                # Search for the date pattern in the English paragraph
                english_date_extracted = re.search(r'dated (.*?) of', english_paragraph_text, re.DOTALL | re.IGNORECASE)
                if english_date_extracted:
                    extracted_date_english = english_date_extracted.group(1).strip()
                    try:
                        # Convert the extracted date to datetime object
                        date_obj = datetime.strptime(extracted_date_english, "%B %Y")
                        results['Extracted Date from TTS DB'] = date_obj.strftime("%d/%m/%Y")
                    except ValueError:
                        results['Extracted Date from TTS DB'] = 'Invalid date format in TTS DB'

    return results

# Read the CSV file containing the strategy keys [Remember to change this when moving on to a new set]
strategy_keys_df = pd.read_csv('strategy_keys\strategy_keys_set5.csv')  # Ensure the CSV file has a column named 'Strategy Key'
strategy_keys = strategy_keys_df['Strategy Key'].tolist()

# Create an empty list to store results
results = []

# Iterate through strategy keys and scrape dates for each
for strategy_key in strategy_keys:
    print(f"Now on strategy key: {strategy_key}")
    result = scrape_dates_from_website(strategy_key)
    results.append(result)
    # URL from which PDFs are to be downloaded
    url = f"https://citi.privemanagers.com/?locale=en&viewMode=BASIC#investmentDetails;strategyKey={strategy_key};hideBackButton=false;dataSource=2;token=1d9c18a2-3df7-4af0-9249-334b61d30ebc;exePlatformKey=3630;P1=1d9c18a2-3df7-4af0-9249-334b61d30ebc;P2=5;P3=HKG"

    try:
        # Create a WebDriver instance (you will need to install the appropriate driver for your browser)
        driver = webdriver.Chrome()  # Make sure to have the Chrome WebDriver installed

        # Navigate to the URL
        driver.get(url)

        # Wait for a specific element to be present (you may need to adjust the selector)
        wait = WebDriverWait(driver, 30)  # Increased timeout to 60 seconds
        element = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '.pdf')]")))

        # Find all hyperlinks with an 'href' attribute containing '.pdf'
        pdf_links = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
        i = 0

        # Iterate through PDF links and download PKF files
        for link in pdf_links:
            href = link.get_attribute("href")
            # Check the sections in the URL to classify PDFs
            if 'PKF' in href:

                # Extract date from the PDF file name
                pdf_date_match = re.search(r'_(\d{8})\.pdf', href)
                if pdf_date_match:
                    extracted_date_pdf = pdf_date_match.group(1)
                    try:
                        # Convert the extracted date to datetime object
                        date_obj = datetime.strptime(extracted_date_pdf, "%Y%m%d")
                        formatted_date = date_obj.strftime("%d/%m/%Y")
                        results[-1]['Extracted Date from PDF File'] = formatted_date
                    except ValueError:
                        results[-1]['Extracted Date from PDF File'] = 'Invalid date format in PDF'

                # Extract ISIN from the href
                isin_match = re.search(r'fileName=([^_]+)', href)
                if isin_match:
                    extracted_isin = isin_match.group(1).strip()
                    results[-1]['ISIN'] = extracted_isin
                else:
                    results[-1]['ISIN'] = 'ISIN not found'

    except Exception as e:
        print(f"An error occurred for strategy key {strategy_key}: {str(e)}")

    finally:
        # Close the browser
        driver.quit()

# Convert today's date to a datetime object
today_date = datetime.now()

# Calculate days since last updated and add columns
for result in results:
    # Extract date from PDF
    pdf_date_str = result['Extracted Date from PDF File']
    if pdf_date_str != 'Date not found in the paragraph' and pdf_date_str != 'Invalid date format in PDF':
        pdf_date = datetime.strptime(pdf_date_str, "%d/%m/%Y")
        days_since_pdf = (today_date - pdf_date).days
        result['Days since last updated from PDF File'] = days_since_pdf
    else:
        result['Days since last updated from PDF File'] = 'N/A'

    # Extract date from TTS DB
    tts_date_str = result['Extracted Date from TTS DB']
    if tts_date_str != 'Date not found in the paragraph' and tts_date_str != 'Invalid date format in TTS DB':
        tts_date = datetime.strptime(tts_date_str, "%d/%m/%Y")
        days_since_tts = (today_date - tts_date).days
        result['Days since last updated from TTS DB'] = days_since_tts
    else:
        result['Days since last updated from TTS DB'] = 'N/A'

    # Check if update is needed
    if pdf_date_str != 'Date not found in the file name' and pdf_date_str != 'Invalid date format in PDF' and tts_date_str != 'Date not found in the paragraph' and tts_date_str != 'Invalid date format in TTS DB':
        pdf_month_year = pdf_date.strftime("%m/%Y")
        tts_month_year = tts_date.strftime("%m/%Y")
        if pdf_month_year == tts_month_year:
            result['Update Needed?'] = 'NO'
        else:
            result['Update Needed?'] = 'YES'
    else:
        result['Update Needed?'] = 'N/A'

# Create a DataFrame from the results
df = pd.DataFrame(results)
df.to_csv('TTS_updates_set32.csv', encoding='utf-8', index=False) #[Remember to change this when moving on to a new set]

# Print the DataFrame
print(df)
 