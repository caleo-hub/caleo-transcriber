#ifndef AppVersion
  #error AppVersion is required
#endif
#ifndef SourceDir
  #error SourceDir is required
#endif
#ifndef OutputDir
  #error OutputDir is required
#endif

[Setup]
AppId={{6B4DB72C-5FB6-49F3-80D6-CB35DA06EF10}
AppName=Caleo Transcriber
AppVersion={#AppVersion}
AppPublisher=caleo-hub
AppPublisherURL=https://github.com/caleo-hub/caleo-transcriber
AppSupportURL=https://github.com/caleo-hub/caleo-transcriber/issues
DefaultDirName={localappdata}\Programs\Caleo Transcriber
DefaultGroupName=Caleo Transcriber
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.19045
UninstallDisplayIcon={app}\CaleoTranscriber.exe
OutputDir={#OutputDir}
OutputBaseFilename=CaleoTranscriber-Setup-{#AppVersion}-x64
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern dynamic
SetupLogging=yes
CloseApplications=yes
RestartApplications=no
VersionInfoVersion={#AppVersion}.0
VersionInfoCompany=caleo-hub
VersionInfoDescription=Instalador do Caleo Transcriber
VersionInfoProductName=Caleo Transcriber
VersionInfoProductVersion={#AppVersion}

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Caleo Transcriber"; Filename: "{app}\CaleoTranscriber.exe"

[Run]
Filename: "{app}\CaleoTranscriber.exe"; Description: "Abrir Caleo Transcriber"; Flags: nowait postinstall skipifsilent
