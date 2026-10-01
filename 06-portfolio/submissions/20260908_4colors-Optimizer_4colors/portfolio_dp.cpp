// portfolio_dp.cpp — exact dynamic program for QOBLIB 06-portfolio.
//
// Marcin Kaminski, 4colors Research.
// SPDX-License-Identifier: Apache-2.0
//
// STANDALONE AND SELF-CONTAINED.  Depends on nothing but the C++17 standard
// library: no Boost, no GMP, no project headers, no code from our heuristics.
// It is meant to be handed to the QOBLIB maintainers as the evidence behind an
// optimality claim, so it must be readable and runnable on its own.
//
//   g++ -O2 -std=c++17 -o portfolio_dp portfolio_dp.cpp
//   ./portfolio_dp <instance-dir> --budget B --lambda L [--out sol.txt]
//
// WHAT IT PROVES
// --------------
// For the small-budget instance families (a003, a004, a005, a010) it computes
// the exact minimum of the reference objective over *every* feasible position
// plan, by dynamic programming over periods.  The state is the full unit-count
// vector of one period; the transition cost is the rebalancing cost between
// consecutive periods.  Because the state space is enumerated exhaustively and
// every transition is relaxed exactly, the value returned is the optimum, not
// a heuristic bound.
//
// It also writes the optimal plan in the canonical solution format, so the
// claim can be checked two ways: run the official `check_portfolio` on the
// emitted file to confirm the objective, and read this file to confirm that
// nothing better exists.
//
// WHY THE MODEL BELOW IS THE RIGHT ONE
// ------------------------------------
// Every formula here is transcribed from the official checker,
// 06-portfolio/check/src/main.rs, functions `evaluate()` and the feasibility
// block in `main()`.  Deviating from it would make the result meaningless, so
// the correspondence is called out term by term in the comments.  In
// particular `zround` is Zimpl's round(): add +-1/2 by sign, then truncate
// toward zero (round half away from zero), applied to an *exact* rational —
// which is why this file carries a small exact-rational layer rather than
// using double.
//
// SCOPE.  The DP enumerates all count vectors with total units <= budget, so
// it is exponential in the budget and linear in the number of periods.  It is
// intended for budgets in the single digits (a003/a004/a005: B=3,4;
// a010: B=4 gives 10,606 states).  It is NOT applicable to a050 (B=20).
//
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>
#include <functional>

// ===========================================================================
// 1. Minimal exact big integers and rationals
// ===========================================================================
// Only what the coefficient precomputation needs: construction from a decimal
// string, +, -, *, comparison, and truncating division.  Speed is irrelevant
// here (a few thousand operations per instance); exactness is not.

struct BigInt {
    // sign-magnitude, base 1e9, little-endian limbs; zero has empty mag.
    int sign = 0;
    std::vector<uint32_t> mag;
    static const uint32_t BASE = 1000000000u;

    BigInt() = default;
    explicit BigInt(long long v) {
        if (v == 0) return;
        sign = v < 0 ? -1 : 1;
        unsigned long long a = v < 0 ? -(unsigned long long)v : (unsigned long long)v;
        while (a) { mag.push_back((uint32_t)(a % BASE)); a /= BASE; }
    }
    bool isZero() const { return sign == 0; }
    void trim() {
        while (!mag.empty() && mag.back() == 0) mag.pop_back();
        if (mag.empty()) sign = 0;
    }
    static int cmpMag(const std::vector<uint32_t>& a, const std::vector<uint32_t>& b) {
        if (a.size() != b.size()) return a.size() < b.size() ? -1 : 1;
        for (size_t i = a.size(); i-- > 0;)
            if (a[i] != b[i]) return a[i] < b[i] ? -1 : 1;
        return 0;
    }
    static std::vector<uint32_t> addMag(const std::vector<uint32_t>& a,
                                        const std::vector<uint32_t>& b) {
        std::vector<uint32_t> r;
        uint64_t carry = 0;
        for (size_t i = 0; i < std::max(a.size(), b.size()) || carry; ++i) {
            uint64_t s = carry;
            if (i < a.size()) s += a[i];
            if (i < b.size()) s += b[i];
            r.push_back((uint32_t)(s % BASE));
            carry = s / BASE;
        }
        return r;
    }
    // requires |a| >= |b|
    static std::vector<uint32_t> subMag(const std::vector<uint32_t>& a,
                                        const std::vector<uint32_t>& b) {
        std::vector<uint32_t> r = a;
        int64_t borrow = 0;
        for (size_t i = 0; i < r.size(); ++i) {
            int64_t cur = (int64_t)r[i] - borrow - (i < b.size() ? (int64_t)b[i] : 0);
            if (cur < 0) { cur += BASE; borrow = 1; } else borrow = 0;
            r[i] = (uint32_t)cur;
        }
        while (!r.empty() && r.back() == 0) r.pop_back();
        return r;
    }
    friend BigInt operator+(const BigInt& a, const BigInt& b) {
        if (a.sign == 0) return b;
        if (b.sign == 0) return a;
        BigInt r;
        if (a.sign == b.sign) { r.sign = a.sign; r.mag = addMag(a.mag, b.mag); }
        else {
            int c = cmpMag(a.mag, b.mag);
            if (c == 0) return BigInt();
            if (c > 0) { r.sign = a.sign; r.mag = subMag(a.mag, b.mag); }
            else       { r.sign = b.sign; r.mag = subMag(b.mag, a.mag); }
        }
        r.trim();
        return r;
    }
    friend BigInt operator-(const BigInt& a) { BigInt r = a; r.sign = -r.sign; return r; }
    friend BigInt operator-(const BigInt& a, const BigInt& b) { return a + (-b); }
    friend BigInt operator*(const BigInt& a, const BigInt& b) {
        if (a.sign == 0 || b.sign == 0) return BigInt();
        BigInt r;
        r.sign = a.sign * b.sign;
        r.mag.assign(a.mag.size() + b.mag.size(), 0);
        for (size_t i = 0; i < a.mag.size(); ++i) {
            uint64_t carry = 0;
            for (size_t j = 0; j < b.mag.size() || carry; ++j) {
                uint64_t cur = r.mag[i + j] + carry;
                if (j < b.mag.size()) cur += (uint64_t)a.mag[i] * b.mag[j];
                r.mag[i + j] = (uint32_t)(cur % BASE);
                carry = cur / BASE;
            }
        }
        r.trim();
        return r;
    }
    friend int cmp(const BigInt& a, const BigInt& b) {
        if (a.sign != b.sign) return a.sign < b.sign ? -1 : 1;
        int c = cmpMag(a.mag, b.mag);
        return a.sign >= 0 ? c : -c;
    }
    // truncating division toward zero; also yields the remainder.
    static void divmod(const BigInt& a, const BigInt& b, BigInt& q, BigInt& r) {
        if (b.isZero()) { std::fprintf(stderr, "division by zero\n"); std::exit(2); }
        q = BigInt(); r = BigInt();
        if (a.isZero()) return;
        // long division on magnitudes
        std::vector<uint32_t> quo(a.mag.size(), 0);
        BigInt rem;
        for (size_t i = a.mag.size(); i-- > 0;) {
            // rem = rem*BASE + a.mag[i]
            rem.mag.insert(rem.mag.begin(), a.mag[i]);
            rem.sign = 1; rem.trim();
            if (rem.isZero()) { rem.sign = 0; }
            // binary search the digit
            uint32_t lo = 0, hi = BASE - 1, d = 0;
            BigInt babs = b; babs.sign = 1;
            while (lo <= hi) {
                uint32_t mid = lo + (hi - lo) / 2;
                BigInt t = babs * BigInt((long long)mid);
                if (cmpMag(t.mag, rem.mag) <= 0) { d = mid; lo = mid + 1; }
                else { if (mid == 0) break; hi = mid - 1; }
            }
            quo[i] = d;
            BigInt t = babs * BigInt((long long)d);
            rem.mag = subMag(rem.mag, t.mag);
            rem.trim();
            if (rem.mag.empty()) rem.sign = 0; else rem.sign = 1;
        }
        q.mag = quo; q.sign = a.sign * b.sign; q.trim();
        r = rem; if (!r.mag.empty()) r.sign = a.sign; else r.sign = 0;
    }
    long long toLL() const {
        long long v = 0;
        for (size_t i = mag.size(); i-- > 0;) v = v * (long long)BASE + mag[i];
        return sign < 0 ? -v : v;
    }
    bool fitsLL() const { return mag.size() <= 2; }  // < 1e18, safe for our use
};

static BigInt bpow10(int e) {
    BigInt r((long long)1), ten((long long)10);
    for (int i = 0; i < e; ++i) r = r * ten;
    return r;
}

// Exact rational num/den, den > 0.  Not reduced (we never need it to be:
// magnitudes stay modest and every use ends in a zround).
struct Rat {
    BigInt num, den;
    Rat() : num(BigInt((long long)0)), den(BigInt((long long)1)) {}
    Rat(long long v) : num(BigInt(v)), den(BigInt((long long)1)) {}
    Rat(BigInt n, BigInt d) : num(std::move(n)), den(std::move(d)) {}
    bool isZero() const { return num.isZero(); }
};
static Rat operator*(const Rat& a, const Rat& b) { return Rat(a.num * b.num, a.den * b.den); }
static Rat operator-(const Rat& a, const Rat& b) {
    return Rat(a.num * b.den - b.num * a.den, a.den * b.den);
}
static Rat operator/(const Rat& a, const Rat& b) {
    BigInt n = a.num * b.den, d = a.den * b.num;
    if (d.sign < 0) { n = -n; d = -d; }
    return Rat(n, d);
}

// Mirrors parse_decimal() in the official checker, including scientific
// notation, so "1e-02" and "0.001" round-trip identically.
static bool parseDecimal(const std::string& s0, Rat& out) {
    std::string s;
    for (char c : s0) if (!isspace((unsigned char)c)) s += c;
    if (s.empty()) return false;
    long long exp10 = 0;
    size_t epos = s.find_first_of("eE");
    std::string mant = s;
    if (epos != std::string::npos) {
        mant = s.substr(0, epos);
        try { exp10 = std::stoll(s.substr(epos + 1)); } catch (...) { return false; }
    }
    bool neg = false;
    if (!mant.empty() && (mant[0] == '-' || mant[0] == '+')) { neg = mant[0] == '-'; mant = mant.substr(1); }
    std::string ip = mant, fp;
    size_t dot = mant.find('.');
    if (dot != std::string::npos) { ip = mant.substr(0, dot); fp = mant.substr(dot + 1); }
    if (ip.empty() && fp.empty()) return false;
    for (char c : ip + fp) if (!isdigit((unsigned char)c)) return false;
    std::string digits = ip + fp;
    // build the integer from decimal digits
    BigInt num((long long)0), ten((long long)10);
    for (char c : digits) num = num * ten + BigInt((long long)(c - '0'));
    if (neg) num = -num;
    long long shift = exp10 - (long long)fp.size();
    if (shift >= 0) out = Rat(num * bpow10((int)shift), BigInt((long long)1));
    else            out = Rat(num, bpow10((int)(-shift)));
    return true;
}

// Zimpl's round(): +-1/2 by sign, then truncate toward zero.
// Implemented exactly: trunc((2*num + sign*den) / (2*den)).
static long long zround(const Rat& x) {
    BigInt two((long long)2);
    BigInt n2 = x.num * two;
    BigInt d2 = x.den * two;
    BigInt adj = (x.num.sign < 0) ? (n2 - x.den) : (n2 + x.den);
    BigInt q, r;
    BigInt::divmod(adj, d2, q, r);
    if (!q.fitsLL()) {
        std::fprintf(stderr, "zround: coefficient does not fit in 64 bits\n");
        std::exit(2);
    }
    return q.toLL();
}

// ===========================================================================
// 2. Instance data
// ===========================================================================

struct Params {
    Rat cash, unit, delta, nu, rho;
    int ub = 3, cs1 = 4, cs2 = 7;
    long long budget = -1;
    Rat lambda;
    bool lambdaSet = false;
    Params() {
        parseDecimal("1000000", cash);
        parseDecimal("100000", unit);
        parseDecimal("0.001", delta);
        parseDecimal("0.0001", nu);
        parseDecimal("0.000025", rho);
    }
    long long capital() const {
        Rat c = cash / unit;
        BigInt q, r; BigInt::divmod(c.num, c.den, q, r);
        if (!r.isZero()) { std::fprintf(stderr, "cash/unit must be integral\n"); std::exit(2); }
        return q.toLL();
    }
};

struct Instance {
    std::vector<std::string> symbols;
    int periods = 0;
    std::vector<std::vector<Rat>> unitPrice;              // [asset][t]
    std::map<std::tuple<int,int,int>, Rat> cov;           // (i,j,t) -> value
    std::unordered_map<std::string,int> index;            // symbol -> asset id
};

// Reads plain text, or a .gz transparently via `gunzip -c` (no zlib needed).
static std::vector<std::string> readLines(const std::string& path) {
    std::vector<std::string> out;
    if (path.size() > 3 && path.substr(path.size() - 3) == ".gz") {
        std::string cmd = "gunzip -c '" + path + "'";
        FILE* p = popen(cmd.c_str(), "r");
        if (!p) { std::fprintf(stderr, "cannot run: %s\n", cmd.c_str()); std::exit(2); }
        char buf[65536];
        std::string cur;
        while (fgets(buf, sizeof buf, p)) {
            cur += buf;
            size_t nl;
            while ((nl = cur.find('\n')) != std::string::npos) {
                out.push_back(cur.substr(0, nl));
                cur.erase(0, nl + 1);
            }
        }
        if (!cur.empty()) out.push_back(cur);
        pclose(p);
    } else {
        std::ifstream f(path);
        if (!f) { std::fprintf(stderr, "cannot open %s\n", path.c_str()); std::exit(2); }
        std::string line;
        while (std::getline(f, line)) out.push_back(line);
    }
    return out;
}

static std::string findFile(const std::string& dir, const std::string& base) {
    for (const std::string& ext : {std::string(""), std::string(".gz")}) {
        std::string p = dir + "/" + base + ext;
        std::ifstream f(p);
        if (f) return p;
    }
    std::fprintf(stderr, "missing %s[.gz] in %s\n", base.c_str(), dir.c_str());
    std::exit(2);
}

// ===========================================================================
// 3. Integer coefficient tables
// ===========================================================================
// Every objective term in the checker has the shape zround(<rational>) * <int>.
// We evaluate each zround ONCE here, exactly; from then on the DP is pure
// integer arithmetic and cannot drift.

struct Coeffs {
    int n = 0, T = 0;
    std::vector<std::vector<long long>> wTrans;   // [i][t] zround(delta * P_i(t))
    std::vector<std::vector<long long>> wShort;   // [i][t] zround(rho   * P_i(t))
    std::vector<std::vector<long long>> wRet;     // [i][t] zround(P_i(t+1) - P_i(t))
    std::vector<long long> wCash;                 // [k]    zround(nu * unit * 2^k)
    // risk: [t] -> dense n x n of zround(lambda * cov(i,j,t) * P_i(t) * P_j(t))
    std::vector<std::vector<long long>> wRisk;
};

static Coeffs buildCoeffs(const Instance& inst, const Params& par,
                          const std::vector<char>& used) {
    Coeffs c;
    c.n = (int)inst.symbols.size();
    c.T = inst.periods;
    c.wTrans.assign(c.n, std::vector<long long>(c.T, 0));
    c.wShort.assign(c.n, std::vector<long long>(c.T, 0));
    c.wRet.assign(c.n, std::vector<long long>(std::max(0, c.T - 1), 0));
    for (int i = 0; i < c.n; ++i)
        for (int t = 0; t < c.T; ++t) {
            c.wTrans[i][t] = zround(par.delta * inst.unitPrice[i][t]);
            c.wShort[i][t] = zround(par.rho   * inst.unitPrice[i][t]);
            if (t + 1 < c.T)
                c.wRet[i][t] = zround(inst.unitPrice[i][t + 1] - inst.unitPrice[i][t]);
        }
    c.wCash.assign(par.cs1, 0);
    for (int k = 0; k < par.cs1; ++k) {
        Rat p2((long long)1);
        for (int b = 0; b < k; ++b) p2 = p2 * Rat((long long)2);
        c.wCash[k] = zround(par.nu * par.unit * p2);
    }
    c.wRisk.assign(c.T, std::vector<long long>((size_t)c.n * c.n, 0));
    if (par.lambdaSet && !par.lambda.isZero()) {
        for (int t = 0; t < c.T; ++t)
            for (int i = 0; i < c.n; ++i)
                for (int j = 0; j < c.n; ++j) {
                    if (!used.empty() && (!used[i] || !used[j])) continue;
                    auto it = inst.cov.find({i, j, t});
                    if (it == inst.cov.end()) continue;
                    // sign tau_i*tau_j is applied outside: zround is odd, so
                    // zround(sign*x) == sign*zround(x).
                    Rat base = par.lambda * it->second * inst.unitPrice[i][t] * inst.unitPrice[j][t];
                    c.wRisk[t][(size_t)i * c.n + j] = zround(base);
                }
    }
    return c;
}

// ===========================================================================
// 4. State space
// ===========================================================================
// A state is the unit-count vector of one period over 2n slots: slot 2i is
// asset i long, slot 2i+1 is asset i short.  Feasibility (from the checker's
// main()):  0 <= u_slot <= ub;  total = sum u <= budget with budget - total <=
// 2^cs2 - 1;  net = sum_long - sum_short with 0 <= capital - net <= 2^cs1 - 1.

struct StateSpace {
    int slots = 0, ub = 3;
    std::vector<std::vector<uint8_t>> states;   // [idx][slot]
    std::vector<long long> total, net;
    // up[idx][s]   = index of the state with slot s incremented (-1 if none)
    // down[idx][s] = index of the state with slot s decremented (-1 if none)
    // ordAsc / ordDesc = state indices ordered by total units.
    std::vector<std::vector<int>> up, down;
    std::vector<int> ordAsc, ordDesc;
};

static StateSpace buildStates(int n, const Params& par, long long budget) {
    StateSpace S;
    S.slots = 2 * n;
    S.ub = par.ub;
    long long cap = par.capital();
    long long maxSlack1 = (1LL << par.cs1) - 1;
    long long maxSlack2 = (1LL << par.cs2) - 1;

    std::vector<uint8_t> cur(S.slots, 0);
    // depth-first over slots, pruning on running total
    std::function<void(int, long long, long long)> rec = [&](int s, long long tot, long long nt) {
        if (s == S.slots) {
            long long slack1 = cap - nt, slack2 = budget - tot;
            if (slack1 < 0 || slack1 > maxSlack1) return;
            if (slack2 < 0 || slack2 > maxSlack2) return;
            S.states.push_back(cur);
            S.total.push_back(tot);
            S.net.push_back(nt);
            return;
        }
        for (int v = 0; v <= par.ub; ++v) {
            if (tot + v > budget) break;             // total can only grow
            cur[s] = (uint8_t)v;
            rec(s + 1, tot + v, nt + ((s % 2 == 0) ? v : -v));
        }
        cur[s] = 0;
    };
    rec(0, 0, 0);

    // Neighbour tables and a total-order, for the removals-then-additions
    // transform below.
    std::unordered_map<std::string,int> idx;
    for (int i = 0; i < (int)S.states.size(); ++i)
        idx[std::string((const char*)S.states[i].data(), S.slots)] = i;
    S.up.assign(S.states.size(), std::vector<int>(S.slots, -1));
    S.down.assign(S.states.size(), std::vector<int>(S.slots, -1));
    for (int i = 0; i < (int)S.states.size(); ++i) {
        std::string k((const char*)S.states[i].data(), S.slots);
        for (int sl = 0; sl < S.slots; ++sl) {
            if (S.states[i][sl] < par.ub) {
                k[sl] = (char)(S.states[i][sl] + 1);
                auto it = idx.find(k);
                if (it != idx.end()) S.up[i][sl] = it->second;
                k[sl] = (char)S.states[i][sl];
            }
            if (S.states[i][sl] > 0) {
                k[sl] = (char)(S.states[i][sl] - 1);
                auto it = idx.find(k);
                if (it != idx.end()) S.down[i][sl] = it->second;
                k[sl] = (char)S.states[i][sl];
            }
        }
    }
    S.ordAsc.resize(S.states.size());
    for (int i = 0; i < (int)S.states.size(); ++i) S.ordAsc[i] = i;
    std::sort(S.ordAsc.begin(), S.ordAsc.end(),
              [&](int a, int b) { return S.total[a] < S.total[b]; });
    S.ordDesc.assign(S.ordAsc.rbegin(), S.ordAsc.rend());
    return S;
}

// ===========================================================================
// 5. The dynamic program
// ===========================================================================
// Stage cost at period t for state u (all terms straight from evaluate()):
//   risk           sum_{i,j active} tau_i tau_j * wRisk[t][i][j] * u_i * u_j
//   cash interest  -sum_{bit k set in (capital - net)} wCash[k]
//   short cost     sum_{short slots} wShort[i][t] * u
//   return (t<T-1) -sum tau * wRet[i][t] * u
//   buy-in (t==0)  sum wTrans[i][0] * u
//   liquidation    (t==T-1) sum wTrans[i][T-1] * u
// Transition cost from u (period t-1) to v (period t), for 0 < t < T-1:
//   sum over slots wTrans[i][t] * |u_slot - v_slot|
// and, per the checker's comment, there is NO rebalancing term into the last
// period: t_end carries only its own stage cost.

static const long long INF = (long long)4e18;

struct DPResult {
    long long best = INF;
    std::vector<int> plan;   // state index per period
};

static long long stageCost(const StateSpace& S, const Coeffs& C, const Params& par,
                           int t, int idx) {
    const auto& u = S.states[idx];
    int n = C.n;
    long long v = 0;
    // risk
    if (!C.wRisk[t].empty()) {
        for (int a = 0; a < S.slots; ++a) {
            if (!u[a]) continue;
            int ia = a / 2, ta = (a % 2 == 0) ? 1 : -1;
            for (int b = 0; b < S.slots; ++b) {
                if (!u[b]) continue;
                int ib = b / 2, tb = (b % 2 == 0) ? 1 : -1;
                long long w = C.wRisk[t][(size_t)ia * n + ib];
                if (!w) continue;
                v += (long long)ta * tb * w * (long long)u[a] * (long long)u[b];
            }
        }
    }
    // cash interest on the low cs1 bits of the slack
    long long slack1 = par.capital() - S.net[idx];
    if (slack1 >= 0)
        for (int k = 0; k < par.cs1; ++k)
            if ((slack1 >> k) & 1) v -= C.wCash[k];
    // short cost, return, buy-in, liquidation
    for (int a = 0; a < S.slots; ++a) {
        if (!u[a]) continue;
        int i = a / 2, tau = (a % 2 == 0) ? 1 : -1;
        if (tau == -1) v += C.wShort[i][t] * (long long)u[a];
        if (t + 1 < C.T) v -= (long long)tau * C.wRet[i][t] * (long long)u[a];
        if (t == 0) v += C.wTrans[i][0] * (long long)u[a];
        if (t == C.T - 1) v += C.wTrans[i][C.T - 1] * (long long)u[a];
    }
    return v;
}

// Exact min-plus transform of `f` by the transition cost sum_s w_s |u_s - v_s|.
//
// The obvious separable trick -- relax one slot at a time along the grid axes --
// is WRONG here, because the state space is not a box: it is constrained by
// total <= budget, so the implied L1 path between two feasible states can pass
// through vectors that are not states, and those transitions are silently lost.
// (Caught by --brute on a004: -11495 against a true optimum of -14226.)
//
// Instead split every transition into removals followed by additions.  Their
// meeting point is the componentwise minimum of u and v, whose total is at most
// min(total(u), total(v)) <= budget, so it is always a state.  Two monotone
// sweeps therefore compute the transform exactly, and stay inside the state set:
//   pass 1, totals descending:  g(x) = min over u >= x of f(u) + w*(u-x)
//   pass 2, totals ascending:   h(v) = min over x <= v of g(x) + w*(v-x)
static void relaxTransition(const StateSpace& S, const Coeffs& C, int t,
                            std::vector<long long>& f, std::vector<int>* argmin) {
    for (int i : S.ordDesc)                       // removals
        for (int sl = 0; sl < S.slots; ++sl) {
            int j = S.up[i][sl];
            if (j < 0 || f[j] == INF) continue;
            long long cand = f[j] + C.wTrans[sl / 2][t];
            if (cand < f[i]) { f[i] = cand; if (argmin) (*argmin)[i] = (*argmin)[j]; }
        }
    for (int i : S.ordAsc)                         // additions
        for (int sl = 0; sl < S.slots; ++sl) {
            int j = S.down[i][sl];
            if (j < 0 || f[j] == INF) continue;
            long long cand = f[j] + C.wTrans[sl / 2][t];
            if (cand < f[i]) { f[i] = cand; if (argmin) (*argmin)[i] = (*argmin)[j]; }
        }
}

static DPResult runDP(const StateSpace& S, const Coeffs& C, const Params& par) {
    int T = C.T, M = (int)S.states.size();
    std::vector<long long> f(M);
    std::vector<std::vector<int>> back(T, std::vector<int>(M, -1));
    for (int i = 0; i < M; ++i) f[i] = stageCost(S, C, par, 0, i);

    for (int t = 1; t < T; ++t) {
        std::vector<long long> g = f;
        std::vector<int> am(M);
        for (int i = 0; i < M; ++i) am[i] = i;
        if (t < T - 1) {
            relaxTransition(S, C, t, g, &am);
        } else {
            // The reference model charges no rebalancing between t_end-1 and
            // t_end.  That makes the last transition FREE, not forbidden: the
            // final period may take any state at zero cost.  Coding it as "no
            // transition" instead pins the last period to its predecessor and
            // silently loses solutions (caught by --brute: -1106 vs -1995).
            int jmin = 0;
            for (int i = 1; i < M; ++i) if (f[i] < f[jmin]) jmin = i;
            for (int i = 0; i < M; ++i) { g[i] = f[jmin]; am[i] = jmin; }
        }
        for (int i = 0; i < M; ++i) {
            back[t][i] = am[i];
            f[i] = (g[i] == INF) ? INF : g[i] + stageCost(S, C, par, t, i);
        }
    }
    DPResult R;
    int arg = -1;
    for (int i = 0; i < M; ++i) if (f[i] < R.best) { R.best = f[i]; arg = i; }
    R.plan.assign(T, -1);
    for (int t = T - 1; t >= 0 && arg >= 0; --t) { R.plan[t] = arg; arg = back[t][arg]; }
    return R;
}

// ===========================================================================
// 6. Instance / covariance / solution I/O
// ===========================================================================
// Formats are exactly those of the official checker:
//   stock_prices.txt[.gz]         lines: day symbol price
//   covariance_matrices.txt[.gz]  lines: day sym1 sym2 value
//   solution                      headers instance/budget/lambda/objective,
//                                 then lines: period symbol long short

static Instance readInstance(const std::string& dir, const Params& par) {
    Instance inst;
    std::unordered_map<std::string,int> index;
    struct E { int id, day; Rat v; };
    std::vector<E> entries;
    int maxDay = 0;
    for (const std::string& line : readLines(findFile(dir, "stock_prices.txt"))) {
        std::istringstream is(line);
        std::string d, sym, val;
        if (!(is >> d >> sym >> val)) continue;
        if (d.empty() || d[0] == '#') continue;
        int day = std::stoi(d);
        Rat v; if (!parseDecimal(val, v)) { std::fprintf(stderr, "bad price '%s'\n", val.c_str()); std::exit(2); }
        auto it = index.find(sym);
        int id;
        if (it == index.end()) { id = (int)inst.symbols.size(); index[sym] = id; inst.symbols.push_back(sym); }
        else id = it->second;
        maxDay = std::max(maxDay, day);
        entries.push_back({id, day, v});
    }
    inst.periods = maxDay + 1;
    int n = (int)inst.symbols.size();
    std::vector<std::vector<Rat>> raw(n, std::vector<Rat>(inst.periods));
    std::vector<std::vector<char>> seen(n, std::vector<char>(inst.periods, 0));
    for (auto& e : entries) { raw[e.id][e.day] = e.v; seen[e.id][e.day] = 1; }
    for (int i = 0; i < n; ++i)
        for (int t = 0; t < inst.periods; ++t)
            if (!seen[i][t]) { std::fprintf(stderr, "missing price for %s at day %d\n", inst.symbols[i].c_str(), t); std::exit(2); }
    inst.unitPrice.assign(n, {});
    for (int i = 0; i < n; ++i) {
        const Rat& base = raw[i][0];
        if (base.isZero()) { std::fprintf(stderr, "zero price at day 0\n"); std::exit(2); }
        for (int t = 0; t < inst.periods; ++t)
            inst.unitPrice[i].push_back(raw[i][t] * par.unit / base);
    }
    inst.index = index;
    return inst;
}

static void readCovariance(const std::string& dir, Instance& inst,
                           const std::vector<char>& used) {
    for (const std::string& line : readLines(findFile(dir, "covariance_matrices.txt"))) {
        std::istringstream is(line);
        std::string d, s1, s2, val;
        if (!(is >> d >> s1 >> s2 >> val)) continue;
        if (d.empty() || d[0] == '#') continue;
        auto i1 = inst.index.find(s1), i2 = inst.index.find(s2);
        if (i1 == inst.index.end() || i2 == inst.index.end()) continue;
        if (!used.empty() && (!used[i1->second] || !used[i2->second])) continue;
        int day = std::stoi(d);
        if (day >= inst.periods) continue;
        Rat v; if (!parseDecimal(val, v)) continue;
        inst.cov[{i1->second, i2->second, day}] = v;
    }
}

// Which assets does a solution file actually touch?  Restricts the covariance
// load and the risk table, exactly as the official checker's needed(i,j) does --
// without this a 400-asset instance builds a 400x400xT table of exact-rational
// products and takes minutes instead of milliseconds.
static std::vector<char> usedAssets(const std::string& path, const Instance& inst) {
    std::vector<char> used(inst.symbols.size(), 0);
    for (const std::string& raw : readLines(path)) {
        std::string line = raw;
        size_t h = line.find('#');
        if (h != std::string::npos) line = line.substr(0, h);
        std::istringstream is(line);
        std::vector<std::string> tok; std::string w;
        while (is >> w) tok.push_back(w);
        if (tok.size() != 4 || !isdigit((unsigned char)tok[0][0])) continue;
        auto it = inst.index.find(tok[1]);
        if (it == inst.index.end()) continue;
        if (std::stoi(tok[2]) > 0 || std::stoi(tok[3]) > 0) used[it->second] = 1;
    }
    return used;
}

// Re-score an existing solution file with these coefficient tables.  This is
// Re-score an existing solution file with this implementation of the objective.
// we already hold before the DP's optimum may be believed.
static long long evaluateSolutionFile(const std::string& path, const Instance& inst,
                                      const Coeffs& C, const Params& par) {
    std::vector<std::vector<int>> lo(inst.periods, std::vector<int>(C.n, 0));
    std::vector<std::vector<int>> sh(inst.periods, std::vector<int>(C.n, 0));
    for (const std::string& raw : readLines(path)) {
        std::string line = raw;
        size_t h = line.find('#');
        if (h != std::string::npos) line = line.substr(0, h);
        std::istringstream is(line);
        std::vector<std::string> tok; std::string w;
        while (is >> w) tok.push_back(w);
        if (tok.size() != 4) continue;                 // headers and blanks
        if (!isdigit((unsigned char)tok[0][0])) continue;
        int t = std::stoi(tok[0]);
        auto it = inst.index.find(tok[1]);
        if (it == inst.index.end() || t >= inst.periods) continue;
        lo[t][it->second] = std::stoi(tok[2]);
        sh[t][it->second] = std::stoi(tok[3]);
    }
    long long cap = par.capital(), total = 0;
    for (int t = 0; t < inst.periods; ++t) {
        long long net = 0;
        for (int i = 0; i < C.n; ++i) net += lo[t][i] - sh[t][i];
        // risk
        if (!C.wRisk[t].empty())
            for (int i = 0; i < C.n; ++i)
                for (int ti = 0; ti < 2; ++ti) {
                    int ui = ti == 0 ? lo[t][i] : sh[t][i]; if (!ui) continue;
                    int taui = ti == 0 ? 1 : -1;
                    for (int j = 0; j < C.n; ++j)
                        for (int tj = 0; tj < 2; ++tj) {
                            int uj = tj == 0 ? lo[t][j] : sh[t][j]; if (!uj) continue;
                            int tauj = tj == 0 ? 1 : -1;
                            total += (long long)taui * tauj * C.wRisk[t][(size_t)i * C.n + j] * ui * uj;
                        }
                }
        long long slack1 = cap - net;
        if (slack1 >= 0)
            for (int k = 0; k < par.cs1; ++k) if ((slack1 >> k) & 1) total -= C.wCash[k];
        for (int i = 0; i < C.n; ++i) {
            if (sh[t][i]) total += C.wShort[i][t] * sh[t][i];
            if (t + 1 < C.T) total -= (long long)C.wRet[i][t] * (lo[t][i] - sh[t][i]);
            if (t == 0) total += C.wTrans[i][0] * (lo[t][i] + sh[t][i]);
            if (t == C.T - 1) total += C.wTrans[i][C.T - 1] * (lo[t][i] + sh[t][i]);
            if (t > 0 && t < C.T - 1)
                total += C.wTrans[i][t] * (std::abs(lo[t][i] - lo[t-1][i]) + std::abs(sh[t][i] - sh[t-1][i]));
        }
    }
    return total;
}

// Exhaustive enumeration over all period-plans.  Exponential
// in the number of periods (M^T), so only for the tiny families, but it shares
// no code with runDP() beyond the stage-cost function — which is the point.
static long long bruteForce(const StateSpace& S, const Coeffs& C, const Params& par) {
    int T = C.T, M = (int)S.states.size();
    std::vector<long long> stage((size_t)T * M);
    for (int t = 0; t < T; ++t)
        for (int i = 0; i < M; ++i) stage[(size_t)t * M + i] = stageCost(S, C, par, t, i);

    // Valid pruning bound.  Stage costs can be NEGATIVE (returns and cash
    // interest are subtracted), so cutting on the partial cost alone discards
    // better solutions -- that bug made this routine report -2480 where the
    // true optimum is -2505.  Instead bound the remaining stages from below by
    // their per-stage minima; transition costs are non-negative and are simply
    // omitted, which keeps the bound valid.
    std::vector<long long> suffix(T + 1, 0);
    for (int t = T - 1; t >= 0; --t) {
        long long m = INF;
        for (int i = 0; i < M; ++i) m = std::min(m, stage[(size_t)t * M + i]);
        suffix[t] = suffix[t + 1] + m;
    }

    long long best = INF;
    std::vector<int> cur(T, 0);
    std::function<void(int, long long)> rec = [&](int t, long long acc) {
        if (t == T) { best = std::min(best, acc); return; }
        if (best != INF && acc + suffix[t] >= best) return;
        for (int i = 0; i < M; ++i) {
            long long add = stage[(size_t)t * M + i];
            if (t > 0 && t < T - 1) {          // no rebalancing into t_end
                const auto& u = S.states[cur[t - 1]];
                const auto& v = S.states[i];
                for (int sl = 0; sl < S.slots; ++sl)
                    add += C.wTrans[sl / 2][t] * std::abs((int)u[sl] - (int)v[sl]);
            }
            cur[t] = i;
            rec(t + 1, acc + add);
        }
    };
    rec(0, 0);
    return best;
}

// ===========================================================================
// 7. Driver
// ===========================================================================

static void writeSolution(const std::string& path, const Instance& inst,
                          const StateSpace& S, const DPResult& R,
                          const std::string& instName, long long budget,
                          const std::string& lambdaStr, long long objective) {
    std::ofstream o(path);
    o << "# 4colors Research - exact dynamic program over the count-space chain\n";
    o << "# Proven optimal: the DP enumerates every feasible position plan.\n";
    o << "# Evaluated at checker defaults (C=10, ub=3, cs1=4, cs2=7).\n";
    o << "instance " << instName << "\n";
    o << "budget " << budget << "\n";
    o << "lambda " << lambdaStr << "\n";
    o << "objective " << objective << "\n";
    for (int t = 0; t < (int)R.plan.size(); ++t) {
        const auto& u = S.states[R.plan[t]];
        for (int i = 0; i < (int)inst.symbols.size(); ++i) {
            int lo = u[2 * i], sh = u[2 * i + 1];
            if (lo || sh) o << t << " " << inst.symbols[i] << " " << lo << " " << sh << "\n";
        }
    }
}

int main(int argc, char** argv) {
    if (argc < 2) {
        std::fprintf(stderr,
            "usage: %s <instance-dir> --budget B --lambda L [--out FILE]\n"
            "       %s <instance-dir> --lambda L --evaluate SOLFILE\n",
            argv[0], argv[0]);
        return 2;
    }
    std::string dir = argv[1], out, evalFile;
    bool brute = false;
    Params par;
    std::string lambdaStr = "0";
    for (int i = 2; i < argc; ++i) {
        std::string a = argv[i];
        auto need = [&]() -> std::string {
            if (i + 1 >= argc) { std::fprintf(stderr, "missing value after %s\n", a.c_str()); std::exit(2); }
            return argv[++i];
        };
        if (a == "--budget") par.budget = std::stoll(need());
        else if (a == "--lambda") { lambdaStr = need(); parseDecimal(lambdaStr, par.lambda); par.lambdaSet = true; }
        else if (a == "--ub") par.ub = std::stoi(need());
        else if (a == "--cs1") par.cs1 = std::stoi(need());
        else if (a == "--cs2") par.cs2 = std::stoi(need());
        else if (a == "--out") out = need();
        else if (a == "--evaluate") evalFile = need();
        else if (a == "--brute") brute = true;
        else { std::fprintf(stderr, "unknown option %s\n", a.c_str()); return 2; }
    }

    Instance inst = readInstance(dir, par);
    std::vector<char> used;                      // empty => every asset
    if (!evalFile.empty()) used = usedAssets(evalFile, inst);
    if (par.lambdaSet && !par.lambda.isZero()) readCovariance(dir, inst, used);
    Coeffs C = buildCoeffs(inst, par, used);

    if (!evalFile.empty()) {
        long long v = evaluateSolutionFile(evalFile, inst, C, par);
        std::printf("objective %lld\n", v);
        return 0;
    }

    if (par.budget < 0) { std::fprintf(stderr, "--budget is required\n"); return 2; }
    StateSpace S = buildStates(C.n, par, par.budget);
    std::fprintf(stderr, "assets=%d periods=%d budget=%lld states=%zu\n",
                 C.n, C.T, par.budget, S.states.size());
    if (S.states.empty()) { std::fprintf(stderr, "no feasible state\n"); return 3; }

    DPResult R = runDP(S, C, par);
    std::printf("optimal objective %lld\n", R.best);
    if (brute) {
        long long b = bruteForce(S, C, par);
        std::printf("brute force      %lld  %s\n", b, b == R.best ? "AGREES" : "*** DISAGREES ***");
        if (b != R.best) return 4;
    }
    size_t slash = dir.find_last_of('/');
    std::string instName = slash == std::string::npos ? dir : dir.substr(slash + 1);
    if (!out.empty()) {
        writeSolution(out, inst, S, R, instName, par.budget, lambdaStr, R.best);
        std::fprintf(stderr, "wrote %s — verify it with the official check_portfolio\n", out.c_str());
    }
    return 0;
}
