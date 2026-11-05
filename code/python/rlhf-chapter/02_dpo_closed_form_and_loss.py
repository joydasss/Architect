"""KL-regularized optimum, implicit reward, and the DPO loss on a toy policy.

Standard library only. A "prompt" has four possible responses with a reference
probability and a reward. We compute:
1. The closed-form optimum pi*(y) = pi_ref(y) exp(r(y)/beta) / Z for several beta.
2. The objective value E[r] - beta * KL for pi_ref, pi*, and a greedy policy.
3. A worked DPO loss for one preference pair, with the implicit reward margin.
"""

import math

RESPONSES = ["terse", "helpful", "verbose", "unsafe"]
PI_REF = [0.30, 0.40, 0.25, 0.05]
REWARD = [0.2, 1.0, 1.3, 1.6]  # proxy reward model prefers unsafe and verbose


def kl(p, q):
    return sum(pi * math.log(pi / qi) for pi, qi in zip(p, q) if pi > 0)


def optimum(beta):
    w = [p * math.exp(r / beta) for p, r in zip(PI_REF, REWARD)]
    z = sum(w)
    return [x / z for x in w]


def objective(pi, beta):
    er = sum(p * r for p, r in zip(pi, REWARD))
    return er, kl(pi, PI_REF), er - beta * kl(pi, PI_REF)


def sigmoid(z):
    return 1.0 / (1.0 + math.exp(-z))


def main():
    print("== Closed-form optimum pi* for several beta ==")
    print("beta   " + "  ".join(f"{n:>8}" for n in RESPONSES) + "    E[r]     KL")
    for beta in (2.0, 1.0, 0.5, 0.2, 0.1):
        pi = optimum(beta)
        er, k, _ = objective(pi, beta)
        print(f"{beta:<5}  " + "  ".join(f"{p:8.4f}" for p in pi) + f"  {er:6.3f}  {k:6.3f}")

    beta = 0.5
    pi_star = optimum(beta)
    greedy = [0.0, 0.0, 0.0, 1.0]
    print("\n== Objective E[r] - beta*KL at beta=0.5 ==")
    for name, pi in (("pi_ref", PI_REF), ("pi_star", pi_star)):
        er, k, obj = objective(pi, beta)
        print(f"{name:8} E[r]={er:.3f} KL={k:.3f} objective={obj:.3f}")
    er = sum(p * r for p, r in zip(greedy, REWARD))
    k = kl(greedy, PI_REF)
    print(f"greedy   E[r]={er:.3f} KL={k:.3f} objective={er - beta * k:.3f}")

    # Implicit reward: beta * log(pi*/pi_ref) equals r - beta*log Z.
    print("\n== Implicit reward beta*log(pi*/pi_ref) vs r ==")
    z = sum(p * math.exp(r / beta) for p, r in zip(PI_REF, REWARD))
    for n, p, ps, r in zip(RESPONSES, PI_REF, pi_star, REWARD):
        ir = beta * math.log(ps / p)
        print(f"{n:8} implicit={ir:7.4f}  r - beta*logZ={r - beta * math.log(z):7.4f}")

    # Worked DPO loss: chosen = helpful, rejected = terse, policy not yet optimal.
    pol = {"helpful": 0.46, "terse": 0.26}
    ref = {"helpful": 0.40, "terse": 0.30}
    margin = beta * (math.log(pol["helpful"] / ref["helpful"])
                     - math.log(pol["terse"] / ref["terse"]))
    loss = -math.log(sigmoid(margin))
    print("\n== Worked DPO loss (beta=0.5) ==")
    print(f"log ratio chosen   = {math.log(pol['helpful'] / ref['helpful']):.4f}")
    print(f"log ratio rejected = {math.log(pol['terse'] / ref['terse']):.4f}")
    print(f"scaled margin      = {margin:.4f}")
    print(f"P(chosen) implied  = {sigmoid(margin):.4f}")
    print(f"DPO loss           = {loss:.4f}")
    print(f"gradient weight sigma(-margin) = {sigmoid(-margin):.4f}")


if __name__ == "__main__":
    main()
