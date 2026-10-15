"""책장 넘기는 소리 (1015) — 마스터 노트 책상의 소품(마스터 육성 · 튜토리얼 · 스케줄 · 학생 명부)을 누를 때

    python3 tools/gen/sfx/book_flip.py          # 저장소 맨 위에서 (numpy · scipy · ffmpeg) · 몇 번 돌려도 같다 (난수 씨앗 고정)

녹음 소리를 받아 올 수 없어(작업 공간의 인터넷이 막혀 있다) 종이 소리를 합성했다 — bgm/book_flip1 · 2 · 3.ogg (게임은 셋 중 하나를 빠르기 ±6% 로).
더 나은 녹음이 있으면 같은 이름의 .ogg 로 bgm/ 에 덮어쓰면 소리만 바뀐다 (game.html SFX 표의 book_flip1 ~ 3).
만드는 법: ① 책장을 드는 바스락(작은 종이 튐 몇 개) → ② 휙 넘어가는 바람 소리(잡음 · 밝기가 오르내리는 저역 통과 · 종이가 떠는 진폭 흔들림 ·
그동안 종이 튐이 잦아진다) → ③ 내려앉는 '탁'(짧은 잡음 + 낮은 울림) → 짧은 꼬리. 봉우리 −4 dBFS · 50ms 창 RMS 최대 −18 dB 안팎.
"""
import os, subprocess, tempfile, wave
import numpy as np
from scipy import signal as sg

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SR = 48000
VARIANTS = [   # 씨앗 · 길이 · 휙 가운데 · 내려앉는 때 · 밝기(최고 차단 주파수) · 떨림
    dict(seed=11, L=.58, tc=.19, tl=.37, fmax=5200, flut=22),
    dict(seed=23, L=.54, tc=.17, tl=.33, fmax=6000, flut=27),
    dict(seed=37, L=.62, tc=.22, tl=.40, fmax=4600, flut=19),
]


def bpass(x, lo, hi, order=4):
    return sg.sosfilt(sg.butter(order, [lo, hi], "bandpass", fs=SR, output="sos"), x)


def lpass(x, f, order=4):
    return sg.sosfilt(sg.butter(order, f, "lowpass", fs=SR, output="sos"), x)


def hpass(x, f, order=4):
    return sg.sosfilt(sg.butter(order, f, "highpass", fs=SR, output="sos"), x)


def grain(rng, n, lo, hi):
    """짧은 종이 튐 — 고역 잡음을 빠르게 사그라뜨린다"""
    g = bpass(rng.standard_normal(n + 64), lo, hi, 2)[64:]
    a = max(2, int(SR * .0003))                                          # 0.3ms 로 살짝 열어 딱딱한 클릭이 되지 않게
    g[:a] *= np.linspace(0, 1, a)
    return g * np.exp(-np.arange(n) / (n * .28))


def make(V):
    rng = np.random.default_rng(V["seed"])
    n = int(SR * V["L"]); t = np.arange(n) / SR
    out = np.zeros(n)
    # ② 휙 — 잡음의 짧은 구간마다 저역 통과 차단 주파수를 바꾼다 (STFT 로 스펙트럼 모양을 곱한다)
    f, tt, Z = sg.stft(rng.standard_normal(n), fs=SR, nperseg=1024, noverlap=768)
    tc, tl = V["tc"], V["tl"]
    for k, tk in enumerate(tt):
        u = np.clip((tk - .02) / (tl - .02), 0, 1)                      # 0 → 1 (든 때 → 내려앉는 때)
        fc = 1400 + (V["fmax"] - 1400) * np.sin(np.pi * u) ** 1.3       # 가운데서 가장 밝다
        shape = 1 / np.sqrt(1 + (f / fc) ** 6) * (1 - np.exp(-(f / 260) ** 2))
        Z[:, k] *= shape
    sw = sg.istft(Z, fs=SR, nperseg=1024, noverlap=768)[1][:n]
    s1, s2 = .075, .095
    env = np.where(t < tc, np.exp(-.5 * ((t - tc) / s1) ** 2), np.exp(-.5 * ((t - tc) / s2) ** 2))
    flut = 1 + .38 * lpass(rng.standard_normal(n), V["flut"], 2) / .08 + .18 * np.sin(2 * np.pi * V["flut"] * t + rng.uniform(0, 6))
    sw = sw / (np.abs(sw).max() + 1e-9) * env * np.clip(flut, .2, 2)
    out += sw
    # ① · ② 종이 튐 — 처음 든 때 몇 개 + 휙 동안 잦게
    def crack(at, amp, ms):
        k = int(at * SR); m = int(SR * ms / 1000)
        if k + m >= n: return
        out[k:k + m] += amp * grain(rng, m, 2600, 9000) / .3
    for _ in range(6):
        crack(rng.uniform(.004, .06), rng.uniform(.08, .2), rng.uniform(.6, 2.2))
    for _ in range(int(rng.integers(40, 58))):
        at = rng.normal(tc, .09)
        if .03 < at < tl - .01:
            e = np.exp(-.5 * ((at - tc) / .1) ** 2)
            crack(at, rng.uniform(.04, .18) * e, rng.uniform(.4, 1.8))
    # ③ 내려앉는 '탁' — 짧은 잡음 + 낮은 울림, 뒤에 작은 바스락 몇 개
    k0 = int(tl * SR); m = int(SR * .05)
    fl = lpass(rng.standard_normal(m), 2400, 2) * np.exp(-np.arange(m) / (SR * .011))
    fl[:int(SR * .002)] *= np.linspace(0, 1, int(SR * .002))
    out[k0:k0 + m] += .55 * fl / (np.abs(fl).max() + 1e-9)
    m2 = int(SR * .08); f0 = rng.uniform(150, 190)
    th = np.sin(2 * np.pi * f0 * np.arange(m2) / SR) * np.exp(-np.arange(m2) / (SR * .016))
    out[k0:k0 + m2] += .22 * th
    for _ in range(4):
        crack(tl + rng.uniform(.01, .07), rng.uniform(.04, .1), rng.uniform(.5, 1.5))
    # 마무리 — 저역 덜어내기 · 끝 페이드 · 크기
    out = hpass(out, 110, 2)
    fade = int(SR * .03); out[-fade:] *= np.linspace(1, 0, fade); out[:48] *= np.linspace(0, 1, 48)
    out /= np.abs(out).max() + 1e-9
    win = int(SR * .05); rms = np.sqrt(np.convolve(out * out, np.ones(win) / win, "valid")).max()
    out *= min(10 ** (-18 / 20) / rms, 10 ** (-4 / 20))                    # 50ms RMS −18 dB · 봉우리는 −4 dBFS 넘지 않게
    return out


def write_ogg(x, path):
    with tempfile.TemporaryDirectory() as d:
        wp = os.path.join(d, "a.wav")
        with wave.open(wp, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wp, "-c:a", "libvorbis", "-q:a", "6", "-ac", "1", "-ar", "48000",
                        "-map_metadata", "-1", "-fflags", "+bitexact", "-flags:a", "+bitexact", path], check=True)


def main():
    for i, V in enumerate(VARIANTS, 1):
        x = make(V)
        p = os.path.join(ROOT, "bgm", "book_flip%d.ogg" % i)
        write_ogg(x, p)
        win = int(SR * .05); rms = np.sqrt(np.convolve(x * x, np.ones(win) / win, "valid")).max()
        print("bgm/book_flip%d.ogg  %.2f초 · 봉우리 %.1f dBFS · 50ms RMS %.1f dB · %d B"
              % (i, len(x) / SR, 20 * np.log10(np.abs(x).max()), 20 * np.log10(rms), os.path.getsize(p)))


if __name__ == "__main__":
    main()
