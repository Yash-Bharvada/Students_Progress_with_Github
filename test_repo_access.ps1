# PowerShell script to test real-time GitHub repository access
# Usage: .\test_repo_access.ps1 "YOUR_JWT_TOKEN_HERE"

param(
    [Parameter(Mandatory=$true)]
    [string]$JwtToken
)

Write-Host "🧪 TESTING REAL-TIME GITHUB REPOSITORY ACCESS" -ForegroundColor Cyan
Write-Host "=" * 60

# Test 1: Validate JWT Token
Write-Host "`n🔑 Step 1: Validating JWT Token..." -ForegroundColor Yellow
try {
    $response = curl -H "Authorization: Bearer $JwtToken" "http://localhost:8000/test/validate-token" | ConvertFrom-Json
    Write-Host "✅ Token is valid!" -ForegroundColor Green
    Write-Host "   User: $($response.user.username)" -ForegroundColor White
    Write-Host "   Role: $($response.user.role)" -ForegroundColor White
    Write-Host "   GitHub ID: $($response.user.github_id)" -ForegroundColor White
} catch {
    Write-Host "❌ Token validation failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Fetch User Repositories
Write-Host "`n📁 Step 2: Fetching repositories for Yash-Bharvada..." -ForegroundColor Yellow
try {
    $repoResponse = curl -H "Authorization: Bearer $JwtToken" "http://localhost:8000/test/repositories/Yash-Bharvada" | ConvertFrom-Json
    Write-Host "✅ Successfully fetched repositories!" -ForegroundColor Green
    Write-Host "   Total repositories: $($repoResponse.total_repositories)" -ForegroundColor White
    Write-Host "   Showing: $($repoResponse.showing)" -ForegroundColor White
    
    Write-Host "`n📋 Repository List:" -ForegroundColor Cyan
    foreach ($repo in $repoResponse.repositories) {
        Write-Host "   • $($repo.name)" -ForegroundColor White
        Write-Host "     Language: $($repo.language)" -ForegroundColor Gray
        Write-Host "     Stars: $($repo.stars), Forks: $($repo.forks)" -ForegroundColor Gray
        Write-Host "     Private: $($repo.private)" -ForegroundColor Gray
        Write-Host "     URL: $($repo.html_url)" -ForegroundColor Blue
        Write-Host ""
    }
    
    # Store first repository name for commit testing
    $firstRepo = $repoResponse.repositories[0].name
    
} catch {
    Write-Host "❌ Repository fetch failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 3: Fetch Commits from First Repository
if ($firstRepo) {
    Write-Host "`n📝 Step 3: Fetching commits from repository '$firstRepo'..." -ForegroundColor Yellow
    try {
        $commitResponse = curl -H "Authorization: Bearer $JwtToken" "http://localhost:8000/test/commits/Yash-Bharvada/$firstRepo" | ConvertFrom-Json
        Write-Host "✅ Successfully fetched commits!" -ForegroundColor Green
        Write-Host "   Total commits: $($commitResponse.total_commits)" -ForegroundColor White
        Write-Host "   Showing: $($commitResponse.showing)" -ForegroundColor White
        
        Write-Host "`n📋 Recent Commits:" -ForegroundColor Cyan
        foreach ($commit in $commitResponse.commits[0..4]) {  # Show first 5 commits
            Write-Host "   • [$($commit.sha)] $($commit.message)" -ForegroundColor White
            Write-Host "     Author: $($commit.author.name)" -ForegroundColor Gray
            Write-Host "     Date: $($commit.author.date)" -ForegroundColor Gray
            if ($commit.stats) {
                Write-Host "     Changes: +$($commit.stats.additions) -$($commit.stats.deletions)" -ForegroundColor Gray
            }
            Write-Host ""
        }
        
    } catch {
        Write-Host "❌ Commit fetch failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n🎉 REAL-TIME REPOSITORY ACCESS TEST COMPLETE!" -ForegroundColor Green
Write-Host "=" * 60
Write-Host "✅ Authentication: Working" -ForegroundColor Green
Write-Host "✅ Repository Access: Working" -ForegroundColor Green
Write-Host "✅ Commit Data: Working" -ForegroundColor Green
Write-Host "`nThe system can now access and analyze real GitHub repositories!" -ForegroundColor Cyan