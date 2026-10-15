"""Genera el video de perfil horizontal (1920x1080, 30 fps) de Leandro Valero.

Uso:  python3 video/generar_video.py
Salida: video/perfil_leandro_horizontal.mp4
Requiere: Pillow y ffmpeg.
"""
import math
import os
import subprocess

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1920, 1080, 30
AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, "perfil_leandro_horizontal.mp4")
AUDIO = os.path.join(AQUI, "_fondo.wav")

FUENTES = "/usr/share/fonts/opentype/inter/"
def fuente(peso, tam):
    return ImageFont.truetype(FUENTES + f"Inter-{peso}.otf", tam)

FONDO_A = (8, 22, 40)
FONDO_B = (14, 52, 72)
ACENTO = (46, 196, 182)
DORADO = (232, 190, 110)
BLANCO = (245, 248, 250)
GRIS = (170, 190, 205)

# Narración con la voz del Dr. Leandro (ElevenLabs). Si existe, se mezcla
# sobre la música y las escenas están sincronizadas con sus frases.
NARRACION = os.path.join(AQUI, "narracion_leandro.mp3")
RETRASO_VOZ_MS = 800

# (duración en segundos, etiqueta, título, subtítulo)
ESCENAS = [
    (6.7, "PERFIL PROFESIONAL", "Dr. Leandro Pio\nValero Peñafiel", "Médico · Especialista en Salud Digital"),
    (4.4, "01 · ESPECIALIDAD", "Salud Digital", "Tecnología e innovación al servicio\nde la atención médica"),
    (2.7, "02 · MASTERADO", "Gerencia en\nServicios de la Salud", "Gestión y dirección de instituciones de salud"),
    (3.2, "03 · MASTERADO", "Asesoramiento de Imagen\ny Consultoría Política", "Comunicación estratégica y liderazgo"),
    (6.5, "04 · EN CURSO", "Masterado en\nSexología", "Salud integral y bienestar humano"),
    (8.0, "", "Leandro Valero", "Salud · Gestión · Comunicación"),
]
TOTAL = sum(e[0] for e in ESCENAS)


def suave(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def fondo_base():
    """Degradado diagonal precalculado."""
    lado = 2400
    g = Image.linear_gradient("L").resize((lado, lado)).rotate(-55, resample=Image.BICUBIC)
    g = g.crop(((lado - W) // 2, (lado - H) // 2, (lado + W) // 2, (lado + H) // 2))
    a = Image.new("RGB", (W, H), FONDO_A)
    b = Image.new("RGB", (W, H), FONDO_B)
    return Image.composite(b, a, g)


BASE = fondo_base()


def fondo(t):
    img = BASE.copy()
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    # Círculos suaves que se desplazan lentamente
    for i, (cx, cy, r, col) in enumerate([
        (1500, 300, 420, ACENTO + (38,)),
        (300, 850, 360, DORADO + (22,)),
        (1100, 950, 260, ACENTO + (25,)),
    ]):
        dx = 60 * math.sin(t * 0.35 + i * 2.1)
        dy = 40 * math.cos(t * 0.3 + i * 1.3)
        d.ellipse((cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r), fill=col)
    capa = capa.filter(ImageFilter.GaussianBlur(90))
    img.paste(capa, (0, 0), capa)
    # Retícula de puntos (motivo "digital")
    d2 = ImageDraw.Draw(img)
    desplaz = (t * 12) % 60
    for x in range(1240, W, 60):
        for y in range(-60, H, 60):
            yy = y + desplaz
            dist = math.hypot(x - 1600, yy - 540) / 700
            if dist < 1:
                c = int(60 + 60 * (1 - dist))
                d2.ellipse((x - 2, yy - 2, x + 2, yy + 2), fill=(c // 2, c, c))
    return img


def texto_multilinea(d, xy, txt, f, col, interlineado, alfa):
    x, y = xy
    for linea in txt.split("\n"):
        d.text((x, y), linea, font=f, fill=col + (alfa,))
        y += interlineado
    return y


F_ETIQ = fuente("SemiBold", 30)
F_TIT = fuente("Bold", 104)
F_TIT_FIN = fuente("Bold", 130)
F_SUB = fuente("Regular", 44)


def escena(img, idx, tl, dur):
    etiq, tit, sub = ESCENAS[idx][1:]
    entrada = suave(tl / 0.9)
    salida = 1 - suave((tl - (dur - 0.6)) / 0.6) if idx < len(ESCENAS) - 1 else 1 - suave((tl - (dur - 1.2)) / 1.2)
    vis = min(entrada, salida)

    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    x0 = 160
    final = idx == len(ESCENAS) - 1

    if final:
        f_t = F_TIT_FIN
        a = int(255 * vis)
        bb = d.textbbox((0, 0), tit, font=f_t)
        tw = bb[2] - bb[0]
        y = 400 + int(30 * (1 - entrada))
        d.text(((W - tw) // 2, y), tit, font=f_t, fill=BLANCO + (a,))
        largo = int(520 * suave((tl - 0.5) / 1.0))
        d.rectangle(((W - largo) // 2, y + 175, (W + largo) // 2, y + 181), fill=ACENTO + (a,))
        a2 = int(255 * min(suave((tl - 0.9) / 0.9), salida))
        bb = d.textbbox((0, 0), sub, font=F_SUB)
        d.text(((W - (bb[2] - bb[0])) // 2, y + 215), sub, font=F_SUB, fill=DORADO + (a2,))
    else:
        desliz = int(80 * (1 - entrada))
        y = 300 if idx == 0 else 330
        a_e = int(255 * vis)
        if etiq:
            d.rectangle((x0, y + 12, x0 + int(60 * entrada), y + 16), fill=ACENTO + (a_e,))
            d.text((x0 + 80, y), etiq, font=F_ETIQ, fill=ACENTO + (a_e,))
        y += 70
        y = texto_multilinea(d, (x0 + desliz, y), tit, F_TIT, BLANCO, 122, int(255 * vis))
        a_s = int(255 * min(suave((tl - 0.5) / 0.9), salida))
        texto_multilinea(d, (x0 + desliz // 2, y + 30), sub, F_SUB, GRIS, 58, a_s)
        # Barra de progreso de capítulos
        n = len(ESCENAS) - 2
        if idx >= 1:
            for k in range(n):
                col = ACENTO if k + 1 <= idx else (60, 80, 100)
                d.rectangle((x0 + k * 70, 940, x0 + k * 70 + 50, 946), fill=col + (int(255 * vis),))
    img.paste(capa, (0, 0), capa)


def cuadro(n):
    t = n / FPS
    img = fondo(t)
    acum = 0.0
    for i, e in enumerate(ESCENAS):
        if t < acum + e[0] or i == len(ESCENAS) - 1:
            escena(img, i, t - acum, e[0])
            break
        acum += e[0]
    # Fundido general de entrada/salida
    f = min(suave(t / 0.8), 1 - suave((t - (TOTAL - 0.8)) / 0.8))
    if f < 1:
        img = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), img, f)
    return img


def generar_audio():
    """Fondo musical ambiental suave (acordes sintetizados)."""
    acordes = [(220.0, 277.18, 329.63), (196.0, 246.94, 293.66),
               (174.61, 220.0, 261.63), (196.0, 246.94, 329.63)]
    seg = TOTAL / len(acordes)
    partes = []
    for i, ac in enumerate(acordes):
        voz = "+".join(f"sin(2*PI*{f}*t)+0.3*sin(2*PI*{2*f}*t)" for f in ac)
        env = f"min(1,(t-{i*seg})/1.5)*min(1,({(i+1)*seg}-t)/1.5)"
        partes.append(f"between(t,{i*seg},{(i+1)*seg})*{env}*({voz})")
    expr = "0.045*(" + "+".join(partes) + ")"
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
        "-i", f"aevalsrc='{expr}|{expr}':s=44100:d={TOTAL}",
        "-af", f"aecho=0.8:0.7:120|240:0.35|0.2,afade=t=in:d=2,afade=t=out:st={TOTAL-2.5}:d=2.5,lowpass=f=2500",
        AUDIO if not os.path.exists(NARRACION) else AUDIO + ".musica.wav",
    ], check=True)
    if os.path.exists(NARRACION):
        musica = AUDIO + ".musica.wav"
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-i", musica, "-i", NARRACION,
            "-filter_complex",
            f"[0:a]volume=0.45[m];[1:a]adelay={RETRASO_VOZ_MS}|{RETRASO_VOZ_MS},volume=1.6[v];"
            "[m][v]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95",
            "-ac", "2", AUDIO,
        ], check=True)
        os.remove(musica)


def main():
    generar_audio()
    total = int(TOTAL * FPS)
    proc = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", AUDIO,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart",
        SALIDA,
    ], stdin=subprocess.PIPE)
    for n in range(total):
        proc.stdin.write(cuadro(n).tobytes())
    proc.stdin.close()
    proc.wait()
    os.remove(AUDIO)
    print("Listo:", SALIDA)


if __name__ == "__main__":
    main()
