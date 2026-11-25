@echo off
chcp 65001 >nul
rem 스팀 본편 올리기 (1125) — 더블클릭하면 스팀 계정 이름을 묻는다 (또는: upload_main.bat 스팀계정이름)
rem 본편 앱 5658660 · depot 5658661 (My Hero's Academy) — 데모(upload_demo.bat · 앱 5670460)와 다른 앱이다
rem steamcmd — STEAMCMD 에 경로가 있으면 그것 · 없으면 D:\steamcmd\steamcmd.exe · 그것도 없으면 PATH 의 steamcmd.exe
rem 비밀번호 · Steam Guard 코드는 steamcmd 가 직접 묻는다 (어디에도 적지 않는다)
setlocal
set ACC=%~1
if "%ACC%"=="" set /p ACC=스팀 계정 이름:
if "%ACC%"=="" ( echo 계정 이름이 없어 멈춘다. & goto :end )
set ROOT=%~dp0..\dist\win-unpacked
if not exist "%ROOT%\HeroSchool.exe" ( echo dist\win-unpacked 가 없다 — desktop 에서 npm run dist 먼저 & goto :end )
rem 체험판이 본편으로 올라가지 않게 — 정식판 빌드는 app.asar 안이 'const DEMO_END = null;' 이다 (체험판은 끝 주차가 채워져 있다)
findstr /c:"const DEMO_END = null;" "%ROOT%\resources\app.asar" >nul || ( echo dist\win-unpacked 가 체험판 빌드다 — desktop 에서 npm run dist 로 정식판을 다시 만든다 & goto :end )
if "%STEAMCMD%"=="" if exist "D:\steamcmd\steamcmd.exe" set STEAMCMD=D:\steamcmd\steamcmd.exe
if "%STEAMCMD%"=="" set STEAMCMD=steamcmd.exe
echo steamcmd: %STEAMCMD%
"%STEAMCMD%" +login %ACC% +run_app_build "%~dp0app_build_main.vdf" +quit
echo.
echo 끝 — 위에 'Successfully finished' 가 보이면 Steamworks 본편 앱(5658660) SteamPipe ^> Builds 에서 새 빌드를 default 브랜치에 지정한다.
:end
echo.
pause
