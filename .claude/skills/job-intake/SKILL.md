---
name: job-intake
description: First step of the kit. Interviews the user about their career, constraints and goals, one question at a time, and writes me/profile.md, me/strategy.md and me/voice.md. Use when me/profile.md does not exist, when the user says "start", "set me up", "interview me", or when their situation changes (new target, new location, new salary floor).
---

# Job intake

Everything else in this kit reads three files. This skill writes them, by interviewing the user until there is nothing important left to guess.

- `me/profile.md`: facts about the person. Only true things. Anything in it can come up in an interview.
- `me/strategy.md`: what they are looking for and how the search decides.
- `me/voice.md`: how they write, so letters and answers sound like them.

The `me/` folder is in `.gitignore`. Tell the user that once, at the start: nothing they say here goes to GitHub.

## Start from what already exists

Before asking anything, ask for material, because it saves half the interview:
- their LinkedIn profile as a PDF (on LinkedIn: their profile, then More, then Save to PDF), or the text pasted in;
- their current CV in any format;
- optionally, two or three things they wrote themselves (emails, posts) for `voice.md`.

Read all of it. Fill the templates in `templates/` with what you can, mark every gap, and only then start asking. Never ask for something the documents already answer; confirm it in one line instead.

## How to interview

Ask one question at a time. With each question, give your recommended answer based on what you have read, so the user can just say "yes" when you are right. Push back when an answer is vague ("about 20 people" becomes "how many, exactly, on a normal week?") or when it contradicts something earlier. Numbers must be ones the user can defend out loud in an interview: straight figures, never invented, and labelled as estimates when they are estimates.

Keep going until every item below is answered or the user says to skip it. Then show a short summary and ask what is wrong before writing the files.

### 1. Facts (goes to profile.md)
- Name, city, email, phone, LinkedIn, portfolio. Never ask for ID numbers, date of birth or bank details: forms that need them are filled by the user.
- Work authorization: which countries they can work in without sponsorship, citizenships, visas.
- Languages and real level.
- Every role, most recent first: title, company, dates, team size, what they actually owned, two to four results with numbers. Ask what was menial and what was real; the CV leads with the real part.
- Education and training that matters.
- Tools they really use, and how deeply. Never list a tool they have only heard of.
- Side projects, awards, anything that shows how they work.
- Known gaps: certifications, degrees, tools or experience that roles often ask for and they lack. These stay private; they exist so nothing gets faked.
- Facts that must never drift (a title that was not theirs, a credit that was shared). Write them in a "locked facts" list.

### 2. The search (goes to strategy.md)
- Target roles, in their words, and the level. Test the level against evidence: have they been rejected or interviewed at that level? A level that gets no interviews is a finding, not a failure.
- Lanes: two to five groups of roles or industries to search, with a rough weight for each. For a career change, ask which lane is the same work in a new place (easier) and which is truly new (harder).
- Location rules: cities, remote (which countries or regions it must cover), hybrid, relocation.
- Salary: the floor and the target. The kit judges a job by the top of its range: if the top of the band is at or above the floor, it qualifies.
- Non-negotiables (no 24/7 on-call, no travel, no agencies, and so on).
- Hard gates: requirements that mean "skip" (for example, a must-have programming language they do not know). "Nice to have" is never a gate.
- Companies to exclude, starting with ex-employers they do not want to go back to.
- Application language: which language the CV and letters go out in.
- Cadence: how many scan rounds a week, how many applications they can really send.
- Where the tracker lives (default `me/tracker.csv`) and whether they want an email or chat summary after each scan.

### 3. Voice (goes to voice.md)
From their own writing, note sentence length, words they use, words they would never use, how formal they are, how they open and close. Add the kit's defaults: no em dashes, no corporate filler (leverage, passionate, dynamic, seamless, excited to apply), concrete over abstract, first person.

## Write the files

Use `templates/profile.md`, `templates/strategy.md` and `templates/voice.md` as the structure. Keep the user's words where they are good. Then tell them the next steps, in order:

1. `base-cv` to build the master CV from the profile.
2. `linkedin-tune` to align LinkedIn with it.
3. `search-setup` to turn the strategy into searches.
4. `job-scan` for the first round.

Run this skill again whenever something changes. Update the files; do not start over.
