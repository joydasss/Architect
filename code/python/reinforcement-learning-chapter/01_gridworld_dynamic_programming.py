"""Dynamic programming on a tiny gridworld (standard library only).

Part 1: 2x2 grid, goal in the bottom-right cell, reward -1 per step, gamma = 1.
        Iterative policy evaluation of the equiprobable random policy, then one
        greedy improvement step. The exact values are A=-8, B=-6, C=-6, G=0.
Part 2: value iteration on a 4x4 grid with gamma = 0.9 and a pit.
Run: python 01_gridworld_dynamic_programming.py
"""

ACTIONS = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}


def step(state, action, n, goal):
    """Deterministic move. Walls leave the agent in place."""
    if state == goal:
        return state
    r, c = state
    dr, dc = ACTIONS[action]
    nr, nc = r + dr, c + dc
    if 0 <= nr < n and 0 <= nc < n:
        return (nr, nc)
    return state


def evaluate_random_policy(n, goal, gamma, sweeps):
    states = [(r, c) for r in range(n) for c in range(n)]
    v = {s: 0.0 for s in states}
    history = [dict(v)]
    for _ in range(sweeps):
        new_v = dict(v)  # synchronous (Jacobi) sweep
        for s in states:
            if s == goal:
                continue
            total = 0.0
            for a in ACTIONS:
                s2 = step(s, a, n, goal)
                total += 0.25 * (-1.0 + gamma * v[s2])
            new_v[s] = total
        v = new_v
        history.append(dict(v))
    return v, history


def greedy_actions(v, n, goal, gamma):
    policy = {}
    for r in range(n):
        for c in range(n):
            s = (r, c)
            if s == goal:
                continue
            q = {a: -1.0 + gamma * v[step(s, a, n, goal)] for a in ACTIONS}
            best = max(q.values())
            policy[s] = "".join(a for a in "UDLR" if abs(q[a] - best) < 1e-9)
    return policy


def part1():
    n, goal = 2, (1, 1)
    names = {(0, 0): "A", (0, 1): "B", (1, 0): "C", (1, 1): "G"}
    v, hist = evaluate_random_policy(n, goal, 1.0, 200)
    print("Part 1: 2x2 grid, random policy, gamma=1")
    for k in (0, 1, 2, 3, 10):
        row = ", ".join(f"{names[s]}={hist[k][s]:.3f}" for s in sorted(hist[k]))
        print(f"  sweep {k:>2}: {row}")
    print("  converged:", ", ".join(f"{names[s]}={v[s]:.3f}" for s in sorted(v)))
    pol = greedy_actions(v, n, goal, 1.0)
    print("  greedy actions after improvement:",
          {names[s]: a for s, a in pol.items()})


def value_iteration(n, goal, pit, gamma, tol=1e-9):
    states = [(r, c) for r in range(n) for c in range(n)]
    v = {s: 0.0 for s in states}
    sweeps = 0
    while True:
        delta = 0.0
        for s in states:
            if s == goal or s == pit:
                continue
            best = float("-inf")
            for a in ACTIONS:
                s2 = step(s, a, n, goal)
                reward = 10.0 if s2 == goal else (-10.0 if s2 == pit else -1.0)
                terminal = s2 == goal or s2 == pit
                best = max(best, reward + (0.0 if terminal else gamma * v[s2]))
            delta = max(delta, abs(best - v[s]))
            v[s] = best
        sweeps += 1
        if delta < tol:
            return v, sweeps


def part2():
    n, goal, pit, gamma = 4, (3, 3), (1, 1), 0.9
    v, sweeps = value_iteration(n, goal, pit, gamma)
    print("\nPart 2: value iteration, 4x4, goal=(3,3) +10, pit=(1,1) -10,"
          " step -1, gamma=0.9")
    print(f"  converged in {sweeps} in-place sweeps")
    for r in range(n):
        print("  " + " ".join(f"{v[(r, c)]:7.3f}" for c in range(n)))


if __name__ == "__main__":
    part1()
    part2()
