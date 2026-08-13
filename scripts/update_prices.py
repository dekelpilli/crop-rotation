#!/usr/bin/env python3
"""Fetches current lifeforce-per-divine rates from poe.ninja for every cached
league and writes prices.json. Run hourly by .github/workflows/update-prices.yml;
can also be run locally (`python3 scripts/update_prices.py`) to refresh the file
by hand.
"""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

NINJA_URL = "https://poe.ninja/poe1/api/economy/exchange/current/overview"
LEAGUES = ["Allflame", "Hardcore Allflame", "Standard", "Hardcore"]
COLOURS = {"primal": "primal-lifeforce", "vivid": "vivid-lifeforce", "wild": "wild-lifeforce"}
OUT_PATH = "prices.json"


def fetch_league(league):
    target = f"{NINJA_URL}?league={urllib.parse.quote(league)}&type=Currency"
    req = urllib.request.Request(target, headers={"User-Agent": "crop-rotation-tree-calc/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read())

    by_id = {line["id"]: line for line in data.get("lines", [])}
    divine_line = by_id.get("divine")
    if not divine_line or not isinstance(divine_line.get("primaryValue"), (int, float)):
        raise ValueError("divine rate not found")
    chaos_per_divine = divine_line["primaryValue"]

    rates = {}
    for colour, ninja_id in COLOURS.items():
        line = by_id.get(ninja_id)
        if not line or not isinstance(line.get("primaryValue"), (int, float)) or line["primaryValue"] <= 0:
            raise ValueError(f"{ninja_id} rate not found")
        rates[colour] = round(chaos_per_divine / line["primaryValue"])

    rates["chaosPerDivine"] = chaos_per_divine
    return rates


def main():
    leagues = {}
    failures = []
    for league in LEAGUES:
        try:
            leagues[league] = fetch_league(league)
        except (urllib.error.URLError, ValueError, json.JSONDecodeError) as e:
            failures.append(f"{league}: {e}")

    if not leagues:
        print("Failed to fetch any league:\n" + "\n".join(failures), file=sys.stderr)
        sys.exit(1)

    if failures:
        print("Warning, some leagues failed:\n" + "\n".join(failures), file=sys.stderr)

    out = {
        "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "leagues": leagues,
    }
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print(f"Wrote {OUT_PATH} with {len(leagues)}/{len(LEAGUES)} leagues.")


if __name__ == "__main__":
    main()
