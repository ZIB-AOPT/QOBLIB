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
JSON_FOLDER="./../../instances"  # The folder where .json files are located
MISC_FOLDER="./../../misc"
DAT_FOLDER="./dat_files"  # Temporary folder for .dat files
LP_FOLDER="./lp_files"    # Temporary folder for .lp files

# Set paths to other scripts and binary files
ZIMPL="./../../../misc/zimpl-3.7.1.linux.x86_64.gnu.static.opt"
JSON2DAT="./../../misc/parse_matrices.py"
# GENPERM="${MISC_FOLDER}/genperm"

# Define which siyes should be generated
# Note that for this formuation, the size increases factorially
START=3
END=6

# Create necessary folders if they don't exist
mkdir -p "$DAT_FOLDER"
mkdir -p "$LP_FOLDER"

# Function to convert .json to .dat using an python script
convert_json_to_dat() {
    local i="$1"

    python $JSON2DAT $JSON_FOLDER/qbench_${i}_dense.json $i $DAT_FOLDER/bhD-${i}
    python $JSON2DAT $JSON_FOLDER/qbench_${i}_sparse.json $i $DAT_FOLDER/bhS-${i}
}

for i in $(seq $START $END); do
    i=$(printf "%02d" $i)
    convert_json_to_dat $i

    mkdir ${LP_FOLDER}/bhD-${i}
    mkdir ${LP_FOLDER}/bhS-${i}

    # Set scale to 1000 if $i = 3 otherwise 10_000

    if [ "$i" -eq 3 ]; then
        SCALE=1000
    else
        SCALE=10000
    fi

    # Convert dense matrices
    for inst in ${DAT_FOLDER}/bhD-$i/bhD-$i-*.dat
    do
        basename=`basename $inst .dat`
        lp_file="${LP_FOLDER}/bhD-${i}/${basename}"

        $ZIMPL -t lp -Dfilename=$inst -Dmsize=$i -Dssize=$SCALE -o "$lp_file" ./birkhoff_ilp.zpl

        # Compress the .lp file with xz
        echo "Compressing $lp_file.lp with xz"
        xz -z "$lp_file.lp"

        # Clean up auxiliary files
        rm "$lp_file.tbl"
    done

    # Convert sparse matrices
    for inst in ${DAT_FOLDER}/bhS-$i/bhS-$i-*.dat
    do
        basename=`basename $inst .dat`
        lp_file="${LP_FOLDER}/bhS-${i}/${basename}"

        $ZIMPL -t lp -Dfilename=$inst -Dmsize=$i -Dssize=$SCALE -o $lp_file ./birkhoff_ilp.zpl

        # Compress the .lp file with xz
        echo "Compressing $lp_file.lp with xz"
        xz -z "$lp_file.lp"

        # Clean up auxiliary files
        rm "$lp_file.tbl"
    done
done


# Clean up temporary folders
rm -r "$DAT_FOLDER"

# Binary should not be pushed
rm "$GENPERM"

echo "Process complete! All .lp files are archived in $LP_FOLDER."
