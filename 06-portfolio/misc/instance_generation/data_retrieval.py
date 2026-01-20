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


from typing import Any, Dict, List, Optional
import yfinance as yf
import pandas as pd
import os

def get_sp500_symbols() -> List[str]:
    """Fetch and return a list of S&P 500 company symbols from Wikipedia.

    Returns:
        List[str]: A list of the S&P 500 company symbols.
    """
    tables = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    sp500_df = tables[0]
    sp500_symbols = sp500_df['Symbol'].tolist()
    return sp500_symbols

def get_top_companies_by_market_cap(top_n: int = 50) -> List[str]:
    """Fetch market cap data for S&P 500 companies and return the top N symbols.

    Parameters:
        top_n (int): The number of top companies to return. Defaults to 50.

    Returns:
        List[str]: A list of the top N company symbols.
    """
    # Get the list of S&P 500 company symbols
    symbols: List[str] = get_sp500_symbols()
    market_cap_data: List[Dict[str, Any]] = []

    # Iterate over the symbols and retrieve the market cap data for each
    for symbol in symbols:
        print(f"Retrieving data for {symbol}...")
        try:
            stock = yf.Ticker(symbol)
            market_cap = stock.info.get('marketCap')

            if market_cap is not None:
                market_cap_data.append({'symbol': symbol, 'market_cap': market_cap})
                
        except Exception as e:
            print(f"Failed to retrieve data for {symbol}: {e}")

    market_cap_df: pd.DataFrame = pd.DataFrame(market_cap_data)

    # Sort the DataFrame by market cap in descending order and keep the top N
    market_cap_df = market_cap_df.sort_values(by='market_cap', ascending=False)
    
    market_cap_df.to_csv('market_cap_data.csv', index=False)
    
    market_cap_df = market_cap_df#.head(top_n)

    top_symbols: List[str] = market_cap_df['symbol'].values.tolist()

    return top_symbols

def download_stock_data(symbols: List[str], start_date: str = "2024-01-01", end_date: str = "2024-05-31") -> Dict[str, pd.DataFrame]:
    """Download historical stock data for given symbols.

    Parameters:
        symbols (List[str]): List of stock symbols to download data for.
        start_date (str): Start date in the format 'YYYY-MM-DD'. Defaults to '2024-01-01'.
        end_date (str): End date in the format 'YYYY-MM-DD'. Defaults to '2024-05-31'.

    Returns:
        Dict[str, pd.DataFrame]: A dictionary where the keys are the stock symbols and the values are the historical stock data as DataFrames.
    """
    historical_data: Dict[str, pd.DataFrame] = {}
    
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            historical_data[symbol] = ticker.history(start=start_date, end=end_date, auto_adjust=False)
        except Exception as error:
            print(f"Error downloading data for {symbol}: {error}")
            
    return historical_data

def combine_stock_data(input_dir: str, output_file: str = 'combined_stock_data.csv') -> pd.DataFrame:
    """
    Combine stock data from multiple CSV files into a single CSV file using pandas merge.

    Parameters:
        input_dir (str): The directory containing individual stock data CSV files.
        output_file (str): The path for the combined CSV output file.

    Returns:
        pd.DataFrame: The combined stock data as a DataFrame.
    """
    combined_data: Optional[pd.DataFrame] = None

    for file_name in os.listdir(input_dir):
        if file_name.endswith('.csv'):
            file_path = os.path.join(input_dir, file_name)
            symbol = file_name.split('.')[0]

            data = pd.read_csv(file_path, usecols=['Date', 'Adj Close'])
            data.rename(columns={'Adj Close': symbol}, inplace=True)

            if combined_data is None:
                combined_data = data
            else:
                combined_data = pd.merge(combined_data, data, on='Date', how='outer')

    if combined_data is not None:
        combined_data.to_csv(output_file, index=False)
    
    return combined_data
