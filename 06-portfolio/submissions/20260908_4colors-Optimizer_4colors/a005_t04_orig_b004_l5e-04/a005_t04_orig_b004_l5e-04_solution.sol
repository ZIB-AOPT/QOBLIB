# 4colors Research - exact dynamic program over the reduced count-space chain
# Proven optimal. Default checker parameters (capital C=10, ub=3, cs1=4, cs2=7),
# i.e. exactly what misc/ci/check_submission.py passes to check_portfolio.
# Objective re-verified in exact rational arithmetic.
instance po_a005_t04_orig
budget 4
lambda 5e-4
objective -2562
# period symbol long short
0 AAPL 0 1
0 GOOGL 1 0
1 GOOG 2 0
1 GOOGL 0 2
2 GOOG 2 0
2 GOOGL 0 2
