"""Rebuild video with optional tools: pip install numpy pillow imageio-ffmpeg."""
from pathlib import Path
import math
import os
import subprocess
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1] / "static" / "video"
OUT.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1280, 720, 20
SIZES = (1, 2, 5, 10, 30, 100)
INK, MUTED, BLUE, ORANGE = "#172d48", "#546b82", "#197bd2", "#e57239"

def font(size, bold=False):
    candidates = [
        Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / ("arialbd.ttf" if bold else "arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu") / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
    ]
    return ImageFont.truetype(str(next(p for p in candidates if p.exists())), size)

F = {s: font(s) for s in (18, 20, 22, 24)}
TITLE, BOLD = font(36, True), font(26, True)
rng = np.random.default_rng(20260924)
# Independent exponential observations: population mean = standard deviation = 1.
samples = {n: math.sqrt(n) * (rng.exponential(size=(5000, n)).mean(axis=1) - 1) for n in SIZES}
edges = np.linspace(-4, 6, 61)

def frame(stage, progress):
    n = SIZES[stage]
    count = min(5000, 200 + int(progress * 4800))
    im = Image.new("RGB", (W, H), "#eff5fb")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 125), fill="#0b467e")
    d.text((38, 22), "ĐỊNH LÝ GIỚI HẠN TRUNG TÂM", font=TITLE, fill="white")
    d.text((40, 77), "Từ phân phối lệch phải đến phân phối gần chuẩn", font=F[24], fill="#d6eafa")
    d.rounded_rectangle((28, 145, 386, 600), radius=18, fill="white")
    d.rounded_rectangle((404, 145, 1252, 600), radius=18, fill="white")
    d.text((50, 165), "1. Phân phối gốc", font=BOLD, fill=INK)
    d.text((50, 207), "Phân phối mũ · μ = 1 · σ = 1", font=F[20], fill=MUTED)
    left, top, right, bottom = 60, 278, 358, 476
    d.line((left, top, left, bottom, right, bottom), fill="#bccddd", width=2)
    curve = [(left + x/5*(right-left), bottom-math.exp(-x)*(bottom-top)) for x in np.linspace(0, 5, 180)]
    d.polygon([(left, bottom)] + curve + [(right, bottom)], fill="#d5e9fc")
    d.line(curve, fill=BLUE, width=4)
    for tick in range(6):
        d.text((left+tick/5*(right-left), bottom+10), str(tick), font=F[18], fill=MUTED, anchor="mt")
    d.text((50, 536), "Lấy n giá trị độc lập / mỗi mẫu", font=F[20], fill=INK)
    d.text((430, 165), "2. Trung bình mẫu đã chuẩn hóa", font=BOLD, fill=INK)
    d.text((430, 206), f"n = {n}     |     Đã lặp: {count:,} / 5,000 mẫu", font=F[22], fill=BLUE)
    x0, y0, x1, y1 = 466, 284, 1212, 482
    def xy(x, y):
        return (x0+(x+4)/10*(x1-x0), y1-y/1.1*(y1-y0))
    for y in (0, .25, .5, .75, 1):
        py = xy(0, y)[1]
        d.line((x0, py, x1, py), fill="#e2eaf2")
        d.text((x0-10, py), f"{y:g}", font=F[18], fill=MUTED, anchor="rm")
    # Include samples beyond the plotted range in the density denominator.
    density = np.histogram(samples[n][:count], bins=edges)[0] / (count*np.diff(edges))
    for i, h in enumerate(density):
        a, b = xy(edges[i], float(h)), xy(edges[i+1], 0)
        if h > 0:
            d.rectangle((a[0]+1, a[1], b[0]-1, b[1]), fill=BLUE)
    gaussian = [xy(x, math.exp(-x*x/2)/math.sqrt(2*math.pi)) for x in np.linspace(-4, 6, 300)]
    d.line(gaussian, fill=ORANGE, width=4)
    for tick in range(-4, 7, 2):
        d.text((xy(tick, 0)[0], y1+10), str(tick), font=F[18], fill=MUTED, anchor="mt")
    d.text((430, 247), "Mật độ", font=F[18], fill=MUTED)
    d.text((825, 524), "Z = √n (X̄ − μ) / σ", font=F[24], fill=INK, anchor="mt")
    d.line((468, 578, 494, 578), fill=ORANGE, width=4)
    d.text((504, 565), "Đường chuẩn N(0, 1)", font=F[20], fill=MUTED)
    d.rectangle((857, 570, 875, 587), fill=BLUE)
    d.text((885, 565), "Histogram mô phỏng", font=F[20], fill=MUTED)
    captions = [
        "n = 1: Phân phối còn lệch phải rõ rệt.",
        "n = 2: Lấy trung bình giúp giảm độ lệch.",
        "n = 5: Histogram bắt đầu có hình dạng chuông.",
        "n = 10: Phân phối tiến gần đường chuẩn hơn.",
        "n = 30: Histogram đã khá gần đường cong chuẩn.",
        "n = 100: Trung bình chuẩn hóa xấp xỉ N(0, 1).",
    ]
    d.text((40, 623), captions[stage], font=BOLD, fill=INK)
    d.text((40, 664), "Ví dụ: các mẫu độc lập, cùng phân phối, có phương sai hữu hạn. Video không có âm thanh.", font=F[20], fill=MUTED)
    return im

frame(4, 1).save(OUT / "clt_poster.jpg", quality=92)
command = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-vcodec", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(OUT / "clt_simulation.mp4")]
process = subprocess.Popen(command, stdin=subprocess.PIPE)
try:
    for stage in range(len(SIZES)):
        for i in range(FPS*5):
            process.stdin.write(frame(stage, min(1, i/(FPS*3))).tobytes())
        print(f"Rendered n={SIZES[stage]}", flush=True)
finally:
    process.stdin.close()
if process.wait() != 0:
    raise RuntimeError("Video encoding failed")
print(f"Saved {OUT / 'clt_simulation.mp4'}")
