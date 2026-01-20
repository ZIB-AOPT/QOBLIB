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

import networkx as nx
import numpy as np
import warnings

from qiskit.transpiler.passes.routing.commuting_2q_gate_routing import SwapStrategy


def get_qubo_entry(line: str) -> tuple:
    """Get the QUBO entry from a line of a .qs file."""

    if len(line) > 0:
        # catch comments
        if line[0] == "#":
            return None

        entries = line.split(" ")

        # Anything that does not have three entries is not of <i> <j> <Q[i, j]> format
        if len(entries) != 3:
            return None

        # Get i, j, Q[i, j]
        try:
            row, col, value = int(entries[0]), int(entries[1]), float(entries[2])

            return row, col, value
        except ValueError:
            return None

    return None


def parse_qs_file(file_name: str):
    """Parse a .qs file to get header and qubo matrix."""
    qubo, num_vars = [], 0

    with open(file_name, "r") as fin:
        for line in fin:
            qubo_entry = get_qubo_entry(line)

            if qubo_entry is not None:
                qubo.append(qubo_entry)
                num_vars = max([num_vars, qubo_entry[0], qubo_entry[1]])

    qubo_matrix = np.zeros((num_vars, num_vars))

    for row, col, val in qubo:
        qubo_matrix[row - 1, col - 1] = val

    return qubo_matrix


def simplify_qubo_file(file_name: str, number_of_layers: int):
    """Simplifies the QUBO for execution on quantum hardware.

    Warning: this simplification explicitly changes the problem. After
    simplification, the given problem may not even correspond to the same
    class as the orgiginal problem.

    The problem is simplified according to the number of layers of SWAP gates
    that it takes to implement the connectivity required by the QUBO on a
    line of qubits. If an entry `Q[i, j]` requires `k` or more layers then it
    is not implemented and simply set to zero. The intent is to create a continuity
    of problem instances that are harder and harder. This makes it possible to
    benchmark performance on noisy quantum hardware.

    Args:
        file_name: The .qs file to read.
        number_of_layers: The number of swap layers allowed, i.e., `k`. If the QUBO
            is of dimension `n x n`, i.e., `n` binary variables, then `n - 2` layers
            of swap gates are sufficient to implement full connectivity. Therefore,
            this variable should take on values between 0 and `n - 2`.
    """

    if file_name[-3::] != ".qs":
        raise ValueError(f"The file must be in .qs format. Found {file_name}.")

    qubo = parse_qs_file(file_name)

    num_vars = qubo.shape[0]

    if number_of_layers < 0 or number_of_layers > num_vars - 2:
        raise ValueError(
            f"number_of_layers should be in the range [0, {num_vars} - 2] received {number_of_layers}"
        )

    swap_strategy = SwapStrategy.from_line(range(num_vars))

    # Throw away edges that cannot be implemented in less than number_of_layers
    simplified_qubo = qubo * (swap_strategy.distance_matrix < number_of_layers)

    # Now, we need to check that the resulting QUBO is connected.
    graph = nx.from_numpy_array(simplified_qubo)

    nonzero_entries = np.count_nonzero(np.triu(simplified_qubo))

    output_path = file_name[0:-3] + f"_{number_of_layers}layers.qs"

    with open(output_path, "w") as fout:
        fout.write(f"# This file is generated from {file_name}.\n")
        fout.write(
            f"# {number_of_layers} swap layers were used to simplify the instance.\n"
        )

        if not nx.is_connected(graph):
            warnings.warn("The instance is not connected.")
            fout.write("WARNING: The instance is not connected.\n")

        fout.write("# Vars Non-zeros\n")
        fout.write(f"{num_vars} {nonzero_entries}\n")
        for i in range(simplified_qubo.shape[0]):
            for j in range(i, simplified_qubo.shape[1]):
                if simplified_qubo[i, j] != 0:
                    fout.write(f"{i + 1} {j + 1} {simplified_qubo[i, j]}\n")
