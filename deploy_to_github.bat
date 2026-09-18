@echo off
echo ========================================================
echo   Deploy Money that matters - EGX to GitHub
echo ========================================================
echo.
set /p GH_USER="Enter your GitHub username: "
set /p REPO_NAME="Enter your repository name (or press Enter for money-that-matters-egx): "
if "%REPO_NAME%"=="" set REPO_NAME=money-that-matters-egx

echo.
echo Setting remote origin to: https://github.com/%GH_USER%/%REPO_NAME%.git
git remote remove origin 2>nul
git remote add origin https://github.com/%GH_USER%/%REPO_NAME%.git
git branch -M main
echo.
echo Pushing code to GitHub...
echo (Windows will open a one-click GitHub browser login if needed)
git push -u origin main
echo.
echo ========================================================
echo Code is successfully pushed to GitHub!
echo Now go to https://render.com and deploy for free.
echo ========================================================
pause
