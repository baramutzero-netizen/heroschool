@echo off
chcp 65001 >nul
rem 스팀 체험판 올리기 — 더블클릭하면 스팀 계정 이름을 묻는다 (또는: upload_demo.bat 스팀계정이름)
rem steamcmd — STEAMCMD 에 경로가 있으면 그것 · 없으면 D:\steamcmd\steamcmd.exe · 그것도 없으면 PATH 의 steamcmd.exe
rem 비밀번호 · Steam Guard 코드는 steamcmd 가 직접 묻는다 (어디에도 적지 않는다)
rem 1124 — 더블클릭하면 창이 바로 닫혀 보이지 않던 것을 고쳤다 (계정 이름을 묻고 · 끝나면 멈춘다)
setlocal
set ACC=%~1
if "%ACC%"=="" set /p ACC=스팀 계정 이름:
if "%ACC%"=="" ( echo 계정 이름이 없어 멈춘다. & goto :end )
findstr /c:"DEMO_APPID" /c:"DEMO_DEPOTID" "%~dp0app_build_demo.vdf" "%~dp0depot_build_demo.vdf" >nul && ( echo vdf 에 DEMO_APPID / DEMO_DEPOTID 가 아직 남아 있다 — 앱 ID · depot ID 로 바꾼다 & goto :end )
if not exist "%~dp0..\dist-demo\win-unpacked\HeroSchool.exe" ( echo dist-demo\win-unpacked 가 없다 — desktop 에서 npm run dist:demo 먼저 & goto :end )
if "%STEAMCMD%"=="" if exist "D:\steamcmd\steamcmd.exe" set STEAMCMD=D:\steamcmd\steamcmd.exe
if "%STEAMCMD%"=="" set STEAMCMD=steamcmd.exe
echo steamcmd: %STEAMCMD%
"%STEAMCMD%" +login %ACC% +run_app_build "%~dp0app_build_demo.vdf" +quit
echo.
echo 끝 — 위에 'Successfully finished' 가 보이면 Steamworks SteamPipe ^> Builds 에서 새 빌드를 default 브랜치에 지정한다.
:end
echo.
pause
