/* 용사 학원 키우기 — 실행기 HeroSchool.exe (1102 · desktop/launcher)
 *
 * 왜: STOVE DRM Maker 는 고른 exe 에 DrmCheckerV3.dll 을 import 로 넣는다 (그 DLL 은 D3D · DXGI · GL 을 가로채는 오버레이 + 소유 확인).
 *   Electron 본체는 GPU · 화면 · 네트워크 하위 프로세스를 자기 exe 를 다시 띄워(--type=…) 만들어서, 본체에 DRM 을 입히면 하위 프로세스마다
 *   DrmChecker 가 돌아 게임이 켜지자마자 꺼졌다 (사용자 1102 — STOVE 테스트 빌드 52448 · '플레이를 누르면 잠시 게임 창이 켜졌다가 순식간에 바로 창이 닫히면서 꺼져').
 *   그래서 DRM 은 이 작은 실행기에만 입히고, 실행기가 본체 HeroSchoolGame.exe 를 띄운다.
 * 하는 일:
 *   · 같은 폴더의 HeroSchoolGame.exe 를 받은 인자 그대로 띄우고 끝날 때까지 기다린다 — STOVE 플레이 시간 · DRM 확인은 이 프로세스로 · 끝 코드도 그대로
 *   · 환경 변수 HS_LAUNCHER=1 — 본체(main.js)가 실행기를 거쳐 켜졌는지 안다 (본체를 바로 켜면 본체가 실행기로 다시 켠다)
 *   · 작업 개체(KILL_ON_JOB_CLOSE) — 실행기가 끝나면(STOVE · DRM 이 끝내도) 게임도 같이 끝난다
 *   · 본체가 없거나 못 띄우면 알림 창 (한국어 · 영어)
 * 빌드: desktop/launcher/build.sh (mingw-w64 · 클라우드) — 만든 HeroSchool.exe 를 이 폴더에 두면 electron-builder 가 win-unpacked 맨 위에 넣는다 (package.json build.extraFiles)
 */
#define WIN32_LEAN_AND_MEAN
#ifndef UNICODE
#define UNICODE
#endif
#ifndef _UNICODE
#define _UNICODE
#endif
#include <windows.h>
#include <wchar.h>
#include <stdio.h>

#define GAME_EXE L"HeroSchoolGame.exe"
#define TITLE L"용사 학원 키우기"
#define BUF (MAX_PATH * 8)

/* 명령줄의 첫 토큰(이 실행기 경로)을 건너뛴 나머지 — CommandLineToArgvW 와 같은 규칙 (따옴표면 다음 따옴표까지 · 아니면 공백까지) */
static const wchar_t *after_arg0(const wchar_t *c){
  if(!c) return L"";
  if(*c == L'"'){ c++; while(*c && *c != L'"') c++; if(*c == L'"') c++; }
  else { while(*c && *c != L' ' && *c != L'\t') c++; }
  while(*c == L' ' || *c == L'\t') c++;
  return c;
}

static void fail(const wchar_t *what, const wchar_t *exe, DWORD err){
  wchar_t msg[BUF + 512];
  _snwprintf(msg, sizeof msg / sizeof msg[0],
    L"게임을 시작하지 못했습니다. (%ls · %lu)\n"
    L"STOVE 에서 파일 검사 또는 다시 설치를 해 주세요.\n\n"
    L"Could not start the game (%ls · %lu).\n%ls", what, err, what, err, exe);
  msg[sizeof msg / sizeof msg[0] - 1] = 0;
  MessageBoxW(NULL, msg, TITLE, MB_ICONERROR | MB_OK | MB_SETFOREGROUND);
}

int WINAPI wWinMain(HINSTANCE inst, HINSTANCE prev, PWSTR cmd, int show){
  (void)inst; (void)prev; (void)cmd; (void)show;
  static wchar_t self[BUF], dir[BUF], exe[BUF];
  DWORD n = GetModuleFileNameW(NULL, self, BUF);
  if(!n || n >= BUF){ fail(L"path", L"", GetLastError()); return 1; }
  wcscpy(dir, self);
  wchar_t *cut = wcsrchr(dir, L'\\');
  if(cut) *cut = 0;
  _snwprintf(exe, BUF, L"%ls\\%ls", dir, GAME_EXE);
  exe[BUF - 1] = 0;
  if(GetFileAttributesW(exe) == INVALID_FILE_ATTRIBUTES){ fail(GAME_EXE, exe, GetLastError()); return 2; }

  const wchar_t *rest = after_arg0(GetCommandLineW());
  size_t len = wcslen(exe) + wcslen(rest) + 8;
  wchar_t *line = (wchar_t *)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, len * sizeof(wchar_t));
  if(!line){ fail(L"memory", exe, GetLastError()); return 3; }
  _snwprintf(line, len, L"\"%ls\"%ls%ls", exe, *rest ? L" " : L"", rest);

  SetEnvironmentVariableW(L"HS_LAUNCHER", L"1");

  HANDLE job = CreateJobObjectW(NULL, NULL);                  /* 실행기가 끝나면 게임도 — 하위 프로세스는 Chromium 이 따로 묶을 수 있게 BREAKAWAY_OK */
  if(job){
    JOBOBJECT_EXTENDED_LIMIT_INFORMATION li;
    ZeroMemory(&li, sizeof li);
    li.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE | JOB_OBJECT_LIMIT_BREAKAWAY_OK;
    if(!SetInformationJobObject(job, JobObjectExtendedLimitInformation, &li, sizeof li)){ CloseHandle(job); job = NULL; }
  }

  STARTUPINFOW si;
  PROCESS_INFORMATION pi;
  ZeroMemory(&si, sizeof si); si.cb = sizeof si;
  ZeroMemory(&pi, sizeof pi);
  if(!CreateProcessW(exe, line, NULL, NULL, FALSE, CREATE_SUSPENDED | CREATE_UNICODE_ENVIRONMENT, NULL, dir, &si, &pi)){
    fail(GAME_EXE, exe, GetLastError());
    return 4;
  }
  if(job && !AssignProcessToJobObject(job, pi.hProcess)){ CloseHandle(job); job = NULL; }   /* 묶지 못해도 게임은 그대로 */
  ResumeThread(pi.hThread);
  CloseHandle(pi.hThread);
  WaitForSingleObject(pi.hProcess, INFINITE);
  DWORD code = 0;
  if(!GetExitCodeProcess(pi.hProcess, &code)) code = 0;
  CloseHandle(pi.hProcess);
  HeapFree(GetProcessHeap(), 0, line);
  if(job) CloseHandle(job);                                    /* 남은 하위 프로세스가 있으면 같이 끝난다 */
  return (int)code;
}
