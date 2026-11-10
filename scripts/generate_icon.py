"""Gera o ícone oficial do NTSL Cores em múltiplas resoluções."""
from pathlib import Path
import math
from PIL import Image, ImageDraw

OUT = Path("assets")
OUT.mkdir(exist_ok=True)
SIZES = [16, 24, 32, 48, 64, 128, 256]
PALETTE = ["#ff5d70", "#ffb454", "#f5df65", "#48d69a",
           "#54b7ff", "#8b83ff", "#d77bff"]


def render(size):
    scale = 4
    n = size * scale
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((2*scale, 2*scale, n-2*scale, n-2*scale),
                        radius=int(size*.23*scale), fill="#171d2b",
                        outline="#34435f", width=max(1, scale))
    # Aro cromático em sete segmentos, com círculos suaves.
    cx, cy, radius = n*.5, n*.43, n*.29
    for i in range(420, 0, -1):
        angle = (i/420) * math.tau
        x = cx + math.cos(angle)*radius*.78
        y = cy + math.sin(angle)*radius*.78
        color = PALETTE[int((angle % math.tau)/math.tau*len(PALETTE))]
        rr = n*.095
        d.ellipse((x-rr, y-rr, x+rr, y+rr), fill=color)
    # Miolo escuro e uma paleta com cinco amostras.
    d.ellipse((n*.36, n*.29, n*.64, n*.57), fill="#202a3b",
              outline="#dce7ff", width=max(1, scale))
    d.rounded_rectangle((n*.16, n*.65, n*.84, n*.82),
                        radius=n*.055, fill="#f2f5fb",
                        outline="#ffffff", width=max(1, scale))
    for j, color in enumerate(PALETTE[:5]):
        x0 = n*(.195+j*.126)
        d.rounded_rectangle((x0, n*.675, x0+n*.095, n*.795),
                            radius=n*.025, fill=color)
    return im.resize((size, size), Image.Resampling.LANCZOS)


images = [render(s) for s in SIZES]
images[-1].save(OUT / "NTSL-Cores.ico", format="ICO",
                sizes=[(s, s) for s in SIZES])
print("Ícone criado: assets/NTSL-Cores.ico")
