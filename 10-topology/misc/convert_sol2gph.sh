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

# Check if the directory and Python script are provided
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <problem_specific_python_script> <directory>"
    exit 1
fi

# Get the directory and Python script from arguments
PYTHON_SCRIPT=$1
DIRECTORY=$2

# Check if the provided directory exists
if [ ! -d "$DIRECTORY" ]; then
    echo "Error: Directory '$DIRECTORY' does not exist."
    exit 1
fi

# Check if the Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: Python script '$PYTHON_SCRIPT' does not exist."
    exit 1
fi

# Loop through all files in the directory
for FILE in "$DIRECTORY"/*.sol; do
    # Skip directories and only process files
    if [ -f "$FILE" ]; then
        echo "Processing file: $FILE"
        python3 "$PYTHON_SCRIPT" -f "$FILE"
    fi
done
