# Runs each weekday morning via Task Scheduler.
# Scaffolds the next problem, shows what is due for a repeat, and opens the write-up.
# It never writes a solution and never commits — that part is yours.

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

Write-Host ''
Write-Host '  Neetcode 150 ' -ForegroundColor Black -BackgroundColor DarkCyan
Write-Host ''

python scripts/nc.py status
Write-Host ''

# Anything owed from a previous day comes first.
$review = python scripts/nc.py review 2>&1 | Out-String
if ($review -notmatch 'Nothing due') {
    Write-Host $review -ForegroundColor Yellow
}

# Scaffold today's problem unless one is already open.
$next = python scripts/nc.py next 2>&1 | Out-String
if ($next -match 'Still open') {
    Write-Host $next -ForegroundColor Yellow
} else {
    Write-Host $next
    python scripts/nc.py new
}

# Open the newest write-up in whatever editor is available.
$latest = Get-ChildItem -Path (Join-Path $repo 'solutions') -Directory -ErrorAction SilentlyContinue |
          Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($latest) {
    $readme = Join-Path $latest.FullName 'README.md'
    if (Get-Command code -ErrorAction SilentlyContinue) {
        code $latest.FullName $readme
    } elseif (Test-Path $readme) {
        Invoke-Item $readme
    }
}

Write-Host ''
Write-Host '  Twenty-five minutes, then read the solution and reimplement it.' -ForegroundColor DarkGray
Write-Host '  When it passes:  python scripts/nc.py done ; git push' -ForegroundColor DarkGray
Write-Host ''

# Weekly, not daily: open source is a weekend job and a daily nag for it just
# trains you to ignore this window.
if ((Get-Date).DayOfWeek -eq 'Saturday') {
    python scripts/oss_digest.py
}

Write-Host '  Press Enter to close.' -ForegroundColor DarkGray
[void][System.Console]::ReadLine()
