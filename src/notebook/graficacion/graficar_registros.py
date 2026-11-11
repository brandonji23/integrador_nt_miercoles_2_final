"""Gráficas de la HU G01 sobre la tabla registros (archivo LIMPIO).

Ubicación: src/notebook/graficacion/graficar_registros.py
Lee:       data/limpio/registros_limpio.csv  (y data/crudo/registros_sucio.csv
           solo para contar las inscripciones duplicadas de las conclusiones)
Guarda:    reportes/registros_grafica_1.png, _2.png y _3.png

Se puede ejecutar de dos formas (desde cualquier carpeta):
    python src/notebook/graficacion/graficar_registros.py
    o importando graficar_registros() desde main.py
"""
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Sin ventana: el script nunca se queda esperando
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

# graficacion -> notebook -> src -> raíz del proyecto
RAIZ = Path(__file__).resolve().parents[3]
RUTA_LIMPIO = RAIZ / "data" / "limpio" / "registros_limpio.csv"
RUTA_SUCIO = RAIZ / "data" / "crudo" / "registros_sucio.csv"
CARPETA_REPORTES = RAIZ / "reportes"


def leer_registros(ruta=RUTA_LIMPIO):
    """Lee el CSV limpio y valida que existan las columnas necesarias."""
    ruta = Path(ruta)
    if not ruta.is_file():
        raise SystemExit(f"Error: no existe '{ruta}'. Ejecuta primero la limpieza.")

    df = pd.read_csv(ruta)
    requeridas = {"id", "id_usuario", "id_reto", "estado", "mes"}
    faltan = requeridas - set(df.columns)
    if faltan:
        raise SystemExit(f"Error: faltan columnas en el CSV: {sorted(faltan)}")
    return df


def guardar_grafica(ruta):
    """Ajusta el diseño, guarda la figura con dpi=120 y la cierra."""
    plt.tight_layout()
    plt.savefig(ruta, dpi=120)
    plt.close()


def grafica_1_estados(df):
    """Gráfica 1 (barras): participaciones por estado."""
    conteo = df["estado"].value_counts()
    conteo.plot(kind="bar")
    plt.title("Participaciones por estado")
    plt.xlabel("Estado")
    plt.ylabel("Número de participaciones")
    plt.xticks(rotation=30, ha="right")
    ruta = CARPETA_REPORTES / "registros_grafica_1.png"
    guardar_grafica(ruta)
    return ruta


def grafica_2_meses(df):
    """Gráfica 2 (línea): participaciones por mes. Devuelve (ruta, serie)."""
    por_mes = df.groupby("mes")["id"].count()
    por_mes.plot(kind="line", marker="o")
    plt.title("Participaciones por mes")
    plt.xlabel("Mes")
    plt.ylabel("Número de participaciones")
    plt.xticks(range(len(por_mes)), por_mes.index, rotation=45, ha="right")
    ruta = CARPETA_REPORTES / "registros_grafica_2.png"
    guardar_grafica(ruta)
    return ruta, por_mes


def grafica_3_retos(df):
    """Gráfica 3 (barras horizontales): los 10 retos con más participantes.

    Devuelve (ruta, serie con todos los retos ordenados de mayor a menor).
    """
    todos = df.groupby("id_reto")["id"].count().sort_values(ascending=False)
    top_retos = todos.head(10).sort_values()  # el mayor queda arriba en barh
    top_retos.index = top_retos.index.str[:8]  # id corto para que se lea bien
    top_retos.plot(kind="barh")
    plt.title("Top 10 retos con más participantes")
    plt.xlabel("Número de participantes")
    plt.ylabel("Reto (primeros 8 caracteres del id)")
    ruta = CARPETA_REPORTES / "registros_grafica_3.png"
    guardar_grafica(ruta)
    return ruta, todos


def contar_duplicados(df_limpio):
    """Cuenta las inscripciones duplicadas (mismo usuario en el mismo reto).

    El archivo limpio ya no tiene duplicados, así que se cuentan en el archivo
    sucio. Devuelve (duplicados, total_de_filas, nombre_del_archivo_usado).
    """
    if RUTA_SUCIO.is_file():
        sucio = pd.read_csv(RUTA_SUCIO)
        repetidas = sucio.duplicated(subset=["id_usuario", "id_reto"], keep="first")
        return int(repetidas.sum()), len(sucio), RUTA_SUCIO.name
    repetidas = df_limpio.duplicated(subset=["id_usuario", "id_reto"], keep="first")
    return int(repetidas.sum()), len(df_limpio), RUTA_LIMPIO.name


def imprimir_conclusiones(todos, por_mes, n_duplicados, n_total, archivo):
    """Imprime las conclusiones que pide la HU."""
    print("\nCONCLUSIONES")
    print(f"- Reto más popular: '{todos.index[0]}' con {todos.iloc[0]} participantes.")
    print(f"- Mes con más inscripciones: {por_mes.idxmax()} ({por_mes.max()} inscripciones).")
    print(f"- Inscripciones duplicadas encontradas: {n_duplicados} de {n_total} filas ({archivo}).")
    print("  El back debe bloquearlas con 409 (Conflict) porque la inscripción ya existe:")
    print("  aceptar al mismo usuario dos veces en el mismo reto inflaría los conteos,")
    print("  y es el servidor quien debe rechazarla, no el análisis de datos.")


def graficar_registros(ruta_entrada=RUTA_LIMPIO):
    """Lee el CSV limpio, crea las tres gráficas e imprime las conclusiones."""
    os.makedirs(CARPETA_REPORTES, exist_ok=True)
    df = leer_registros(ruta_entrada)

    print("Gráficas generadas:")
    print(" ", grafica_1_estados(df))
    ruta2, por_mes = grafica_2_meses(df)
    print(" ", ruta2)
    ruta3, todos = grafica_3_retos(df)
    print(" ", ruta3)

    n_duplicados, n_total, archivo = contar_duplicados(df)
    imprimir_conclusiones(todos, por_mes, n_duplicados, n_total, archivo)


if __name__ == "__main__":
    graficar_registros()