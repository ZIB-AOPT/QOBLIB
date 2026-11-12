# 4colors Research - exact dynamic program over the reduced count-space chain
# Proven optimal. Default checker parameters (capital C=10, ub=3, cs1=4, cs2=7),
# i.e. exactly what misc/ci/check_submission.py passes to check_portfolio.
# Objective re-verified in exact rational arithmetic.
instance po_a004_t04_orig
budget 4
lambda 1e-6
objective -13911
# period symbol long short
0 AAPL 0 1
0 GOOG 3 0
1 AAPL 0 1
1 NVDA 0 3
2 AAPL 1 0
2 NVDA 0 3
