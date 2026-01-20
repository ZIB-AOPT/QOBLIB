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
# Usage: ./check_all.sh

cargo build --release

PASSED=0
FAILED=0
ERRORS=0

# Path to demand matrix file
DEMAND_FILE="../instances/demand.txt"

if [ ! -f "$DEMAND_FILE" ]; then
    echo "ERROR: Demand file not found at $DEMAND_FILE"
    exit 2
fi

for solution_file in ../solutions/*.sol
do
    BASENAME=$(basename "$solution_file" .opt.sol)
    BASENAME=$(basename "$BASENAME" .bst.sol)
    
    # Extract the number from the filename (e.g., network05 -> 05 -> 5)
    if [[ $BASENAME =~ network([0-9]+) ]]; then
        INSTANCE_SIZE="${BASH_REMATCH[1]}"
        # Remove leading zeros
        INSTANCE_SIZE=$((10#$INSTANCE_SIZE))
    else
        echo "Skipping $BASENAME: Cannot extract instance size from filename"
        continue
    fi
    
    echo "Checking $BASENAME (size $INSTANCE_SIZE)..."
    
    OUTPUT=$(target/release/check_network "$INSTANCE_SIZE" "$DEMAND_FILE" "$solution_file" 2>&1)
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
    echo ""
done

echo "================================"
echo "Summary:"
echo "  Passed: $PASSED"
echo "  Failed: $FAILED"
echo "  Errors: $ERRORS"
echo "================================"

if [ $FAILED -gt 0 ] || [ $ERRORS -gt 0 ]; then
    exit 1
else
    exit 0
fi
