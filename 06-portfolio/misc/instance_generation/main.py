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


import os

import pandas as pd
from csv_to_txt import create_zimpl_covariance_matrices, create_zimpl_prices
from data_preparation import generate_daily_covariance_matrices, perturb_returns_and_generate_prices
from data_retrieval import combine_stock_data, download_stock_data, get_top_companies_by_market_cap

def retrieve_stock_data(start_date: str = '2024-01-01', end_date: str = '2024-05-31'):
    # create directory for stock data
    stock_dir = f'./stock_data_{start_date}_{end_date}'

    
    if os.path.exists(stock_dir):
        # if stock_dir exists, skip
        print(f"Stock data already retrieved and combined in {stock_dir}.")
        return stock_dir
    elif os.path.exists(stock_dir + '.tar.gz'):
        # check whether there is a .tar.gz with that name and extract it if it exists
        os.system(f'tar -xzf {stock_dir}.tar.gz')
        print(f"Extracted {stock_dir}.tar.gz")
        return stock_dir
    else:
        print(f"Retrieving stock data from {start_date} to {end_date}...")
    
    
    individual_stock_dir = os.path.join(stock_dir, 'individual_stock_data')
    os.makedirs(individual_stock_dir, exist_ok=True)
    
    # retrieve data from yfinance and save to csv
    top_symbols = get_top_companies_by_market_cap()
    data = download_stock_data(top_symbols, start_date=start_date, end_date=end_date)
    for symbol in data:
        stock_path = os.path.join(individual_stock_dir, f'{symbol}.csv')
        data[symbol].to_csv(stock_path)
        
    combined_stock_path = os.path.join(stock_dir, f'combined_stock_data.csv')
    combine_stock_data(input_dir=individual_stock_dir, output_file=combined_stock_path)
    
    print(f"Data retrieval and combination completed {stock_dir}.")
    
    return stock_dir

def generate_perturbed_prices(stock_data, instance_dir, time_interval, iterations=10):
    num_assets = len(stock_data.columns)
    
    instances = []
    # initialize mask to keep all original data
    mask = stock_data.index

    # create perturbed stock data
    for iteration in range(iterations):
        print("")
        print(f"> Generating for seed {iteration}")

        # create directory for perturbed instance
        perturbed_instance = os.path.join(instance_dir, f'po_a{num_assets:03}_t{time_interval:02}_s{iteration:02}')
        os.makedirs(perturbed_instance, exist_ok=True)
        perturbed_file = os.path.join(perturbed_instance, f'combined_stock_data.csv')

        # perturb stock data
        perturbed_data, mask = perturb_returns_and_generate_prices(stock_data, seed=iteration)

        # save perturbed data
        perturbed_data.to_csv(perturbed_file)
        instances.append(perturbed_instance)

        print(f"> Written combined perturbed prices to {perturbed_file}")
    
    # add the original data as well
    original_instance = os.path.join(instance_dir, f'po_a{num_assets:03}_t{time_interval:02}_orig')
    os.makedirs(original_instance, exist_ok=True)
    original_file = os.path.join(original_instance, f'combined_stock_data.csv')

    stock_data.loc[mask].to_csv(original_file)
    instances.append(original_instance)

    print("")
    print(f"> Written combined original prices to {original_file}")
        
    return instances
    
def convert_to_txt(instance_dir):
    # set input files
    covariance_matrices_dir = os.path.join(instance_dir, 'future_covariance_matrices')
    stock_prizes = os.path.join(instance_dir, 'stock_prices.csv')
    
    # set output files
    output_file_cov = os.path.join(instance_dir, 'covariance_matrices.txt.gz')
    output_file_prices = os.path.join(instance_dir, 'stock_prices.txt.gz')
    
    # create .txt.gz files
    create_zimpl_covariance_matrices(covariance_matrices_dir, output_file_cov)
    create_zimpl_prices(stock_prizes, output_file_prices)

def main():
    # Instances to generate
    asset_params = [10, 50, 200, 400]
    time_params = [10, 15]
    seeds_per_instance = 3
    
    # retrieve stock data if not already retrieved
    stock_dir = retrieve_stock_data()

    instance_dir = './../../instances/new'

    # create directories if not exist
    os.makedirs(instance_dir, exist_ok=True)

    perturbed_instances = []
    
    # read necessary info
    market_caps = pd.read_csv(os.path.join(stock_dir, 'market_cap_data.csv'))
    stock_data = pd.read_csv(os.path.join(stock_dir, 'combined_stock_data.csv'), index_col='Date', parse_dates=True)
    
    for num_assets in asset_params:
        for time_interval in time_params:
            # get top companies and load stock data
            top_companies = market_caps.head(num_assets)['symbol'].values.tolist()
            
            # only use top n companies
            local_stock_data = stock_data[top_companies]
            
            print("")
            print(f"=== Generating perturbed prizes for {num_assets} assets and {time_interval} days ===")

            local_perturbed_instances = generate_perturbed_prices(stock_data=local_stock_data, instance_dir=instance_dir, time_interval=time_interval, iterations=seeds_per_instance)
            
            print("")
            for perturbed_instance in local_perturbed_instances:
                print(f"> Generating daily covariances for {perturbed_instance}")
                generate_daily_covariance_matrices(perturbed_instance, time_interval=time_interval)

            perturbed_instances.extend(local_perturbed_instances)
        
    print("")
    print("=== Generating necessary data for ZIMPL model ===")
    # iterate over all perturbed directories and create .txt.gz files
    
    # iterate over all perturbed directories
    for perturbed_instance in perturbed_instances:
        print(f"> Processing {perturbed_instance}")
        convert_to_txt(perturbed_instance)

    # tarball the stock data
    os.system(f'tar -czf {stock_dir}.tar.gz {stock_dir}')
    
    print("done.")
    
if __name__ == "__main__":
    main()
            