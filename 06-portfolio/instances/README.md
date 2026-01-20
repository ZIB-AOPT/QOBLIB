# Instances for Portfolio

The model inputs consist of **price** and **covariance** data. We provide price and covariance information for various subsets of stocks, selected from the S&P 500 stocks, across multiple time periods. The stocks are chosen based on their market capitalization, including the top 10, top 50, top 200, and top 400 stocks. All data files are provided in compressed text format (`.txt.gz`).

## Price Data

**Example:** `po_a200_t15_orig/stock_prices.txt.gz`

Each line in the `stock_prices.txt.gz` file contains three elements:
1. The day index
2. The stock symbol
3. The stock’s price on that day

## Covariance Data

**Example:** `po_a200_t15_orig/covariance_matrices.txt.gz`

Each line in the `covariance_matrices.txt.gz` file contains four elements:
1. The day index
2. Stock symbol 1
3. Stock symbol 2
4. The return covariance between these two stocks on that day

## Instance Generation

All instances can be generated using the `main.py` script located in the `misc/instance_generation` directory. 
Ti generate more instances, adjust the parameters in the main function in th [main file](./../misc/instance_generation/main.py).
