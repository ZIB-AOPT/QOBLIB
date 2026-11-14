# CP-SAT feasibility runs for the sports timetabling instances

The benchmark version of problem 05 only asks for a timetable that satisfies
every hard constraint. I post those constraints directly as a constraint
programming model over binary game variables x[home, away, slot], with home
and break indicator variables, and let OR-Tools CP-SAT look for a feasible
point. There is no objective and soft constraints are ignored, as the
benchmark description specifies.

The variable counts in each summary describe that model: n(n-1)S game
variables, nS home indicators and, when the instance has break constraints,
2n(S-1) break indicators, all binary. The constraints are posted to CP-SAT
directly and no matrix form is built, so the coefficient fields are N/A.

## Runs

Every instance was run five times, with CP-SAT seeds 0 to 4, 8 workers and a
600 s limit per run, strictly one run at a time on one laptop on AC power. 40
runs that overlapped other work on the laptop were discarded and run again with
the same seed, and one kept run ended about 2 s after the laptop was unplugged
(Addition_046_Medium, seed 0, no timetable in 600 s; that instance has no row).
CP-SAT with several workers is not deterministic, so these are reported as
independent stochastic runs. With 8 workers and only 5 performance cores, part
of the work runs on the efficiency cores; the setting is the same for every
run.

Total Runtime is the mean wall clock time over the five runs, model build
included, and a run that found no timetable counts with its full time. CPU
Runtime is the mean process CPU time, which adds up all CP-SAT worker threads
and is therefore up to about eight times the wall clock time. A few runs of a
fraction of a second show CPU time below wall clock time, since such a run is
partly idle (for example while the worker threads start and stop). Time to
Solution is the mean wall clock time of the runs that found a timetable.
Runtimes in the rows are rounded to 0.01 s, the per run times in the remarks to
0.1 s (1 s for runs without a timetable). Each row lists the time of every run
in its remarks, and the objective time series holds all five runs (an incumbent
of 0 when the timetable is found, null before that or for the whole run if none
was found).

Instances: the 26 ITC2021 instances of the first version of this submission,
and every Tiny, Small and Medium instance that has a value in the best known
table (51 + 51 + 45). Rows are only included where at least one run found a
timetable: 164 rows. No run found a timetable for nine Medium instances
(Addition_003, 029, 043, 046, 064, 067, 083, 100 and 107), so they have no row.
For seven more Medium instances (Addition_016, 032, 082, 085, 109, 111 and
Late_005) only some of the runs found one, and those rows count only these runs
as successful. Not run with this protocol: the other 19 ITC2021 instances, the
6 Medium instances without a table value and the 51 Large instances.

Each timetable was checked with my own checker, which reproduces the hard
constraint semantics of the ITC2021 problem description and accepts all 249
reference solutions in 05-sports/solutions. The .sol files use the Gurobi style
x#home#away#slot lines that 05-sports/misc/sol2itc.py converts to RobinX XML.

An earlier version of this submission had one run per instance on a cloud
machine with 16 workers, called the method deterministic and copied wall time
into the CPU field. Those rows are replaced by these.

Code, run records (json, timetable and checker result of every run, run log,
settings) and the script that builds these rows from them:
https://github.com/mnn31/qoblib-solvers/tree/c83703b5de3b9c998407b3f4375b7034f7394382/sports

## Existing timetables for the ITC2021 instances

05-sports/solutions/ITC2021 already holds RobinX XML timetables for these
instances from the ITC2021 competition, and the competition README lists a
best soft objective from the literature for each of them. The best known table
does not show them, because the objective reader does not parse XML, so the
remarks say "no entry in the best known table", not "no feasible solution".
The timetables here were computed from scratch and were never seeded from
those files. What they add is a reproducible method with the time CP-SAT needs
to reach feasibility.

## AI disclosure

assisted —  code and repetitive boiler syntax implementation. The solver code,
the packaging scripts and the first drafts of the write-ups were written with help from
Claude (Claude Code, Claude Fable 5.1, Anthropic). All goals, problem choices,
methods and responses  were directed by the author, and every reported
run and solution file was executed, checked and confirmed by the author.
