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
# La narración se arma con la grabación base y la frase de proyectos, que se
# inserta después de la frase de Sexología (en CORTE_BASE segundos del audio base).
NARRACION = os.path.join(AQUI, "narracion_base.mp3")
NARRACION_PROYECTOS = os.path.join(AQUI, "narracion_proyectos.mp3")
CORTE_BASE = 22.85
PAUSA = 0.4
RETRASO_VOZ_MS = 800

FOTOS = os.path.join(AQUI, "fotos")

# Subtítulos: (inicio, fin, texto) en segundos del video, alineados a la narración.
SUBTITULOS = [
    (0.8, 4.0, "Hola, soy el doctor Leandro Pio Valero Peñafiel,"),
    (4.3, 6.6, "médico especialista en Salud Digital."),
    (7.0, 11.0, "Creo en la tecnología y la innovación\nal servicio de la atención médica."),
    (11.4, 13.9, "Soy masterado en Gerencia en Servicios de la Salud,"),
    (14.1, 17.0, "y en Asesoramiento de Imagen y Consultoría Política."),
    (17.3, 23.5, "Actualmente culmino mi masterado en Sexología, para acompañar\nla salud integral y el bienestar de las personas."),
    (24.05, 28.2, "Además, estamos construyendo el curso de\nDirección Sanitaria Aumentada,"),
    (28.4, 32.3, "y ASTRA, un videojuego para aprender\na gestionar hospitales."),
    (32.85, 35.2, "Salud, gestión y comunicación."),
    (35.5, 37.3, "Bienvenidos a mi perfil."),
]

# (duración en segundos, etiqueta, título, subtítulo, foto)
ESCENAS = [
    (6.7, "PERFIL PROFESIONAL", "Dr. Leandro Pio\nValero Peñafiel", "Médico · Especialista en Salud Digital", ["retrato_traje.jpg", "retrato_bata_medival.jpg"]),
    (4.4, "01 · ESPECIALIDAD", "Salud Digital", "Tecnología e innovación al servicio\nde la atención médica", ["telemedicina.jpg", "equipo_medico.jpg"]),
    (2.7, "02 · MASTERADO", "Gerencia en\nServicios de la Salud", "Gestión y dirección de\ninstituciones de salud", ["reunion_institucional.jpg", "medival_tablero_gestion.jpg"]),
    (3.2, "03 · MASTERADO", "Asesoramiento de Imagen\ny Consultoría Política", "Comunicación estratégica y liderazgo", ["charla_presentacion.jpg"]),
    (6.5, "04 · EN CURSO", "Masterado en\nSexología", "Salud integral y bienestar humano", ["retrato_bata_corbata.jpg"]),
    (9.1, "05 · EN DESARROLLO", "Proyectos en\ndesarrollo", "Curso Dirección Sanitaria\nAumentada y ASTRA, videojuego\nde gestión hospitalaria",
     [("logo_dsa.jpg", 4.9), ("astra_simulador.jpg", 2.3), ("medival_presentacion_72h.jpg", 1.9)], "ancho"),
    (10.5, "", "Leandro Valero", "Salud · Gestión · Comunicación", "retrato_traje_gris.jpg"),
]
TOTAL = sum(e[0] for e in ESCENAS)

# Mosaico de fotos del cierre
MOSAICO = ["familia.jpg", "reconocimiento.jpg", "trabajo_campo.jpg", "visita_salud_hogar.jpg", "hijo_copa.jpg"]
LOGO = "logo_medival.jpg"

# Datos de contacto del cierre: (etiqueta, valor)
CONTACTO = [
    ("WhatsApp", "098 962 3790"),
    ("Correo", "valeroyasociados9@gmail.com"),
    ("LinkedIn", "in/leandro-valero-b00492112"),
]

# Encuadre y movimiento de cada foto: (foco_x, foco_y, zoom, paneo_x, paneo_y).
# foco: 0 = izquierda/arriba, 1 = derecha/abajo. El paneo es cuánto se desplaza
# el encuadre durante la escena; el zoom crece un 18 % para dar efecto de clip.
# La charla se encuadra para dejar fuera el banner del fondo.
FOCO = {
    "retrato_traje.jpg": (0.5, 0.08, 1.0, 0.0, 0.0),
    "retrato_bata_medival.jpg": (0.5, 0.1, 1.0, 0.0, 0.0),
    "retrato_bata_corbata.jpg": (0.5, 0.12, 1.0, 0.0, 0.0),
    "equipo_medico.jpg": (0.45, 0.4, 1.0, 0.3, 0.0),
    "reunion_institucional.jpg": (0.55, 0.4, 1.0, -0.25, 0.0),
    "charla_presentacion.jpg": (0.68, 0.34, 1.35, 0.12, 0.0),
    "telemedicina.jpg": (0.62, 0.4, 1.0, 0.0, 0.1),
    "medival_tablero_gestion.jpg": (0.47, 0.45, 1.0, 0.0, 0.0),
    "logo_dsa.jpg": (0.5, 0.5, 1.0, 0.0, 0.0),
    "astra_simulador.jpg": (0.12, 0.5, 1.0, 0.2, 0.0),
    "medival_presentacion_72h.jpg": (0.3, 0.4, 1.0, 0.25, 0.0),
    "retrato_traje_gris.jpg": (0.5, 0.12),
    "familia.jpg": (0.5, 0.45), "reconocimiento.jpg": (0.5, 0.6),
    "trabajo_campo.jpg": (0.5, 0.4), "visita_salud_hogar.jpg": (0.1, 0.3),
    "hijo_copa.jpg": (0.5, 0.35),
}
CRECE_ZOOM = 0.18


def suave_lineal(x):
    """Avance casi lineal (para movimiento continuo de cámara)."""
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x) * 0.3 + x * 0.7


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
F_TIT = fuente("Bold", 84)
F_SUBT = fuente("Medium", 38)

PANEL = (1240, 150, 1760, 890)  # x0, y0, x1, y1 del recuadro de foto
PANEL_ANCHO = (960, 200, 1800, 673)  # recuadro 16:9 para afiches y logos
_cache_fotos = {}


def foto_recortada(nombre, ancho, alto, zoom=1.0, foco_y=0.3, foco_x=0.5):
    """Recorta la foto para cubrir ancho x alto, con zoom lento (Ken Burns)."""
    if nombre not in _cache_fotos:
        _cache_fotos[nombre] = Image.open(os.path.join(FOTOS, nombre)).convert("RGB")
    im = _cache_fotos[nombre]
    # Recorte con coordenadas decimales para que el movimiento sea suave
    esc = max(ancho / im.width, alto / im.height) * zoom
    bw, bh = ancho / esc, alto / esc
    fx, fy = min(max(foco_x, 0.0), 1.0), min(max(foco_y, 0.0), 1.0)
    bx, by = (im.width - bw) * fx, (im.height - bh) * fy
    return im.resize((ancho, alto), Image.BICUBIC, box=(bx, by, bx + bw, by + bh))


def mascara_redondeada(ancho, alto, radio):
    m = Image.new("L", (ancho, alto), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, ancho - 1, alto - 1), radio, fill=255)
    return m


def foto_panel(fotos, w, h, tl, dur):
    """Muestra las fotos de la escena una tras otra, con fundido cruzado.

    Cada foto puede ser un nombre o (nombre, segundos) para fijar su duración
    y que coincida con lo que dice la narración.
    """
    fotos = [f if isinstance(f, tuple) else (f, dur / len(fotos)) for f in fotos]
    inicios, acum = [], 0.0
    for _, seg in fotos:
        inicios.append(acum)
        acum += seg
    i = max(k for k in range(len(fotos)) if tl >= inicios[k] or k == 0)
    def una(k):
        nombre, seg = fotos[k]
        fx, fy, z, px, py = FOCO.get(nombre, (0.5, 0.2, 1.0, 0.0, 0.0))
        p = suave_lineal((tl - inicios[k] + 0.4) / (seg + 0.4))
        return foto_recortada(nombre, w, h, zoom=z * (1 + CRECE_ZOOM * p),
                              foco_x=fx + px * (p - 0.5), foco_y=fy + py * (p - 0.5))
    foto = una(i)
    if i > 0 and tl - inicios[i] < 0.4:
        foto = Image.blend(una(i - 1), foto, suave((tl - inicios[i]) / 0.4))
    return foto


def poner_foto(img, nombres, tl, dur, vis, entrada, panel=PANEL):
    x0, y0, x1, y1 = panel
    w, h = x1 - x0, y1 - y0
    foto = foto_panel(nombres, w, h, tl, dur)
    dx = int(60 * (1 - entrada))
    mask = mascara_redondeada(w, h, 28).point(lambda p: int(p * vis))
    # Sombra y borde de acento
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sombra)
    ds.rounded_rectangle((x0 + dx + 18, y0 + 24, x1 + dx + 18, y1 + 24), 28, fill=(0, 0, 0, int(110 * vis)))
    sombra = sombra.filter(ImageFilter.GaussianBlur(24))
    img.paste(sombra, (0, 0), sombra)
    img.paste(foto, (x0 + dx, y0), mask)
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle((x0 + dx - 14, y0 - 14, x0 + dx + 110, y0 - 8), 3, fill=ACENTO + (int(255 * vis),))


def poner_mosaico(img, tl, salida):
    n = len(MOSAICO)
    tw, th, gap = 280, 200, 24
    xs = (W - (n * tw + (n - 1) * gap)) // 2
    y = 650
    for k, nombre in enumerate(MOSAICO):
        a = min(suave((tl - 1.2 - 0.25 * k) / 0.6), salida)
        if a <= 0:
            continue
        fx, fy = FOCO.get(nombre, (0.5, 0.3))[:2]
        foto = foto_recortada(nombre, tw, th, zoom=1.0 + 0.03 * tl, foco_y=fy, foco_x=fx)
        mask = mascara_redondeada(tw, th, 18).point(lambda p: int(p * a))
        img.paste(foto, (xs + k * (tw + gap), y + int(30 * (1 - a))), mask)


def poner_contacto(img, a):
    if a <= 0:
        return
    d = ImageDraw.Draw(img, "RGBA")
    f_et, f_val = fuente("SemiBold", 26), fuente("Medium", 32)
    piezas = []
    for et, val in CONTACTO:
        we = d.textbbox((0, 0), et.upper(), font=f_et)[2]
        wv = d.textbbox((0, 0), val, font=f_val)[2]
        piezas.append((et.upper(), val, we, wv))
    sep = 70
    total = sum(we + 14 + wv for _, _, we, wv in piezas) + sep * (len(piezas) - 1)
    x, y = (W - total) // 2, 885
    for i, (et, val, we, wv) in enumerate(piezas):
        d.text((x, y + 5), et, font=f_et, fill=ACENTO + (int(255 * a),))
        x += we + 14
        d.text((x, y), val, font=f_val, fill=BLANCO + (int(255 * a),))
        x += wv
        if i < len(piezas) - 1:
            d.ellipse((x + sep // 2 - 4, y + 16, x + sep // 2 + 4, y + 24), fill=DORADO + (int(255 * a),))
            x += sep


def poner_logo(img, a):
    logo = Image.open(os.path.join(FOTOS, LOGO)).convert("RGB")
    lw = 190
    logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.BICUBIC)
    x, y = W - lw - 60, 50
    mask = mascara_redondeada(logo.width, logo.height, 18).point(lambda p: int(p * a))
    img.paste(logo, (x, y), mask)


def poner_retrato_circular(img, nombre, centro, diam, vis):
    fx, fy = FOCO.get(nombre, (0.5, 0.12))[:2]
    foto = foto_recortada(nombre, diam, diam, foco_y=fy, foco_x=fx)
    m = Image.new("L", (diam, diam), 0)
    ImageDraw.Draw(m).ellipse((0, 0, diam - 1, diam - 1), fill=int(255 * vis))
    cx, cy = centro
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse((cx - diam // 2 - 8, cy - diam // 2 - 8, cx + diam // 2 + 8, cy + diam // 2 + 8),
              outline=ACENTO + (int(255 * vis),), width=5)
    img.paste(foto, (cx - diam // 2, cy - diam // 2), m)


def poner_subtitulo(img, t):
    for ini, fin, txt in SUBTITULOS:
        if ini <= t <= fin:
            a = min(suave((t - ini) / 0.25), 1 - suave((t - (fin - 0.2)) / 0.2))
            capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(capa)
            lineas = txt.split("\n")
            alto_l = 50
            anchos = [d.textbbox((0, 0), l, font=F_SUBT)[2] for l in lineas]
            caja_w = max(anchos) + 64
            caja_h = alto_l * len(lineas) + 30
            y0 = 1040 - caja_h
            d.rounded_rectangle(((W - caja_w) // 2, y0, (W + caja_w) // 2, y0 + caja_h), 16,
                                fill=(5, 14, 26, int(185 * a)))
            for i, (l, lw) in enumerate(zip(lineas, anchos)):
                d.text(((W - lw) // 2, y0 + 12 + i * alto_l), l, font=F_SUBT, fill=BLANCO + (int(255 * a),))
            img.paste(capa, (0, 0), capa)
            break
F_TIT_FIN = fuente("Bold", 130)
F_SUB = fuente("Regular", 44)


def escena(img, idx, tl, dur):
    etiq, tit, sub, foto = ESCENAS[idx][1:5]
    panel = PANEL_ANCHO if ESCENAS[idx][5:] == ("ancho",) else PANEL
    entrada = suave(tl / 0.9)
    salida = 1 - suave((tl - (dur - 0.6)) / 0.6) if idx < len(ESCENAS) - 1 else 1 - suave((tl - (dur - 1.2)) / 1.2)
    vis = min(entrada, salida)

    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    x0 = 160
    final = idx == len(ESCENAS) - 1

    if final:
        poner_retrato_circular(img, foto, (W // 2, 165), 210, vis)
        poner_logo(img, vis)
        poner_mosaico(img, tl, salida)
        poner_contacto(img, min(suave((tl - 2.4) / 0.8), salida))
        f_t = F_TIT_FIN
        a = int(255 * vis)
        bb = d.textbbox((0, 0), tit, font=f_t)
        tw = bb[2] - bb[0]
        y = 290 + int(30 * (1 - entrada))
        d.text(((W - tw) // 2, y), tit, font=f_t, fill=BLANCO + (a,))
        largo = int(520 * suave((tl - 0.5) / 1.0))
        d.rectangle(((W - largo) // 2, y + 175, (W + largo) // 2, y + 181), fill=ACENTO + (a,))
        a2 = int(255 * min(suave((tl - 0.9) / 0.9), salida))
        bb = d.textbbox((0, 0), sub, font=F_SUB)
        d.text(((W - (bb[2] - bb[0])) // 2, y + 215), sub, font=F_SUB, fill=DORADO + (a2,))
    else:
        poner_foto(img, foto, tl, dur, vis, entrada, panel)
        desliz = int(80 * (1 - entrada))
        y = 250 if idx == 0 else 280
        a_e = int(255 * vis)
        if etiq:
            d.rectangle((x0, y + 12, x0 + int(60 * entrada), y + 16), fill=ACENTO + (a_e,))
            d.text((x0 + 80, y), etiq, font=F_ETIQ, fill=ACENTO + (a_e,))
        y += 70
        # Ajusta el tamaño del título para que no toque la foto
        tam = 84
        while max(d.textbbox((0, 0), l, font=fuente("Bold", tam))[2] for l in tit.split("\n")) > panel[0] - x0 - 90:
            tam -= 2
        f_tit = F_TIT if tam == 84 else fuente("Bold", tam)
        y = texto_multilinea(d, (x0 + desliz, y), tit, f_tit, BLANCO, int(tam * 1.19), int(255 * vis))
        a_s = int(255 * min(suave((tl - 0.5) / 0.9), salida))
        texto_multilinea(d, (x0 + desliz // 2, y + 30), sub, F_SUB, GRIS, 58, a_s)
        # Barra de progreso de capítulos
        n = len(ESCENAS) - 2
        if idx >= 1:
            for k in range(n):
                col = ACENTO if k + 1 <= idx else (60, 80, 100)
                d.rectangle((x0 + k * 70, 800, x0 + k * 70 + 50, 806), fill=col + (int(255 * vis),))
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
    poner_subtitulo(img, t)
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
            "ffmpeg", "-y", "-loglevel", "error", "-i", musica, "-i", NARRACION, "-i", NARRACION_PROYECTOS,
            "-filter_complex",
            "[1:a]aresample=44100,aformat=channel_layouts=mono,asplit[b1][b2];"
            "[2:a]aresample=44100,aformat=channel_layouts=mono[pr];"
            f"[b1]atrim=0:{CORTE_BASE},asetpts=PTS-STARTPTS[a];"
            f"[b2]atrim=start={CORTE_BASE},asetpts=PTS-STARTPTS[c];"
            f"aevalsrc=0:s=44100:d={PAUSA}[s1];aevalsrc=0:s=44100:d={PAUSA}[s2];"
            "[a][s1][pr][s2][c]concat=n=5:v=0:a=1[voz];"
            f"[0:a]volume=0.45[m];[voz]adelay={RETRASO_VOZ_MS}|{RETRASO_VOZ_MS},volume=1.6[v];"
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
