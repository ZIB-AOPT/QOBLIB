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

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <source_directory> <destination_directory>"
    exit 1
fi

SOURCE_DIR=$1
DEST_DIR=$2

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Source directory does not exist."
    exit 1
fi

# Check if destination directory exists, if not create it
if [ ! -d "$DEST_DIR" ]; then
    mkdir -p "$DEST_DIR"
fi

# Loop through all directories in the source directory
for dir in "$SOURCE_DIR"/*; do
    if [ -d "$dir" ]; then
        dir_name=$(basename "$dir")
        new_dir="$DEST_DIR/$dir_name"

        # Create the new directory in the destination directory
        mkdir -p "$new_dir"

        # Copy the specified files to the new directory
        cp "$dir/covariance_matrices.txt.gz" "$new_dir/"
        cp "$dir/stock_prices.txt.gz" "$new_dir/"

        # Delete the original directory
        rm -rf "$dir"
    fi
done

if [ -d "./stock_data_2024-01-01_2024_05-31/" ]; then
    rm -rf ./stock_data_2024-01-01_2024_05-31/
fi