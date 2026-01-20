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

#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../misc"))
import mdutils
import json
import pandas as pd

__author__ = "Paul Meinhold"
__copyright__ = "Copyright 2024, Zuse Institute Berlin"

USAGE = "Usage: python json2mdtable.py <outfile>"
MD_HEADER = """
# Solutions
We only provide solutions up to size 6. 
GUROBI fails to solve dense instances of size 6 optimally within one hour. 

## Overview
"""

def get_data_from_json(jsonpath):
    """Loads a dictionary from a json file"""
    with open(jsonpath) as f:
        return json.load(f)

def extract_relevant(data):
    """Extract and return relevant info from solution data dictionary"""
    n = len(data.keys())
    new = mdutils.get_new_data(n)
    # Write instance names and solutions to new data
    for i, (num, d) in enumerate(data.items()):
        new[mdutils.KEY['I']][i] = num
        new[mdutils.KEY['S']][i] = str(d['k'])
        # If optimal, append \*
        if d["optimal"] == True:
            new[mdutils.KEY['S']][i] += "\\*"
    return new

def main():
    # Read user input
    if len(sys.argv) != 2:
        print(USAGE)
        sys.exit(1)
    outfile = os.path.normpath(sys.argv[1])
    # Get the solution directory path
    miscdir = os.path.dirname(os.path.realpath(__file__))
    parent = os.path.abspath(os.path.join(miscdir, os.pardir))
    soldir = os.path.join(parent, "solutions")
    # Start with the Markdown header
    md_string = MD_HEADER
    # Append wrapped Markdown table per json file 
    for file in os.listdir(soldir):
        # Only touch files with correct json extension
        root, ext = os.path.splitext(file)
        if ext != ".json":
            continue
        # Convert to Markdown table
        jsonpath = os.path.join(soldir, file)
        data = get_data_from_json(jsonpath)
        data = extract_relevant(data)
        # mdutils.fill_first_citation(data)
        md_table = mdutils.data_to_table(data)
        # Append table with header
        md_string += f"### {root}\n\n{md_table}\n\n"
    # Write
    mdutils.write_md(outfile, md_string)

if __name__ == "__main__":
    main()
