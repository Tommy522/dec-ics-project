"""
extract_features.py

Builds a clean numeric feature table from:
  1. baseline_log.csv  (continuous "normal" poller data: timestamp,value)
  2. a Zeek modbus log (e.g. modbus_detailed.log) for labeled attack traffic

Usage:
    python3 extract_features.py baseline baseline_log.csv
    python3 extract_features.py attack modbus_detailed.log attack_label
"""

import sys
import csv
import pandas as pd


def extract_baseline_features(csv_path, baseline_value=1500):
    rows = []
    with open(csv_path) as f:
        reader = csv.reader(f)
        prev_ts = None
        for ts_str, value_str in reader:
            ts = pd.to_datetime(ts_str)
            try:
                value = int(value_str)
            except ValueError:
                continue  # skip ERROR rows from poller outages
            inter_arrival = (ts - prev_ts).total_seconds() if prev_ts else None
            rows.append({
                "timestamp": ts,
                "value": value,
                "delta_from_baseline": value - baseline_value,
                "inter_arrival": inter_arrival,
            })
            prev_ts = ts
    return pd.DataFrame(rows)


def read_zeek_log(path):
    """Generic Zeek TSV reader: uses the #fields header line, so it adapts
    to whatever columns are actually present instead of assuming a fixed schema."""
    with open(path) as f:
        lines = f.readlines()

    fields = None
    data_lines = []
    for line in lines:
        if line.startswith("#fields"):
            fields = line.rstrip("\n").split("\t")[1:]
        elif not line.startswith("#"):
            data_lines.append(line.rstrip("\n"))

    if fields is None:
        raise ValueError(f"No #fields header found in {path} — is this a Zeek log?")

    rows = []
    for line in data_lines:
        values = line.split("\t")
        rows.append(dict(zip(fields, values)))
    return pd.DataFrame(rows), fields


def _first_value(vector_str):
    """Zeek vector fields are comma-separated ('-' = unset/empty). Return the
    first register value as an int, or None if there isn't one."""
    if vector_str in (None, "-", ""):
        return None
    first = vector_str.split(",")[0]
    try:
        return int(first)
    except ValueError:
        return None


def extract_modbus_features(log_path, baseline_value=1500):
    df, fields = read_zeek_log(log_path)
    print(f"Columns found in {log_path}: {fields}")

    out = pd.DataFrame()
    out["timestamp"] = pd.to_datetime(df["ts"].astype(float), unit="s") if "ts" in df else None
    out["source"] = df["id.orig_h"] if "id.orig_h" in df else None
    out["function_code"] = df["func"] if "func" in df else None
    out["address"] = pd.to_numeric(df["address"], errors="coerce") if "address" in df else None
    out["quantity"] = pd.to_numeric(df["quantity"], errors="coerce") if "quantity" in df else None
    out["exception_code"] = df["exception_code"] if "exception_code" in df else None

    # value: prefer request_values (what the client sent), fall back to response_values (what the server returned)
    if "request_values" in df:
        out["value"] = df["request_values"].apply(_first_value)
    if "value" not in out or out["value"].isna().all():
        if "response_values" in df:
            out["value"] = df["response_values"].apply(_first_value)

    if "value" in out:
        out["delta_from_baseline"] = out["value"] - baseline_value

    # rolling request rate per source: count of requests from the same source in the trailing 1 second
    out = out.sort_values("timestamp").reset_index(drop=True)
    rates = []
    for i, row in out.iterrows():
        window_start = row["timestamp"] - pd.Timedelta(seconds=1)
        mask = (out["source"] == row["source"]) & (out["timestamp"] > window_start) & (out["timestamp"] <= row["timestamp"])
        rates.append(mask.sum())
    out["request_rate_1s"] = rates

    return out


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    mode = sys.argv[1]
    path = sys.argv[2]

    if mode == "baseline":
        df = extract_baseline_features(path)
        out_path = "baseline_features.csv"
    elif mode == "attack":
        label = sys.argv[3] if len(sys.argv) > 3 else "attack"
        df = extract_modbus_features(path)
        out_path = f"{label}_features.csv"
    else:
        print("mode must be 'baseline' or 'attack'")
        sys.exit(1)

    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} rows to {out_path}")
