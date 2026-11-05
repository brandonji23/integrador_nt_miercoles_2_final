"""Reporte de graficas de la tabla empresas (HU G01).

Uso (desde la raiz del proyecto):
    python src/notebook/graficacion/reporte_empresas.py

Lee data/limpio/empresas_limpio.csv, genera tres graficas en reportes/ e
imprime la ruta de cada una junto con las conclusiones.
Opcional: python src/notebook/graficacion/reporte_empresas.py [ruta_csv_limpio]
"""
import os
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # backend sin ventana: el script nunca se queda esperando
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import pandas as pd

# Raiz del proyecto: graficacion -> notebook -> src -> raiz
RAIZ = Path(__file__).resolve().parents[3]
RUTA_LIMPIO = RAIZ / "data" / "limpio" / "empresas_limpio.csv"
CARPETA_SALIDA = str(RAIZ / "reportes")
PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
VALORES_ACTIVA = {"true": True, "1": True, "si": True, "sí": True, "activa": True,
                  "activo": True, "false": False, "0": False, "no": False,
                  "inactiva": False, "inactivo": False}


def cargar_datos(ruta_csv):
    """Lee el CSV, valida las columnas necesarias y normaliza 'activa' a texto."""
    if not os.path.isfile(ruta_csv):
        sys.exit(f"Error: no se encontro el archivo '{ruta_csv}'.")
    df = pd.read_csv(ruta_csv)
    df.columns = [c.strip().lower() for c in df.columns]
    for columna in ("sector", "activa"):
        if columna not in df.columns:
            sys.exit(f"Error: el CSV no tiene la columna obligatoria '{columna}'.")

    df["sector"] = df["sector"].fillna("Sin sector").astype(str).str.strip()
    booleanos = df["activa"].astype(str).str.strip().str.lower().map(VALORES_ACTIVA)
    if booleanos.isna().any():
        sys.exit("Error: la columna 'activa' tiene valores no reconocidos.")
    df["activa"] = booleanos.map({True: "Activa", False: "Inactiva"})
    return df


def guardar_grafica(nombre_archivo):
    """Ajusta el diseno, guarda la figura con dpi=120, la cierra e imprime la ruta."""
    plt.tight_layout()
    ruta = os.path.join(CARPETA_SALIDA, nombre_archivo)
    plt.savefig(ruta, dpi=120)
    plt.close()
    print(f"Grafica guardada: {ruta}")
    return ruta


def grafica_1_por_sector(df):
    """Grafica 1: barras con la cantidad de empresas por sector."""
    por_sector = df["sector"].value_counts()
    plt.figure(figsize=(9, 5))
    por_sector.plot(kind="bar", color="#3b7dd8")
    plt.title("Cantidad de empresas por sector")
    plt.xlabel("Sector")
    plt.ylabel("Numero de empresas")
    plt.xticks(rotation=45, ha="right")
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    return guardar_grafica("empresas_grafica_1.png")


def grafica_2_activas(df):
    """Grafica 2: torta de empresas activas frente a inactivas."""
    plt.figure(figsize=(6, 6))
    df["activa"].value_counts().plot(kind="pie", autopct="%1.1f%%",
                                     colors=["#4caf7a", "#e0634f"])
    plt.title("Empresas activas vs inactivas")
    plt.xlabel("Estado de la empresa")
    plt.ylabel("Proporcion de empresas")
    return guardar_grafica("empresas_grafica_2.png")


def grafica_3_apiladas(df):
    """Grafica 3: barras apiladas de activas e inactivas por sector."""
    tabla = pd.crosstab(df["sector"], df["activa"])
    plt.figure(figsize=(9, 5))
    tabla.plot(kind="bar", stacked=True, color=["#4caf7a", "#e0634f"],
               ax=plt.gca())
    plt.title("Empresas activas e inactivas por sector")
    plt.xlabel("Sector")
    plt.ylabel("Numero de empresas")
    plt.xticks(rotation=45, ha="right")
    plt.legend(title="Estado")
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    return guardar_grafica("empresas_grafica_3.png")


def contar_correos_invalidos(df):
    """Cuenta los correos vacios o con formato invalido; devuelve (invalidos, total)."""
    columnas = [c for c in df.columns if "correo" in c or "email" in c]
    if not columnas:
        return None, len(df)
    correos = df[columnas[0]].fillna("").astype(str).str.strip()
    invalidos = int((~correos.apply(lambda c: bool(PATRON_CORREO.match(c)))).sum())
    return invalidos, len(df)


def imprimir_conclusiones(df):
    """Calcula e imprime las conclusiones que piden los criterios de la HU."""
    por_sector = df["sector"].value_counts()
    maximo = por_sector.max()
    lideres = list(por_sector[por_sector == maximo].index)
    total = len(df)
    n_inactivas = int((df["activa"] == "Inactiva").sum())
    pct_inactivas = n_inactivas / total * 100
    invalidos, _ = contar_correos_invalidos(df)

    print("\n=== CONCLUSIONES ===")
    if len(lideres) == 1:
        print(f"1. El sector con mas empresas registradas es '{lideres[0]}' "
              f"con {maximo} de {total} empresas.")
    else:
        print(f"1. Hay empate: los sectores {', '.join(lideres)} tienen "
              f"{maximo} empresas cada uno (de {total}).")
    print(f"2. {pct_inactivas:.1f}% de las empresas esta inactivo "
          f"({n_inactivas} de {total}). Significa que esas empresas se "
          "registraron pero no operan en la plataforma: hay que reactivarlas "
          "o depurarlas, y no deben contarse como clientes vigentes.")
    if invalidos is None:
        print("3. El CSV no tiene columna de correo: no se pudo validar.")
    else:
        print(f"3. Aparecieron {invalidos} correos invalidos (vacios o sin "
              "formato usuario@dominio.ext). Hay que validarlos en el back "
              "porque la validacion del front se puede saltar (llamadas "
              "directas a la API, otros clientes); el back es la ultima "
              "barrera que protege la integridad de los datos y evita "
              "correos que rebotan.")


def main():
    """Punto de entrada: valida el argumento, genera graficas y conclusiones."""
    ruta_csv = sys.argv[1] if len(sys.argv) > 1 else RUTA_LIMPIO
    df = cargar_datos(ruta_csv)
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    grafica_1_por_sector(df)
    grafica_2_activas(df)
    grafica_3_apiladas(df)
    imprimir_conclusiones(df)


if __name__ == "__main__":
    main()