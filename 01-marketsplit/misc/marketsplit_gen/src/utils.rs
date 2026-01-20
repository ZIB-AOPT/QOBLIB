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

use rand::{distributions::Uniform, prelude::Distribution, rngs::StdRng, seq::SliceRandom};

/// Compute the slack (RHS - sum of selected entries) for a given row.
/// The sum of selected entries is where the corresponding position in `solution` is `true`.
pub fn compute_slack(row: &[i32], solution: &[bool], rhs: i32) -> i32 {
    let sum = row
        .iter()
        .zip(solution.iter())
        .map(|(a, b)| if *b { *a } else { 0 })
        .sum::<i32>();
    rhs - sum
}

pub fn check_range(row: &[i32], low: i32, high: i32) -> bool {
    row.iter().all(|&value| value >= low && value <= high)
}

/// Generate a random binary vector of size `size`.
/// Approximately half of its entries are 1, half are 0 (with a small +/- offset).
pub fn random_bin_vector(size: usize, rng: &mut StdRng) -> Vec<bool> {
    let range = Uniform::new_inclusive(0, 4);

    // Randomly pick how many 1's we want, around half of `size`
    let num_ones = (size / 2) + range.sample(rng) - 2;
    let num_zeros = size - num_ones;

    // Fill the vector with `true` for 1's, `false` for 0's
    let mut binary_vector = vec![true; num_ones];
    binary_vector.extend(vec![false; num_zeros]);

    // Shuffle to get random distribution of 1's and 0's
    binary_vector.shuffle(rng);

    binary_vector
}
