---
name: base-cv
description: Builds the master CV (one, or two for two clearly different lanes) from me/profile.md and saves it to me/cv/ as Markdown and PDF. Use after job-intake, or when the user says "build my CV", "rewrite my CV", "make a base CV".
---

# Base CV

The base CV is the master. Every application gets a tailored copy of it; the base itself only changes when the facts change.

## Inputs
`me/profile.md`, `me/strategy.md`, `me/voice.md`. If any is missing, run `job-intake` first.

## Decide how many
One base CV is the default. Make a second only when two lanes need a different story (for example, operations roles versus creative roles), and name each after its lane: `me/cv/operations/cv.md`, `me/cv/creative/cv.md`.

## Write it
Use `templates/cv.md` as the shape. One page when the career allows it, two at most.

- **Header:** name, city, email, phone, LinkedIn, portfolio. Under the name, a short tagline of two or three phrases that name the role family, not adjectives.
- **Summary:** three or four sentences in the user's voice. What they did, at what scale, what they are known for. No buzzwords, no "results-driven professional".
- **Experience:** most recent first. Three to five bullets per role. Each bullet is an action and a result: what they did, how big it was, what changed. Use the numbers from the profile exactly as written there. Lead with the most impressive true angle; put the menial parts last or leave them out.
- **Other experience, education, skills, languages.** Skills only list tools the profile says they really use.

Rules that never bend:
- Every claim comes from `me/profile.md`. If something would make the CV stronger but is not in the profile, ask the user; do not write it.
- Respect the "locked facts" list.
- No em dashes, no tables or columns (applicant tracking systems read them badly), plain fonts.

## Render and check
```bash
python3 tools/make_cv.py me/cv/*
```
Open the PDF and check it fits the page. Then read it once as a recruiter would, in ten seconds: is the target role obvious from the top third? If not, fix the tagline and summary.

Show the user the result and get their approval. Once approved, the base is frozen: `tailor-application` copies it and changes only what each posting needs.
