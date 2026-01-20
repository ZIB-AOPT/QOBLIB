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
QBench Market Split Problem Solution Checker
25Dec2024-26Dec2024
Copyright (C) 2025 by Thorsten Koch

This program reads a market split problem from qbench and a solutions and checks whether it is a feasible solution.
*/
const VERSION : &str = "1.0";

use std::fs;
use std::env;
use regex::Regex;

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
fn extract_solution_01(data : &[u8], dim : usize) -> Vec<u32> {
    let mut solution = Vec::<u32>::new();
    let mut i = 0;
    while i < data.len() {
        let c = data[i] as char;
        if c == '0' || c == '1' {
            solution.push((data[i] - b'0') as u32);
        } else if !c.is_ascii_whitespace() && !c.is_ascii_punctuation() { 
            panic!("Parsing solution. Expected 0/1 found {}", c);    
        } 
        i += 1;
    }
    if solution.len() != dim {
        panic!("Expected solution length {dim} but found {}", solution.len());
    }
    solution
}

fn extract_solution_numb(data : &[u8], dim : usize) -> Vec<u32> {
    let mut solution   = vec![0u32; dim];
    let mut lineno = 1;
    let mut index  = 0;
    let mut i      = 0;

    while i < data.len() {
        let c = data[i] as char;

        if c.is_ascii_whitespace() || c.is_ascii_punctuation() {
            if index > 0 {
                solution[index - 1] = 1;
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


fn extract_solution_text(data: &[u8], dim: usize) -> Vec<u32> {
    let mut solution = vec![0u32; dim];
    let re = Regex::new(r"x#(\d+)\s+([01])").unwrap();
    let text = std::str::from_utf8(data).expect("Invalid UTF-8 sequence");

    for (lineno, cap) in re.captures_iter(text).enumerate() {
        let index: usize = cap[1].parse().unwrap_or_else(|err| panic!("Solution line {}. Expected variable index: {err}", lineno + 1));
        if index < 1 || index > dim {
            panic!("Solution line {}. Expected variable index between 1..{}: found {}", lineno + 1, dim, index);
        }
        let value: u32 = cap[2].parse().unwrap();
        solution[index - 1] = value;
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

fn detect_solution_format(data : &[u8]) -> SolutionFormat {
    let mut format = SolutionFormat::OnlySpace;

    for b in data {
        let c = *b as char;

        if format == SolutionFormat::OnlySpace && !c.is_ascii_whitespace() {
            format = SolutionFormat::ZeroOneVec;
        }
        if format == SolutionFormat::ZeroOneVec && !c.is_ascii_whitespace() && !c.is_ascii_punctuation() && c != '0' && c != '1' {
            format = SolutionFormat::IndexList;
        }
        if format == SolutionFormat::IndexList && !c.is_ascii_whitespace() && !c.is_ascii_punctuation() && !c.is_ascii_digit() {
            format = SolutionFormat::XVarList;
            break;
        }
    }
    format
}

fn extract_solution(data : &[u8], dim : usize) -> Vec<u32> {
    match detect_solution_format(data) {
        SolutionFormat::OnlySpace  => panic!("Parsing solution: found empty file"),
        SolutionFormat::ZeroOneVec => extract_solution_01(data, dim),
        SolutionFormat::IndexList  => extract_solution_numb(data, dim),
        SolutionFormat::XVarList   => extract_solution_text(data, dim)
    }
}

fn verify_solution(instance_data : &str, solution_data : &[u8]) -> bool {
    let mut solution = Vec::<u32>::new();	
    let mut num_cons = 0;
    let mut num_vars = 0;
    let mut cnt_cons = 0;
    let mut verified = true;

    for (lineno, line) in instance_data.replace(",", " ").lines().enumerate() {
        let fields : Vec<&str> = line.split_whitespace().collect();

        // Ignore empty lines or line starting with "#"
        if fields.is_empty() || fields[0].starts_with('#') {
            continue;
        }
        // The first non comment line has the number of constraints nodes and variables
        if fields.len() >= 2 && num_cons == 0 && num_vars == 0 {
            num_cons = fields[0].parse::<usize>().unwrap_or_else(|err| panic!("Line {} expected number of constraints: {err}", lineno + 1));
            num_vars = fields[1].parse::<usize>().unwrap_or_else(|err| panic!("Line {} expected number of variables: {err}", lineno + 1));

            solution = extract_solution(solution_data, num_vars);
            println!("Problem has {num_vars} variables.");
            continue;
        }
        // Other lines have format: value value ... value Weight
        if fields.len() > num_vars && num_cons > 0 {
            let mut sum = 0;
            let mut tot = 0;

            for i in 0..num_vars { 
                let val : u32 = fields[i].parse().unwrap_or_else(|err| panic!("Line {} expected value: {err}", lineno + 1));
                tot += val;
                sum += val * solution[i];
            }
            let rhs : u32 = fields[num_vars].parse().unwrap_or_else(|err| panic!("Line {} expected value: {err}", lineno + 1));

            cnt_cons += 1;

            if tot / 2 != rhs {
                panic!("Constraint {cnt_cons} line {} RHS expected {} found {rhs}", lineno + 1, tot / 2);
            }

            print!("Constraint {cnt_cons} ");
            if sum == rhs {
                println!("ok");
            } else {
                println!("failed: expected {rhs} got {sum}");
                verified = false;
            }
            continue;
        }
        panic!("Line {} syntax error", lineno + 1);
    }
    if cnt_cons != num_cons {
        panic!("Expected {num_cons} constraints, got {cnt_cons}");
    }
   
    verified
}
fn main() {
    println!("Qbench Market Split Solution Checker Version {VERSION}");

    let args: Vec<String> = env::args().collect();

    if args.len() < 3 {
        panic!("usage: {} instance-file solution-file|01-string", &args[0]);
    }
    let instance_data = fs::read_to_string(&args[1]).unwrap_or_else(|err| panic!("Reading {} failed: {err}", args[1]));

    let solution_arg = &args[2];

    // Check if a string consists only of '1's and '0's
    let is_binary = |s: &str| s.chars().all(|c| c == '0' || c == '1');

    let solution_data = if is_binary(solution_arg) {
        solution_arg.as_bytes().to_vec()
    } else {
        fs::read(solution_arg).unwrap_or_else(|err| panic!("Reading {} failed: {err}", solution_arg))
    };

    // Verify solution, exit with code 0 if valid, 1 if invalid
    if verify_solution(&instance_data, &solution_data) {
        println!("VALID: Solution successfully verified");
        std::process::exit(0);
    } else {
        println!("INVALID: Solution failed verification");
        std::process::exit(1);
    }
}

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
