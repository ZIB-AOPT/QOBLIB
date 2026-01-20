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

import os
import lzma
import tempfile
import sys
import shutil
from pathlib import Path
import numpy as np

from docplex.mp.model_reader import ModelReader
from qiskit_optimization.converters import QuadraticProgramToQubo
from qiskit_optimization.translators import from_docplex_mp
from gurobipy import read
from qiskit_optimization.translators import from_gurobipy


def decompress_lp_file(lp_xz_path, tmp_dir):
    """
    Decompresses a single .lp.xz file to a temporary directory.
    Returns the path to the decompressed .lp file.
    """
    print(f"Decompressing {lp_xz_path} ...")
    base_name = os.path.basename(lp_xz_path).replace('.xz', '')
    output_path = os.path.join(tmp_dir, base_name)
    
    with lzma.open(lp_xz_path, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    return output_path


def lp_to_qubo(lp_path):
    """
    Reads an LP file via docplex's ModelReader, then converts to a QUBO.
    Returns the QUBO as a QuadraticProgram.
    """
    print(f"Parsing LP: {lp_path} ...")
    # Use Gurobi to parse the LP file
    model = read(lp_path)

    
    # Convert all continuous variables to integer
    for var in model.getVars():
        if var.vtype == 'C':  # Check if the variable is continuous
            var.vtype = 'I'  # Change the variable type to integer

    # Convert Gurobi model to Qiskit's QuadraticProgram
    qp = from_gurobipy(model)

    # Convert QuadraticProgram to QUBO
    converter = QuadraticProgramToQubo()
    qubo = converter.convert(qp)

    quadratic_matrix = qubo.objective.quadratic.to_array()
    density = (quadratic_matrix != 0).sum() / quadratic_matrix.size
    size = quadratic_matrix.shape
    print(f"Quadratic matrix size: {size}")
    print(f"Quadratic matrix density: {density}")

    return qubo


def write_qubo(qubo, output_path):
    """
    Writes a QUBO to a compressed .qs.xz file in QS format.
    Every line in the file is of the form:
    <row> <col> <value>
    """
    quadratic_matrix = qubo.objective.quadratic.to_array()
    linear_matrix = qubo.objective.linear.to_array()
    constant = qubo.objective.constant

    print(f"Writing QUBO to {output_path} ...")

    Q = quadratic_matrix + np.diag(linear_matrix)
    Q = (Q + Q.T) / 2  # Ensure symmetry

    nonzero_entries = np.count_nonzero(np.triu(Q))
    num_vars = Q.shape[0]

    with lzma.open(output_path, 'wt') as f:
        f.write(f"# ObjectiveOffset {constant}\n")
        f.write(f"{num_vars} {nonzero_entries}\n")
        for i in range(Q.shape[0]):
            for j in range(i, Q.shape[1]):
                if Q[i, j] != 0:
                    f.write(f"{i + 1} {j + 1} {Q[i, j]}\n")


def convert_single_file(lp_xz_path, tmp_dir):
    """
    Converts a single .lp.xz file to a .qs.xz file.
    """
    try:
        # Decompress the .lp.xz file
        lp_file = decompress_lp_file(lp_xz_path, tmp_dir)
        
        # Convert to QUBO
        qubo = lp_to_qubo(lp_file)
        print(f"Successfully converted {lp_xz_path} to a QUBO!\n")
        
        # Generate output filename: replace .lp.xz with .qs.xz
        output_file = lp_xz_path.replace(".lp.xz", ".qs.xz")
        
        # Write compressed QUBO
        write_qubo(qubo, output_file)
        print(f"QUBO written to {output_file}")
        print("-" * 60)
        return True

    except Exception as e:
        print(f"Failed to convert {lp_xz_path}: {e}")
        print("-" * 60)
        return False


def main(input_path):
    """
    Converts .lp.xz file(s) to .qs.xz file(s).
    If input_path is a directory, converts all .lp.xz files in it.
    If input_path is a file, converts that single file.
    """
    tmp_dir = tempfile.mkdtemp(dir="/tmp")
    
    try:
        # Check if input is a directory or file
        if os.path.isdir(input_path):
            # Find all .lp.xz files in the directory and subdirectories
            lp_xz_files = sorted(Path(input_path).rglob("*.lp.xz"))
            
            if not lp_xz_files:
                print(f"No .lp.xz files found in directory: {input_path}")
                sys.exit(1)
            
            print(f"Found {len(lp_xz_files)} .lp.xz file(s) to convert\n")
            
            success_count = 0
            fail_count = 0
            
            for lp_xz_file in lp_xz_files:
                if convert_single_file(str(lp_xz_file), tmp_dir):
                    success_count += 1
                else:
                    fail_count += 1
            
            print(f"\n{'='*60}")
            print(f"Conversion complete: {success_count} succeeded, {fail_count} failed")
            print(f"{'='*60}")
            
        elif os.path.isfile(input_path):
            # Convert single file
            if not input_path.endswith('.lp.xz'):
                print("Error: Input file must have .lp.xz extension")
                sys.exit(1)
            
            if not convert_single_file(input_path, tmp_dir):
                sys.exit(1)
        else:
            print(f"Error: Path does not exist: {input_path}")
            sys.exit(1)
    
    finally:
        # Clean up temporary directory
        shutil.rmtree(tmp_dir)
        print(f"Temporary directory {tmp_dir} has been deleted.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convert_lp_to_qubo.py <path_to_lp_xz_file_or_directory>")
        sys.exit(1)

    input_path = sys.argv[1]
    main(input_path)
