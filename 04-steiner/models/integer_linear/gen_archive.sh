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

# Skript can be used in the following way:
# ./gen_archive.sh [size_filter]
# where size_filter is an optional argument to filter instance sizes.
# It can be a single size (e.g., 5), a comma-separated list of sizes (e.g., 4,6),
# or a regex pattern (e.g., ^(4|6)$) to match specific sizes.

# Set the execution directory to the directory the script is in
cd "$(dirname "$0")"

# Set folder paths
STP_FOLDER="./../../instances"  # The folder where subfolders are located
LP_FOLDER="./lp_files"    # Temporary folder for .lp files

# Define the model and ZIMPL executable
MODEL="./stp_node_disjoint.zpl"
ZIMPL="./../../../misc/zimpl-3.7.1.linux.x86_64.gnu.static.opt"

# Optional argument for instance size filtering (supports comma-separated values or regex)
SIZE_FILTER=$1

# Create necessary folders if they don't exist
mkdir -p "$LP_FOLDER"

# Process all subfolders
for folder in "$STP_FOLDER"/*/; do
    # Get the base name of the folder
    basename=$(basename "$folder")

    # extract the instance size from the name stp_s<size>_l<layers>_t<terminals>_h<holes>_rs<seed>
    size=$(echo "$basename" | sed -n 's/stp_s\([0-9]*\)_l[0-9]*_t[0-9]*_h[0-9]*_rs[0-9]*/\1/p')
    
    # Strip leading zeros for numeric comparison
    size_numeric=$((10#$size))

    # If SIZE_FILTER is set, check if size matches
    if [[ -n "$SIZE_FILTER" ]]; then
        match=false
        # Check if filter contains comma (multiple values)
        if [[ "$SIZE_FILTER" == *,* ]]; then
            # Split by comma and check each value
            IFS=',' read -ra SIZES <<< "$SIZE_FILTER"
            for filter_size in "${SIZES[@]}"; do
                filter_size_numeric=$((10#$filter_size))
                if [[ "$size_numeric" -eq "$filter_size_numeric" ]]; then
                    match=true
                    break
                fi
            done
        else
            # Try numeric comparison first, fall back to regex if it fails
            if [[ "$SIZE_FILTER" =~ ^[0-9]+$ ]]; then
                # It's a number, do numeric comparison
                filter_size_numeric=$((10#$SIZE_FILTER))
                if [[ "$size_numeric" -eq "$filter_size_numeric" ]]; then
                    match=true
                fi
            elif [[ "$size" =~ ^${SIZE_FILTER}$ ]]; then
                # It's a regex pattern
                match=true
            fi
        fi
        
        if [[ "$match" == false ]]; then
            echo "Skipping folder $folder due to size filter"
            continue
        fi
    fi
    
    # Define paths to arcs.dat, param.dat, roots.dat, and terms.dat
    arcs_file="$folder/arcs.dat"
    param_file="$folder/param.dat"
    roots_file="$folder/roots.dat"
    terms_file="$folder/terms.dat"
    
    # Check if all files exist
    if [[ -f "$arcs_file" && -f "$param_file" && -f "$roots_file" && -f "$terms_file" ]]; then
        # Define output file
        lp_file="$LP_FOLDER/$basename"
        echo "Generating $lp_file from $arcs_file, $param_file, $roots_file, and $terms_file"
        
        # Run ZIMPL command
        $ZIMPL -t lp -Darcs_file="$arcs_file" -Dparam_file="$param_file" -Droots_file="$roots_file" -Dterms_file="$terms_file" -o "$lp_file" $MODEL

        # Compress the .lp file with xz
        echo "Compressing $lp_file.lp with xz"
        xz -z "$lp_file.lp"

        # Clean up auxiliary files
        rm "$lp_file.tbl"
    else
        echo "Skipping folder $folder: One or more required files not found"
    fi
done

echo "Process complete! All .lp files are archived in $LP_FOLDER"
