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

/*
Author: Maximilian Schicker
Last Change: 2021-04-14
Description: Main file for the market split generator
USAGE: cargo run --release -- -o hello.dat -s 42 -c 90 -r 10 -m 100
*/

use clap::{Arg, Command};
use instance::Instance;

mod instance;
mod utils;

fn main() {
    let matches = Command::new("Market Split Instance Generator")
        .version("1.0")
        .author("Maximilian Schicker <schicker@zib.de>")
        .about("Generates feasible market split instances")
        .arg(
            Arg::new("output")
                .short('o')
                .long("output")
                .value_name("FILE")
                .help("Output file")
                .default_value("ms_instance.dat"),
        )
        .arg(
            Arg::new("num_cols")
                .short('c')
                .long("num_cols")
                .value_name("NUM_COLS")
                .help("Number of columns in the instance")
                .default_value("40"),
        )
        .arg(
            Arg::new("num_rows")
                .short('r')
                .long("num_rows")
                .value_name("NUM_ROWS")
                .help("Number of rows in the instance")
                .default_value("5"),
        )
        .arg(
            Arg::new("max_coeff")
                .short('m')
                .long("max_coeff")
                .value_name("MAX_COEFF")
                .help("Maximum coefficient value")
                .default_value("100"),
        )
        .arg(
            Arg::new("seed")
                .short('s')
                .long("seed")
                .value_name("SEED")
                .help("Seed for the random number generator")
                .default_value("42"),
        )
        .arg(
            Arg::new("verbose")
                .short('v')
                .long("verbose")
                .help("Sets the level of verbosity")
                .action(clap::ArgAction::SetTrue),
        )
        .get_matches();

    let output_file = matches.get_one::<String>("output").unwrap();
    let num_cols: usize = matches
        .get_one::<String>("num_cols")
        .unwrap()
        .parse::<usize>()
        .expect("Invalid num_cols value");
    let num_rows: usize = matches
        .get_one::<String>("num_rows")
        .unwrap()
        .parse::<usize>()
        .expect("Invalid num_rows value");
    let max_coeff: i32 = matches
        .get_one::<String>("max_coeff")
        .unwrap()
        .parse::<i32>()
        .expect("Invalid max_coeff value");
    let seed: u64 = matches
        .get_one::<String>("seed")
        .unwrap()
        .parse::<u64>()
        .expect("Invalid seed value");
    let verbose = matches.get_flag("verbose");

    if verbose {
        println!("Output file: {}", output_file);
        println!("Number of columns: {}", num_cols);
        println!("Number of rows: {}", num_rows);
        println!("Max coefficient: {}", max_coeff);
        println!("Seed: {}", seed);
        println!("Generating instance...");
    }

    let instance = Instance::new(num_rows, num_cols, max_coeff, seed, verbose);

    let _ = instance.write_file(output_file);
    let _ = instance.write_gurobi_sol(&output_file.replace(".dat", ".sol"));

    println!("Instance written to {}", output_file);
}
