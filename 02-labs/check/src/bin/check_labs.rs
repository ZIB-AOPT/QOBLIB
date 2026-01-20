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
QBench Low Autocorrelation Binary Sequence (LABS) Solution Checker
27Dec2024
Copyright (C) 2025 by Thorsten Koch

This program reads a LABS solution computes it quality.
*/
const VERSION: &str = "1.0";

use std::env;
use std::fs;

/* possilble solution formats:
  # comment
  x#1  1
  x#2  0
  ...
  Important: Only lines starting with "x" are looked at.
  The next number coming after the "x" is the index of the variable between 1..number-of-variables
  Then everything is ignored until some whitespace is encountered.
  The next digit after the whitespace must then be either 0 or 1.
  Everything afterwards is ignored.
  Missing indices are set to zero.
  Be aware that 0.9999999 is taken as 0

  or
  01110001110000111000110 or 0 1 0 0 0 1 0 1 0 1 0 1 0 or 0,1,0,0,0,1,0,1,0,1,0,1,0
  or
  1
  0
  1
  ...
*/
fn extract_solution_01(data: &[u8], dim: usize) -> Vec<i32> {
    let mut solution = Vec::<i32>::new();
    let mut i = 0;

    while i < data.len() {
        let c = data[i] as char;
        if c == '0' || c == '1' {
            solution.push(1 - 2 * ((data[i] - b'0') as i32));
        } else if !c.is_ascii_whitespace() && !c.is_ascii_punctuation() {
            panic!("Parsing solution. Expected 0/1 found {}", c);
        }
        i += 1;
    }
    if solution.len() != dim {
        panic!(
            "Expected solution length {dim} but found {}",
            solution.len()
        );
    }
    solution
}

fn extract_solution_numb(data: &[u8], dim: usize) -> Vec<i32> {
    let mut solution = vec![1i32; dim];
    let mut lineno = 1;
    let mut index = 0;
    let mut i = 0;

    while i < data.len() {
        let c = data[i] as char;

        if c.is_ascii_whitespace() || c.is_ascii_punctuation() {
            if index > 0 {
                solution[index - 1] = -1;
                index = 0;
            }
            if c == '\n' {
                lineno += 1;
            }
        }
        if c.is_ascii_digit() {
            index = index * 10 + ((data[i] - b'0') as usize);
            if index > dim {
                panic!("Solution line {lineno}. Expected variable index between 1..{dim}: found {index}");
            }
        }
        i += 1;
    }
    solution
}

fn extract_solution_text(data: &[u8], dim: usize) -> Vec<i32> {
    let mut solution = vec![0i32; dim];
    let mut lineno = 1;
    let mut field = 0;
    let mut index = 0;
    let mut i = 0;
    // field      0       1      2      3       3      4     5
    //        [space]? x [text]? index [text]? [space] [10] [garbage]? \n
    //        # \n
    while i < data.len() {
        let c = data[i] as char;

        if c == '\n' {
            lineno += 1;
            field = 0;
            index = 0;
        }
        match field {
            // If we start with a comment marker, we ignore the rest of the line
            0 => {
                if c == 'x' {
                    field = 1;
                } else if !c.is_ascii_whitespace() {
                    // We ignore lines that do not start with x
                    field = 5;
                }
            }
            // We ignore everything until we found some digit
            1 => {
                if c.is_ascii_digit() {
                    field = 2;
                    index = (data[i] - b'0') as usize;
                }
            }
            // We collect the index
            2 => {
                if c.is_ascii_digit() {
                    index = index * 10 + ((data[i] - b'0') as usize);
                } else {
                    // When finished we check whether within bounds
                    if index < 1 || index > dim {
                        panic!("Solution line {lineno}. Expected variable index between 1..{dim}: found {index}");
                    }
                    index -= 1;
                    field = if c.is_ascii_whitespace() { 4 } else { 3 };
                }
            }
            // After index we ignore everything until we find some whitespace
            3 => {
                if c.is_ascii_whitespace() {
                    field = 4;
                }
            }
            // The next character after the whitespace should be either 0 or 1
            4 => {
                if c == '0' || c == '1' {
                    solution[index] = 1 - 2 * ((data[i] - b'0') as i32);
                    field = 5;
                } else {
                    panic!("Solution line {lineno}. Expected 0/1 found {c}");
                }
            }
            // We ignore everything after we got what we wanted
            _ => (),
        }
        i += 1;
    }
    solution
}

#[derive(PartialEq)]
enum SolutionFormat {
    OnlySpace,
    ZeroOneVec,
    IndexList,
    XVarList,
}

fn detect_solution_format(data: &[u8]) -> SolutionFormat {
    let mut format = SolutionFormat::OnlySpace;

    for b in data {
        let c = *b as char;

        if format == SolutionFormat::OnlySpace && !c.is_ascii_whitespace() {
            format = SolutionFormat::ZeroOneVec;
        }
        if format == SolutionFormat::ZeroOneVec
            && !c.is_ascii_whitespace()
            && !c.is_ascii_punctuation()
            && c != '0'
            && c != '1'
        {
            format = SolutionFormat::IndexList;
        }
        if format == SolutionFormat::IndexList
            && !c.is_ascii_whitespace()
            && !c.is_ascii_punctuation()
            && !c.is_ascii_digit()
        {
            format = SolutionFormat::XVarList;
            break;
        }
    }
    format
}

fn extract_solution(data: &[u8], dim: usize) -> Vec<i32> {
    match detect_solution_format(data) {
        SolutionFormat::OnlySpace => panic!("Parsing solution: found empty file"),
        SolutionFormat::ZeroOneVec => extract_solution_01(data, dim),
        SolutionFormat::IndexList => extract_solution_numb(data, dim),
        SolutionFormat::XVarList => extract_solution_text(data, dim),
    }
}

fn autocorrelation(k: usize, j: usize, solution: &[i32]) -> i32 {
    let mut sum = 0;
    for i in 0..k - j {
        sum += solution[i] * solution[i + j];
    }
    sum
}

fn sequenz_energy(k: usize, solution: &[i32]) -> i32 {
    let mut sum = 0;
    for j in 1..=k - 1 {
        let ac = autocorrelation(k, j, solution);
        sum += ac * ac;
    }
    sum
}

fn print_count(count: i32) {
    if count < 10 {
        print!("{count}");
    } else if count < 36 {
        print!("{}", (b'a' + (count - 10) as u8) as char);
    } else if count < 62 {
        print!("{}", (b'A' + (count - 36) as u8) as char);
    } else {
        print!("<{count}>")
    }
}

fn print_llc(solution: &[i32]) {
    let mut count = 0;
    let mut prev = solution[0];

    for s in solution {
        if *s == prev {
            count += 1;
        } else {
            print_count(count);
            count = 1;
            prev = *s;
        }
    }
    print_count(count);
    println!("");
}

fn verify_solution(k: usize, solution_data: &[u8]) -> bool {
    let optimal_solution = [
        0, 0, 0, 1, 2, 2, 7, 3, 8, 12, 13, 5, 10, 6, 19, 15, 24, 32, 25, 29, 26, 26, 39, 47, 36,
        36, 45, 37, 50, 62, 59, 67, 64, 64, 65, 73, 82, 86, 87, 99, 108, 108, 101, 109, 122, 118,
        131, 135, 140, 136, 153, 153, 166, 170, 175, 171, 192, 188, 197, 205, 218, 226, 235, 207,
        208, 240, 257,
    ]; // from Packebusch und Mertens, arXiv:1512.02475v2
    let mut verified = true;
    let solution = extract_solution(solution_data, k);
    let es = sequenz_energy(k, &solution);

    //for s in &solution {
    //    print!("{s} ");
    //}
    //println!("");

    print!("LABS k={k} E(S)={es} seq=");
    print_llc(&solution);

    if k >= 3 && k < optimal_solution.len() {
        if es == optimal_solution[k] {
            println!("OPTIMAL");
        } else {
            println!("NOT OPTIMAL, expected E(S)={}", optimal_solution[k]);
            verified = false;
        }
    } else {
        println!(
            "Results for k<3 and k>={} not known",
            optimal_solution.len()
        );
    }
    verified
}
fn main() {
    println!("Qbench LABS Solution Checker Version {VERSION}");

    let args: Vec<String> = env::args().collect();

    if args.len() < 3 {
        panic!(
            "usage: {} instance-size solution-file|01-string|LL-string",
            &args[0]
        );
    }
    let k: usize = args[1]
        .parse()
        .unwrap_or_else(|err| panic!("Expected problem size: {err}"));

    let solution_arg = &args[2];

    // Check if a string consists only of '1's and '0's
    let is_llcode = |s: &str| s.chars().all(|c| c.is_ascii_digit() && c != '0');

    let solution_data = if is_llcode(solution_arg) {
        solution_arg.as_bytes().to_vec()
    } else {
        fs::read_to_string(solution_arg)
            .unwrap_or_else(|err| panic!("Reading {} failed: {err}", solution_arg))
            .lines()
            .filter(|line| !line.starts_with('#'))
            .collect::<Vec<_>>()
            .join("\n")
            .into_bytes()
    };

    if verify_solution(k, &solution_data) {
        println!("VALID: Solution successfully verified");
        std::process::exit(0);
    } else {
        println!("INVALID: Solution failed verification");
        std::process::exit(1);
    }
}

/*
#[test]
fn verify_text_solution() {
    let instance =
    "3 20\n\
     62,  20  96  46  43  38,  64,  83,  39,  20,  31,  99,  53,  91,   7,  30,  72,  26,  81,  78, 539 \n\
      45,  32,   8,  58,  94,  53,  14,  33,  69,  93,  17,  95,  87,  74,  43,  26,  12,  31,  36,   5, 462 \n\
     29,36,3,34,47,96,  11,  28,   8,  38,  78,  28,  37,  13,   0,  21,  91,  58,  93,  15, 382\n ";

    let solution =
    b"# Solution for model obj\n\
      # Objective value = 0\n\
      s#1 0\n\
       s#2 0\n\
      s#3 0\n\
      x#20 1\n\
      x#19 0\n\
      x#18 1\n\
      x#17 1\n\
      x#16 1\n\
      x#15 1\n\
      x#14 1\n\
      x#13 0\n\
       x#12 1\n\
      x#11 1\n\
      x#10 0\n\
      x#9 1\n\
      x#8 0\n\
      x#7 0\n\
      x#6 0\n\
      x#5 0\n\
      x#4 1\n\
      x#3 0\n\
      x#2 1\n\
      x#1 0\n";

    verify_solution(instance, solution);
}

#[test]
fn verify_01_a_solution() {
    let instance =
    "3 20\n\
     62,  20  96  46  43  38,  64,  83,  39,  20,  31,  99,  53,  91,   7,  30,  72,  26,  81,  78, 539 \n\
      45,  32,   8,  58,  94,  53,  14,  33,  69,  93,  17,  95,  87,  74,  43,  26,  12,  31,  36,   5, 462 \n\
     29,36,3,34,47,96,  11,  28,   8,  38,  78,  28,  37,  13,   0,  21,  91,  58,  93,  15, 382\n ";

    let solution = b"01010000101101111101";

    assert_eq!(verify_solution(instance, solution), true);
}

#[test]
fn verify_01_b_solution() {
    let instance =
    "3 20\n\
     62,  20  96  46  43  38,  64,  83,  39,  20,  31,  99,  53,  91,   7,  30,  72,  26,  81,  78, 539 \n\
      45,  32,   8,  58,  94,  53,  14,  33,  69,  93,  17,  95,  87,  74,  43,  26,  12,  31,  36,   5, 462 \n\
     29,36,3,34,47,96,  11,  28,   8,  38,  78,  28,  37,  13,   0,  21,  91,  58,  93,  15, 382\n ";

    let solution = b"0,1,0;1..0  0 0 0 1, 0 ,11 011 1.1.1 0 1";

    assert_eq!(verify_solution(instance, solution), true);
}

#[test]
fn verify_wrong_solution() {
    let instance =
    "3 20\n\
     62,  20  96  46  43  38,  64,  83,  39,  20,  31,  99,  53,  91,   7,  30,  72,  26,  81,  78, 539 \n\
      45,  32,   8,  58,  94,  53,  14,  33,  69,  93,  17,  95,  87,  74,  43,  26,  12,  31,  36,   5, 462 \n\
     29,36,3,34,47,96,  11,  28,   8,  38,  78,  28,  37,  13,   0,  21,  91,  58,  93,  15, 382\n ";

    let solution = b"01010100111101111101";

    assert_eq!(verify_solution(instance, solution), false);
}
*/
