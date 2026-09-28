@echo off
REM CareerOps on-demand scan - cmd wrapper.
REM Runs the full scanner from this machine so the IP-gated Arabic job
REM boards (mostaql, proz, bayt, gulftalent, wuzzuf, ureed) are reachable
REM again, and shares dedup state with the scheduled 09:00 Libya scan.
REM
REM Usage:
REM   run_scan.cmd                      comprehensive (default, strongest)
REM   run_scan.cmd quick                ~5 min, Tier 1 only
REM   run_scan.cmd standard             ~10 min
REM   run_scan.cmd deep                 ~30 min
REM   run_scan.cmd comprehensive        ~60 min, all sources

setlocal
set "MODE=%~1"
if "%MODE%"=="" set "MODE=comprehensive"

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Run-ScanNow.ps1" -Mode "%MODE%"
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (
  echo.
  echo Scan failed with exit code %RC%.
)
endlocal & exit /b %RC%