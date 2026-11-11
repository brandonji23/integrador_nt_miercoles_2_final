"""Limpieza de la tabla registros (HU L01 - Kaizen).

Ubicación: src/notebook/limpieza/limpiar_registros.py
Lee:       data/crudo/registros_sucio.csv
Guarda:    data/limpio/registros_limpio.csv

Se puede ejecutar de dos formas (desde cualquier carpeta):
    python src/notebook/limpieza/limpiar_registros.py
    o importando limpiar_registros() desde main.py
"""
from pathlib import Path

import pandas as pd

# limpieza -> notebook -> src -> raíz del proyecto
RAIZ = Path(__file__).resolve().parents[3]
RUTA_ENTRADA = RAIZ / "data" / "crudo" / "registros_sucio.csv"
RUTA_SALIDA = RAIZ / "data" / "limpio" / "registros_limpio.csv"

# Columnas que no pueden quedar con nulos después de limpiar.
COLUMNAS_OBLIGATORIAS = ["id_usuario", "id_reto", "fecha_registro", "estado"]


def imprimir_diagnostico(df, titulo):
    """Imprime shape, info, nulos por columna y duplicados exactos."""
    print(f"\n===== {titulo} =====")
    print("shape:", df.shape)
    print("\ninfo:")
    df.info()
    print("\nnulos por columna:")
    print(df.isna().sum())
    print("\nduplicados exactos:", df.duplicated().sum())


def convertir_fecha(df):
    """Convierte fecha_registro a datetime aunque venga en dos formatos.

    Las fechas ISO (AAAA-MM-DD) se leen primero con su formato exacto, porque
    dayfirst=True las interpretaría al revés (2024-04-10 -> 2024-10-04).
    El resto (DD/MM/AAAA) se lee con format="mixed" y dayfirst=True.
    Lo que no se pueda interpretar queda como NaT (errors="coerce").
    """
    texto = df["fecha_registro"].astype("string").str.strip()
    fechas = pd.to_datetime(texto, format="%Y-%m-%d", errors="coerce")
    pendientes = fechas.isna() & texto.notna()
    fechas[pendientes] = pd.to_datetime(
        texto[pendientes], format="mixed", dayfirst=True, errors="coerce"
    )
    df["fecha_registro"] = fechas
    return df


def unificar_estado(df):
    """Quita espacios sobrantes, pasa a mayúsculas y cambia espacios por guion bajo."""
    df["estado"] = (
        df["estado"].str.strip().str.upper().str.replace(r"\s+", "_", regex=True)
    )
    return df


def rellenar_observaciones(df):
    """Rellena las observaciones vacías con 'Sin observacion'."""
    df["observacion"] = df["observacion"].fillna("Sin observacion")
    return df


def quitar_participaciones_repetidas(df):
    """Imprime cuántas participaciones están repetidas y deja la primera de cada par."""
    repetidos = df[df.duplicated(subset=["id_usuario", "id_reto"], keep=False)]
    print(f"\nFilas involucradas en participaciones repetidas: {len(repetidos)}")
    return df.drop_duplicates(subset=["id_usuario", "id_reto"], keep="first")


def quitar_nulos_obligatorios(df):
    """Elimina filas con nulos en columnas obligatorias (p. ej. fechas inválidas)."""
    antes = len(df)
    df = df.dropna(subset=COLUMNAS_OBLIGATORIAS)
    print(f"Filas eliminadas por nulos en columnas obligatorias: {antes - len(df)}")
    return df


def crear_columna_mes(df):
    """Crea la columna 'mes' (periodo mensual) para agrupar después."""
    df["mes"] = df["fecha_registro"].dt.to_period("M")
    return df


def verificar_resultado(df):
    """Comprueba que no queden nulos obligatorios ni duplicados exactos."""
    assert df[COLUMNAS_OBLIGATORIAS].isna().sum().sum() == 0, "Quedan nulos obligatorios"
    assert df.duplicated().sum() == 0, "Quedan duplicados exactos"
    print("\nVerificación OK: sin nulos obligatorios ni duplicados exactos.")


def limpiar_registros(ruta_entrada=RUTA_ENTRADA, ruta_salida=RUTA_SALIDA):
    """Flujo completo: leer, diagnosticar, limpiar, diagnosticar y guardar."""
    df = pd.read_csv(ruta_entrada)
    filas_iniciales = len(df)
    imprimir_diagnostico(df, "DIAGNÓSTICO ANTES DE LIMPIAR")

    df = df.drop_duplicates()
    df = convertir_fecha(df)
    df = unificar_estado(df)
    df = rellenar_observaciones(df)
    df = quitar_participaciones_repetidas(df)
    df = quitar_nulos_obligatorios(df)
    df = crear_columna_mes(df)

    imprimir_diagnostico(df, "DIAGNÓSTICO DESPUÉS DE LIMPIAR")
    print(f"\nFilas eliminadas en total: {filas_iniciales - len(df)}")
    verificar_resultado(df)

    Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta_salida, index=False, encoding="utf-8")
    print(f"Archivo guardado en: {ruta_salida}")
    return df


if __name__ == "__main__":
    limpiar_registros()
    