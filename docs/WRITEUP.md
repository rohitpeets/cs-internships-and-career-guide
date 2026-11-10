# Things I Wish I Knew: CS Edition — design notes

Things I Wish I Knew: CS Edition is a job board and set of guides for computer science and computer engineering students. I started it for my friends and classmates at my university (about 300 CS and CE students), and it's open to any student. It lists internships, new-grad roles and freshman/sophomore programs, pulled straight from companies' own job boards and refreshed every day. I built it because the boards students already use are either paid, cluttered with roles they can't apply to, or silent on the question international students care about most: will this employer work with my visa status?

## How it works

Every company publishes its openings through a job system: Greenhouse, Lever, Ashby, SmartRecruiters, Workday, Oracle, or its own (Amazon, and Netflix on Eightfold). Most of these have a public JSON endpoint behind the career page. The board keeps a list of 965 company boards (`data/companies.yaml`) and asks each one what's open.

The work is split between two machines:

| Runs on | Sources | Why |
|---|---|---|
| GitHub Actions, daily | Greenhouse, Lever, Ashby, SmartRecruiters, Amazon, Eightfold (287 boards) | Fast, small JSON feeds; fits easily in a free run |
| My laptop, nightly | Workday, Oracle (678 boards) | Slower: several searches plus one request per posting, which doesn't fit comfortably in a free cloud run |

The laptop writes exactly one file, `data/local.json`, and pushes it. The Action writes everything else and merges the laptop's file in. Because the two never edit the same file, their pushes can't conflict. If the laptop is off for three days, its rows stay on the board marked ⚠ instead of disappearing.

On the first full run the cloud half found 732 postings and the laptop half found 2,790, from 902 boards with 3 failures. After the CS/CE-only, U.S.-only filters (below), about 1,500 to 1,700 roles are open on a given day; the README shows the live count.

## Decisions and trade-offs

**Company feeds instead of community lists.** The biggest open internship list on GitHub has no license, so its data isn't free to copy. Reading companies' own feeds avoids that and gives full job descriptions, which the tags need. The cost is coverage: measured against a larger aggregator's data, these five job systems reach about 54% of postings, and 58% of the postings that fit a CS student best (versus 53% of the weakest fits), so the gaps aren't concentrated in the roles that matter most.

**Three-state tags with evidence.** Each posting gets sponsorship (yes / no / not mentioned), citizenship-required and clearance-required tags. "Not mentioned" is the default; a tag is set only on an explicit sentence, and that sentence is saved with the posting so anyone can check it. The sponsorship rule is negation-aware ("unable to sponsor" is a no), and a sentence about export licenses is ignored, because "without sponsorship for an export license" has nothing to do with visas. A wrong "sponsors" tag costs an international student the most, so the classifier errs toward saying nothing.

**Closing jobs without guessing.** A posting is removed only after it is missing from its company's feed on two different days (two runs on one day count once). If a whole board returns "not found" (usually a renamed board), comes back suddenly empty, or hits a page cap, its postings are marked ⚠ instead of closed, and the run log lists the board to fix. ⚠ rows from any source leave after seven days. Postings added by hand are link-checked instead, and links that can't be verified are marked ⚠ for up to seven days before they're removed.

**Failing loudly.** Every adapter checks the shape of the response. If a job system changes its format, the run fails instead of quietly reporting zero jobs. A run where more than 30% of boards fail writes nothing. A second guard refuses to publish if open postings fall below half of the highest count in the last seven commits, so a slow slide can't get past it either. An intended drop, like a stricter filter, is committed with `[reset-baseline]` in the message.

**Filtering for the audience.** A title has to look like an internship or entry-level role and name CS or computer-engineering work (an allow-list: software, data, IT, security, embedded, hardware validation, robotics and so on). "Engineer" alone isn't enough. Early runs let through civil, mechanical and geotechnical engineering, marketing internships and non-US programs. Each of those became a test case, so the filter can't quietly regress. I also checked the filter against about 2,100 postings I had screened earlier for my own applications: of the ones I'd rated a strong fit, it was dropping 62. The real misses (robotics, BS/MS roles, IT operations) were fixed, and the 38 still dropped are sales, marketing or mechanical roles with "AI" in the title.

**Auditing the tags.** I checked every 🛂✅ tag by hand. 4 of 17 were wrong: "No relocation assistance or visa sponsorship is available" read as a yes, and "F-1 students on CPT are eligible" counted as sponsorship. Now any "no" sentence wins, CPT/OPT never counts, and "for select candidates" isn't treated as an offer. Generic "comply with export control laws" lines no longer set 🇺🇸. Every case from the audit is a test.

**Read-only for students.** Only maintainers can change the board. Students suggest postings to an ACM officer, who adds them to `data/manual.yaml`. With 300 readers, an open write path would mean spam and broken tables.


**Treating feed text as untrusted.** Titles, locations and links come from other companies' systems and end up on a public page. Every cell is HTML- and markdown-escaped, and a link is used only if it's a plain http(s) URL, so a posting titled `Intern](https://phishing.example)` can't plant a link. The workflow's actions are pinned to commit SHAs and dependencies to exact versions.

**F-1 students.** 🛂❌ (no sponsorship later) is kept separate from 🚫 (the posting says it won't take CPT/OPT), because only the second one closes the role to an F-1 student right now. Government and national-lab titles get 🏛 as a "check this" flag even when the posting doesn't say it's U.S.-only.


## Measured accuracy

After the fixes above, I hand-checked 200 random rows from the live board (no descriptions, judged from title, location and the saved evidence):

| Check | Errors | Rate |
|---|---|---|
| Is it a CS/CE role? | 10 / 200 | 5% |
| Is it in the U.S.? | 4 / 200 | 2% |
| Right level (not grad-only, not an expired term)? | 3 / 200 | 1.5% |
| Right section? | 1 / 200 | 0.5% |
| Tag matches its evidence sentence | 2 / 55 tagged rows | 4% |
| Posting date in the future | 0 / 74 dated rows | 0% |

Every wrong row in that sample became a test case and a rule fix (bare "QA", "security intern" and "data center electrical" no longer count as CS; country codes like "ESP" and "BRA" are non-U.S.; "2026 Summer" roles listed after the summer started are dropped; "clearance is not required" no longer sets 🔒). The numbers above are from before those fixes, so they're an upper bound; a fresh sample is the next check.

## What I'd do next

- Hand-label about 150 postings and report precision and recall for each tag, especially how often the board wrongly says a company sponsors.
- Add adapters for big companies that run their own career sites (Google, Microsoft, Amazon, Meta, Apple). The README lists which must-have companies aren't covered yet.
- Add Louisiana and Gulf Coast employers.
- A small searchable page on GitHub Pages, with each student's "applied" checkmarks saved in their browser.
- Weekly numbers in the README: postings tracked, added and closed.

## Stack

Python 3.12, `requests`, PyYAML, JSON Schema and pytest; GitHub Actions for the daily run; Windows Task Scheduler and PowerShell for the laptop job.
