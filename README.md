# Job search kit

In 2026 the department I worked in for seven years closed, and I had to look for a job for the first time in a long while. I treated it like the operations work I know: a process with steps, rules and a tracker, run with Claude. This is that system, emptied of my data, so anyone can use it.

You open this folder with [Claude Code](https://claude.com/claude-code) (or Codex) and it walks you through the whole search:

1. **An interview first.** It asks about your career one question at a time, pushes back on vague answers, and reads your LinkedIn PDF and old CV so it doesn't ask what it already knows. Out of that come three private files: your profile (only true facts), your strategy (what you want, your salary floor, what's a dealbreaker) and your writing voice.
2. **A base CV** built from the profile, rendered to a plain PDF that applicant tracking systems can read.
3. **Your LinkedIn**, rewritten to tell the same story, plus the settings that help recruiters find you.
4. **Your searches**: a company-portal scanner, a remote-job harvester and a playbook of job board links for each kind of role you're after.
5. **Scan rounds.** It runs the scanners, reads the boards, and judges every job with four questions (level, pay, hard requirements, location) instead of trusting titles. The good ones go into the tracker.
6. **One folder per job**: a CV adapted to that posting, a cover letter if the form takes one, answers to the form's questions, and the posting saved before it disappears.
7. **Follow-ups**: one chaser after seven days, interview prep, thank-you notes and a weekly look at what's working.

It never applies for you. It prepares everything, shows you a list, and waits. Accounts, passwords and the final submit button are always yours.

## Getting started

You need Python 3.9 or newer, Node 18 or newer, and Claude Code or Codex.

```bash
git clone https://github.com/diego-salomon/job-search-kit.git
cd job-search-kit
python3 -m pip install -r requirements.txt
claude          # or: codex
```

Then say "start". If there's no profile yet, it begins the interview. Have your LinkedIn PDF (your profile, More, Save to PDF) and your CV at hand.

## What's inside

```
.claude/skills/     the seven steps above, one skill each (plain Markdown, readable by any agent)
tools/
  scan_portals.py   reads job APIs of Greenhouse, Ashby, Lever, Workable, Recruitee, SmartRecruiters
  harvest_remote.py remote boards (Remotive, RemoteOK, Jobicy, Working Nomads, Himalayas), sorted
                    into worldwide, eligible for your region, unknown, and region-locked
  ats-score.mjs     which of the posting's requirement words your CV never mentions
  make_cv.py        cv.md and cover-letter.md to clean PDFs
  tracker.py        the applications tracker, as a CSV you can open in Excel or Sheets
templates/          profile, strategy, voice, CV, cover letter, playbook
search/             your search config (portals.example.yml to start)
me/                 your private files. Ignored by git.
applications/       one folder per job. Ignored by git.
scans/              scanner output and the round log. Ignored by git.
```

The tools also work on their own:

```bash
python3 tools/harvest_remote.py --keyword "operations,coordinator" --region "europe,spain" --out scans/remote.csv
python3 tools/scan_portals.py --probe gitlab,zapier          # which ATS does a company use?
node tools/ats-score.mjs applications/acme/posting.txt applications/acme/cv.md
python3 tools/tracker.py add --company Acme --role "Operations Specialist" --link https://...
python3 tools/tracker.py due                                   # follow-ups due
```

## Things I learned running it

- Don't filter by words in the title. My first version blocked "engineer" and hid a process-improvement job that fit me well. Search broad, read the posting, then decide.
- Judge pay by the top of the range. A 45 to 55k band is worth applying to if your floor is 50k.
- Most "remote" jobs on the free boards are locked to one country. The harvester assumes a named place is a restriction, so the list is short but real.
- Apply fast. I learned the hard way that a posting two or three days old can already be filled.
- Many applications and no interviews at one level is data. When that happened to me, I changed the level I was aiming at, not the CV font.
- Big companies on Workday or SuccessFactors can't be scanned through a public API. Keep them in the playbook as links.

## Privacy

Everything about you lives in `me/`, `applications/` and `scans/`, and `.gitignore` keeps all three out of any commit. If you fork this to share your own version, check `git status` before you push.

Code comments and docs are in English. The kit writes in whatever language your applications need.
