@echo off
set /p VERSION=Welche Version möchtest du veröffentlichen? (z. B. 1.0.1): 
echo %VERSION% > version.txt
git add version.txt
git commit -m "Release v%VERSION%"
git tag v%VERSION%
git push
git push origin v%VERSION%
