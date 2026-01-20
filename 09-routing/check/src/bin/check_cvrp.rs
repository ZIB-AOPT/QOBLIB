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
QBench Capacitated Vehicle Routing Problem Solution Checker
Maximilian Schicker - 12Jan2026
Copyright (C) 2026

This program reads a CVRP problem in TSPLIB/CVRPLIB format and a solution and 
checks whether it is a feasible solution, computing the total cost.
*/
const VERSION: &str = "1.0";

use std::fs;
use std::env;
use regex::Regex;

#[derive(Debug)]
struct Instance {
    name: String,
    num_nodes: usize,
    capacity: i32,
    coords: Vec<(f64, f64)>,
    demands: Vec<i32>,
    depot: usize,
}

#[derive(Debug)]
struct Solution {
    routes: Vec<Vec<usize>>,
    cost: Option<i32>,
}

fn parse_instance(data: &str) -> Instance {
    let mut name = String::new();
    let mut num_nodes = 0;
    let mut capacity = 0;
    let mut coords = Vec::new();
    let mut demands = Vec::new();
    let mut depot = 1;
    
    let mut section = "";
    
    for line in data.lines() {
        let line = line.trim();
        
        // Skip empty lines and comments
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        
        // Check for section markers
        if line.contains("NODE_COORD_SECTION") {
            section = "coords";
            continue;
        } else if line.contains("DEMAND_SECTION") {
            section = "demands";
            continue;
        } else if line.contains("DEPOT_SECTION") {
            section = "depot";
            continue;
        } else if line == "EOF" || line == "-1" {
            if section == "depot" {
                section = "";
            }
            continue;
        }
        
        // Parse header fields
        if line.starts_with("NAME") {
            name = line.split(':').nth(1).unwrap_or("").trim().to_string();
            continue;
        } else if line.starts_with("DIMENSION") {
            num_nodes = line.split(':').nth(1).unwrap_or("0").trim().parse().unwrap_or(0);
            continue;
        } else if line.starts_with("CAPACITY") {
            capacity = line.split(':').nth(1).unwrap_or("0").trim().parse().unwrap_or(0);
            continue;
        }
        
        // Parse section data
        match section {
            "coords" => {
                let parts: Vec<&str> = line.split_whitespace().collect();
                if parts.len() >= 3 {
                    let x: f64 = parts[1].parse().unwrap_or(0.0);
                    let y: f64 = parts[2].parse().unwrap_or(0.0);
                    coords.push((x, y));
                }
            }
            "demands" => {
                let parts: Vec<&str> = line.split_whitespace().collect();
                if parts.len() >= 2 {
                    let demand: i32 = parts[1].parse().unwrap_or(0);
                    demands.push(demand);
                }
            }
            "depot" => {
                if let Ok(d) = line.parse::<usize>() {
                    if d > 0 {
                        depot = d;
                    }
                }
            }
            _ => {}
        }
    }
    
    Instance {
        name,
        num_nodes,
        capacity,
        coords,
        demands,
        depot,
    }
}

fn parse_solution(data: &str) -> Solution {
    let mut routes = Vec::new();
    let mut cost = None;
    
    let route_re = Regex::new(r"Route\s*#\d+\s*:\s*(.+)").unwrap();
    let cost_re = Regex::new(r"Cost\s+(\d+)").unwrap();
    
    for line in data.lines() {
        let line = line.trim();
        
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        
        // Parse route
        if let Some(cap) = route_re.captures(line) {
            let route_str = cap.get(1).unwrap().as_str();
            let route: Vec<usize> = route_str
                .split_whitespace()
                .filter_map(|s| s.parse().ok())
                .collect();
            routes.push(route);
        }
        
        // Parse cost
        if let Some(cap) = cost_re.captures(line) {
            cost = cap.get(1).unwrap().as_str().parse().ok();
        }
    }
    
    Solution { routes, cost }
}

fn euclidean_distance(p1: (f64, f64), p2: (f64, f64)) -> f64 {
    let dx = p1.0 - p2.0;
    let dy = p1.1 - p2.1;
    (dx * dx + dy * dy).sqrt()
}

fn verify_solution(instance: &Instance, solution: &Solution) -> (bool, i32) {
    let mut valid = true;
    let mut total_cost = 0;
    let depot_idx = instance.depot - 1;
    let num_customers = instance.num_nodes - 1; // Exclude depot
    
    println!("Instance: {}", instance.name);
    println!("Number of customers: {} (plus depot)", num_customers);
    println!("Vehicle capacity: {}", instance.capacity);
    println!("Number of routes: {}", solution.routes.len());
    println!();
    
    // Track which customers are visited (indexed by customer number 1..n, not node ID)
    let mut visited = vec![false; num_customers + 1]; // Index 0 unused, 1..n for customers
    
    for (route_num, route) in solution.routes.iter().enumerate() {
        let route_num_display = route_num + 1;
        print!("Route #{}: ", route_num_display);
        
        if route.is_empty() {
            println!("EMPTY - skipping");
            continue;
        }
        
        // Calculate route load and cost
        let mut route_load = 0;
        let mut route_cost: i32 = 0;
        
        // Start from depot
        let mut prev_node = depot_idx;
        
        for &customer_num in route {
            // Solution uses customer numbering 1..n (not node IDs)
            // Customer k corresponds to node k+1 (since node 1 is depot)
            if customer_num < 1 || customer_num > num_customers {
                println!("INVALID - customer {} out of range (1..{})", customer_num, num_customers);
                valid = false;
                break;
            }
            
            // Check if customer was already visited
            if visited[customer_num] {
                println!("INVALID - customer {} visited multiple times", customer_num);
                valid = false;
                break;
            }
            
            visited[customer_num] = true;
            
            // Convert customer number to node index
            let node_idx = customer_num; // customer k -> node k+1 -> index k
            route_load += instance.demands[node_idx];
            
            // Add distance from previous node to current customer
            let dist: i32 = euclidean_distance(
                instance.coords[prev_node],
                instance.coords[node_idx]
            ).round() as i32;

            route_cost += dist;
            prev_node = node_idx;
        }
        
        // Return to depot
        let dist: i32 = euclidean_distance(
            instance.coords[prev_node],
            instance.coords[depot_idx]
        ).round() as i32;

        route_cost += dist;
        
        // Add to total cost
        total_cost += route_cost;
        
        // Check capacity constraint
        if route_load > instance.capacity {
            println!("INVALID - load {} exceeds capacity {} (cost: {})", 
                     route_load, instance.capacity, route_cost);
            valid = false;
        } else {
            println!("OK - load {} / {} (cost: {})", 
                     route_load, instance.capacity, route_cost);
        }
    }
    
    println!();
    
    // Check if all customers are visited
    for customer_num in 1..=num_customers {
        if !visited[customer_num] {
            println!("INVALID - customer {} not visited", customer_num);
            valid = false;
        }
    }
    
    println!("Total cost: {}", total_cost);
    
    if let Some(claimed_cost) = solution.cost {
        if claimed_cost != total_cost {
            println!("WARNING: Claimed cost {} does not match calculated cost {}", 
                     claimed_cost, total_cost);
            // Note: We still consider the solution valid if routes are feasible
            // even if the cost doesn't match
        }
    }
    
    (valid, total_cost)
}

fn main() {
    println!("QOBLIB CVRP Solution Checker Version {}", VERSION);
    println!();
    
    let args: Vec<String> = env::args().collect();
    
    if args.len() < 3 {
        eprintln!("Usage: {} <instance-file> <solution-file>", args[0]);
        std::process::exit(2);
    }
    
    let instance_data = fs::read_to_string(&args[1])
        .unwrap_or_else(|err| {
            eprintln!("ERROR: Reading instance file {} failed: {}", args[1], err);
            std::process::exit(2);
        });
    
    let solution_data = fs::read_to_string(&args[2])
        .unwrap_or_else(|err| {
            eprintln!("ERROR: Reading solution file {} failed: {}", args[2], err);
            std::process::exit(2);
        });
    
    let instance = parse_instance(&instance_data);
    let solution = parse_solution(&solution_data);
    
    let (valid, _cost) = verify_solution(&instance, &solution);
    
    println!();
    if valid {
        println!("VALID: Solution successfully verified");
        std::process::exit(0);
    } else {
        println!("INVALID: Solution failed verification");
        std::process::exit(1);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_parse_instance() {
        let data = r#"
NAME : TEST-n5-k2
DIMENSION : 6
CAPACITY : 100
NODE_COORD_SECTION
1    0   0
2    10  10
3    20  20
4    30  30
5    40  40
6    50  50
DEMAND_SECTION
1    0
2    30
3    30
4    20
5    20
6    40
DEPOT_SECTION
1
-1
EOF
"#;
        
        let instance = parse_instance(data);
        assert_eq!(instance.name, "TEST-n5-k2");
        assert_eq!(instance.num_nodes, 6);
        assert_eq!(instance.capacity, 100);
        assert_eq!(instance.coords.len(), 6);
        assert_eq!(instance.demands.len(), 6);
        assert_eq!(instance.depot, 1);
    }
    
    #[test]
    fn test_parse_solution() {
        let data = r#"
Route #1: 2 3 5
Route #2: 4 6
Cost 150
"#;
        
        let solution = parse_solution(data);
        assert_eq!(solution.routes.len(), 2);
        assert_eq!(solution.routes[0], vec![2, 3, 5]);
        assert_eq!(solution.routes[1], vec![4, 6]);
        assert_eq!(solution.cost, Some(150));
    }
    
    #[test]
    fn test_euclidean_distance() {
        let p1 = (0.0, 0.0);
        let p2 = (3.0, 4.0);
        let dist = euclidean_distance(p1, p2);
        assert!((dist - 5.0).abs() < 0.001);
    }
}
