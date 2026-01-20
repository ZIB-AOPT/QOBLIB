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

# This script generates permutation data files using ZIMPL for sizes from START to END.

#!/bin/bash

# Set the execution directory to the directory the script is in
cd "$(dirname "$0")"

# Set paths to other scripts and binary files
ZIMPL="./../../misc/zimpl-3.7.1.linux.x86_64.gnu.static.opt"
GEN_PERM="./permutation.zpl"

START=$1
END=$2

# If no arguments are given, default to sizes 3 to 6
if [ -z "$START" ] || [ -z "$END" ]; then
    START=3
    END=6
fi

# Generate permutation data files for sizes from START to END
for i in $(seq $START $END); do
    i_formatted=$(printf "%02d" $i)
    perm_file="./zimpl_p${i_formatted}"
    txt_file="./zimpl_p${i_formatted}.dat"
    
    output=$($ZIMPL -t data -Dmsize=$i -o $perm_file $GEN_PERM 2>&1)
    
    # Extract the line containing the permutations
    perm_line=$(echo "$output" | grep "Multi: |$i|")
    
    # Extract permutations between { and }, then split by commas and extract each <...>
    if [ -n "$perm_line" ]; then
        echo "Extracting permutations to $txt_file"
        # Extract content between { and }
        perms=$(echo "$perm_line" | sed 's/.*{\(.*\)}.*/\1/')
        # Replace >,< with newline to separate permutations, then remove < and >, and replace commas with spaces
        echo "$perms" | sed 's/>,</>\n</g' | sed 's/[<>]//g' | sed 's/,/ /g' > "$txt_file"
    fi

    # remove generated .lp and .tbl file
    rm -f "${perm_file}.lp" "${perm_file}.tbl"
done 