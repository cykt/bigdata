#!/usr/bin/env python3
"""Week 7 · Task 1 — k-means, and the thing that decides the answer.

Textbook §7.1 (clustering, the curse of dimensionality), §7.3 (k-means).

k-means is four lines: pick centroids, assign every point to the nearest one,
move each centroid to the mean of its points, repeat. It always converges.

It converges to a **local** optimum, and which one depends entirely on where you
started. That is not a footnote - it is the difference between a clustering that
means something and one that does not, and you can watch it happen on nine points.

    python3 task1_kmeans.py --verify
"""
import argparse, math, random

# Three obvious blobs of three points each. Any sensible clustering finds them.
BLOBS = [(0.0, 0.0), (0.2, 0.1), (0.1, 0.2),
         (8.0, 8.0), (8.2, 8.1), (8.1, 8.2),
         (0.0, 8.0), (0.2, 8.1), (0.1, 8.2)]


def euclidean(a, b):
    """Distance between two points of any dimension."""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def assign(points, centroids):
    """Nearest centroid for each point. Return a list of centroid indices.

    Ties go to the lower index, so that everybody's answer is the same.
    """
    out = []
    for p in points:
        best_i, best_d = 0, float("inf")
        for i, c in enumerate(centroids):
            d = euclidean(p, c)
            if d < best_d:  # strict: ties remain with the lower index
                best_i, best_d = i, d
        out.append(best_i)
    return out


def update(points, labels, k):
    """Move each centroid to the mean of its points.

    An empty cluster has no mean. Decide what you do - and say so, because the
    choice changes the result and there is more than one defensible answer.
    """
    dims = len(points[0])
    out = []
    for j in range(k):
        group = [p for p, label in zip(points, labels) if label == j]
        if group:
            out.append(tuple(sum(p[d] for p in group) / len(group)
                            for d in range(dims)))
        else:
            # An empty cluster keeps its previous position; kmeans supplies it.
            out.append(None)
    return out


def kmeans(points, k, init="random", seed=246, max_iter=100):
    """Run to convergence. Return (labels, centroids, sse).

    `sse` is the sum over points of the squared distance to their own centroid.
    It is what k-means minimises, and it is how you compare two runs.

    `init` is either:
        "random"   pick k points at random as the starting centroids
        "++"       k-means++ (§7.3.2): pick the first at random, then pick each
                   next one with probability proportional to the squared distance
                   to the nearest centroid already chosen

    Set `kmeans.iterations` to how many passes you used.
    """
    if not points or not 1 <= k <= len(points):
        raise ValueError("k must be between 1 and the number of points")
    rng = random.Random(seed)
    if init == "random":
        centroids = [tuple(points[i]) for i in rng.sample(range(len(points)), k)]
    elif init == "++":
        centroids = [tuple(points[rng.randrange(len(points))])]
        while len(centroids) < k:
            weights = [min(euclidean(p, c) ** 2 for c in centroids)
                       for p in points]
            total = sum(weights)
            if total == 0:
                candidates = [tuple(p) for p in points if tuple(p) not in centroids]
                centroids.append(rng.choice(candidates or [tuple(points[0])]))
            else:
                r = rng.random() * total
                for p, w in zip(points, weights):
                    r -= w
                    if r <= 0:
                        centroids.append(tuple(p))
                        break
    else:
        raise ValueError("init must be 'random' or '++'")

    for iteration in range(1, max_iter + 1):
        labels = assign(points, centroids)
        updated = update(points, labels, k)
        new_centroids = [old if new is None else new
                         for old, new in zip(centroids, updated)]
        if new_centroids == centroids:
            kmeans.iterations = iteration
            return labels, centroids, sse_of(points, labels, centroids)
        centroids = new_centroids
    kmeans.iterations = max_iter
    labels = assign(points, centroids)
    return labels, centroids, sse_of(points, labels, centroids)


def sse_of(points, labels, centroids):
    """Sum of squared distances from each point to its assigned centroid."""
    return sum(euclidean(p, centroids[label]) ** 2
               for p, label in zip(points, labels))


# ------------------------------------------------------------------- harness
def verify():
    fails = 0

    def check(label, ok, detail=""):
        nonlocal fails
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<50} {detail}")
        fails += not ok

    try:
        check("distance in 2d", abs(euclidean((0, 0), (3, 4)) - 5) < 1e-9)
        check("distance in 5d",
              abs(euclidean((0,) * 5, (1,) * 5) - math.sqrt(5)) < 1e-9)
    except NotImplementedError:
        print("  euclidean is still a stub"); return 1

    try:
        labels, cents, sse = kmeans(BLOBS, 3, init="++", seed=1)
    except NotImplementedError:
        print("  kmeans is still a stub"); return 1

    groups = {}
    for p, l in zip(BLOBS, labels):
        groups.setdefault(l, []).append(p)
    check("three clusters of three", sorted(len(g) for g in groups.values()) == [3, 3, 3],
          sorted(len(g) for g in groups.values()))
    check("the three blobs were recovered",
          all(max(q[0] for q in g) - min(q[0] for q in g) < 1 and
              max(q[1] for q in g) - min(q[1] for q in g) < 1
              for g in groups.values()))
    check("sse is small when clusters are right", sse < 1.0, f"sse {sse:.4f}")

    # Bad luck with random starts should sometimes be visibly worse.
    randoms = [kmeans(BLOBS, 3, init="random", seed=s)[2] for s in range(40)]
    plusplus = [kmeans(BLOBS, 3, init="++", seed=s)[2] for s in range(40)]
    check("random init sometimes lands badly", max(randoms) > min(randoms) * 5,
          f"sse from {min(randoms):.3f} to {max(randoms):.3f}")
    check("k-means++ is more reliable than random",
          sum(plusplus) / len(plusplus) <= sum(randoms) / len(randoms),
          f"mean sse: ++ {sum(plusplus) / len(plusplus):.3f} vs "
          f"random {sum(randoms) / len(randoms):.3f}")

    print(f"\n  {'all ok' if not fails else str(fails) + ' failed'}")
    return 1 if fails else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    raise SystemExit(verify() if a.verify else p.print_help())
