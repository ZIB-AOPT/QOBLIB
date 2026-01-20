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
from pathlib import Path
import pandas as pd
import numpy as np

def perturb_returns_and_generate_prices(data: pd.DataFrame, window_size=30, seed: int = 42) -> pd.DataFrame:
    """
    Perturb the returns (percentage differences) of stock prices and regenerate prices.
    
    Parameters:
        data (pd.DataFrame): The original stock price DataFrame with a 'Adj Close' column.
        perturbation_factor (float): The maximum percentage perturbation to apply to returns.
        seed (int): The random seed for reproducibility.
    
    Returns:
        pd.DataFrame: A DataFrame containing the original and perturbed prices.
    """    
    # Set the random seed for reproducibility
    np.random.seed(seed)
    
    # Compute the possible date range for the perturbed prices
    # The first date is the first date after the rolling window
    start_date = pd.Timestamp(data.index[window_size])
    start_final = pd.Timestamp(data.index[2 * window_size])
    end_date = pd.Timestamp(data.index.max())
    
    # Filter the data by date range
    mask = (data.index >= start_date) & (data.index <= end_date)
        
    # Filter the data by date range
    # Compute the returns (percentage changes)
    returns = data.pct_change(fill_method=None)

    # Generate perturbed returns
    # Draw samples from a multinomial distribution with the given covariance matrix
    rolling_returns = returns.rolling(window=window_size)
    
    print("> Computing rolling means and covariances")
    # We mask the covariance matrices and means that don't have enough data
    rolling_cov_matrices = rolling_returns.cov()
    mean_returns = rolling_returns.mean()[mask]
    std_returns = rolling_returns.std()[mask]
    
    # Workaround because of multiindex
    mask_cov = (rolling_cov_matrices.index.get_level_values(0) >= start_date) & (
        rolling_cov_matrices.index.get_level_values(0) <= end_date
    )
    rolling_cov_matrices = rolling_cov_matrices[mask_cov]
    
    # Create a DataFrame to store the perturbed returns
    perturbed_returns = pd.DataFrame(index=returns[mask].index, columns=returns.columns)
    
    print("> Computing perturbed returns by sampling normal-t distribution")
    for idx in perturbed_returns.index:
        cov_matrix = rolling_cov_matrices.loc[idx]
        mean_return = mean_returns.loc[idx]
        std_return = std_returns.loc[idx]

        # Check for NaN or infinite values in the covariance matrix
        if cov_matrix.isnull().values.any() or np.isinf(cov_matrix.values).any():
            # print which stock has NaN values
            print(idx, len(cov_matrix.columns[cov_matrix.isnull().any()]))
            for i in range(cov_matrix.shape[0]):
                for j in range(cov_matrix.shape[1]):
                    if np.isnan(cov_matrix.iloc[i, j]):
                        print(cov_matrix.columns[i], cov_matrix.columns[j])
                # print(cov_matrix.iloc[i])
            # print(cov_matrix[:20])
            print("> W: Matrix had NaN on inf entries - replaced by 0")
            cov_matrix = np.nan_to_num(cov_matrix)
        
        # Generate perturbed returns
        # perturbed_returns.loc[idx] = np.random.standard_t(df=10, size=len(mean_return)) * np.sqrt((10 - 2) / 10) @ np.linalg.cholesky(cov_matrix).T + mean_return

        # Ensure the covariance matrix is positive definite
        epsilon = 1e-9  # Small value to add to the diagonal
        cov_matrix += np.eye(cov_matrix.shape[0]) * epsilon
        # eigvals, eigvecs = np.linalg.eigh(cov_matrix)
        # eigvals[eigvals < 0] = 1e-9  # Set any negative eigenvalues to a small positive value
        # cov_matrix = eigvecs @ np.diag(eigvals) @ eigvecs.T
        
        df = 5  # Degrees of freedom for the t-distribution
        base_draw = np.random.standard_t(df=df, size=len(mean_return)) * np.sqrt((df - 2) / df) @ np.linalg.cholesky(cov_matrix).T + mean_return
        perturbed_returns.loc[idx] = base_draw

        # Introduce outliers on a stock-by-stock basis
        for stock_name in perturbed_returns.columns:
            # Base chance of outlier (could vary by asset class, regime, or volatility)
            base_chance = 0.01
            
            # If the return is near or below mean (within 0.1 std),
            # you might slightly increase chance (mimicking more frequent "bad surprises")
            deviation_in_std = abs((perturbed_returns.loc[idx, stock_name] - mean_return[stock_name]) / std_return[stock_name])
            if deviation_in_std < 0.25:
                base_chance = 0.03
            
            # Check if we generate an outlier
            if np.random.rand() < base_chance:
                # Decide direction and magnitude of outlier
                # Here, we assume more probability of large negative jumps (financial "shocks").
                shock_direction = np.random.choice([1, -1], p=[0.4, 0.6])
                
                # If negative, typically bigger in magnitude than positive
                # (You can tweak these ranges or distributions to suit your model.)
                if shock_direction == -1:
                    outlier_factor = np.random.exponential(scale=1) + 1  # Larger negative swings
                else:
                    outlier_factor = np.random.exponential(scale=1) + 1  # Smaller positive swings
                
                # Convert the baseline deviation to a more extreme outlier
                # and scale it back to the original returns scale
                new_perturbed_return = mean_return[stock_name] + deviation_in_std * outlier_factor * shock_direction
                perturbed_returns.loc[idx, stock_name] = new_perturbed_return * std_return[stock_name]
        
    # Regenerate prices from perturbed returns
    perturbed_prices = pd.DataFrame(index=data[mask].index, columns=data.columns)
    perturbed_prices.loc[start_final] = data.loc[start_final]  # Prices on the 30th day remain the same

    print("> Computing prices from returns")
    # Compute the perturbed prices forward
    for i in range(31, len(perturbed_prices)):
        perturbed_prices.iloc[i] = perturbed_prices.iloc[i - 1] * (1.0 + perturbed_returns.iloc[i])
    
    # Compute the perturbed prices backward
    for i in range(29, -1, -1):
        perturbed_prices.iloc[i] = perturbed_prices.iloc[i + 1] / (1.0 + perturbed_returns.iloc[i + 1])

    return perturbed_prices, mask

def generate_daily_covariance_matrices(instance_dir: Path, time_interval: int = 10, window_size: int = 30) -> None:
    """
    Generate daily covariance matrices from historical stock prices.

    Parameters:
        input_dir (str): The directory containing the stock prices data.
        output_dir (str): The directory to save the output in.
        window_size (int): The size of the rolling window to use when computing the covariance matrices.

    Returns:
        None
    """
    input_path = os.path.join(instance_dir, "combined_stock_data.csv")

    # Load stock prices
    # prices_file = os.path.join(input_path, "prices.csv")
    prices_df = pd.read_csv(input_path, parse_dates=["Date"], index_col="Date")

    # Compute returns
    returns_df = prices_df.pct_change(fill_method=None)#.dropna()

    # Compute rolling covariance matrices
    rolling_cov_matrices = returns_df.rolling(window=window_size).cov()

    # Filter the covariance matrices by date range
    start_date = pd.Timestamp(prices_df.index[window_size])
    end_date = pd.Timestamp(prices_df.index.max())
    
    mask = (rolling_cov_matrices.index.get_level_values(0) >= start_date) & (
        rolling_cov_matrices.index.get_level_values(0) <= end_date
    )
    filtered_rolling_cov_matrices = rolling_cov_matrices[mask]

    # Filter prices and returns by date
    mask = (prices_df.index >= start_date) & (prices_df.index <= end_date)
    prices_df = prices_df.loc[mask]
    returns_df = returns_df.loc[mask]

    # Create output directory
    output_path_cov = os.path.join(instance_dir, "future_covariance_matrices")
    os.makedirs(output_path_cov, exist_ok=True)

    # Save the filtered stock prices and returns to a directory
    prices_df.iloc[:time_interval].to_csv(os.path.join(instance_dir, "stock_prices.csv"))
    returns_df.iloc[:time_interval].to_csv(os.path.join(instance_dir, "future_daily_returns.csv"))

    # Save the filtered covariance matrices to a directory
    for date, cov_matrix in list(filtered_rolling_cov_matrices.groupby(level=0))[:time_interval]:
        cov_matrix = cov_matrix.reset_index(level=0, drop=True)
        output_file = os.path.join(output_path_cov, f"cov_matrix_{date.date()}.csv")
        cov_matrix.to_csv(output_file)
        
    print(f"> Instance Data written to {instance_dir}")
