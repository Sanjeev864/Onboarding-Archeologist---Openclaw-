param(
    [Parameter(Mandatory=$true)][string]$Owner,
    [Parameter(Mandatory=$true)][string]$Repo,
    [string]$Branch = ""
)

$ErrorActionPreference = "Stop"
$BaseUrl = if ($env:ARCHAEOLOGIST_API_URL) { $env:ARCHAEOLOGIST_API_URL } else { "http://localhost:8000" }

try {
    Invoke-RestMethod -Uri "$BaseUrl/health" | Out-Null
} catch {
    Write-Error "Analyzer not running at $BaseUrl. Start it with: docker-compose up -d backend"
}

$Body = @{ owner = $Owner; repo = $Repo; branch = $Branch } | ConvertTo-Json
$Response = Invoke-RestMethod -Uri "$BaseUrl/api/openclaw/analyze" -Method Post -ContentType "application/json" -Body $Body
$StatePath = Join-Path $PSScriptRoot "..\resources\last_repository.json"
@{ repository_id = $Response.repository_id; owner = $Owner; repo = $Repo } | ConvertTo-Json | Set-Content -Path $StatePath
$Response.text
