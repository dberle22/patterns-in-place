"""IRS SOI county migration totals, 2018-2022 (destination tax years), for every US county.

Why: silver.irs_migration_flows holds county *pairs* only, and IRS suppresses pairs under 20 returns. Those small,
scattered flows are mostly moves to and from other states, so pair sums undercount them badly (Albany's metro: about
1,800 people a year in from other states on pairs vs 10,600 on the IRS totals). The IRS files also publish each
county's uncapped totals ("Total Migration-US", "-Same State", "-Different State"), which this extract keeps.

Run: python data/build_irs_county_totals.py [download_dir]
  Reads countyinflow{yy}{yy}.csv / countyoutflow{yy}{yy}.csv from download_dir (downloads any that are missing from
  https://www.irs.gov/pub/irs-soi/) and writes data/irs_county_totals_2018_2022.csv: one row per county, direction
  ('in', 'out') and bucket ('us', 'same_state', 'different_state'), with people (exemptions) and households (returns)
  summed over the five years. Suppressed cells (-1) count as zero.
"""
import sys
import urllib.request
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
CODES = ["1718", "1819", "1920", "2021", "2122"]  # destination tax years 2018-2022
BUCKETS = {"Total Migration-US": "us", "Total Migration-Same State": "same_state", "Total Migration-Different State": "different_state"}


def main(download_dir: Path) -> None:
    download_dir.mkdir(parents=True, exist_ok=True)
    parts = []
    for code in CODES:
        for kind, direction in [("inflow", "in"), ("outflow", "out")]:
            path = download_dir / f"county{kind}{code}.csv"
            if not path.exists():
                urllib.request.urlretrieve(f"https://www.irs.gov/pub/irs-soi/county{kind}{code}.csv", path)
            d = pd.read_csv(path, encoding="latin-1")
            # Inflow files: y2 is the county, y1 the other end. Outflow files: the reverse.
            me, other_name = (("y2_statefips", "y2_countyfips"), "y1_countyname") if kind == "inflow" else (("y1_statefips", "y1_countyfips"), "y2_countyname")
            # Summary rows are named "<County> Total Migration-US" and so on.
            label = d[other_name].astype(str).str.strip().str.extract(r"(Total Migration-(?:US|Same State|Different State))$")[0]
            d = d.loc[d[me[1]] != 0].assign(bucket=label.map(BUCKETS)).dropna(subset=["bucket"])
            parts.append(pd.DataFrame({
                "county_geoid": d[me[0]].astype(int).map("{:02d}".format) + d[me[1]].astype(int).map("{:03d}".format),
                "direction": direction, "bucket": d["bucket"], "year": 2000 + int(code[2:]),
                "people": d["n2"].clip(lower=0), "households": d["n1"].clip(lower=0),
            }))
    out = (pd.concat(parts).groupby(["county_geoid", "direction", "bucket"], as_index=False)[["people", "households"]].sum()
           .assign(years="2018-2022"))
    out.to_csv(HERE / "irs_county_totals_2018_2022.csv", index=False)
    print(len(out), "rows;", out["county_geoid"].nunique(), "counties")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "irs_raw")
