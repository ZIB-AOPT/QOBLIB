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

# Set folder paths
DAT_FOLDER="./../../instances"  # The folder where .gph files are located
LP_FOLDER="./lp_files"    # Temporary folder for .lp files

# Set paths to other scripts and binary files
MODEL="./topology_flow.zpl"
ZIMPL="./../../../misc/zimpl-3.7.1.linux.x86_64.gnu.static.opt"

# Create necessary folders if they don't exist
mkdir -p "$LP_FOLDER"

# Process all .csv files
for dat_file in "$DAT_FOLDER"/topology_[0-9][0-9]_*.dat; do
    # Get the base name of the .csv file (without extension)
    basename=$(basename "$dat_file" .dat)
    
    # Process the .dat file to generate the .lp file
    lp_file="$LP_FOLDER/$basename"
    echo "Generating $lp_file from $dat_file"
    
    # Run your command that generates .lp files from .dat files
    # For example: my_program is a placeholder for the actual command
    $ZIMPL -t lp -Dfilename="$dat_file" -o "$lp_file" $MODEL

    # Compress the .lp file with xz
    echo "Compressing $lp_file.lp with xz"
    xz -z "$lp_file.lp"

    # Clean up auxiliary files
    rm "$lp_file.tbl"
done

echo "Process complete! All .lp files are archived in $LP_FOLDER"
