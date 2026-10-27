#!/usr/bin/env python3
"""Exercise 2.4.1 - Read and Analyze Complaint Data with Python.

Validates a complaints CSV, then writes status/category counts, the
highest-volume category percentage and closed-case resolution time.

Usage:
    python complaint_analysis.py [--input complaints.csv]
        [--output-csv complaint_analysis_output.csv]
        [--summary-md complaint_analysis_summary.md]

Exit codes: 0 = ok, 2 = file not found / unreadable, 3 = missing required
columns, 4 = no valid rows left to analyse.

Only the standard library is used so another consultant can run it as-is.
"""
import argparse
import csv
import statistics
import sys
from collections import Counter
from datetime import datetime

REQUIRED_COLUMNS = ["complaint_id", "customer_id", "category", "status",
                    "created_date", "resolved_date"]
# The sample extract names the date columns date_opened / date_closed.
# Map them to the contract names instead of changing the contract.
COLUMN_ALIASES = {"date_opened": "created_date", "date_closed": "resolved_date"}
CLOSED_STATUS = "Closed"   # metric definition: resolved = status "Closed"
DATE_FORMATS = ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S")


class ComplaintDataError(Exception):
    """Controlled, user-readable failure. Carries the process exit code."""
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code


def blank(v):
    return v is None or str(v).strip() == ""


def parse_date(v):
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(str(v).strip(), fmt).date()
        except ValueError:
            pass
    return None


# ---------------------------------------------------------------- Step 1
def load_complaints(path):
    """Return (rows, columns_found, aliases_applied). Raises ComplaintDataError."""
    try:
        with open(path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                raise ComplaintDataError(f"ERROR: '{path}' is empty (no header row).", 3)
            header = [h.strip() for h in reader.fieldnames]
            aliases = {a: c for a, c in COLUMN_ALIASES.items()
                       if a in header and c not in header}
            header = [aliases.get(h, h) for h in header]
            missing = [c for c in REQUIRED_COLUMNS if c not in header]
            if missing:
                raise ComplaintDataError(
                    f"ERROR: '{path}' is missing required column(s): {', '.join(missing)}", 3)
            reader.fieldnames = header
            rows = [{k: (v if v is not None else "") for k, v in r.items() if k}
                    for r in reader]
    except FileNotFoundError:
        raise ComplaintDataError(f"ERROR: input file not found: '{path}'. "
                                 "Check the path and re-run.", 2)
    except (PermissionError, IsADirectoryError, UnicodeDecodeError) as exc:
        raise ComplaintDataError(f"ERROR: cannot read '{path}': {exc}", 2)
    return rows, header, aliases


def missing_value_counts(rows, columns):
    return {c: sum(1 for r in rows if blank(r.get(c))) for c in columns}


def validate_rows(rows):
    """Split rows into (valid, rejected[(row_number, reason)]).

    A row is rejected when it cannot be counted reliably:
      - blank complaint_id / customer_id / category / status / created_date
      - unparseable created_date or resolved_date
      - Closed with no resolved_date, or resolved_date before created_date
    A blank resolved_date on a non-Closed case is NORMAL and is not rejected.
    """
    valid, rejected, seen = [], [], set()
    for i, r in enumerate(rows, start=2):          # row 1 is the header
        reasons = [f"missing {c}" for c in
                   ("complaint_id", "customer_id", "category", "status", "created_date")
                   if blank(r.get(c))]
        created = parse_date(r["created_date"]) if not blank(r.get("created_date")) else None
        if not blank(r.get("created_date")) and created is None:
            reasons.append("invalid created_date")
        resolved = None
        if not blank(r.get("resolved_date")):
            resolved = parse_date(r["resolved_date"])
            if resolved is None:
                reasons.append("invalid resolved_date")
        if r.get("status", "").strip() == CLOSED_STATUS and blank(r.get("resolved_date")):
            reasons.append("Closed case has no resolved_date")
        if created and resolved and resolved < created:
            reasons.append("resolved_date before created_date")
        cid = r.get("complaint_id", "").strip()
        if cid and cid in seen:
            reasons.append("duplicate complaint_id")
        seen.add(cid)
        if reasons:
            rejected.append((i, cid or "(blank)", "; ".join(reasons)))
        else:
            clean = {k: (v.strip() if isinstance(v, str) else v) for k, v in r.items()}
            clean["_created"], clean["_resolved"] = created, resolved
            valid.append(clean)
    return valid, rejected


# ---------------------------------------------------------------- Step 2
def pct(n, d):
    return round(100.0 * n / d, 1) if d else 0.0


def summarise(valid):
    total = len(valid)
    status = Counter(r["status"] for r in valid)
    category = Counter(r["category"] for r in valid)
    top_cat, top_n = sorted(category.items(), key=lambda kv: (-kv[1], kv[0]))[0]
    days = [(r["_resolved"] - r["_created"]).days
            for r in valid if r["status"] == CLOSED_STATUS and r["_resolved"]]
    res = None
    if days:
        res = {"closed_with_dates": len(days),
               "avg_days": round(statistics.mean(days), 1),
               "median_days": statistics.median(days),
               "min_days": min(days), "max_days": max(days)}
    return {"total": total, "status": status, "category": category,
            "top_category": top_cat, "top_count": top_n,
            "top_pct": pct(top_n, total), "resolution": res}


# ---------------------------------------------------------------- Step 3
def write_output_csv(path, s):
    rows = [("total", "total_complaints", "", s["total"], 100.0)]
    for k, n in sorted(s["status"].items(), key=lambda kv: (-kv[1], kv[0])):
        rows.append(("status_count", k, "", n, pct(n, s["total"])))
    for k, n in sorted(s["category"].items(), key=lambda kv: (-kv[1], kv[0])):
        rows.append(("category_count", k, "", n, pct(n, s["total"])))
    rows.append(("highest_volume_category", s["top_category"], "",
                 s["top_count"], s["top_pct"]))
    r = s["resolution"]
    if r:
        for name, key, unit in (("avg_resolution_days", "avg_days", "days"),
                                ("median_resolution_days", "median_days", "days"),
                                ("min_resolution_days", "min_days", "days"),
                                ("max_resolution_days", "max_days", "days")):
            rows.append(("closed_case_resolution", name, unit, r[key], ""))
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["measure_group", "measure", "unit", "value", "percent_of_valid_rows"])
        w.writerows(rows)


def write_summary_md(path, src, s, loaded, missing, rejected, aliases):
    L = []
    a = L.append
    a("# Complaint Analysis Summary\n")
    a(f"Source: `{src}` | Rows read: {loaded} | Rows analysed: {s['total']} | "
      f"Rows excluded: {len(rejected)}\n")
    a("## Definitions\n")
    a("- **Complaint** = one row; counted once per `complaint_id`.")
    a(f"- **Closed case** = `status` equals `{CLOSED_STATUS}`. All other statuses are treated as unresolved.")
    a("- **Resolution time** = `resolved_date` minus `created_date`, in calendar days, "
      "for Closed cases only.")
    a("- **Highest-volume category** = category with most complaints; percentage = its count / rows analysed.")
    a("- Percentages are rounded to 1 decimal place.")
    a("- These follow the 2.2.2 metric definitions as understood here; confirm against the 2.2.2 file before merge.")
    if aliases:
        a("- Column mapping applied: " + ", ".join(f"`{k}` -> `{v}`" for k, v in aliases.items()) + ".")
    a("\n## Data quality (load evidence)\n")
    a("| Column | Missing values |\n|---|---|")
    for c, n in missing.items():
        a(f"| {c} | {n} |")
    a(f"\nRows excluded by validation: {len(rejected)}.")
    a("A blank `resolved_date` on a non-Closed case is expected and is not an error.\n")
    a("## Status counts\n")
    a("| Status | Count | % |\n|---|---:|---:|")
    for k, n in sorted(s["status"].items(), key=lambda kv: (-kv[1], kv[0])):
        a(f"| {k} | {n} | {pct(n, s['total'])}% |")
    a("\n## Category counts\n")
    a("| Category | Count | % |\n|---|---:|---:|")
    for k, n in sorted(s["category"].items(), key=lambda kv: (-kv[1], kv[0])):
        a(f"| {k} | {n} | {pct(n, s['total'])}% |")
    a("\n## Observations\n")
    a(f"- **{s['top_category']}** is the highest-volume category: {s['top_count']} of "
      f"{s['total']} complaints ({s['top_pct']}%).")
    closed = s["status"].get(CLOSED_STATUS, 0)
    a(f"- {closed} of {s['total']} complaints ({pct(closed, s['total'])}%) are Closed; "
      f"{s['total'] - closed} remain Open, In Review or Escalated.")
    r = s["resolution"]
    if r:
        a(f"- Across {r['closed_with_dates']} Closed cases, resolution took an average of "
          f"{r['avg_days']} days (median {r['median_days']}, range {r['min_days']}-{r['max_days']}).")
    else:
        a("- No Closed cases with valid dates, so resolution time is not reported.")
    a("\n## Limitations\n")
    a("- Synthetic data; no claim is made about real customers or performance.")
    a("- Counts are a snapshot. No trend, seasonality or improvement/deterioration claim is made "
      "because this exercise does not compare periods.")
    a("- Average resolution covers Closed cases only; open cases are not yet resolved, so it "
      "is not a measure of the whole backlog.")
    a("- Category shares do not show severity, cost or customer impact.")
    if rejected:
        a("\n## Excluded rows\n")
        a("| Row | complaint_id | Reason |\n|---:|---|---|")
        for row, cid, why in rejected[:25]:
            a(f"| {row} | {cid} | {why} |")
        if len(rejected) > 25:
            a(f"\n...and {len(rejected) - 25} more.")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


# ------------------------------------------------------------------ main
def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--input", default="complaints.csv")
    p.add_argument("--output-csv", default="complaint_analysis_output.csv")
    p.add_argument("--summary-md", default="complaint_analysis_summary.md")
    args = p.parse_args(argv)
    try:
        rows, header, aliases = load_complaints(args.input)
        print(f"Loaded {len(rows)} rows from '{args.input}'.")
        if aliases:
            print("Column mapping applied: " +
                  ", ".join(f"{k}->{v}" for k, v in aliases.items()))
        # missing-value counts across every column present, required first
        extra = [c for c in header if c not in REQUIRED_COLUMNS]
        missing = missing_value_counts(rows, REQUIRED_COLUMNS + extra)
        print("Missing-value counts:")
        for c, n in missing.items():
            print(f"  {c}: {n}")
        valid, rejected = validate_rows(rows)
        for row, cid, why in rejected:
            print(f"WARNING: row {row} ({cid}) excluded - {why}")
        if not valid:
            raise ComplaintDataError("ERROR: no valid rows to analyse.", 4)
        s = summarise(valid)
        write_output_csv(args.output_csv, s)
        write_summary_md(args.summary_md, args.input, s, len(rows), missing, rejected, aliases)
        print(f"Analysed {s['total']} rows ({len(rejected)} excluded).")
        print(f"Highest-volume category: {s['top_category']} "
              f"({s['top_count']}, {s['top_pct']}%)")
        print(f"Wrote {args.output_csv} and {args.summary_md}")
        return 0
    except ComplaintDataError as exc:
        print(str(exc), file=sys.stderr)
        return exc.code


if __name__ == "__main__":
    sys.exit(main())