# CP-SAT feasibility runs for the sports timetabling instances

The benchmark version of problem 05 only asks for a timetable that satisfies
every hard constraint. I post those constraints directly as a constraint
programming model over binary game variables x[home, away, slot], with home
and break indicator variables, and let OR-Tools CP-SAT look for a feasible
point. There is no objective and soft constraints are ignored, as the
benchmark description specifies.

The variable counts in each summary describe that model: n(n-1)S game
variables, nS home indicators and, when the instance has break constraints,
2n(S-1) break indicators, all binary. Since there is no objective and no
reference MIP is built, the coefficient fields are N/A.

Each timetable was verified twice. My own checker reproduces the hard
constraint semantics of the ITC2021 problem description and accepts all 249
reference solutions in 05-sports/solutions. The official RobinX validator from
the ITC2021 organisers reports infeasibility 0 for every file. The .sol files
use the Gurobi style x#home#away#slot lines that 05-sports/misc/sol2itc.py
converts to RobinX XML, and a RobinX XML copy of each timetable is included
next to it with the soft penalty the validator computed.

Code: https://github.com/mnn31/qoblib-solvers/tree/main/sports
