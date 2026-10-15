"""스타일리시 전투 체크포인트 효과음 (1015) — 목업의 WebAudio 짧은 삑을 같은 파형으로 합성해 bgm/*.ogg 로

    python3 tools/gen/heroic/sfx_synth.py          # 저장소 맨 위에서 (ffmpeg 가 있어야 한다)

사용자 1015: '스타일리시 전투에서 임의로 사용한 슬롯 관련 사운드들하고 정신력 시험에서 사용한 두근두근 사운드하고
불굴의 의지 발생했을 때 사운드 · 기절 사운드도 같이 적용'.
목업(mockups/stylish-checkpoint · heroic-resolve 의 page_tpl.html — beep(주파수, ms, 파형, 크기, 미끄럼, 늦춤))을 그대로 옮겼다:
진폭은 지수로 0.0001 까지 · 주파수 미끄럼도 지수 · 파형은 WebAudio 처럼 대역 제한(배음 합) 후 봉우리 1.
파일은 봉우리 −6 dBFS 로 맞추고, 목업에서 들리던 크기 비는 game.html SFX 표의 v 로 되살린다 (아래 V — 설정 효과음 70 에서 목업과 같은 크기).
"""
import math, os, subprocess, tempfile, wave
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SR = 48000


def osc_table(kind, n):
    """한 주기 φ ∈ [0, 2π) 의 배음 계수 — (k, a_k) · 봉우리 1 로 맞출 값도 함께"""
    if kind == "sine":
        ks = [1]; amps = [1.0]
    elif kind == "square":
        ks = list(range(1, n + 1, 2)); amps = [4 / math.pi / k for k in ks]
    elif kind == "sawtooth":
        ks = list(range(1, n + 1)); amps = [2 / math.pi * ((-1) ** (k + 1)) / k for k in ks]
    elif kind == "triangle":
        ks = list(range(1, n + 1, 2)); amps = [8 / math.pi ** 2 * ((-1) ** ((k - 1) // 2)) / k ** 2 for k in ks]
    else:
        raise ValueError(kind)
    ph = np.linspace(0, 2 * math.pi, 4096, endpoint=False)
    w = sum(a * np.sin(k * ph) for k, a in zip(ks, amps))
    return ks, amps, 1 / max(1e-9, float(np.abs(w).max()))


def beep(f, ms, kind="square", vol=.05, slide=None, delay=0):
    """WebAudio: o.frequency f → (slide 면) 지수로 slide 까지 · g.gain vol → 지수로 .0001 까지 ms 동안 · ms+20 에서 멈춘다"""
    d = ms / 1000; n = int(round((d + .02) * SR)); t = np.arange(n) / SR
    tt = np.minimum(t, d)
    if slide:
        r = slide / f
        phase = 2 * math.pi * f * d / math.log(r) * (r ** (tt / d) - 1)
        phase = phase + 2 * math.pi * slide * np.maximum(0, t - d)          # 미끄럼이 끝난 뒤 (멈출 때까지 20ms)
        fmax = max(f, slide)
    else:
        phase = 2 * math.pi * f * t; fmax = f
    ks, amps, norm = osc_table(kind, max(1, int((SR / 2 * .95) // fmax)))
    w = sum(a * np.sin(k * phase) for k, a in zip(ks, amps)) * norm
    g = vol * (.0001 / vol) ** (tt / d)
    g[t > d] = .0001
    y = w * g
    y[-int(.004 * SR):] *= np.linspace(1, 0, int(.004 * SR))                # 멈출 때 딸깍 없게 (4ms)
    return int(round(delay / 1000 * SR)), y


def mix(parts):
    end = max(o + len(y) for o, y in parts)
    out = np.zeros(end)
    for o, y in parts:
        out[o:o + len(y)] += y
    return out


# 목업 그대로 (stylish-checkpoint SND · heroic-resolve SND)
SOUNDS = {
    "pick_snap":   [beep(880, 60, "square", .045)],                                             # 기본기 상자 — 확정이라 바로 촥
    "pick_spin":   [beep(450, 25, "square", .012)],                                             # 슬롯이 도는 동안 70ms 마다 (게임은 빠르기 .93 ~ 1.07 로 420 ~ 480Hz)
    "pick_land":   [beep(988, 70, "square", .045), beep(1319, 110, "square", .04, delay=60)],   # 뜬 스킬이 꽂힌다
    "pick_fail":   [beep(160, 160, "sawtooth", .05, 90)],                                       # 안 뜬 스킬 — X
    "pick_hop":    [beep(1200, 22, "square", .03)],                                             # 하이라이트가 한 칸 옮길 때
    "pick_choose": [beep(784, 80, "triangle", .07), beep(1175, 160, "triangle", .07, delay=80)],  # 고름
    "pick_resist": [beep(110, 220, "sawtooth", .08, 55), beep(70, 260, "square", .05)],         # RESIST 딱지
    "pick_ok":     [beep(1568, 90, "triangle", .05)],                                           # 시전 성공 금빛 링
    "test_beat":   [beep(62, 120, "sine", .22), beep(55, 140, "sine", .18, delay=170)],         # 정신력 시험 — 두근 (0.8초마다)
    "test_hero":   [beep(fq, 260, "triangle", .06, delay=i * 70) for i, fq in enumerate([523, 659, 784, 1047, 1319])],   # 기상 — 오르는 다섯 음
    "test_faint":  [beep(330, 600, "sawtooth", .05, 70), beep(165, 700, "square", .03, 50, delay=80)],                   # 기절 — 내려앉는 소리
}
PEAK = .5            # 파일 봉우리 −6 dBFS (게임의 다른 효과음과 같은 높이)
G = 1 / .49          # 설정 효과음 70(sfxGain .49)에서 목업(WebAudio 크기 1)과 같은 크기가 되게


def main():
    out = os.path.join(ROOT, "bgm")
    os.makedirs(out, exist_ok=True)
    V = {}
    for name, parts in SOUNDS.items():
        y = mix(parts)
        p = float(np.abs(y).max())
        V[name] = round(min(1, p * G / PEAK), 3)
        y = y * (PEAK / p)
        pcm = (np.clip(y, -1, 1) * 32767).astype("<i2")
        with tempfile.TemporaryDirectory() as td:
            wav = os.path.join(td, name + ".wav")
            with wave.open(wav, "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
            dst = os.path.join(out, name + ".ogg")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", "libvorbis", "-q:a", "6", "-ar", str(SR), "-ac", "1", dst], check=True)
        print("%-12s %5.0f ms  봉우리(목업) %.3f → v %.3f  %5.1f KB" % (name, len(y) / SR * 1000, p, V[name], os.path.getsize(dst) / 1024))
    print("SFX 표의 v:", V)


if __name__ == "__main__":
    main()
