[Setup]
AppName=SovAuto
AppVersion=1.0.3
DefaultDirName={autopf}\SovAuto
DefaultGroupName=SovAuto
OutputDir=dist_installer
OutputBaseFilename=SovAuto-Setup-1.0.3
SetupIconFile=build\branding\sovauto.ico
WizardImageFile=build\branding\wizard-image.bmp
WizardSmallImageFile=build\branding\wizard-small.bmp
UninstallDisplayIcon={app}\SovAuto.exe
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "dist\SovAuto\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Icons]
Name: "{group}\SovAuto"; Filename: "{app}\SovAuto.exe"; IconFilename: "{app}\SovAuto.exe"
Name: "{autodesktop}\SovAuto"; Filename: "{app}\SovAuto.exe"; Tasks: desktopicon; IconFilename: "{app}\SovAuto.exe"

[Run]
Filename: "{app}\SovAuto.exe"; Description: "Launch SovAuto"; Flags: nowait postinstall skipifsilent

[Code]
var
  DeleteUserData: Boolean;

function GetUserDataDir: string;
begin
  Result := ExpandConstant('{userappdata}\SovAuto');
end;

function WantDeleteUserData: Boolean;
var
  I: Integer;
begin
  Result := False;
  for I := 1 to ParamCount do
  begin
    if CompareText(ParamStr(I), '/DELETEUSERDATA=1') = 0 then
    begin
      Result := True;
      exit;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then
  begin
    DeleteUserData := WantDeleteUserData;
    if (not DeleteUserData) and (not UninstallSilent) then
    begin
      DeleteUserData := MsgBox(
        'Delete SovAuto user data from AppData as well?',
        mbConfirmation,
        MB_YESNO
      ) = IDYES;
    end;
    if DeleteUserData and DirExists(GetUserDataDir) then
      DelTree(GetUserDataDir, True, True, True);
  end;
end;



