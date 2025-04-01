[Setup]
AppName=RwG DayZ Launcher
AppVersion=1.0.0
DefaultDirName={autopf}\RwG DayZ Launcher
DefaultGroupName=RwG DayZ Launcher
OutputBaseFilename=RwGLauncherSetup
Compression=lzma
SolidCompression=yes
[Files]
Source: "dist\RwG DayZ Launcher.exe"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{commondesktop}\RwG DayZ Launcher"; Filename: "{app}\RwG DayZ Launcher.exe"
