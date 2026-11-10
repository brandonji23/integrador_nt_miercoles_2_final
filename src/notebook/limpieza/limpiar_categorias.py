import os
from pathlib import Path

import pandas as pd

# Raíz del proyecto: integrador_kevin_moncada/
RAIZ = Path(__file__).resolve().parents[3]
CARPETA_CRUDO = RAIZ / "data" / "crudo"
CARPETA_LIMPIO = RAIZ / "data" / "limpio"

RUTA_CSV = CARPETA_CRUDO / "categorias_sucio.csv"
RUTA_XLSX = CARPETA_CRUDO / "categorias_sucio.xlsx"
RUTA_JSON = CARPETA_CRUDO / "categorias_sucio.json"

OBLIGATORIAS = ["id", "nombre", "descripcion", "area_responsable"]


def leer_archivos():
    """Lee los tres archivos crudos y devuelve un diccionario {formato: DataFrame}."""
    return {
        "csv": pd.read_csv(RUTA_CSV),
        "xlsx": pd.read_excel(RUTA_XLSX, sheet_name="categorias"),
        "json": pd.read_json(RUTA_JSON, orient="records"),
    }


def imprimir_diagnostico(df, titulo):
    print(f"\n=== {titulo} ===")
    print("df.shape:", df.shape)
    print("\ndf.info():")
    df.info()
    print("\ndf.isna().sum():")
    print(df.isna().sum())
    print("\ndf.duplicated().sum():", df.duplicated().sum())


def limpiar(df):
    df = df.copy()

    # 1. Duplicados exactos
    df = df.drop_duplicates()

    # 2. Unificar nombre: espacios y mayúscula inicial
    df["nombre"] = df["nombre"].str.strip().str.title()

    # 3. Quitar tildes ("logística" y "logistica" quedan iguales)
    df["nombre"] = (
        df["nombre"].str.normalize("NFKD")
        .str.encode("ascii", "ignore").str.decode("utf-8")
    )

    # 4. Rellenar nulos
    df["descripcion"] = df["descripcion"].fillna("Sin descripcion")
    df["area_responsable"] = df["area_responsable"].fillna("Sin asignar")

    # 5. Largo de la descripción
    df["largo_desc"] = df["descripcion"].str.len()

    return df


def verificar(df):
    nulos = int(df[OBLIGATORIAS].isna().sum().sum())
    duplicados = int(df.duplicated().sum())
    print("\n=== Verificación ===")
    print(f"Nulos en columnas obligatorias: {nulos} -> {'PASA' if nulos == 0 else 'FALLA'}")
    print(f"Duplicados exactos: {duplicados} -> {'PASA' if duplicados == 0 else 'FALLA'}")
    return nulos == 0 and duplicados == 0


def limpiar_y_guardar(df_sucio, formato):
    print("\n" + "#" * 60)
    print(f"LIMPIEZA DEL ARCHIVO {formato.upper()}")
    print("#" * 60)

    filas_antes = len(df_sucio)
    imprimir_diagnostico(df_sucio, f"ANTES ({formato})")

    df = limpiar(df_sucio)

    imprimir_diagnostico(df, f"DESPUÉS ({formato})")
    verificar(df)

    os.makedirs(CARPETA_LIMPIO, exist_ok=True)
    if formato == "csv":
        ruta = CARPETA_LIMPIO / "categorias_limpio.csv"
        df.to_csv(ruta, index=False, encoding="utf-8")
    elif formato == "xlsx":
        ruta = CARPETA_LIMPIO / "categorias_limpio.xlsx"
        df.to_excel(ruta, index=False, sheet_name="categorias")
    else:
        ruta = CARPETA_LIMPIO / "categorias_limpio.json"
        df.to_json(ruta, orient="records", force_ascii=False, indent=2)

    print("\n=== Resultado ===")
    print(f"Filas antes: {filas_antes}")
    print(f"Filas después: {len(df)}")
    print(f"Filas eliminadas: {filas_antes - len(df)}")
    print(f"Guardado: {ruta} {df.shape}")

    return df


if __name__ == "__main__":
    crudos = leer_archivos()
    limpios = {f: limpiar_y_guardar(d, f) for f, d in crudos.items()}

    # Catálogo real (una fila por categoría), desde el CSV limpio
    catalogo = limpios["csv"].drop_duplicates(subset=["nombre"])
    ruta_catalogo = CARPETA_LIMPIO / "categorias_catalogo.csv"
    catalogo.to_csv(ruta_catalogo, index=False, encoding="utf-8")
    print(f"\nCatálogo: {ruta_catalogo} {catalogo.shape}")

    # Los tres formatos deben dar el mismo resultado
    iguales = (
        limpios["csv"].reset_index(drop=True).equals(limpios["xlsx"].reset_index(drop=True))
        and limpios["csv"].reset_index(drop=True).equals(limpios["json"].reset_index(drop=True))
    )
    print(f"Los 3 archivos limpios coinciden: {'PASA' if iguales else 'FALLA'}")