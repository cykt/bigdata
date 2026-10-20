# Task 2 convergence results

| nodes | beta | tol | iterations | seconds |
|---:|---:|---:|---:|---:|
| 1200 | 0.5 | 1.0e-10 | 14 | 0.0074 |
| 1200 | 0.7 | 1.0e-10 | 17 | 0.0086 |
| 1200 | 0.85 | 1.0e-10 | 20 | 0.0109 |
| 1200 | 0.95 | 1.0e-10 | 23 | 0.0130 |
| 1200 | 0.99 | 1.0e-10 | 24 | 0.0130 |
| 1200 | 0.85 | 1.0e-06 | 12 | 0.0080 |
| 20000 | 0.85 | 1.0e-10 | 21 | 0.3359 |
| 20000 | 0.95 | 1.0e-10 | 24 | 0.3270 |

Machine: Windows-11-10.0.26300-SP0; Python 3.15.0.

Interpretation: iterations generally increase as beta approaches 1 because less probability teleports, so mixing is slower.

## Observations

### A3. Effect of beta

For the 1,200-node graph with tolerance `1e-10`, the iteration count increased
from 14 at beta `0.50` to 24 at beta `0.99`. As beta approaches 1, the surfer
teleports less often, so the Markov chain mixes more slowly and convergence
requires more iterations.

### A4. Effect of graph size

At beta `0.85`, the iteration count was 20 for 1,200 nodes and 21 for 20,000
nodes. At beta `0.95`, it was 23 and 24 respectively. Therefore, graph size
changed the iteration count very little, while wall-clock time increased from
about `0.011` seconds to `0.336` seconds at beta `0.85`. Each iteration must
process more nodes and edges, so runtime grows even when the number of
iterations remains nearly constant.

### A5. Effect of tolerance

At beta `0.85` on the 1,200-node graph, changing tolerance from `1e-6` to
`1e-10` increased the iteration count from 12 to 20: 8 additional iterations
for four extra decimal places of requested precision. A smaller tolerance
requires the rank vector to change by a smaller amount before stopping.

### A6. Top-10 ranking

The top-10 list first changed between beta `0.50` and beta `0.70`: `p00004`
and `p00000` exchanged positions. From beta `0.70` through `0.99`, the top-10
ordering was unchanged in this experiment. This indicates that the main
ranking was stable here, but beta can still affect borderline pages, so a
published ranking should report the beta value used.

### A7. Measurement environment

Platform: Windows 11 (`Windows-11-10.0.26300-SP0`)

Processor: Intel64 Family 6 Model 154 Stepping 3

Python: 3.15.0

RAM: 16 GB

Other programs running: Microsoft Edge and VS Code
