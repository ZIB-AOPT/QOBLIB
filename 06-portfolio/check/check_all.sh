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
# Checks every curated solution under ../solutions against the instances.
# Solutions live under ../solutions/<instance-name>/*.sol; the instance
# directory is the subdirectory name, which matches instances/<name>/.

cargo build --release

PASSED=0
FAILED=0
ERRORS=0

for i in ../solutions/*/*.opt.sol ../solutions/*/*.bst.sol
do
    [ -e "$i" ] || continue
    NAME=`basename $i`
    # The parent directory name is the instance name (e.g. po_a010_t10_orig).
    INST_NAME=`basename $(dirname $i)`
    INST_DIR="../instances/$INST_NAME"
    echo "Checking $NAME..."

    OUTPUT=$(target/release/check_portfolio "$INST_DIR" "$i" 2>&1)
    EXIT_CODE=$?

    echo "$OUTPUT" | sed 's/^/  /'

    if [ $EXIT_CODE -eq 0 ]; then
        PASSED=$((PASSED+1))
    elif [ $EXIT_CODE -eq 21 ] || [ $EXIT_CODE -eq 20 ]; then
        FAILED=$((FAILED+1))
    else
        echo "  ERROR: Checker exited with code $EXIT_CODE"
        ERRORS=$((ERRORS+1))
    fi
done

echo ""
echo "Results: $PASSED passed, $FAILED failed, $ERRORS errors (total: $((PASSED + FAILED + ERRORS)))"
