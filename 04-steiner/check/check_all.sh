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

#!/bin/sh
#MS03Mar2025
# sh check_all.sh
#

cd "$(dirname "$0")"

cargo build --release 

PASSED=0
FAILED=0
ERRORS=0

# Set folder paths
STP_FOLDER="./../instances"  # The folder where subfolders are located
SOLUTIONS="./../solutions"   

# Process all solution files
for solution in "$SOLUTIONS"/*.sol; do
    # Get the base name of the solution file
    basename=$(basename "$solution" .sol)
    basename=$(basename "$basename" .bst)
    basename=$(basename "$basename" .opt)
    
    # Define paths to arcs.dat and terms.dat
    arcs_file="$STP_FOLDER/$basename/arcs.dat"
    terms_file="$STP_FOLDER/$basename/terms.dat"
    
    # Check if all files exist
    if [ -f "$arcs_file" ] && [ -f "$terms_file" ]; then
        echo "Checking $basename..."

        OUTPUT=$(target/release/check_steiner --arcs "$arcs_file" --terms "$terms_file" --sol "$solution" 2>&1)
        EXIT_CODE=$?
        
        echo "$OUTPUT" | sed 's/^/  /'
        
        if [ $EXIT_CODE -eq 0 ]; then
            PASSED=$((PASSED+1))
        elif [ $EXIT_CODE -eq 1 ]; then
            FAILED=$((FAILED+1))
        else
            echo "  ERROR: Checker exited with code $EXIT_CODE"
            ERRORS=$((ERRORS+1))
        fi
    else
        echo "Skipping $solution: One or more required files not found"
    fi
done

echo ""
echo "Results: $PASSED passed, $FAILED failed, $ERRORS errors (total: $((PASSED + FAILED + ERRORS)))"
