#!/bin/sh
# 실행기 HeroSchool.exe 빌드 (1102) — 리눅스 클라우드: apt-get install gcc-mingw-w64-x86-64 binutils-mingw-w64-x86-64 (윈도에서는 MSYS2 mingw-w64 로 같은 명령)
#   sh desktop/launcher/build.sh      → desktop/launcher/HeroSchool.exe (electron-builder 가 win-unpacked 맨 위에 넣는다 — package.json build.extraFiles)
set -e
cd "$(dirname "$0")"
x86_64-w64-mingw32-windres --codepage=65001 -O coff launcher.rc -o launcher.res.o
x86_64-w64-mingw32-gcc -municode -mwindows -O2 -s -Wall -Wextra -o HeroSchool.exe launcher.c launcher.res.o \
  -Wl,--dynamicbase,--nxcompat,--high-entropy-va -static-libgcc
rm -f launcher.res.o
ls -l HeroSchool.exe
