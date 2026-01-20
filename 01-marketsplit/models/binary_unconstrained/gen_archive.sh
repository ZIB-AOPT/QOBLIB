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
DAT_FOLDER="./../../instances"  # The folder where .csv files are located
TXT_FOLDER="./txt_files"        # Temporary folder for .dat files
LP_FOLDER="./lp_files"          # Temporary folder for .lp files
QS_FOLDER="./qs_files"          # Temporary folder for .qs files

# Set paths to other scripts and binary files
MODEL="./marketsplit_bup.zpl"
ZIMPL="./../../../misc/zimpl-3.7.1.linux.x86_64.gnu.static.opt"
DAT2TXT="./../../misc/convert_dat2txt.awk"

# Create necessary folders if they don't exist
mkdir -p "$TXT_FOLDER"
mkdir -p "$LP_FOLDER"
mkdir -p "$QS_FOLDER"

# Function to convert .csv to .dat using an AWK script
convert_dat_to_txt() {
    local csv_file="$1"
    local dat_file="$2"

    awk -f $DAT2TXT "$csv_file" > "$dat_file"
}

# Process all .csv files
for dat_file in "$DAT_FOLDER"/*.dat; do
    # Get the base name of the .csv file (without extension)
    base_name=$(basename "$dat_file" .dat)
    
    # Define the .dat file path
    txt_file="$TXT_FOLDER/$base_name.txt"
    
    # Convert .csv to .dat
    echo "Converting $dat_file to $txt_file"
    convert_dat_to_txt "$dat_file" "$txt_file"
    
    # Process the .dat file to generate the .lp and .qs file
    lp_file="$LP_FOLDER/$base_name"
    qs_file="$QS_FOLDER/$base_name"
    echo "Generating $lp_file and $qs_file from $txt_file"
    
    # Generate .lp and .qs files
    $ZIMPL -t lp -Dfilename="$txt_file" -o "$lp_file" $MODEL
    $ZIMPL -t q -Dfilename="$txt_file" -o "$qs_file" $MODEL


    # Compress the generated files with xz
    echo "Compressing $lp_file.lp and $qs_file.qs with xz"
    xz -z "$lp_file.lp"
    xz -z "$qs_file.qs"
    
    # Clean up auxiliary files
    rm "$lp_file.tbl"
    rm "$qs_file.tbl"
done

# Clean up temporary folders
rm -r "$TXT_FOLDER"

echo "Process complete! All .lp files are archived in $output_archive_lp"
