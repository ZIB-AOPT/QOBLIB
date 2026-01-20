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
LP_FOLDER="./lp_files"    # Temporary folder for .lp files
QS_FOLDER="./qs_files"    # Temporary folder for .qs files

# Set the model and the ZIMPL executable
MODEL="./labs_bup.zpl"
ZIMPL="./../../../misc/zimpl-3.7.1.linux.x86_64.gnu.static.opt"

# Set which instances should be generated
START=2
END=100

# Create necessary folders if they don't exist
mkdir -p "$LP_FOLDER"
mkdir -p "$QS_FOLDER"

# Process all .csv files
for ((i=START; i<=END; i++)); do
    # Define the file name
    basename=$(printf "labs%03d" $i)
    
    lp_file="$LP_FOLDER/$basename"
    qs_file="$QS_FOLDER/$basename"

    echo "Generating $lp_file and $qs_file"
    
    # Run your command that generates .lp files from .dat files
    $ZIMPL -t lp -Dn="$i" -o "$lp_file" $MODEL
    $ZIMPL -t qs -Dn="$i" -o "$qs_file" $MODEL

    # Compress the .lp and .qs files with xz
    echo "Compressing $lp_file.lp and $qs_file.qs with xz"
    xz -z "$lp_file.lp"
    xz -z "$qs_file.qs"

    # Clean up auxiliary files
    rm "$lp_file.tbl"
    rm "$qs_file.tbl"
done

echo "Process complete! All .lp and .qs files are archived in $LP_FOLDER and $QS_FOLDER respectively."
