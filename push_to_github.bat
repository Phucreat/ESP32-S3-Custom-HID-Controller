@echo off
chcp 65001 > nul
echo === PUSH REPO TO GITHUB ===
set /p REPO_URL=Nhap GitHub Repo URL: 
git init
git branch -M main
git add .
git commit -m feat: Initial release of ESP32-S3 Custom USB HID Controller
git remote remove origin 2>nul
git remote add origin %REPO_URL%
git push -u origin main
pause
