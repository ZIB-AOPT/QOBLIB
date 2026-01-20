#!/bin/bash

# Iterate over all .gph files in the ./../instances/ directory
for file in ./../instances/*.gph; do
    echo "Processing file: $file"

    # Run the Python script on each file
    python validate_graph.py "$file"
done