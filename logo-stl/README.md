# Logo "studio" – cartel de 50 cm para Bambu Lab

Cartel de **500 × 104 mm**, fondo negro de 5 mm + logo blanco en relieve de 2 mm (7 mm total).
Va en **3 piezas** con encastre **cola de milano** (0,15 mm de holgura por lado) para que entre en la cama
de 256 × 256 mm (X1, P1, A1, H2D). Los cortes están alineados con bordes verticales del logo para que la unión casi no se note.

| Pieza | Medida (con la cola) |
|---|---|
| 1 | 186 × 104 mm |
| 2 | 189 × 104 mm |
| 3 | 144 × 104 mm |

## Archivos (`stl/`)
- `pieza_N_fondo_negro.stl` + `pieza_N_logo_blanco.stl` → para imprimir con **AMS** (2 colores).
- `pieza_N_completa.stl` → un solo cuerpo, para imprimir **sin AMS** con cambio de filamento por altura.
- `cartel_completo_referencia.stl` → sólo para ver el cartel entero (no entra en la cama).

## Cómo imprimir en Bambu Studio
**Con AMS:** arrastrá juntos `pieza_1_fondo_negro.stl` y `pieza_1_logo_blanco.stl` → cuando pregunte
"¿Cargar como un solo objeto con varias partes?" decí **Sí** → asigná filamento negro al fondo y blanco al logo. Repetí con las piezas 2 y 3.

**Sin AMS:** abrí `pieza_N_completa.stl`, en la barra de capas (derecha) andá a **Z = 5,0 mm**, clic derecho en el `+` →
**Añadir pausa / cambio de filamento**. La impresora para, cambiás a blanco y sigue.

Ajustes sugeridos: PLA, capa 0,2 mm, 3–4 paredes, 15 % de relleno, sin soportes, apoyada con la cara lisa de atrás sobre la cama.

## Tiempo y peso estimados
PLA, capa 0,2 mm, 2 paredes, 15 % de relleno, velocidades tipo X1/P1. Lo calculé con otro slicer (PrusaSlicer configurado como una Bambu), así que puede variar un poco respecto de Bambu Studio.

| Pieza | Tiempo | Peso |
|---|---|---|
| 1 | ~1 h 32 min | ~58 g |
| 2 | ~1 h 38 min | ~58 g |
| 3 | ~1 h 17 min | ~44 g |
| **Total** | **~4 h 30 min** | **~160 g** (~120 g negro + ~40 g blanco) |

Con AMS sumá ~5 min y ~5–10 g de purga por pieza (hay un solo cambio de color por pieza). En la A1, que es más lenta, puede tardar entre un 20 y un 30 % más.

## Armado
Encastrá las colas de milano (entran de arriba hacia abajo) y poné una gota de pegamento (CA / gotita) en la unión.
Para colgarlo: cinta doble faz o adhesivo de montaje en la parte de atrás.

## Regenerar / cambiar medidas o colores
Los colores se cambian con `COLOR_FONDO` / `COLOR_LOGO` arriba del script (sólo cambian nombres de archivo y la vista previa; la geometría es la misma).

```bash
pip install numpy pillow opencv-python-headless shapely trimesh manifold3d mapbox_earcut rtree matplotlib
python3 generar_stl.py
```
Los parámetros (ancho total, margen, espesores, holgura, posición de los cortes) están arriba de `generar_stl.py`.
