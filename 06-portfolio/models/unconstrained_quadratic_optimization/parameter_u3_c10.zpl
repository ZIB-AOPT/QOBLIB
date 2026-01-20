# This file is part of QOBLIB - Quantum Optimization Benchmarking Library
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

param num_assets        := 50;  # Default a (overwritten by -Da=... if desired)
param time_intervals    := 10;  # Default t (overwritten by -Dt=... if desired)

# Basic parameters
param cash      := 1000000;
param unit      := 100000;
param delta     := 0.001;
param rho_p     := 0.0003;
param nu        := 0.0001;
param rho       := 0.000025;
param ub        := 3;
param lambda    := 1;
param upscale   := 1;

# b_tot depends on the value of a; we do not use an else
param B := 50;

# Start and end time indices
param t_beg := 0;
param t_end := t_beg + time_intervals - 1;

# How many units of stocks can be bought initially
param C := cash / unit;

# Reading the data sets (stock prices and covariance)
set T               := { read stock_price as "<1n>" comment "#" };
set S               := { read stock_price as "<2s>" comment "#" };
param raw_p[S*T]    := read stock_price as "<2s,1n> 3n" comment "#";
param cov[S*S*T]    := read stock_covariance as "<2s,3s,1n> 4n" comment "#";

# One unit is unit/p[s,t_beg] shares of stock s
param ucnt[<s> in S] := unit / raw_p[s,t_beg];

# p[s,tt] is the price of one unit of stock s at time tt
param p[<s,tt> in S*T] := raw_p[s,tt] * ucnt[s];

# Additional sets for slack variables
set CS1 := { 0 .. 3 };
set CS2 := { 0 .. 6 };
set TX  := { t_beg .. t_end };
set SC  := { 1 .. ub };
set SL  := { 1, -1 };
set SX  := S * SC * SL;

# Declare binary variables
var x[SX*TX]   binary;
var y[CS1*TX] binary;
var s2[CS2*TX] binary;

