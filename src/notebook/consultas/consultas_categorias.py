import os
from pathlib import Path

import pandas as pd

# Raíz del proyecto: integrador_kevin_moncada/
RAIZ = Path(__file__).resolve().parents[3]
CARPETA_LIMPIO = RAIZ / "data" / "limpio"
RUTA_LIMPIO = CARPETA_LIMPIO / "categorias_limpio.csv"


def cargar_datos():
    """Lee el archivo LIMPIO (no el sucio)."""
    return pd.read_csv(RUTA_LIMPIO, encoding="utf-8")


def consulta_1(df):
    """Cuántas veces aparece cada categoría (detecta las variantes)."""
    print("\nConsulta 1 — ¿Cuántas veces aparece cada categoría? (detecta las variantes)")
    return df["nombre"].value_counts()


def consulta_2(df):
    """Categorías sin descripción."""
    print("\nConsulta 2 — ¿Qué categorías no tienen descripción?")
    return df[df["descripcion"] == "Sin descripcion"]


def consulta_3(df):
    """GROUPBY: largo promedio de la descripción por categoría."""
    print("\nConsulta 3 — ¿Cuál es el largo promedio de la descripción por categoría?")
    return df.groupby("nombre")["largo_desc"].mean().round(1).sort_values(ascending=False)


def consulta_4(df):
    """GROUPBY: cuántas categorías maneja cada área."""
    print("\nConsulta 4 — ¿Cuántas categorías maneja cada área?")
    return df.groupby("area_responsable")["id"].count().sort_values(ascending=False)


def consulta_5(df):
    """GROUPBY doble: categorías por área (tabla cruzada)."""
    print("\nConsulta 5 — ¿Cuántas filas de cada categoría tiene cada área? (tabla cruzada)")
    return df.groupby(["area_responsable", "nombre"])["id"].count().unstack(fill_value=0)


def mostrar_y_guardar(resultado, numero, con_indice):
    """Imprime el resultado y lo guarda como data/limpio/categorias_consulta_N.csv."""
    if len(resultado) == 0:
        print("(sin resultados)")
    else:
        print(resultado.to_string())
    ruta = CARPETA_LIMPIO / f"categorias_consulta_{numero}.csv"
    resultado.to_csv(ruta, index=con_indice, encoding="utf-8")
    print(f"-> guardado en {ruta}")


def ejecutar_consultas(df=None):
    if df is None:
        df = cargar_datos()

    os.makedirs(CARPETA_LIMPIO, exist_ok=True)
    print(f"Archivo: {RUTA_LIMPIO} — {df.shape[0]} filas")

    # (función, ¿se guarda con índice?)
    consultas = [
        (consulta_1, True),
        (consulta_2, False),
        (consulta_3, True),
        (consulta_4, True),
        (consulta_5, True),
    ]
    resultados = []
    for numero, (funcion, con_indice) in enumerate(consultas, start=1):
        resultado = funcion(df)
        mostrar_y_guardar(resultado, numero, con_indice)
        resultados.append(resultado)
    return resultados


if __name__ == "__main__":
    ejecutar_consultas()