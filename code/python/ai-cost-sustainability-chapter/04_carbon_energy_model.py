"""Energy and carbon arithmetic for inference and batch work: energy per
request, Software Carbon Intensity (SCI) style rate, PUE, utilization and idle
power, carbon-aware scheduling, region choice, and training amortization.

Standard library only. Every constant is an ILLUSTRATIVE assumption with a
wide uncertainty band; measure your own hardware and use your grid data.

Run: python 04_carbon_energy_model.py
"""


def energy_per_request():
    print("== Energy per request from GPU power and throughput (illustrative) ==")
    gpu_busy_w, gpu_idle_w = 700.0, 120.0     # per accelerator
    gpus, host_w = 8, 900.0                    # one node
    pue = 1.2
    tokens_s_busy = 9000.0                     # node output tokens/s at saturation
    out_tokens = 350
    for util in (0.15, 0.40, 0.80):
        node_w = gpus * (gpu_idle_w + util * (gpu_busy_w - gpu_idle_w)) + host_w
        tokens_s = tokens_s_busy * util
        j_per_token = node_w / tokens_s
        wh_req = j_per_token * out_tokens / 3600 * pue
        print(f"utilization {util:>4.0%}: node {node_w:6.0f} W, "
              f"{j_per_token:6.2f} J/token, {wh_req:6.3f} Wh/request (with PUE {pue})")


def sci_rate():
    print("\n== SCI-style rate per request ==")
    wh_req = 0.12                     # 40 percent utilization case above
    kwh = wh_req / 1000
    for region, intensity in (("low-carbon grid", 50.0), ("average grid", 400.0),
                              ("coal-heavy grid", 700.0)):   # gCO2e/kWh
        e_term = kwh * intensity
        # embodied: node 3,000 kgCO2e over 4 years at 40% share-time -> per request
        node_kg = 3000.0
        life_s = 4 * 365 * 24 * 3600
        req_per_s = 9000 * 0.4 / 350
        m_term = node_kg * 1000 / (life_s * req_per_s)       # g per request
        print(f"{region:<16} I={intensity:>5.0f} g/kWh  E*I={e_term * 1000:7.3f} mg  "
              f"M={m_term * 1000:7.3f} mg  SCI={(e_term + m_term) * 1000:7.3f} mgCO2e/request")


def carbon_aware_batch():
    print("\n== Carbon-aware scheduling of a deferrable batch (illustrative) ==")
    # 24 hourly grid intensities, gCO2e/kWh, a solar-heavy grid
    hourly = [420, 410, 405, 400, 400, 410, 380, 330, 260, 200, 160, 140,
              130, 135, 150, 200, 290, 380, 440, 460, 450, 440, 430, 425]
    job_kwh = 1800.0       # whole nightly job
    hours_needed = 6
    start_naive = 0         # runs 00:00-06:00
    naive = sum(hourly[(start_naive + i) % 24] for i in range(hours_needed)) / hours_needed
    best, best_start = None, None
    for s in range(24):
        a = sum(hourly[(s + i) % 24] for i in range(hours_needed)) / hours_needed
        if best is None or a < best:
            best, best_start = a, s
    print(f"naive window 00:00 average {naive:.0f} g/kWh -> {job_kwh * naive / 1000:.0f} kgCO2e")
    print(f"best window {best_start:02d}:00 average {best:.0f} g/kWh -> {job_kwh * best / 1000:.0f} kgCO2e")
    print(f"reduction {100 * (1 - best / naive):.1f}%")
    # Spot/short-window variant: pause when above threshold
    thr = 250
    picked = sorted(range(24), key=lambda h: hourly[h])[:hours_needed]
    avg = sum(hourly[h] for h in picked) / hours_needed
    print(f"cherry-picking the {hours_needed} cleanest hours (pausable job): {avg:.0f} g/kWh, "
          f"{100 * (1 - avg / naive):.1f}% below naive; hours {sorted(picked)}")
    print(f"hours below {thr} g/kWh: {sum(1 for h in hourly if h < thr)}")
    # Deadline-constrained: pages arrive until 18:00, results due 14:00 next day.
    # Hours are indexed 0-23 on the next calendar day; a window must end by 14.
    cands = list(range(18, 24)) + list(range(0, 9))
    scored = []
    for s in cands:
        avg_s = sum(hourly[(s + i) % 24] for i in range(hours_needed)) / hours_needed
        scored.append((avg_s, s))
    avg_c, s_c = min(scored)
    kg_c = job_kwh * avg_c / 1000
    print(f"deadline 14:00: best contiguous start {s_c:02d}:00, avg {avg_c:.1f} g/kWh, "
          f"{kg_c:.0f} kgCO2e ({100 * (1 - avg_c / naive):.1f}% below naive)")
    saved = job_kwh * naive / 1000 - kg_c
    print(f"saving per night {saved:.0f} kg; per 30 nights {saved * 30 / 1000:.1f} t; "
          f"per year {saved * 365 / 1000:.0f} t")


def training_amortization():
    print("\n== Training amortized over inference (illustrative) ==")
    train_mwh = 1200.0          # energy of a hypothetical training run, MWh
    intensity = 400.0           # g/kWh
    train_t = train_mwh * 1000 * intensity / 1e6      # tonnes CO2e
    print(f"training: {train_mwh:.0f} MWh x {intensity:.0f} g/kWh = {train_t:.0f} tCO2e")
    wh_req = 0.12
    for reqs_per_day in (1e7, 1e8, 1e9):
        daily_kwh = reqs_per_day * wh_req / 1000
        days = 365
        inf_t = daily_kwh * days * intensity / 1e6
        print(f"{reqs_per_day:>9.0e} req/day: inference {daily_kwh:>8.0f} kWh/day, "
              f"{inf_t:>7.0f} tCO2e/yr vs training {train_t:.0f} tCO2e "
              f"(ratio {inf_t / train_t:5.2f})")


def region_choice():
    print("\n== Region selection trade-off (illustrative) ==")
    regions = [("Region A (nearby, avg grid)", 400, 20, 1.00),
               ("Region B (low-carbon)", 60, 95, 0.97),
               ("Region C (cheap, coal-heavy)", 650, 140, 0.88)]
    kwh_month = 52000.0
    for name, g, rtt_ms, price in regions:
        print(f"{name:<30} {kwh_month * g / 1e6:6.1f} tCO2e/mo  "
              f"extra RTT {rtt_ms:>4} ms  relative price {price:.2f}")


if __name__ == "__main__":
    energy_per_request()
    sci_rate()
    carbon_aware_batch()
    training_amortization()
    region_choice()
