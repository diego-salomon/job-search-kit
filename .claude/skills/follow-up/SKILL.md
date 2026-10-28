---
name: follow-up
description: Keeps the pipeline moving after applications go out - follow-up emails when they are due, thank-you notes after interviews, interview prep, and a weekly review of what is working. Use when the user says "follow up", "what's due", "weekly review", "prep me for the interview", or "they replied".
---

# Follow-up

## What's due
```bash
python3 tools/tracker.py due      # applied 7+ days ago, no answer yet
python3 tools/tracker.py stats
```
For each due row, draft one short follow-up in the user's voice (`me/voice.md`): one line on the role, one line of real interest, one clear ask. Never more than one follow-up per application, never for a rejection, and never sent without the user approving the exact text.

If the user's email is connected, you can also sweep it for replies: rejections become `Rejected` in the tracker, interview invitations become `Interview`. Ask before marking anything as read or moving mail.

## Interviews
When a row moves to `Interview`, build a prep sheet in the application folder (`prep.md`):
- what the company does, how it makes money, recent news;
- the posting's requirements, each matched to a story from `me/profile.md`;
- a 60-second introduction;
- five stories in situation, action, result form, all true and with real numbers;
- the hard questions this role and this profile invite (gaps, career change, reasons for leaving), with honest answers;
- questions to ask them.
Offer a mock interview: ask one question at a time, then give direct feedback.
Within 24 hours after the interview, draft a short thank-you note.

## Offers
Research the pay range for that role, level, country and company type, and cite the sources. Suggest asking for their budget before naming a number, and a band whose floor is the user's floor. Before accepting, run a hard look at the offer against `me/strategy.md`: what does it give up?

## Weekly review
Once a week, read the tracker, `scans/log.md` and any replies, and answer plainly:
- How many applications went out, and how many turned into interviews?
- Which lanes and boards produce interviews, and which only produce applications?
- Is the level right? Many applications with no interviews at a level is evidence.
- One or two concrete changes for next week, written into `me/strategy.md` or `search/playbook.md` if the user agrees.
