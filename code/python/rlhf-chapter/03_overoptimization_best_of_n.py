"""Best-of-n against an imperfect proxy reward: Goodhart in a few lines.

Standard library only. Each candidate has a true quality t ~ N(0,1) and an
exploitable feature e ~ N(0,1) (think length or confident tone) that the proxy
rewards but humans do not. proxy = t + 0.6*e + noise. Best-of-n picks the
candidate with the highest proxy. We report the mean true quality, mean proxy,
and the KL cost of best-of-n, which is log(n) - (n-1)/n (upper bound, nats).
"""

import math
import random


def trial(n, rng):
    best_proxy, best_true, best_e = -1e9, 0.0, 0.0
    for _ in range(n):
        t = rng.gauss(0, 1)
        e = rng.gauss(0, 1)
        proxy = t + 0.6 * e + rng.gauss(0, 0.3)
        if proxy > best_proxy:
            best_proxy, best_true, best_e = proxy, t, e
    return best_proxy, best_true, best_e


def main():
    rng = random.Random(11)
    trials = 20000
    print(" n   KL(nats)  mean proxy  mean true  mean exploit")
    for n in (1, 2, 4, 8, 16, 64, 256):
        sp = st = se = 0.0
        for _ in range(trials // max(1, n // 8 + 1)):
            p, t, e = trial(n, rng)
            sp, st, se = sp + p, st + t, se + e
        m = trials // max(1, n // 8 + 1)
        kl_bon = math.log(n) - (n - 1) / n
        print(f"{n:>3}  {kl_bon:8.3f}  {sp / m:10.3f}  {st / m:9.3f}  {se / m:12.3f}")

    print("\nTrue quality keeps rising here because t is still part of the proxy.")
    print("Now make the exploit dominant: proxy = t + 1.5*e.")
    print(" n   mean proxy  mean true  mean exploit")
    for n in (1, 4, 16, 64, 256):
        m = 4000
        sp = st = se = 0.0
        for _ in range(m):
            best = (-1e9, 0.0, 0.0)
            for _ in range(n):
                t, e = rng.gauss(0, 1), rng.gauss(0, 1)
                proxy = t + 1.5 * e
                if proxy > best[0]:
                    best = (proxy, t, e)
            sp, st, se = sp + best[0], st + best[1], se + best[2]
        print(f"{n:>3}  {sp / m:10.3f}  {st / m:9.3f}  {se / m:12.3f}")


if __name__ == "__main__":
    main()
