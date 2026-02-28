# Script to rename commits using git filter-branch (non-interactive)

cd "c:\Users\chira\OneDrive\Desktop\camera_access"

# First, abort any stuck rebase
Write-Host "Aborting any stuck operations..." -ForegroundColor Yellow
git rebase --abort 2>$null
git merge --abort 2>$null

# Define commit message mapping  
$commitMessages = @{
    # Old message patterns -> New message
    "Privacy protection system" = "feat: Initial commit"
    "Initial project implementation" = "feat: Add core system"  
    "Add project gitignore" = "chore: Add project configuration"
}

Write-Host "Current commits:" -ForegroundColor Green
git log --oneline -5

Write-Host "`nApplying filter-branch to rename commits...`n" -ForegroundColor Yellow

# Use git filter-branch to rewrite all commit messages
# This iterates through each commit and applies a filter
git filter-branch -f --msg-filter '
    $msg = $input
    if ($msg -like "*Privacy protection system*") { 
        "feat: Initial commit" 
    } 
    elseif ($msg -like "*Initial project implementation*") { 
        "feat: Add core system" 
    }
    elseif ($msg -like "*Add project gitignore*") { 
        "chore: Add project configuration" 
    }
    else { 
        $msg 
    }
' -- --all 2>&1

Write-Host "`nNew commits:" -ForegroundColor Green
git log --oneline -5

Write-Host "`nForce pushing to origin..." -ForegroundColor Yellow
git push origin main --force-with-lease

Write-Host "`nDone!" -ForegroundColor Green
