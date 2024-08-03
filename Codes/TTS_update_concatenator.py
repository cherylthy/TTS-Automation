import os
import pandas as pd

def concatenate_csv_files(input_folder, output_file):
    # List all files in the input folder
    files = os.listdir(input_folder)
    
    # Filter out only CSV files
    csv_files = [file for file in files if file.endswith('.csv')]
    
    # Create an empty list to store dataframes
    dfs = []
    
    # Read and append each CSV file to the list
    for csv_file in csv_files:
        file_path = os.path.join(input_folder, csv_file)
        df = pd.read_csv(file_path)
        dfs.append(df)
    
    # Concatenate all dataframes
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Write the combined dataframe to the output file
    combined_df.to_csv(output_file, index=False)
    print(f"All CSV files have been concatenated into {output_file}")

# Example usage
input_folder = 'TTS_updates'  # Replace with the path to your folder containing CSV files
output_file = 'TTS_updates1.csv'  # Replace with the desired output file name

concatenate_csv_files(input_folder, output_file)
