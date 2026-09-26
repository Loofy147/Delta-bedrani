from time import perf_counter
from delta_matroid import complete_graph

for n in (16, 18, 20, 22, 24):
    G = complete_graph(n)
    t0 = perf_counter()
    count = G.feasible_count()
    dt = perf_counter() - t0
    expected = 2 ** (n - 1)
    print(f"K_{n}: feasible={count:,}, expected={expected:,}, time={dt:.6f}s")
