# Laptop job: fetch Workday + Oracle boards, commit data/local.json, push.
# Scheduled nightly by Task Scheduler (see docs/MAINTAINING.md). Touches only data/local.json.
# Continue, not Stop: git writes normal progress to stderr, which PowerShell would otherwise treat as an error
$ErrorActionPreference = "Continue"
Set-Location (Join-Path $PSScriptRoot "..\..")
New-Item -ItemType Directory -Force logs | Out-Null
$log = "logs\nightly-$(Get-Date -Format yyyy-MM-dd).log"

git pull --rebase --autostash *>> $log
python scripts/fetch_ats.py --local --workers 4 *>> $log
if ($LASTEXITCODE -ne 0) { "fetch failed" >> $log; exit 1 }

git add data/local.json
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m "Laptop refresh $(Get-Date -Format yyyy-MM-dd)" *>> $log
    for ($i = 0; $i -lt 3; $i++) {
        git push *>> $log
        if ($LASTEXITCODE -eq 0) { break }
        git pull --rebase --autostash *>> $log   # the Action pushed first; our files never overlap with its files
    }
}
