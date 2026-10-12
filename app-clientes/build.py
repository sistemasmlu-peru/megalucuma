"""Genera app-clientes/index.html incrustando el logo y el ornamento como data URIs."""
import base64, io, pathlib
from PIL import Image

root = pathlib.Path(__file__).resolve().parent.parent
src = (root / "app-clientes/app.src.html").read_text(encoding="utf-8")

def data_uri(img, fmt, mime, **kw):
    buf = io.BytesIO(); img.save(buf, fmt, **kw)
    return f"data:{mime};base64," + base64.b64encode(buf.getvalue()).decode()

logo = Image.open(root / "assets/logo-blanco.png"); logo.thumbnail((240, 160))
orn = Image.open(root / "assets/ornamento-dorado.png").convert("RGBA")
orn.thumbnail((520, 700))
alpha = orn.getchannel("A").point(lambda a: int(a * 0.55)); orn.putalpha(alpha)

out = (src.replace("{{LOGO}}", data_uri(logo, "PNG", "image/png", optimize=True))
          .replace("{{ORNAMENTO}}", data_uri(orn, "WEBP", "image/webp", quality=80)))
(root / "app-clientes/index.html").write_text(out, encoding="utf-8")
print("index.html", len(out) // 1024, "KB")
