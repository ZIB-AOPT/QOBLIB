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

# When converting to lp file, there will be /2 in the secondary item, which leads to the error with the objective of .qs file.
# Main optimization model

include "parameter_u3_c10.zpl";

minimize risk:
   upscale * (
      sum <t> in TX : (
         sum <i,m,tau_i,j,n,tau_j> in SX * SX : (
            round(lambda * tau_i * tau_j * cov[i,j,t] * p[i,t] * p[j,t]) 
            * x[i,m,tau_i,t] * x[j,n,tau_j,t]
         ) # risk
         - sum <k> in CS1 : round(nu * unit * 2^k) * y[k,t]  # cash interest
         + sum <i,m,-1> in SX : round(rho * p[i,t]) * x[i,m,-1,t]  # short sell cost
      )
      + sum <t> in TX \ { t_beg, t_end } : (
         - sum <i,m,tau> in SX : (
            round(tau * (p[i,t+1] - p[i,t])) * x[i,m,tau,t]  # return
            - round(delta * p[i,t]) * (x[i,m,tau,t-1] + x[i,m,tau,t]
                                - 2 * x[i,m,tau,t-1] * x[i,m,tau,t])  # transaction cost
         )
      )
      - sum <i,m,tau> in SX : (
         round(tau * (p[i,t_beg+1] - p[i,t_beg])) * x[i,m,tau,t_beg]  # return for the first day
         - round(delta * p[i,t_beg]) * x[i,m,tau,t_beg]  # transaction cost for the first day
      )
      + sum <i,m,tau> in SX : round(delta * p[i,t_end]) * x[i,m,tau,t_end]  # transaction cost for the last day
   )
;

subto c2:
   # Limit for short selling: total short units plus slack must match b_csh
   forall <t> in TX :
      sum <i,m,tau> in SX : tau * x[i,m,tau,t] + sum <c> in CS1 : 2^c * y[c,t] == C, qubo, penalty7;

subto c3:
   # Total number of assets (including short sells) must not exceed b_tot
   forall <t> in TX :
      sum <i,m,tau> in SX : x[i,m,tau,t] + sum <c> in CS2 : 2^c * s2[c,t] == B, qubo, penalty7;
