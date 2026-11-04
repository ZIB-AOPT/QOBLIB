# Instances for Stable Set

## Instance Format

This file describes the format in which the instances within the "instances" directory are saved.

The instances are stored as the graphs belonging to the MISP using the standard DIMACS graph format.
The first k lines starting with the letter 'c' describe comment lines, that are used to give information about the graph and can be ignored when processing the graph.
After that a single line in the form "p edge n m" follows, where n and m are the amount of nodes and edges of the graph respectively.
The file ends with m lines in the form "e v_i v_j" that describe the (undirected) edge between nodes v_i and v_j. Nodes are numberd from 1 to n.

The following illustrates an example graph.

```
c A beautiful and complicated graph!
c :)
p edge 3 2
e 1 2
e 2 3
```

**IMPORTANT.** The DIMACS graphs, i.e.: brock200_2, brock400_1, brock800_1, C500.9, c4000.5, gen200_p0-9_44, hamming10-4, keller4, keller6, p_hat1500_1 and p_hat1500-3 have already been inverted, as they have been originally used as max clique instances. Therefore results obtained on these inverted graphs are directly comparable to the results of the original max clique problem.

## Instance Sources

[aves-sparrow-social](https://networkrepository.com/aves-sparrow-social.php)  
[brock200-1](https://networkrepository.com/brock200-2.php)  
[brock200-2](https://networkrepository.com/brock200-2.php)  
[brock200-3](https://networkrepository.com/brock200-2.php)  
[brock200-4](https://networkrepository.com/brock200-2.php)  
[brock400-1](https://networkrepository.com/brock400-1.php)  
[brock800-1](https://networkrepository.com/brock800-1.php)  
[c-fat200-1](https://networkrepository.com/c-fat200-1.php)  
[C125-9](https://networkrepository.com/C125-9.php)  
[C500-9](https://networkrepository.com/C500-9.php)  
[C4000-5](https://networkrepository.com/C4000-5.php)  
[chesapeake](https://networkrepository.com/chesapeake.php)  
[es60fst01](https://steinlib.zib.de/showset.php?ES60FST)  
[es60fst02](https://steinlib.zib.de/showset.php?ES60FST)  
[es60fst03](https://steinlib.zib.de/showset.php?ES60FST)  
[es60fst04](https://steinlib.zib.de/showset.php?ES60FST)  
[farm](https://networkrepository.com/farm.php)  
[football](https://networkrepository.com/football.php)  
[frb45-21-3](https://networkrepository.com/frb45-21-3.php)  
[frb50-23-3](https://networkrepository.com/frb50-23-3.php)  
[frb53-24-1](https://networkrepository.com/frb53-24-1.php)  
[frb59-26-2](https://networkrepository.com/frb59-26-2.php)  
[frb100-40](https://networkrepository.com/frb100-40.php)  
[gen200_p0-9_44](https://networkrepository.com/gen200-p0-9-44.php)  
[hamming6-2](https://networkrepository.com/hamming6-2.php)  
[hamming6-4](https://networkrepository.com/hamming6-4.php)  
[hamming10-4](https://networkrepository.com/hamming10-4.php)  
[ibm32](https://networkrepository.com/ibm32.php)  
[insecta-ant-colony1-day38](https://networkrepository.com/insecta-ant-colony1-day38.php)  
[insecta-ant-colony3-day09](https://networkrepository.com/insecta-ant-colony3-day09.php)
[johnson8-2-4](https://networkrepository.com/johnson8-2-4.php)  
[johnson8-4-4](https://networkrepository.com/johnson8-4-4.php)  
[johnson16-2-4](https://networkrepository.com/johnson16-2-4.php)  
[karate](https://networkrepository.com/karate.php)  
[keller4](https://networkrepository.com/keller4.php)  
[keller6](https://networkrepository.com/keller6.php)  
[mammalia-kangaroo-interactions](https://networkrepository.com/mammalia-kangaroo-interactions.php)  
[MANN-a9](https://networkrepository.com/MANN-a9.php)  
[p_hat1500-1](https://networkrepository.com/p-hat1500-1.php)  
[p_hat1500-3](https://networkrepository.com/p-hat1500-3.php)  
R_500_005_1: generated during bachelor thesis  
R_1000_005_1: generated during bachelor thesis  
[sloane_1dc_128.gph](https://oeis.org/A265032/a265032.html)  
[sloane_1dc_64.gph](https://oeis.org/A265032/a265032.html)  
[sloane_1zc_128.gph](https://oeis.org/A265032/a265032.html)  
[sloane_2dc_128.gph](https://oeis.org/A265032/a265032.html)  
[socfb-haverford76](https://networkrepository.com/socfb-Haverford76.php)  
[socfb-trinity100](https://networkrepository.com/socfb-Trinity100.php)  
[sorrell4](https://miplib.zib.de/instance_details_sorrell4.html)  
[sorrell7](https://miplib.zib.de/instance_details_sorrell7.html)

## Adversarial generated instances (2026)

The following instances add two small dense, quantum-scale graphs and two sparse
frozen-XORSAT families with exact optima.

| Instance | Vertices | Edges | Density | Exact alpha | Generation family |
| :-- | --: | --: | --: | --: | :-- |
| `aheg_n99_s31` | 99 | 2,780 | 0.5731 | 7 | solver-guided evolutionary search |
| `hybrid_csp_spinglass_n180_s42` | 180 | 5,277 | 0.3276 | 15 | hybrid CSP and spin glass |
| `frozen_xorsat_c3k3_compact_n700` | 700 | 5,226 | 0.0214 | 175 | compact frozen (3,3)-XORSAT |
| `frozen_xorsat_c3k3_compact_n800` | 800 | 5,996 | 0.0188 | 200 | compact frozen (3,3)-XORSAT |
| `frozen_xorsat_c3k3_compact_n1000` | 1,000 | 7,472 | 0.0150 | 250 | compact frozen (3,3)-XORSAT |
| `frozen_xorsat_c3k3_compact_n1200` | 1,200 | 8,988 | 0.0125 | 300 | compact frozen (3,3)-XORSAT |
| `frozen_xorsat_c3k3_regular_n1500` | 1,500 | 4,750 | 0.0042 | 500 | regular frozen (3,3)-XORSAT |
| `frozen_xorsat_v2_qc_l75_s1` | 900 | 6,750 | 0.0167 | 225 | v2 quasi-cyclic frozen-XORSAT |
| `frozen_xorsat_v2_qc_l100_s4` | 1,200 | 9,000 | 0.0125 | 300 | v2 quasi-cyclic frozen-XORSAT |
| `frozen_xorsat_v2_qc_l125_s1` | 1,500 | 11,250 | 0.0100 | 375 | v2 quasi-cyclic frozen-XORSAT |

The n=99 and n=180 instances are deliberately small and dense.  They are
classically solved, and are included for structural and size coverage rather
than as claims of classical intractability.  The XORSAT reductions provide
larger sparse graphs whose optima have short combinatorial certificates: a
partition of all vertices into clique blocks gives an upper bound equal to the
size of the planted independent set.

The v2 XORSAT cases use quasi-cyclic lifts of a K3,3 Tanner protograph to add a
structured, girth-12 counterpart to the original compact random construction.

Generation code, parameters, exact regeneration commands for the XORSAT
family, solution verification, and bounded solver evidence are documented in
[the generator directory](../misc/adversarial_generators/README.md).  Reference
solutions are in [`../solutions/`](../solutions/).
