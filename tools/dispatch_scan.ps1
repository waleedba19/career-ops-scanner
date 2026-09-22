# tools/dispatch_scan.ps1 — precisely trigger a CareerOps scan on GitHub.
#
# Called by Windows Task Scheduler at 09:00 and 18:00 Libya. workflow_dispatch
# starts instantly (no GitHub cron queue, no stale crones), so the email lands
# ~5-10 min later.
#
# Manual usage:  powershell -ExecutionPolicy Bypass -File tools\dispatch_scan.ps1 [-mode standard]

param([string]$mode = "standard")

$repo = "waleedba19/career-ops-scanner"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $scriptDir
$envFile = Join-Path $root ".env"

if (-not (Test-Path $envFile)) {
    Write-Host "ERROR: .env not found at $envFile"; exit 1
}

$tok = ""
foreach ($line in Get-Content $envFile) {
    if ($line -match '^GITHUB_TOKEN_WALEEDBA19_1=') {
        $tok = ($line -split '=', 2)[1].Trim()
        break
    }
}
if (-not $tok -or $tok -eq "***") {
    Write-Host "ERROR: GITHUB_TOKEN_WALEEDBA19_1 missing in .env (token was masked)."; exit 1
}

$body = @{ ref = "main"; inputs = @{ mode = $mode } } | ConvertTo-Json
$headers = @{
    "Authorization" = "Bearer $tok"
    "Accept"        = "application/vnd.github+json"
    "User-Agent"    = "careerops-local-dispatcher"
}

try {
    Invoke-RestMethod -Uri "https://api.github.com/repos/$repo/actions/workflows/scan.yml/dispatches" `
        -Method Post -Headers $headers -ContentType "application/json" -Body $body -TimeoutSec 30
    Write-Host "CareerOps scan dispatched at $((Get-Date).ToString('HH:mm:ss')) Libya (mode=$mode)"
} catch {
    Write-Host "DISPATCH FAILED: $($_.Exception.Message)"
    exit 1
}