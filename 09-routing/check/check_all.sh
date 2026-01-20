#!/bin/bash

# This file is part of QOBLIB - Quantum Optimization Benchmarking Library
# Licensed under the Apache License, Version 2.0

# Script to check all CVRP solutions

INSTANCE_DIR="../instances"
SOLUTION_DIR="../solutions"
CHECKER="./target/release/check_cvrp"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Build the checker if needed
if [ ! -f "$CHECKER" ]; then
    echo "Building checker..."
    cargo build --release
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to build checker${NC}"
        exit 1
    fi
fi

# Counters
total=0
valid=0
invalid=0
missing=0

# Find all instance files
for solution in "$SOLUTION_DIR"/*.sol; do
    if [ ! -f "$solution" ]; then
        continue
    fi

    echo "Checking: $basename..."
    
    # Get instance basename
    basename=$(basename "$solution" .sol)
    basename=$(basename "$basename" .opt)
    basename=$(basename "$basename" .bst)
    
    # Find matching instance
    instance=""
    if [ -f "$INSTANCE_DIR/${basename}.vrp" ]; then
        instance="$INSTANCE_DIR/${basename}.vrp"
    fi
    
    # Skip if no instance file found
    if [ -z "$instance" ]; then
        echo -e "  MISSING:${NC} $basename (no instance file)"
        ((missing++))
        ((total++))
        continue
    fi
    
    # Run checker
    output=$("$CHECKER" "$instance" "$solution" 2>&1)
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo "$output" | sed 's/^/  /'
        # echo -e "  VALID:${NC} $basename"
        ((valid++))
    elif [ $exit_code -eq 1 ]; then
        echo -e "  INVALID:${NC} $basename"
        echo "$output" | sed 's/^/  /'
        ((invalid++))
    else
        echo "$output" | sed 's/^/  /'
        echo -e "  ERROR:${NC} $basename (exit code $exit_code)"
        ((invalid++))
    fi
    
    ((total++))
    echo ""
done

# Print summary
echo "================================================"
echo "Summary:"
echo "================================================"
echo "Total instances: $total"
echo -e "Valid solutions: $valid${NC}"
echo -e "Invalid solutions: $invalid${NC}"
echo -e "Missing solutions: $missing${NC}"
echo ""

if [ $invalid -gt 0 ]; then
    exit 1
else
    exit 0
fi
