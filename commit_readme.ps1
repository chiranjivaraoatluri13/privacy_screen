# Standalone script to commit README changes
$ErrorActionPreference = "SilentlyContinue"

cd "c:\Users\chira\OneDrive\Desktop\camera_access"

# Abort any stuck rebase
git rebase --abort 2>$null
git merge --abort 2>$null

# Wait a moment
Start-Sleep -Milliseconds 500

# Disable pager to prevent interactive mode
$env:GIT_PAGER = "cat"

# Stage README
git add README.md

# Commit with professional message
git commit -m "docs: Comprehensive README with learning outcomes and technology choices"

# Show result
$lastExitCode = $LASTEXITCODE
if ($lastExitCode -eq 0) {
    Write-Host "✓ README committed successfully" -ForegroundColor Green
} else {
    Write-Host "! Commit may have failed (exit code: $lastExitCode)" -ForegroundColor Yellow
}

# Show latest commit
git log --oneline -1

# Push to remote
Write-Host "`nForce pushing to GitHub..." -ForegroundColor Cyan
git push origin main --force-with-lease

Write-Host "`nDone!" -ForegroundColor Green
