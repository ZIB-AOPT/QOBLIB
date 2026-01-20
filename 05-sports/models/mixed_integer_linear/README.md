# Mixed Integer Programming Formulation

This directory contains the mixed integer programming formulation for the Sports Scheduling problem (double round-robin tournament).

There are different ways to model and solve the double round-robin tournament. In this repository, we include exemplary [MIP models](/05-sports/exemplary-models/mixed_integer_linear) of the given [instances](/05-sports/instances) in LP format (`.lp.gz`) as well as in ZIMPL format (`.tbl.gz`).

## Model Details

The MIP formulations follow the modeling approach described in [this paper](/05-sports/info/MILP_Try_Repeat.pdf). The models were created from the XML-based [instances](/05-sports/instances) using the [converter](/05-sports/misc/convert_xml2lp.sh).

## Generation

To generate the LP and MPS files, run `gen_archive.sh` on a Linux machine.
