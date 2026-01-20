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

use std::{
    fs::File,
    io::{self, BufWriter, Write},
};

use rand::{
    distributions::{Distribution, Uniform},
    rngs::StdRng,
    seq::IteratorRandom,
    SeedableRng,
};

use crate::utils::{check_range, compute_slack, random_bin_vector};

/// Struct representing a random integer linear problem instance:
/// - `solution` is a feasible binary solution vector.
/// - `rhs` is the right-hand side vector for each row.
/// - `rows` is a list of matrix rows (each row is a vector of coefficients).
pub struct Instance {
    solution: Vec<bool>,
    rhs: Vec<i32>,
    rows: Vec<Vec<i32>>,
}

impl Instance {
    /// Main constructor for `Instance`. Currently supports only the KochRandom variant.
    pub fn new(
        num_rows: usize,
        num_cols: usize,
        max_coeff: i32,
        seed: u64,
        verbose: bool,
    ) -> Instance {
        let mut rng = StdRng::seed_from_u64(seed);

        Instance::new_random(num_rows, num_cols, max_coeff, &mut rng, verbose)
    }

    /// Generates an instance using the Koch approach:
    ///  1. Create a random binary `solution` vector (roughly half ones, half zeros).
    ///  2. For each row, fill it with random coefficients in [0, max_coeff - 1].
    ///  3. Set the row's RHS to half the sum of that row's coefficients.
    ///  4. Attempt to make the instance feasible by:
    ///     - Greedily swapping coefficients between 1/0 positions to fix slack.
    ///     - If still infeasible, adjust some entries up/down.
    fn new_random(
        num_rows: usize,
        num_cols: usize,
        max_coeff: i32,
        rng: &mut StdRng,
        verbose: bool,
    ) -> Instance {
        // Bounds for generating random coefficients
        let low = 0;
        let high = max_coeff - 1;

        // 1. Generate a random solution vector (binary)
        let solution = random_bin_vector(num_cols, rng);

        // Count how many entries in `solution` are 1
        let num_ones: usize = solution.iter().map(|&b| b as usize).sum();

        // Separate indices for 1 and 0 entries
        let mut one_indices = Vec::new();
        let mut zero_indices = Vec::new();
        for (idx, value) in solution.iter().enumerate() {
            if *value {
                one_indices.push(idx);
            } else {
                zero_indices.push(idx);
            }
        }

        let mut rhs = Vec::<i32>::with_capacity(num_rows);
        let mut rows = Vec::<Vec<i32>>::with_capacity(num_rows);

        // Uniform distribution for sampling
        let range = Uniform::new(low, high);

        // 2. Generate random rows
        for _ in 0..num_rows {
            let mut row: Vec<i32> = vec![0; num_cols];

            // Fill each entry with a random value in [low, high]
            for entry in row.iter_mut() {
                *entry = range.sample(rng);
            }

            // 3. Compute RHS as half of the sum of row's coefficients
            let sum: i32 = row.iter().sum();
            rhs.push(sum / 2);
            rows.push(row);
        }

        // Build the Instance struct
        let mut instance = Instance {
            solution,
            rhs,
            rows,
        };

        // 4. Attempt to make each row feasible with respect to `solution`
        if verbose {
            println!("Initial slack:");
            instance.print_slack();
        }

        'row_iterator: for (row_idx, row) in instance.rows.iter_mut().enumerate() {
            let mut slack = compute_slack(row, &instance.solution, instance.rhs[row_idx]);

            // If already feasible, move on
            if slack == 0 {
                if verbose {
                    println!("Row {} is already feasible", row_idx);
                }
                continue 'row_iterator;
            }

            loop {
                // Step 1: Greedily switch entries in row to reduce slack
                'phase_one: loop {
                    let previous_slack = slack;
                    let mut best_slack = slack.abs();
                    let mut best_indices = (0, 0);

                    // Try switching a '1' entry with a '0' entry
                    for (i, el_i) in one_indices.iter().map(|&idx| (idx, row[idx])) {
                        for (j, el_j) in zero_indices.iter().map(|&idx| (idx, row[idx])) {
                            let current_slack = slack + el_i - el_j;
                            if current_slack.abs() < best_slack {
                                best_slack = current_slack.abs();
                                best_indices = (i, j);
                            }
                        }
                    }

                    // If we found a beneficial switch, apply it
                    if best_slack < previous_slack.abs() {
                        row.swap(best_indices.0, best_indices.1);
                        // Update slack
                        slack = compute_slack(row, &instance.solution, instance.rhs[row_idx]);
                    } else {
                        if verbose {
                            println!(
                                "Row {} couldn't find a beneficial switch (slack = {})",
                                row_idx, slack
                            );
                        }
                        break 'phase_one;
                    }

                    // Check if we've fixed slack
                    if slack == 0 {
                        if verbose {
                            println!("Row {} is now feasible - via switching", row_idx);
                        }
                        assert_eq!(
                            compute_slack(row, &instance.solution, instance.rhs[row_idx]),
                            0
                        );
                        continue 'row_iterator;
                    }
                }

                // Step 2: Adjust entries in matrix to fix slack if switching was insufficient
                let num_cols_to_adjust =
                    (2 * num_ones / 3).min(slack.unsigned_abs() as usize).max(1);
                let adjustment = slack / num_cols_to_adjust as i32;

                // We expect a non-zero adjustment or we'll loop forever
                assert_ne!(adjustment, 0);

                for _ in 0..num_cols_to_adjust {
                    // Choose a random '1' index that can handle +adjustment
                    let i = one_indices
                        .iter()
                        .filter(|&idx| {
                            row[*idx] + adjustment >= low && row[*idx] + adjustment <= high
                        })
                        .choose(rng)
                        .expect("No feasible adjustment on a '1' entry");

                    // Choose a random '0' index that can handle -adjustment
                    let j = zero_indices
                        .iter()
                        .filter(|&idx| {
                            row[*idx] - adjustment >= low && row[*idx] - adjustment <= high
                        })
                        .choose(rng)
                        .expect("No feasible adjustment on a '0' entry");

                    // Apply the adjustments
                    row[*i] += adjustment;
                    row[*j] -= adjustment;
                }

                slack = compute_slack(row, &instance.solution, instance.rhs[row_idx]);
                if slack == 0 {
                    if verbose {
                        println!("Row {} is now feasible - via adjustment", row_idx);
                    }
                    continue 'row_iterator;
                }

                if verbose {
                    println!("Row {} remains infeasible (slack = {})", row_idx, slack);
                }
            }
        }

        // Final check: Ensure overall feasibility
        for (row_idx, row) in instance.rows.iter().enumerate() {
            let slack = compute_slack(row, &instance.solution, instance.rhs[row_idx]);
            assert_eq!(slack, 0);
            assert!(check_range(row, low, high), "Row {} out of range", row_idx);
        }

        instance
    }

    /// Helper to print the slack for each row (RHS - sum of selected columns).
    fn print_slack(&self) {
        for (row_idx, row) in self.rows.iter().enumerate() {
            let slack = compute_slack(row, &self.solution, self.rhs[row_idx]);
            println!("Row {}: slack = {}", row_idx, slack);
        }
    }

    /// Write the instance to a file:
    ///  - First line: number of rows, number of columns
    ///  - For each row: coefficients followed by the row's RHS
    ///  - Finally, a commented-out line with the feasible binary solution.
    pub fn write_file(&self, filename: &str) -> io::Result<()> {
        let file = File::create(filename)?;
        let mut writer = BufWriter::new(file);

        // Print dimensions
        writeln!(writer, "{}\t{}", self.rhs.len(), self.solution.len())?;

        // For each row, print the coefficients followed by the corresponding RHS value
        for (row_idx, row) in self.rows.iter().enumerate() {
            let row_str = row
                .iter()
                .map(|value| format!("{:>5}", value))
                .collect::<Vec<_>>()
                .join(" ");
            writeln!(writer, "{} {:>5}", row_str, self.rhs[row_idx])?;
        }

        // Print the solution as a comment
        let solution_str = self
            .solution
            .iter()
            .map(|&b| if b { "1" } else { "0" })
            .collect::<Vec<_>>()
            .join(" ");
        writeln!(writer, "# Solution: {}", solution_str)?;

        writer.flush()?;
        Ok(())
    }

    pub fn write_gurobi_sol(&self, filename: &str) -> io::Result<()> {
        let file = File::create(filename)?;
        let mut writer = BufWriter::new(file);

        writeln!(writer, "# Solution for {}", filename.replace(".sol", ""))?;
        writeln!(writer, "# Objective value = 0")?;

        for (row_idx, &in_sol) in self.solution.iter().enumerate() {
            writeln!(writer, "x#{} {}", row_idx + 1, if in_sol { 1 } else { 0 })?;
        }

        writer.flush()?;
        Ok(())
    }

    #[allow(dead_code)]
    /// Print the entire instance to stdout (debug purposes).
    pub fn print(&self) {
        println!("Solution: {:?}", self.solution);
        println!("RHS: {:?}", self.rhs);
        println!("Rows: {:?}", self.rows);
    }
}
