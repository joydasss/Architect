"""Audio basics, standard library only: frames, FFT, mel bins, WER, CTC.

Uses a synthetic signal so no audio file is needed.
"""
import cmath
import math


def fft(x):
    n = len(x)
    if n == 1:
        return list(x)
    even, odd = fft(x[0::2]), fft(x[1::2])
    out = [0j] * n
    for k in range(n // 2):
        t = cmath.exp(-2j * math.pi * k / n) * odd[k]
        out[k], out[k + n // 2] = even[k] + t, even[k] - t
    return out


def frame_count(n_samples, win, hop):
    return 1 + (n_samples - win) // hop


def hz_to_mel(f):
    return 2595 * math.log10(1 + f / 700)


def mel_to_hz(m):
    return 700 * (10 ** (m / 2595) - 1)


def mel_bin_edges(n_mels, n_fft, sr):
    step = (hz_to_mel(sr / 2) - hz_to_mel(0)) / (n_mels + 1)
    return [int((n_fft + 1) * mel_to_hz(i * step) / sr) for i in range(n_mels + 2)]


def wer(ref, hyp):
    r, h = ref.split(), hyp.split()
    d = [[0] * (len(h) + 1) for _ in range(len(r) + 1)]
    for i in range(len(r) + 1):
        d[i][0] = i
    for j in range(len(h) + 1):
        d[0][j] = j
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            cost = 0 if r[i - 1] == h[j - 1] else 1
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost)
    return d[-1][-1] / len(r)


def ctc_greedy(path, blank="_"):
    """Collapse repeats, then drop blanks."""
    out, prev = [], None
    for s in path:
        if s != prev and s != blank:
            out.append(s)
        prev = s
    return "".join(out)


if __name__ == "__main__":
    sr, win, hop, n_fft = 16_000, 400, 160, 512
    n = sr * 2
    x = [math.sin(2 * math.pi * 440 * i / sr) + 0.5 * math.sin(2 * math.pi * 1200 * i / sr)
         for i in range(n)]
    print(f"samples={n}  frames={frame_count(n, win, hop)} (25 ms window, 10 ms hop)")
    frame = [x[i] * (0.5 - 0.5 * math.cos(2 * math.pi * i / (win - 1))) for i in range(win)]
    frame += [0.0] * (n_fft - win)
    mag = [abs(c) for c in fft(frame)[: n_fft // 2 + 1]]
    top = sorted(range(len(mag)), key=lambda k: -mag[k])[:2]
    print(f"bin width {sr / n_fft:.2f} Hz; two strongest bins {sorted(top)} -> "
          f"{[round(k * sr / n_fft) for k in sorted(top)]} Hz (tones at 440 and 1200 Hz)")
    edges = mel_bin_edges(80, n_fft, sr)
    print(f"80 mel bins; first edges {edges[:6]} ... last {edges[-3:]} (FFT bins 0..256)")
    print(f"mel frame rate {sr // hop} per second; after 4x stacking 25 per second "
          f"-> 30 s = {30 * 25} audio tokens")

    ref = "please cancel my order number four seven two"
    hyp = "please cancel my order number for seven two"
    print(f"\nWER = {wer(ref, hyp):.3f}  (1 substitution in 8 words)")
    hyp2 = "please cancel order number four seven two now"
    print(f"WER = {wer(ref, hyp2):.3f}  (1 deletion + 1 insertion in 8 words)")

    print(f"\nCTC path hh_e_ll_ll_oo -> {ctc_greedy('hh_e_ll_ll_oo')}")
    print(f"CTC path hhel_lloo -> {ctc_greedy('hhel_lloo')}  (blank separates the double l)")

    print()
    for name, fps, books, bits in [("RVQ 75 Hz x 8 codebooks x 10 bit", 75, 8, 10),
                                   ("RVQ 12.5 Hz x 8 codebooks x 11 bit", 12.5, 8, 11)]:
        print(f"{name}: {fps * books * bits / 1000:.2f} kbps, {fps * books:.0f} tokens/s")
    print(f"raw 16 kHz 16-bit mono PCM: {sr * 16 / 1000:.0f} kbps")
