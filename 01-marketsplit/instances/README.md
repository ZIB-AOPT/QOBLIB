# Instances for Market Split

## Format Description

The market split problem can be expressed as finding a vector $x \in \{0,1\}^n$ such that $Ax = b$ for given $A \in \mathbb{N}^{m,n}$ and $b \in \mathbb{N}^m$.
We provide the instances in dat format, where the first line gives $m$ and $n$ and the consecutive $m$ lines contain $n + 1$ whitespace separated values: 
The first $n$ values are the entries of the repective row in $A$ and the last value is the respective entry in $b$.

This way, we can easily add or take away specific rows to increase or decrease the difficulty of the problem. 

## Instance Generation

All instances in this directory up to size $7$ were generated randomly with a script provided in [misc](./../misc/) using an instance generator written by Marc Pfetch.

Instances from size $8$ and up were generated using the script provided [here](./../misc/marketsplit_gen/).

The solutions that were used to generate the instances can be found [here](./instance_gen_set/).