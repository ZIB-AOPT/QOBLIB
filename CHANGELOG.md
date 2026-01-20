# Changelog [v1.1.0]

## 1. Directory Structure

- Removed redundant README files across multiple problem directories
- Removed redundant `misc` directory from problem folders
- Cleaned up redundant permutation code from 03-birkhoff

## 2. Problems

All problems (01-10) have been updated to follow a consistent format and structure.

## 3. Instances

- Updated 03-birkhoff LP files to new format

## 4. Models

### Model Format Updates
- Updated model READMEs across all problems to follow a similar format
- Enhanced documentation consistency across all problem types

## 5. Solutions

### Solution Format Updates
- Converted 01-marketsplit solutions to better canonical format
- Converted 07-independentset solutions to canonical format
- Converted large 10-topology solutions to compressed `.xz` format for better storage efficiency
- Updated 03-birkhoff solutions to match new format

### New Solutions
- Added 03-birkhoff submission and updated solutions

## 6. Submissions

### 03-birkhoff
- Added new 03-birkhoff submissions

## 7. Checkers

### New Checkers
- Added [03-birkhoff Solution Checker](./03-birkhoff/check/)
- Added [08-network Solution Checker](./08-network/check/)
- Added [09-routing Solution Checker](./09-routing/check/)

### Checker Improvements
- Updated all solution checkers to follow standardized exit code formats:
  - Exit code 0: Solution is valid
  - Exit code 1: Solution is invalid
  - Exit code 2: Error occurred
- Updated checker READMEs for better documentation

## 8. Metadata & Documentation

### Main Documentation
- Updated main [README.md](./README.md) with improved structure and clarity
- Updated [CONTRIBUTING.md](./CONTRIBUTING.md) to follow the paper more closely
- Fixed mathematical formulas in CONTRIBUTING.md
- Corrected mathematical formulas in 03-birkhoff misc README

### Problem-Specific Documentation
- Updated README files for all problem directories (01-10) to follow consistent format
- Added figures to problem READMEs for better visualization
- Updated README widths for improved readability in problems:
  - 04-steiner
  - 07-independentset
  - 08-network
  - 09-routing

### Miscellaneous Documentation
- Updated misc READMEs across the repository

## 9. Tooling & Automation

### Updated Tools
- Updated [metrics script](./misc/get_metrics.py) for better performance
- Updated [QUBO conversion tool](./misc/convert_lp2qubo.py) for new format
- Deleted redundant metrics files

### Infrastructure Updates
- Updated ZIMPL version to 3.7.1
- Fixed [submission template](./misc/submission_template.csv)

## 10. Versioning & Compatibility

Current release is v1.1.0.

This version introduces:
- Standardized solution and model formats across all problems
- Improved documentation consistency
- Enhanced checker functionality with standardized exit codes
- Better compression for large solution files
- New checkers for additional problem types

## 11. Miscellaneous

- Various bug fixes and improvements throughout the codebase
- Improved consistency in file naming and structure
- Enhanced tooling for repository maintenance
