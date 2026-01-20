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
QS_FOLDER="./qs_files"          # Temporary folder for .qs files

# Set paths to other scripts and binary files
MODEL="./indset_blp_unconst.zpl"
ZIMPL="./../../../misc/zimpl-3.7.1.linux.x86_64.gnu.static.opt"

# Create necessary folders if they don't exist
mkdir -p "$LP_FOLDER"
mkdir -p "$QS_FOLDER"

# Process all .csv files
for gph_file in "$GPH_FOLDER"/*.gph; do
    # Get the base name of the .csv file (without extension)
    basename=$(basename "$gph_file" .gph)
    
    # Process the .dat file to generate the .lp file
    lp_file="$LP_FOLDER/$basename"
    qs_file="$QS_FOLDER/$basename"
    echo "Generating $lp_file from $dat_file"
    
    # Run your command that generates .lp files from .dat files
    # For example: my_program is a placeholder for the actual command
    $ZIMPL -t lp -Dfilename="$gph_file" -o "$lp_file" $MODEL
    $ZIMPL -t q -Dfilename="$gph_file" -o "$qs_file" $MODEL

    # Compress the .lp file with xz
    echo "Compressing $lp_file.lp with xz"
    xz -z "$lp_file.lp"

    # Compress the .qs file with xz
    echo "Compressing $qs_file.qs with xz"
    xz -z "$qs_file.qs"

    # Clean up auxiliary files
    rm "$lp_file.tbl"
    rm "$qs_file.tbl"
done

echo "Process complete! All .lp files are archived in $LP_FOLDER and all .qs files are archived in $QS_FOLDER."
