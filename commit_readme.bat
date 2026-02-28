@echo off
setlocal enabledelayedexpansion

REM Navigate to project
cd /d "c:\Users\chira\OneDrive\Desktop\camera_access"

REM Disable pager
git config core.pager "cat"

REM Abort any stuck operations
git rebase --abort 2>nul
git merge --abort 2>nul

REM Stage and commit README
echo Committing README changes...
git add README.md
git commit -m "docs: Comprehensive README with learning outcomes and technology choices"

if %ERRORLEVEL% EQU 0 (
    echo README committed successfully
) else (
    echo Commit may have failed
)

REM Show latest commit
echo.
echo Latest commit:
git log --oneline -n 1

REM Push to remote
echo.
echo Pushing to GitHub...
git push origin main --force-with-lease

echo.
echo Done!
