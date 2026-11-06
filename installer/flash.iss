; Inno Setup script for Flash. Built by scripts\build.ps1 (ISCC.exe installer\flash.iss /DAppVersion=x.y.z).
; Packages the one-folder PyInstaller build in dist\Flash. Keep AppId unchanged so upgrades replace old versions.
#ifndef AppVersion
  #define AppVersion "3.1.0"
#endif
#define AppName "Flash"
#define AppExe  "Flash.exe"

[Setup]
AppId={{9BA915AD-004E-4E4D-8324-96DD1D1935E5}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher=Mohamed Gueni
AppPublisherURL=https://github.com/Gueni/flash
AppSupportURL=https://github.com/Gueni/flash/issues
AppComments=Flash, inspect and secure ESP32 / ESP8266 chips
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\release
OutputBaseFilename=Flash-{#AppVersion}-Setup
SetupIconFile=..\src\flash\assets\flash.ico
UninstallDisplayIcon={app}\{#AppExe}
UninstallDisplayName={#AppName} {#AppVersion}
VersionInfoVersion={#AppVersion}
VersionInfoProductName={#AppName}
VersionInfoCompany=Mohamed Gueni
CloseApplications=yes
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[InstallDelete]
; drop files of a previous version so stale libraries never mix with new ones
Type: filesandordirs; Name: "{app}\_internal"

[Files]
Source: "..\dist\Flash\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\tests\micropython-esp32\*.bin"; DestDir: "{app}\samples\micropython-esp32"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExe}"; Comment: "ESP32 / ESP8266 flashing toolkit"
Name: "{autoprograms}\{#AppName} sample firmware"; Filename: "{app}\samples"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent
