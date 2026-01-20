## Solution file format

Each file BX_Y_Z.rtf contains the solutions of 10 instances. 
    - X indicates the size of the doubly stochastic matrix (e.g., X = 4 for a 4x4 matrix).
    - Y is the density of the doubly stochastic matrix to decompose, i.e., the number of permutation matrices used to generate the doubly stochastic matrix. Sparse matrices have Y = X. Dense matrices have Y = X^2. 
    - Z contains the instance id (1-10). 

### How to read the solutions ###
The solutions consist of a list of permutations and weights.
    - Permutation: For a matrix of size nxn, a permutation is an array of size n containing integers from 1 to n. Each element in the array is unique. A permutation array is used to construct a permutation matrix: a binary matrix where each row and column sum to one. The permutation array indicates where the ones are located in the permutation matrix. In particular, the i-th element in the permutation array indicates the position of the 1 in the i-th column of the permutation matrix P. For example, for a 3x3 doubly stochastic matrix, the permutation array [1 3 2] corresponds to the permutation matrix
     [1 0 0]
 P = [0 0 1]
     [0 1 0]
    - Weights: A list of non-negative numbers that sum to 1. Each number is associated with a permutation matrix. The sum of weighted permutation matrices is a doubly stochastic matrix. Example for a 3x3 matrix:
Permutations:
 [1 2 3]
 [1 3 2]
 [2 1 3]
Weights: [0.5     0.3     0.2]
Reconstructed doubly stochastic matrix: 
[0.8 0.2   0]         [1 0 0]         [1 0 0]         [0 1 0]
[0.2 0.5 0.3] = 0.5 * [0 1 0] + 0.3 * [0 0 1] + 0.2 * [1 0 0]
[  0 0.3 0.7]         [0 0 1]         [0 1 0]         [0 0 1]
