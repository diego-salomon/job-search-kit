---
name: linkedin-tune
description: Rewrites the user's LinkedIn profile so it tells the same story as their base CV, and gives a checklist of LinkedIn settings that help recruiters find them. Saves the text to me/linkedin.md. Use after base-cv, or when the user says "fix my LinkedIn", "rewrite my LinkedIn", "tune my profile".
---

# LinkedIn tune

Recruiters read LinkedIn before the CV, and they search it by title and keywords. The goal is one story told the same way in both places.

## Inputs
`me/profile.md`, `me/strategy.md`, `me/voice.md`, the base CV in `me/cv/`, and the current LinkedIn text (the PDF from intake, or ask the user to paste it).

## What to write

Save everything to `me/linkedin.md`, section by section, so the user can paste it.

- **Headline** (220 characters max). Lead with the title they want to be found for, then two or three real specialties. Recruiters search titles; "Operations Specialist" is found, "Problem solver" is not.
- **About.** Three short paragraphs in the user's voice: what they do and at what scale, one concrete story or result, and what they are into now or looking for. No lists of adjectives. First person.
- **Experience.** The same bullets as the base CV, a little more conversational. Same numbers, same locked facts.
- **Skills.** The five that matter most for the target roles, pinned first. Only real ones.
- **Featured.** Two or three links that prove the work: a portfolio, a project, press.
- **Languages and certifications**, matching the profile.

## Settings checklist
Give the user these steps to do themselves, in the LinkedIn app or website:
1. Open to work: on, visible to recruiters only (unless they are fine with the public banner), with their target titles, locations and remote preference from the strategy.
2. Job alerts that match the searches in `search/playbook.md` (created by `search-setup`).
3. Custom profile URL with their name.
4. Location set to where they want to work, if they are open to that market.

## Check
Read the headline and About next to the CV summary. If a recruiter saw both, would they think it is the same person going for the same role? If not, fix whichever one is off.

The user edits LinkedIn themselves. Never log in to their account or change it for them unless they ask you to and are watching.
