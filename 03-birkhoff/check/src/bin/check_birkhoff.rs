/*
This file is part of QOBLIB - Quantum Optimization Benchmarking Library
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

/**
Birkhoff Decomposition Solution Checker
Verifies that the given permutation matrices and weights correctly reconstruct
the doubly stochastic matrix.
*/
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::env;
use std::fs;

const VERSION: &str = "1.0";

#[derive(Debug, Deserialize, Serialize)]
struct Instance {
    scaled_doubly_stochastic_matrix: Vec<i32>,
    weights: Vec<i32>,
    id: String,
    permutations: Vec<i32>,
    scale: i32,
    n: usize,
}

#[derive(Debug, Deserialize)]
struct InstanceFile {
    #[serde(skip_serializing_if = "Option::is_none")]
    _license: Option<String>,
    #[serde(flatten)]
    instances: HashMap<String, Instance>,
}

#[derive(Debug, Deserialize, Serialize)]
struct Solution {
    scaled_doubly_stochastic_matrix: Vec<i32>,
    weights: Vec<i32>,
    permutations: Vec<i32>,
    id: String,
}

#[derive(Debug, Deserialize)]
struct SolutionFile {
    #[serde(flatten)]
    solutions: HashMap<String, Solution>,
}

fn is_valid_permutation(perm: &[i32], n: usize) -> bool {
    // Check that permutation has correct length
    if perm.len() != n {
        return false;
    }

    // Check that all values are in range [1..n]
    for &val in perm {
        if val < 1 || val > n as i32 {
            return false;
        }
    }

    // Check that all values are unique (valid permutation)
    let mut seen = vec![false; n];
    for &val in perm {
        let idx = (val - 1) as usize;
        if seen[idx] {
            return false; // Duplicate value
        }
        seen[idx] = true;
    }

    true
}

fn check_birkhoff_decomposition(instance: &Instance, solution: &Solution) -> Result<bool, String> {
    let n = instance.n;

    // Get target matrix
    let target_matrix: Vec<i32> = instance.scaled_doubly_stochastic_matrix.clone();

    // Check that weights sum to scale
    let weight_sum: i32 = solution.weights.iter().sum();
    if weight_sum != instance.scale {
        return Ok(false);
    }

    let num_perms = solution.weights.len();
    let expected_perm_data_len = num_perms * n;

    if solution.permutations.len() != expected_perm_data_len {
        println!(
            "    Permutation data length {} doesn't match expected {}",
            solution.permutations.len(),
            expected_perm_data_len
        );
        return Ok(false);
    }

    // Reconstruct the matrix from the Birkhoff decomposition
    let mut reconstructed = vec![0; n * n];

    for i in 0..num_perms {
        // Extract the i-th permutation vector
        let start_idx = i * n;
        let end_idx = (i + 1) * n;
        let perm = &solution.permutations[start_idx..end_idx];

        // Verify it's a valid permutation
        if !is_valid_permutation(perm, n) {
            println!(
                "    Permutation {} is not a valid permutation: {:?}",
                i + 1,
                perm
            );
            return Ok(false);
        }

        // Add weighted permutation to reconstruction
        // For each row, the permutation gives the column index (1-indexed)
        for row in 0..n {
            let col = (perm[row] - 1) as usize; // Convert to 0-indexed
            reconstructed[row * n + col] += solution.weights[i];
        }
    }

    // Check if reconstruction matches target
    for i in 0..(n * n) {
        if reconstructed[i] != target_matrix[i] {
            println!(
                "    Reconstruction mismatch at index {}: expected {}, got {}",
                i, target_matrix[i], reconstructed[i]
            );
            return Ok(false);
        }
    }

    // Count non-zero weights
    let num_nonzero_weights = solution.weights.iter().filter(|&&w| w > 0).count();
    println!(
        "    Valid decomposition with {} permutation matrices",
        num_nonzero_weights
    );

    Ok(true)
}

fn main() {
    println!(
        "QOBLIB Birkhoff Decomposition Solution Checker Version {}",
        VERSION
    );

    let args: Vec<String> = env::args().collect();

    if args.len() < 3 {
        eprintln!("ERROR: usage: {} instance-file solution-file", &args[0]);
        std::process::exit(2);
    }

    // Load instance file
    let instance_data = fs::read_to_string(&args[1])
        .unwrap_or_else(|err| panic!("Reading {} failed: {err}", args[1]));

    let instance_file: InstanceFile = serde_json::from_str(&instance_data)
        .unwrap_or_else(|err| panic!("Parsing instance JSON failed: {err}"));

    // Load solution file
    let solution_data = fs::read_to_string(&args[2])
        .unwrap_or_else(|err| panic!("Reading {} failed: {err}", args[2]));

    let solution_file: SolutionFile = serde_json::from_str(&solution_data)
        .unwrap_or_else(|err| panic!("Parsing solution JSON failed: {err}"));

    // make the ids of instances and solutions their keys
    let instance_map: HashMap<String, &Instance> = instance_file
        .instances
        .iter()
        .map(|(_, instance)| (instance.id.clone(), instance))
        .collect();

    let solution_map: HashMap<String, &Solution> = solution_file
        .solutions
        .iter()
        .map(|(_, solution)| (solution.id.clone(), solution))
        .collect();

    // Check all instances
    let mut all_valid = true;
    let mut passed = 0;
    let mut failed = 0;

    let mut solution_ids: Vec<String> = solution_map.keys().cloned().collect();
    solution_ids.sort();

    for solution_id in solution_ids {
        let solution = &solution_map[&solution_id];

        if let Some(instance) = instance_map.get(&solution_id) {
            print!("  Instance {}: ", solution_id);
            match check_birkhoff_decomposition(instance, solution) {
                Ok(true) => {
                    passed += 1;
                }
                Ok(false) => {
                    failed += 1;
                    all_valid = false;
                }
                Err(e) => {
                    println!("ERROR: {}", e);
                    failed += 1;
                    all_valid = false;
                }
            }
        } else {
            println!("  Instance {}: MISSING in instance file", solution_id);
            failed += 1;
            all_valid = false;
        }
    }

    println!();
    if all_valid {
        println!("VALID: All {} instances verified successfully", passed);
        std::process::exit(0);
    } else {
        println!(
            "INVALID: {} of {} instances failed",
            failed,
            passed + failed
        );
        std::process::exit(1);
    }
}
