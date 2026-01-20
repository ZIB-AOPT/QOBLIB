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

import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance, entropy
from scipy.spatial.distance import jensenshannon
import matplotlib.pyplot as plt
import seaborn as sns
from numpy.linalg import norm
import os

def load_data(directory):
    file_path = os.path.join(directory, "combined_stock_data.csv")
    data = pd.read_csv(file_path, parse_dates=[0])
    return data

def compute_percentage_returns(data):
    return data.pct_change(fill_method=None)

def compute_js_divergence(returns1, returns2):
    hist1, _ = np.histogram(returns1.stack().dropna(), bins=50, density=True)
    hist2, _ = np.histogram(returns2.stack().dropna(), bins=50, density=True)
    return jensenshannon(hist1, hist2)

def compute_rolling_covariance(returns, window_size):
    return returns.rolling(window_size).corr()

def frobenius_norm_diff(cov_matrix1, cov_matrix2):
    return norm(cov_matrix1 - cov_matrix2, 'fro')

def plot_frobenius_norm_diffs(dates, norms, output_file):
    plt.figure(figsize=(10, 6))
    plt.scatter(dates, norms, marker='o')
    plt.title("Frobenius Norm Differences of Covariance Matrices Over Time")
    plt.xlabel("Date")
    plt.ylabel("Frobenius Norm Difference")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.savefig(output_file)

def plot_histogram_comparison(returns1, returns2, output_file):
    plt.figure(figsize=(10, 6))
    sns.histplot(returns1.stack().dropna(), kde=True, label="Original Data", color='blue')
    sns.histplot(returns2.stack().dropna(), kde=True, label="Perturbed Data", color='orange')
    plt.title("Comparison of Percentage Return Histograms")
    plt.xlabel("Percentage Return")
    plt.ylabel("Frequency")
    plt.legend()
    plt.savefig(output_file)

def plot_qq_plot(returns1, returns2, output_file):
    sorted_returns1 = np.sort(returns1.stack().dropna())
    sorted_returns2 = np.sort(returns2.stack().dropna())
    plt.figure(figsize=(10, 6))
    plt.plot(sorted_returns1, sorted_returns2, 'o', markersize=2)
    plt.plot([sorted_returns1.min(), sorted_returns1.max()], [sorted_returns1.min(), sorted_returns1.max()], 'r--')
    plt.title("QQ Plot of Percentage Returns")
    plt.xlabel("Original Data Quantiles")
    plt.ylabel("Perturbed Data Quantiles")
    plt.savefig(output_file)

def plot_qq_plot_norm(returns1, returns2, output_file):
    data_returns1 = returns1.stack().dropna().values
    data_returns2 = returns2.stack().dropna().values
    sorted_returns1 = np.sort(data_returns1)
    sorted_returns2 = np.sort(data_returns2)
    quantiles = np.linspace(0, 1, 100)
    q1 = np.quantile(sorted_returns1, quantiles)
    q2 = np.quantile(sorted_returns2, quantiles)
    plt.figure(figsize=(10, 6))
    plt.plot(q1, q2, 'o', markersize=3, alpha=0.7, label='Empirical Q–Q')
    min_val = min(q1[0], q2[0])
    max_val = max(q1[-1], q2[-1])
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', label='y = x')
    plt.title("Q–Q Plot of Percentage Returns")
    plt.xlabel("Quantiles of Original Data")
    plt.ylabel("Quantiles of Perturbed Data")
    plt.legend()
    plt.grid(True)
    plt.savefig(output_file)

def main(directory1, directory2):
    data1 = load_data(directory1)
    data2 = load_data(directory2)

    common_stocks = data1.columns.intersection(data2.columns)
    data1 = data1[common_stocks]
    data2 = data2[common_stocks]

    data1.set_index(data1.columns[0], inplace=True)
    data2.set_index(data2.columns[0], inplace=True)

    data1 = data1
    data2 = data2

    percentage_returns1 = compute_percentage_returns(data1)
    percentage_returns2 = compute_percentage_returns(data2)

    js_divergence = compute_js_divergence(percentage_returns1, percentage_returns2)
    print(f"Jensen-Shannon Divergence: {js_divergence:.4f}")

    rolling_window = 30
    rolling_cov1 = compute_rolling_covariance(percentage_returns1, rolling_window)
    rolling_cov2 = compute_rolling_covariance(percentage_returns2, rolling_window)

    rolling_cov_dates = rolling_cov1.dropna().index.levels[0][30:]
    frobenius_diffs = []

    for date in rolling_cov_dates:
        cov_matrix1 = rolling_cov1.loc[date]
        cov_matrix2 = rolling_cov2.loc[date]
        frobenius_diff = frobenius_norm_diff(cov_matrix1, cov_matrix2) / 50
        frobenius_diffs.append((date, frobenius_diff))

    dates, norms = zip(*frobenius_diffs)
    plot_frobenius_norm_diffs(dates, norms, "frobenius_norm_diff.png")
    plot_histogram_comparison(percentage_returns1, percentage_returns2, "histogram_comparison.png")
    plot_qq_plot(percentage_returns1, percentage_returns2, "qq_plot.png")
    plot_qq_plot_norm(percentage_returns1, percentage_returns2, "qq_plot_norm.png")

if __name__ == "__main__":
    # Replace with the actual directory paths
    directory1 = "./../../instances/new/po_a010_t10_s01"  # Replace with the actual directory path
    directory2 = "./../../instances/new/po_a010_t10_s00"  # Replace with the actual directory path
    main(directory1, directory2)
