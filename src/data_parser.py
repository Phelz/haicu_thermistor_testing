# """
# data_parser.py
# Parses the thermistor log file into a pandas DataFrame.

# Each line format:
#   YYYY-MM-DD HH:MM:SS 0 <val> 1 <val> ... 15 <val>
# """

# import pandas as pd
# from pathlib import Path

# DATA_FILE = Path("example_data.txt")  # adjust path as needed


# def parse_data(filepath: Path = DATA_FILE) -> pd.DataFrame:
#     """
#     Parse the log file and return a tidy DataFrame with columns:
#       timestamp (datetime), channel (int 0-15), value (int 0-1023)
#     """
#     records = []
#     with open(filepath, "r") as f:
#         for line in f:
#             line = line.strip()
#             if not line:
#                 continue
#             tokens = line.split()
#             # tokens[0] = date, tokens[1] = time, then pairs of (index, value)
#             ts = pd.Timestamp(f"{tokens[0]} {tokens[1]}")
#             pairs = tokens[2:]
#             for i in range(0, len(pairs), 2):
#                 channel = int(pairs[i])
#                 value = int(pairs[i + 1])
#                 records.append({"timestamp": ts, "channel": channel, "value": value})
#     return pd.DataFrame(records)


"""
data_parser.py
Parses all thermistor log files from the data directory structure:
  data/<day>/<hour>.txt  (e.g. data/2026-04-20/00.txt ... data/2026-04-20/23.txt)

Each line format:
  YYYY-MM-DD HH:MM:SS 0 <val> 1 <val> ... 15 <val>
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path("../data")


def parse_file(filepath: Path) -> pd.DataFrame:
    """Parse a single hour file into a tidy DataFrame."""
    records = []
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            tokens = line.split()
            if len(tokens) < 34:  # 2 (date+time) + 16*2 (index+value)
                continue
            ts = pd.Timestamp(f"{tokens[0]} {tokens[1]}")
            pairs = tokens[2:]
            for i in range(0, len(pairs), 2):
                channel = int(pairs[i])
                value = int(pairs[i + 1])
                records.append({"timestamp": ts, "channel": channel, "value": value})
    return pd.DataFrame(records, columns=["timestamp", "channel", "value"])


def parse_all(data_dir: Path = DATA_DIR) -> pd.DataFrame:
    """
    Walk all day/hour files under data_dir and return a single sorted DataFrame.
    Expected structure: data_dir/<YYYY-MM-DD>/<HH>.txt
    """
    frames = []
    if not data_dir.exists():
        return pd.DataFrame(columns=["timestamp", "channel", "value"])

    for day_dir in sorted(data_dir.iterdir()):
        if not day_dir.is_dir():
            continue
        for hour_file in sorted(day_dir.glob("*.txt")):
            try:
                df = parse_file(hour_file)
                if not df.empty:
                    frames.append(df)
            except Exception as e:
                print(f"[data_parser] Skipping {hour_file}: {e}")

    if not frames:
        return pd.DataFrame(columns=["timestamp", "channel", "value"])

    combined = pd.concat(frames, ignore_index=True)
    combined.sort_values("timestamp", inplace=True)
    combined.reset_index(drop=True, inplace=True)
    return combined


# Downsampling options: display label -> pandas resample offset alias (None = raw)
RESAMPLE_OPTIONS = {
    "None (10 s)": None,
    "1 min":       "1min",
    "5 min":       "5min",
    "10 min":      "10min",
}


def downsample(df: pd.DataFrame, rule: str | None) -> pd.DataFrame:
    """
    Resample the DataFrame to the given pandas rule (e.g. '1min').
    Values within each bin are averaged and rounded to the nearest integer.
    Returns the original DataFrame unchanged when rule is None.
    """
    if rule is None or df.empty:
        return df

    resampled_frames = []
    for ch in sorted(df["channel"].unique()):
        sub = df[df["channel"] == ch].set_index("timestamp")["value"]
        r = (
            sub.resample(rule)
               .mean()
               .dropna()
               .round()
               .astype(int)
               .reset_index()
        )
        r["channel"] = ch
        resampled_frames.append(r)

    if not resampled_frames:
        return df

    out = pd.concat(resampled_frames, ignore_index=True)
    out.sort_values(["timestamp", "channel"], inplace=True)
    out.reset_index(drop=True, inplace=True)
    return out
