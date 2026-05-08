# Install Onboarding Archaeologist OpenClaw skill on Windows
# Usage: .\scripts\install-openclaw-skill.ps1 [-ApiUrl http://localhost:8000]

param(
    [string]$ApiUrl = "http://localhost:8000"
)

$ErrorActionPreference = "Stop"

$SkillDir = Join-Path $env:USERPROFILE ".openclaw\skills\archaeologist"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$SourceDir = Join-Path $ProjectRoot "openclaw\skills\archaeologist"

Write-Host "Installing Onboarding Archaeologist OpenClaw Skill" -ForegroundColor Yellow
Write-Host "Skill directory: $SkillDir"
Write-Host "Backend API:     $ApiUrl"
Write-Host ""

# 1. Create skill directory
Write-Host "[1/5] Creating skill directory..." -ForegroundColor Green
New-Item -ItemType Directory -Force -Path $SkillDir | Out-Null
Write-Host "  OK  Directory ready: $SkillDir"

# 2. Copy skill files
Write-Host "[2/5] Copying skill files..." -ForegroundColor Green
if (-not (Test-Path $SourceDir)) {
    Write-Host "  FAIL  Source not found: $SourceDir" -ForegroundColor Red
    exit 1
}
foreach ($file in @("skill.yaml", "handlers.py", "system_prompt.md")) {
    $src = Join-Path $SourceDir $file
    if (-not (Test-Path $src)) {
        Write-Host "  FAIL  Missing: $src" -ForegroundColor Red
        exit 1
    }
    Copy-Item -Path $src -Destination $SkillDir -Force
}
Write-Host "  OK  skill.yaml, handlers.py, system_prompt.md copied"

# 3. Verify backend
Write-Host "[3/5] Verifying backend connectivity..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "$ApiUrl/health" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    Write-Host "  OK  Backend reachable at $ApiUrl"
} catch {
    Write-Host "  WARN  Backend not responding at $ApiUrl (it may start later)" -ForegroundColor Yellow
    Write-Host "        Start FastAPI before running OpenClaw:"
    Write-Host "        uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"
}

# 4. Write .env for skill
Write-Host "[4/5] Setting up environment..." -ForegroundColor Green
$EnvFile = Join-Path $SkillDir ".env"
if (-not (Test-Path $EnvFile)) {
    "ARCHAEOLOGIST_API_URL=$ApiUrl" | Set-Content -Path $EnvFile
    Write-Host "  OK  Created $EnvFile"
} else {
    Write-Host "  SKIP  $EnvFile already exists"
}

# 5. Done
Write-Host "[5/5] Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Onboarding Archaeologist skill installed successfully" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Set your Telegram bot token:"
Write-Host "     `$env:TELEGRAM_BOT_TOKEN = 'your_bot_token_here'" -ForegroundColor Yellow
Write-Host ""
Write-Host "  2. Start the FastAPI backend (new terminal):"
Write-Host "     uvicorn backend.app.main:app --host 0.0.0.0 --port 8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "  3. Start OpenClaw Gateway:"
Write-Host "     openclaw run --config openclaw.config.yaml" -ForegroundColor Yellow
Write-Host ""
Write-Host "  4. Send your Telegram bot:"
Write-Host "     /analyze-autonomous torvalds/linux" -ForegroundColor Yellow
Write-Host ""
Write-Host "For full setup details see docs/OPENCLAW_INTEGRATION.md"
