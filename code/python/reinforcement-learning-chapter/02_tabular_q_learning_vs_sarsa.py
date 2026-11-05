"""Tabular Q-learning versus SARSA on the cliff-walking gridworld.

Standard library only. The grid is 4 rows x 12 columns. The agent starts at the
bottom-left, the goal is bottom-right, and the cells between them on the bottom
row are a cliff (reward -100, return to start). Every other step costs -1.

Q-learning (off-policy) learns the shortest path along the cliff edge.
SARSA (on-policy) learns the safer, longer path because its own epsilon-greedy
exploration sometimes falls off the cliff.
Run: python 02_tabular_q_learning_vs_sarsa.py
"""
import random

ROWS, COLS = 4, 12
START, GOAL = (3, 0), (3, 11)
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
ARROWS = "^v<>"


def env_step(state, a):
    r, c = state
    dr, dc = MOVES[a]
    r2 = min(max(r + dr, 0), ROWS - 1)
    c2 = min(max(c + dc, 0), COLS - 1)
    if r2 == 3 and 0 < c2 < 11:
        return START, -100.0, False  # fell off the cliff
    return (r2, c2), -1.0, (r2, c2) == GOAL


def eps_greedy(q, s, eps, rng):
    if rng.random() < eps:
        return rng.randrange(4)
    vals = q[s]
    best = max(vals)
    return rng.choice([i for i, x in enumerate(vals) if x == best])


def run(algo, episodes=2000, alpha=0.1, gamma=1.0, eps=0.1, seed=0):
    rng = random.Random(seed)
    q = {(r, c): [0.0] * 4 for r in range(ROWS) for c in range(COLS)}
    returns = []
    for _ in range(episodes):
        s, total = START, 0.0
        a = eps_greedy(q, s, eps, rng)
        for _t in range(500):
            s2, rew, done = env_step(s, a)
            total += rew
            a2 = eps_greedy(q, s2, eps, rng)
            if algo == "sarsa":
                target_next = q[s2][a2]
            else:  # q-learning: max over next actions
                target_next = max(q[s2])
            target = rew + (0.0 if done else gamma * target_next)
            q[s][a] += alpha * (target - q[s][a])
            s, a = s2, a2
            if done:
                break
        returns.append(total)
    return q, returns


def greedy_path(q):
    s, path = START, [START]
    for _ in range(50):
        vals = q[s]
        a = vals.index(max(vals))
        s, _, done = env_step(s, a)
        path.append(s)
        if done:
            break
    return path


def draw(path):
    grid = [["." for _ in range(COLS)] for _ in range(ROWS)]
    for c in range(1, 11):
        grid[3][c] = "C"
    for (r, c) in path:
        if (r, c) not in (START, GOAL):
            grid[r][c] = "*"
    grid[3][0], grid[3][11] = "S", "G"
    return "\n".join("  " + "".join(row) for row in grid)


def worked_update():
    # One Q-learning update by hand: alpha=0.5, gamma=1, Q(s,a)=0, r=-1,
    # max_a' Q(s',a') = -3  ->  target = -1 + (-3) = -4,  Q <- 0 + 0.5*(-4-0)
    q_sa, alpha, gamma, r, max_next = 0.0, 0.5, 1.0, -1.0, -3.0
    target = r + gamma * max_next
    print(f"worked update: target={target}, new Q={q_sa + alpha * (target - q_sa)}")


if __name__ == "__main__":
    worked_update()
    for algo in ("q_learning", "sarsa"):
        avg_online, finals = [], []
        for seed in range(20):
            q, rets = run(algo, seed=seed)
            avg_online.append(sum(rets[-100:]) / 100)
        q, rets = run(algo, seed=0)
        path = greedy_path(q)
        print(f"\n{algo}: mean online return, last 100 episodes, 20 seeds = "
              f"{sum(avg_online) / len(avg_online):.1f}")
        print(f"  greedy path length (seed 0) = {len(path) - 1} steps")
        print(draw(path))
