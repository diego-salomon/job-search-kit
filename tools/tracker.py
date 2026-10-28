#!/usr/bin/env python3
"""
tracker.py -- the applications tracker, as a plain CSV you can also open in Excel or Sheets.

  python3 tools/tracker.py add --company Acme --role "Operations Specialist" --link URL \
          [--lane "Startup ops"] [--salary "45-55k"] [--fit 4] [--note "..."] [--status Queued]
  python3 tools/tracker.py set Acme "Operations Specialist" Applied     # change the status
  python3 tools/tracker.py list [--status Queued]
  python3 tools/tracker.py find Acme                                     # is it already there?
  python3 tools/tracker.py due                                           # chasers due today or earlier
  python3 tools/tracker.py stats

Statuses: Queued, Verify first, Applied, Interview, Offer, Rejected, Not a fit, Closed.
Setting a row to Applied fills the applied date and a chaser date 7 days later.
The same company with the same or almost the same title counts as the same job.
"""
import argparse
import csv
import difflib
import os
import sys
from collections import Counter
from datetime import date, timedelta

PATH = os.environ.get("TRACKER", os.path.join(os.path.dirname(__file__), "..", "me", "tracker.csv"))
COLUMNS = ["status", "role", "company", "lane", "salary", "fit", "applied", "chaser_due", "note", "link", "added"]
STATUSES = ["Queued", "Verify first", "Applied", "Interview", "Offer", "Rejected", "Not a fit", "Closed"]
CHASER_DAYS = 7


def load():
    if not os.path.exists(PATH):
        return []
    with open(PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save(rows):
    os.makedirs(os.path.dirname(os.path.abspath(PATH)), exist_ok=True)
    order = {s: i for i, s in enumerate(STATUSES)}
    rows.sort(key=lambda r: (order.get(r["status"], 99), r.get("added", "")), reverse=False)
    with open(PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in COLUMNS})


def same_job(row, company, role):
    if row["company"].strip().lower() != company.strip().lower():
        return False
    a, b = row["role"].strip().lower(), role.strip().lower()
    return a == b or difflib.SequenceMatcher(None, a, b).ratio() >= 0.85


def find(rows, company, role=None):
    if role is None:
        return [r for r in rows if company.lower() in r["company"].lower()]
    return [r for r in rows if same_job(r, company, role)]


def set_status(row, status):
    if status not in STATUSES:
        sys.exit(f"Unknown status '{status}'. Use one of: {', '.join(STATUSES)}")
    row["status"] = status
    if status == "Applied" and not row.get("applied"):
        today = date.today()
        row["applied"] = today.isoformat()
        row["chaser_due"] = (today + timedelta(days=CHASER_DAYS)).isoformat()
    if status in ("Rejected", "Not a fit", "Closed", "Offer", "Interview"):
        row["chaser_due"] = ""


def show(rows):
    if not rows:
        print("(nothing)")
        return
    for r in rows:
        fit = f" fit {r['fit']}/5" if r.get("fit") else ""
        extra = f"  chaser {r['chaser_due']}" if r.get("chaser_due") else ""
        print(f"{r['status']:<12} {r['company']} | {r['role']}{fit}{extra}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("--company", required=True)
    a.add_argument("--role", required=True)
    a.add_argument("--link", default="")
    a.add_argument("--lane", default="")
    a.add_argument("--salary", default="")
    a.add_argument("--fit", default="")
    a.add_argument("--note", default="")
    a.add_argument("--status", default=None, help="default Queued for a new row; an existing row keeps its status")
    s = sub.add_parser("set")
    s.add_argument("company")
    s.add_argument("role")
    s.add_argument("status")
    l = sub.add_parser("list")
    l.add_argument("--status")
    f = sub.add_parser("find")
    f.add_argument("company")
    f.add_argument("role", nargs="?")
    sub.add_parser("due")
    sub.add_parser("stats")
    args = ap.parse_args()

    rows = load()
    if args.cmd == "add":
        dup = find(rows, args.company, args.role)
        if dup:
            print("Already tracked, updating that row instead:")
            row = dup[0]
            for k in ("link", "lane", "salary", "fit", "note"):
                if getattr(args, k):
                    row[k] = getattr(args, k)
        else:
            row = {"company": args.company, "role": args.role, "link": args.link, "lane": args.lane,
                   "salary": args.salary, "fit": args.fit, "note": args.note, "added": date.today().isoformat()}
            rows.append(row)
        if args.status or not dup:
            set_status(row, args.status or "Queued")
        save(rows)
        show([row])
    elif args.cmd == "set":
        hit = find(rows, args.company, args.role)
        if not hit:
            sys.exit(f"No row for {args.company} | {args.role}")
        set_status(hit[0], args.status)
        save(rows)
        show(hit[:1])
    elif args.cmd == "list":
        show([r for r in rows if not args.status or r["status"] == args.status])
    elif args.cmd == "find":
        show(find(rows, args.company, args.role))
    elif args.cmd == "due":
        today = date.today().isoformat()
        show([r for r in rows if r["status"] == "Applied" and r.get("chaser_due") and r["chaser_due"] <= today])
    elif args.cmd == "stats":
        c = Counter(r["status"] for r in rows)
        print(", ".join(f"{s}: {c[s]}" for s in STATUSES if c[s]) or "(empty)")
        applied = sum(c[s] for s in ("Applied", "Interview", "Offer", "Rejected", "Closed"))
        if applied:
            print(f"{applied} sent, {c['Interview'] + c['Offer']} at interview or offer right now")


if __name__ == "__main__":
    main()
