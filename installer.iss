; Script Inno Setup pour Tello Face Tracking
; Compatible Windows 7 et supérieur
; Usage: Compiler avec Inno Setup Compiler

#define MyAppName "Tello Face Tracking"
#define MyAppVersion "1.0"
#define MyAppPublisher "Tello Face Tracking"
#define MyAppURL "https://github.com/yourusername/yolo-face"
#define MyAppExeName "TelloFaceTracking.exe"
#define MyAppId "{{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}"

[Setup]
; Informations de base
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=
InfoBeforeFile=
InfoAfterFile=
OutputDir=installer
OutputBaseFilename=TelloFaceTracking-Setup
SetupIconFile=
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Compatibilité Windows 7+
MinVersion=6.1

; Interface
WizardImageFile=
WizardSmallImageFile=

; Permissions
ChangesAssociations=no
ChangesEnvironment=no

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Exécutable principal
Source: "dist\TelloFaceTracking.exe"; DestDir: "{app}"; Flags: ignoreversion
; Modèle YOLO (si non inclus dans l'exe)
; Source: "yolov8n-face.pt"; DestDir: "{app}"; Flags: ignoreversion; Check: FileExists(ExpandConstant('{app}\yolov8n-face.pt')) = False

; DLL et dépendances supplémentaires si nécessaire
; Source: "dist\*.dll"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Vérification de l'espace disque disponible (minimum 2 GB recommandé)
function InitializeSetup(): Boolean;
var
  FreeSpace: Int64;
begin
  FreeSpace := DiskFreeSpace(ExpandConstant('{app}'));
  if FreeSpace < 2147483648 then // 2 GB en octets
  begin
    MsgBox('Attention: L''installation nécessite au moins 2 GB d''espace disque libre.' + #13#10 +
           'Espace disponible: ' + FormatByteSize(FreeSpace), mbError, MB_OK);
    Result := False;
  end
  else
    Result := True;
end;

// Vérification de la version de Windows
function InitializeUninstall(): Boolean;
begin
  Result := True;
end;

