"""Limpia la tabla prioridades siguiendo los criterios de la HU L01 de Kaizen.

Lee data/crudo/prioridades_sucio.csv y guarda data/limpio/prioridades_limpio.csv.
"""
from pathlib import Path

import pandas as pd

# Catalogo real del proyecto: nombre de la prioridad -> nivel
NIVELES = {"Urgente": 1, "Alta": 2, "Media": 3, "Baja": 4, "Planificada": 5}

RUTA_ENTRADA = Path("data/crudo/prioridades_sucio.csv")
CARPETA_SALIDA = Path("data/limpio")
COLUMNAS_OBLIGATORIAS = ["nombre", "nivel", "dias_max_respuesta"]


def diagnostico(df, titulo, completo=True):
    """Imprime el diagnostico: shape, nulos y, si completo, info y duplicados."""
    print(f"\n=== {titulo} ===")
    print("shape:", df.shape)
    if completo:
        print("\ninfo:")
        df.info()
    print("\nnulos por columna:")
    print(df.isna().sum())
    if completo:
        print("\nduplicados exactos:", df.duplicated().sum())


def convertir_nivel(df):
    """Convierte nivel a numero (uno..cinco -> 1..5) y rellena vacios segun el nombre."""
    nivel = df["nivel"].astype("string").str.strip().str.lower()
    nivel = nivel.replace({"uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5})
    df["nivel"] = pd.to_numeric(nivel, errors="coerce")
    df["nivel"] = df["nivel"].fillna(df["nombre"].map(NIVELES))
    return df


def limpiar_dias(df):
    """Convierte dias_max_respuesta a numero, anula valores > 60 y rellena con la mediana."""
    df["dias_max_respuesta"] = pd.to_numeric(df["dias_max_respuesta"], errors="coerce")
    df.loc[df["dias_max_respuesta"] > 60, "dias_max_respuesta"] = None
    df["dias_max_respuesta"] = df["dias_max_respuesta"].fillna(df["dias_max_respuesta"].median())
    return df


def limpiar(df):
    """Aplica todos los criterios de limpieza y devuelve el DataFrame limpio."""
    df = df.drop_duplicates()
    df["nombre"] = df["nombre"].str.strip().str.capitalize()
    df = convertir_nivel(df)
    df = limpiar_dias(df)
    # Al unificar nombres pueden aparecer nuevos duplicados exactos: se quitan tambien
    return df.drop_duplicates().reset_index(drop=True)


def guardar(df):
    """Guarda el CSV limpio y el catalogo real (un registro por nombre)."""
    CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)
    ruta = CARPETA_SALIDA / "prioridades_limpio.csv"
    df.to_csv(ruta, index=False, encoding="utf-8")
    catalogo = df.drop_duplicates(subset=["nombre"])
    ruta_cat = CARPETA_SALIDA / "prioridades_catalogo.csv"
    catalogo.to_csv(ruta_cat, index=False, encoding="utf-8")
    print(f"\nGuardado: {ruta} ({len(df)} filas)")
    print(f"Guardado: {ruta_cat} ({len(catalogo)} filas)")


def main():
    """Lee el CSV crudo, limpia, muestra diagnosticos y guarda."""
    df = pd.read_csv(RUTA_ENTRADA)
    filas_inicio = len(df)

    diagnostico(df, "DIAGNOSTICO ANTES")
    df = limpiar(df)
    diagnostico(df, "DIAGNOSTICO DESPUES", completo=False)

    print("\nduplicados exactos:", df.duplicated().sum())
    print(f"Filas eliminadas: {filas_inicio - len(df)}")
    if df[COLUMNAS_OBLIGATORIAS].isna().any().any():
        print("AVISO: quedan nulos en columnas obligatorias")
    guardar(df)


if __name__ == "__main__":
    main()