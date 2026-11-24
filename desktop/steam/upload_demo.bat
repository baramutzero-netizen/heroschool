@echo off
chcp 65001 >nul
rem 스팀 체험판 올리기 — 사용: upload_demo.bat 스팀계정이름
rem steamcmd.exe 가 PATH 에 있거나 STEAMCMD 에 경로를 넣는다 (예: set STEAMCMD=C:\steamcmd\steamcmd.exe)
rem 비밀번호 · Steam Guard 코드는 steamcmd 가 직접 묻는다 (어디에도 적지 않는다)
setlocal
if "%~1"=="" ( echo 사용: upload_demo.bat 스팀계정이름 & exit /b 1 )
findstr /c:"DEMO_APPID" /c:"DEMO_DEPOTID" "%~dp0app_build_demo.vdf" "%~dp0depot_build_demo.vdf" >nul && ( echo vdf 에 DEMO_APPID / DEMO_DEPOTID 가 아직 남아 있다 — 앱 ID · depot ID 로 바꾼다 & exit /b 1 )
if not exist "%~dp0..\dist-demo\win-unpacked\HeroSchool.exe" ( echo dist-demo\win-unpacked 가 없다 — desktop 에서 npm run dist:demo 먼저 & exit /b 1 )
if "%STEAMCMD%"=="" set STEAMCMD=steamcmd.exe
"%STEAMCMD%" +login %1 +run_app_build "%~dp0app_build_demo.vdf" +quit
