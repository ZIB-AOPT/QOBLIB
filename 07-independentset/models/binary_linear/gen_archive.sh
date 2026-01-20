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
GPH_FOLDER="./../../instances"  # The folder where .gph files are located
LP_FOLDER="./lp_files"    # Temporary folder for .lp files

# Set paths to other scripts and binary files
MODEL="./indset_blp.zpl"
ZIMPL="./../../../misc/zimpl-3.7.1.linux.x86_64.gnu.static.opt"

# Create necessary folders if they don't exist
mkdir -p "$LP_FOLDER"

# Process all .csv files
for gph_file in "$GPH_FOLDER"/*.gph; do
    # Get the base name of the .csv file (without extension)
    basename=$(basename "$gph_file" .gph)
    
    # Process the .gph file to generate the .lp file
    lp_file="$LP_FOLDER/$basename"
    echo "Generating $lp_file from $gph_file"
    
    # Run your command that generates .lp files from .gph files
    # For example: my_program is a placeholder for the actual command
    $ZIMPL -t lp -Dfilename="$gph_file" -o "$lp_file" $MODEL

    # Compress the .lp file with xz
    echo "Compressing $lp_file.lp with xz"
    xz -z "$lp_file.lp"

    # Clean up auxiliary files
    rm "$lp_file.tbl"
done

echo "Process complete! All .lp files are archived in $LP_FOLDER."
