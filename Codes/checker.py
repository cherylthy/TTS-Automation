import pandas as pd

def find_missing_strategy_keys(strategy_keys_file, updates_file, output_file):
    # Read the strategy keys from the input CSV file
    strategy_keys_df = pd.read_csv(strategy_keys_file)
    
    # Read the TTS updates from the CSV file
    updates_df = pd.read_csv(updates_file)
    
    # Ensure both DataFrames have a 'Strategy Key' column
    if 'Strategy Key' not in strategy_keys_df.columns or 'Strategy Key' not in updates_df.columns:
        raise ValueError("Both input files must have a 'Strategy Key' column")
    
    # Find strategy keys that are in strategy_keys_df but not in updates_df
    missing_keys_df = strategy_keys_df[~strategy_keys_df['Strategy Key'].isin(updates_df['Strategy Key'])]
    
    # Write the missing strategy keys to the output CSV file
    missing_keys_df.to_csv(output_file, index=False)
    print(f"Missing strategy keys have been written to {output_file}")

# Example usage
strategy_keys_file = 'strategy_keys\strategy_keys.csv'  # Replace with the path to your strategy keys CSV file
updates_file = 'TTS_updates.csv'  # Replace with the path to your TTS updates CSV file
output_file = 'missing_strategy_keys.csv'  # Replace with the desired output file name

find_missing_strategy_keys(strategy_keys_file, updates_file, output_file)
