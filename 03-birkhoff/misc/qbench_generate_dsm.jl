# Script to generate sparse and dense doubly stochastic matrices
# VV July 2024
#
# How to run: `$julia qbench_generate_dsm.jl n dense/sparse` where n is the matrix size
# Example: `julia qbench_generate_dsm.jl 3 sparse`

using Random
using JSON3

n = parse(Int64, ARGS[1])
num_permutations = n*n
file_name = "qbench_" * string(n) * "_dense.json"

if (ARGS[2] == "sparse")
    num_permutations = n
    file_name = "qbench_" * string(n) * "_sparse.json"
end

## Functions
function get_weights(x, max_interval)
  intervals = rand(0:max_interval, x-1)
  push!(intervals,0)
  push!(intervals,max_interval)
  intervals = sort(intervals)
  return diff(intervals)
end

function get_perm(n)
  P = Int16.(zeros(n,n))
  perm = randperm(n)
  for i=1:length(perm)
      P[perm[i], i] = 1
  end
  return P, perm
end


## Generate doubly stochastic matrices
dataset_size = 100
dataset = Dict([])
max_interval = 10^(length(string(n*n)) + 2)

for i in range(0,dataset_size)
  
  X = zeros(n,n)
  permutations = zeros(n,num_permutations)
  weights = get_weights(num_permutations, max_interval)

  # generate doubly stochastic matrix
  for j=1:num_permutations
    P, perm = get_perm(n)
    X = X .+ weights[j]*P
    permutations[:,j] = perm
  end
  # save doubly stochastic matrix, weights, and permutations
  entry = Dict([("n",n),
    ("scale", max_interval), 
    ("scaled_doubly_stochastic_matrix", X),
    ("permutations", Int16.(permutations)), 
    ("weights", weights)
    ])
  dataset[i] = entry

end

# Write output file


open(file_name,"w") do io
  JSON3.pretty(io, dataset)
end