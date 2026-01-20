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
# sh check_all.sh
#
cargo build --release

PASSED=0
FAILED=0
ERRORS=0

for i in ../solutions/*.gph
do
    # Skip if file doesn't exist
    [ -e "$i" ] || continue
    
    # Get base filename and extract parameters
    BASENAME=$(basename "$i" .gph)
    BASENAME=$(basename "$BASENAME" .opt)
    BASENAME=$(basename "$BASENAME" .bst)
    
    # Extract node_count and max_degree from filename
    # Format: topology_<nodes>_<degree>
    NODES=$(echo "$BASENAME" | sed 's/topology_\([0-9]*\)_\([0-9]*\).*/\1/')
    DEGREE=$(echo "$BASENAME" | sed 's/topology_\([0-9]*\)_\([0-9]*\).*/\2/')
    
    # Skip instances with more than 1000 nodes for computational reasons
    if [ "$NODES" -gt 1000 ]; then
        echo "Skipping $BASENAME (too large: $NODES nodes)"
        continue
    fi
    
    # Try to read diameter from first few comment lines in the file
    # Format: "c Undirected Graph with Diameter 3"
    DIAMETER=$(head -n 5 "$i" | grep -i '^c.*diameter' | grep -o '[0-9]\+' | tail -n 1)
    
    # If diameter not found in file, use a large default value
    if [ -z "$DIAMETER" ]; then
        DIAMETER=999999
    fi
    
    echo "Checking $BASENAME (nodes=$NODES, degree=$DEGREE, diameter=$DIAMETER)..."
    
    OUTPUT=$(target/release/check_topology "$NODES" "$DEGREE" "$DIAMETER" "$i" 2>&1)
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
done

echo ""
echo "Results: $PASSED passed, $FAILED failed, $ERRORS errors (total: $((PASSED + FAILED + ERRORS)))"
