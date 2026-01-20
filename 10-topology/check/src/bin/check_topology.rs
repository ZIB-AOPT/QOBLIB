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
QBench Order-Degree Problem Solution Checker
29Dec2024
Copyright (C) 2025 by Thorsten Koch

This program reads a solution graph for a order-degree problem and checks whether it is a feasible solution and computes the diameter.
*/
const VERSION: &str = "1.0";

use flate2::read::GzDecoder;
use rayon::prelude::*;
use std::collections::VecDeque;
use std::env;
use std::fmt;
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
        debug_assert_eq!(edge_count % 2, 0);
        edge_count / 2
    }

    /// Return the maximum node degree in the graph
    pub fn max_degree(&self) -> usize {
        self.nodes
            .iter()
            .map(|v| v.neighbors.len())
            .max()
            .unwrap_or(0)
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

    /// Compute diameter in parallel
    pub fn diameter(&self) -> usize {
        (0..self.node_count())
            .into_par_iter()
            .map(|n| self.bfs_depth(n as NodeNo))
            .max()
            .unwrap_or(0)
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

fn verify_solution(node_count: usize, max_degree: usize, diameter: usize, g: &Graph) -> bool {
    let mut verified = true;

    print!("Graph {} has {} nodes, ", g.name(), g.node_count());
    if node_count != g.node_count() {
        print!("expected {node_count}, ");
        verified = false;
    }
    print!("{} edges, ", g.edge_count());
    print!("max degree {}, ", g.max_degree());
    if max_degree < g.max_degree() {
        print!("expected {max_degree}, ");
        verified = false;
    }
    let components = g.connected_components();
    if components > 1 {
        print!("{components} components, ");
        verified = false;
    }
    let d = g.diameter();

    print!("diameter {d}, ");
    if diameter < d {
        print!("expected {diameter}, ");
        verified = false;
    } else if diameter > d {
        print!("required was {diameter}, ")
    }
    if verified {
        println!("ok");
    } else {
        println!("failed");
    }
    verified
}

fn main() {
    println!("Qbench Order-Degree Solution Checker Version {VERSION}");

    let args: Vec<String> = env::args().collect();

    if args.len() < 4 {
        eprintln!(
            "ERROR: usage: {} node-count max-degree diameter solution-graph-file",
            &args[0]
        );
        std::process::exit(2);
    }
    let node_count = args[1]
        .parse()
        .unwrap_or_else(|err| panic!("Expected node count: {err}"));
    let max_degree = args[2]
        .parse()
        .unwrap_or_else(|err| panic!("Expected max degree: {err}"));
    let diameter = args[3]
        .parse()
        .unwrap_or_else(|err| panic!("Expected max degree: {err}"));
    let basename = Path::new(&args[4])
        .file_stem()
        .and_then(|name| name.to_str())
        .unwrap_or("Order-Degree");
    let g = Graph::read_from_file(basename, &args[4]);

    let verified = verify_solution(node_count, max_degree, diameter, &g);

    if verified {
        println!("VALID: Solution successfully verified");
        std::process::exit(0);
    } else {
        println!("INVALID: Solution verification failed");
        std::process::exit(1);
    }
}

#[test]
fn verify_15_3_solution() {
    use std::io::Cursor;
    use std::io::Read;

    let instance = "c Undirected Graph with Diameter 3\n\
    p edge 15 22\n\
    e 1 9\n\
    e 1 11\n\
    e 1 12\n\
    e 2 7\n\
    e 2 10\n\
    e 2 11\n\
    e 3 5\n\
    e 3 10\n\
    e 3 13\n\
    e 4 8\n\
    e 4 13\n\
    e 4 14\n\
    e 5 6\n\
    e 5 14\n\
    e 6 10\n\
    e 6 12\n\
    e 7 8\n\
    e 7 12\n\
    e 8 9\n\
    e 9 13\n\
    e 11 15\n\
    e 14 15";

    // it is possible to read a graph from a string using Cursor
    let mut input: Box<dyn Read> = Box::new(Cursor::new(instance));
    let g = Graph::read_from_stream("test", &mut input);
    assert_eq!(verify_solution(15, 3, 3, &g), true);
}

#[test]
fn diameter_fail() {
    use std::io::Cursor;
    use std::io::Read;

    let instance = "c Undirected Graph with Diameter 3\n\
    p edge 15 22\n\
    e 1 9\ne 1 11\ne 1 12\ne 2 7\ne 2 10\ne 2 11\ne 3 5\ne 3 10\n\
    e 3 13\ne 4 8\ne 4 13\ne 4 14\ne 5 6\ne 5 14\ne 6 10\ne 6 12\n\
    e 7 8\ne 7 12\ne 8 9\ne 9 13\ne 11 15\ne 14 15\n";

    // it is possible to read a graph from a string using Cursor
    let mut input: Box<dyn Read> = Box::new(Cursor::new(instance));
    let g = Graph::read_from_stream("test", &mut input);
    assert_eq!(verify_solution(15, 3, 2, &g), false);
}
