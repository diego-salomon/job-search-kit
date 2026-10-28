---
name: search-setup
description: Turns me/strategy.md into the actual searches - search/portals.yml for the company-portal scanner, keywords for the remote-board harvester, and search/playbook.md with ready-to-open job board links per lane. Use after job-intake, or when the strategy changes ("add a lane", "search in Germany too", "stop showing me X").
---

# Search setup

The scans need to know where to look and what to keep. This skill writes that down once, so every round runs the same way.

## Inputs
`me/strategy.md` (lanes, levels, locations, salary floor, gates, exclusions) and `me/profile.md`.

## 1. Company portals (`search/portals.yml`)
Start from `search/portals.example.yml`.

- `location_filter.allow`: every place the strategy accepts, in every language the postings use ("Remote", "Spain", "España", "EMEA"...).
- `title_filter.positive`: the role words of every lane. Keep them broad; the scan reads each posting anyway.
- `title_filter.negative`: only words that are always wrong for this person (seniority they will not take, unrelated functions). Be careful: blocking "engineer" also hides "process engineer" roles that might fit.
- `tracked_companies`: companies the user wants to watch. For each one, find which applicant tracking system it uses:
  ```bash
  python3 tools/scan_portals.py --probe company-slug
  ```
  Only enable companies that answer with jobs. Large enterprises often use Workday or SuccessFactors, which the scanner cannot read; put those in the playbook as links instead.

## 2. Remote boards
Pick the keywords and regions for the harvester from the strategy and write the exact command into the playbook:
```bash
python3 tools/harvest_remote.py --keyword "operations,coordinator,..." --region "europe,spain" --exclude "intern,director" --out scans/remote_latest.csv
```

## 3. The playbook (`search/playbook.md`)
Start from `templates/playbook.md`. For each lane, list:
- LinkedIn searches as links, with the filters in the URL: last 14 days (`f_TPR=r1209600`), the right seniority (`f_E=3%2C4` is Associate and Mid-Senior), remote when needed (`f_WT=2`), sorted by date (`sortBy=DD`), one link per location.
- The job boards that matter for that lane and country (general boards, industry boards, startup boards, impact boards), as direct search links.
- Recruitment agencies that place this kind of role, if the lane is a like-for-like move.
- A watchlist of specific companies to check every round.

Finish with the four questions every job is judged by (they come from the strategy) and the cadence.

## Check
Run both scanners once and look at the output with the user:
```bash
python3 tools/scan_portals.py --config search/portals.yml --out scans/portal_jobs.csv --max-age-days 14
python3 tools/harvest_remote.py ... (the command from the playbook)
```
If they return nothing useful, widen the keywords before blaming the market. If they return a flood, add exclusions. Then hand over to `job-scan`.
