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
 * Network Flow Solution Checker
 * Verifies that the given solution satisfies all constraints of the network flow problem.
 *
 * MS 2026-01-10 - Initial version
 *
 * Usage: check_network <instance_size> <demand_file> <solution_file>
 */
use regex::Regex;
use std::collections::HashMap;
use std::env;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::PathBuf;

const INTSCALE: i32 = 1000;

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() != 4 {
        eprintln!(
            "Usage: {} <instance_size> <demand_file> <solution_file>",
            args[0]
        );
        eprintln!("  instance_size: number of nodes (5-24)");
        eprintln!("  demand_file: path to demand matrix file");
        eprintln!("  solution_file: path to Gurobi solution file");
        std::process::exit(2);
    }

    let n: usize = match args[1].parse() {
        Ok(num) if num >= 5 && num <= 24 => num,
        _ => {
            eprintln!("Error: instance_size must be between 5 and 24");
            std::process::exit(2);
        }
    };

    let demand_path = PathBuf::from(&args[2]);
    let sol_path = PathBuf::from(&args[3]);

    // Read demand matrix
    let demand_matrix = match parse_demand_file(&demand_path, n) {
        Ok(matrix) => matrix,
        Err(e) => {
            eprintln!("ERROR: {}", e);
            std::process::exit(2);
        }
    };

    let result = run_checker(n, &demand_matrix, &sol_path);

    match result {
        Ok(true) => {
            std::process::exit(0);
        }
        Ok(false) => {
            println!("INVALID: Solution verification failed");
            std::process::exit(1);
        }
        Err(e) => {
            eprintln!("ERROR: {}", e);
            std::process::exit(2);
        }
    }
}

fn run_checker(
    n: usize,
    demand_matrix: &Vec<Vec<i32>>,
    sol_path: &PathBuf,
) -> Result<bool, String> {
    // Parse solution file
    let (x_vars, f_vars, z_value) = parse_solution(sol_path, n)?;

    // Check 1: Each node has out-degree = 2
    for i in 1..=n {
        let outdegree: i32 = (1..=n)
            .filter(|&j| j != i)
            .map(|j| *x_vars.get(&(i, j)).unwrap_or(&0))
            .sum();

        if outdegree != 2 {
            println!(
                "INVALID: Node {} has out-degree {} (expected 2)",
                i, outdegree
            );
            return Ok(false);
        }
    }

    // Check 2: Each node has in-degree = 2
    for j in 1..=n {
        let indegree: i32 = (1..=n)
            .filter(|&i| i != j)
            .map(|i| *x_vars.get(&(i, j)).unwrap_or(&0))
            .sum();

        if indegree != 2 {
            println!(
                "INVALID: Node {} has in-degree {} (expected 2)",
                j, indegree
            );
            return Ok(false);
        }
    }

    // Check 3: Flow conservation constraints
    // For each commodity k and node i (where i != k), flow in - flow out = demand[k][i]
    for k in 1..=n {
        for i in 1..=n {
            if i == k {
                continue;
            }

            // Flow into node i for commodity k
            let flow_in: i32 = (1..=n)
                .filter(|&j| j != i)
                .map(|j| *f_vars.get(&(k, j, i)).unwrap_or(&0))
                .sum();

            // Flow out of node i for commodity k (excluding flow to k itself)
            let flow_out: i32 = (1..=n)
                .filter(|&j| j != i && j != k)
                .map(|j| *f_vars.get(&(k, i, j)).unwrap_or(&0))
                .sum();

            let expected_demand = demand_matrix[k][i] * INTSCALE;
            let net_flow = flow_in - flow_out;

            if net_flow != expected_demand {
                println!(
                    "INVALID: Flow conservation violated for commodity {} at node {}",
                    k, i
                );
                println!(
                    "  Flow in: {}, Flow out: {}, Net: {}, Expected: {}",
                    flow_in, flow_out, net_flow, expected_demand
                );
                return Ok(false);
            }
        }
    }

    // Check 4: Flow capacity constraints
    // For each edge (i,j), if x[i,j] = 0, then all flows on it should be 0
    for i in 1..=n {
        for j in 1..=n {
            if i == j {
                continue;
            }

            let edge_exists = *x_vars.get(&(i, j)).unwrap_or(&0);

            if edge_exists == 0 {
                // Check that no flow uses this edge
                for k in 1..=n {
                    if k == j {
                        continue;
                    }
                    let flow = *f_vars.get(&(k, i, j)).unwrap_or(&0);
                    if flow != 0 {
                        println!("INVALID: Flow {} on non-existent edge ({}, {})", flow, i, j);
                        return Ok(false);
                    }
                }
            }
        }
    }

    // Check 5: Compute objective value and verify
    let mut max_flow = 0;
    for i in 1..=n {
        for j in 1..=n {
            if i == j {
                continue;
            }

            // Sum all commodity flows on edge (i,j)
            let total_flow: i32 = (1..=n)
                .filter(|&k| k != j)
                .map(|k| *f_vars.get(&(k, i, j)).unwrap_or(&0))
                .sum();

            if total_flow > max_flow {
                max_flow = total_flow;
            }
        }
    }

    println!("Computed maximum flow: {}", max_flow);
    println!("Solution objective value: {}", z_value);

    if max_flow != z_value {
        println!(
            "WARNING: Computed objective ({}) doesn't match solution objective ({})",
            max_flow, z_value
        );
        // Don't fail on this, just warn
    }

    println!("VALID: Solution successfully verified");
    Ok(true)
}

/// Parse a Gurobi solution file
/// Returns (x_vars, f_vars, z_value)
fn parse_solution(
    path: &PathBuf,
    n: usize,
) -> Result<
    (
        HashMap<(usize, usize), i32>,
        HashMap<(usize, usize, usize), i32>,
        i32,
    ),
    String,
> {
    let file = File::open(path).map_err(|e| format!("Cannot open file: {}", e))?;
    let reader = BufReader::new(file);

    let mut x_vars: HashMap<(usize, usize), i32> = HashMap::new();
    let mut f_vars: HashMap<(usize, usize, usize), i32> = HashMap::new();
    let mut z_value = 0;

    // Regex patterns for parsing
    let x_re = Regex::new(r"^x#(\d+)#(\d+)\s+(\d+)$").unwrap();
    let f_re = Regex::new(r"^f#(\d+)#(\d+)#(\d+)\s+(\d+)$").unwrap();
    let z_re = Regex::new(r"^z\s+(\d+)$").unwrap();

    for line_result in reader.lines() {
        let line = line_result.map_err(|e| e.to_string())?;
        let trimmed = line.trim();

        // Skip comments and empty lines
        if trimmed.is_empty() || trimmed.starts_with('#') {
            continue;
        }

        // Try to match z variable
        if let Some(caps) = z_re.captures(trimmed) {
            z_value = caps[1]
                .parse::<i32>()
                .map_err(|e| format!("Error parsing z value: {}", e))?;
            continue;
        }

        // Try to match x variable
        if let Some(caps) = x_re.captures(trimmed) {
            let i = caps[1]
                .parse::<usize>()
                .map_err(|e| format!("Error parsing x variable: {}", e))?;
            let j = caps[2]
                .parse::<usize>()
                .map_err(|e| format!("Error parsing x variable: {}", e))?;
            let value = caps[3]
                .parse::<i32>()
                .map_err(|e| format!("Error parsing x variable: {}", e))?;

            if i > n || j > n || i == j {
                return Err(format!("Invalid x variable indices: x#{}#{}", i, j));
            }

            x_vars.insert((i, j), value);
            continue;
        }

        // Try to match f variable
        if let Some(caps) = f_re.captures(trimmed) {
            let k = caps[1]
                .parse::<usize>()
                .map_err(|e| format!("Error parsing f variable: {}", e))?;
            let i = caps[2]
                .parse::<usize>()
                .map_err(|e| format!("Error parsing f variable: {}", e))?;
            let j = caps[3]
                .parse::<usize>()
                .map_err(|e| format!("Error parsing f variable: {}", e))?;
            let value = caps[4]
                .parse::<i32>()
                .map_err(|e| format!("Error parsing f variable: {}", e))?;

            if k > n || i > n || j > n || i == j {
                return Err(format!("Invalid f variable indices: f#{}#{}#{}", k, i, j));
            }

            f_vars.insert((k, i, j), value);
            continue;
        }
    }

    Ok((x_vars, f_vars, z_value))
}

/// Parse demand matrix from file
/// Expected format: CSV-like with pipe separators and row labels
/// Example: |1  | 0, 24, 43, 23, ...
/// The file may contain a larger matrix than needed; we extract only the first n rows and columns
fn parse_demand_file(path: &PathBuf, n: usize) -> Result<Vec<Vec<i32>>, String> {
    let file = File::open(path).map_err(|e| format!("Cannot open demand file: {}", e))?;
    let reader = BufReader::new(file);

    // Initialize n+1 x n+1 matrix (1-indexed, so row 0 and col 0 unused)
    let mut matrix = vec![vec![0; n + 1]; n + 1];

    let mut row_count = 0;

    for line_result in reader.lines() {
        let line = line_result.map_err(|e| e.to_string())?;
        let trimmed = line.trim();

        // Skip empty lines
        if trimmed.is_empty() {
            continue;
        }

        // Skip header line (starts with just spaces and pipes)
        if trimmed.starts_with('|') && !trimmed.chars().nth(1).unwrap_or(' ').is_numeric() {
            continue;
        }

        // Parse data lines like: |1  | 0, 24, 43, 23, 21, ...
        if let Some(pipe_pos) = trimmed.find('|') {
            let after_first_pipe = &trimmed[pipe_pos + 1..];
            if let Some(second_pipe_pos) = after_first_pipe.find('|') {
                let row_label = after_first_pipe[..second_pipe_pos].trim();
                let row_idx: usize = match row_label.parse() {
                    Ok(idx) if idx >= 1 && idx <= n => idx,
                    Ok(_) => continue, // Skip rows beyond n
                    _ => continue,     // Skip invalid row labels
                };

                let values_str = &after_first_pipe[second_pipe_pos + 1..];
                // Remove trailing pipe if present
                let values_str = values_str.trim_end_matches('|').trim();

                // Parse comma-separated values, but only keep the first n
                let values: Vec<i32> = values_str
                    .split(',')
                    .take(n) // Only take the first n columns
                    .map(|s| s.trim().parse::<i32>())
                    .collect::<Result<Vec<_>, _>>()
                    .map_err(|e| format!("Error parsing demand values: {}", e))?;

                if values.len() != n {
                    return Err(format!(
                        "Row {} has {} values (after taking first {}), expected {}",
                        row_idx,
                        values.len(),
                        n,
                        n
                    ));
                }

                // Store values (1-indexed)
                for (col_idx, &value) in values.iter().enumerate() {
                    matrix[row_idx][col_idx + 1] = value;
                }

                row_count += 1;
            }
        }
    }

    if row_count != n {
        return Err(format!(
            "Demand file has {} rows (up to row {}), expected {}",
            row_count, n, n
        ));
    }

    Ok(matrix)
}
