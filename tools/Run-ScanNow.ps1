<#
.SYNOPSIS
    Run a full-strength CareerOps scan right now, from this machine.

.DESCRIPTION
    The scheduled 09:00 Libya digest runs on GitHub Actions, and GitHub's
    datacenter IPs are blocked (HTTP 403 / Cloudflare) by several job boards
    that actually carry Arabic-language work - mostaql, proz, bayt, gulftalent,
    wuzzuf, ureed. They were switched off after a probe confirmed the block.

    This script runs the same scanner from your home connection, so those
    sources are reachable again, and it can be fired at any moment instead of
    waiting for the cron slot.

    It shares ONE state store with the hosted scan: state is downloaded from
    the repo before the scan and uploaded after it, so dedup memory is
    identical whichever side runs the scan.

.PARAMETER Mode
    quick        ~5 min   Tier 1 sources only
    standard     ~10 min  Tier 1-2
    deep         ~30 min  Tier 1-3
    comprehensive ~60 min all sources, full AI (default - strongest result)
    adaptive     comprehensive, but morning slot gets full depth

.PARAMETER NoUpload
    Scan without pushing state back to the repo (dry run - dedup memory for
    the hosted scan is left untouched).

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File tools\Run-ScanNow.ps1
    powershell -ExecutionPolicy Bypass -File tools\Run-ScanNow.ps1 -Mode quick
#>
[CmdletBinding()]
param(
    [ValidateSet('quick', 'standard', 'deep', 'comprehensive', 'adaptive')]
    [string]$Mode = 'comprehensive',
    [switch]$NoUpload
)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $repo '.env'

if (-not (Test-Path -LiteralPath $envFile)) {
    Write-Host "ERROR: .env not found at $envFile" -ForegroundColor Red
    exit 1
}

# ---- 1. Load secrets from .env into this process -----------------------------
Get-Content -LiteralPath $envFile -Encoding UTF8 | ForEach-Object {
    $line = $_.Trim()
    if (-not $line -or $line.StartsWith('#')) { return }
    $i = $line.IndexOf('=')
    if ($i -lt 1) { return }
    $k = $line.Substring(0, $i).Trim()
    $v = $line.Substring($i + 1).Trim().Trim('"').Trim("'")
    if ($k -and -not [Environment]::GetEnvironmentVariable($k)) {
        [Environment]::SetEnvironmentVariable($k, $v)
    }
}

# ---- 2. Locate a Python 3.12+ interpreter -----------------------------------
$python = $null
foreach ($cand in @('python', 'py -3.12', 'py')) {
    try {
        if ($cand -eq 'python') {
            $null = & python --version 2>&1
            if ($LASTEXITCODE -eq 0) { $python = 'python'; break }
        } else {
            $null = & ($cand.Split(' ') + @('--version')) 2>&1
            if ($LASTEXITCODE -eq 0) { $python = $cand; break }
        }
    } catch { }
}
if (-not $python) {
    Write-Host 'ERROR: no python interpreter found on PATH.' -ForegroundColor Red
    exit 1
}

# ---- 3. Point state sync at the repo, and un-block the IP-gated sources ------
# GITHUB_TOKEN: the hosted run gets it from secrets; locally take it from .env.
if (-not $env:GITHUB_TOKEN) {
    $tok = (Get-Content -LiteralPath $envFile -Encoding UTF8 |
        Select-String -Pattern '^\s*(GITHUB_TOKEN[A-Z0-9_]*)\s*=\s*(.+)$' |
        Select-Object -First 1)
    if ($tok) {
        $env:GITHUB_TOKEN = ($tok.Matches[0].Groups[2].Value).Trim().Trim('"').Trim("'")
    }
}
$env:CAREEROPS_SYNC = '1'
$env:CAREEROPS_SYNC_REPO = 'waleedba19/career-ops-scanner'
# Home IP is not a datacenter IP: attempt the sources GitHub Actions gets 403 on.
$env:CAREEROPS_FORCE_BLOCKED = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'

if (-not $env:GITHUB_TOKEN) {
    Write-Host 'WARNING: no GITHUB_TOKEN in .env - state sync will be skipped and' -ForegroundColor Yellow
    Write-Host '         dedup memory will NOT be shared with the hosted scan.' -ForegroundColor Yellow
    $env:CAREEROPS_SYNC = '0'
}

$py = { param($argsList) & $python.Split(' ') $argsList }

Write-Host ''
Write-Host '===============================================================' -ForegroundColor Cyan
Write-Host " CareerOps on-demand scan   mode=$Mode" -ForegroundColor Cyan
Write-Host " started $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') (Libya local time)" -ForegroundColor Cyan
Write-Host '===============================================================' -ForegroundColor Cyan
Write-Host " python      : $python"
Write-Host " IP-gated sources: ENABLED (running from this machine, not Actions)"
Write-Host " state sync  : $(if ($env:CAREEROPS_SYNC -eq '1') { 'ON  (shared with the hosted 09:00 scan)' } else { 'OFF' })"
Write-Host ''

Set-Location -LiteralPath $repo

# ---- 4. Pull shared state (dedup memory) ------------------------------------
if ($env:CAREEROPS_SYNC -eq '1') {
    Write-Host '[1/3] Downloading state from GitHub...' -ForegroundColor Yellow
    & $python.Split(' ') 'state_sync.py' 'download'
    if ($LASTEXITCODE -ne 0) { Write-Host '  (state download failed - continuing with local state)' -ForegroundColor DarkYellow }
}

# ---- 5. The scan ------------------------------------------------------------
Write-Host "[2/3] Running scanner (this takes $Mode budget)..." -ForegroundColor Yellow
$start = Get-Date
& $python.Split(' ') 'scanner.py' '--mode' $Mode
$scanRc = $LASTEXITCODE
$mins = [math]::Round(((Get-Date) - $start).TotalMinutes, 1)

# ---- 6. Push state back ------------------------------------------------------
if ($env:CAREEROPS_SYNC -eq '1' -and -not $NoUpload) {
    Write-Host '[3/3] Uploading state to GitHub...' -ForegroundColor Yellow
    & $python.Split(' ') 'state_sync.py' 'upload'
    if ($LASTEXITCODE -ne 0) { Write-Host '  (state upload failed - next run may re-announce these jobs)' -ForegroundColor DarkYellow }
} else {
    Write-Host '[3/3] Skipping state upload.' -ForegroundColor DarkGray
}

# ---- 7. Report ---------------------------------------------------------------
$health = Join-Path $repo 'output\health.json'
$hist = Join-Path $repo 'output\fresh_matches_history.json'
if (Test-Path -LiteralPath $health) {
    try {
        $h = Get-Content -LiteralPath $health -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host ''
        Write-Host "RESULT: matched=$($h.total_matches)  health=$($h.health_pct)%  errors=$($h.total_errors)  elapsed=${mins}m" -ForegroundColor Green
    } catch { }
}
if (Test-Path -LiteralPath $hist) {
    try {
        $rows = @(Get-Content -LiteralPath $hist -Raw -Encoding UTF8 | ConvertFrom-Json)
        if ($rows.Count -gt 0) {
            Write-Host ''
            Write-Host 'Delivered to Telegram + email:' -ForegroundColor Green
            foreach ($r in $rows) {
                Write-Host ("  - [{0}%] {1} | {2} | {3}" -f $r.score, $r.company, $r.title, $r.location)
            }
        } else {
            Write-Host ''
            Write-Host 'No new matches passed the filters this run.' -ForegroundColor DarkYellow
            Write-Host 'Check the run log above for the funnel counts (duplicates / too old /' -ForegroundColor DarkGray
            Write-Host 'not-worldwide) to see which stage removed everything.' -ForegroundColor DarkGray
        }
    } catch { }
}

Write-Host ''
if ($scanRc -eq 0) { Write-Host 'Scan finished OK.' -ForegroundColor Green }
else { Write-Host "Scan exited with code $scanRc" -ForegroundColor Red }
exit $scanRc