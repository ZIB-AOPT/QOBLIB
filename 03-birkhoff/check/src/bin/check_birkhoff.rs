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
use clap::Parser;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;

const VERSION: &str = "1.2";

#[derive(Debug, Deserialize, Serialize)]
struct Instance {
    scaled_doubly_stochastic_matrix: Vec<u32>,
    weights: Vec<u32>,
    id: String,
    permutations: Vec<u32>,
    scale: u32,
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
    scaled_doubly_stochastic_matrix: Vec<u32>,
    weights: Vec<f64>,
    permutations: Vec<u32>,
    id: String,
}

#[derive(Debug, Deserialize)]
struct SolutionFile {
    #[serde(flatten)]
    solutions: HashMap<String, Solution>,
}

fn is_valid_permutation(perm: &[u32], n: usize) -> bool {
    // Check that permutation has correct length
    if perm.len() != n {
        return false;
    }

    // Check that all values are in range [1..n]
    for &val in perm {
        if val < 1 || val > n as u32 {
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

fn check_birkhoff_decomposition(
    instance: &Instance,
    solution: &Solution,
    tolerance: f64,
) -> Result<bool, String> {
    let n = instance.n;

    // Get target matrix
    let target_matrix: Vec<u32> = instance.scaled_doubly_stochastic_matrix.clone();

    // Check that weights sum to scale (exact)
    let weight_sum: f64 = solution.weights.iter().sum();
    let scale_f = instance.scale as f64;
    if weight_sum != scale_f {
        println!(
            "    Weight sum {} does not equal scale {}",
            weight_sum, instance.scale
        );
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
    let mut reconstructed = vec![0f64; n * n];

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

    // Count non-zero weights
    let num_nonzero_weights = solution.weights.iter().filter(|&&w| w != 0.0).count();

    // Compute normalised squared Frobenius norm
    //   (1 / (n² · scale²)) · Σ (target[i] - reconstructed[i])²
    let sq_frob: f64 = target_matrix
        .iter()
        .zip(reconstructed.iter())
        .map(|(&t, &r)| {
            let d = t as f64 - r;
            d * d
        })
        .sum();
    let normalised_sq_frob = sq_frob / ((n * n) as f64 * scale_f * scale_f);

    if tolerance == 0.0 {
        if normalised_sq_frob != 0.0 {
            // Find first mismatch for a helpful message
            for i in 0..(n * n) {
                if (target_matrix[i] as f64 - reconstructed[i]).abs() != 0.0 {
                    println!(
                        "    Reconstruction mismatch at index {}: expected {}, got {}",
                        i, target_matrix[i], reconstructed[i]
                    );
                    return Ok(false);
                }
            }
        }
        println!(
            "    Valid decomposition with {} permutation matrices",
            num_nonzero_weights
        );
    } else {
        println!(
            "    {} permutation matrices, normalised Frobenius² = {:.6e} (tolerance {:.6e})",
            num_nonzero_weights, normalised_sq_frob, tolerance
        );
        if normalised_sq_frob > tolerance {
            return Ok(false);
        }
    }

    Ok(true)
}

/// QOBLIB Birkhoff Decomposition Solution Checker
#[derive(Parser)]
#[command(version = VERSION, about, long_about = None)]
struct Cli {
    /// Path to the JSON instance file
    instance_file: String,

    /// Path to the JSON solution file
    solution_file: String,

    /// Maximum allowed normalised squared Frobenius error.
    /// When omitted (or 0), an exact integer reconstruction is required.
    /// Use a small positive value (e.g. 1e-6) to accept approximate solutions.
    #[arg(long, default_value_t = 0.0, value_parser = parse_tolerance)]
    tolerance: f64,
}

fn parse_tolerance(s: &str) -> Result<f64, String> {
    let v: f64 = s.parse().map_err(|_| format!("'{s}' is not a valid float"))?;
    if v < 0.0 {
        return Err(format!("tolerance must be non-negative, got {v}"));
    }
    Ok(v)
}

fn main() {
    // Exit-code contract (see misc/ci/CHECKER_CONTRACT.md):
    //   0  VALID        valid file, feasible
    //   21 INFEASIBLE   valid file, one or more instances fail verification
    //   10 INVALID_FILE unparseable solution file (raised via this hook)
    //   2  USAGE        bad arguments
    std::panic::set_hook(Box::new(|info| {
        eprintln!("INVALID_FILE: {info}");
        std::process::exit(10);
    }));

    println!(
        "QOBLIB Birkhoff Decomposition Solution Checker Version {}",
        VERSION
    );

    let cli = Cli::parse();
    let tolerance = cli.tolerance;

    // Load instance file (a support file: read/parse failures are USAGE, not a
    // statement about the solution).
    let instance_data = fs::read_to_string(&cli.instance_file).unwrap_or_else(|err| {
        eprintln!("USAGE: reading instance file {} failed: {err}", cli.instance_file);
        std::process::exit(2);
    });

    let instance_file: InstanceFile = serde_json::from_str(&instance_data)
        .unwrap_or_else(|err| {
            eprintln!("USAGE: parsing instance JSON failed: {err}");
            std::process::exit(2);
        });

    // Load solution file (unreadable file is USAGE/infra; malformed content below
    // is funnelled to INVALID_FILE by the panic hook).
    let solution_data = fs::read_to_string(&cli.solution_file).unwrap_or_else(|err| {
        eprintln!("USAGE: reading solution file {} failed: {err}", cli.solution_file);
        std::process::exit(2);
    });

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
            match check_birkhoff_decomposition(instance, solution, tolerance) {
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
            "INFEASIBLE: {} of {} instances failed",
            failed,
            passed + failed
        );
        std::process::exit(21);
    }
}
