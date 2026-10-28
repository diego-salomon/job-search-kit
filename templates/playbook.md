# Scan playbook

> Where each round looks, lane by lane. Written by `search-setup`; followed by `job-scan`.

## Scanners
```bash
python3 tools/scan_portals.py --config search/portals.yml --out scans/portal_jobs.csv --max-age-days 14
python3 tools/harvest_remote.py --keyword "..." --region "..." --exclude "..." --out scans/remote_latest.csv
```

## Lane 1: [name]
- LinkedIn, [location]: [link with f_TPR=r1209600, f_E, f_WT, sortBy=DD]
- [Board]: [search link]
- Agencies: [links]

## Lane 2: [name]
- ...

## Watchlist (every round, any age)
- [Company]: [careers link]

## Judge every job with the four questions in me/strategy.md.
Shortlist cap per round: [n]. Log the round in scans/log.md.
