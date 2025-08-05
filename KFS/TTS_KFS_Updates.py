import pandas as pd
from datetime import datetime

# Load both CSV files
ecura_file_path = 'TTS-Automation\KFS\ScraperVerifyReportInternal_2025-05-26_07_34_08.csv'
prive_file_path = 'TTS-Automation\KFS\TTS_FUNDS_20250512.csv'

ecura_csv = pd.read_csv(ecura_file_path)
prive_csv = pd.read_csv(prive_file_path)

# Function to convert "Month Year" to "1/Month/Year"
def convert_text_to_date(text):
    if isinstance(text, str):  # Ensure the value is a string
        try:
            date_obj = datetime.strptime(text, "%B %Y")
            return date_obj.strftime("1/%m/%Y")
        except ValueError:
            return None  # Return None for invalid formats
    return None

# Apply the conversion function to the 'Text' column in ecura_csv
ecura_csv['Date from ecura DB'] = ecura_csv['Text'].apply(convert_text_to_date)

# Convert both the 'Date from ecura DB' and 'DOCDATE' to datetime objects for comparison
ecura_csv['Date from ecura DB'] = pd.to_datetime(ecura_csv['Date from ecura DB'], format="1/%m/%Y", errors='coerce')
prive_csv['DOCDATE'] = pd.to_datetime(prive_csv['DOCDATE'], errors='coerce')

# Filter the ecura_csv to only include rows where Language is 'en'
ecura_filtered = ecura_csv[ecura_csv['Language'] == 'en']

# Filter both DataFrames to only include matching ISINs
matched_isin = ecura_filtered[ecura_filtered['ISIN'].isin(prive_csv['ISIN'])]

# Merge ecura_filtered with prive_csv based on ISIN to compare only matching ISINs
result_df = pd.merge(prive_csv, matched_isin[['ISIN', 'Date from ecura DB']], on='ISIN', how='inner')

# Compare the dates between 'Date from ecura DB' and 'DOCDATE' and apply the new logic
def get_status(row):
    if pd.notnull(row['Date from ecura DB']) and pd.notnull(row['DOCDATE']):
        # If docdate is older than Date from ecura DB, mark as "date is not updated in fund universe"
        if row['DOCDATE'] < row['Date from ecura DB']:
            return 'date is not updated in fund universe'
        # If month and year are the same, mark as "Up to date"
        elif row['Date from ecura DB'].year == row['DOCDATE'].year and row['Date from ecura DB'].month == row['DOCDATE'].month:
            return 'Up to date'
        # If dates are different, mark as "Outdated"
        else:
            return 'Outdated'
    return 'Outdated'

# Apply the comparison logic for status
result_df[f'Status as of {datetime.now()}'] = result_df.apply(get_status, axis=1)

# Calculate "Days since last updated in TTS DB" and "Days since last updated from PDF File"
current_date = pd.Timestamp.now()

result_df['Days since last updated in TTS DB'] = (current_date - result_df['Date from ecura DB']).dt.days
result_df['Days since last updated from PDF File'] = (current_date - result_df['DOCDATE']).dt.days

# Display the result with all columns from prive_csv plus the new ones
print(result_df.head())

# You can also save the result to a CSV file if needed
result_df.to_csv('TTS-Automation/KFS/Updated_TTS_FUNDS_Result.csv', index=False)
