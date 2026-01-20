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

# Convert provided instances in XML format to ZIMPL files to generate LPs.

# Check if two arguments are provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <path_to_directory>"
    exit 1
fi

if [ ! -d "$1" ]; then
    echo "$1 does not exist."
fi


# Find all .xml files in the current directory and its subdirectories
find $1 -type f -name "*.xml.gz" | while read -r file; do
    file_name_path="${file%.xml.gz}"
    output_zpl_file="${file_name_path}.zpl"
    
    python3 itc2mip.py --nosoft $file > $output_zpl_file
    zimpl -t lp -o $file_name_path $output_zpl_file
done