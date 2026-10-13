# 4colors Research - exact dynamic program over the reduced count-space chain
# Proven optimal. Default checker parameters (capital C=10, ub=3, cs1=4, cs2=7),
# i.e. exactly what misc/ci/check_submission.py passes to check_portfolio.
# Objective re-verified in exact rational arithmetic.
instance po_a005_t04_orig
budget 4
lambda 1e-5
objective -14419
# period symbol long short
0 GOOG 1 0
0 GOOGL 3 0
1 AAPL 0 1
1 NVDA 0 1
1 MSFT 0 2
2 AAPL 2 0
2 NVDA 0 1
2 MSFT 0 1
