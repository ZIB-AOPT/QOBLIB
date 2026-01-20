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
#TK27Dec2024
# sh check_all.sh
#
cargo build --release 

PASSED=0
FAILED=0
ERRORS=0

for i in ../solutions/*.opt.sol
do
    NAME=`basename $i .opt.sol`
    echo "Checking $NAME..."

    OUTPUT=$(target/release/check_marketsplit ../instances/$NAME.dat $i 2>&1)
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
