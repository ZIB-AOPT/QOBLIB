# Edge-switch annealing for the order/degree problem

Submitter: Arhan Canli (Quantavane), 2026-11-02.

Three instances get a smaller diameter than the listed best-known value. Each graph has the instance's node count,
maximum degree at most d, is connected, and has the stated diameter.

| Instance | Diameter found | Previous best known | Lower bound | Status | Runs reaching it | Mean time per run |
| :------- | -------------: | ------------------: | ----------: | :----- | :--------------: | ----------------: |
| topology_30_6 | 2 | 3 | 2 | optimal | 10 / 10 | 36.99 s |
| topology_35_5 | 3 | 4 | 3 | optimal | 10 / 10 | 0.01 s |
| topology_50_4 | 4 | 5 | 3 | not proven | 10 / 10 | 0.01 s |

Lower bounds: topology_30_6 cannot have diameter 1 (that needs the complete graph, degree 29). For topology_35_5
and topology_50_4 the Moore bound applies: a graph of maximum degree d and diameter 2 has at most 1 + d + d(d-1)
nodes, which is 26 for d = 5 and 17 for d = 4. So diameters 2 and 3 are optimal for the first two instances.
For topology_50_4, diameter 3 would need a 50-node graph of degree at most 4 and diameter 3; the largest such graph
known has 41 nodes, so diameter 4 is very likely optimal but is not proven here.

## Method

A direct search over graphs; no MIP or QUBO model.

- Degrees are fixed at d (one node at d - 1 when n*d is odd). The start is a circulant graph (offsets 1..floor(d/2),
  plus the antipodal matching when d is odd), scrambled by 20 * |E| random degree-preserving switches.
- Move: a switch. Two edges (a,b) and (c,e) become (a,c) and (b,e), or (a,e) and (b,c), when both new edges are
  new and not loops. Degrees never change.
- Cost: with R_k(v) the set of nodes within distance k of v, kept as bitsets and grown level by level
  (R_{k+1}(v) = R_k(v) united with R_k(u) over the neighbours u of v),
  cost = far + near, where far = sum over v of (n - |R_D(v)|) counts ordered pairs further apart than the target
  diameter D, and near = sum over k = 1..D-1 of sum over v of (n - |R_k(v)|) rewards slack.
- Simulated annealing (Metropolis acceptance) with geometric cooling from T = 8 to T = 0.5 over 10,000,000 moves per
  round; each new round restarts from the best graph of the run. A run stops at the first graph with far = 0.
- Ten independent runs per instance with seeds 1 to 10. Every run reached the target. The submitted graph is the
  one from seed 1; runs are deterministic for a given seed and reproduce bit for bit.

## Verification

Every graph was re-checked by a separate program written independently of the search (Python, plain breadth-first
search from every node): node count, no loops or repeated edges, maximum degree, connectivity and the diameter.

## Hardware and software

Apple M5 Pro (18 cores: 6 performance, 12 efficiency), 24 GB RAM, macOS 26.6.2. Search in C, compiled with
Apple clang 21.0.0 at -O3; one single-threaded process per run on a shared machine (nice 10), so wall-clock times
include contention. Checker: Python 3.9.6. Runtimes in the CSV files are means over the ten runs.

## AI disclosure

generated: the search program (C), the checking program (Python) and this write-up were written with Claude
(Anthropic), model Claude Opus 5.5 (claude-opus-5-5), in Claude Code, and reviewed by the submitter, who takes
responsibility for the submission. Every solution was checked by the independent program described above. The
pull request was opened by the submitter.
