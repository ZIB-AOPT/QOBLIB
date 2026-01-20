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

# Set the model and the ZIMPL executable
MODEL="./labs_ip.zpl"
ZIMPL="./../../../misc/zimpl-3.7.1.linux.x86_64.gnu.static.opt"

# Set which instances should be generated
START=2
END=100

# Create necessary folders if they don't exist
mkdir -p "$LP_FOLDER"

# Process all .csv files
for ((i=START; i<=END; i++)); do
    # Define the file name
    basename=$(printf "labs%03d" $i)
    
    lp_file="$LP_FOLDER/$basename"

    echo "Generating $lp_file"
    
    # Run your command that generates .lp files from .dat files
    $ZIMPL -t lp -Dn="$i" -o "$lp_file" $MODEL

    # Compress the .lp file with xz
    echo "Compressing $lp_file.lp with xz"
    xz -z "$lp_file.lp"

    # Clean up auxiliary files
    rm "$lp_file.tbl"
done

echo "Process complete! All .lp files are archived in $LP_FOLDER."
