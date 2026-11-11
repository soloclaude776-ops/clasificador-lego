"""Soporte / gancho en U para pared (copia del gancho de acero inoxidable).

Medidas en mm. Cambiá los parámetros de arriba y volvé a correr:
    pip install cadquery
    python soporte_gancho.py
Genera soporte_gancho.stl (para imprimir) y soporte_gancho.step (para CAD).

Ejes: X = ancho, Y = profundidad (la pared está en Y=0), Z = alto.
"""
import cadquery as cq

# ---------- Parámetros ----------
ANCHO = 60.0          # ancho del gancho
ALTO_PLACA = 70.0     # alto de la placa trasera (la que va a la pared)
ALTO_LABIO = 34.0     # alto de la pestaña delantera
HUECO = 24.0          # espacio libre interior de la U (lo que entra adentro)
ESPESOR = 4.0         # espesor de la chapa
R_DOBLEZ = 4.0        # radio interior de los dobleces de abajo
R_ESQ_PLACA = 5.0     # redondeo de las esquinas de arriba de la placa
R_ESQ_LABIO = 2.0     # redondeo de las esquinas de la pestaña

D_AGUJERO = 5.0       # agujero para tornillo (4-4.5 mm)
D_AVELLANADO = 10.0   # diámetro del avellanado (cabeza del tornillo)
SEP_AGUJEROS = 28.0   # distancia entre centros de agujeros
Z_AGUJEROS = 49.0     # altura de los agujeros desde abajo
# --------------------------------

t, W, H, L, G = ESPESOR, ANCHO, ALTO_PLACA, ALTO_LABIO, HUECO
prof = 2 * t + G      # profundidad total


def caja(x0, y0, z0, dx, dy, dz):
    return cq.Workplane("XY").box(dx, dy, dz, centered=False).translate((x0, y0, z0))


cuerpo = (
    caja(0, 0, 0, W, t, H)            # placa trasera
    .union(caja(0, 0, 0, W, prof, t))  # base
    .union(caja(0, t + G, 0, W, t, L))  # pestaña delantera
)


def aristas_x(wp, y, z, tol=0.01):
    """Selecciona las aristas paralelas a X que pasan por (y, z)."""
    return wp.edges(
        cq.selectors.BoxSelector((-1, y - tol, z - tol), (W + 1, y + tol, z + tol))
    )


# Dobleces exteriores (radio = interior + espesor) e interiores
cuerpo = aristas_x(cuerpo, 0, 0).fillet(R_DOBLEZ + t)
cuerpo = aristas_x(cuerpo, prof, 0).fillet(R_DOBLEZ + t)
cuerpo = aristas_x(cuerpo, t, t).fillet(R_DOBLEZ)
cuerpo = aristas_x(cuerpo, t + G, t).fillet(R_DOBLEZ)

# Esquinas superiores redondeadas (aristas paralelas a Y)
def aristas_y(wp, x, z, y0, y1, tol=0.01):
    return wp.edges(
        cq.selectors.BoxSelector((x - tol, y0 - tol, z - tol), (x + tol, y1 + tol, z + tol))
    )

for x in (0, W):
    cuerpo = aristas_y(cuerpo, x, H, 0, t).fillet(R_ESQ_PLACA)
    cuerpo = aristas_y(cuerpo, x, L, t + G, prof).fillet(R_ESQ_LABIO)

# Agujeros avellanados (el avellanado mira hacia adentro de la U)
prof_cono = (D_AVELLANADO - D_AGUJERO) / 2  # cono a 90°
for dx in (-SEP_AGUJEROS / 2, SEP_AGUJEROS / 2):
    x = W / 2 + dx
    pasante = (
        cq.Workplane("XZ").center(x, Z_AGUJEROS).circle(D_AGUJERO / 2)
        .extrude(-(t + 2)).translate((0, -1, 0))
    )
    cono = cq.Solid.makeCone(
        D_AGUJERO / 2, D_AVELLANADO / 2 + 0.01, prof_cono + 0.01,
        pnt=cq.Vector(x, t - prof_cono, Z_AGUJEROS), dir=cq.Vector(0, 1, 0),
    )
    cuerpo = cuerpo.cut(pasante).cut(cq.Workplane().add(cono))

# Bisel finito en todos los bordes para que no corte (0.4 mm)
try:
    cuerpo = cuerpo.edges().chamfer(0.4)
except Exception:
    pass

if __name__ == "__main__":
    import os
    aqui = os.path.dirname(os.path.abspath(__file__))
    cq.exporters.export(cuerpo, os.path.join(aqui, "soporte_gancho.stl"), tolerance=0.02, angularTolerance=0.1)
    cq.exporters.export(cuerpo, os.path.join(aqui, "soporte_gancho.step"))
    bb = cuerpo.val().BoundingBox()
    print(f"OK  {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm  vol={cuerpo.val().Volume()/1000:.1f} cm3  valido={cuerpo.val().isValid()}")
