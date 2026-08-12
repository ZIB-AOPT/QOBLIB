// This file is part of QOBLIB - Quantum Optimization Benchmarking Library
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

//! QOBLIB portfolio optimization solution checker.
//!
//! Verifies a solution in the canonical portfolio solution format against an
//! instance (stock_prices / covariance_matrices) and recomputes the objective
//! of the reference model `models/binary_quadratic_programming/bqp_u3_c10.zpl`
//! in exact rational arithmetic. Coefficient rounding replicates Zimpl's
//! `round()` (round half away from zero on exact rationals), so the computed
//! objective agrees bit-for-bit with any solver run on the shipped LP/QUBO
//! files.
//!
//! Exit codes follow misc/ci/CHECKER_CONTRACT.md:
//!   0  VALID (well-formed and feasible)
//!   21 INFEASIBLE (well-formed, violates a constraint)
//!   10 INVALID_FILE (malformed solution file, out-of-range values,
//!      dimension mismatch, or a claimed objective that does not match)
//!   2  USAGE (bad arguments or unreadable instance files)

use flate2::read::GzDecoder;
use num_bigint::BigInt;
use num_rational::BigRational;
use num_traits::{One, Signed, Zero};
use std::collections::HashMap;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::{Path, PathBuf};
use std::process::exit;

const EXIT_VALID: i32 = 0;
const EXIT_INVALID_FILE: i32 = 10;
const EXIT_INFEASIBLE: i32 = 21;
const EXIT_USAGE: i32 = 2;

/// Model parameters. Defaults are those of parameter_u3_c10.zpl and apply to
/// every model variant shipped under models/ (only `budget` and `lambda` vary
/// between variants; they are read from the solution header or the command
/// line).
struct Params {
    cash: BigRational,
    unit: BigRational,
    delta: BigRational,
    nu: BigRational,
    rho: BigRational,
    upscale: BigRational,
    ub: u32,
    cs1: u32, // number of cash slack digits  (CS1 = {0..cs1-1})
    cs2: u32, // number of count slack digits (CS2 = {0..cs2-1})
    budget: Option<BigInt>,
    lambda: Option<BigRational>,
}

impl Params {
    fn default() -> Self {
        Params {
            cash: int(1_000_000),
            unit: int(100_000),
            delta: dec("0.001"),
            nu: dec("0.0001"),
            rho: dec("0.000025"),
            upscale: int(1),
            ub: 3,
            cs1: 4,
            cs2: 7,
            budget: None,
            lambda: None,
        }
    }
    fn capital(&self) -> BigInt {
        let c = &self.cash / &self.unit;
        assert!(c.is_integer(), "cash/unit must be integer");
        c.to_integer()
    }
}

fn int(v: i64) -> BigRational {
    BigRational::from_integer(BigInt::from(v))
}

fn dec(s: &str) -> BigRational {
    parse_decimal(s).unwrap_or_else(|| panic!("bad decimal constant {s}"))
}

/// Parse a decimal number (optionally in scientific notation) into an exact
/// rational. Returns None on malformed input.
fn parse_decimal(s: &str) -> Option<BigRational> {
    let s = s.trim();
    if s.is_empty() {
        return None;
    }
    let (mant, exp10) = match s.find(['e', 'E']) {
        Some(i) => (&s[..i], s[i + 1..].parse::<i64>().ok()?),
        None => (s, 0i64),
    };
    let (mant, neg) = match mant.strip_prefix('-') {
        Some(r) => (r, true),
        None => (mant.strip_prefix('+').unwrap_or(mant), false),
    };
    let (ipart, fpart) = match mant.find('.') {
        Some(i) => (&mant[..i], &mant[i + 1..]),
        None => (mant, ""),
    };
    if ipart.is_empty() && fpart.is_empty() {
        return None;
    }
    if !ipart.chars().all(|c| c.is_ascii_digit()) || !fpart.chars().all(|c| c.is_ascii_digit()) {
        return None;
    }
    let digits = format!("{ipart}{fpart}");
    let mut num: BigInt = digits.parse().ok()?;
    if neg {
        num = -num;
    }
    let shift = exp10 - fpart.len() as i64;
    let ten = BigInt::from(10);
    let (n, d) = if shift >= 0 {
        (num * ten.pow(shift as u32), BigInt::one())
    } else {
        (num, ten.pow((-shift) as u32))
    };
    Some(BigRational::new(n, d))
}

/// Zimpl's round(): add +-1/2 depending on sign, then truncate toward zero.
/// This is round-half-away-from-zero on exact rationals (numbgmp.c).
fn zround(x: &BigRational) -> BigInt {
    let half = BigRational::new(BigInt::one(), BigInt::from(2));
    let shifted = if x.is_negative() { x - half } else { x + half };
    shifted.trunc().to_integer()
}

// ---------------------------------------------------------------------------
// Instance data
// ---------------------------------------------------------------------------

struct Instance {
    symbols: Vec<String>,
    index: HashMap<String, usize>,
    periods: usize,
    /// p[s][t] = raw[s][t] * unit / raw[s][0]  (value of one unit)
    unit_prices: Vec<Vec<BigRational>>,
}

fn open_maybe_gz(path: &Path) -> std::io::Result<Box<dyn BufRead>> {
    let f = File::open(path)?;
    if path.extension().map(|e| e == "gz").unwrap_or(false) {
        Ok(Box::new(BufReader::new(GzDecoder::new(f))))
    } else {
        Ok(Box::new(BufReader::new(f)))
    }
}

fn find_data_file(dir: &Path, base: &str) -> Option<PathBuf> {
    for name in [format!("{base}.txt.gz"), format!("{base}.txt")] {
        let p = dir.join(&name);
        if p.is_file() {
            return Some(p);
        }
    }
    None
}

fn usage_err(msg: &str) -> ! {
    eprintln!("USAGE: {msg}");
    exit(EXIT_USAGE);
}

fn read_instance(dir: &Path, params: &Params) -> Instance {
    let price_path = find_data_file(dir, "stock_prices")
        .unwrap_or_else(|| usage_err(&format!("no stock_prices.txt[.gz] in {}", dir.display())));
    let reader = open_maybe_gz(&price_path)
        .unwrap_or_else(|e| usage_err(&format!("cannot open {}: {e}", price_path.display())));

    let mut symbols: Vec<String> = Vec::new();
    let mut index: HashMap<String, usize> = HashMap::new();
    let mut entries: Vec<(usize, usize, BigRational)> = Vec::new();
    let mut max_day = 0usize;
    for (ln, line) in reader.lines().enumerate() {
        let line = line.unwrap_or_else(|e| usage_err(&format!("read error in prices: {e}")));
        let line = line.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        let mut it = line.split_whitespace();
        let (d, s, v) = match (it.next(), it.next(), it.next()) {
            (Some(d), Some(s), Some(v)) => (d, s, v),
            _ => usage_err(&format!("prices line {}: expected 'day symbol price'", ln + 1)),
        };
        let day: usize = d
            .parse()
            .unwrap_or_else(|_| usage_err(&format!("prices line {}: bad day '{d}'", ln + 1)));
        let val = parse_decimal(v)
            .unwrap_or_else(|| usage_err(&format!("prices line {}: bad price '{v}'", ln + 1)));
        let id = *index.entry(s.to_string()).or_insert_with(|| {
            symbols.push(s.to_string());
            symbols.len() - 1
        });
        max_day = max_day.max(day);
        entries.push((id, day, val));
    }
    let periods = max_day + 1;
    let mut raw: Vec<Vec<Option<BigRational>>> = vec![vec![None; periods]; symbols.len()];
    for (id, day, val) in entries {
        raw[id][day] = Some(val);
    }
    let mut raw_prices = Vec::with_capacity(symbols.len());
    for (id, row) in raw.into_iter().enumerate() {
        let mut out = Vec::with_capacity(periods);
        for (t, v) in row.into_iter().enumerate() {
            match v {
                Some(v) => out.push(v),
                None => usage_err(&format!("missing price for {} at day {t}", symbols[id])),
            }
        }
        raw_prices.push(out);
    }
    let mut unit_prices = Vec::with_capacity(symbols.len());
    for row in &raw_prices {
        let base = &row[0];
        if base.is_zero() {
            usage_err("zero price at day 0");
        }
        unit_prices.push(row.iter().map(|v| v * &params.unit / base).collect());
    }
    Instance {
        symbols,
        index,
        periods,
        unit_prices,
    }
}

/// Load covariance entries for the (ordered) symbol pairs in `needed`.
/// Key: (i, j, t) with i, j symbol ids.
fn read_covariance(
    dir: &Path,
    inst: &Instance,
    needed: &dyn Fn(usize, usize) -> bool,
) -> HashMap<(usize, usize, usize), BigRational> {
    let cov_path = find_data_file(dir, "covariance_matrices").unwrap_or_else(|| {
        usage_err(&format!(
            "no covariance_matrices.txt[.gz] in {}",
            dir.display()
        ))
    });
    let reader = open_maybe_gz(&cov_path)
        .unwrap_or_else(|e| usage_err(&format!("cannot open {}: {e}", cov_path.display())));
    let mut cov = HashMap::new();
    for (ln, line) in reader.lines().enumerate() {
        let line = line.unwrap_or_else(|e| usage_err(&format!("read error in covariance: {e}")));
        let line = line.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        let mut it = line.split_whitespace();
        let (d, s1, s2, v) = match (it.next(), it.next(), it.next(), it.next()) {
            (Some(d), Some(s1), Some(s2), Some(v)) => (d, s1, s2, v),
            _ => usage_err(&format!(
                "covariance line {}: expected 'day sym1 sym2 value'",
                ln + 1
            )),
        };
        let (i, j) = match (inst.index.get(s1), inst.index.get(s2)) {
            (Some(&i), Some(&j)) => (i, j),
            _ => continue, // symbol not in price file: ignore
        };
        if !needed(i, j) {
            continue;
        }
        let day: usize = d
            .parse()
            .unwrap_or_else(|_| usage_err(&format!("covariance line {}: bad day '{d}'", ln + 1)));
        if day >= inst.periods {
            continue;
        }
        let val = parse_decimal(v)
            .unwrap_or_else(|| usage_err(&format!("covariance line {}: bad value '{v}'", ln + 1)));
        cov.insert((i, j, day), val);
    }
    cov
}

// ---------------------------------------------------------------------------
// Solution file
// ---------------------------------------------------------------------------

struct Solution {
    instance_name: Option<String>,
    budget: Option<BigInt>,
    lambda: Option<BigRational>,
    objective: Option<BigRational>,
    /// positions[(t, sym_id)] = (long units, short units)
    positions: HashMap<(usize, usize), (u32, u32)>,
}

fn parse_solution(path: &Path, inst: &Instance, params: &Params) -> Solution {
    let f = File::open(path)
        .unwrap_or_else(|e| panic!("cannot open solution file {}: {e}", path.display()));
    let reader = BufReader::new(f);
    let mut sol = Solution {
        instance_name: None,
        budget: None,
        lambda: None,
        objective: None,
        positions: HashMap::new(),
    };
    for (ln, line) in reader.lines().enumerate() {
        let line = line.unwrap_or_else(|e| panic!("read error in solution file: {e}"));
        let line = match line.find('#') {
            Some(i) => &line[..i],
            None => &line[..],
        };
        let line = line.trim();
        if line.is_empty() {
            continue;
        }
        let toks: Vec<&str> = line.split_whitespace().collect();
        let lno = ln + 1;
        let is_position = toks[0].chars().next().map(|c| c.is_ascii_digit()).unwrap_or(false);
        match (is_position, toks[0]) {
            (false, "instance" | "budget" | "lambda" | "objective") => {
                if toks.len() != 2 {
                    panic!("line {lno}: header '{}' needs exactly one value", toks[0]);
                }
                match toks[0] {
                    "instance" => {
                        if sol.instance_name.replace(toks[1].to_string()).is_some() {
                            panic!("line {lno}: duplicate 'instance' header");
                        }
                    }
                    "budget" => {
                        let b: BigInt = toks[1]
                            .parse()
                            .unwrap_or_else(|_| panic!("line {lno}: bad budget '{}'", toks[1]));
                        if b.is_negative() {
                            panic!("line {lno}: budget must be non-negative");
                        }
                        if sol.budget.replace(b).is_some() {
                            panic!("line {lno}: duplicate 'budget' header");
                        }
                    }
                    "lambda" => {
                        let l = parse_decimal(toks[1])
                            .unwrap_or_else(|| panic!("line {lno}: bad lambda '{}'", toks[1]));
                        if l.is_negative() {
                            panic!("line {lno}: lambda must be non-negative");
                        }
                        if sol.lambda.replace(l).is_some() {
                            panic!("line {lno}: duplicate 'lambda' header");
                        }
                    }
                    "objective" => {
                        let o = parse_decimal(toks[1])
                            .unwrap_or_else(|| panic!("line {lno}: bad objective '{}'", toks[1]));
                        if sol.objective.replace(o).is_some() {
                            panic!("line {lno}: duplicate 'objective' header");
                        }
                    }
                    _ => unreachable!(),
                }
            }
            (true, _) => {
                if toks.len() != 4 {
                    panic!("line {lno}: expected 'period symbol long short', got '{line}'");
                }
                let t: usize = toks[0]
                    .parse()
                    .unwrap_or_else(|_| panic!("line {lno}: bad period '{}'", toks[0]));
                if t >= inst.periods {
                    panic!(
                        "line {lno}: period {t} out of range (instance has periods 0..{})",
                        inst.periods - 1
                    );
                }
                let sym = toks[1];
                let id = *inst
                    .index
                    .get(sym)
                    .unwrap_or_else(|| panic!("line {lno}: unknown asset symbol '{sym}'"));
                let lo: u32 = toks[2]
                    .parse()
                    .unwrap_or_else(|_| panic!("line {lno}: bad long count '{}'", toks[2]));
                let sh: u32 = toks[3]
                    .parse()
                    .unwrap_or_else(|_| panic!("line {lno}: bad short count '{}'", toks[3]));
                if lo > params.ub || sh > params.ub {
                    panic!(
                        "line {lno}: unit count exceeds per-asset bound ub={} (long={lo}, short={sh})",
                        params.ub
                    );
                }
                if sol.positions.insert((t, id), (lo, sh)).is_some() {
                    panic!("line {lno}: duplicate position line for period {t}, asset {sym}");
                }
            }
            (false, other) => panic!("line {lno}: unknown header key '{other}'"),
        }
    }
    sol
}

// ---------------------------------------------------------------------------
// Evaluation
// ---------------------------------------------------------------------------

struct Objective {
    risk: BigInt,
    ret: BigInt,
    transaction: BigInt,
    cash_interest: BigInt,
    short_cost: BigInt,
    liquidation: BigInt,
}

impl Objective {
    fn total(&self) -> BigInt {
        &self.risk + &self.ret + &self.transaction + &self.cash_interest + &self.short_cost
            + &self.liquidation
    }
}

/// Per period, per asset: (long units, short units), zero-filled.
fn counts_at(sol: &Solution, t: usize, id: usize) -> (i64, i64) {
    match sol.positions.get(&(t, id)) {
        Some(&(lo, sh)) => (lo as i64, sh as i64),
        None => (0, 0),
    }
}

fn evaluate(
    inst: &Instance,
    sol: &Solution,
    params: &Params,
    lambda: &BigRational,
    cov: &HashMap<(usize, usize, usize), BigRational>,
) -> Objective {
    let t_end = inst.periods - 1;
    let mut obj = Objective {
        risk: BigInt::zero(),
        ret: BigInt::zero(),
        transaction: BigInt::zero(),
        cash_interest: BigInt::zero(),
        short_cost: BigInt::zero(),
        liquidation: BigInt::zero(),
    };

    // active (id, tau) groups per period with unit counts
    let mut active: Vec<Vec<(usize, i32, i64)>> = vec![Vec::new(); inst.periods];
    for (&(t, id), &(lo, sh)) in &sol.positions {
        if lo > 0 {
            active[t].push((id, 1, lo as i64));
        }
        if sh > 0 {
            active[t].push((id, -1, sh as i64));
        }
    }
    let capital = params.capital();

    for t in 0..inst.periods {
        // ---- risk: sum over ordered pairs of active groups
        if !lambda.is_zero() {
            for &(i, taui, ui) in &active[t] {
                for &(j, tauj, uj) in &active[t] {
                    let c = cov
                        .get(&(i, j, t))
                        .unwrap_or_else(|| {
                            usage_err(&format!(
                                "missing covariance entry ({}, {}, {t})",
                                inst.symbols[i], inst.symbols[j]
                            ))
                        });
                    let sign = BigRational::from_integer(BigInt::from(taui * tauj));
                    let base = lambda
                        * &sign
                        * c
                        * &inst.unit_prices[i][t]
                        * &inst.unit_prices[j][t];
                    obj.risk += zround(&base) * BigInt::from(ui) * BigInt::from(uj);
                }
            }
        }

        // ---- cash interest on slack digits
        let net: i64 = active[t].iter().map(|&(_, tau, u)| tau as i64 * u).sum();
        let slack1 = &capital - BigInt::from(net);
        if slack1 >= BigInt::zero() {
            // digits are well-defined only for representable slack; the
            // feasibility check reports violations separately.
            if let Ok(s) = u64::try_from(&slack1) {
                for k in 0..params.cs1 {
                    if (s >> k) & 1 == 1 {
                        let pow2 = BigRational::from_integer(BigInt::one() << (k as usize));
                        let coef = zround(&(&params.nu * &params.unit * pow2));
                        obj.cash_interest -= coef;
                    }
                }
            }
        }

        // ---- short selling cost
        for &(i, tau, u) in &active[t] {
            if tau == -1 {
                obj.short_cost += zround(&(&params.rho * &inst.unit_prices[i][t])) * BigInt::from(u);
            }
        }

        // ---- return for t in [t_beg, t_end)
        if t < t_end {
            for &(i, tau, u) in &active[t] {
                let dp = &inst.unit_prices[i][t + 1] - &inst.unit_prices[i][t];
                let signed = BigRational::from_integer(BigInt::from(tau)) * dp;
                obj.ret -= zround(&signed) * BigInt::from(u);
            }
        }

        // ---- transaction cost
        if t == 0 {
            // initial buy-in: every unit held at t_beg
            for &(i, _tau, u) in &active[t] {
                obj.transaction +=
                    zround(&(&params.delta * &inst.unit_prices[i][t])) * BigInt::from(u);
            }
        } else if t < t_end {
            // rebalancing between t-1 and t: |delta units| per (asset, tau)
            // (canonical slot assignment fills copies 1..u, minimizing XOR)
            let mut groups: Vec<(usize, i32)> = Vec::new();
            for &(i, tau, _) in active[t - 1].iter().chain(active[t].iter()) {
                if !groups.contains(&(i, tau)) {
                    groups.push((i, tau));
                }
            }
            for (i, tau) in groups {
                let (lo_p, sh_p) = counts_at(sol, t - 1, i);
                let (lo_c, sh_c) = counts_at(sol, t, i);
                let (prev, cur) = if tau == 1 { (lo_p, lo_c) } else { (sh_p, sh_c) };
                let flips = (prev - cur).abs();
                if flips > 0 {
                    obj.transaction += zround(&(&params.delta * &inst.unit_prices[i][t]))
                        * BigInt::from(flips);
                }
            }
        }
        // note: the reference model has no rebalancing term between t_end-1
        // and t_end; positions at t_end only incur the liquidation cost below.

        // ---- liquidation at t_end
        if t == t_end {
            for &(i, _tau, u) in &active[t] {
                obj.liquidation +=
                    zround(&(&params.delta * &inst.unit_prices[i][t])) * BigInt::from(u);
            }
        }
    }

    // upscale (integer 1 in all shipped models; kept for completeness)
    let up = zround(&params.upscale);
    obj.risk *= &up;
    obj.ret *= &up;
    obj.transaction *= &up;
    obj.cash_interest *= &up;
    obj.short_cost *= &up;
    obj.liquidation *= &up;
    obj
}

// ---------------------------------------------------------------------------
// main
// ---------------------------------------------------------------------------

fn print_help() {
    println!(
        "Usage: check_portfolio <instance-dir> <solution-file> [options]

  <instance-dir>   directory with stock_prices.txt[.gz] and
                   covariance_matrices.txt[.gz], e.g.
                   ../instances/po_a010_t10_orig
                   (alternatively the instances root; the directory is then
                   resolved from the solution's 'instance' header)
  <solution-file>  solution in the canonical portfolio format (see README)

Options (defaults match models/binary_quadratic_programming/parameter_u3_c10.zpl):
  --budget B     asset budget, overrides the solution header
  --lambda L     risk weight, overrides the solution header
  --ub N         units per asset and direction        [3]
  --cash V       total cash                           [1000000]
  --unit V       cash per unit                        [100000]
  --delta V      transaction cost rate                [0.001]
  --nu V         cash interest rate                   [0.0001]
  --rho V        short selling cost rate              [0.000025]
  --cs1 N        number of cash slack bits            [4]
  --cs2 N        number of count slack bits           [7]
  --upscale V    objective scaling                    [1]
  -h, --help     show this help"
    );
}

fn main() {
    // Per CHECKER_CONTRACT.md: any parse panic is an INVALID_FILE.
    std::panic::set_hook(Box::new(|info| {
        let msg = info
            .payload()
            .downcast_ref::<String>()
            .cloned()
            .or_else(|| info.payload().downcast_ref::<&str>().map(|s| s.to_string()))
            .unwrap_or_else(|| info.to_string());
        eprintln!("INVALID_FILE: {msg}");
        exit(EXIT_INVALID_FILE);
    }));

    let args: Vec<String> = std::env::args().collect();
    let mut params = Params::default();
    let mut positional: Vec<String> = Vec::new();
    let mut i = 1;
    while i < args.len() {
        let a = &args[i];
        let val = |i: &mut usize| -> String {
            *i += 1;
            args.get(*i)
                .unwrap_or_else(|| usage_err(&format!("missing value after {a}")))
                .clone()
        };
        match a.as_str() {
            "-h" | "--help" => {
                print_help();
                exit(EXIT_VALID);
            }
            "--budget" => {
                params.budget = Some(
                    val(&mut i)
                        .parse()
                        .unwrap_or_else(|_| usage_err("bad --budget value")),
                )
            }
            "--lambda" => {
                params.lambda =
                    Some(parse_decimal(&val(&mut i)).unwrap_or_else(|| usage_err("bad --lambda")))
            }
            "--ub" => params.ub = val(&mut i).parse().unwrap_or_else(|_| usage_err("bad --ub")),
            "--cash" => {
                params.cash = parse_decimal(&val(&mut i)).unwrap_or_else(|| usage_err("bad --cash"))
            }
            "--unit" => {
                params.unit = parse_decimal(&val(&mut i)).unwrap_or_else(|| usage_err("bad --unit"))
            }
            "--delta" => {
                params.delta =
                    parse_decimal(&val(&mut i)).unwrap_or_else(|| usage_err("bad --delta"))
            }
            "--nu" => {
                params.nu = parse_decimal(&val(&mut i)).unwrap_or_else(|| usage_err("bad --nu"))
            }
            "--rho" => {
                params.rho = parse_decimal(&val(&mut i)).unwrap_or_else(|| usage_err("bad --rho"))
            }
            "--cs1" => params.cs1 = val(&mut i).parse().unwrap_or_else(|_| usage_err("bad --cs1")),
            "--cs2" => params.cs2 = val(&mut i).parse().unwrap_or_else(|_| usage_err("bad --cs2")),
            "--upscale" => {
                params.upscale =
                    parse_decimal(&val(&mut i)).unwrap_or_else(|| usage_err("bad --upscale"))
            }
            _ if a.starts_with('-') => usage_err(&format!("unknown option {a}")),
            _ => positional.push(a.clone()),
        }
        i += 1;
    }
    if positional.len() != 2 {
        print_help();
        exit(EXIT_USAGE);
    }
    let mut inst_dir = PathBuf::from(&positional[0]);
    let sol_path = PathBuf::from(&positional[1]);
    if !sol_path.is_file() {
        // A missing solution file is an infrastructure error, not a statement
        // about the solution.
        usage_err(&format!("solution file {} not found", sol_path.display()));
    }

    // The instance dir may be the instances root; peek at the solution header
    // to resolve the concrete instance directory in that case.
    if find_data_file(&inst_dir, "stock_prices").is_none() {
        if let Some(name) = peek_instance_name(&sol_path) {
            let candidate = inst_dir.join(&name);
            if find_data_file(&candidate, "stock_prices").is_some() {
                inst_dir = candidate;
            }
        }
    }

    let inst = read_instance(&inst_dir, &params);
    let sol = parse_solution(&sol_path, &inst, &params);

    if let (Some(hdr), Some(dir_name)) = (
        sol.instance_name.as_deref(),
        inst_dir.file_name().and_then(|n| n.to_str()),
    ) {
        if hdr != dir_name {
            println!("Warning: solution header instance '{hdr}' vs instance directory '{dir_name}'");
        }
    }

    let budget = params
        .budget
        .clone()
        .or_else(|| sol.budget.clone())
        .unwrap_or_else(|| usage_err("budget not given (solution header 'budget' or --budget)"));
    let lambda = params
        .lambda
        .clone()
        .or_else(|| sol.lambda.clone())
        .unwrap_or_else(|| usage_err("lambda not given (solution header 'lambda' or --lambda)"));

    println!(
        "Instance: {} ({} assets, {} periods)",
        inst_dir
            .file_name()
            .and_then(|n| n.to_str())
            .unwrap_or("?"),
        inst.symbols.len(),
        inst.periods
    );
    println!(
        "Model:    B={budget}, lambda={}, ub={}, C={}, slack bits {}+{}",
        ratio_str(&lambda),
        params.ub,
        params.capital(),
        params.cs1,
        params.cs2
    );

    // ---- feasibility ------------------------------------------------------
    let capital = params.capital();
    let max_slack1 = (BigInt::one() << (params.cs1 as usize)) - 1;
    let max_slack2 = (BigInt::one() << (params.cs2 as usize)) - 1;
    let mut infeasible = false;
    for t in 0..inst.periods {
        let mut net = BigInt::zero();
        let mut tot = BigInt::zero();
        for (&(tt, _), &(lo, sh)) in &sol.positions {
            if tt == t {
                net += BigInt::from(lo as i64 - sh as i64);
                tot += BigInt::from(lo as i64 + sh as i64);
            }
        }
        let slack1 = &capital - &net;
        let slack2 = &budget - &tot;
        let ok1 = slack1 >= BigInt::zero() && slack1 <= max_slack1;
        let ok2 = slack2 >= BigInt::zero() && slack2 <= max_slack2;
        let status = if ok1 && ok2 { "ok" } else { "VIOLATED" };
        println!(
            "t={t:>2}: net={net:>4} total={tot:>4} cash_slack={slack1:>4} count_slack={slack2:>4}  {status}"
        );
        if !ok1 {
            println!(
                "   capital constraint failed: net position {net} requires cash slack {slack1} outside [0, {max_slack1}]"
            );
            infeasible = true;
        }
        if !ok2 {
            println!(
                "   budget constraint failed: {tot} positions require count slack {slack2} outside [0, {max_slack2}]"
            );
            infeasible = true;
        }
    }
    if infeasible {
        println!("Solution is INFEASIBLE");
        exit(EXIT_INFEASIBLE);
    }

    // ---- objective --------------------------------------------------------
    let cov = if lambda.is_zero() {
        HashMap::new()
    } else {
        let mut used = vec![false; inst.symbols.len()];
        for (&(_, id), &(lo, sh)) in &sol.positions {
            if lo > 0 || sh > 0 {
                used[id] = true;
            }
        }
        read_covariance(&inst_dir, &inst, &|i, j| used[i] && used[j])
    };
    let obj = evaluate(&inst, &sol, &params, &lambda, &cov);
    let total = obj.total();
    println!("Objective breakdown:");
    println!("  risk            {:>16}", obj.risk);
    println!("  return          {:>16}", obj.ret);
    println!("  transaction     {:>16}", obj.transaction);
    println!("  cash interest   {:>16}", obj.cash_interest);
    println!("  short cost      {:>16}", obj.short_cost);
    println!("  liquidation     {:>16}", obj.liquidation);
    println!("Objective value = {total}");

    if let Some(claimed) = &sol.objective {
        let total_rat = BigRational::from_integer(total.clone());
        if claimed != &total_rat {
            eprintln!(
                "INVALID_FILE: claimed objective {} does not match computed objective {total}",
                ratio_str(claimed)
            );
            exit(EXIT_INVALID_FILE);
        }
        println!("Claimed objective matches.");
    }
    println!("Solution successfully verified");
    exit(EXIT_VALID);
}

/// Read only the 'instance' header from a solution file (best effort).
fn peek_instance_name(path: &Path) -> Option<String> {
    let f = File::open(path).ok()?;
    for line in BufReader::new(f).lines().map_while(Result::ok) {
        let line = match line.find('#') {
            Some(i) => line[..i].trim().to_string(),
            None => line.trim().to_string(),
        };
        let toks: Vec<&str> = line.split_whitespace().collect();
        if toks.len() == 2 && toks[0] == "instance" {
            return Some(toks[1].to_string());
        }
    }
    None
}

fn ratio_str(r: &BigRational) -> String {
    if r.is_integer() {
        return r.to_integer().to_string();
    }
    // decimal display when the denominator is a power of ten
    let d = r.denom().to_string();
    if d.starts_with('1') && d[1..].chars().all(|c| c == '0') {
        let frac_digits = d.len() - 1;
        let neg = r.numer() < &BigInt::zero();
        let n = r.numer().magnitude().to_string();
        let n = format!("{:0>width$}", n, width = frac_digits + 1);
        let split = n.len() - frac_digits;
        let (ip, fp) = (&n[..split], &n[split..]);
        return format!("{}{}.{}", if neg { "-" } else { "" }, ip, fp);
    }
    format!("{}/{}", r.numer(), r.denom())
}
