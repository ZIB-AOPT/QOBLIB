import sys

def validate_graph_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    problems = []
    edge_set = set()
    corrected_edges = set()
    node_set = set()
    p_line = None
    comments = []

    # Parse lines
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('c'):
            comments.append(line)
            continue
        if line.startswith('p'):
            if p_line:
                problems.append("Multiple 'p edge N M' lines found.")
            p_line = line
            continue
        if line.startswith('e'):
            parts = line.split()
            if len(parts) != 3:
                problems.append(f"Invalid edge format: '{line}'")
                continue
            try:
                a, b = int(parts[1]), int(parts[2])
            except ValueError:
                problems.append(f"Edge has invalid node indices: '{line}'")
                continue
            if a == b:
                problems.append(f"Self-loop detected: {a} -> {b}")
                continue
            u, v = sorted((a, b))
            if (u, v) in edge_set:
                problems.append(f"Duplicate edge: {u} {v}")
            else:
                edge_set.add((u, v))
                corrected_edges.add((u, v))
                node_set.update([u, v])
        else:
            problems.append(f"Unknown line format: '{line}'")

    if not p_line:
        problems.append("Missing 'p edge N M' line.")
        n = len(node_set)
        m = len(edge_set)
    else:
        try:
            _, _, n_str, m_str = p_line.split()
            n, m = int(n_str), int(m_str)
            if n != len(node_set):
                problems.append(f"Declared number of nodes {n} does not match actual {len(node_set)}")
            if m != len(edge_set):
                problems.append(f"Declared number of edges {m} does not match actual {len(edge_set)}")
        except Exception:
            problems.append(f"Invalid 'p edge' line format: '{p_line}'")
            n = len(node_set)
            m = len(edge_set)

    if problems:
        print("Problems found in the graph file:")
        for problem in problems:
            print(f" - {problem}")

        fix = input(f"Would you like to write a corrected version of the graph from '{filename}'? (y/n): ").strip().lower()
        if fix == 'y':
            out_file = input("Enter output filename: ").strip()
            with open(out_file, 'w') as f:
                f.write("c This file was auto-corrected due to format issues\n")
                for c in comments:
                    f.write(c + '\n')
                f.write(f"p edge {n} {len(corrected_edges)}\n")
                for u, v in sorted(corrected_edges):
                    f.write(f"e {u} {v}\n")
            print(f"Corrected graph written to {out_file}")
    else:
        print("Graph file is valid!")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python validate_graph.py <graphfile>")
    else:
        validate_graph_file(sys.argv[1])