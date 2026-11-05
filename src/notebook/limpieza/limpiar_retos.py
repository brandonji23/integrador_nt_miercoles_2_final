"""Limpia la tabla retos del proyecto integrador (HU L01 de Kaizen).

Uso (desde cualquier carpeta):
    python src/notebook/limpieza/limpiar_retos.py

Lee data/crudo/retos_sucio.csv, imprime el diagnostico, corrige los errores que
piden los criterios, imprime el diagnostico otra vez y guarda
data/limpio/retos_limpio.csv.
"""

import sys
from pathlib import Path

import pandas as pd

# Raiz del proyecto: limpieza -> notebook -> src -> raiz
RAIZ = Path(__file__).resolve().parents[3]

# Rutas de entrada y salida (las pide el criterio de la HU)
RUTA_ENTRADA = RAIZ / "data" / "crudo" / "retos_sucio.csv"
RUTA_SALIDA = RAIZ / "data" / "limpio" / "retos_limpio.csv"

# Columnas que el script necesita para limpiar
COLUMNAS_NECESARIAS = ["estado", "descripcion", "fecha_inicio", "fecha_fin"]

# Columnas obligatorias: despues de limpiar no puede quedar ningun nulo en ellas.
# La descripcion no entra porque se rellena con "Sin descripcion".
COLUMNAS_OBLIGATORIAS = ["id", "nombre", "estado", "fecha_inicio", "fecha_fin"]


def leer_datos(ruta):
    """Lee el CSV sucio con pd.read_csv() y devuelve el DataFrame."""
    df = pd.read_csv(ruta)
    faltan = [c for c in COLUMNAS_NECESARIAS if c not in df.columns]
    if faltan:
        sys.exit(f"Error: faltan las columnas {faltan} en {ruta}")
    return df


def imprimir_diagnostico(df, titulo):
    """Imprime shape, info, nulos y duplicados exactos del DataFrame."""
    print(f"\n===== {titulo} =====")
    print(f"df.shape: {df.shape}")
    print("\ndf.info():")
    df.info()
    print("\ndf.isna().sum():")
    print(df.isna().sum())
    print(f"\ndf.duplicated().sum(): {df.duplicated().sum()}")


def quitar_duplicados(df):
    """Quita las filas duplicadas exactas con df.drop_duplicates()."""
    return df.drop_duplicates()


def convertir_fechas(df):
    """Convierte fecha_inicio y fecha_fin a datetime, aunque vengan en dos formatos.

    Lo que no se pueda convertir queda como NaT (errors="coerce").
    """
    for columna in ["fecha_inicio", "fecha_fin"]:
        texto = df[columna]
        # Primero el formato ISO (AAAA-MM-DD): con dayfirst=True pandas lo
        # confunde y voltea dia y mes (2026-01-10 saldria como 2026-10-01)
        fechas = pd.to_datetime(texto, format="ISO8601", errors="coerce")
        # Lo que no es ISO (por ejemplo DD/MM/AAAA) se lee con el dia primero
        resto = pd.to_datetime(
            texto[fechas.isna()], format="mixed", dayfirst=True, errors="coerce"
        )
        df[columna] = fechas.fillna(resto)
    return df


def unificar_estado(df):
    """Unifica el estado: sin espacios sobrantes, en mayusculas y con guion bajo."""
    # \s+ junta varios espacios seguidos en un solo guion bajo (EN__PROGRESO no)
    df["estado"] = (
        df["estado"].str.strip().str.upper().str.replace(r"\s+", "_", regex=True)
    )
    return df


def rellenar_descripciones(df):
    """Rellena las descripciones vacias con "Sin descripcion"."""
    # Una descripcion que solo tiene espacios tambien cuenta como vacia
    df["descripcion"] = df["descripcion"].replace(r"^\s*$", pd.NA, regex=True)
    df["descripcion"] = df["descripcion"].fillna("Sin descripcion")
    return df


def crear_duracion(df):
    """Crea duracion_dias y marca en fecha_valida las fechas coherentes (fin >= inicio)."""
    df["duracion_dias"] = (df["fecha_fin"] - df["fecha_inicio"]).dt.days.astype("Int64")
    # Si falta una fecha no se puede calcular la duracion: no es valida
    df["fecha_valida"] = (df["duracion_dias"] >= 0).fillna(False).astype(bool)
    return df


def quitar_nulos_obligatorios(df):
    """Quita las filas con nulos en las columnas obligatorias.

    Pasa, por ejemplo, con una fecha que no se pudo convertir. No hay una regla
    para rellenarlas, asi que la fila no se puede usar.
    """
    columnas = [c for c in COLUMNAS_OBLIGATORIAS if c in df.columns]
    return df.dropna(subset=columnas)


def guardar(df, ruta):
    """Guarda el DataFrame limpio en CSV (sin indice, en UTF-8)."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False, encoding="utf-8")


def main():
    """Ejecuta todo el proceso: leer, diagnosticar, limpiar, diagnosticar y guardar."""
    df = leer_datos(RUTA_ENTRADA)
    filas_antes = df.shape[0]
    nulos_antes = df.isna().sum()

    imprimir_diagnostico(df, "DIAGNOSTICO ANTES DE LIMPIAR")

    # --- Limpieza ---
    df = quitar_duplicados(df)
    df = convertir_fechas(df)
    df = unificar_estado(df)
    df = rellenar_descripciones(df)
    df = crear_duracion(df)
    df = quitar_nulos_obligatorios(df)
    # Unificar el estado puede dejar filas iguales: se quitan otra vez
    df = quitar_duplicados(df)

    imprimir_diagnostico(df, "DIAGNOSTICO DESPUES DE LIMPIAR")

    # --- Resumen ---
    nulos_despues = df.isna().sum()
    # Las columnas nuevas (duracion_dias, fecha_valida) no existian: cuentan 0 nulos antes
    nulos_antes = nulos_antes.reindex(nulos_despues.index, fill_value=0)
    comparacion = pd.DataFrame(
        {
            "antes": nulos_antes,
            "despues": nulos_despues,
            "corregidos": nulos_antes - nulos_despues,
        }
    )
    print("\n===== NULOS ANTES Y DESPUES =====")
    print(comparacion)

    incoherentes = int((~df["fecha_valida"]).sum())
    print(f"\nFechas incoherentes (fin antes que inicio): {incoherentes}")
    print(f"Filas antes: {filas_antes} | filas despues: {df.shape[0]}")
    print(f"Filas eliminadas: {filas_antes - df.shape[0]}")

    guardar(df, RUTA_SALIDA)
    print(f"\nArchivo limpio guardado en: {RUTA_SALIDA}")


if __name__ == "__main__":
    main()