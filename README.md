# Log File Analyzer

A command-line Python tool that scans a system/network log file and produces
a clean summary report — entry counts by severity, recurring issues, and the
most severe events — instead of requiring someone to read every line by hand.

This is modeled on a real, everyday task for IT technicians and NOC staff:
quickly spotting what actually needs attention in a stream of log output.

## What it does

- Parses log entries in the format: `YYYY-MM-DD HH:MM:SS LEVEL message`
- Counts entries by severity (`INFO`, `WARNING`, `ERROR`, `CRITICAL`)
- Detects **recurring issues** — the same problem repeating (e.g. a host
  timing out four times) is usually more important than a single one-off
  event, so these are surfaced separately
- Lists the most severe events (`CRITICAL` and `ERROR`) in one place
- Can filter the whole report down to a single severity level
- Can save the report to a text file instead of just printing it

## Usage

```bash
# Basic report
python log_analyzer.py sample.log

# Only show WARNING-level entries
python log_analyzer.py sample.log --level WARNING

# Save the report to a file instead of just printing it
python log_analyzer.py sample.log --output report.txt
```

## Example output

```
============================================================
LOG ANALYSIS REPORT
============================================================
Total entries parsed:  24

Entries by severity:
  CRITICAL  2
  ERROR     7
  WARNING   6
  INFO      9

Recurring issues (appeared more than once):
  [4x] Connection timeout to host 10.0.4.15
  [2x] Authentication failure for user svc-monitor on switch-access-07

Most severe events:
  [CRITICAL] 2026-01-15 05:03:47 - Power supply failure detected on rack-03-u02 (PSU-B)
  [CRITICAL] 2026-01-15 06:15:30 - Cooling system alert: intake temp 82F on aisle-3
  ...
============================================================
```

## Files

- `log_analyzer.py` — the script
- `sample.log` — a sample data-center-style log file to test it against

## What this demonstrates

- Reading and parsing structured text with regular expressions
- Command-line argument handling (`argparse`)
- Data aggregation and normalization (grouping similar messages even when
  they contain different numbers, like CPU percentages)
- Writing code that fails gracefully (missing file, malformed lines) instead
  of crashing

## Possible next steps

- Support additional log formats (e.g. syslog, JSON logs)
- Add a `--since` flag to only analyze entries after a given timestamp
- Export the report as CSV for use in a spreadsheet
