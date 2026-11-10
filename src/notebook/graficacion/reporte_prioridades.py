"""Reporte de prioridades (HU G01): tres graficas y conclusiones.

Lee data/limpio/prioridades_limpio.csv y guarda las graficas en reportes/.
"""
import os

import matplotlib

matplotlib.use("Agg")  # Sin ventana: el script nunca se queda esperando
import matplotlib.pyplot as plt
import pandas as pd

RUTA_ENTRADA = os.path.join("data", "limpio", "prioridades_limpio.csv")
CARPETA = "reportes"
NIVEL_MIN, NIVEL_MAX = 1, 5


def guardar_grafica(numero):
    """Aplica tight_layout, guarda la grafica con dpi=120, la cierra y devuelve su ruta."""
    plt.tight_layout()
    ruta = os.path.join(CARPETA, f"prioridades_grafica_{numero}.png")
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def grafica_1(df):
    """Grafica 1 (barras): cuantas filas hay por nivel."""
    por_nivel = df.groupby("nivel")["id"].count()
    plt.figure(figsize=(7, 5))
    por_nivel.plot(kind="bar", rot=0)
    plt.title("Cantidad de filas por nivel")
    plt.xlabel("Nivel")
    plt.ylabel("Cantidad de filas")
    return guardar_grafica(1)


def grafica_2(df):
    """Grafica 2 (barras): dias promedio de respuesta por prioridad."""
    resumen = df.groupby("nombre")["dias_max_respuesta"].agg(["min", "mean", "max"]).round(1)
    # Ordenar de la prioridad mas urgente a la menos urgente
    orden = df.groupby("nombre")["nivel"].min().sort_values().index
    resumen = resumen.loc[orden]
    plt.figure(figsize=(8, 5))
    resumen["mean"].plot(kind="bar", rot=0)
    plt.title("Dias promedio de respuesta por prioridad")
    plt.xlabel("Prioridad")
    plt.ylabel("Dias promedio de respuesta")
    return guardar_grafica(2)


def grafica_3(df):
    """Grafica 3 (torta): reparto de las prioridades."""
    conteo = df["nombre"].value_counts()
    plt.figure(figsize=(6, 6))
    conteo.plot(kind="pie", autopct="%1.1f%%")
    plt.title("Reparto de las prioridades")
    plt.xlabel("Prioridad")
    plt.ylabel("Proporcion de filas", labelpad=25)
    return guardar_grafica(3)


def imprimir_conclusiones(df):
    """Imprime las conclusiones calculadas a partir de los datos."""
    reales = df["nombre"].nunique()
    promedio = df.groupby("nivel")["dias_max_respuesta"].mean().round(1)
    fuera = (~df["nivel"].between(NIVEL_MIN, NIVEL_MAX)).sum()

    print("\n=== CONCLUSIONES ===")
    print(f"1. Prioridades reales que quedaron al final: {reales} "
          f"({', '.join(sorted(df['nombre'].unique()))}).")
    print("2. Relacion entre nivel y dias maximos de respuesta: "
          "a mayor nivel (menos urgente), mas dias para responder.")
    print("   Dias promedio por nivel:")
    for nivel, dias in promedio.items():
        print(f"     nivel {int(nivel)}: {dias} dias")
    print("   (Los promedios se desvian un poco de 1, 3, 7, 15 y 30 porque "
          "los valores nulos y absurdos se rellenaron con la mediana.)")
    print(f"3. El back debe validar que nivel este entre {NIVEL_MIN} y {NIVEL_MAX} "
          "porque solo existen esas 5 prioridades: un valor fuera de rango "
          "(0, 7, 999, texto o vacio) no corresponde a ninguna prioridad real, "
          "rompe la relacion con los dias de respuesta y dana los reportes.")
    print(f"   Filas con nivel fuera de rango en este archivo: {fuera}.")


def main():
    """Lee el CSV limpio, crea las tres graficas y muestra las conclusiones."""
    if not os.path.exists(RUTA_ENTRADA):
        print(f"Error: no se encontro {RUTA_ENTRADA}. Ejecuta primero la limpieza.")
        return

    df = pd.read_csv(RUTA_ENTRADA)
    df["nivel"] = df["nivel"].astype(int)  # 1.0 -> 1 en los ejes
    os.makedirs(CARPETA, exist_ok=True)

    for grafica in (grafica_1, grafica_2, grafica_3):
        print("Guardada:", grafica(df))

    imprimir_conclusiones(df)


if __name__ == "__main__":
    main()