# Task 2 · The crossover, measured on my machine

**Machine (A6)**

| | |
|---|---|
| OS | Windows 11 (10.0.26300), 64-bit |
| CPU | Intel 12th-gen hybrid (Family 6 Model 154 — P-cores + E-cores) |
| RAM | 16 GB (15.7 GiB usable, measured via GlobalMemoryStatusEx) |
| Python | 3.13.9 |
| Background load | VS Code + normal desktop background; nothing heavy was launched during measurement |
| Method | `task2_crossover.py` — wall clock (`perf_counter`) + `tracemalloc` peak, single run per point |

All numbers below are copied from `out/crossover.json`, measured on the machine above. They are **not** expected to match anyone else's.

## A1 · Sizes measured

Six sizes, spanning **16.96×** (requirement: ≥5 sizes, ≥16×):

```
125 → 250 → 500 → 1000 → 2000 → 2120
```

2120 is the ceiling of this harness on purpose: `bench.build()` produces exactly 2,000 + 120 planted-clone = **2,120 documents**, so any `--sizes` value beyond 2120 re-measures the same corpus and would be a fake data point.

## A3 · Time vs n (wall seconds, includes tracemalloc)

| n | brute force | comparisons | LSH (MinHash + banding) | LSH comparisons |
|---:|---:|---:|---:|---:|
| 125 | 0.075 s | 7,750 | 3.274 s | 0 |
| 250 | 0.246 s | 31,125 | 3.202 s | 1 |
| 500 | 1.261 s | 124,750 | 3.891 s | 7 |
| 1000 | 4.939 s | 499,500 | 4.708 s | 28 |
| 2000 | 18.182 s | 1,999,000 | 6.052 s | 112 |
| 2120 | 20.653 s | 2,246,140 | 7.177 s | 129 |

```
brute force (1 char ≈ 0.5 s)
125  █ 0.08
250  ▌ 0.25
500  ██▌ 1.26
1000 █████████▉ 4.94
2000 ████████████████████████████████████▎ 18.18
2120 █████████████████████████████████████████ 20.65

LSH (1 char ≈ 0.25 s)
125  █████████████ 3.27
250  █████████████ 3.20
500  ███████████████▌ 3.89
1000 ███████████████████ 4.71
2000 ████████████████████████▏ 6.05
2120 █████████████████████████████ 7.18
```

Brute force is flat then explodes; LSH starts high and climbs almost flat. They cross just below n = 1000.

## A4 · Is brute force actually quadratic?

Arithmetic on my own numbers (not an assertion).

**Consecutive doubling ratios** (ideal: ×4, last pair ×1.06 → ideal ×1.124):

| n → 2n | measured | ideal |
|---|---:|---:|
| 125 → 250 | 3.27× | 4× |
| 250 → 500 | 5.13× | 4× |
| 500 → 1000 | 3.92× | 4× |
| 1000 → 2000 | 3.68× | 4× |
| 2000 → 2120 | 1.136× | 1.124× |

**Anchor fit** — take c = t(2000)/2000² = 18.1823/4,000,000 = 4.546×10⁻⁶ s/doc², predict t = c·n²:

| n | predicted | measured | error |
|---:|---:|---:|---:|
| 125 | 0.071 s | 0.075 s | +5.8% |
| 250 | 0.284 s | 0.246 s | −13.5% |
| 500 | 1.136 s | 1.261 s | +11.0% |
| 1000 | 4.546 s | 4.939 s | +8.6% |
| 2120 | 20.435 s | 20.653 s | +1.1% |

**Verdict: held.** Every point fits c·n² within ~13%, and the exact pair count is a perfect n(n−1)/2 (7,750 at n=125, 2,246,140 at n=2120). The one off-ratio (250→500 = 5.13×) is single-run noise on a hybrid-core laptop, not a broken curve — the anchor fit absorbs it.

Per-comparison cost at n=2120: 20.65 s / 2,246,140 ≈ **9.2 µs** per Jaccard comparison (with tracemalloc attached).

## A5 · Peak memory at the largest n (n = 2120)

| method | peak bytes | ≈ |
|---|---:|---|
| BruteForce | 22,312 B | **21.8 KiB** |
| LSH finder | 40,012,900 B | **38.2 MiB** |

Brute force keeps almost nothing — a result set of found pairs — so its peak barely grows (7 KB → 27 KB across the whole sweep). LSH is ~**1,790×** heavier at n=2120, and the memory is paid *up front*:

- the precomputed hash table `cols`: 5,001 shingle ids × 176 hash functions ≈ 880k int objects ≈ ~32 MB,
- 2,120 signatures × 176 ints ≈ ~10 MB,
- banding keys: 2,120 × 44 ≈ 93k tuples ≈ ~8 MB.

That is the price of making comparisons cheap: LSH bought 40 MB of machinery to turn 2,246,140 comparisons into **129** — and still found all the pairs (129 calls, recall 100% in `bench.py --yours` on the same corpus).

## A7 · Where they cross

| n | brute − LSH |
|---:|---:|
| 500 | −2.63 s (brute wins) |
| 1000 | +0.23 s (LSH wins) |
| 2000 | +12.13 s (LSH wins big) |
| 2120 | +13.48 s |

The measured sign flip is between 500 and 1000. Linear interpolation of the difference gives **n ≈ 960**; the model fit (t = 3.2 s + 0.002 s/doc vs c·n²) puts it at ≈ 1,090. Call the crossover **n ≈ 1,000 documents** on this machine. Above it the gap grows quadratically for brute and only linearly for LSH: by n=2120 LSH is 2.9× faster, and extrapolated brute cost at n=10,000 is ~455 s per run.

## A8 · Why LSH loses at small n

LSH pays for machinery *before it compares anything*:

1. **Fixed signature setup ≈ 3.2 s, paid even for 125 documents.** `YourFinder._signatures` precomputes a hash value for every (shingle id, hash function) pair: 5,001 × 176 ≈ **880k modular multiplications** in pure Python. This cost is independent of n — at n=125 the LSH run makes **zero** similarity calls and still burns 3.27 s.
2. **Per-document signature pass**: 60 shingles × 176 min-updates per doc — linear, ≈ 2 s per extra 1,000 docs (250→1000 slope: 0.0020 s/doc).
3. **Banding**: 44 bucket inserts per doc, each building a tuple key — linear again.

So at n=500, brute force spends 1.26 s doing 124,750 genuinely useful comparisons, while LSH spends 3.89 s mostly computing hashes it did not need yet. Below the crossover you are paying for machinery you didn't use; the LSH call counter shows how little it got for it: **0, 1, 7** comparisons at n = 125, 250, 500.

## A2 · Where it hurt

The wall I actually hit is the **corpus, not the machine**: `bench.build()` ships exactly 2,120 documents, so n = 2120 is the last honest point — the task's suggested 4000/8000/16000 would silently re-measure the same 2,120 sets and fabricate a curve. At that ceiling brute force takes **20.7 s** of waiting per run — the first genuinely unpleasant point — and what ran out first was **time** (brute force peak memory was only 22 KB). Extrapolating the fitted quadratic: n = 10,000 → ~7.6 minutes per run; n = 100,000 → ~12.7 hours. Quadratic stops being usable long before "big data", exactly as advertised.

## Measurement caveats

- **tracemalloc inflates LSH more than brute.** The tracer taxes every allocation; LSH allocates ~1M int objects up front while brute allocates ~nothing per pair. Absolute LSH times above are upper bounds, so the *un-traced* crossover sits below n ≈ 1000; the comparison stays fair in the sense that both sides carry the same instrumentation.
- **Single runs.** The 250→500 ratio of 5.13× against the anchor fit's ±13% band shows the noise floor of one-shot timing on a hybrid-core laptop (background threads migrate between P- and E-cores). The quadratic conclusion does not depend on any single ratio.

### Cross-check at n = 2120 without tracemalloc

`python bench.py --yours` (same 2,120-document corpus, no memory tracing) confirms the caveat is real:

| method | with tracemalloc | without | inflation |
|---|---:|---:|---:|
| brute force | 20.65 s | 12.77 s | ×1.6 |
| LSH | 7.18 s | **1.61 s** | ×4.5 |

So un-traced, LSH is **7.9× faster** at n = 2120 and the true crossover lands lower — scaling the traced LSH curve by the measured 1.61/7.18 ratio and re-solving against the un-traced quadratic (c = 12.77/2120² = 2.84×10⁻⁶) puts it at roughly **n ≈ 600**. The reported crossover of ≈1,000 is therefore the conservative, instrumentation-inflated bound. Bench output is preserved in `out/bench.txt` (recall 100%, precision 100%, 129 comparisons instead of 2,246,140 → grade "strong").

