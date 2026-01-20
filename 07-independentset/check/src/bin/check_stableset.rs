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
QBench Stable Set Problem Solution Checker
13Nov2023-26Dec2024
Copyright (C) 2025 by Thorsten Koch

This program reads a stable set problem from qbench and a solutions and checks whether it is a feasible solution.
*/
const VERSION: &str = "1.0";

use flate2::read::GzDecoder;
use std::collections::VecDeque;
use std::env;
use std::fmt;
use std::fs;
use std::fs::File;
use std::io::{stdin, BufRead, BufReader, Read};
use std::path::Path;

/// Can be easily changed to u64 and u32.
pub type NodeNo = u32;

/// A node consists of its neighbors.
#[derive(Debug)]
struct Node {
    neighbors: Vec<NodeNo>,
}

impl Node {
    /// Create a new node.
    fn new() -> Self {
        Node {
            neighbors: Vec::new(),
        }
    }
    /// Add a new neighbour to a node.
    fn add_neighbor(&mut self, head: NodeNo) {
        self.neighbors.push(head)
    }
}

/// A graph consists of nodes, which possibly have edges.
/// Nodes are numbered 0 .. node_count.
#[derive(Debug)]
pub struct Graph {
    name: String,
    nodes: Vec<Node>,
}

impl Graph {
    pub const INVALID_NODE: NodeNo = NodeNo::MAX;

    /// Create a new empty graph.
    pub fn new(name: &str) -> Self {
        Graph {
            name: name.to_string(),
            nodes: Vec::new(),
        }
    }

    /// Add a node to a graph.
    pub fn add_node(&mut self) -> NodeNo {
        self.nodes.push(Node::new());
        (self.nodes.len() - 1) as NodeNo
    }

    /// Add an edge to a graph.
    /// We are an undirected graph, so we add every edge in both directions.
    pub fn add_edge(&mut self, tail: NodeNo, head: NodeNo) {
        debug_assert!((tail as usize) < self.nodes.len());
        debug_assert!((head as usize) < self.nodes.len());
        self.nodes[tail as usize].add_neighbor(head);
        self.nodes[head as usize].add_neighbor(tail);
    }

    /// Return the number of nodes in the graph.
    pub fn node_count(&self) -> usize {
        self.nodes.len()
    }

    /// Return the name of the graph
    pub fn name(&self) -> &str {
        &self.name
    }

    /// Return the number of edges in the graph.
    pub fn edge_count(&self) -> usize {
        let edge_count: usize = self.nodes.iter().map(|v| v.neighbors.len()).sum();
        /* same as:
            let mut edge_count = 0;
            for node in &self.nodes {
                edge_count += node.neighbors.len();
            }
        */
        debug_assert_eq!(edge_count % 2, 0);
        edge_count / 2
    }

    /// Create a new graph from the data in a file.
    /// If the filename is just "-" we read from the standard input.
    /// Otherwise from a normal text file, or a gzip compressed file.
    pub fn read_from_file(name: &str, filepath: &str) -> Self {
        let mut input: Box<dyn Read> = if filepath == "-" {
            Box::new(stdin())
        } else {
            let path = Path::new(filepath);
            let file =
                File::open(path).unwrap_or_else(|err| panic!("Can't open {filepath}: {err}"));

            if path.extension() == Some(std::ffi::OsStr::new("gz")) {
                Box::new(GzDecoder::new(file))
            } else {
                Box::new(file)
            }
        };
        Self::read_from_stream(name, &mut input)
    }

    /// Create a new graph from the data in a stream.
    pub fn read_from_stream(name: &str, stream: &mut Box<dyn Read>) -> Self {
        let input = BufReader::new(stream);
        let mut g = Graph::new(name);
        let mut node_count = 0;
        let mut edge_count = 0;

        for (lineno, line) in input.lines().enumerate() {
            let data = line.unwrap_or_else(|err| panic!("Line {} {err}", lineno + 1));
            let fields: Vec<&str> = data.split_whitespace().collect();

            // Ignore empty lines or line starting with "c"
            if fields.is_empty() || fields[0].starts_with("c") {
                continue;
            }
            // The "p" line has the number of nodes and edges
            if fields[0].starts_with("p") {
                if fields.len() < 4 || node_count != 0 || edge_count != 0 {
                    panic!("Line {} syntax error", lineno + 1);
                }
                node_count = fields[2].parse::<usize>().unwrap_or_else(|err| {
                    panic!("Line {} expected number of nodes: {err}", lineno + 1)
                });
                edge_count = fields[3].parse::<usize>().unwrap_or_else(|err| {
                    panic!("Line {} expected number of edges: {err}", lineno + 1)
                });

                g.nodes.resize_with(node_count, || Node::new());
                continue;
            }
            // The "e" lines list the edges: e Tail-Node-No Head-Node-No
            if fields[0].starts_with("e") {
                if fields.len() < 3 || node_count == 0 || edge_count == 0 {
                    panic!("Line {} syntax error", lineno + 1);
                }
                let tail: NodeNo = fields[1]
                    .parse()
                    .unwrap_or_else(|err| panic!("Line {} expected node no: {err}", lineno + 1));
                let head: NodeNo = fields[2]
                    .parse()
                    .unwrap_or_else(|err| panic!("Line {} expected node no: {err}", lineno + 1));

                if tail < 1
                    || tail as usize > node_count
                    || head < 1
                    || head as usize > node_count
                    || tail == head
                {
                    panic!(
                        "Line {} edge {}-{} outside range [1..{}]",
                        lineno + 1,
                        tail,
                        head,
                        node_count
                    );
                }
                g.add_edge(head - 1, tail - 1);
                edge_count -= 1;
                continue;
            }
            panic!("Line {} syntax error", lineno + 1);
        }
        if edge_count != 0 {
            panic!("End of file: {} edges missing", edge_count);
        }
        g
    }

    /// Runs a breadth first search (BFS) starting from node start
    /// and computes the depth of the resulting of tree.
    pub fn bfs_depth(&self, start: NodeNo) -> usize {
        assert!(
            (start as usize) < self.node_count(),
            "start node >= node count"
        );

        let mut depth = vec![0; self.node_count()];

        self.bfs(start, &mut depth)
    }

    /// Runs a breadth first search (BFS) starting from node start
    /// and stores the depth of the nodes.
    fn bfs(&self, start: NodeNo, depth: &mut [usize]) -> usize {
        debug_assert!(
            (start as usize) < self.node_count(),
            "start node >= node count"
        );

        let mut queue = VecDeque::new();
        let mut dmax = 1;

        depth[start as usize] = dmax;
        queue.push_back(start);

        while !queue.is_empty() {
            let tail = queue.pop_front().unwrap();
            let d = depth[tail as usize];

            for n in &self.nodes[tail as usize].neighbors {
                debug_assert!(depth[*n as usize] <= depth[tail as usize] + 1);
                if depth[*n as usize] == 0 {
                    queue.push_back(*n);
                    debug_assert!(d == dmax || d == dmax - 1);
                    dmax = d + 1;
                    depth[*n as usize] = dmax;
                }
            }
        }
        dmax - 1
    }

    /// Find the number of connected components.
    /// To do so, we run a BFS from every not visited node.
    pub fn connected_components(&self) -> usize {
        let mut depth = vec![0; self.node_count()];
        let mut components = 0;

        for n in 0..self.node_count() {
            if depth[n] == 0 {
                components += 1;
                self.bfs(n as NodeNo, &mut depth);
            }
        }
        components
    }

    /// Check if set is stable
    pub fn is_set_stable(&self, set: &[bool]) -> bool {
        for i in 0..self.node_count() {
            if set[i] {
                for n in &self.nodes[i].neighbors {
                    if set[*n as usize] {
                        return false;
                    }
                }
            }
        }
        true
    }
}

/// Implement `Display` for `Graph`
impl fmt::Display for Graph {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        writeln!(f, "Graph: nodes={}", self.nodes.len())?;
        for (i, node) in self.nodes.iter().enumerate() {
            for n in &node.neighbors {
                writeln!(f, "   e {:3} {:3}", i, *n)?;
            }
        }
        Ok(())
    }
}

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
fn extract_solution_01(data: &[u8], dim: usize) -> Vec<bool> {
    let mut solution = Vec::<bool>::new();
    let mut i = 0;
    while i < data.len() {
        let c = data[i] as char;
        if c == '0' || c == '1' {
            solution.push(data[i] == b'1');
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

fn extract_solution_numb(data: &[u8], dim: usize) -> Vec<bool> {
    let mut solution = vec![false; dim];
    let mut lineno = 1;
    let mut index = 0;
    let mut i = 0;

    while i < data.len() {
        let c = data[i] as char;

        if c.is_ascii_whitespace() || c.is_ascii_punctuation() {
            if index > 0 {
                solution[index - 1] = true;
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

fn extract_solution_text(data: &[u8], dim: usize) -> Vec<bool> {
    let mut solution = vec![false; dim];
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
                if c.is_ascii_whitespace() {
                    // ignore
                } else if c == '0' || c == '1' {
                    solution[index] = data[i] == b'1';
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

fn extract_solution(data: &[u8], dim: usize) -> Vec<bool> {
    match detect_solution_format(data) {
        SolutionFormat::OnlySpace => panic!("Parsing solution: found empty file"),
        SolutionFormat::ZeroOneVec => extract_solution_01(data, dim),
        SolutionFormat::IndexList => extract_solution_numb(data, dim),
        SolutionFormat::XVarList => extract_solution_text(data, dim),
    }
}

fn verify_solution(g: &Graph, solution_data: &[u8]) -> bool {
    let solution = extract_solution(solution_data, g.node_count());

    //let set_size = &solution.into_iter().filter(|b| *b).count();
    let mut set_size = 0; //solution.into_iter().filter(|b| *b).count();
    for b in &solution {
        if *b {
            set_size += 1;
        }
    }
    print!(
        "Graph has {} nodes, {} edges, {} components, stable set size = {set_size} is ",
        g.node_count(),
        g.edge_count(),
        g.connected_components()
    );

    let verified = g.is_set_stable(&solution);

    if verified {
        println!("ok");
    } else {
        println!("wrong!");
    }
    verified
}

fn main() {
    println!("Qbench Stable Set Solution Checker Version {VERSION}");

    let args: Vec<String> = env::args().collect();

    if args.len() < 3 {
        eprintln!(
            "ERROR: usage: {} graph-file solution-file|01-string",
            &args[0]
        );
        std::process::exit(2);
    }
    let basename = Path::new(&args[1])
        .file_stem()
        .and_then(|name| name.to_str())
        .unwrap_or("Stable Set");
    let g = Graph::read_from_file(basename, &args[1]);
    let solution_arg = &args[2];

    // Check if a string consists only of '1's and '0's
    let is_binary = |s: &str| s.chars().all(|c| c == '0' || c == '1');

    let solution_data = if is_binary(solution_arg) {
        solution_arg.as_bytes().to_vec()
    } else {
        fs::read(solution_arg)
            .unwrap_or_else(|err| panic!("Reading {} failed: {err}", solution_arg))
    };

    let verified = verify_solution(&g, &solution_data);

    if verified {
        println!("VALID: Solution successfully verified");
        std::process::exit(0);
    } else {
        println!("INVALID: Solution verification failed");
        std::process::exit(1);
    }
}

#[test]
fn verify_numb_solution() {
    use std::io::Cursor;
    use std::io::Read;

    let instance = "c Undirected Graph\n\
    p edge 17 39\n\
    e 7 17\n\
    e 6 4\n\
    e 7 5\n\
    e 1 6\n\
    e 2 6\n\
    e 3 6\n\
    e 1 7\n\
    e 2 7\n\
    e 3 7\n\
    e 4 7\n\
    e 1 8\n\
    e 2 8\n\
    e 1 9\n\
    e 2 9\n\
    e 4 9\n\
    e 1 10\n\
    e 2 10\n\
    e 5 10\n\
    e 1 11\n\
    e 2 11\n\
    e 4 11\n\
    e 1 12\n\
    e 2 12\n\
    e 3 12\n\
    e 6 12\n\
    e 1 13\n\
    e 2 13\n\
    e 4 13\n\
    e 6 13\n\
    e 1 14\n\
    e 2 14\n\
    e 3 14\n\
    e 7 14\n\
    e 1 15\n\
    e 2 15\n\
    e 4 15\n\
    e 7 15\n\
    e 3 16\n\
    e 4 17\n";

    let solution = b"5 8 9 11 12 13 14 15 16 17";

    // it is possible to read a graph from a string using Cursor
    let mut input: Box<dyn Read> = Box::new(Cursor::new(instance));
    let g = Graph::read_from_stream("test", &mut input);
    assert_eq!(verify_solution(&g, solution), true);
}
