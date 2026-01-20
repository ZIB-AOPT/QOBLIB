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
__author__ = "Paul Meinhold"

import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../misc"))
import mdutils

USAGE = "Usage: python sol2mdtable.py <outfile>"
MD_HEADER = """
# Solutions
All problems we provide solutions for are feasible. Others have to be checked.

Their objective value is always 0 because we encode feasibility in the objective
function.

## Overview
"""

def main():
    # Read user input
    if len(sys.argv) != 2:
        print(USAGE)
        sys.exit(1)
    outfile = os.path.normpath(sys.argv[1])
    # Get the solutions and instances directory path
    miscdir = os.path.dirname(os.path.realpath(__file__))
    parent = os.path.abspath(os.path.join(miscdir, os.pardir))
    soldir = os.path.join(parent, "solutions")
    instdir = os.path.join(parent, "instances")
    # Extract actual instances with csv extension
    instances = [
        inst for inst in os.listdir(instdir)
        if os.path.splitext(inst)[1] == ".csv" ]
    instances.sort()
    solutions = os.listdir(soldir) 
    data = mdutils.get_new_data(len(instances))
    mdutils.fill_first_citation(data)
    # For each instance check what to write into Markdown table
    for i, file in enumerate(instances):
        root, ext = os.path.splitext(file)
        data[mdutils.KEY['I']][i] = root
        if root + ".opt.sol" in solutions:
            data[mdutils.KEY['S']][i] = "feasible\*"
        else:
            data[mdutils.KEY['S']][i] = "unknown"
    # Convert to Markdown table
    md_table = mdutils.data_to_table(data)
    # Don't wrap into details here.
    #md_table = mdutils.wrap_table_into_details(md_table, "Table")
    md_string = MD_HEADER + md_table
    # Write
    mdutils.write_md(outfile, md_string)

if __name__ == "__main__":
    main()
