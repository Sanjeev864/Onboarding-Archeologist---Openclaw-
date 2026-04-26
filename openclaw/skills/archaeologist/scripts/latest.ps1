$ErrorActionPreference = "Stop"
$BaseUrl = if ($env:ARCHAEOLOGIST_API_URL) { $env:ARCHAEOLOGIST_API_URL } else { "http://localhost:8000" }
$Response = Invoke-RestMethod -Uri "$BaseUrl/api/openclaw/repositories/latest"
$StatePath = Join-Path $PSScriptRoot "..\resources\last_repository.json"
$Response | ConvertTo-Json | Set-Content -Path $StatePath
$Response | ConvertTo-Json
