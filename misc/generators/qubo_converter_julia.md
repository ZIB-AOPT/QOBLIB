# Julia File Converter LP to QUBO (@Pedro other formats supported)

[Github repo](https://github.com/JuliaQUBO/QUBO.jl)
[arXiv paper](https://arxiv.org/abs/2307.02577)

## Installation

1. Install julia
```shell
$curl -fsSL https://install.julialang.org | sh
```
1. Install converter package
```shell
$ julia --project=utils/converter -e 'import Pkg; Pkg.instantiate()'
```

## Usage

```shell
$ julia --project=utils/converter ./utils/converter/toqubo.jl [source_paths...]
```

## Example

```shell
$ julia --project=utils/converter ./utils/converter/toqubo.jl ./utils/converter/examples/model.lp

$ cat ./utils/converter/examples/model.lp.qh
```
