# This file is part of QOBLIB - Quantum Optimization Benchmarking Library
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Define the path to the folder containing the CSV files
import gzip
import os
import pandas as pd

def create_zimpl_prices(input_csv_path: str, output_gzip_path: str) -> None:
    """
    Convert stock prices from CSV to a ZIMPL-formatted gzip file.

    The input CSV file should contain a header row with stock symbols and a column
    labeled 'Date'. The function will iterate over the rows of the CSV file, and
    for each row, it will write the stock symbol and price to the output file,
    followed by a newline character. The day index is incremented for each day.

    :param input_csv_path: The path to the input CSV file
    :param output_gzip_path: The path to the output gzip file
    :return: None
    """
    stock_data = pd.read_csv(input_csv_path)

    # Initialize the day index to 0
    day_index = 0

    # Open the output file to write in gzip format
    with gzip.open(output_gzip_path, 'wt') as output_file:
        # Iterate over the rows of the CSV file
        for _, row in stock_data.iterrows():
            # Iterate over the columns of the row
            for stock, price in row.items():
                # Skip the 'Date' column
                if stock != 'Date':
                    # Write the day index, stock symbol, and price to the output file
                    output_file.write(f"{day_index} {stock} {price}\n")
            # Increment the day index
            day_index += 1

    print(f"> ZIMPL-formatted prices file created successfully at {output_gzip_path}.")

def create_zimpl_covariance_matrices(folder_path: str, output_file_path: str) -> None:
    """
    Create a ZIMPL-formatted file from the covariance matrices in the given folder.

    The input folder should contain CSV files with the following format:
        - The first column contains stock symbols
        - The remaining columns are the stock symbols
        - The values in the table are the covariances between the stocks

    The output file will be a gzip file with the following format:
        - Each line represents a covariance matrix for a given day
        - The first column is the day index
        - The second column is the first stock symbol
        - The third column is the second stock symbol
        - The fourth column is the covariance value
    """

    # Get a list of all CSV files in the folder
    file_paths = sorted([os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')])

    # Open the output file to write in gzip format
    with gzip.open(output_file_path, 'wt') as file:
        # Initialize the day counter starting from 6
        day_counter = 0

        # Loop through each CSV file
        for file_path in file_paths:
            # Load the CSV file
            df = pd.read_csv(file_path)

            # Get the stock names from the columns
            stock_names = df.columns[1:]

            # Loop through each row in the DataFrame
            for _, row in df.iterrows():
                # Loop through each column (stock name and value)
                for j, stock_name in enumerate(stock_names):
                    # Write to the output file
                    file.write(f"{day_counter} {row.iloc[0]} {stock_name} {row.iloc[j+1]}\n")

            # Increment the day counter for each CSV file
            day_counter += 1

    print(f"> ZIMPL-formatted covariance matrices file created successfully at {output_file_path}.")
