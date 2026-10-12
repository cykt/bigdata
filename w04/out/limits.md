# Task 2: Exact Counting and Flajolet-Martin

## Machine

- Platform: Windows-11-10.0.26300-SP0
- Processor: Intel64 Family 6 Model 154 Stepping 3
- Python: 3.13.9

## Measurements

| Stream size `n` | True distinct | Exact time | Exact peak memory | FM estimate | FM time | FM peak memory | FM ratio |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100,000 | 36,702 | 0.23 s | 3.93 MB | 57,821 | 46.55 s | 0.004 MB | 1.58x |
| 400,000 | 146,970 | 1.00 s | 11.59 MB | 183,761 | 197.27 s | 0.004 MB | 1.25x |
| 1,600,000 | 587,625 | 7.19 s | 46.65 MB | 887,123 | 920.71 s | 0.004 MB | 1.51x |
| 6,400,000 | 2,349,909 | 113.32 s | 188.29 MB | 3,295,029 | 7,589.40 s | 0.004 MB | 1.40x |

The four measurements span 64x, satisfying the required 16x range. The
Flajolet-Martin ratios are between 1.25x and 1.58x, so every estimate is within
the required factor of two.

## Memory growth

The exact method stores every distinct key in a Python `set`. Its peak memory
increases from 3.93 MB at 100,000 items to 188.29 MB at 6,400,000 items. Thus,
the exact memory requirement grows with the stream and becomes expensive at
the largest tested size.

Flajolet-Martin uses only a fixed collection of hash statistics. Its measured
peak memory stays almost constant, from 4,395 bytes to 4,463 bytes, while the
stream grows by 64x. This confirms that sketch memory is determined by the
number of hash registers rather than by the number of input items.

Using the first and last measurements, the approximate growth rates are:

- Exact memory: `(188.29 - 3.93) / (6,400,000 - 100,000)` MB per item,
  or approximately 0.029 MB per 1,000 items.
- Flajolet-Martin: approximately 68 bytes per 1,000,000 additional items,
  effectively constant at this scale.

## Accuracy and runtime

The FM estimate does not become steadily more accurate as `n` grows. Its ratio
varies from 1.25x to 1.58x, which is normal for a deliberately approximate
Flajolet-Martin sketch. The method saves memory but is much slower in this
implementation because each stream item is processed with many hash
functions.

At 6,400,000 items, exact counting took 113.32 seconds and used 188.29 MB,
whereas Flajolet-Martin took 7,589.40 seconds (about 126.5 minutes) while
using only about 0.004 MB of traced memory.

## Conclusion

Exact counting is preferable when the distinct set fits in memory and an exact
answer is required. Flajolet-Martin is preferable when the stream is too large
to store and an estimate within a factor of two is acceptable. These
measurements show the central trade-off: exact memory grows with the data,
while sketch memory remains essentially flat at the cost of approximation.
