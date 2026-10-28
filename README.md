# Job search kit

A tool that automates as much of a job search as possible and keeps you on top of every posting that shows up. It gives anyone looking for work a full structure, from onboarding to follow-ups, run with [Claude Code](https://claude.com/claude-code) or Codex.

1. **Onboarding.** An interview, one question at a time, that reads your LinkedIn PDF and CV and writes your profile, your search strategy and your writing voice.
2. **Base CV**, built from the profile, as a plain PDF that applicant tracking systems can read.
3. **LinkedIn**, rewritten to match the CV, plus the settings that help recruiters find you.
4. **Searches**: a company-portal scanner, a remote-job harvester and a playbook of job board links for each kind of role.
5. **Scan rounds** that read every new posting and judge it by level, pay, hard requirements and location.
6. **One folder per job**: tailored CV, cover letter, form answers and the saved posting.
7. **Tracker and follow-ups**: every job in one CSV, chasers when they're due, interview prep and a weekly review.

It prepares everything and waits. Submitting, accounts and passwords stay with you.

## Getting started

You need Python 3.9+, Node 18+ and Claude Code or Codex.

```bash
git clone https://github.com/diego-salomon/job-search-kit.git
cd job-search-kit
python3 -m pip install -r requirements.txt
claude          # or: codex
```

Say "start". Have your LinkedIn PDF (your profile, More, Save to PDF) and your CV at hand.

## What's inside

```
.claude/skills/   one skill per step (plain Markdown, readable by any agent)
tools/
  scan_portals.py   job APIs of Greenhouse, Ashby, Lever, Workable, Recruitee, SmartRecruiters
  harvest_remote.py remote boards, sorted into worldwide, eligible for your region, unknown and region-locked
  ats-score.mjs     requirement words from the posting that your CV never mentions
  make_cv.py        cv.md and cover-letter.md to PDF
  tracker.py        the tracker, a CSV you can open in Excel or Sheets
templates/        profile, strategy, voice, CV, cover letter, playbook
search/           search config
me/  applications/  scans/   your data. Ignored by git.
```

The tools also work on their own:

```bash
python3 tools/harvest_remote.py --keyword "operations,coordinator" --region "europe" --out scans/remote.csv
python3 tools/scan_portals.py --probe gitlab,zapier
node tools/ats-score.mjs applications/acme/posting.txt applications/acme/cv.md
python3 tools/tracker.py add --company Acme --role "Operations Specialist" --link https://...
python3 tools/tracker.py due
```

## Good to know

- Search broad and judge by reading the posting, not the title.
- A job qualifies when the top of its pay range reaches your floor.
- Most "remote" jobs on free boards are locked to one country; the harvester treats any named place as a restriction.
- Apply within days. Postings fill fast.
- Companies on Workday or SuccessFactors can't be scanned through a public API; keep them as links in the playbook.

## Privacy

Your data lives in `me/`, `applications/` and `scans/`, which git ignores. Check `git status` before pushing a fork.

MIT license.
