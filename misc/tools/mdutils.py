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

"""mdutils.py: Helper Functions For Markdown Table Creation"""

import os
import sys
import pandas as pd

__author__ = "Paul Meinhold"
__copyright__ = "Copyright 2024, Zuse Institute Berlin"

# Constants
FILLSTR = "fill_" * 12
KEY = {
    'I': "Instance",
    'S': "Our Solution", 
    'B': "Best Solution in Literature",
    'C': "Citation"}

def get_new_data(n=0):
    """Return a new data dictionary with keys KEY and n empty strings in values"""
    data = {}
    # Initialize lists as data values with n empty strings
    for v in KEY.values():
        data[v] = [ "" for _ in range(n) ]
    return data

def fill_first_citation(data):
    """Fills the first citation field with FILL in data dictionary for width"""
    data[KEY['C']][0] = FILLSTR

def data_to_table(data):
    """Convert data dictionary to Markdown table"""
    return pd.DataFrame(data).to_markdown(
        index=False, colalign=("right", "right", "right", "left"))

def wrap_table_into_details(md_table, summary):
    """Surround Markdown table with HTML details clause under summary"""
    return f"\n<details><summary>{summary}</summary>\n\n{md_table}\n</details>"

def write_md(filepath, md_string):
    """Write a Mardown string to file"""
    with open(filepath, 'w') as f:
        f.write(md_string)

def main():
    data = get_new_data()
    print(data)
    data = get_new_data(10)
    print(data)

if __name__ == "__main__":
    main()
