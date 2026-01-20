# This file is part of QOBLIB - Quantum Optimization Benchmarking Library
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np
import numpy.random as random
import sys
import os
import subprocess
import xml.etree.ElementTree as ET
import argparse

# Example of grid for ease of reference:

# 1 2 3 4
# 5 6 7 8
# 9 10 11 12
# 13 14 15 16

# 17 18 19 20
# 21 22 23 24
# 25 26 27 28
# 29 30 31 32


def parse_args():
    parser = argparse.ArgumentParser(description="Generate feasible instances for Steiner tree problem.")
    parser.add_argument("size", type=int, help="For size=n, the final grid will be of size n*n")
    parser.add_argument("num_layers", type=int, help="Number of stacked grid layers")
    parser.add_argument("max_terminals", type=int, help="Maximum number of terminals per net, iteratively reduced until feasible net found")
    parser.add_argument("--num_holes", type=int, default=0, help="Number of random holes to generate")
    parser.add_argument("--randseed", type=int, default=12345, help="Random seed")
    parser.add_argument("--zimpl_path", type=str, default='zimpl', help="Path to ZIMPL executable")
    parser.add_argument("--cplex_path", type=str, default='cplex', help="Path to CPLEX executable")
    parser.add_argument("--force_diff_side", type=bool, default=False, help="Must the second terminal in each net be on a different side than the first one?")
    return parser.parse_args()


def node_from_coord(x, y, z, size, num_layers):
    """ return node id from its coordinates """
    assert(x <= size)
    assert(y <= size)
    assert(z <= num_layers)
    return x + (y-1)*size + (z-1)*size*size

def coord_from_node(node_id, size, num_layers):
    """ return coordinates from node id"""
    assert(node_id <= size + (size-1)*size + (num_layers-1)*size*size)
    if (node_id % (size*size) == 0):
        z = node_id // (size*size)
    else:
        z = node_id // (size*size) + 1
    if ((node_id - size*size*(z-1)) % size == 0):
        y = (node_id - size*size*(z-1)) // size
    else:
        y = (node_id - size*size*(z-1)) // size + 1
    x = node_id - size*size*(z-1) - size*(y-1)
    return x, y, z

def node_neighbors(node_id, size, num_layers):
    """ return list of all neighbors of a given node """
    x, y, z = coord_from_node(node_id, size, num_layers)
    neighbor = []
    if x > 1:
        neighbor.append((x-1, y, z))
    if x < size:
        neighbor.append((x+1, y, z))
    if y > 1:
        neighbor.append((x, y-1, z))
    if y < size:
        neighbor.append((x, y+1, z))
    if z > 1:
        neighbor.append((x, y, z-1))
    if z < num_layers:
        neighbor.append((x, y, z+1))
    return [node_from_coord(x, y, z, size, num_layers) for x, y, z in neighbor]

def generate_holes(size, num_layers, num_holes):
    """ generate a given number of holes """
    holes = set()
    for j in range(num_holes):
        # size of the hole along x, y, z axis
        hole_size_x = random.randint(max(size//10, 1), max(size//4, 2) + 1)
        hole_size_y = random.randint(max(size//10, 1), max(size//4, 2) + 1)
        hole_size_z = random.randint(0, num_layers//2 + 1)
        # coordinate
        hole_start_x = random.randint(1, size + 1 - hole_size_x)
        hole_start_y = random.randint(1, size + 1 - hole_size_y)
        hole_start_z = random.randint(1, num_layers + 1 - hole_size_z)
        for i in range(hole_size_x):
            for j in range(hole_size_y):
                # For the z axis, we allow holes of size 0, but we
                # still want to do at least one iteration of the for
                # loop.
                for k in range(max(hole_size_z, 1)):
                    center = node_from_coord(
                        hole_start_x + i, hole_start_y + j,
                        hole_start_z + k, size, num_layers)
                    right = node_from_coord(
                        hole_start_x + i + 1, hole_start_y + j,
                        hole_start_z + k, size, num_layers)
                    if ((center, right)) not in holes:
                        holes.add((center, right))
                        holes.add((right, center))
                    down = node_from_coord(
                        hole_start_x + i, hole_start_y + j + 1,
                        hole_start_z + k, size, num_layers)
                    if ((center, down)) not in holes:
                        holes.add((center, down))
                        holes.add((down, center))
                    if (hole_size_z > 0):
                        # If hole_size_z = 0, the hole is "flat" on a
                        # single layer, so nothing to do. If
                        # hole_size_z > 0, we remove vertical edges.
                        below = node_from_coord(
                            hole_start_x + i, hole_start_y + j,
                            hole_start_z + k + 1, size, num_layers)
                        if ((center, below)) not in holes:
                            holes.add((center, below))
                            holes.add((below, center))
        print('Hole from {:d} {:d} {:d} size {:d} {:d} {:d}'.format(
            hole_start_x, hole_start_y, hole_start_z,
            hole_size_x, hole_size_y, hole_size_z))
    return holes


def random_node_on_edge(size, num_layers):
    """ generate a random node on the edges (border) of the first layer. """
    # There are 4*(size-1) nodes on the edge. Randomly pick one
    # of them. Recall that randint excludes the upper limit.
    node_on_edge = random.randint(1, 4*(size-1) + 1)
    if (node_on_edge <= size-1):
        # Top edge
        term = node_from_coord(node_on_edge, 1, 1,
                               size, num_layers)
    elif (node_on_edge <= 2*(size-1)):
        # Right edge
        term = node_from_coord(size, node_on_edge-(size-1),
                               1, size, num_layers)
    elif (node_on_edge <= 3*(size-1)):
        # Bottom edge
        term = node_from_coord(node_on_edge - 2*(size-1) +1,
                               size, 1, size, num_layers)
    else:
        # Left edge
        term = node_from_coord(1, node_on_edge-3*(size-1)+1,
                               1, size, num_layers)
    return term

def write_arcs_file(filename, size, num_layers, holes):
    """ generate arcs of the graph and write in a file. """
    arc_f = open(filename, "w")
    arc_f.write("# Tail Head Cost\n")
    # If we have holes we skip the corresponding arcs.
    for k in range(1, num_layers+1):
        for j in range(1, size+1):
            for i in range(1, size+1):
                if (i < size and
                    (node_from_coord(i, j, k, size, num_layers),
                     node_from_coord(i+1, j, k, size, num_layers))
                    not in holes):
                    arc_f.write("{:>3d} {:>3d} 1\n".format(
                        node_from_coord(i, j, k, size, num_layers),
                        node_from_coord(i+1, j, k, size, num_layers)
                    ))
                    arc_f.write("{:>3d} {:>3d} 1\n".format(
                        node_from_coord(i+1, j, k, size, num_layers),
                        node_from_coord(i, j, k, size, num_layers)
                    ))
                if (j < size and
                    (node_from_coord(i, j, k, size, num_layers),
                     node_from_coord(i, j+1, k, size, num_layers))
                    not in holes):
                    arc_f.write("{:>3d} {:>3d} 1\n".format(
                        node_from_coord(i, j, k, size, num_layers),
                        node_from_coord(i, j+1, k, size, num_layers)
                    ))
                    arc_f.write("{:>3d} {:>3d} 1\n".format(
                        node_from_coord(i, j+1, k, size, num_layers),
                        node_from_coord(i, j, k, size, num_layers)
                    ))
                if (k < num_layers and
                    (node_from_coord(i, j, k, size, num_layers),
                     node_from_coord(i, j, k+1, size, num_layers))
                    not in holes):
                    arc_f.write("{:>3d} {:>3d} 1\n".format(
                        node_from_coord(i, j, k, size, num_layers),
                        node_from_coord(i, j, k+1, size, num_layers)
                    ))
                    arc_f.write("{:>3d} {:>3d} 1\n".format(
                        node_from_coord(i, j, k+1, size, num_layers),
                        node_from_coord(i, j, k, size, num_layers)
                    ))
    arc_f.close()

def write_terminals_file(filename, nets):
    terms_f = open(filename, "w")
    terms_f.write("# Node Net\n")
    for (j, terminal_id) in enumerate(nets):
        for term in terminal_id:
            terms_f.write("{:>3d} {:>3d}\n".format(term, j+1))
    terms_f.close()

def write_roots_file(filename, roots):
    roots_f = open(filename, "w")
    roots_f.write("# Node Net\n")
    for (j, root_id) in enumerate(roots):
        roots_f.write("{:>3d} {:>3d}\n".format(root_id, j+1))
    roots_f.close()

def write_blocked_arcs_file(filename, blocked_arcs):
    blocked_f = open(filename, "w")
    blocked_f.write("# Tail Head\n")
    for arc in blocked_arcs:
        blocked_f.write("{:>3d} {:>3d}\n".format(arc[0], arc[1]))
    blocked_f.close()

def write_param_file(filename, num_nodes, num_nets):
    param_f = open(filename, "w")
    param_f.write("nodes {:d}\n".format(num_nodes))
    param_f.write("nets {:d}\n".format(num_nets))
    param_f.close()

def write_partial_solution_file(filename, partial_solution):
    """ filename: file to write
        partial_solution: list of triples [head, tail, net_id]
    """
    partial_sol_f = open(filename, "w")
    partial_sol_f.write("# Cost: {:d}\n\n".format(len(partial_solution)))
    partial_sol_f.write("# Tail Head Net\n")
    for partial in partial_solution:
        partial_sol_f.write("{:d} {:d} {:d}\n".format(*partial))
    partial_sol_f.close()

def generate_feasible_instance(size, num_layers, max_terminals,
                               num_holes = 0, max_attempt = 5,
                               max_generated_nets = float('inf'),
                               zimpl_path='zimpl',
                               cplex_path='cplex',
                               force_diff_side=False):
    """ size: number of nodes on one edge of the square grid
        num_layers: how many square grids stacked
        max_terminals: how many terminals in the initial net
        num_holes: how many holes
        max_attempt: how many times we try to generate a steiner tree before we decide that we failed
        max_generated_nets: how many nets at most
        force_diff_side: if True, the second terminal in each net will be on a different side of the square
    """
    # Generate holes, if any
    holes = generate_holes(size, num_layers, num_holes)
                    
    # Write arc file. This is the same for each net.
    write_arcs_file("arcs.dat", size, num_layers, holes)

    current_terminals = max_terminals
    # Keep track of all generated nets and roots
    nets = []
    roots = []
    # Arcs to be blocked out so far
    blocked_arcs = set()
    # Partial y solution for feasibility
    partial_solution = []
    print('*** INITIAL NUMBER OF TERMINALS {:d}***'.format(current_terminals))
    # Stop if we are generating nets with too few terminls    
    while (current_terminals >= max_terminals//2 and current_terminals >= 2
           and len(nets) <= max_generated_nets):
        # Consecutive number of failed attempts
        attempt = 0
        while (attempt < max_attempt):
            print('Attempt:', attempt)
            terminal_id = []
            # Keep generating at random until we have desired
            # number. Make sure we do not run for ever.
            while_iter = 0
            while (len(terminal_id) < current_terminals and while_iter < 10000):
                # Generate terminals on the edges (border) of the
                # grid. All terminals are on the first (top) layer.
                duplicate = True
                count_duplicate = 0
                while (duplicate and count_duplicate < max_attempt):
                    term = random_node_on_edge(size, num_layers)
                    # Check for duplicates among terminals in this
                    # net, or previously generated nets
                    duplicate = False
                    if (term in terminal_id or
                        any(term in net for net in nets)):
                        duplicate = True
                    # If this is the second terminal, make sure it is
                    # not on the same edge as the first one; this
                    # ensures not all terminals in the net are on the
                    # same edge.
                    if (force_diff_side and len(terminal_id) == 1):
                        x1, y1, z1 = coord_from_node(terminal_id[0], size, num_layers)
                        x2, y2, z2 = coord_from_node(term, size, num_layers)
                        if ((x1 == 1 and x2 == 1) or
                            (x1 == size and x2 == size) or
                            (y1 == 1 and y2 == 1) or
                            (y1 == size and y2 == size)):
                            duplicate = True
                    count_duplicate += int(duplicate)
                if (count_duplicate < max_attempt):
                    terminal_id.append(term)
                while_iter += 1
            root_id = terminal_id[random.randint(0, len(terminal_id))]
            # Write terminals file and roots file.
            write_terminals_file("terms.dat", [terminal_id])
            write_roots_file("roots.dat", [root_id])
            # Write file of blocked edges
            write_blocked_arcs_file("blocked.dat", blocked_arcs)
            # Write params file
            write_param_file(
                "param.dat",
                node_from_coord(size, size, num_layers, size, num_layers),
                1)

            # Solve instance to get Steiner tree, if it exists.
            current_dir = os.getcwd()
            subprocess.call(['rm', '-f', 'stp.sol', 'stp.lp'], cwd=current_dir)
            subprocess.run([zimpl_path, '-t', 'lp', '-o', 'stp', 'stp3d6_blocked.zpl'], cwd=current_dir, capture_output=True)
            subprocess.run([cplex_path, '-c', 'set timelimit 600', 'read stp.lp', 'mipopt', 'write stp.sol'], cwd=current_dir, capture_output=True)

            solution_found = True
            # In Cplex, the solution file is an .xml. It is not
            # created if there is no solution.
            try:
                tree = ET.parse('stp.sol')
                root = tree.getroot()
            except FileNotFoundError:
                solution_found = False

            if (not solution_found):
                attempt += 1
                continue
                
            if (root[0].tag != 'header'):
                print('Error reading solution xml')
                exit()
            if (root[0].attrib['solutionStatusValue'] != '101'):
                # Solution is not optimal
                print('*** Steiner tree not optimal, we can still continue')

            # Reset consecutive number of failed attempts
            attempt = 0
            # We have a new net, store it
            nets.append(terminal_id)
            roots.append(root_id)
            print('Generated', len(nets), 'nets')

            # Get arcs in the solution and block them out
            if (root[3].tag != 'variables'):
                print('Error reading solution xml')
                exit()
            for var in root[3]:                
                if (round(float(var.attrib['value'])) == 1 and
                    var.attrib['name'][0] == 'y'):
                    # This is one of the arcs that we should
                    # block. Identify the endpoints of the arc. The
                    # variable names are of the form y#i#j#k where i,j
                    # are node ids, and k is the net.
                    fields = var.attrib['name'].split('#')
                    tail = int(fields[1])
                    head = int(fields[2])
                    if ((tail, head) not in blocked_arcs):
                        blocked_arcs.add((tail, head))
                        blocked_arcs.add((head, tail))
                    # Also block adjacent arcs since we use a
                    # node-disjoint model
                    tail_neighbors = node_neighbors(tail, size, num_layers)
                    for j in tail_neighbors:
                        if ((tail, j) not in blocked_arcs and
                            (tail, j) not in holes):
                            blocked_arcs.add((tail, j))
                            blocked_arcs.add((j, tail))
                    head_neighbors = node_neighbors(head, size, num_layers)
                    for j in head_neighbors:
                        if ((head, j) not in blocked_arcs and
                            (head, j) not in holes):
                            blocked_arcs.add((head, j))
                            blocked_arcs.add((j, head))
                    # Add to partial solution
                    partial_solution.append([tail, head, len(nets)])
        # Closes 'while (attempt < max_attempt)'
        current_terminals -= 1
        print('*** DECREASING NUMBER OF TERMINALS TO {:d}***'.format(current_terminals))

    # Write final .dat files with all the nets found
    if (len(nets) > 0):
        write_param_file(
            "param.dat",
            node_from_coord(size, size, num_layers, size, num_layers),
            len(nets))
        write_terminals_file("terms.dat", nets)
        write_roots_file("roots.dat", roots)
        write_partial_solution_file("partial_sol.txt", partial_solution)
    else:
        print('The script could not successfully generate a random instance.')
        print('Try increasing the timeouts, allowing for more retries, or changing the random seed.')



def main():
    args = parse_args()

    # Set the random seed
    random.seed(args.randseed)

    # Call the instance generator function
    generate_feasible_instance(
        size=args.size,
        num_layers=args.num_layers,
        max_terminals=args.max_terminals,
        num_holes=args.num_holes, 
        zimpl_path=args.zimpl_path,
        cplex_path=args.cplex_path,
        force_diff_side=args.force_diff_side
    )


if __name__ == "__main__":
    main()
