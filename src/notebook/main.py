import sys
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent

# Agregamos las carpetas para poder importar los modulos
sys.path.insert(0, str(BASE / "simulacion"))
sys.path.insert(0, str(BASE / "exportacion"))
sys.path.insert(0, str(BASE / "limpieza"))
sys.path.insert(0, str(BASE / "consultas"))
sys.path.insert(0, str(BASE / "graficacion"))

from simular_retos import generar_retos
from exportar_retos import exportar_retos
from limpiar_retos import main as limpiar_retos, RUTA_SALIDA, COLUMNAS_OBLIGATORIAS
from consultar_retos import main as consultar_retos, CARPETA_LIMPIO
from graficar_retos import main as graficar_retos, CARPETA as CARPETA_REPORTES

COLUMNAS = [
    "id", "nombre", "descripcion", "fecha_inicio", "fecha_fin",
    "estado", "id_empresa", "id_categoria", "id_prioridad",
]


def comprobar(nombre, condicion):
    print(f"[{'PASA' if condicion else 'FALLA'}] {nombre}")


def probar_simulacion():
    print("\n=== HU F01: simulacion ===")
    df = generar_retos()

    print(df.shape)
    print(df.head())
    print(df.isna().sum())

    comprobar("devuelve un DataFrame", isinstance(df, pd.DataFrame))
    comprobar("tiene las 9 columnas de la HU", list(df.columns) == COLUMNAS)
    comprobar("525 filas (500 + 5% duplicados)", len(df) == 525)
    comprobar("25 duplicados exactos", df.duplicated().sum() == 25)
    comprobar("hay nulos en descripcion", df["descripcion"].isna().any())
    comprobar("hay nulos en fecha_fin", df["fecha_fin"].isna().any())
    comprobar(
        "fecha_inicio mezcla dos formatos",
        df["fecha_inicio"].astype(str).str.contains("/").any()
        and df["fecha_inicio"].astype(str).str.contains("-").any(),
    )
    comprobar(
        "estado tiene variantes sucias",
        df["estado"].isin(["en_curso", "EN CURSO", " Cerrado "]).any(),
    )
    comprobar("nombre tiene espacios sobrantes", (df["nombre"] != df["nombre"].str.strip()).any())

    return df


def probar_exportacion():
    print("\n=== HU X01: exportacion ===")
    rutas = exportar_retos()

    for ruta in rutas:
        comprobar(f"existe {ruta.name}", ruta.exists())

    csv, xlsx, json = rutas
    comprobar("CSV se lee con 525 filas", pd.read_csv(csv).shape == (525, 9))
    comprobar("XLSX se lee con 525 filas", pd.read_excel(xlsx, sheet_name="retos").shape == (525, 9))
    comprobar("JSON se lee con 525 filas", pd.read_json(json, orient="records").shape == (525, 9))


def probar_limpieza():
    print("\n=== HU L01: limpieza ===")
    # Lee data/crudo/retos_sucio.csv (lo que acaba de crear la exportacion)
    limpiar_retos()

    comprobar("existe retos_limpio.csv", RUTA_SALIDA.exists())

    limpio = pd.read_csv(RUTA_SALIDA)
    comprobar("tiene 11 columnas (9 + duracion_dias + fecha_valida)", limpio.shape[1] == 11)
    comprobar("se eliminaron filas (menos de 525)", limpio.shape[0] < 525)
    comprobar("no quedan duplicados exactos", limpio.duplicated().sum() == 0)
    comprobar("sin nulos en columnas obligatorias", limpio[COLUMNAS_OBLIGATORIAS].isna().sum().sum() == 0)
    comprobar("sin nulos en descripcion", limpio["descripcion"].isna().sum() == 0)
    comprobar(
        "estado sin espacios y en mayusculas",
        (limpio["estado"] == limpio["estado"].str.strip().str.upper()).all()
        and not limpio["estado"].str.contains(" ").any(),
    )
    comprobar(
        "fechas convertidas a formato AAAA-MM-DD",
        limpio["fecha_inicio"].str.match(r"^\d{4}-\d{2}-\d{2}$").all()
        and limpio["fecha_fin"].str.match(r"^\d{4}-\d{2}-\d{2}$").all(),
    )
    comprobar(
        "fecha_valida coincide con duracion_dias >= 0",
        (limpio["fecha_valida"] == (limpio["duracion_dias"] >= 0)).all(),
    )


def probar_consultas():
    print("\n=== HU Q01: consultas ===")
    # Lee data/limpio/retos_limpio.csv (lo que acaba de crear la limpieza)
    consultar_retos()

    total = len(pd.read_csv(RUTA_SALIDA))
    rutas = [CARPETA_LIMPIO / f"retos_consulta_{n}.csv" for n in range(1, 6)]

    for ruta in rutas:
        comprobar(f"existe {ruta.name}", ruta.exists())

    c1, c2, c3, c4, c5 = [pd.read_csv(r) for r in rutas]

    comprobar("consulta 1: solo retos EN_CURSO", (c1["estado"] == "EN_CURSO").all())
    comprobar("consulta 2: 10 retos ordenados de mayor a menor duracion",
              len(c2) == 10 and c2["duracion_dias"].is_monotonic_decreasing)
    comprobar("consulta 3: los conteos por estado suman todas las filas", c3["cantidad"].sum() == total)
    comprobar("consulta 4: groupby por estado cuenta todas las filas", c4["count"].sum() == total)
    comprobar("consulta 4: tiene count, mean, min y max",
              {"count", "mean", "min", "max"}.issubset(c4.columns))
    comprobar("consulta 5: groupby por mes cuenta todas las filas", c5["cantidad"].sum() == total)


def probar_graficas():
    print("\n=== HU G01: graficas ===")
    # Lee data/limpio/retos_limpio.csv y guarda las imagenes en reportes/
    graficar_retos()

    for n in range(1, 4):
        ruta = CARPETA_REPORTES / f"retos_grafica_{n}.png"
        comprobar(f"existe {ruta.name} y no esta vacia", ruta.exists() and ruta.stat().st_size > 0)


if __name__ == "__main__":
    probar_simulacion()
    probar_exportacion()
    probar_limpieza()
    probar_consultas()
    probar_graficas()