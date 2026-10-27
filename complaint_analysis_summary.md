# Complaint Analysis Summary

Source: `complaints.csv` | Rows read: 120 | Rows analysed: 120 | Rows excluded: 0

## Definitions

- **Complaint** = one row; counted once per `complaint_id`.
- **Closed case** = `status` equals `Closed`. All other statuses are treated as unresolved.
- **Resolution time** = `resolved_date` minus `created_date`, in calendar days, for Closed cases only.
- **Highest-volume category** = category with most complaints; percentage = its count / rows analysed.
- Percentages are rounded to 1 decimal place.
- These follow the 2.2.2 metric definitions as understood here; confirm against the 2.2.2 file before merge.
- Column mapping applied: `date_opened` -> `created_date`, `date_closed` -> `resolved_date`.

## Data quality (load evidence)

| Column | Missing values |
|---|---|
| complaint_id | 0 |
| customer_id | 0 |
| category | 0 |
| status | 0 |
| created_date | 0 |
| resolved_date | 86 |
| account_id | 39 |
| channel | 0 |
| priority | 0 |

Rows excluded by validation: 0.
A blank `resolved_date` on a non-Closed case is expected and is not an error.

## Status counts

| Status | Count | % |
|---|---:|---:|
| Closed | 34 | 28.3% |
| In Review | 32 | 26.7% |
| Escalated | 30 | 25.0% |
| Open | 24 | 20.0% |

## Category counts

| Category | Count | % |
|---|---:|---:|
| Mortgage Servicing | 31 | 25.8% |
| Card or Transaction Dispute | 25 | 20.8% |
| Service Quality | 21 | 17.5% |
| Digital Banking | 19 | 15.8% |
| Fees | 15 | 12.5% |
| Account Access | 9 | 7.5% |

## Observations

- **Mortgage Servicing** is the highest-volume category: 31 of 120 complaints (25.8%).
- 34 of 120 complaints (28.3%) are Closed; 86 remain Open, In Review or Escalated.
- Across 34 Closed cases, resolution took an average of 10.1 days (median 9.0, range 1-20).

## Limitations

- Synthetic data; no claim is made about real customers or performance.
- Counts are a snapshot. No trend, seasonality or improvement/deterioration claim is made because this exercise does not compare periods.
- Average resolution covers Closed cases only; open cases are not yet resolved, so it is not a measure of the whole backlog.
- Category shares do not show severity, cost or customer impact.