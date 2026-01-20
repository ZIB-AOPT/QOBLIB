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

# Check if the directory is provided as an argument
if [ -z "$1" ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

# Directory containing the .sol files
DIRECTORY="$1"

# Loop through all .sol files in the directory
for FILE in "$DIRECTORY"/*.sol; do
    # Skip files that already have .opt.sol
    if [[ "$FILE" != *.opt.sol ]]; then
        # Rename the file to .bst.sol
        mv "$FILE" "${FILE%.sol}.bst.sol"
    fi
done
