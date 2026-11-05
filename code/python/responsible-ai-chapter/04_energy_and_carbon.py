"""Energy and carbon accounting for training and inference (standard library only).

Energy (kWh) = accelerators x average power (kW) x hours x PUE.
Emissions (kg CO2e) = energy x grid intensity (kg CO2e per kWh).
All inputs are illustrative. Replace them with measured power draw, your
facility or cloud provider's PUE, and the location- or market-based grid
intensity for the region and hour you actually ran in.

Run: python 04_energy_and_carbon.py
"""


def energy_kwh(devices, avg_kw, hours, pue):
    return devices * avg_kw * hours * pue


def main():
    print("== Fine-tuning job ==")
    e = energy_kwh(devices=8, avg_kw=0.55, hours=36, pue=1.2)
    print(f"energy: 8 x 0.55 kW x 36 h x 1.2 = {e:.1f} kWh")
    for region, ci in (("low-carbon grid", 0.05), ("average grid", 0.40), ("coal-heavy grid", 0.75)):
        print(f"  {region:<16} {ci:.2f} kg/kWh -> {e * ci:7.1f} kg CO2e")

    print("\n== Inference service ==")
    requests_per_day = 2_000_000
    wh_per_request = 0.9  # measured at the wall for a mid-size model, illustrative
    pue = 1.2
    day_kwh = requests_per_day * wh_per_request / 1000 * pue
    year_kwh = day_kwh * 365
    print(f"daily energy: {requests_per_day:,} x {wh_per_request} Wh x {pue} = {day_kwh:,.0f} kWh")
    print(f"yearly energy: {year_kwh:,.0f} kWh")
    ci = 0.40
    print(f"yearly emissions at {ci} kg/kWh: {year_kwh * ci / 1000:,.1f} tonnes CO2e")

    print("\n== Training versus inference break-even ==")
    train_kwh = 120_000.0  # illustrative one-off training energy
    days = train_kwh / day_kwh
    print(f"inference matches the training energy after {days:.0f} days of serving")

    print("\n== Effect of a 40% per-request energy reduction (distillation, batching) ==")
    saved = year_kwh * 0.40
    print(f"saved: {saved:,.0f} kWh/year, {saved * ci / 1000:,.1f} tonnes CO2e/year")


if __name__ == "__main__":
    main()
