"""Check synthetic Google Cloud resource location compatibility."""


RESOURCES = {
    "global-vpc": {"scope": "global", "location": None},
    "regional-address": {"scope": "regional", "location": "us-central1"},
    "zonal-vm": {"scope": "zonal", "location": "us-central1-a"},
    "zonal-disk": {"scope": "zonal", "location": "us-central1-b"},
}


def can_attach(disk_name: str, vm_name: str) -> tuple[bool, str]:
    disk = RESOURCES[disk_name]
    vm = RESOURCES[vm_name]
    if disk["scope"] != "zonal" or vm["scope"] != "zonal":
        return False, "modeled attachment requires zonal resources"
    if disk["location"] != vm["location"]:
        return False, f"zone mismatch: {disk['location']} versus {vm['location']}"
    return True, "same-zone attachment assumption passes"


def main() -> None:
    print("global network scope:", RESOURCES["global-vpc"]["scope"])
    print("regional address scope:", RESOURCES["regional-address"]["location"])
    compatible, reason = can_attach("zonal-disk", "zonal-vm")
    print(f"disk attachment: {'allow' if compatible else 'reject'} ({reason})")


if __name__ == "__main__":
    main()