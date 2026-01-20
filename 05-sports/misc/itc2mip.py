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

# \file      itc2mip.py
# \brief     Convert ITC Instances into a MILP
# \author    Thorsten Koch
# \version   1.0
# \date      04May2021-28Feb2022
# \copyright Copyright (C) 2022 by Thorsten Koch <koch@zib.de>,
#            licensed under GPL version 3 or later
#
#
# This program reads in an XML file with an ITC instances and writes out
# a file in the Zimpl modelling languages http://zimpl.zib.de which then
# can be converted into a .mps or .lp file to be solved with an standard
# MILP solver.
#
# Example:
#     python3 itc2mip.py --nosoft instances/ITC2021_Middle_7.xml.gz >M07d.zpl
#     zimpl -t mps M07d.zpl
#
# Todo
# - Optional Mirror constraint for phased
# - modell BR1 intp=0 directly on x variables
#
import sys
import gzip
import argparse
import xml.etree.ElementTree as ET


def output_base(
    teams,
    slots,
    is_phased,
    have_br,
    have_fa2,
    enforce_symmetry,
    feas_opt,
    gen_odd3,
    gen_oddall,
    fix_xcount,
    objective,
):

    assert (
        not gen_odd3 or not gen_oddall
    ), "add3 and odd all can not be active at the same time"

    print("param teams := ", len(teams), ";", sep="")
    print("param slots := ", len(slots), ";", sep="")

    print(
        """
set T  := { 0 .. teams - 1 };           # Teams
set S  := { 0 .. slots - 1 };           # Slots
set S0 := { 1 .. slots - 1 };           # without 1st slot
set S1 := { 0 .. slots / 2 - 1 };       # 1. Half season
set S2 := { slots / 2 .. slots - 1 };   # 2. Half season
set SZ := { 0 .. slots - 2 };           # without last slot
set M  := { <m,n> in T*T with m != n }; # Matches
set MR := { <m,n> in T*T with m <  n }; # Pairings

param matches_per_slot := card(T) / 2;

var x[M*S] binary;
var bh[T*S0] binary;
var ba[T*S0] binary;
        """
    )
    print(
        """
# Each match gets assigned to exactly one slot
subto c1:
   forall <m,n> in M :
      sum <s> in S : x[m,n,s]""",
        "== 1;" if not feas_opt else "<= 1;",
    )

    print(
        """
# At each slot, there are matches_per_slot matches.
subto c2:
   forall <s> in S:
      sum <m,n> in M : x[m,n,s]""",
        "== matches_per_slot;" if not feas_opt else "<= matches_per_slot;",
    )

    print(
        """
# Each team can only play once per slot
subto c3:
   forall <s> in S :
      forall <t> in T :
         sum <t,n> in M : x[t,n,s] + sum <m,t> in M : x[m,t,s]""",
        "== 1;" if not feas_opt else "<= 1;",
    )

    if fix_xcount:
        print(
            """
# Fix number of x variables that have to be 1
subto f1:
   sum <m,n,s> in M*S: x[m,n,s] == slots * teams / 2;
        """
        )

    if gen_odd3:
        print(
            """
# Generate 1-odd-set 3 constraints
set K3[] := subsets(T, 3);
set I3   := indexset(K3);
subto c6:
   forall <s> in S:
      forall <i> in I3:
         sum <m,n> in K3[i] * (T \\ K3[i]): (x[m,n,s] + x[n,m,s]) >= 1;
        """
        )

    if gen_oddall:
        print("\n# Generate 1-odd-set constraints")
        for k in range(3, int(len(teams) / 2) + 1, 2):
            ks = str(k)
            print("set K" + ks + "[] := subsets(T, " + ks + ");")
            print("set I" + ks + "   := indexset(K" + ks + ");")
            print("subto cos" + ks + ":")
            print("   forall <s> in S:")
            print("      forall <i> in I" + ks + ":")
            print(
                "         sum <m,n> in K"
                + ks
                + "[i] * (T \\ K"
                + ks
                + "[i]): (x[m,n,s] + x[n,m,s]) >= 1;"
            )

    if have_br:
        print(
            """
# Count breaks
subto br_count:
   forall <t> in T:
      forall <s> in S0:
         sum <a> in T \\ { t } : x[t,a,s - 1] + sum <a> in T \\ { t } : x[t,a,s] - 1 <= bh[t,s]  # home breaks
     and sum <h> in T \\ { t } : x[h,t,s - 1] + sum <h> in T \\ { t } : x[h,t,s] - 1 <= ba[t,s]; # away breaks
            """
        )
    if is_phased and not enforce_symmetry:
        print(
            """
# Each team once per half season
subto c4:
   forall <m,n> in MR :
      sum <s> in S1 : (x[m,n,s] + x[n,m,s])""",
            "== 1;" if not feas_opt else "<= 1;",
        )

    if have_fa2:
        if is_phased:
            print("var hg[<t,s> in T*S] <= min(s + 1, card(S) / 2);")  # can be integer
        else:
            print("var hg[<t,s> in T*S] <= s + 1;")  # can be integer

        print("subto hg_count:")
        print("   forall <t> in T:")
        print("      forall <s> in S:")
        print("         sum <a,p> in (T \\ { t }) * { 0 .. s }: x[t,a,p] == hg[t,s];")

    if objective is not None:
        objective.append("minimize violation:")

    if enforce_symmetry:
        print(
            """
# Ensure summetric solution in two phases
subto c5:
   forall <m,n> in MR :
      forall <s> in { 0 ..  floor((slots - 1) / 2) }:
        x[m,n,s] == x[n,m,s + (slots / 2)];
        """
        )

    return


def output_ca1(elem, count, count_soft, objective):

    print("\n#", elem.tag, str(elem.attrib).replace("'", ""))

    assert int(elem.attrib["min"]) == 0, "unhandled min attribute in CA1"

    maxi = int(elem.attrib["max"])
    mode = elem.attrib["mode"]
    ctype = elem.attrib["type"]
    penalty = int(elem.attrib["penalty"])
    slots = [int(i) for i in elem.attrib["slots"].split(";")]
    teams = [int(i) for i in elem.attrib["teams"].split(";")]
    count += 1

    assert mode == "H" or mode == "A", "unhandled mode attribute in CA1"
    assert ctype == "HARD" or ctype == "SOFT", "unknown type in CA2"

    if objective is None and ctype == "SOFT":
        return count, count_soft

    print("subto ca1_", count, ": ", sep="", end="")
    for t in sorted(teams):
        print("sum <n> in T\\{", t, "}: (", sep="", end="")
        for s in sorted(slots):
            if mode == "H":
                print(" + x[", t, ",n,", s, "]", sep="", end="")
            else:
                print(" + x[n,", t, ",", s, "]", sep="", end="")

    if ctype == "HARD":
        print(") <= ", maxi, ";", sep="")
    else:  # SOFT
        count_soft += 1
        vname = "ca1_viol[" + str(count_soft) + "]"
        print(") <=", maxi, "+", vname + ";")
        objective.append(vname + " * " + str(penalty))

    return count, count_soft


def output_ca2(elem, count, count_soft, objective):

    print("\n#", elem.tag, str(elem.attrib).replace("'", ""))

    assert int(elem.attrib["min"]) == 0, "unhandled min attribute in CA2"
    assert elem.attrib["mode2"] == "GLOBAL", "unhandled mode2 attribute in CA2"

    maxi = int(elem.attrib["max"])
    mode1 = elem.attrib["mode1"]
    ctype = elem.attrib["type"]
    penalty = int(elem.attrib["penalty"])
    slots = [int(i) for i in elem.attrib["slots"].split(";")]
    teams1 = [int(i) for i in elem.attrib["teams1"].split(";")]
    teams2 = [int(i) for i in elem.attrib["teams2"].split(";")]
    count += 1

    assert ctype == "HARD" or ctype == "SOFT", "unknown type in CA2"
    assert mode1 == "H" or mode1 == "A" or mode1 == "HA", "unknown mode1 in CA2"

    if objective is None and ctype == "SOFT":
        return count, count_soft

    slots = "{" + ", ".join(map(str, sorted(slots))) + "}"
    sumset = slots + " * " + "{" + ", ".join(map(str, sorted(teams2))) + "}"

    print("subto ca2_", count, ": ", sep="", end="")
    print("   forall <t> in {" + ", ".join(map(str, sorted(teams1))) + "}:")
    print("      sum <s,m> in " + sumset + ": (", end="")

    if mode1 == "H" or mode1 == "HA":
        print(" + x[t,m,s]", sep="", end="")
    if mode1 == "A" or mode1 == "HA":
        print(" + x[m,t,s]", sep="", end="")

    if elem.attrib["type"] == "HARD":
        print(") <= ", maxi, ";", sep="")
    else:  # SOFT
        count_soft += 1
        vname = "ca2_viol[" + str(count_soft) + "]"
        print(") <=", maxi, "+", vname + ";")
        objective.append(vname + " * " + str(penalty))

    return count, count_soft


def output_ca3(elem, count, objective):

    print("\n#", elem.tag, str(elem.attrib).replace("'", ""))

    assert int(elem.attrib["min"]) == 0, "unhandled min attribute in CA3"
    assert elem.attrib["mode2"] == "SLOTS", "unhandled mode2 attribute in CA3"

    maxi = int(elem.attrib["max"])
    intp = int(elem.attrib["intp"])
    mode1 = elem.attrib["mode1"]
    ctype = elem.attrib["type"]
    penalty = int(elem.attrib["penalty"])
    teams1 = [int(i) for i in elem.attrib["teams1"].split(";")]
    teams2 = [int(i) for i in elem.attrib["teams2"].split(";")]
    count += 1

    assert ctype == "HARD" or ctype == "SOFT", "unknown type in CA3"
    assert mode1 == "H" or mode1 == "A" or mode1 == "HA", "unknown mode1 in CA2"
    assert intp >= 2, "cannot handle intp < 2"

    if objective is None and ctype == "SOFT":
        return count

    slots = "S \\ { 0 .. " + str(intp - 2) + " }"

    if ctype == "SOFT":
        print("var ca3_" + str(count) + "_viol[" + slots + "] >= 0;")

    print("subto ca3_", count, ": ", sep="")
    print("   forall <t> in {" + ", ".join(map(str, sorted(teams1))) + "}:")
    print("      forall <s> in " + slots + ":")
    print(
        "         sum <m> in {" + ", ".join(map(str, sorted(teams2))) + "} \\ { t }: (",
        end="",
    )

    for i in range(intp):
        if mode1 == "H" or mode1 == "HA":
            print(" + x[t,m,s - ", i, "]", sep="", end="")
        if mode1 == "A" or mode1 == "HA":
            print(" + x[m,t,s - ", i, "]", sep="", end="")

    if ctype == "HARD":
        print(") <= ", maxi, ";", sep="")
    else:  # ctype == "SOFT":
        vname = "ca3_" + str(count) + "_viol[s]"
        print(") <=", maxi, "+", vname + ";")
        objective.append("sum <s> in " + slots + ": " + vname + " * " + str(penalty))

    return count


def output_ca4(elem, count, objective):

    print("\n#", elem.tag, str(elem.attrib).replace("'", ""))

    assert int(elem.attrib["min"]) == 0, "unhandled min attribute in CA4"

    maxi = int(elem.attrib["max"])
    mode1 = elem.attrib["mode1"]
    mode2 = elem.attrib["mode2"]
    ctype = elem.attrib["type"]
    penalty = int(elem.attrib["penalty"])
    slots = [int(i) for i in elem.attrib["slots"].split(";")]
    teams1 = [int(i) for i in elem.attrib["teams1"].split(";")]
    teams2 = [int(i) for i in elem.attrib["teams2"].split(";")]
    count += 1

    assert ctype == "HARD" or ctype == "SOFT", "unknown type in CA4"
    assert mode1 == "H" or mode1 == "A" or mode1 == "HA", "unknown mode1 in CA4"
    assert mode2 == "GLOBAL" or mode2 == "EVERY", "unknown mode2 in CA4"

    if objective is None and ctype == "SOFT":
        return count

    slots = "{" + ", ".join(map(str, sorted(slots))) + "}"
    t1 = "{" + ", ".join(map(str, sorted(teams1))) + "}"
    t2 = "{" + ", ".join(map(str, sorted(teams2))) + "}"

    if ctype == "SOFT":
        if mode2 == "GLOBAL":
            print("var ca4_" + str(count) + "_viol >= 0;")
        else:
            print("var ca4_" + str(count) + "_viol[" + slots + "] >= 0;")

    if mode2 == "GLOBAL":
        t1_x_t2_slots = t1 + " * " + t2 + " * " + slots

        print("subto ca4_", count, ": ", sep="", end="")
        print("   sum <m,n,s> in " + t1_x_t2_slots + " with m != n: (", end="")

    else:  # EVERY
        t1_x_t2 = t1 + " * " + t2

        print("subto ca4_", count, ": ", sep="", end="")
        print("   forall <s> in " + slots + ":")
        print("      sum <m,n> in " + t1_x_t2 + " with m != n: (", end="")

    if mode1 == "H" or mode1 == "HA":
        print(" + x[m,n,s]", sep="", end="")
    if mode1 == "A" or mode1 == "HA":
        print(" + x[n,m,s]", sep="", end="")

    if ctype == "HARD":
        print(") <= ", maxi, ";", sep="")
    else:  # SOFT
        if mode2 == "GLOBAL":
            vname = "ca4_" + str(count) + "_viol"
            objective.append(vname + " * " + str(penalty))
        else:
            vname = "ca4_" + str(count) + "_viol[s]"
            objective.append(
                "sum <s> in " + slots + " : " + vname + " * " + str(penalty)
            )

        print(") <=", maxi, "+", vname + ";")

    return count


def output_ga1(elem, count, count_soft, objective):

    print("\n#", elem.tag, str(elem.attrib).replace("'", ""))

    mini = int(elem.attrib["min"])
    maxi = int(elem.attrib["max"])
    ctype = elem.attrib["type"]
    penalty = int(elem.attrib["penalty"])
    ga1_slots = [int(i) for i in elem.attrib["slots"].split(";")]
    meetings = [
        tuple(map(int, m.split(","))) for m in elem.attrib["meetings"].split(";")[:-1]
    ]
    count += 1

    assert ctype == "HARD" or ctype == "SOFT", "unknown type in GA1"

    if objective is None and ctype == "SOFT":
        if mini > 0:
            count += 1
        return count, count_soft

    print("subto ga1_", count, ": ", sep="", end="")
    print("sum <s> in {" + ", ".join(map(str, sorted(ga1_slots))) + "}: (", end="")
    for m in meetings:
        print("+ x[", m[0], ",", m[1], ",s]", sep="", end="")

    if ctype == "HARD":
        print(") <= ", maxi, ";", sep="")
    else:  # SOFT
        count_soft += 1
        vname = "ga1_viol[" + str(count_soft) + "]"
        print(") <=", maxi, "+", vname + ";")

        objective.append(vname + " * " + str(penalty))

    if mini > 0:
        count += 1
        print("subto ga1_", count, ": ", sep="", end="")
        print("sum <s> in {" + ", ".join(map(str, sorted(ga1_slots))) + "}: (", end="")
        for m in meetings:
            print("+ x[", m[0], ",", m[1], ",s]", sep="", end="")

        if ctype == "HARD":
            print(") >= ", mini, ";", sep="")
        else:  # SOFT
            vname = "ga1_viol[" + str(count_soft) + "]"  # ??? share variable here?
            print(") >=", mini, "-", vname + ";")

    return count, count_soft


# <BR1 intp="1" mode1="LEQ" mode2="HA" penalty="5" slots="3;8;9" teams="2" type="SOFT"/>
# <BR1 intp="0" mode1="LEQ" mode2="HA" penalty="5" slots="4" teams="0" type="SOFT"/>
def output_br1(elem, count, objective):

    print("\n#", elem.tag, str(elem.attrib).replace("'", ""))

    assert elem.attrib["mode1"] == "LEQ", "unhandled mode1 attribute in BR1"

    intp = int(elem.attrib["intp"])
    ctype = elem.attrib["type"]
    mode2 = elem.attrib["mode2"]
    penalty = int(elem.attrib["penalty"])
    slots = sorted([int(i) for i in elem.attrib["slots"].split(";")])
    teams = sorted([int(i) for i in elem.attrib["teams"].split(";")])
    count += 1

    assert ctype == "HARD" or ctype == "SOFT", "unknown type in BR1"
    assert mode2 == "H" or mode2 == "A" or mode2 == "HA", "unknown mode1 in BR1"

    if objective is None and ctype == "SOFT":
        return count

    if slots[0] == 0:  # slot 0 can never be a break
        slots.remove(0)
        # if 0 was the only slot, nothing to do
        if len(slots) == 0:
            return count

    #  assert slots[0] != 0, "cannot handle slot 0 in BR1"

    if ctype == "SOFT":
        print("var br1_" + str(count) + "_viol >= 0;")

    ts = "{" + ", ".join(map(str, teams)) + "}"
    sl = "{" + ", ".join(map(str, slots)) + "}"
    ts_x_sl = ts + " * " + sl

    print("subto br1_", count, ": ", sep="")
    print("   forall <t> in " + ts + ":")
    print("      sum <s> in " + sl + ": (", end="")

    if mode2 == "H" or mode2 == "HA":
        print(" + bh[t,s]", sep="", end="")
    if mode2 == "A" or mode2 == "HA":
        print(" + ba[t,s]", sep="", end="")

    if ctype == "HARD":
        print(") <= ", intp, ";", sep="")
    else:  # ctype == "SOFT":
        vname = "br1_" + str(count) + "_viol"
        print(") <= ", intp, " + ", vname + ";", sep="")
        objective.append(vname + " * " + str(penalty))

    return count


# <BR2 intp="16" homeMode="HA" mode2="LEQ" penalty="1" slots="9;2;3;4;5;6;7;8;1;0" teams="2;0;3;5;4;1" type="HARD"/>
def output_br2(elem, count, objective):

    print("\n#", elem.tag, str(elem.attrib).replace("'", ""))

    assert elem.attrib["homeMode"] == "HA", "unhandled homeMode attribute in BR2"
    assert elem.attrib["mode2"] == "LEQ", "unhandled mode2 attribute in BR2"

    intp = int(elem.attrib["intp"])
    ctype = elem.attrib["type"]
    penalty = int(elem.attrib["penalty"])
    slots = sorted([int(i) for i in elem.attrib["slots"].split(";")])
    teams = sorted([int(i) for i in elem.attrib["teams"].split(";")])
    count += 1

    assert ctype == "HARD" or ctype == "SOFT", "unknown type in BR2"
    assert slots == list(range(slots[0], slots[-1] + 1)), "slots not consecutive in BR2"

    if objective is None and ctype == "SOFT":
        return count

    if ctype == "SOFT":
        print("var br2_" + str(count) + "_viol >= 0;")

    ts = "{" + ", ".join(map(str, teams)) + "}"
    sl = (
        "{" + ", ".join(map(str, slots[1:])) + "}"
    )  # ??? not clear whether 1 element should be removed if not 0 ???
    ts_x_sl = ts + " * " + sl

    print("subto br2_", count, ": ", sep="")
    print("   sum <t,s> in " + ts_x_sl + ": ", end="")

    if ctype == "HARD":
        print("(bh[t,s] + ba[t,s]) <= ", intp, ";", sep="")
    else:  # ctype == "SOFT":
        vname = "br2_" + str(count) + "_viol"
        print("(bh[t,s] + ba[t,s]) <= ", intp, "+", vname + ";", sep="")
        objective.append(vname + " * " + str(penalty))

    return count


# <FA2 intp="2" mode="H" penalty="10" slots="1;2;3;4;5;6;7;8;9;0" teams="1;0;5;2;3;4" type="SOFT"/>
def output_fa2(elem, count, objective):

    print("\n#", elem.tag, str(elem.attrib).replace("'", ""))

    assert elem.attrib["mode"] == "H", "unhandled mode attribute in FA2"

    intp = int(elem.attrib["intp"])
    ctype = elem.attrib["type"]
    penalty = int(elem.attrib["penalty"])
    slots = sorted([int(i) for i in elem.attrib["slots"].split(";")])
    teams = sorted([int(i) for i in elem.attrib["teams"].split(";")])
    count += 1

    assert ctype == "HARD" or ctype == "SOFT", "unknown type in FA2"

    if objective is None and ctype == "SOFT":
        return count

    sl = "{" + ", ".join(map(str, slots)) + "}"
    mr = "{" + ", ".join(map(str, sorted(teams))) + "}"
    fa2set = "FA2_" + str(count)

    print("set " + fa2set + " := { <m,n> in " + mr + " * " + mr + " with m < n };")
    print("var fa2_" + str(count) + "_viol[" + fa2set + "] >= 0;")

    print("subto fa2a_", count, ": ", sep="")
    print("   forall <m,n> in " + fa2set + ":")
    print("      forall <s> in " + sl + ":")

    if ctype == "HARD":
        print("         hg[m,s] - hg[n,s] <=", intp)
        print("     and hg[n,s] - hg[m,s] <=", intp, end=";\n")
    else:  # SOFT
        vname = "fa2_" + str(count) + "_viol[m,n]"

        print("         hg[m,s] - hg[n,s] <=", intp, "+ " + vname)
        print("     and hg[n,s] - hg[m,s] <=", intp, "+ " + vname, end=";\n")

        objective.append("sum <m,n> in " + fa2set + ": " + vname + " * " + str(penalty))

    return count


# <SE1 mode1="SLOTS" min="10" penalty="10" teams="2;0;3;5;4;1" type="SOFT"/>
def output_se1(elem, count, objective):

    print("\n#", elem.tag, str(elem.attrib).replace("'", ""))

    assert elem.attrib["mode1"] == "SLOTS", "unhandled mode1 attribute in SE1"

    mini = int(elem.attrib["min"])
    ctype = elem.attrib["type"]
    teams = [int(i) for i in elem.attrib["teams"].split(";")]
    penalty = elem.attrib["penalty"]
    count += 1

    assert ctype == "HARD" or ctype == "SOFT", "unknown type in SE1"

    if objective is None and ctype == "SOFT":
        return count

    mr = "{" + ", ".join(map(str, sorted(teams))) + "}"
    mr_x_mr = "<m,n> in " + mr + " * " + mr + " with m < n"

    if ctype == "SOFT":
        print("var se1_" + str(count) + "_viol[" + mr_x_mr + "] >= 0;")

    print("subto se1_", count, ": ", sep="")
    print("   forall " + mr_x_mr + ":")
    print(
        "      vabs(sum <s> in S : ((s + 1) * x[m,n,s] - (s + 1) * x[n,m,s])) >=",
        mini + 1,
        end="",
    )

    if ctype == "HARD":
        print(";")
    else:
        vname = "se1_" + str(count) + "_viol[m,n]"
        print(" - " + vname + ";")
        objective.append("sum " + mr_x_mr + ": " + vname + " * " + penalty)

    return count


def output_ca1_soft_prep(root):

    # count CA1 soft constraints
    count = 0
    for elem in root.iter():
        if elem.tag == "CA1":
            if elem.attrib["type"] == "SOFT":
                count += 1

    print("set CA1 := { 1 ..", count, "};")
    print("var ca1_viol[CA1] >= 0;")

    return


def output_ca2_soft_prep(root):

    # count CA2 soft constraints
    count = 0
    for elem in root.iter():
        if elem.tag == "CA2":
            if elem.attrib["type"] == "SOFT":
                count += 1

    print("set CA2 := { 1 ..", count, "};")
    print("var ca2_viol[CA2] >= 0;")

    return


def output_ga1_soft_prep(root):

    # count GA1 soft constraints
    count = 0
    for elem in root.iter():
        if elem.tag == "GA1":
            if elem.attrib["type"] == "SOFT":
                count += 1

    print("set GA1 := { 1 ..", count, "};")
    print("var ga1_viol[GA1] >= 0;")

    return


# -------------------------------------------------------------------------------------
filename = sys.argv[1]

parser = argparse.ArgumentParser()

parser.add_argument(
    "--nosoft", action="store_true", help="do not generate soft constraints"
)
parser.add_argument("--sym", action="store_true", help="enforce symmetric solution")
parser.add_argument("--feasopt", action="store_true", help="feasibility as objective")
parser.add_argument(
    "--odd3", action="store_true", help="generate odd-set 3 constraints"
)
parser.add_argument(
    "--oddall", action="store_true", help="generate all odd-set constraints"
)
parser.add_argument(
    "--xcount", action="store_true", help="fix number of x variables being 1"
)
parser.add_argument("--objcut", help="add objective cutoff constraint")
parser.add_argument("filename")

args = parser.parse_args()

objective = [] if not args.nosoft else None

xml_f = (
    gzip.open(args.filename, "rt")
    if args.filename[-3:] == ".gz"
    else open(args.filename)
)
tree = ET.parse(xml_f)
root = tree.getroot()
teams = []
slots = []
ca1_count = 0
ca1_count_soft = 0
ca2_count = 0
ca2_count_soft = 0
ca3_count = 0
ca4_count = 0
ga1_count = 0
ga1_count_soft = 0
se1_count = 0
br1_count = 0
br2_count = 0
fa2_count = 0
is_phased = False

have_fa2 = False
for elem in root.iter():
    if elem.tag == "FA2":
        have_fa2 = True
        break

have_br = False
for elem in root.iter():
    if elem.tag[:-1] == "BR":
        have_br = True
        break

for elem in root.iter():
    if elem.tag == "InstanceName":
        print("# Name:", elem.text)
        name = elem.text
    elif elem.tag == "gameMode":
        is_phased = elem.text == "P"
    elif elem.tag == "team":
        teams.append(int(elem.attrib["id"]))
    elif elem.tag == "slot":
        slots.append(int(elem.attrib["id"]))
    elif elem.tag == "Constraints":
        print("# Phased" if is_phased else "# No phase")
        print("# Teams: ", teams)
        print("# Slots: ", slots)
        print("")

        if not (objective is None):
            output_ca1_soft_prep(root)
            output_ca2_soft_prep(root)
            output_ga1_soft_prep(root)
            print("")

        output_base(
            teams,
            slots,
            is_phased,
            have_br,
            have_fa2,
            args.sym,
            args.feasopt,
            args.odd3,
            args.oddall,
            args.xcount,
            objective,
        )
    elif elem.tag == "CA1":
        ca1_count, ca1_count_soft = output_ca1(
            elem, ca1_count, ca1_count_soft, objective
        )
    elif elem.tag == "CA2":
        ca2_count, ca2_count_soft = output_ca2(
            elem, ca2_count, ca2_count_soft, objective
        )
    elif elem.tag == "CA3":
        ca3_count = output_ca3(elem, ca3_count, objective)
    elif elem.tag == "CA4":
        ca4_count = output_ca4(elem, ca4_count, objective)
    elif elem.tag == "GA1":
        ga1_count, ga1_count_soft = output_ga1(
            elem, ga1_count, ga1_count_soft, objective
        )
    elif elem.tag == "SE1":
        se1_count = output_se1(elem, se1_count, objective)
    elif elem.tag == "BR1":
        br1_count = output_br1(elem, br1_count, objective)
    elif elem.tag == "BR2":
        br2_count = output_br2(elem, br2_count, objective)
    elif elem.tag == "FA2":
        fa2_count = output_fa2(elem, fa2_count, objective)

if objective is not None:
    if args.feasopt:
        objective.append("sum <m,n,s> in M*S: -1000 * x[m,n,s]")
    elif args.objcut is not None:
        print("subto oc1:")
        print("\n   + ".join(objective[19:]) + " <=", args.objcut + ";")

    print("\n" + "\n   + ".join(objective) + ";")
else:
    if args.feasopt:
        print("maximize games: sum <m,n,s> in M*S: x[m,n,s];")


# print(name)
# print(teams)
# print(slots)

# print(root)
# inst = root.find('Instance')
# name = inst.find('InstanceName')
# print(inst, name);

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
