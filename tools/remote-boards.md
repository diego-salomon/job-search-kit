# Sources & field mappings

All endpoints are free, public JSON, no API key. The harvester fetches each in its own
`s_<name>(insecure, kw)` function, normalizes to a common row via `norm(...)`, then the
main loop keyword-filters, classifies (`bucket`), tags a CV family, de-dupes, and writes CSV.

| Source | Endpoint | Eligibility field | Reliable? | Notes |
|---|---|---|---|---|
| **Remotive** | `https://remotive.com/api/remote-jobs` | `candidate_required_location` ("Worldwide", "LATAM", "USA"…) | ✅ clean | Free endpoint returns only ~28 jobs total. Best single signal for worldwide/region. |
| **RemoteOK** | `https://remoteok.com/api` | `location` = company **HQ**, not eligibility | ⚠️ HQ only | First array item is a legal notice — skipped. US-heavy; HQ cities fall to RESTRICTED on purpose. |
| **Jobicy** | `https://jobicy.com/api/v2/remote-jobs?count=50` | `jobGeo` ("Anywhere", "USA", "EMEA"…) | ✅ clean | `count` caps at 50. |
| **Working Nomads** | `https://www.workingnomads.com/api/exposed_jobs/` | `location` ("Anywhere", region) | ✅-ish | Exposes ~40 recent roles. |
| **Himalayas** | `https://himalayas.app/jobs/api?limit=100` | `locationRestrictions` (array, e.g. ["Worldwide"]) | ✅ clean | Shape guarded with `.get`; returns ~20. |

## Classification (`bucket`)
1. location contains `worldwide` / `anywhere` / `global` → **WORLDWIDE**
2. location contains one of the user's **own** regions (passed via `--region`, e.g. `latam`, `europe`, `spain`) → **ELIGIBLE**
3. location is blank or just "remote" → **WORLDWIDE?** (verify the real listing)
4. anything else that names a place → **RESTRICTED** (hidden unless `--all`)

Precision-first by design: a named location is assumed to be a restriction, because on these
boards it almost always is. Better a short clean list than a flood of US-only false positives.

## CV-family tagging (`family`)
Keyword → family map (`FAMILIES` in the script): Operations, SEO & Content, Email & Lifecycle,
Growth & Performance, Ecommerce/Amazon, Data, Automation/AI, Engineering, Customer/Support,
else Generalist. Each hit's `cv_family` suggests which CV/resume version to apply with
(hand off to the `tailor-application` skill).

## Candidate boards to add later
- **We Work Remotely** — has many worldwide roles; blocks scripted JSON (403). Use the RSS feeds
  (`https://weworkremotely.com/remote-jobs.rss`); region is only loosely tagged per item.
- **Jobspresso**, **Remote.co**, **Pangian**, **WellFound** — worldwide-friendly, varying API access.
- Add each as an `s_<name>` function returning `norm(...)` rows, then append to `SOURCES`.
