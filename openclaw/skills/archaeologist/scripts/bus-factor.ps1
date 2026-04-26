param([Parameter(Mandatory=$true)][int]$RepositoryId)
$BaseUrl = if ($env:ARCHAEOLOGIST_API_URL) { $env:ARCHAEOLOGIST_API_URL } else { "http://localhost:8000" }
(Invoke-RestMethod -Uri "$BaseUrl/api/openclaw/repositories/$RepositoryId/bus-factor").text
