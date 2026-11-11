"""
consultar_retos.py - HU Q01: consultas sobre la tabla retos (archivo LIMPIO).

Uso (desde cualquier carpeta):
    python src/notebook/consultas/consultar_retos.py

Lee data/limpio/retos_limpio.csv y resuelve cinco consultas con pandas, cada
una en su propia función. Imprime el título y el resultado de cada una y guarda
data/limpio/retos_consulta_N.csv.
"""

import os
import sys
from pathlib import Path

import pandas as pd

# Raiz del proyecto: consultas -> notebook -> src -> raiz
RAIZ = Path(__file__).resolve().parents[3]
CARPETA_LIMPIO = RAIZ / "data" / "limpio"
RUTA_ENTRADA = CARPETA_LIMPIO / "retos_limpio.csv"

COLUMNAS_NECESARIAS = ["id", "nombre", "estado", "duracion_dias", "fecha_inicio"]


def cargar_datos(ruta):
    """Lee retos_limpio.csv, valida las columnas y convierte los tipos."""
    if not os.path.isfile(ruta):
        sys.exit(f"ERROR: no existe el archivo '{ruta}'.")
    df = pd.read_csv(ruta)
    faltan = [c for c in COLUMNAS_NECESARIAS if c not in df.columns]
    if faltan:
        sys.exit(f"ERROR: faltan columnas en el archivo: {faltan}")
    # La fecha debe ser datetime para poder agrupar por mes (.dt.to_period)
    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce")
    df["duracion_dias"] = pd.to_numeric(df["duracion_dias"], errors="coerce")
    return df


def consulta_1(df):
    """Consulta 1: ¿Qué retos están en curso? (filtro por estado EN_CURSO)."""
    en_curso = df[df["estado"] == "EN_CURSO"]
    return en_curso


def consulta_2(df):
    """Consulta 2: ¿Cuáles son los 10 retos más largos? (nlargest por duración)."""
    largos = df.nlargest(10, "duracion_dias")[["nombre", "duracion_dias", "estado"]]
    return largos


def consulta_3(df):
    """Consulta 3: ¿Cuántos retos hay por estado? (value_counts)."""
    conteo = df["estado"].value_counts().rename_axis("estado").reset_index(name="cantidad")
    return conteo


def consulta_4(df):
    """Consulta 4 (GROUPBY): duración promedio, mínima y máxima por estado."""
    resumen = df.groupby("estado")["duracion_dias"].agg(["count", "mean", "min", "max"])
    resumen["mean"] = resumen["mean"].round(2)
    return resumen.reset_index()


def consulta_5(df):
    """Consulta 5 (GROUPBY): ¿cuántos retos empiezan cada mes?"""
    por_mes = df.groupby(df["fecha_inicio"].dt.to_period("M"))["id"].count()
    por_mes = por_mes.rename("cantidad").reset_index()
    por_mes = por_mes.rename(columns={"fecha_inicio": "mes"})
    por_mes["mes"] = por_mes["mes"].astype(str)  # 2025-03 en vez de Period
    return por_mes


def mostrar_y_guardar(numero, titulo, resultado, carpeta):
    """Imprime el título y el resultado de la consulta y guarda retos_consulta_N.csv."""
    print(f"\n=== Consulta {numero}: {titulo} ===")
    if resultado.empty:
        print("(sin resultados)")
    else:
        print(resultado.to_string(index=False))
    ruta = os.path.join(carpeta, f"retos_consulta_{numero}.csv")
    resultado.to_csv(ruta, index=False)
    print(f"-> guardado en {ruta}")


def main():
    """Punto de entrada: lee el CSV limpio y ejecuta las cinco consultas en orden."""
    ruta = RUTA_ENTRADA
    carpeta = CARPETA_LIMPIO
    df = cargar_datos(ruta)
    print(f"Archivo leído: {ruta} ({len(df)} filas)")

    consultas = [
        (1, "Retos que están en curso", consulta_1),
        (2, "Los 10 retos más largos", consulta_2),
        (3, "Cuántos retos hay por estado", consulta_3),
        (4, "Duración promedio, mínima y máxima por estado", consulta_4),
        (5, "Cuántos retos empiezan cada mes", consulta_5),
    ]
    for numero, titulo, funcion in consultas:
        mostrar_y_guardar(numero, titulo, funcion(df), carpeta)


if __name__ == "__main__":
    main()