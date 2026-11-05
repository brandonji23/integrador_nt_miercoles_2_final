"""Consultas de la HU Q01 sobre la tabla empresas.

Uso (desde la raiz del proyecto):
    python src/notebook/consultas/consultas_empresas.py

Lee data/limpio/empresas_limpio.csv, resuelve cinco consultas (cada una en su
funcion), imprime el titulo y el resultado, y guarda
data/limpio/empresas_consulta_N.csv.
Opcional: python src/notebook/consultas/consultas_empresas.py [ruta_csv_limpio]
"""
import sys
from pathlib import Path

import pandas as pd

# Raiz del proyecto: consultas -> notebook -> src -> raiz
RAIZ = Path(__file__).resolve().parents[3]
RUTA_LIMPIO = RAIZ / "data" / "limpio" / "empresas_limpio.csv"

# Sector que se usa en la consulta 2 (debe existir en los datos).
SECTOR_CONSULTA = "Salud"


def cargar_datos(ruta):
    """Lee el CSV limpio y deja la columna 'activa' como booleana."""
    df = pd.read_csv(ruta)
    if df["activa"].dtype != bool:
        # Por si el CSV trae "True"/"False" como texto.
        df["activa"] = df["activa"].astype(str).str.strip().str.lower() == "true"
    return df


def guardar(resultado, carpeta, numero):
    """Guarda el resultado de una consulta como empresas_consulta_N.csv."""
    resultado.to_csv(carpeta / f"empresas_consulta_{numero}.csv")


def consulta_1_activas(df):
    """Consulta 1: devuelve las empresas activas."""
    print("\nConsulta 1 - Que empresas estan activas?")
    activas = df[df["activa"] == True]  # noqa: E712
    print(activas.to_string(index=False))
    return activas


def consulta_2_sector(df):
    """Consulta 2: empresas de un sector, ordenadas por nombre."""
    print(f"\nConsulta 2 - Que empresas son del sector {SECTOR_CONSULTA}, ordenadas por nombre?")
    del_sector = df[df["sector"] == SECTOR_CONSULTA].sort_values("nombre")
    print(del_sector.to_string(index=False))
    return del_sector


def consulta_3_conteo(df):
    """Consulta 3: conteo rapido de empresas por sector (value_counts)."""
    print("\nConsulta 3 - Cuantas empresas hay por sector (conteo rapido)?")
    conteo = df["sector"].value_counts()
    print(conteo.to_string())
    return conteo


def consulta_4_groupby(df):
    """Consulta 4 (groupby): empresas por sector, de mayor a menor."""
    print("\nConsulta 4 - Cuantas empresas hay por sector, de mayor a menor? (groupby)")
    por_sector = df.groupby("sector")["id"].count().sort_values(ascending=False)
    print(por_sector.to_string())
    return por_sector


def consulta_5_groupby_doble(df):
    """Consulta 5 (groupby doble): activas e inactivas por sector."""
    print("\nConsulta 5 - Cuantas empresas activas e inactivas hay por sector? (groupby doble)")
    tabla = df.groupby(["sector", "activa"])["id"].count().unstack(fill_value=0)
    print(tabla.to_string())
    return tabla


def main():
    """Carga el CSV, ejecuta las cinco consultas en orden y guarda los resultados."""
    ruta = Path(sys.argv[1]) if len(sys.argv) > 1 else RUTA_LIMPIO
    df = cargar_datos(ruta)
    carpeta = ruta.parent

    consultas = [
        consulta_1_activas,
        consulta_2_sector,
        consulta_3_conteo,
        consulta_4_groupby,
        consulta_5_groupby_doble,
    ]
    for numero, consulta in enumerate(consultas, start=1):
        guardar(consulta(df), carpeta, numero)

    print("\nListo: se guardaron empresas_consulta_1.csv ... empresas_consulta_5.csv")


if __name__ == "__main__":
    main()