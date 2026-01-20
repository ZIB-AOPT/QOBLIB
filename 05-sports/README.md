# 05 - Sports Tournament Scheduling

[← Back to Main Repository](../README.md)

---

## Overview

Sports tournament scheduling involves creating timetables for round-robin tournaments where each team plays every other team a fixed number of times. The problem becomes highly complex when considering real-world constraints such as venue capacity, travel considerations, and fairness requirements.

## Problem Description

In sports timetabling, a round-robin tournament is a tournament where each team plays against every other team a fixed number of times; see [1].
Round-robin tournaments are very common in practice, especially double round-robin tournaments,
where teams meet twice.
Here, we consider such double round-robin tournaments with an even number of teams and with a time-constrained timetable.
Under this setting, the total number of time slots is exactly equal to the total number of games
per team, and hence each team plays exactly one game per time slot.
In addition to these base constraints, each tournament has its own requirements such that real-life problems
face very diverse constraints.

The [instances](/05-sports/instances)
contained in this benchmark repository are taken from [3] and [4] (corresponding author [David Van Bulck](mailto:david.vanbulck@ugent.be)) and follow the XML-based human readable RobinX format; see [2].
The instances consider the following constraint types:

### Constraints

#### 1. **Capacity Constraints (CA)**
Regulate when teams can play home or away. There are four specific types of capacity constraints:

- **CA1**: Team *i* plays at least or no more than *k* home games during specified time slots.
- **CA2**: Same as CA1 but considering opponents as well.
- **CA3**: No more than two consecutive home or two consecutive away games.
- **CA4**: Same as CA2, but considering multiple teams.

#### 2. **Break Constraints (BR)**
A team has a break if it plays consecutively at home or away. There are two specific types of break constraints:

- **BR1**: Team *i* has no more than *k* breaks during specified time slots.
- **BR2**: The number of breaks over all teams is no more than *k*.

#### 3. **Game Constraints (GA)**
Game constraints enforce or forbid specific assignments of games to time slots:

- **GA1**: No more than *k* games from a given list during specified time slots.

#### 4. **Fairness and Separation Constraints (FA, SE)**
Increase the attractiveness and fairness of the tournament.

- **FA1**: at any point in time, the difference in the number of home games played between any two teams does not exceed two.
- **SE1**: there are at least 10 time slots between each pair of games involving the same teams.


#### Feasibility vs. Optimization Problem
In the original RobinX format, constraints can be either hard or soft. While hard constraints represent fundamental properties of the timetable and can never be violated, soft constraints rather represent preferences that should be satisfied whenever possible.
In order to lower the entrance barrier, the quantum benchmark ignores all soft constraints which reduces the problem to a feasibility problem.
A subset of the original instances were selected for which existing solvers could not find any feasible solution within a reasonable amount of time (see [Large instances](/05-sports/instances/Large) and [4]).
Since the original instances are possibly bigger (16 to 20 teams; >100 variables), we also provide instances with 8 (see [Small instances](/05-sports/instances/Small)) and 12 teams (see [Medium instances](/05-sports/instances/Medium)).
For the original problem instances with soft constraints, see the [ITC2021 instances](/05-sports/instances/ITC2021).

### Objective

For the feasibility version of the problem considered in this benchmark, the objective is to find feasible solutions to all instances in as little time as possible.

For the original ITC2021 problem, the objective is to minimize soft constraint violations. Please, refer to the [competition manual](/05-sports/info/OrganizationITC2021_V7.pdf) for more information. If you find new best known solutions, please submit them to the official [ITC2021 website](https://robinxval.ugent.be/ITC2021/instances.php).

## Directory Contents

- **[instances/](instances/)** - Tournament scheduling instances in RobinX XML format
  - [Small instances](instances/Small) - 8 teams
  - [Medium instances](instances/Medium) - 12 teams
  - [Large instances](instances/Large) - 16-20 teams
  - [ITC2021 instances](instances/ITC2021) - Original competition instances with soft constraints
- **[models/](models/)** - Mathematical model formulations
- **[solutions/](solutions/)** - Feasible solutions and best-known results
- **[info/](info/)** - Competition documentation and papers
- **[misc/](misc/)** - Utility scripts and tools
- **[submissions/](submissions/)** - Community solution submissions

## Related Work

- **van Doornmalen, Hojny, Lambers, Spieksma** - [Integer programming models for round robin tournaments](https://www.sciencedirect.com/science/article/pii/S0377221723001510)
- **Urdaneta, Yuan, Siqueira** - [Alternative Integer Linear and Quadratic Programming Formulations for HA-Assignment Problems](https://proceedings.sbmac.org.br/sbmac/article/view/2063) - QUBO formulation for home-away assignment
- **Kuramata, Katsuki, Nakata** - [Solving Large Break Minimization Problems in a Mirrored Double Round Robin Tournament Using Quantum Annealing](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0266846)
- **Fuji, Matsui** - [Solving break minimization problems in mirrored double round-robin tournament with QUBO solver](https://arxiv.org/abs/2307.00263)
- **Rosati, Petris, Di Gaspero, Schaerf** - [Multi-neighborhood simulated annealing for the sports timetabling competition ITC2021](https://doi.org/10.1007/s10951-022-00740-y) - Open source benchmarking algorithm


## References

[1] [ITC2021 – Sports Timetabling Problem Description and File Format](/05-sports/info/OrganizationITC2021_V7.pdf)

[2] [RobinX: A three-field classification and unified data format for round-robin sports timetabling](/05-sports/info/VanBulck2019.pdf)

[3] **Van Bulck, D., Goossens, D.** [The International Timetabling Competition on Sports Timetabling (ITC2021)](/05-sports/info/1-s2.0-S0377221722009201-main.pdf)

[4] **Van Bulck, D., et al.** [Which algorithm to select in sports timetabling?](/05-sports/info/VanBulck2024.pdf)

