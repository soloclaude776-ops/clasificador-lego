"""Genera el cartel del logo (50 cm) en piezas con encastre cola de milano
para imprimir en Bambu Lab (cama 256x256; las piezas también entran en A1 mini 180x180).

Uso:  python3 generar_stl.py
Requiere: pip install numpy pillow opencv-python-headless shapely trimesh manifold3d mapbox_earcut
"""
import os
import cv2
import numpy as np
import trimesh
from shapely.geometry import Polygon, MultiPolygon, box
from shapely.ops import unary_union
from shapely import affinity

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, "stl")

# ---------------- Parámetros (mm) ----------------
ANCHO_TOTAL = 500.0      # ancho del cartel (fondo blanco) = 50 cm
MARGEN = 15.0            # borde blanco alrededor del logo
RADIO_ESQUINA = 8.0      # esquinas redondeadas del fondo
ESPESOR_FONDO = 5.0      # placa blanca
ALTO_LOGO = 2.0          # relieve negro sobre la placa
# Cortes alineados con bordes verticales del logo para que la unión casi no se vea.
# Piezas: ~186 / ~190 / ~144 mm (con la cola) -> entran en X1/P1/A1 (256x256) y H2D.
CORTES = [176.2, 355.8]
HOLGURA = 0.15           # juego por lado en el encastre
COLA_CUELLO = 14.0       # ancho del cuello de la cola de milano
COLA_CABEZA = 22.0       # ancho de la cabeza
COLA_LARGO = 10.0        # cuánto entra en la pieza vecina


def vectorizar(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    _, bw = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY_INV)
    contornos, jer = cv2.findContours(bw, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    jer = jer[0]
    polys = []
    for i, c in enumerate(contornos):
        if jer[i][3] != -1 or len(c) < 10:
            continue  # sólo exteriores aquí
        ext = c[:, 0, :].astype(float)
        agujeros = []
        h = jer[i][2]
        while h != -1:
            if len(contornos[h]) >= 10:
                agujeros.append(contornos[h][:, 0, :].astype(float))
            h = jer[h][0]
        p = Polygon(ext, agujeros).buffer(0)
        if p.area > 200:
            polys.append(p)
    logo = unary_union(polys)
    logo = affinity.scale(logo, 1, -1, origin=(0, 0))  # imagen: y hacia abajo
    return logo.simplify(0.6)


def escalar_logo(logo):
    minx, miny, maxx, maxy = logo.bounds
    s = (ANCHO_TOTAL - 2 * MARGEN) / (maxx - minx)
    logo = affinity.translate(logo, -minx, -miny)
    logo = affinity.scale(logo, s, s, origin=(0, 0))
    logo = affinity.translate(logo, MARGEN, MARGEN)
    return logo.buffer(0)


def fondo_redondeado(ancho, alto, r):
    return box(r, r, ancho - r, alto - r).buffer(r, resolution=16)


def lado_izquierdo(x, alto):
    """Región a la izquierda de la línea de corte en x, con colas de milano
    que salen hacia la derecha (macho en la pieza izquierda)."""
    region = box(-100, -100, x, alto + 100)
    colas = []
    for yc in (alto * 0.27, alto * 0.73):
        colas.append(Polygon([
            (x - 1, yc - COLA_CUELLO / 2),
            (x, yc - COLA_CUELLO / 2),
            (x + COLA_LARGO, yc - COLA_CABEZA / 2),
            (x + COLA_LARGO, yc + COLA_CABEZA / 2),
            (x, yc + COLA_CUELLO / 2),
            (x - 1, yc + COLA_CUELLO / 2),
        ]))
    return unary_union([region] + colas)


def extruir(geom, z0, h):
    if geom.is_empty:
        return None
    geoms = geom.geoms if isinstance(geom, MultiPolygon) else [geom]
    mallas = []
    for g in geoms:
        if g.area < 0.5:
            continue
        m = trimesh.creation.extrude_polygon(g, h)
        m.apply_translation((0, 0, z0))
        mallas.append(m)
    return trimesh.util.concatenate(mallas) if mallas else None


def main():
    os.makedirs(SALIDA, exist_ok=True)
    logo = escalar_logo(vectorizar(os.path.join(AQUI, "logo.png")))
    _, _, _, maxy = logo.bounds
    alto = maxy + MARGEN
    fondo = fondo_redondeado(ANCHO_TOTAL, alto, RADIO_ESQUINA)
    print(f"Cartel: {ANCHO_TOTAL:.0f} x {alto:.1f} mm, espesor {ESPESOR_FONDO + ALTO_LOGO:.1f} mm")

    cortes = CORTES
    N_PIEZAS = len(cortes) + 1
    izq = [lado_izquierdo(x, alto) for x in cortes]
    vista = []

    for n in range(N_PIEZAS):
        region = box(-100, -100, ANCHO_TOTAL + 100, alto + 100)
        if n > 0:      # recorta lo que pertenece a la pieza anterior (+ holgura)
            region = region.difference(izq[n - 1].buffer(HOLGURA, join_style=2))
        if n < N_PIEZAS - 1:
            region = region.intersection(izq[n].buffer(-HOLGURA, join_style=2))
        f = fondo.intersection(region)
        l = logo.intersection(region)
        base = extruir(f, 0, ESPESOR_FONDO)
        relieve = extruir(l, ESPESOR_FONDO, ALTO_LOGO)
        # mueve la pieza al origen
        dx, dy = -f.bounds[0], -f.bounds[1]
        for m in (base, relieve):
            if m is not None:
                m.apply_translation((dx, dy, 0))
        tag = f"pieza_{n + 1}"
        base.export(os.path.join(SALIDA, f"{tag}_fondo_blanco.stl"))
        relieve.export(os.path.join(SALIDA, f"{tag}_logo_negro.stl"))
        # versión en un solo cuerpo (para cambio de filamento por altura)
        uno = trimesh.boolean.union([base, relieve], engine="manifold")
        uno.export(os.path.join(SALIDA, f"{tag}_completa.stl"))
        vista.append((f, l))
        bx = f.bounds
        print(f"{tag}: {bx[2] - bx[0]:.1f} x {bx[3] - bx[1]:.1f} mm  "
              f"(watertight base={base.is_watertight} logo={relieve.is_watertight} completa={uno.is_watertight})")

    # cartel completo (sólo de referencia / vista previa)
    todo = trimesh.util.concatenate([extruir(fondo, 0, ESPESOR_FONDO), extruir(logo, ESPESOR_FONDO, ALTO_LOGO)])
    todo.export(os.path.join(SALIDA, "cartel_completo_referencia.stl"))
    dibujar_vista(vista, os.path.join(AQUI, "vista_previa.png"))


def dibujar_vista(vista, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 1, figsize=(16, 7), dpi=110)
    for ax, sep in ((axs[0], 0.0), (axs[1], 18.0)):
        for i, (f, l) in enumerate(vista):
            for g, fc in ((f, "#f4f4f4"), (l, "#111111")):
                for p in (g.geoms if isinstance(g, MultiPolygon) else [g]):
                    x, y = p.exterior.xy
                    ax.fill([v + i * sep for v in x], y, fc=fc, ec="#999", lw=0.5)
                    for h in p.interiors:
                        hx, hy = h.xy
                        ax.fill([v + i * sep for v in hx], hy, fc="#f4f4f4", ec="#999", lw=0.5)
        ax.set_aspect("equal"); ax.axis("off")
    axs[0].set_title("Armado (50 cm)"); axs[1].set_title("Piezas separadas - encastre cola de milano")
    plt.tight_layout(); plt.savefig(path)


if __name__ == "__main__":
    main()
