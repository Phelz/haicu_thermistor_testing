# # """
# # data_parser.py
# # Parses the thermistor log file into a pandas DataFrame.

# # Each line format:
# #   YYYY-MM-DD HH:MM:SS 0 <val> 1 <val> ... 15 <val>
# # """

# # import pandas as pd
# # from pathlib import Path

# # DATA_FILE = Path("example_data.txt")  # adjust path as needed


# # def parse_data(filepath: Path = DATA_FILE) -> pd.DataFrame:
# #     """
# #     Parse the log file and return a tidy DataFrame with columns:
# #       timestamp (datetime), channel (int 0-15), value (int 0-1023)
# #     """
# #     records = []
# #     with open(filepath, "r") as f:
# #         for line in f:
# #             line = line.strip()
# #             if not line:
# #                 continue
# #             tokens = line.split()
# #             # tokens[0] = date, tokens[1] = time, then pairs of (index, value)
# #             ts = pd.Timestamp(f"{tokens[0]} {tokens[1]}")
# #             pairs = tokens[2:]
# #             for i in range(0, len(pairs), 2):
# #                 channel = int(pairs[i])
# #                 value = int(pairs[i + 1])
# #                 records.append({"timestamp": ts, "channel": channel, "value": value})
# #     return pd.DataFrame(records)


# """
# data_parser.py
# Parses all thermistor log files from the data directory structure:
#   data/<day>/<hour>.txt  (e.g. data/2026-04-20/00.txt ... data/2026-04-20/23.txt)

# Each line format:
#   YYYY-MM-DD HH:MM:SS 0 <val> 1 <val> ... 15 <val>
# """

# import pandas as pd
# from pathlib import Path

# DATA_DIR = Path("../data")


# def parse_file(filepath: Path) -> pd.DataFrame:
#     """Parse a single hour file into a tidy DataFrame."""
#     records = []
#     with open(filepath, "r") as f:
#         for line in f:
#             line = line.strip()
#             if not line:
#                 continue
#             tokens = line.split()
#             if len(tokens) < 34:  # 2 (date+time) + 16*2 (index+value)
#                 continue
#             ts = pd.Timestamp(f"{tokens[0]} {tokens[1]}")
#             pairs = tokens[2:]
#             for i in range(0, len(pairs), 2):
#                 channel = int(pairs[i])
#                 value = int(pairs[i + 1])
#                 records.append({"timestamp": ts, "channel": channel, "value": value})
#     return pd.DataFrame(records, columns=["timestamp", "channel", "value"])


# def parse_all(data_dir: Path = DATA_DIR) -> pd.DataFrame:
#     """
#     Walk all day/hour files under data_dir and return a single sorted DataFrame.
#     Expected structure: data_dir/<YYYY-MM-DD>/<HH>.txt
#     """
#     frames = []
#     if not data_dir.exists():
#         return pd.DataFrame(columns=["timestamp", "channel", "value"])

#     for day_dir in sorted(data_dir.iterdir()):
#         if not day_dir.is_dir():
#             continue
#         for hour_file in sorted(day_dir.glob("*.txt")):
#             try:
#                 df = parse_file(hour_file)
#                 if not df.empty:
#                     frames.append(df)
#             except Exception as e:
#                 print(f"[data_parser] Skipping {hour_file}: {e}")

#     if not frames:
#         return pd.DataFrame(columns=["timestamp", "channel", "value"])

#     combined = pd.concat(frames, ignore_index=True)
#     combined.sort_values("timestamp", inplace=True)
#     combined.reset_index(drop=True, inplace=True)
#     return combined


# # Downsampling options: display label -> pandas resample offset alias (None = raw)
# RESAMPLE_OPTIONS = {
#     "None (10 s)": None,
#     "1 min":       "1min",
#     "5 min":       "5min",
#     "10 min":      "10min",
# }


# def downsample(df: pd.DataFrame, rule: str | None) -> pd.DataFrame:
#     """
#     Resample the DataFrame to the given pandas rule (e.g. '1min').
#     Values within each bin are averaged and rounded to the nearest integer.
#     Returns the original DataFrame unchanged when rule is None.
#     """
#     if rule is None or df.empty:
#         return df

#     resampled_frames = []
#     for ch in sorted(df["channel"].unique()):
#         sub = df[df["channel"] == ch].set_index("timestamp")["value"]
#         r = (
#             sub.resample(rule)
#                .mean()
#                .dropna()
#                .round()
#                .astype(int)
#                .reset_index()
#         )
#         r["channel"] = ch
#         resampled_frames.append(r)

#     if not resampled_frames:
#         return df

#     out = pd.concat(resampled_frames, ignore_index=True)
#     out.sort_values(["timestamp", "channel"], inplace=True)
#     out.reset_index(drop=True, inplace=True)
#     return out


"""
data_parser.py
Parses all thermistor log files from the data directory structure:
  data/<YYYY-MM-DD>/<HH>.txt  (e.g. data/2026-04-20/00.txt)

Each line format:
  YYYY-MM-DD HH:MM:SS 0 <val> 1 <val> ... 15 <val>

Conversion pipeline (per sample):
  1. V_ref  = raw * 5 / 1023          (ADC → voltage at thermistor node)
  2. V_r    = 5 - V_ref               (voltage across series resistor)
  3. R_calc = V_ref * 1000 / V_r      (thermistor resistance, series R = 1 kΩ)
  4. T (K)  = 1 / (ln(R_calc / R_nom) / B + 1 / T0)
  5. T (°C) = T(K) - 273.15

Thermistor parameters:
  - B    = 3977
  - T0   = 25 + 273.15 K
  - R_nom = 10 kΩ  for channels 0–7 and 12–15
  - R_nom = 24 kΩ  for channels 8–11
"""

import math
import pandas as pd
from pathlib import Path

DATA_DIR = Path("../data")

# ── Thermistor constants ──────────────────────────────────────────────────────
VCC         = 5.0       # supply voltage (V)
R_SERIES    = 1_000     # series resistor (Ω)
B           = 3977      # Beta coefficient
T0          = 25 + 273.15  # reference temperature (K)
R_NOM_DEFAULT  = 10_000    # nominal resistance for most channels (Ω)
R_NOM_HIGH     = 24_000    # nominal resistance for channels 8–11 (Ω)
HIGH_R_CHANNELS = {8, 9, 10, 11}


def r_nom_for_channel(ch: int) -> float:
    return R_NOM_HIGH if ch in HIGH_R_CHANNELS else R_NOM_DEFAULT


def adc_to_celsius(raw: int, ch: int) -> float | None:
    """
    Convert a raw ADC reading to °C.
    Returns None if the reading is out of a physically sensible range
    (e.g. open circuit or short).
    """
    if raw <= 0 or raw >= 1023:
        return None
    v_ref  = raw * VCC / 1023          # voltage across thermistor
    v_r    = VCC - v_ref               # voltage across series resistor
    if v_r == 0:
        return None
    r_calc = v_ref * R_SERIES / v_r    # thermistor resistance (Ω)
    r_nom  = r_nom_for_channel(ch)
    try:
        t_kelvin = 1.0 / (math.log(r_calc / r_nom) / B + 1.0 / T0)
    except (ValueError, ZeroDivisionError):
        return None
    return round(t_kelvin - 273.15, 3)


# ── File / directory parsing ──────────────────────────────────────────────────

def parse_file(filepath: Path) -> pd.DataFrame:
    """Parse a single hour file into a tidy DataFrame."""
    records = []
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            tokens = line.split()
            if len(tokens) < 34:  # 2 (date+time) + 16*2
                continue
            ts = pd.Timestamp(f"{tokens[0]} {tokens[1]}")
            pairs = tokens[2:]
            for i in range(0, len(pairs), 2):
                ch  = int(pairs[i])
                raw = int(pairs[i + 1])
                records.append({
                    "timestamp": ts,
                    "channel":   ch,
                    "raw":       raw,
                    "celsius":   adc_to_celsius(raw, ch),
                })
    return pd.DataFrame(records, columns=["timestamp", "channel", "raw", "celsius"])


def parse_all(data_dir: Path = DATA_DIR) -> pd.DataFrame:
    """
    Walk all day/hour files and return a single sorted DataFrame.
    Structure: data_dir/<YYYY-MM-DD>/<HH>.txt
    """
    frames = []
    if not data_dir.exists():
        return pd.DataFrame(columns=["timestamp", "channel", "raw", "celsius"])

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
        return pd.DataFrame(columns=["timestamp", "channel", "raw", "celsius"])

    combined = pd.concat(frames, ignore_index=True)
    combined.sort_values("timestamp", inplace=True)
    combined.reset_index(drop=True, inplace=True)
    return combined


# ── Downsampling ──────────────────────────────────────────────────────────────

RESAMPLE_OPTIONS = {
    "None (10 s)": None,
    "1 min":       "1min",
    "5 min":       "5min",
    "10 min":      "10min",
}


def downsample(df: pd.DataFrame, rule: str | None) -> pd.DataFrame:
    """
    Resample both raw and celsius columns per channel.
    raw    → rounded integer mean
    celsius → rounded-to-3-decimal mean (NaNs excluded)
    """
    if rule is None or df.empty:
        return df

    frames = []
    for ch in sorted(df["channel"].unique()):
        sub = df[df["channel"] == ch].set_index("timestamp")

        raw_r = (
            sub["raw"].resample(rule).mean()
            .dropna().round().astype(int)
        )
        cel_r = (
            sub["celsius"].resample(rule).mean()
            .round(3)
        )
        r = pd.DataFrame({"raw": raw_r, "celsius": cel_r}).reset_index()
        r["channel"] = ch
        frames.append(r)

    if not frames:
        return df

    out = pd.concat(frames, ignore_index=True)
    out.sort_values(["timestamp", "channel"], inplace=True)
    out.reset_index(drop=True, inplace=True)
    return out
