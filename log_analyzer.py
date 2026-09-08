"""
log_analyzer.py

A command-line tool that reads a system/network log file and produces a
summary report: how many entries at each severity level, which specific
issues repeat most often, and a list of the most severe events.

This mirrors a real, everyday task for IT/data center technicians and NOC
staff: scanning through log output to quickly find what actually needs
attention instead of reading every line by hand.

Usage:
    python log_analyzer.py sample.log
    python log_analyzer.py sample.log --output report.txt
    python log_analyzer.py sample.log --level ERROR
"""

import argparse
import re
from collections import Counter
from pathlib import Path

# Matches lines like:
# 2026-01-15 05:03:47 CRITICAL Power supply failure detected on rack-03-u02 (PSU-B)
LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+"
    r"(?P<level>INFO|WARNING|ERROR|CRITICAL)\s+"
    r"(?P<message>.+)$"
)

# Order of severity, used for sorting the "most severe events" section
SEVERITY_ORDER = {"CRITICAL": 0, "ERROR": 1, "WARNING": 2, "INFO": 3}


def parse_log_file(filepath):
    """
    Read the log file and return a list of parsed entries.

    Each entry is a dict with keys: timestamp, level, message.
    Lines that don't match the expected format are skipped and counted
    separately, since real-world logs are rarely perfectly clean.
    """
    entries = []
    skipped = 0

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            match = LOG_PATTERN.match(line)
            if match:
                entries.append(match.groupdict())
            else:
                skipped += 1

    return entries, skipped


def build_report(entries, skipped, level_filter=None):
    """
    Turn a list of parsed log entries into a human-readable report string.

    If level_filter is given (e.g. "ERROR"), only that severity's entries
    are analyzed for the message-frequency section.
    """
    lines = []
    total = len(entries)

    level_counts = Counter(entry["level"] for entry in entries)

    lines.append("=" * 60)
    lines.append("LOG ANALYSIS REPORT")
    lines.append("=" * 60)
    lines.append(f"Total entries parsed:  {total}")
    if skipped:
        lines.append(f"Lines skipped (unrecognized format): {skipped}")
    lines.append("")

    lines.append("Entries by severity:")
    for level in ("CRITICAL", "ERROR", "WARNING", "INFO"):
        count = level_counts.get(level, 0)
        if count:
            lines.append(f"  {level:<9} {count}")
    lines.append("")

    # Filter down to a specific level if requested
    working_set = entries
    if level_filter:
        working_set = [e for e in entries if e["level"] == level_filter.upper()]
        lines.append(f"Filtered to level: {level_filter.upper()} "
                      f"({len(working_set)} entries)")
        lines.append("")

    # Most frequent messages (a repeated error usually matters more than
    # a one-off) -- we normalize by stripping trailing numbers/percentages
    # so "CPU usage 91%" and "CPU usage 94%" still count as the same issue.
    normalized_messages = [
        re.sub(r"\s+", " ", re.sub(r"\(.*?\)|\d+%|\d+F", "", e["message"])).strip()
        for e in working_set
    ]
    message_counts = Counter(normalized_messages)

    repeats = [(msg, count) for msg, count in message_counts.items() if count > 1]
    repeats.sort(key=lambda x: x[1], reverse=True)

    if repeats:
        lines.append("Recurring issues (appeared more than once):")
        for msg, count in repeats:
            lines.append(f"  [{count}x] {msg}")
        lines.append("")

    # Most severe individual events, most recent first within each severity
    severe = [e for e in working_set if e["level"] in ("CRITICAL", "ERROR")]
    severe.sort(key=lambda e: SEVERITY_ORDER[e["level"]])

    if severe:
        lines.append("Most severe events:")
        for e in severe:
            lines.append(f"  [{e['level']}] {e['timestamp']} - {e['message']}")
        lines.append("")

    if not entries:
        lines.append("No entries matched the expected log format.")

    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze a system/network log file and summarize severity and recurring issues."
    )
    parser.add_argument("logfile", type=str, help="Path to the log file to analyze")
    parser.add_argument(
        "--output", "-o", type=str, default=None,
        help="Optional path to save the report as a text file"
    )
    parser.add_argument(
        "--level", "-l", type=str, default=None,
        help="Only analyze one severity level (e.g. ERROR, WARNING, CRITICAL)"
    )
    args = parser.parse_args()

    path = Path(args.logfile)
    if not path.exists():
        print(f"Error: file not found: {path}")
        return

    entries, skipped = parse_log_file(path)
    report = build_report(entries, skipped, level_filter=args.level)

    print(report)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\nReport saved to {args.output}")


if __name__ == "__main__":
    main()
