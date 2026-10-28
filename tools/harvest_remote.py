#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harvest_remote.py — find FULLY-REMOTE, hire-from-anywhere jobs.

Pulls from several free job-board APIs, classifies each role by where it can be
done from (WORLDWIDE / ELIGIBLE-for-your-region / RESTRICTED), de-dupes, tags a
CV family, writes a ranked CSV, and prints a shortlist. Pure Python standard
library — no installs.

Usage:
  python harvest_remote.py --keyword content,seo,ecommerce --out jobs.csv
  python harvest_remote.py                          # everything, worldwide-only
  python harvest_remote.py --region "europe,spain"  # ALSO count these regions as eligible
  python harvest_remote.py --all                    # also include region-locked roles
"""
import sys, csv, json, ssl, html, argparse, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (compatible; remote-job-harvester/1.0)"}

def fix_text(s):
    """Repair common mojibake (UTF-8 read as latin-1) and unescape HTML entities."""
    if not s:
        return ""
    s = str(s)
    if "Ã" in s or "â€" in s or "Â" in s:
        try:
            repaired = s.encode("latin-1", "ignore").decode("utf-8", "ignore")
            if repaired:
                s = repaired
        except Exception:
            pass
    return html.unescape(s).strip()

def _ctx(insecure):
    if insecure:
        c = ssl.create_default_context(); c.check_hostname = False; c.verify_mode = ssl.CERT_NONE
        return c
    return None

def fetch_json(url, insecure=False, timeout=45):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ctx(insecure)) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except ssl.SSLCertVerificationError:
        if not insecure:
            sys.stderr.write("  [ssl] verify failed, retrying insecurely: %s\n" % url)
            return fetch_json(url, insecure=True, timeout=timeout)
        raise

def norm(source, title, company, url, location, tags, category, salary, date, loc_reliable=True):
    # loc_reliable=False means `location` is the company HQ (e.g. RemoteOK), not a
    # candidate-eligibility field, so it must not be read as a hard restriction.
    if isinstance(tags, str): tags = [tags]
    tags = [t for t in (tags or []) if isinstance(t, str)]
    return dict(source=source, title=fix_text(title), company=fix_text(company),
                url=(url or "").strip(), location=fix_text(location),
                tags=", ".join(tags), category=(category or "").strip(),
                salary=(str(salary).strip() if salary not in (None, "", 0) else ""),
                date=str(date or "")[:10], loc_reliable=loc_reliable)

# ---------------- sources ----------------
def s_remotive(ins, kw):
    d = fetch_json("https://remotive.com/api/remote-jobs", ins)
    return [norm("Remotive", j.get("title"), j.get("company_name"), j.get("url"),
                 j.get("candidate_required_location"), j.get("tags"), j.get("category"),
                 j.get("salary"), j.get("publication_date")) for j in d.get("jobs", [])]

def s_remoteok(ins, kw):
    d = fetch_json("https://remoteok.com/api", ins); out = []
    for j in d:
        if not isinstance(j, dict) or not (j.get("position") or j.get("title")):
            continue
        sal = ""
        if j.get("salary_min"): sal = "%s-%s" % (j.get("salary_min"), j.get("salary_max"))
        out.append(norm("RemoteOK", j.get("position") or j.get("title"), j.get("company"),
                        j.get("url"), j.get("location"), j.get("tags"), "", sal, j.get("date"),
                        loc_reliable=False))
    return out

def s_jobicy(ins, kw):
    d = fetch_json("https://jobicy.com/api/v2/remote-jobs?count=50", ins); out = []
    for j in d.get("jobs", []):
        sal = ""
        if j.get("annualSalaryMin"):
            sal = "%s-%s %s" % (j.get("annualSalaryMin"), j.get("annualSalaryMax"), j.get("salaryCurrency") or "")
        out.append(norm("Jobicy", j.get("jobTitle"), j.get("companyName"), j.get("url"),
                        j.get("jobGeo"), j.get("jobIndustry"),
                        (j.get("jobType") if isinstance(j.get("jobType"), str) else ""), sal, j.get("pubDate")))
    return out

def s_workingnomads(ins, kw):
    d = fetch_json("https://www.workingnomads.com/api/exposed_jobs/", ins)
    if isinstance(d, dict): d = d.get("jobs", d.get("results", []))
    out = []
    for j in d:
        if not isinstance(j, dict): continue
        out.append(norm("WorkingNomads", j.get("title"), j.get("company_name") or j.get("company"),
                        j.get("url"), j.get("location"), j.get("tags"), j.get("category_name"),
                        "", j.get("pub_date") or j.get("publication_date")))
    return out

def s_himalayas(ins, kw):
    d = fetch_json("https://himalayas.app/jobs/api?limit=100", ins)
    jobs = d.get("jobs", []) if isinstance(d, dict) else d
    out = []
    for j in jobs:
        if not isinstance(j, dict): continue
        loc = j.get("locationRestrictions") or j.get("locations") or ""
        if isinstance(loc, list): loc = ", ".join(str(x) for x in loc)
        comp = j.get("companyName")
        if not comp and isinstance(j.get("company"), dict): comp = j["company"].get("name")
        sal = ""
        if j.get("minSalary"): sal = "%s-%s" % (j.get("minSalary"), j.get("maxSalary"))
        out.append(norm("Himalayas", j.get("title"), comp,
                        j.get("applicationLink") or j.get("url") or j.get("guid"),
                        loc, j.get("categories") or j.get("tags"), "", sal,
                        j.get("pubDate") or j.get("publicationDate")))
    return out

SOURCES = [("Remotive", s_remotive), ("RemoteOK", s_remoteok), ("Jobicy", s_jobicy),
           ("WorkingNomads", s_workingnomads), ("Himalayas", s_himalayas)]

# ---------------- classification ----------------
WORLDWIDE_HINTS = ("worldwide", "anywhere", "global", "remote, world")
# Only truly-global terms are eligible by default. Add YOUR region(s) with --region
# (e.g. --region "latam,south america" or "europe,spain,united kingdom" or "india").
ELIG_DEFAULT = ("worldwide", "anywhere", "global")
BLANK_REMOTE = ("", "remote", "fully remote", "100% remote", "remote work", "remote, ")

def bucket(loc, elig_terms, reliable=True):
    # Precision-first. A named place (a city, a country, a region you're not in) is treated
    # as RESTRICTED, because on these boards a named location almost always means the role is
    # locked to that region. Only explicit worldwide, your region, or a blank/"remote-only"
    # field surfaces. Rare-but-clean beats a flood of region-locked false positives.
    s = (loc or "").strip().lower()
    if any(w in s for w in WORLDWIDE_HINTS):
        return "WORLDWIDE"
    if any(t in s for t in elig_terms):
        return "ELIGIBLE"
    if s in BLANK_REMOTE:
        return "WORLDWIDE?"          # no region given -> unknown, worth a 10-second check
    return "RESTRICTED"

FAMILIES = [
    ("Operations", ("operations", "ops ", "logistics", "supply chain", "coordinator", "program manager", "project manager", "process")),
    ("SEO & Content", ("content", "seo", "writer", "copywrit", "editor", "blog", "aeo", "journalist")),
    ("Email & Lifecycle", ("email", "lifecycle", "klaviyo", "crm", "retention", "newsletter")),
    ("Growth & Performance", ("growth", "performance", "ppc", "paid", " ads", "acquisition", "media buyer", "demand gen")),
    ("Ecommerce/Amazon", ("ecommerce", "e-commerce", "shopify", "amazon", "marketplace", "dtc", "catalog", "merchandis")),
    ("Data", ("data", "analyst", "analytics", "sql", "bi ")),
    ("Automation/AI", ("automation", "ai ", " ai", "llm", "prompt", "integration", "no-code", "nocode", "zapier", "make.com")),
    ("Engineering", ("engineer", "developer", "full-stack", "fullstack", "backend", "frontend", "software")),
    ("Customer/Support", ("support", "customer success", "customer service", "csm", "onboarding specialist")),
]

def family(title, tags, cat):
    blob = (" " + title + " " + tags + " " + cat + " ").lower()
    for fam, kws in FAMILIES:
        if any(k in blob for k in kws):
            return fam
    return "Generalist"

# ---------------- main ----------------
def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--keyword", default="", help="comma-separated role keywords")
    ap.add_argument("--out", default="worldwide_remote_jobs.csv")
    ap.add_argument("--all", action="store_true", help="also include region-locked (RESTRICTED) roles")
    ap.add_argument("--region", default="", help="extra eligible region terms, comma-separated (add YOUR region)")
    ap.add_argument("--exclude", default="", help="comma-separated title terms to drop (query-level exclusions)")
    ap.add_argument("--insecure", action="store_true")
    ap.add_argument("--top", type=int, default=30)
    a = ap.parse_args()

    kws = [k.strip().lower() for k in a.keyword.split(",") if k.strip()]
    excl = [k.strip().lower() for k in a.exclude.split(",") if k.strip()]
    elig = list(ELIG_DEFAULT) + [t.strip().lower() for t in a.region.split(",") if t.strip()]
    server_kw = kws[0] if kws else ""

    rows = []
    sys.stderr.write("Fetching sources...\n")
    for name, fn in SOURCES:
        try:
            got = fn(a.insecure, server_kw)
            sys.stderr.write("  %-14s %4d jobs\n" % (name, len(got)))
            rows += got
        except Exception as e:
            sys.stderr.write("  %-14s FAILED: %s\n" % (name, e))

    def keep(r):
        t = r["title"].lower()
        if any(x in t for x in excl): return False
        if not kws: return True
        blob = (r["title"] + " " + r["tags"] + " " + r["category"]).lower()
        return any(k in blob for k in kws)

    seen, out = set(), []
    for r in rows:
        if not r["title"] or not r["url"] or not keep(r):
            continue
        key = (r["title"].lower(), r["company"].lower())
        if key in seen:
            continue
        seen.add(key)
        r["bucket"] = bucket(r["location"], elig, r.get("loc_reliable", True))
        r["cv_family"] = family(r["title"], r["tags"], r["category"])
        out.append(r)

    if not a.all:
        out = [r for r in out if r["bucket"] != "RESTRICTED"]

    order = {"WORLDWIDE": 0, "WORLDWIDE?": 1, "ELIGIBLE": 2, "RESTRICTED": 3}
    out.sort(key=lambda r: r["date"], reverse=True)
    out.sort(key=lambda r: order.get(r["bucket"], 9))

    cols = ["bucket", "title", "company", "location", "cv_family", "salary", "date", "source", "tags", "url"]
    with open(a.out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in out:
            w.writerow(r)

    counts = {}
    for r in out:
        counts[r["bucket"]] = counts.get(r["bucket"], 0) + 1
    print("\n=== %d roles kept ===" % len(out))
    print(" | ".join("%s: %d" % (b, counts.get(b, 0)) for b in ["WORLDWIDE", "WORLDWIDE?", "ELIGIBLE", "RESTRICTED"]))
    print("CSV -> %s\n" % a.out)
    print("TOP MATCHES (newest first):")
    for r in out[:a.top]:
        t = (r["title"][:48]).ljust(48)
        c = (r["company"][:22]).ljust(22)
        loc = (r["location"] or "-")[:18].ljust(18)
        print("[%-10s] %s %s %s %-16s %s" % (r["bucket"], t, c, loc, r["cv_family"], r["source"]))

if __name__ == "__main__":
    main()
