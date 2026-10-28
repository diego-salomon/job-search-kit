---
name: job-scan
description: Runs one round of the job search - runs the scanners, reads the boards in search/playbook.md, judges every plausible job against me/strategy.md, adds the good ones to the tracker and prepares their applications. Use when the user says "scan", "find me jobs", "run a round", or on a schedule. Never submits anything.
---

# Job scan

One round, start to finish. The output is a short list of jobs worth applying to, each with its application folder ready, and a chart the user approves before anything is sent.

## Inputs
`me/strategy.md`, `me/profile.md`, `search/playbook.md`, `search/portals.yml`, and the tracker (`tools/tracker.py`).

## The one rule
Do not judge a job by words in its title. Search broad, then read each plausible posting (the first paragraph and the requirements) and judge it with the four questions. Titles lie in both directions.

## Steps

1. **Run the scanners.**
   ```bash
   python3 tools/scan_portals.py --config search/portals.yml --out scans/portal_jobs.csv --max-age-days 14
   python3 tools/harvest_remote.py <the command in the playbook>
   ```
2. **Read the boards** in `search/playbook.md`, lane by lane, freshest first, within the last 14 days. If a browser tool is available, open the links; if not, use web search and fetch. Close every tab you open.
3. **Judge each plausible job with the four questions**, in this order:
   1. Level: does the role match the level in the strategy? Judge by the description, not the title.
   2. Pay: does the top of the posted or estimated range reach the floor? If no salary is posted, estimate it from public salary sites and say where the estimate came from.
   3. Hard gates: is there a must-have the user truly lacks (see "Known gaps" in the profile)? "Nice to have" is not a gate.
   4. Location: does it fit the location rules? Check for hidden "must reside in" lines in remote jobs.
   Also skip anything on the strategy's exclusion list and anything breaking a non-negotiable.
4. **Dedupe** each survivor against the tracker: `python3 tools/tracker.py find "Company" "Role"`. The same company with the same or almost the same title is the same job.
5. **Rank** the survivors: what the strategy puts first (for example fully remote), then pay, then fit. Recency breaks ties. Cap the shortlist at what the user said they can really send.
6. **Track** each shortlisted job:
   ```bash
   python3 tools/tracker.py add --company "..." --role "..." --link "<direct employer link>" --lane "..." --salary "..." --fit 4 --note "one line on why"
   ```
   Use `--status "Verify first"` when something needs checking by a human (unclear location, salary unknown).
   Always resolve links from aggregators to the employer's own posting.
7. **Prepare** each Queued job with `tailor-application`.
8. **Log** the round in `scans/log.md`, newest on top: date, boards read, how many postings read, what was kept and why, what was skipped and why, and any board that returned nothing. Low yield is useful information.
9. **Show the chart and stop.** One line per job: role, company, salary, what they ask for, link, and the folder. The user decides. "Go" means they want help submitting; see `tailor-application`.

## Never
- Submit an application, create an account, enter a password, solve a CAPTCHA, or pay for anything.
- Contact a recruiter or company without the user approving the exact message.
- Delete tracker rows or application folders.
