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
XML_FOLDER="./../../instances"  # The folder where .xml files are located
MISC_FOLDER="./../../misc"
LP_FOLDER="./lp_files"    # Temporary folder for .lp files
ZPL_FOLDER="./zpl_files"

# Set paths to other scripts and binary files
ITS2MIP="${MISC_FOLDER}/itc2mip.py"
ZIMPL="./../../../misc/zimpl-3.7.1.linux.x86_64.gnu.static.opt"

# Create necessary folders if they don't exist
mkdir -p "$LP_FOLDER"
mkdir -p "$ZPL_FOLDER"

# Find all .xml files in the current directory and its subdirectories
find $XML_FOLDER -type f -name "*.xml.gz" | while read -r file; do

    # remove prefix and suffix
    path="${file#"$XML_FOLDER"}"
    path="${path%.xml.gz}"

    # get basename of file
    basename="$(basename $path)"

    # create necessary subfolders
    sub_folder="${path%$basename}"
    mkdir -p $ZPL_FOLDER/$sub_folder
    mkdir -p $LP_FOLDER/$sub_folder

    output_zpl_file="${ZPL_FOLDER}/${path}.zpl"
    output_lp_file="${LP_FOLDER}/${path}"
    
    python $ITS2MIP --nosoft $file > $output_zpl_file
    $ZIMPL -t lp -o $output_lp_file $output_zpl_file

    # Compress the .lp file with xz
    echo "Compressing $output_lp_file.lp with xz"
    xz -z "$output_lp_file.lp"

    # Clean up auxiliary files
    rm "$output_lp_file.tbl"
done

# Clean up temporary folders
rm -r "$ZPL_FOLDER"

echo "Process complete! All .lp files are archived in $LP_FOLDER."
