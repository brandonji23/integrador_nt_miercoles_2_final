import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # sin ventana: el script guarda las imágenes y termina
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

# Raíz del proyecto: integrador_kevin_moncada/
RAIZ = Path(__file__).resolve().parents[3]
RUTA_LIMPIO = RAIZ / "data" / "limpio" / "categorias_limpio.csv"
RUTA_SUCIO = RAIZ / "data" / "crudo" / "categorias_sucio.csv"
CARPETA = RAIZ / "reportes"

FILAS_ORIGINALES = 250  # filas que genera la simulación (HU F01)


def cargar_datos():
    """Lee el archivo LIMPIO."""
    return pd.read_csv(RUTA_LIMPIO, encoding="utf-8")


def guardar(numero):
    """Aplica tight_layout, guarda con dpi=120, cierra la figura y devuelve la ruta."""
    plt.tight_layout()
    ruta = CARPETA / f"categorias_grafica_{numero}.png"
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def grafica_1(df):
    """Barras horizontales: cuántas veces aparece cada categoría."""
    conteo = df["nombre"].value_counts()
    conteo.plot(kind="barh", color="#4C78A8")
    plt.gca().invert_yaxis()  # la categoría más repetida arriba
    plt.title("Veces que aparece cada categoría")
    plt.xlabel("Cantidad de filas")
    plt.ylabel("Categoría")
    return guardar(1)


def grafica_2(df):
    """Torta: reparto de categorías por área responsable."""
    por_area = df.groupby("area_responsable")["id"].count().sort_values(ascending=False)
    plt.figure(figsize=(9, 6))  # más ancho para que quepan los nombres de área
    por_area.plot(kind="pie", autopct="%1.1f%%")
    plt.title("Reparto de categorías por área responsable")
    plt.xlabel("Área responsable")
    plt.ylabel("Proporción de filas")
    plt.gca().yaxis.set_label_coords(-0.28, 0.5)  # lo separa de los nombres de área
    return guardar(2)


def grafica_3(df):
    """Barras: largo promedio de la descripción por categoría."""
    largos = df.groupby("nombre")["largo_desc"].mean().round(1).sort_values(ascending=False)
    largos.plot(kind="bar", color="#59A14F")
    plt.title("Largo promedio de la descripción por categoría")
    plt.xlabel("Categoría")
    plt.ylabel("Largo promedio (caracteres)")
    plt.xticks(rotation=45, ha="right")
    return guardar(3)


def filas_originales():
    """Filas del archivo sucio si existe; si no, las 250 que genera la simulación."""
    if RUTA_SUCIO.exists():
        return len(pd.read_csv(RUTA_SUCIO, encoding="utf-8"))
    return FILAS_ORIGINALES


def imprimir_conclusiones(df):
    original = filas_originales()
    eliminadas = original - len(df)
    reales = df["nombre"].nunique()

    print("\n=== Conclusiones ===")
    print(f"1. ¿Cuántas filas se eliminaron al quitar duplicados y variantes de escritura?\n"
          f"   Había {original} filas y quedaron {len(df)}: se eliminaron {eliminadas} "
          f"(las filas repetidas tal cual). Las variantes de escritura no eliminan filas: "
          f"se unifican en el mismo nombre.")
    print(f"2. ¿Cuántas categorías REALES quedaron al final?\n"
          f"   Quedaron {reales} categorías reales "
          f"({'coincide con las 10 esperadas' if reales == 10 else 'ojo: se esperaban 10'}).")
    print("3. ¿Por qué el back debe declarar `nombre` como ÚNICO?\n"
          "   Porque la base de datos rechazaría una categoría repetida o escrita de otra "
          "forma desde el origen. Así el catálogo no llega con duplicados ni variantes "
          "('Logística', 'LOGISTICA', ' logistica '), y no hay que limpiarlo después.")


def ejecutar_reporte(df=None):
    if df is None:
        df = cargar_datos()

    os.makedirs(CARPETA, exist_ok=True)
    rutas = [grafica_1(df), grafica_2(df), grafica_3(df)]

    print("Gráficas guardadas:")
    for ruta in rutas:
        print(f"  {ruta}")

    imprimir_conclusiones(df)
    return rutas


if __name__ == "__main__":
    ejecutar_reporte()