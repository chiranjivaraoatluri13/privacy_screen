#!/usr/bin/env pwsh
# Fix stuck rebase and commit README changes

$ErrorActionPreference = "Continue"
$WarningPreference = "SilentlyContinue"

# Navigate to project
Set-Location "c:\Users\chira\OneDrive\Desktop\camera_access"

Write-Host "Step 1: Checking git status..." -ForegroundColor Cyan
git status --short

Write-Host "`nStep 2: Aborting stuck rebase..." -ForegroundColor Cyan
$null = git rebase --abort 2>&1
Start-Sleep -Milliseconds 500

Write-Host "Step 3: Staging README.md..." -ForegroundColor Cyan
git add README.md

Write-Host "Step 4: Committing changes..." -ForegroundColor Cyan
git commit -m "docs: Add comprehensive learning outcomes and technology rationale"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓ Commit successful!" -ForegroundColor Green
    
    Write-Host "`nStep 5: Showing latest commit..." -ForegroundColor Cyan
    git log --oneline -1
    
    Write-Host "`nStep 6: Pushing to GitHub..." -ForegroundColor Cyan
    git push origin main --force-with-lease
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✓ Push successful! Repository updated." -ForegroundColor Green
    } else {
        Write-Host "`n! Push encountered an issue (exit code: $LASTEXITCODE)" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n! Commit failed (exit code: $LASTEXITCODE)" -ForegroundColor Red
    Write-Host "Try: git status" -ForegroundColor Yellow
}

Write-Host "`nDone!" -ForegroundColor Green
