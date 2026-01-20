This folder contains the benchmarking results for the Birkhoff+, Blended FW, and an IP formulation with CPLEX. See Section 4.3.3 in https://arxiv.org/pdf/2504.03832. 

The folders 4-16 contain the results for doubly stochastic matrices of size 4 to 16. In each folder, there are two subfolders for dense and sparse matrices (see Section 4.3.3), each containing 10 instances. 

The file names BX_Y_Z indicate a particular instance. 
- X is the size of the doubly stochastic matrix (e.g., X = 4 for a 4x4 matrix).
- Y is the density of the doubly stochastic matrix to decompose, i.e., the number of permutation matrices used to generate the doubly stochastic matrix. Sparse matrices have Y = X. Dense matrices have Y = X^2. 
- Z is the instance id (1-10). 