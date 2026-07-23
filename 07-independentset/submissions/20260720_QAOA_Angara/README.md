# Submission: 20260720_QAOA_Angara

- **Submitter:** Prashanti Priya Angara
- **Date:** 2026-07-20
- **Problem class:** Maximum Independent Set (07-independentset)
- **Reference:** [Experimental Workflows for Combinatorial Optimization: Towards Quantum Advantage](https://arxiv.org/pdf/2604.25162)

## Contents

- `problem_name/` — one solution file per instance, listing the selected independent-set node indices in a txt file
- `problem_name/problem_name.csv` — one file per solved instance
  
## Instances covered

- `C125-9`: |V|=125, |E|=787, best IS=28, optimal IS=34
- `aves-sparrow-social`: |V|=52, |E|=454, best IS=13, optimal IS=13
- `chesapeake`: |V|=39, |E|=170, best IS=16, optimal IS=17
- `es60fst01`: |V|=123, |E|=159, best IS=56, optimal IS=60
- `farm`: |V|=17, |E|=39, best IS=10, optimal IS=10
- `insecta-ant-colony1-day38`: |V|=56, |E|=1134, best IS=5, optimal IS=6
- `karate`: |V|=34, |E|=78, best IS=20, optimal IS=20
- `mammalia-kangaroo-interactions`: |V|=17, |E|=91, best IS=4, optimal IS=4
- `sloane_1dc_128`: |V|=128, |E|=1471, best IS=12, optimal IS=16
- `sloane_1dc_64`: |V|=64, |E|=543, best IS=8, optimal IS=10
- `sloane_1zc_128`: |V|=128, |E|=1120, best IS=17, optimal IS=18

## Notes

- Feasible/Successful Runs are the total number of samples. All obtained solutions are feasible as the Hamiltonian that is used is truly unconstrained (no penalties)
