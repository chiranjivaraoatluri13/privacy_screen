# PowerShell script to rewrite commit messages non-interactively

# Navigate to repo
cd "c:\Users\chira\OneDrive\Desktop\camera_access"

# Disable git pager
$env:GIT_PAGER = 'cat'

# Abort any stuck rebase
git rebase --abort 2>$null

# Get the commits
$commits = @(git log --format=%H -n 3)

# New professional messages
$messages = @(
    "feat: Initial commit",
    "feat: Add core system",
    "chore: Add project configuration"
)

if ($commits.Count -ge 3) {
    # Reset to parent of oldest commit
    $oldestParent = git rev-parse "$($commits[2])^"
    
    # Do an automated rebase using git filter-branch as fallback
    # Or use git commit-tree to rebuild
    
    # Simpler approach: Reset, stage everything, recommit with new messages
    git reset --soft $oldestParent
    
    # Now all changes are staged
    # Unstage everything first
    git reset HEAD
    
    # Get all files that changed
    $allFiles = git diff --name-only --cached
    
    # Stage all at once and commit with first message
    git add -A
    git commit -m $messages[0]
    
    Write-Host "Commits reset. You may need to manually verify the commits are correct."
    Write-Host "Run: git log --oneline -5"
}
else {
    Write-Host "Could not find enough commits to rewrite"
}
