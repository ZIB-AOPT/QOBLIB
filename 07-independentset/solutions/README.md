# Solutions

## Format

We give the solutions to this problem in two different formats:

1. The standard GUROBI `.sol` format where each line contains the value of the corresponding variable and the objective value and model name is stated in the comments at the beginning of the file.
   For this problem, every variable corresponds to a node.
   If the variable is set to $1$, the node is in the solution, otherwise, it is not.

2. A nodelist.
   This format only contains the indices of the vertices that are in the solutions, i.e., the vertices for which the corresponding variabels in format 1 are set to $1$.

## Results

| Instance                       | Our Solution | Best Solution in Literature | Citation                                                                                                  |
| :----------------------------- | -----------: | --------------------------: | :-------------------------------------------------------------------------------------------------------- |
| aves-sparrow-social            |         13\* |                          13 |                                                                                                           |
| brock200-1                     |          6\* |                           6 |                                                                                                           |
| brock200-2                     |         12\* |                          12 |                                                                                                           |
| brock200-3                     |          9\* |                           9 |                                                                                                           |
| brock200-4                     |          8\* |                           8 |                                                                                                           |
| brock400-1                     |         27\* |                          27 |                                                                                                           |
| brock800-1                     |         23\* |                          23 |                                                                                                           |
| c-fat200-1                     |         18\* |                          18 |                                                                                                           |
| C125-9                         |         34\* |                          34 |                                                                                                           |
| C500-9                         |           57 |                          57 |                                                                                                           |
| C4000-5                        |           18 |                          18 |                                                                                                           |
| chesapeake                     |         17\* |                          17 |                                                                                                           |
| es60fst01                      |         60\* |                          60 |                                                                                                           |
| es60fst02                      |         88\* |                          88 |                                                                                                           |
| es60fst03                      |         55\* |                          55 |                                                                                                           |
| es60fst04                      |         78\* |                          78 |                                                                                                           |
| farm                           |         10\* |                          10 |                                                                                                           |
| football                       |         16\* |                          16 |                                                                                                           |
| frb45-21-3                     |         45\* |                          45 |                                                                                                           |
| frb50-23-3                     |         50\* |                          50 |                                                                                                           |
| frb53-24-1                     |           52 |                          53 | to be checked: [Jin, Hao 2015](https://www.sciencedirect.com/science/article/pii/S0952197614002061#s0055) |
| frb59-26-2                     |           58 |                          59 | to be checked: [Jin, Hao 2015](https://www.sciencedirect.com/science/article/pii/S0952197614002061#s0055) |
| frb100-40                      |           94 |                         100 | to be checked: [Jin, Hao 2015](https://www.sciencedirect.com/science/article/pii/S0952197614002061#s0055) |
| gen200_p0-9_44                 |         44\* |                          44 |                                                                                                           |
| hamming6-2                     |          2\* |                           2 |                                                                                                           |
| hamming6-4                     |         12\* |                          12 |                                                                                                           |
| hamming10-4                    |           40 |                          40 |                                                                                                           |
| ibm32                          |         13\* |                          13 |                                                                                                           |
| insecta-ant-colony1-day38      |          6\* |                           6 |                                                                                                           |
| insecta-ant-colony3-day09      |          9\* |                           9 |                                                                                                           |
| johnson8-2-4                   |          7\* |                           7 |                                                                                                           |
| johnson8-4-4                   |          5\* |                           5 |                                                                                                           |
| johnson16-2-4                  |         15\* |                          15 |                                                                                                           |
| karate                         |         20\* |                          20 |                                                                                                           |
| keller4                        |         11\* |                          11 |                                                                                                           |
| keller6                        |           59 |                          59 |                                                                                                           |
| mammalia-kangoroo-interactions |          4\* |                           4 |                                                                                                           |
| MANN-a9                        |          3\* |                           3 |                                                                                                           |
| p_hat1500-1                    |         12\* |                          12 |                                                                                                           |
| p_hat1500-3                    |         94\* |                          94 |                                                                                                           |
| R_500_005_1                    |           91 |                          91 |                                                                                                           |
| R_1000_005_1                   |          117 |                         117 |                                                                                                           |
| sloane_1dc_64                  |         10\* |                          10 |                                                                                                           |
| sloane_1dc_128                 |         16\* |                          16 |                                                                                                           |
| sloane_1zc_128                 |         18\* |                          18 |                                                                                                           |
| sloane_2dc_128                 |          5\* |                           5 |                                                                                                           |
| socfb-haverford76              |        282\* |                         282 |                                                                                                           |
| socfb-rtinity100               |          499 |                         499 |                                                                                                           |
| sorrell4                       |         24\* |                          24 |                                                                                                           |
| sorrell7                       |          198 |                         198 |                                                                                                           |
