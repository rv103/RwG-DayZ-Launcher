@echo off
set /p VERSION=Neue Version (z. B. 1.0.1): 
echo %VERSION% > version.txt
pyinstaller --noconsole --onefile --name "RwG DayZ Launcher" src\RwG_Launcher.py
mkdir release
copy dist\"RwG DayZ Launcher.exe" release\
copy version.txt release\
powershell -Command "Compress-Archive -Path release\* -DestinationPath RwG_Launcher_v%VERSION%.zip"
git add version.txt
git commit -m "Release v%VERSION%"
git tag v%VERSION%
git push
git push origin v%VERSION%
