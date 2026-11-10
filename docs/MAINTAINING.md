# Maintaining the board

For ACM officers. You need write access to the repo and Python 3.12+.

## Setup

```
git clone https://github.com/rohitpeets/mcneese-jobs
cd mcneese-jobs
pip install -r requirements.txt
python -m pytest -q
```

## Everyday tasks

**Add a posting by hand.** Add it to `data/manual.yaml` (the format is at the top of `scripts/load_manual.py`) and push. A quick run publishes it within a few minutes. Hand-added links are checked daily and drop off once they've been closed on two checks.

**Add a company.** Find its job board link and add one line to `data/companies.yaml`:

| Job system | How to recognise the link | `ats` | `board` |
|---|---|---|---|
| Greenhouse | `job-boards.greenhouse.io/acme` | `greenhouse` | `acme` |
| Lever | `jobs.lever.co/acme` | `lever` | `acme` |
| Ashby | `jobs.ashbyhq.com/acme` | `ashby` | `acme` |
| SmartRecruiters | `jobs.smartrecruiters.com/Acme` | `smartrecruiters` | `Acme` |
| Workday | `acme.wd5.myworkdayjobs.com/AcmeCareers` | `workday` | `acme.wd5/AcmeCareers` |
| Oracle | `xxxx.fa.us2.oraclecloud.com/.../sites/CX_1` | `oracle` | `xxxx.fa.us2/CX_1` |

To check a guess before adding it, put it in `GUESSES` in `scripts/probe_sources.py` and run `python scripts/probe_sources.py`.

**Fix a board the run log calls GONE.** The company renamed or moved its board. Its jobs show ⚠ and leave after 7 days. Find the new link and update the line in `companies.yaml`.

**The daily run failed with "refusing to publish".** Open postings fell below half of the recent high. Check the log first: a broken source should be fixed, not published. If the drop is intended (for example a stricter filter), commit with `[reset-baseline]` in the message.

**Change what counts as a CS job or a tag.** The rules are in `scripts/classify.py`. Add a test for the case in `tests/test_classify.py` first, then change the rule, then run the tests.

## How it runs

- **GitHub Action, daily** (`.github/workflows/daily.yml`): Greenhouse, Lever, Ashby, SmartRecruiters, Amazon and Netflix, then merge, classify, test, validate, and build the pages. Failures email the repo owner. The log is in the Actions tab.
- **Laptop, nightly** (`scripts/local/nightly.ps1`, Windows Task Scheduler): Workday and Oracle, written to `data/local.json`. Any machine with Python and push access can run it. If it stops, those rows show ⚠ after 3 days and leave after 7.
