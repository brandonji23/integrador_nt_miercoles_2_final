"""Reporte gráfico de la tabla retos (HU G01).

Lee data/limpio/retos_limpio.csv, crea tres gráficas con matplotlib, las guarda
en reportes/ (en la raíz del proyecto) e imprime las rutas y las conclusiones.

Uso (desde cualquier carpeta):
    python src/notebook/graficacion/graficar_retos.py
"""
import os
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # sin ventana: el script guarda las imágenes y no se queda esperando
import matplotlib.pyplot as plt
import pandas as pd

# Raiz del proyecto: graficacion -> notebook -> src -> raiz
RAIZ = Path(__file__).resolve().parents[3]
RUTA_ENTRADA = RAIZ / "data" / "limpio" / "retos_limpio.csv"
CARPETA = RAIZ / "reportes"
DPI = 120
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def leer_datos(ruta):
    """Lee el CSV limpio, convierte las fechas y asegura la columna duracion_dias."""
    df = pd.read_csv(ruta, encoding="utf-8-sig")
    for col in ("fecha_inicio", "fecha_fin"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    if "duracion_dias" in df.columns:
        df["duracion_dias"] = pd.to_numeric(df["duracion_dias"], errors="coerce")
    elif {"fecha_inicio", "fecha_fin"} <= set(df.columns):
        # si el archivo no trae la duración, se calcula a partir de las fechas
        df["duracion_dias"] = (df["fecha_fin"] - df["fecha_inicio"]).dt.days
    else:
        raise ValueError("Faltan duracion_dias o las columnas fecha_inicio y fecha_fin.")
    for col in ("estado", "fecha_inicio"):
        if col not in df.columns:
            raise ValueError(f"Falta la columna obligatoria: {col}")
    return df


def guardar_grafica(nombre):
    """Aplica tight_layout, guarda la figura actual con dpi=120, la cierra y devuelve la ruta."""
    os.makedirs(CARPETA, exist_ok=True)
    ruta = CARPETA / nombre
    plt.tight_layout()
    plt.savefig(ruta, dpi=DPI)
    plt.close()
    return ruta


def grafica_barras_estado(df):
    """Gráfica 1: barras con la cantidad de retos por estado."""
    conteo = df["estado"].value_counts()
    plt.figure(figsize=(8, 5))
    conteo.plot(kind="bar")
    plt.title("Cantidad de retos por estado")
    plt.xlabel("Estado")
    plt.ylabel("Cantidad de retos")
    plt.xticks(rotation=0)
    return guardar_grafica("retos_grafica_1.png")


def retos_por_mes(df):
    """Cuenta los retos que empiezan cada mes (incluye los meses sin retos, con 0)."""
    meses = df["fecha_inicio"].dropna().dt.to_period("M")
    por_mes = meses.value_counts().sort_index()
    if por_mes.empty:
        return por_mes
    rango = pd.period_range(por_mes.index.min(), por_mes.index.max(), freq="M")
    return por_mes.reindex(rango, fill_value=0)


def grafica_linea_mes(df):
    """Gráfica 2: línea con los retos que empiezan cada mes."""
    por_mes = retos_por_mes(df)
    por_mes.index = por_mes.index.astype(str)  # etiquetas tipo 2026-03
    plt.figure(figsize=(9, 5))
    por_mes.plot(kind="line", marker="o")
    plt.title("Retos que empiezan cada mes")
    plt.xlabel("Mes de inicio")
    plt.ylabel("Cantidad de retos")
    plt.xticks(range(len(por_mes)), por_mes.index, rotation=45)
    return guardar_grafica("retos_grafica_2.png")


def grafica_histograma_duracion(df):
    """Gráfica 3: histograma con la distribución de la duración de los retos."""
    plt.figure(figsize=(8, 5))
    df["duracion_dias"].plot(kind="hist", bins=20)
    plt.title("Distribución de la duración de los retos")
    plt.xlabel("Duración (días)")
    plt.ylabel("Cantidad de retos")
    return guardar_grafica("retos_grafica_3.png")


def contar_fechas_invertidas(df):
    """Cuenta los retos cuya fecha de fin es anterior a la de inicio (dato para el back)."""
    if {"fecha_inicio", "fecha_fin"} <= set(df.columns):
        return int((df["fecha_fin"] < df["fecha_inicio"]).sum())
    return int((df["duracion_dias"] < 0).sum())


def conclusion_mes(df):
    """Dice en qué mes empiezan más retos y por qué puede ser."""
    por_mes = retos_por_mes(df)
    if por_mes.empty:
        return "1. Mes con más retos: no hay fechas de inicio válidas para calcularlo."
    mes = por_mes.idxmax()
    cantidad = int(por_mes.max())
    total = int(por_mes.sum())
    pct = cantidad / total * 100
    promedio = total / len(por_mes)
    texto = (f"1. Mes con más retos: {MESES[mes.month - 1]} de {mes.year} con {cantidad} "
             f"de {total} retos ({pct:.0f}%; el promedio por mes es {promedio:.1f}). ")
    if cantidad >= 1.5 * promedio:
        texto += ("Los retos se concentran en ese mes; puede deberse a que es un arranque "
                  "de trimestre o de ciclo de planeación en las empresas, o a que hay campañas "
                  "que abren varios retos a la vez (es una hipótesis, los datos no lo confirman).")
    else:
        texto += ("La diferencia con los demás meses es pequeña: el reparto es bastante parejo. "
                  "Si los datos son simulados, esto es esperable porque las fechas se generan "
                  "al azar dentro de un rango.")
    return texto


def conclusion_duracion(df):
    """Calcula la duración promedio por estado (solo con duraciones válidas, >= 0)."""
    validos = df[df["duracion_dias"] >= 0]
    promedios = validos.groupby("estado")["duracion_dias"].mean().round(1)
    if promedios.empty:
        return "2. Duración promedio por estado: no hay duraciones válidas para calcularla."
    lineas = [f"   - {estado}: {valor} días" for estado, valor in promedios.items()]
    general = validos["duracion_dias"].mean()
    return ("2. Duración promedio de un reto según su estado "
            f"(sin contar las fechas invertidas; promedio general {general:.1f} días):\n"
            + "\n".join(lineas))


def conclusion_fechas(df):
    """Informa cuántos retos tienen la fecha de fin antes que la de inicio."""
    n = contar_fechas_invertidas(df)
    return (f"3. Retos con la fecha de fin anterior a la de inicio: {n} de {len(df)}. "
            "Es un error lógico de origen: hay que avisárselo al back para que valide las fechas.")


def main():
    """Lee el archivo, crea las gráficas e imprime rutas y conclusiones."""
    try:
        df = leer_datos(RUTA_ENTRADA)
    except (FileNotFoundError, ValueError) as error:
        print(f"No se pudo leer el archivo: {error}")
        sys.exit(1)

    print("Gráficas guardadas:")
    for ruta in (grafica_barras_estado(df), grafica_linea_mes(df), grafica_histograma_duracion(df)):
        print(f"  {ruta}")

    print("\nConclusiones:")
    print(conclusion_mes(df))
    print(conclusion_duracion(df))
    print(conclusion_fechas(df))


if __name__ == "__main__":
    main()