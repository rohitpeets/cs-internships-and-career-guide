# Things I Wish I Knew: CS Edition — original design

> This is the original plan. Parts not built yet are marked *(planned)*. [WRITEUP.md](WRITEUP.md) describes what's built and what was measured.

A public GitHub repo that lists internships, new-grad roles and early-career programs for computer science and computer engineering students, refreshed daily. Built and owned by Rohitpreet Singh as a portfolio project. Only the maintainers (Rohit and the ACM officers) can change it; everyone else has read access.

## 1. Goals and constraints

| | |
|---|---|
| Audience | Originally about 300 students at my university, mostly CS, some computer engineering, from freshmen to seniors |
| Content | Three sections: Summer internships, New-grad roles, Early programs for freshmen and sophomores, plus a "New this week" section at the top |
| Refresh | Daily (scheduled GitHub Action), plus an immediate run when a maintainer adds postings by hand |
| Freshness | Postings confirmed closed twice in a row are removed; postings that can't be verified are flagged ⚠ instead of removed |
| Access | Maintainers (Rohit + ACM officers) write; everyone else reads. No student submissions through GitHub |
| Applied tracking | Not in v1; students use their own tools (see section 6) |
| Visibility | Public repo |
| Budget | Free: public repos get free GitHub Actions minutes on standard runners and free GitHub Pages |
| Non-goal | Matching the coverage of paid aggregators or of other boards |

**Positioning.** The README says plainly that this board isn't the most complete one, and links other public boards for breadth (links only; no data is copied from them). Its value is:
- local and Gulf Coast companies the big lists miss
- an early-programs section for freshmen and sophomores
- work-authorization tags students can trust

## 2. Data sources

| Source | What it gives | Notes |
|---|---|---|
| **Company job boards** in `companies.yaml` (955 boards: 523 Workday, 158 Greenhouse, 153 Oracle, 53 SmartRecruiters, 36 Ashby, 32 Lever) | Every open role at each company, with full descriptions | Each company's own public board feed. The list was built from the apply links of Rohit's Nov 5 scan (company name and its own board address only). Coverage check against that scan: Greenhouse + Lever + Ashby + Workday reach about 44% of postings and 42% of companies |
| **More ATS feeds:** Workable, Recruitee, Breezy HR, HireHive, Manatal | Startups and small companies, especially YC companies | Each has a documented public JSON endpoint per company; same adapter pattern as Greenhouse |
| **YC company pass** (`scripts/find_boards.py`, monthly) | Y Combinator startups | YC's own job site has no public API and needs a login, so it isn't used. Instead, YC company names are checked against Ashby, Greenhouse, Lever and Workable; boards that exist are added to `companies.yaml` |
| **Hacker News "Who is hiring"** (`scripts/adapters/hn.py`, monthly) | Startup roles posted in the monthly thread | Official HN API / Algolia HN search API; only top-level comments mentioning intern, new grad or similar; each becomes a row linking to its HN comment | *(planned)*
| **Big-company adapters** (`scripts/adapters/`) | Meta, Microsoft, Amazon, Google, Netflix, Qualcomm, Cisco and similar companies on their own career sites | One small adapter per company, using its public job-search endpoint. Brings coverage to an estimated 60–65% of postings, including the names students search for first |
| Public ATS job feeds for a hand-picked company list (`companies.yaml`) | Companies the lists miss: Gulf Coast energy, local employers, semiconductor and instrumentation firms | Greenhouse, Lever and Ashby have public JSON job-board endpoints. Workday has a per-tenant job-search endpoint, but it is undocumented, so use it sparingly. Send a descriptive User-Agent with a contact email, and keep to about 1 request per second per host. |
| Maintainer additions (`manual.yaml`) | One-off postings a maintainer finds or a student mentions to an officer | Added by a maintainer, committed directly, picked up by the next run |

**No third-party lists as a data source.** The main community list (SimplifyJobs) has no license, so its data isn't free to copy. It is linked from the README, not ingested. If a list's maintainers later grant permission, it can be added as one more source.

**Coverage, measured against the 5,375 screened postings of the Nov 5 scan:**

| Sources | Postings covered | Share |
|---|---|---|
| Workday, Greenhouse, Lever, Ashby, SmartRecruiters, Workable and other v1 ATS feeds | 2,571 | 47.8% |
| + Oracle | 3,025 | 56.3% |
| + big-company adapters (Meta, Microsoft, Amazon, Qualcomm, Cisco, Google, Netflix) | 3,133 | 58.3% | *(planned)*
| **+ Eightfold and ADP adapters (v1 final)** | **3,478** | **64.7%** | *(planned)*

**v1 final, by quality and lane:** best fits (4.5+) 72%; top 1,900 queue 70% (SWE 70%, AI/ML 70%, Embedded 80%, Business 67%); 1,098 of 1,726 companies. Coverage is higher for strong postings than weak ones, so the gaps are not concentrated in the important roles.

**Must-have companies check (monthly):** `data/must_have.yaml` lists ~50 well-known CS internship employers. A monthly run confirms each one has a working source; any that don't are flagged in the run log for a maintainer to add an adapter or a `manual.yaml` row. *(planned)*

Hacker News and the YC company pass add startup roles that weren't in that scan at all, so they aren't counted above.

**Largest remaining gaps** (candidates for later adapters): Paylocity 161 (3.0%), Dayforce 122 (2.3%), Taleo 78, BambooHR 55, JazzHR 45, Rippling 40, iCIMS 25, and about 1,400 postings spread over hundreds of companies' own career sites. Until then, maintainers add important ones by hand in `manual.yaml`.

**Not used:** LinkedIn, Indeed, Handshake and Wellfound (no public API; terms forbid scraping). They are linked from the README only.

**Not used:** scraping job aggregators whose terms forbid automated access.

## 3. Repo structure

```
cs-internships-and-career-guide/
├── README.md                     front page (generated): New this week, counts, legend, links to the tables
├── INTERNSHIPS.md                generated table
├── NEW_GRAD.md                   generated table
├── EARLY.md                      generated table
├── LICENSE
├── requirements.txt
├── data/
│   ├── postings.json             source of truth: company, role, link, section, tags,
│   │                             tag_evidence, status (open | uncertain), closed_strikes,
│   │                             uncertain_since, first_seen, last_checked, source
│   ├── companies.yaml            extra companies: name, ATS, board id
│   ├── must_have.yaml            ~50 companies that must always have a working source
│   ├── manual.yaml               postings added by hand: company, role, link, optional notes
│   ├── removed.json              closed postings with removed_on and reason
│   ├── checks.json               link-check results pushed from the laptop (section 4b)
│   └── schema.json               JSON Schema for postings.json
├── scripts/
│   ├── adapters/                 one module per source: greenhouse, lever, ashby, workday, smartrecruiters, oracle, and big-company sites
│   ├── fetch_ats.py              pull each company in companies.yaml (no-op if empty)
│   ├── load_manual.py            merge manual.yaml into the data
│   ├── classify.py               section + tags, with evidence
│   ├── check_links.py            open / closed / uncertain per posting
│   ├── validate.py               schema check + sanity checks
│   ├── build_readme.py           write README.md and the three table files
│   └── local/
│       ├── nightly.ps1           laptop job: run checks, commit data/checks.json, push
│       └── fetch_workday.py      Workday fetch in a real browser (Playwright) *(planned)*
├── tests/
│   ├── fixtures/                 saved Greenhouse, Lever, Ashby, Workday, SmartRecruiters, Oracle and big-company responses
│   └── eval/labeled.csv          ~150 hand-labeled postings for section and tag accuracy *(planned)*
├── docs/
│   ├── WRITEUP.md                design tradeoffs (portfolio)
│   └── MAINTAINING.md            runbook for officers
├── .github/workflows/daily.yml
└── .github/workflows/tests.yml   run tests on every push *(planned)*
```

## 4. The daily run

Scheduled once a day, and runnable by hand. When a maintainer pushes a change to `manual.yaml`, a fast run (steps 3, 4, 6, 7, 8 only) adds the postings within minutes.

1. **Fetch** every board in `companies.yaml` (Greenhouse, Lever, Ashby, SmartRecruiters and big-company adapters in the Action; Workday and Oracle on the laptop, section 4b), keeping only internship, new-grad and early-program titles. Check each source's response shape. A source with an unexpected shape fails loudly instead of silently returning zero postings. New postings get `first_seen` = today.

2. **Merge** with `postings.json`.
   - **Dedup key:** the apply URL, normalized. Strip tracking parameters, keep job-id parameters, and resolve redirect links to the final ATS URL where possible.
   - **Multi-city clones:** same company + same normalized title collapse into one row listing all locations.
   - **Description similarity:** used only for ATS postings, the only source that includes descriptions.

3. **Load manual postings** from `manual.yaml`. Skip any already listed, and flag any whose link doesn't load in the run log.

4. **Classify** each posting.
   - **Section:**
     - New-grad if the text says new grad or entry level, or names graduation years. The years are computed from today's date (the current and next calendar year), never hardcoded.
     - Early program if the text says freshman, sophomore, first-year or second-year, or names a known early program.
     - Otherwise internship.
   - **Tags:** each tag has three states: says yes, says no, or not mentioned (blank, the default).
     - **Sponsorship:** 🛂✅ the posting says it sponsors visas; 🛂❌ it says it doesn't. Matching is negation-aware ("unable to sponsor", "will not sponsor", "does not sponsor" → ❌). The tag is set only on an explicit statement.
     - 🇺🇸 U.S. citizenship or U.S. person required (export control).
     - 🔒 Security clearance required.
     - 📍 Location / remote.
   - **Evidence:** the sentence that triggered each tag is stored in `tag_evidence` so anyone can check it.
   - **README legend:** "🛂❌ usually refers to future visa sponsorship (e.g. H-1B). It doesn't necessarily mean CPT or OPT can't be used. Check with the recruiter and your DSO. A blank tag means the posting doesn't say."

5. **Apply link checks.**
   - **Feed rows** are open for as long as the company's feed lists them; a job missing from two consecutive fetches is closed. This replaces most link checks.
   - **`companies.yaml` and `manual.yaml` rows** use the latest results in `data/checks.json` from the laptop (section 4b). If a row's last check is more than 3 days old, it shows ⚠ instead of being trusted.
   - If `checks.json` is missing (laptop never ran), the Action checks only those rows itself, which is a small set.
   - How a check decides:
   - **Greenhouse, Lever and Ashby:** the job's JSON endpoint returns not-found when the job is closed.
   - **Workday:** use the per-job JSON endpoint, not the page HTML, which is rendered with JavaScript.
   - **Other sites:** HTTP status plus a short list of "no longer accepting" phrases.
   - **Outcomes:**
     - **Open:** strikes reset.
     - **Closed:** one strike. After two consecutive strikes, the posting moves to `removed.json` with the date and reason.
     - **Uncertain** (403, 429, timeout, ambiguous page): shown with ⚠ and kept. After 7 consecutive uncertain days, it's removed with reason "unverifiable".
   - **Reopened jobs:** if a company feed or `manual.yaml` lists a removed URL again after its `removed_on` date, it comes back.

6. **Test and validate.** Run the test suite (`pytest -q`) against the saved fixtures, so a broken parser fails the run instead of publishing. `postings.json` must match `schema.json`. Fail the run if the number of open postings drops more than 50% from the last commit; skip this check on the first run, when there is nothing to compare against. This protects the board from a source format change wiping it.

7. **Build** the board. GitHub cuts off very large READMEs, so the tables live in their own files:
   - `README.md`: "🆕 New this week" (first seen in the last 7 days), counts per section, legend, credits, and links to the three table files
   - `INTERNSHIPS.md`, `NEW_GRAD.md`, `EARLY.md`: one table each, sorted newest first
   - last updated date and a count per section
   - ⏳ for postings older than 60 days, ⚠ for uncertain links
   - tag legend, and links to other public boards for breadth
   - a line telling students to send posting suggestions to an ACM officer

8. **Commit** if anything changed.

## 4b. Laptop work (local offload)

The heavy and fragile work runs on Rohit's laptop; the GitHub Action stays light and keeps working without it.

| Runs where | Job | Why |
|---|---|---|
| Laptop, nightly (Windows Task Scheduler, ~2 a.m.) | Link checks for `companies.yaml` and `manual.yaml` rows; Workday and Oracle fetching through their public JSON search | No 30-minute limit, so it can stay slow and polite; Workday renders with JavaScript; and it isn't limited by a free cloud run's time budget |
| GitHub Action, daily | Upstream fetch, merge, classify, test, validate, build, commit | Light; always runs |

**How the laptop job works (`scripts/local/nightly.ps1`):**
1. `git pull`
2. Run `check_links.py --local` and `fetch_workday.py`; they write only `data/checks.json` (and Workday postings into it). *(planned)*
3. Commit `data/checks.json` and push; if the push is rejected because the Action pushed first, `git pull --rebase` and push again (up to 3 tries). It never touches generated files or `postings.json`, so the rebase can't conflict.

**If the laptop is off,** the Action still runs and uses the last `checks.json`. Rows checked more than 3 days ago show ⚠. Nothing breaks; the data just gets less fresh.

**Credentials:** a fine-grained GitHub token limited to this one repo with "Contents: write" only, stored in Windows Credential Manager (used by git), never in the repo.

**Not used:** a self-hosted GitHub Actions runner on the laptop. On a public repo it would run repository code on a personal machine; a scheduled script that only pushes one data file is simpler and safer.

**Scope limit:** the laptop fetches only companies' own career sites and public ATS feeds, never aggregators whose terms forbid automated access.

## 5. Access

**Who can write.** Collaborators are Rohit and the ACM officers. Everyone else, students included, has read access, which a public repo gives automatically.

**Repo settings:**
- **Issues, Discussions and Wiki:** turned off, so there's no public write surface.
- **Branch ruleset on `main`:** blocks force-pushes and deletion.
- **Pull requests:** anyone can open a pull request against a public repo, but only collaborators can merge one. Outside PRs are closed without merging. If the repo settings offer a way to turn pull requests off or limit them to collaborators, use it.
- **Forks:** anyone can fork a public repo. A fork is the other person's copy and never changes the board.

**Student suggestions** go to an ACM officer outside GitHub (Discord, email, in person). The officer adds the posting to `manual.yaml`.

## 6. Applied tracking

**v1:** none on the board. Students track applications in their own tools (e.g. Simplify), and the README says so.

**Later (option A):** a GitHub Pages page (free for public repos) that reads `postings.json` and stores each student's checkmarks in their browser, with export/import of the checkmarks as a file so they survive switching devices.

## 7. Security

- The workflow is triggered only by the schedule, the manual button, and maintainers' own pushes. It never processes text from outside users.
- The workflow default is no permissions; the refresh job gets only `contents: write`.
- No secrets are needed; the built-in `GITHUB_TOKEN` covers commits.
- Collaborators should have two-factor authentication turned on, since their accounts are the only write path.

## 8. Ownership and maintenance

- **Account:** the repo lives under Rohit's account, with ACM officers as collaborators.
- **Succession:** before Rohit graduates, transfer the repo to an ACM GitHub organization. GitHub keeps stars and redirects the old URL.
- **Failures:** failed scheduled runs email the owner. `docs/MAINTAINING.md` covers re-running, adding a posting or company, handling a source that changes its format, and setting up the laptop job. *(planned)*
- **Rule for maintainers:** edit only `manual.yaml` and `companies.yaml`. Everything else is generated; hand edits to generated files cause rebase conflicts and are overwritten.
- **Schedule pauses:** GitHub pauses scheduled workflows on public repos after 60 days without repository activity. Daily bot commits should count as activity; if the board ever goes quiet, re-enable the workflow from the Actions tab.
- **Action pinning:** third-party actions in the workflows are pinned to a full commit SHA, updated deliberately.
- **Load:** a few minutes of Action time per day.

## 9. Portfolio value

- **Tag accuracy:** precision and recall per tag on `tests/eval/labeled.csv`, reported in the README. Especially the rate of false 🛂✅ tags, the error that costs international students the most. *(planned)*
- **Metrics:** auto-generated weekly numbers in the README — postings tracked, added, removed and flagged uncertain.
- **Tests:** fixtures for every source, run on every push.
- **Write-up:** `docs/WRITEUP.md` on the tradeoffs: daily refresh, ⚠ instead of deletion, three-state tags, maintainer-only writes.

## 10. Scope

**v1 (one weekend):**
- `companies.yaml` with Greenhouse, Lever, Ashby, SmartRecruiters, Workable, Recruitee, Eightfold and ADP adapters, plus the big-company adapters, and the must-have companies check
- Hacker News "Who is hiring" (monthly) and the YC company pass
- our own negation-aware tag classifier on full descriptions (unknown by default)
- `manual.yaml` for hand-added postings
- three sections + New this week
- daily workflow (with tests and the first-run-safe 50% guard)
- separate table files linked from the README
- link checks with ⚠ and two strikes for `manual.yaml` rows (run in the Action until the laptop job exists)
- public repo with Issues off and a `main` ruleset

**v1.1:**
- 3–5 local companies in `companies.yaml` (`fetch_ats.py` is a no-op until then)
- laptop nightly job (`nightly.ps1`, `checks.json`): Workday (523 boards) and Oracle (153 boards)
- weekly metrics

**v1.2:**
- the evaluation set (~150 hand-labeled postings) and per-tag accuracy in the README *(planned)*
- description-based dedup for ATS postings

**Later:**
- applied-tracking page
- transfer to an ACM org

## 11. Open questions

1. Which big-company adapters first (proposed: Meta, Microsoft, Amazon, Google, Apple, NVIDIA, Netflix, Qualcomm, Cisco, Intel)?
2. Which local companies go into `companies.yaml` first?
3. Which channel do students use to suggest postings to officers?
4. Is 7 days the right cutoff before an unverifiable link is removed?
