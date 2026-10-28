import re
from collections import Counter

import pandas as pd

LEVEL_PATTERN = re.compile(
    r"\b(CRITICAL|FATAL|ERROR|ERR|WARNING|WARN|INFO|DEBUG)\b",
    re.IGNORECASE,
)

LEVEL_MAP = {
    "FATAL": "CRITICAL",
    "ERR": "ERROR",
    "WARN": "WARNING",
}

SEVERITY_MAP = {
    "CRITICAL": "Critical",
    "ERROR": "High",
    "WARNING": "Medium",
    "INFO": "Low",
    "DEBUG": "Low",
    "UNKNOWN": "Unclassified",
}


def analyze_logs(log_text):
    """Parse log text into a DataFrame of entries."""
    records = []

    for line_number, raw_line in enumerate(log_text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue

        match = LEVEL_PATTERN.search(line)
        if match:
            original_level = match.group(1).upper()
            level = LEVEL_MAP.get(original_level, original_level)
            message = (line[:match.start()] + line[match.end():]).strip(
                " :-|\t"
            )
        else:
            level = "UNKNOWN"
            message = line

        records.append({
            "Line": line_number,
            "Level": level,
            "Severity": SEVERITY_MAP[level],
            "Message": message or line,
            "Original Log": line,
        })

    return pd.DataFrame(
        records,
        columns=["Line", "Level", "Severity", "Message", "Original Log"],
    )


def get_summary(df):
    """Return counts by log level."""
    counts = Counter(df["Level"]) if not df.empty else Counter()
    return {
        "total": len(df),
        "critical": counts.get("CRITICAL", 0),
        "errors": counts.get("ERROR", 0),
        "warnings": counts.get("WARNING", 0),
        "info": counts.get("INFO", 0),
        "debug": counts.get("DEBUG", 0),
        "unknown": counts.get("UNKNOWN", 0),
    }


def create_text_report(df, filename):
    """Create a plain-text analysis report."""
    summary = get_summary(df)
    lines = [
        "AUTOMATED LOG FILE ANALYZER",
        "=" * 35,
        f"File analyzed: {filename}",
        f"Total log entries: {summary['total']}",
        "",
        "LOG LEVEL SUMMARY",
        "-" * 25,
        f"Critical: {summary['critical']}",
        f"Errors: {summary['errors']}",
        f"Warnings: {summary['warnings']}",
        f"Info: {summary['info']}",
        f"Debug: {summary['debug']}",
        f"Unrecognized: {summary['unknown']}",
        "",
        "MOST FREQUENT ISSUES",
        "-" * 25,
    ]

    issues = df[df["Level"].isin(["CRITICAL", "ERROR", "WARNING"])]
    if issues.empty:
        lines.append("No errors, critical events, or warnings found.")
    else:
        for message, count in Counter(issues["Message"]).most_common(10):
            lines.append(f"{count} occurrence(s): {message}")

    lines.extend(["", "DETAILED LOG ENTRIES", "-" * 25])
    for _, row in df.iterrows():
        lines.append(
            f"Line {row['Line']} | {row['Level']} | {row['Severity']} | "
            f"{row['Original Log']}"
        )
    return "\n".join(lines)
