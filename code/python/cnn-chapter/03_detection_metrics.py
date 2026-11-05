"""Intersection over Union, non-maximum suppression, and average precision.

Standard library only. Run: python 03_detection_metrics.py

Boxes are (x1, y1, x2, y2) with x2 > x1 and y2 > y1 in pixels.
"""


def area(b):
    return max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])


def iou(a, b):
    ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
    ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
    inter = area((ix1, iy1, ix2, iy2))
    union = area(a) + area(b) - inter
    return inter / union if union > 0 else 0.0


def nms(dets, thr):
    """dets: list of (score, box). Greedy: keep the best, drop boxes whose
    IoU with a kept box exceeds thr."""
    order = sorted(dets, key=lambda d: -d[0])
    kept = []
    for d in order:
        if all(iou(d[1], k[1]) <= thr for k in kept):
            kept.append(d)
    return kept


def soft_nms_scores(dets, sigma=0.5):
    """Gaussian Soft-NMS: decay scores instead of deleting boxes."""
    import math
    pool = sorted(dets, key=lambda d: -d[0])
    out = []
    while pool:
        pool.sort(key=lambda d: -d[0])
        best = pool.pop(0)
        out.append(best)
        pool = [(s * math.exp(-(iou(best[1], b) ** 2) / sigma), b) for s, b in pool]
    return out


def average_precision(dets, gts, thr=0.5):
    """dets: list of (score, image_id, box). gts: dict image_id -> list of boxes.
    Greedy matching by descending score, each ground truth matched once.
    Returns (AP with all-point interpolation, per-detection rows)."""
    n_gt = sum(len(v) for v in gts.values())
    used = {k: [False] * len(v) for k, v in gts.items()}
    rows, tp, fp = [], 0, 0
    pr = []
    for score, img, box in sorted(dets, key=lambda d: -d[0]):
        best, best_j = 0.0, -1
        for j, g in enumerate(gts.get(img, [])):
            v = iou(box, g)
            if v > best:
                best, best_j = v, j
        if best >= thr and not used[img][best_j]:
            used[img][best_j] = True
            tp += 1
            label = "TP"
        else:
            fp += 1
            label = "FP"
        prec, rec = tp / (tp + fp), tp / n_gt
        pr.append((rec, prec))
        rows.append((score, img, label, round(best, 3), round(prec, 3), round(rec, 3)))
    # all-point interpolation: precision envelope, then area under it
    recs = [0.0] + [r for r, _ in pr] + [1.0]
    precs = [0.0] + [p for _, p in pr] + [0.0]
    for i in range(len(precs) - 2, -1, -1):
        precs[i] = max(precs[i], precs[i + 1])
    ap = sum((recs[i + 1] - recs[i]) * precs[i + 1] for i in range(len(recs) - 1)
             if recs[i + 1] != recs[i])
    return ap, rows


def main():
    print("=== IoU worked example ===")
    a = (0, 0, 100, 100)
    b = (50, 50, 150, 150)
    print("A=(0,0,100,100) B=(50,50,150,150) IoU =", round(iou(a, b), 4),
          "(intersection 2500, union 17500)")
    c = (10, 10, 110, 110)
    print("A vs C=(10,10,110,110) IoU =", round(iou(a, c), 4))
    d = (0, 0, 50, 100)
    print("A vs D=(0,0,50,100) (half-width box) IoU =", round(iou(a, d), 4))

    print("\n=== Non-maximum suppression ===")
    dets = [(0.95, (100, 100, 200, 200)),
            (0.90, (105, 98, 205, 198)),
            (0.80, (130, 100, 230, 200)),
            (0.85, (300, 300, 380, 380)),
            (0.40, (110, 105, 210, 205)),
            (0.70, (160, 100, 260, 200))]
    print("pairwise IoU with the top box:")
    for s, bx in dets[1:]:
        print(f"  score {s:.2f} IoU {iou(dets[0][1], bx):.3f}")
    for thr in (0.5, 0.7):
        kept = nms(dets, thr)
        print(f"NMS threshold {thr}: keeps scores", [k[0] for k in kept])
    print("Soft-NMS (Gaussian, sigma 0.5) rescored:",
          [(round(s, 3)) for s, _ in soft_nms_scores(dets)])

    print("\n=== Average precision at IoU 0.5 ===")
    gts = {1: [(10, 10, 60, 60), (100, 100, 160, 160)],
           2: [(20, 20, 80, 80), (200, 50, 260, 110)]}
    dets = [(0.95, 1, (12, 12, 62, 62)),
            (0.90, 2, (22, 18, 82, 78)),
            (0.85, 1, (300, 300, 340, 340)),
            (0.80, 1, (98, 102, 158, 162)),
            (0.70, 2, (150, 150, 190, 190)),
            (0.60, 2, (205, 55, 265, 115)),
            (0.50, 1, (14, 14, 64, 64))]
    ap, rows = average_precision(dets, gts, 0.5)
    print("score image label bestIoU precision recall")
    for r in rows:
        print("  ", r)
    print("AP@0.5 =", round(ap, 4))
    ap75, _ = average_precision(dets, gts, 0.75)
    print("AP@0.75 =", round(ap75, 4))
    print("mean over thresholds 0.5..0.95 step 0.05:",
          round(sum(average_precision(dets, gts, 0.5 + 0.05 * i)[0]
                    for i in range(10)) / 10, 4))

    print("\n=== Small-object IoU sensitivity ===")
    for size in (10, 100):
        g = (0, 0, size, size)
        p = (2, 2, size + 2, size + 2)
        print(f"{size}x{size} box shifted by 2 px: IoU = {iou(g, p):.3f}")


if __name__ == "__main__":
    main()
