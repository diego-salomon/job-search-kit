---
name: tailor-application
description: Turns one job posting into a ready application folder - tailored CV, cover letter if the form takes one, answers to the form's questions, the posting link - and a tracker row. Helps submit only after the user says "go". Use when the user shares a posting (link or text), says "tailor for [company]", "apply to this", or after job-scan.
---

# Tailor application

One posting in, one folder out: `applications/<company>-<role>/`.

## Inputs
The posting (link or text), `me/profile.md`, `me/strategy.md`, `me/voice.md`, the base CV in `me/cv/`, the tracker.

## 1. Qualify first
- Resolve aggregator links (LinkedIn, Indeed and similar) to the employer's own posting. Flag a dead or unverifiable posting.
- Give a fit score from 1 to 5 against the strategy (level, pay by the top of the band, gates, location, non-negotiables). If it is 2 or less, or a hard gate is clearly missing, say so in one sentence and ask before building anything.
- Check the tracker for a duplicate.

## 2. The folder
```
applications/<company>-<role>/
  posting.txt        the full text of the posting, saved now (postings disappear)
  link.txt           the direct employer URL
  cv.md / CV.pdf
  cover-letter.md / Cover-Letter.pdf    only if the form has somewhere to put it
  answers.md         only if the form asks questions
```

## 3. The CV (change only what the posting needs)
Copy the right base CV (choose by what the role is, not the company), then:
1. Tagline: swap in the posting's exact title if it is true of the user.
2. Summary: weave in the posting's words where they are true. Never address the posting directly.
3. Bullets: put the most relevant first; reword two to four to use the posting's vocabulary naturally.
4. Skills: mirror the posting's wording for tools the user really uses. Never add a tool they don't.
Everything else stays as in the base. Every claim must be in `me/profile.md`; respect the locked facts.

Check keyword coverage, then render:
```bash
node tools/ats-score.mjs applications/<folder>/posting.txt applications/<folder>/cv.md
python3 tools/make_cv.py applications/<folder>
```
The score shows which requirement words the CV never mentions. Add the ones that are true; leave the rest. It measures keyword coverage only, not fit.

## 4. The cover letter
Write one only if the application has a place for it. Use `templates/cover-letter.md` for the layout.
- 200 to 250 words. Fresh every time; two letters never share structure or sentences.
- Paragraph 1 opens on the company: something specific and true they do or stand for, found by reading their site, and why it matters to the user. Then the role, framed as what they would bring.
- Paragraph 2: two or three concrete examples from the profile that match the job. Do not copy the CV.
- Paragraph 3: the softer things the posting wants (pace, ownership, ambiguity, mission), shown with other parts of their life, and a last sentence about what they would build there.
- Greeting with the hiring manager's name if you can find it, otherwise "Dear [Company] team". Sign off plainly.
- Voice from `me/voice.md`. No em dashes, no "I am writing to apply", no "passionate", "leverage", "excited to apply", "dynamic", "seamless". Gaps, if mentioned at all, are framed as direction, never apology.
- Self-check: could this first sentence belong to another company's letter? Would the user say it out loud? If either answer is wrong, rewrite.

## 5. Form answers
Short and true. Factual questions (work authorization, notice period, salary, languages) come straight from the profile; never guess a fact. Open questions get 80 to 150 words in the user's voice, with something personal in them, not a CV paste. Respect character limits and give the count. Salary: a band whose bottom is at or above the floor, researched for the role, unless the form forces one number.

## 6. Track it
```bash
python3 tools/tracker.py add --company "..." --role "..." --link "..." --fit N --note "Fit N/5. one line"
```

## 7. Submitting, only after "go"
Show the user the folder and a one-line summary per job. Only when they say "go" for a job:
- If a browser tool is available, open the posting, fill the fields from the profile and the answers, upload the PDFs, and stop at the final submit button for the user to press. If uploads are not possible, fill everything else and tell them which file to attach.
- Account creation, passwords, ID numbers, CAPTCHAs and payments are always the user's.
- After they confirm it went through: `python3 tools/tracker.py set "Company" "Role" Applied`. That also sets a follow-up date seven days later.
