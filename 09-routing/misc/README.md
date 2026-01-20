# Miscellaneous

This directory contains utility scripts for visualizing routing problem instances and solutions.

## Scripts

### plot_instance.py

Creates a visual PDF plot of a routing instance, optionally including the solution path.

**Usage:**
```bash
python plot_instance.py <instance_file> [solution_file]
```

**Arguments:**
- `instance_file`: Path to the routing instance file (required)
- `solution_file`: Path to the solution file (optional)

**Output:** Generates a `.pdf` file with a visualization of the instance and solution.

**Examples:**
```bash
# Plot instance only
python plot_instance.py ../instances/route_10_5.dat

# Plot instance with solution
python plot_instance.py ../instances/route_10_5.dat ../solutions/route_10_5.sol
```

**Use cases:**
- Visual verification of instance structure
- Checking solution validity and quality
- Creating figures for presentations or papers
- Debugging instance generation or solution algorithms