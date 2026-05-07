param(
    [string]$OpenClawHome = "$env:USERPROFILE\.openclaw",
    [string]$ApiUrl = $(if ($env:ARCHAEOLOGIST_API_URL) { $env:ARCHAEOLOGIST_API_URL } else { "http://localhost:8000" }),
    [switch]$SkipBackendCheck
)

$ErrorActionPreference = "Stop"

function Fail([string]$Message) {
    Write-Host "OpenClaw skill install failed: $Message" -ForegroundColor Red
    exit 1
}

$Source = Join-Path (Split-Path -Parent $PSScriptRoot) "openclaw\skills\archaeologist"
$ConfigSource = Join-Path (Split-Path -Parent $PSScriptRoot) "openclaw\openclaw.config.yaml"
$Destination = Join-Path $OpenClawHome "skills\archaeologist"
$ConfigDestination = Join-Path $OpenClawHome "openclaw.config.yaml"
$JsonConfigDestination = Join-Path $OpenClawHome "openclaw.json"
$EnvFile = Join-Path $OpenClawHome "archaeologist.env.ps1"

if (!(Test-Path $Source)) {
    Fail "Skill source not found: $Source"
}

if (!(Test-Path $ConfigSource)) {
    Fail "Gateway config not found: $ConfigSource"
}

if (!$env:TELEGRAM_BOT_TOKEN) {
    Fail "TELEGRAM_BOT_TOKEN is not set. Set it before installing so OpenClaw can start the Telegram channel."
}

$env:ARCHAEOLOGIST_API_URL = $ApiUrl
[Environment]::SetEnvironmentVariable("ARCHAEOLOGIST_API_URL", $ApiUrl, "User")

if (!$SkipBackendCheck) {
    try {
        $HealthUrl = "$($ApiUrl.TrimEnd('/'))/health"
        Invoke-RestMethod -Uri $HealthUrl -Method Get -TimeoutSec 10 | Out-Null
        Write-Host "Backend reachable at $HealthUrl" -ForegroundColor Green
    }
    catch {
        Fail "Backend is not reachable at $ApiUrl. Start FastAPI first, or rerun with -SkipBackendCheck."
    }
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Destination) | Out-Null
if (Test-Path $Destination) {
    Remove-Item -Path $Destination -Recurse -Force
}
Copy-Item -Path $Source -Destination $Destination -Recurse -Force
Copy-Item -Path $ConfigSource -Destination $ConfigDestination -Force

$OpenClawConfig = [ordered]@{
    skills = [ordered]@{
        entries = [ordered]@{
            archaeologist = [ordered]@{
                enabled = $true
                path = "~/.openclaw/skills/archaeologist"
                env = [ordered]@{ ARCHAEOLOGIST_API_URL = $ApiUrl }
            }
        }
    }
    channels = [ordered]@{
        telegram = [ordered]@{
            enabled = $true
            mode = "polling"
            botTokenEnv = "TELEGRAM_BOT_TOKEN"
            skills = @("archaeologist")
            allowedCommands = @("analyze-autonomous", "agent-trace", "onboarding", "agent-feedback", "agent-status", "ask")
            rateLimits = [ordered]@{
                default = [ordered]@{ requests = 20; windowSeconds = 60 }
                "analyze-autonomous" = [ordered]@{ requests = 3; windowSeconds = 600 }
                onboarding = [ordered]@{ requests = 10; windowSeconds = 300 }
                "agent-feedback" = [ordered]@{ requests = 30; windowSeconds = 300 }
            }
        }
    }
}

$OpenClawConfig | ConvertTo-Json -Depth 10 | Set-Content -Path $JsonConfigDestination -Encoding UTF8
@"
`$env:ARCHAEOLOGIST_API_URL = "$ApiUrl"
if (-not `$env:TELEGRAM_BOT_TOKEN) {
    throw "Set TELEGRAM_BOT_TOKEN before starting OpenClaw Gateway."
}
"@ | Set-Content -Path $EnvFile -Encoding UTF8

Write-Host "Installed Onboarding Archaeologist skill to: $Destination"
Write-Host "Registered skill config at: $JsonConfigDestination"
Write-Host "Copied gateway YAML to: $ConfigDestination"
Write-Host "Environment helper written to: $EnvFile"
Write-Host ""
Write-Host "Next:"
Write-Host "1. Restart OpenClaw Gateway: openclaw gateway"
Write-Host "2. In a new PowerShell session, run: . `"$EnvFile`""
