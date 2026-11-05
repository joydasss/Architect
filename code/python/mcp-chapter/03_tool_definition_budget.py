"""Worked numbers: context tokens consumed by MCP tool definitions.

Token counts use the rough heuristic tokens ~= characters / 4 for English and
JSON. It is an ILLUSTRATIVE estimate; measure with your model's tokenizer.
Standard library only.
"""
import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("srv", os.path.join(HERE, "01_mini_mcp_server.py"))
srv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(srv)


def est_tokens(obj):
    return round(len(json.dumps(obj, separators=(",", ":"))) / 4)


def main():
    per_tool = [est_tokens(t) for t in srv.TOOLS]
    print("Measured on the two teaching tools (chars/4):", per_tool)
    avg_small = sum(per_tool) / len(per_tool)
    print(f"Average of those two: {avg_small:.0f} tokens per tool")

    # Illustrative sizing: real-world tools often carry longer descriptions and
    # many parameters. We scale three scenarios.
    scenarios = [
        ("Lean server set", 3, 8, 150),
        ("Typical developer setup", 6, 15, 250),
        ("Enterprise catalogue", 20, 25, 350),
    ]
    window = 200_000
    print()
    print(f"{'scenario':26s}{'servers':>8s}{'tools':>7s}{'tok/tool':>9s}{'total':>9s}{'% of 200k':>11s}")
    for name, servers, tools_each, tok in scenarios:
        n = servers * tools_each
        total = n * tok
        print(f"{name:26s}{servers:8d}{n:7d}{tok:9d}{total:9d}{100 * total / window:10.1f}%")

    # Cost of resending definitions every model call (no prompt caching).
    n, tok, calls, price = 150, 250, 40, 3.00  # tools, tok/tool, model calls per task, USD per 1M input tokens
    total = n * tok
    per_task = total * calls
    print()
    print(f"Resend cost: {n} tools x {tok} tokens = {total} tokens per call")
    print(f"{calls} calls per task -> {per_task} input tokens -> ${per_task * price / 1e6:.2f} per task at ${price:.2f}/1M (illustrative price)")
    cached = per_task * 0.1
    print(f"If a cache read costs 10% of the base price: ${cached * price / 1e6:.2f} per task")

    # Narrowing: expose only 12 tools chosen per task.
    narrow = 12 * tok
    print()
    print(f"Narrowed to 12 relevant tools: {narrow} tokens per call, {narrow * calls} per task, ${narrow * calls * price / 1e6:.2f}")
    print(f"Reduction vs full set: {100 * (1 - narrow / total):.0f}%")


if __name__ == "__main__":
    main()
