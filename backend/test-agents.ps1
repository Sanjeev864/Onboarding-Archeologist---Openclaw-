# Complete Agent Testing Script for Windows

$BACKEND_URL = "http://localhost:8000"

Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🤖 AUTONOMOUS AGENTS: COMPLETE TESTING SUITE 🤖" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Test 1: Agent Status
Write-Host "TEST 1: Agent Status" -ForegroundColor Yellow
Write-Host "-" * 50 -ForegroundColor Gray
try {
    $response = curl -s "$BACKEND_URL/api/v2/agent-status"
    $json = $response | ConvertFrom-Json
    Write-Host "✅ Status: $($json.status)" -ForegroundColor Green
    Write-Host "✅ Agents Ready: $(($json.agents | Measure-Object).Count)" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 2: Analyze Autonomous
Write-Host "TEST 2: Autonomous Analysis" -ForegroundColor Yellow
Write-Host "-" * 50 -ForegroundColor Gray
try {
    $response = curl -s -X POST "$BACKEND_URL/api/v2/analyze-autonomous?owner=test&repo=repo"
    $json = $response | ConvertFrom-Json
    Write-Host "✅ Status: $($json.status)" -ForegroundColor Green
    Write-Host "✅ Repository: $($json.repository)" -ForegroundColor Green
    Write-Host "✅ Agents Executed: $($json.agents_executed)" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 3: Agent Trace
Write-Host "TEST 3: Agent Decision Trace" -ForegroundColor Yellow
Write-Host "-" * 50 -ForegroundColor Gray
try {
    $response = curl -s "$BACKEND_URL/api/v2/agent-decision-trace/decisions"
    $json = $response | ConvertFrom-Json
    Write-Host "✅ Agent: $($json.agent_name)" -ForegroundColor Green
    Write-Host "✅ Trace Points: $(($json.decision_trace | Measure-Object).Count)" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 4: Onboarding
Write-Host "TEST 4: Onboarding Generator" -ForegroundColor Yellow
Write-Host "-" * 50 -ForegroundColor Gray
try {
    $response = curl -s -X POST "$BACKEND_URL/api/v2/onboarding-autonomous?level=junior&time_available_hours=40"
    $json = $response | ConvertFrom-Json
    Write-Host "✅ Status: $($json.status)" -ForegroundColor Green
    Write-Host "✅ Level: $($json.learner_level)" -ForegroundColor Green
    Write-Host "✅ Days: $($json.journey.days)" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 5: Feedback
Write-Host "TEST 5: Agent Feedback" -ForegroundColor Yellow
Write-Host "-" * 50 -ForegroundColor Gray
try {
    $body = @{
        agent_id = "arch-decision-001"
        execution_id = "test_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        feedback_type = "positive"
        feedback_text = "Great work!"
        rating = 0.95
    } | ConvertTo-Json
    
    $response = curl -s -X POST "$BACKEND_URL/api/v2/submit-agent-feedback" `
        -H "Content-Type: application/json" `
        -d $body
    
    $json = $response | ConvertFrom-Json
    Write-Host "✅ Status: $($json.status)" -ForegroundColor Green
    Write-Host "✅ Feedback Recorded: $($json.feedback_recorded)" -ForegroundColor Green
    Write-Host "✅ Agent Adapted: $($json.agent_adapted)" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed: $_" -ForegroundColor Red
}
Write-Host ""

# Summary
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ TESTING COMPLETE" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "All endpoints working? You're ready for Day 2! 🚀" -ForegroundColor Green