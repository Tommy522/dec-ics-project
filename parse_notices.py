#!/usr/bin/env python3
import sys
from datetime import datetime, timezone

def parse_zeek_log(path):
    fields = []
    rows = []
    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("#fields"):
                fields = line.split("\t")[1:]
            elif line.startswith("#"):
                continue
            elif not line.strip():
                continue
            else:
                rows.append(line.split("\t"))
    return fields, rows

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "notice.log"
    fields, rows = parse_zeek_log(path)
    idx = {f: i for i, f in enumerate(fields)}

    print(f"{'TIME':<20} {'SOURCE':<22} {'TARGET':<22} {'ALERT TYPE':<35} MESSAGE")
    print("-" * 150)
    for row in rows:
        ts = float(row[idx['ts']])
        time_str = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
        src = f"{row[idx['id.orig_h']]}:{row[idx['id.orig_p']]}"
        dst = f"{row[idx['id.resp_h']]}:{row[idx['id.resp_p']]}"
        note = row[idx['note']]
        msg = row[idx['msg']]
        print(f"{time_str:<20} {src:<22} {dst:<22} {note:<35} {msg}")

if __name__ == "__main__":
    main()
