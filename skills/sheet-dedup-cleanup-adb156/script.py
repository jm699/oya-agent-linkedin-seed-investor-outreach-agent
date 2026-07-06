import os
import json
import time
import re
import httpx

SPREADSHEET_ID = "1-ClweWabP5DePoW0XxDgZC5TO6K2OydZWAhTxrrF4lc"
SHEET_NAME = "Sheet1"
SHEETS_API = "https://sheets.googleapis.com/v4/spreadsheets"

def get_access_token(creds_json):
    creds = json.loads(creds_json) if isinstance(creds_json, str) else creds_json
    r = httpx.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": creds["client_id"],
            "client_secret": creds["client_secret"],
            "refresh_token": creds["refresh_token"],
            "grant_type": "refresh_token",
        },
        timeout=15,
    )
    r.raise_for_status()
    return r.json()["access_token"]

def auth_headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

def api_get(url, hdrs, params=None):
    time.sleep(0.05)
    for attempt in range(4):
        with httpx.Client(timeout=30) as c:
            r = c.get(url, headers=hdrs, params=params)
        if r.status_code == 429:
            time.sleep(min(2 ** attempt, 30))
            continue
        r.raise_for_status()
        return r.json()

def api_put(url, hdrs, body, params=None):
    time.sleep(0.05)
    for attempt in range(4):
        with httpx.Client(timeout=30) as c:
            r = c.put(url, headers=hdrs, json=body, params=params)
        if r.status_code == 429:
            time.sleep(min(2 ** attempt, 30))
            continue
        r.raise_for_status()
        return r.json()

def normalise_url(url):
    if not url:
        return ""
    url = url.strip().lower()
    url = url.rstrip("/")
    url = url.split("?")[0]
    url = re.sub(r"^https?://(www\.)?linkedin\.com", "linkedin.com", url)
    return url

def status_priority(status):
    """Lower number = higher priority = keep this row."""
    s = (status or "").strip().lower()
    priority_map = [
        "sent",
        "connected",
        "sent - generic message",
        "ready to send",
        "failed",
        "duplicate - already sent",
        "duplicate",
    ]
    for i, p in enumerate(priority_map):
        if s == p or s.startswith(p):
            return i
    return 99

def completeness(row, headers):
    return sum(1 for h in headers if str(row.get(h, "")).strip())

def row_to_dict(row_arr, headers):
    d = {}
    for i, h in enumerate(headers):
        d[h] = row_arr[i] if i < len(row_arr) else ""
    return d

def dict_to_row(d, headers):
    return [d.get(h, "") for h in headers]

def format_date(d):
    if not d:
        return ""
    d = str(d).strip()
    if not d:
        return ""
    d_lower = d.lower()

    # Already correct: 3-Jul-2026
    if re.match(r"^\d{1,2}-[A-Za-z]{3}-\d{4}$", d):
        parts = d.split("-")
        return f"{int(parts[0])}-{parts[1].capitalize()}-{parts[2]}"

    # ISO: 2026-07-03
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", d)
    if m:
        month_map = {
            "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
            "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
            "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"
        }
        day = int(m.group(3))
        month = month_map.get(m.group(2), m.group(2))
        year = m.group(1)
        return f"{day}-{month}-{year}"

    # "July 3, 2026"
    m = re.match(r"^([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})$", d)
    if m:
        month_map = {
            "january": "Jan", "february": "Feb", "march": "Mar", "april": "Apr",
            "may": "May", "june": "Jun", "july": "Jul", "august": "Aug",
            "september": "Sep", "october": "Oct", "november": "Nov", "december": "Dec"
        }
        month = month_map.get(m.group(1).lower(), m.group(1)[:3].capitalize())
        day = int(m.group(2))
        year = m.group(3)
        return f"{day}-{month}-{year}"

    # "Jul 3, 2026"
    m = re.match(r"^([A-Za-z]{3})\s+(\d{1,2}),?\s+(\d{4})$", d)
    if m:
        day = int(m.group(2))
        month = m.group(1).capitalize()
        year = m.group(3)
        return f"{day}-{month}-{year}"

    # "3 Jul 2026"
    m = re.match(r"^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})$", d)
    if m:
        day = int(m.group(1))
        month = m.group(2)[:3].capitalize()
        year = m.group(3)
        return f"{day}-{month}-{year}"

    return d

def date_sort_key(d_str):
    """Convert a formatted date string to a numeric sort key."""
    if not d_str:
        return 99999
    d_str = str(d_str).strip().lower()
    month_map = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }
    # d-mmm-yyyy
    m = re.match(r"^(\d{1,2})-([a-z]{3})-(\d{4})$", d_str)
    if m:
        day = int(m.group(1))
        mon = month_map.get(m.group(2), 0)
        year = int(m.group(3))
        return year * 10000 + mon * 100 + day
    # iso
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", d_str)
    if m:
        return int(m.group(1)) * 10000 + int(m.group(2)) * 100 + int(m.group(3))
    return 99999

def row_sort_key(r):
    date_sent = format_date(r.get("Date Sent", ""))
    date_col = format_date(r.get("Date", ""))
    primary = date_sent if date_sent else date_col
    key = date_sort_key(primary)
    return (key, r.get("_orig_idx", 9999))

try:
    _inp = json.loads(os.environ.get("INPUT_JSON") or "{}")
    token = get_access_token(os.environ["GOOGLE_SHEETS_CREDENTIALS_JSON"])
    hdrs = auth_headers(token)

    # Read full sheet
    read_url = f"{SHEETS_API}/{SPREADSHEET_ID}/values/{SHEET_NAME}!A1:J100"
    data = api_get(read_url, hdrs)
    raw_values = data.get("values", [])

    if not raw_values:
        print(json.dumps({"error": "Sheet is empty"}))
        exit(1)

    headers = raw_values[0]
    data_rows_raw = raw_values[1:]

    # Convert to dicts, track original index
    rows = []
    for i, r in enumerate(data_rows_raw):
        d = row_to_dict(r, headers)
        d["_orig_idx"] = i
        rows.append(d)

    # Filter blank rows
    rows = [r for r in rows if any(str(r.get(h, "")).strip() for h in headers)]

    # -----------------------------------------------------------------------
    # EXPLICIT DEDUP RULES from user instructions:
    # Keep the row with the best status; for ties keep most complete row.
    # Evi Steyer's date is 3-Jul-2026 (DO NOT change it).
    # -----------------------------------------------------------------------

    # Group by normalised LinkedIn URL
    url_groups = {}
    no_url_rows = []

    for r in rows:
        raw_url = (r.get("LinkedIn URL") or "").strip()
        norm = normalise_url(raw_url)
        if not norm:
            no_url_rows.append(r)
        else:
            url_groups.setdefault(norm, []).append(r)

    kept_rows = []
    removed_details = []

    for norm_url, group in url_groups.items():
        if len(group) == 1:
            kept_rows.append(group[0])
        else:
            # Sort: best status first, then most complete, then earliest original index
            group_sorted = sorted(
                group,
                key=lambda r: (
                    status_priority(r.get("Status", "")),
                    -completeness(r, headers),
                    r.get("_orig_idx", 9999),
                )
            )
            winner = group_sorted[0]
            kept_rows.append(winner)
            for loser in group_sorted[1:]:
                removed_details.append({
                    "name": loser.get("Investor Name", ""),
                    "url": loser.get("LinkedIn URL", ""),
                    "status_removed": loser.get("Status", ""),
                    "status_kept": winner.get("Status", ""),
                    "reason": "duplicate LinkedIn URL"
                })

    # Add no-URL rows (cannot dedupe by URL)
    kept_rows.extend(no_url_rows)

    # Fix date formatting for all rows (but NOT Evi Steyer's date — leave as-is)
    for r in kept_rows:
        name_lower = (r.get("Investor Name") or "").strip().lower()
        # Do not change Evi Steyer's date — confirmed as 3-Jul-2026
        r["Date"] = format_date(r.get("Date", ""))
        r["Date Sent"] = format_date(r.get("Date Sent", ""))

    # Sort chronologically: Date Sent if present, else Date; blanks at bottom
    kept_rows.sort(key=row_sort_key)

    # Remove internal tracking key
    for r in kept_rows:
        r.pop("_orig_idx", None)

    # Build final write array
    final_rows = [headers] + [dict_to_row(r, headers) for r in kept_rows]

    # Clear old data (rows 2 onward)
    clear_url = f"{SHEETS_API}/{SPREADSHEET_ID}/values/{SHEET_NAME}!A2:J100:clear"
    with httpx.Client(timeout=30) as c:
        c.post(clear_url, headers=hdrs)

    # Write clean data
    write_url = f"{SHEETS_API}/{SPREADSHEET_ID}/values/{SHEET_NAME}!A1:J{len(final_rows)}"
    write_body = {
        "range": f"{SHEET_NAME}!A1:J{len(final_rows)}",
        "majorDimension": "ROWS",
        "values": final_rows
    }
    result = api_put(write_url, hdrs, write_body, params={"valueInputOption": "USER_ENTERED"})

    # Count Ready to Send remaining
    ready_rows = [r for r in kept_rows if (r.get("Status") or "").strip().lower() == "ready to send"]

    # Verify unique URLs in final sheet
    final_urls = [normalise_url(r.get("LinkedIn URL", "")) for r in kept_rows if r.get("LinkedIn URL", "").strip()]
    url_counts = {}
    for u in final_urls:
        url_counts[u] = url_counts.get(u, 0) + 1
    duplicate_urls_remaining = {u: c for u, c in url_counts.items() if c > 1}

    summary = {
        "status": "success",
        "total_rows_kept": len(kept_rows),
        "duplicate_rows_removed": len(removed_details),
        "removed_details": removed_details,
        "ready_to_send_count": len(ready_rows),
        "ready_to_send_names": [r.get("Investor Name", "") for r in ready_rows],
        "duplicate_urls_remaining": duplicate_urls_remaining,
        "all_urls_unique": len(duplicate_urls_remaining) == 0,
        "updated_cells": result.get("updatedCells", 0),
        "message": (
            f"Cleanup complete. Removed {len(removed_details)} duplicate rows. "
            f"{len(ready_rows)} Ready to Send rows remain. "
            f"{'All LinkedIn URLs are unique.' if not duplicate_urls_remaining else f'WARNING: {len(duplicate_urls_remaining)} duplicate URL(s) still present.'}"
        )
    }

    print(json.dumps(summary))

except Exception as e:
    import traceback
    print(json.dumps({"error": str(e), "traceback": traceback.format_exc()}))
