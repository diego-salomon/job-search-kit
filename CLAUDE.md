# Job search kit

This folder is a job search run with an AI assistant. The skills in `.claude/skills/` do the work, in this order:

1. `job-intake`: interview the user and write `me/profile.md`, `me/strategy.md`, `me/voice.md`.
2. `base-cv`: build the master CV in `me/cv/`.
3. `linkedin-tune`: align LinkedIn with the CV.
4. `search-setup`: write `search/portals.yml` and `search/playbook.md`.
5. `job-scan`: one round of searching, judging and preparing applications.
6. `tailor-application`: one posting into one ready folder in `applications/`.
7. `follow-up`: follow-ups, interview prep, weekly review.

## At the start of every session
- If `me/profile.md` does not exist, the user is new. Explain the steps above in three lines and start `job-intake`.
- Otherwise read `me/profile.md`, `me/strategy.md` and `me/voice.md` before doing anything, and run `python3 tools/tracker.py stats`.

## Rules
- `me/profile.md` is the only source of facts about the user. Never invent experience, tools, numbers, titles or credits. If something is missing, ask.
- Write as the user, using `me/voice.md`. No em dashes, no corporate filler.
- Never submit an application, create accounts, type passwords or ID numbers, solve CAPTCHAs, pay, or send a message to anyone without the user's explicit yes for that exact action.
- Never move anything from `me/`, `applications/` or `scans/` into a commit. Those folders are private.
