param(
    [string]$OpenClawHome = "$env:USERPROFILE\.openclaw"
)

$ErrorActionPreference = "Stop"

$Source = Join-Path (Split-Path -Parent $PSScriptRoot) "openclaw\skills\archaeologist"
$Destination = Join-Path $OpenClawHome "skills\archaeologist"

if (!(Test-Path $Source)) {
    throw "Skill source not found: $Source"
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Destination) | Out-Null
Copy-Item -Path $Source -Destination $Destination -Recurse -Force

Write-Host "Installed Code Archaeologist skill to: $Destination"
Write-Host "Next:"
Write-Host "1. Ensure backend is running: docker-compose up -d backend"
Write-Host "2. Enable the skill in $OpenClawHome\openclaw.json if needed"
Write-Host "3. Restart OpenClaw gateway: openclaw gateway"
