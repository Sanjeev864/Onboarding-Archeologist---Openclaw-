param(
    [Parameter(Mandatory=$true)][int]$RepositoryId,
    [Parameter(Mandatory=$true)][string]$Question
)

$ErrorActionPreference = "Stop"
$BaseUrl = if ($env:ARCHAEOLOGIST_API_URL) { $env:ARCHAEOLOGIST_API_URL } else { "http://localhost:8000" }
$Body = @{ repository_id = $RepositoryId; question = $Question } | ConvertTo-Json
$Response = Invoke-RestMethod -Uri "$BaseUrl/api/openclaw/ask" -Method Post -ContentType "application/json" -Body $Body
$Response.text
