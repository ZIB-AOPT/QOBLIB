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

# \file      sol2itc.py
# \brief     Convert MILP solution to ITC result file
# \author    Thorsten Koch
# \version   1.0
# \date      04May2021-28Feb2022
# \copyright Copyright (C) 2022 by Thorsten Koch <koch@zib.de>,
#            licensed under GPL version 3 or later
#
#
# This program reads a Zimpl .tbl file and a result file from
# SCIP, CPLEX, XPRESS, gurobi and writes out a ITC result XML file.
#
# Example:
# python3 sol2itc.py zpl1/E02a.tbl.gz mst/E02a.mst.gz >E02a.xml
#
import sys
import re
import gzip
from datetime import date

#for line in sys.stdin:

games    = []
max_team = 0
objval   = "0"
names    = {}

probname = sys.argv[-1].split("/")[-1][0:3]

for i in range(1, len(sys.argv)):
    filename = sys.argv[i]
    # print("Reading", filename)
    
    with gzip.open(filename, "rt") if filename[-3:] == ".gz" else open(filename) as f:
        for line in f:
            # Adjust for xpress solutions
            if re.search(" C x#", line):
                line = line[4:]
                
            fields = line.strip().split()

            if (line[0:5] == "zimpl" and fields[1] == "v"):
                # print(fields)
                names[fields[3]] = fields[4][1:-1];
                continue;
            
            if (line[0:19] == "# Objective value ="):
                objval = fields[4]
                continue

            # if not re.search("x#[0-9]+#[0-9]+#[0-9]+[ \t]+(1|0\.99999)", line):
            if not re.search("^x#", line):
                continue

            if float(fields[1]) < 0.99:
                continue

            if len(names) > 0 and names[fields[0]]:
                vname = names[fields[0]]
            else:
                vname = fields[0]

            assert 7 <= len(vname) <= 10, "variable [" + vname + "] has strange length"
            # print(line)
            # print(vname)

            values = vname.split("#")
    
            assert len(values) == 4

            home = int(values[1])
            away = int(values[2])
            slot = int(values[3])

            # print(slot, home, away)

            games.append([slot, (home,away)])

            if home > max_team:
                max_team = home
            if away > max_team:
                max_team = away


# print(games)

slots    = set([s for s,_ in games])
max_slot = max(slots)

#print(slots)

# print("Games: ", len(games))
#for s in slots:
#    print([g for t,g in games if t == s])

home_pairs = [(h,a) for h in range(0, max_team + 1) for a in range(h + 1, max_team + 1)]

away_pairs = [(a,h) for h,a in home_pairs]

#for (h,a) in home_pairs:
#    s1 = [s for s,(m,n) in games if (m,n) == (h,a)]
#    s2 = [s for s,(m,n) in games if (m,n) == (a,h)]
#    dist = abs(s1[0] - s2[0]) - 1
#    print(h,a,dist)
    
# print(home_pairs, away_pairs)

print("<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
print("<Solution><MetaData>")
print("<SolutionName>" + probname + "-" + str(objval) + "</SolutionName>")
print("<InstanceName>" + probname + "</InstanceName>")
print("<Contributor>Team MODAL (koch@zib.de)</Contributor>")
print("<Date day=\"" + str(date.today().day) + "\" month=\"" + str(date.today().day) + "\" year=\"" + str(date.today().year) + "\"/>")
print("<SolutionMethod>IP</SolutionMethod>")
print("<ObjectiveValue objective=\"" + objval + "\" infeasibility=\"0\"/>")
print("<LowerBound objective=\"0\" infeasibility=\"0\"/>")
print("<Remarks></Remarks>");
print("</MetaData><Games>")

count = 1
for s,(h,a) in games:
    print("<ScheduledMatch home=\"" + str(h) + "\" away=\"" + str(a) + "\" slot=\"" + str(s) + "\"/>", end="")
    if count % 8 == 0:
        print("")
    count += 1

print("</Games></Solution>")

#
#  This code is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 


