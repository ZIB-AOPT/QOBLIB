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

#!/bin/bash

# Set the execution directory to the directory the script is in
cd "$(dirname "$0")"

# User-defined paths
DATA_DIR="./../../instances" # Replace with your data directory path
LP_FILES="./lp_files" # Replace with your LP files directory

# Define the ZIMPL model files
ZIMPL_EXEC="./../../../misc/bin/zimpl-3.7.1.linux.x86_64.gnu.static.opt"
MODEL_DIR="./"    # Replace with your ZIMPL model directory
BQP_MODEL="bqp_u3_c10.zpl"

# Create necessary directories, you may change the path
mkdir -p "$LP_FILES"

# Define the array of lambda values
lambda_values=(0 0.000001 0.00001 0.00005 0.0001 0.0005 0.001 0.01)

# Loop over all data directories matching the specified pattern
for data_dir in "$DATA_DIR"/po_a0*; do
  if [ -d "$data_dir" ]; then
    dir_name=$(basename "$data_dir")

    # Extract a, t and s information from the directory name
    if [[ "$dir_name" =~ _a([0-9]{3})_t([0-9]{2})_(s[0-9]{2}|orig) ]]; then
      a=$(echo "${BASH_REMATCH[1]}" | sed 's/^0*//')
      t="${BASH_REMATCH[2]}"
      s="${BASH_REMATCH[3]}"
    fi

    echo "Processing directory: $dir_name with $a assets, $t time periods, and seed $s"

    # Set the paths to the stock price data and covariance data
    stock_price_data="$data_dir/stock_prices.txt.gz"
    covariance_data="$data_dir/covariance_matrices.txt.gz"

    # Three-level loops over (a, t, q)
    # Determine B based on a
    # Determine B based on a using a more flexible approach
    case "$a" in
      10) B=4 ;;
      50) B=20 ;;
      200) B=50 ;;
      400) B=100 ;;
      *)
      echo "Warning: Unhandled number of assets ($a). Defaulting B to 0."
      B=0
      ;;
    esac

    for lambda in "${lambda_values[@]}"; do
      echo "Running with a=$a, t=$t, lambda=$lambda, B=$B"

      a_padded=$(printf "%03d" "$a")
      b_padded=$(printf "%03d" "$B")

      SUB_DIR="a${a_padded}_t${t}_${s}_b${b_padded}"

      mkdir -p "$LP_FILES/$SUB_DIR"

      # Normalise lambda to a dot-free token (e.g. 0.0001 -> l1e-4)
      case "$lambda" in
        0)        lambda_tag="l0" ;;
        0.000001) lambda_tag="l1e-6" ;;
        0.00001)  lambda_tag="l1e-5" ;;
        0.00005)  lambda_tag="l5e-5" ;;
        0.0001)   lambda_tag="l1e-4" ;;
        0.0005)   lambda_tag="l5e-4" ;;
        0.001)    lambda_tag="l1e-3" ;;
        0.01)     lambda_tag="l1e-2" ;;
        *)        lambda_tag="l${lambda}" ;;
      esac

      base_filename="bqp_a${a_padded}_t${t}_${s}_b${b_padded}_${lambda_tag}"

      lp_file="${LP_FILES}/${SUB_DIR}/${base_filename}"

      # Generate LP model files using ZIMPL, passing a, t, lambda, B
      $ZIMPL_EXEC \
        -Dnum_assets="$a" \
        -Dtime_intervals="$t" \
        -Dlambda="$lambda" \
        -DB="$B" \
        -Dstock_price="$stock_price_data" \
        -Dstock_covariance="$covariance_data" \
        -o "$lp_file" \
        "$MODEL_DIR/$BQP_MODEL"

      
      # Compress the .lp file with xz
      echo "Compressing $lp_file.lp with xz"
      xz -z "$lp_file.lp"

      # Clean up auxiliary files
      rm "$lp_file.tbl"

    done
  fi
done

echo "Process complete! All .lp files are archived in $LP_FILES"
