"""Consultas de la HU Q01 sobre la tabla prioridades (proyecto integrador).

Lee data/limpio/prioridades_limpio.csv, resuelve las cinco consultas con
pandas, imprime el título y el resultado de cada una y guarda
data/limpio/prioridades_consulta_N.csv.
"""
from pathlib import Path

import pandas as pd

RUTA_ENTRADA = Path("data/limpio/prioridades_limpio.csv")


def guardar(resultado, carpeta, numero):
    """Guarda el resultado de una consulta como prioridades_consulta_N.csv."""
    ruta = carpeta / f"prioridades_consulta_{numero}.csv"
    resultado.to_csv(ruta, encoding="utf-8")
    return ruta


def consulta_1(df):
    """Consulta 1: prioridades ordenadas de la más urgente a la menos urgente."""
    print("\nConsulta 1 - ¿Cuáles son las prioridades ordenadas de la más urgente a la menos urgente?")
    ordenadas = df.sort_values("nivel")
    print(ordenadas.to_string(index=False))
    return ordenadas


def consulta_2(df):
    """Consulta 2: solo las prioridades urgentes (nivel 1 y 2)."""
    print("\nConsulta 2 - ¿Cuáles son las prioridades urgentes (nivel 1 y 2)?")
    urgentes = df[df["nivel"] <= 2]
    print(urgentes.to_string(index=False))
    return urgentes


def consulta_3(df):
    """Consulta 3: cuántas veces aparece cada nombre (detecta variantes)."""
    print("\nConsulta 3 - ¿Cuántas veces aparece cada nombre (se detectan las variantes)?")
    conteo = df["nombre"].value_counts()
    conteo.index.name = "nombre"
    conteo.name = "veces"
    print(conteo.to_string())
    return conteo


def consulta_4(df):
    """Consulta 4 (groupby): cuántas filas hay por nivel."""
    print("\nConsulta 4 - ¿Cuántas filas hay por nivel? (groupby)")
    por_nivel = df.groupby("nivel")["id"].count()
    por_nivel.name = "filas"
    print(por_nivel.to_string())
    return por_nivel


def consulta_5(df):
    """Consulta 5 (groupby): días de respuesta mínimo, promedio y máximo por prioridad."""
    print("\nConsulta 5 - ¿Cuáles son los días de respuesta mínimo, promedio y máximo por prioridad? (groupby)")
    resumen = df.groupby("nombre")["dias_max_respuesta"].agg(["min", "mean", "max"]).round(1)
    print(resumen.to_string())
    return resumen


def main():
    """Lee el CSV limpio, ejecuta las cinco consultas y guarda los resultados."""
    if not RUTA_ENTRADA.exists():
        print(f"Error: no se encontró el archivo {RUTA_ENTRADA}. Ejecuta primero la limpieza.")
        return

    df = pd.read_csv(RUTA_ENTRADA)
    carpeta = RUTA_ENTRADA.parent

    consultas = [consulta_1, consulta_2, consulta_3, consulta_4, consulta_5]
    for numero, consulta in enumerate(consultas, start=1):
        resultado = consulta(df)
        destino = guardar(resultado, carpeta, numero)
        print(f"-> guardado en {destino}")


if __name__ == "__main__":
    main()