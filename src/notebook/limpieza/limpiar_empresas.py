"""Limpieza de la tabla empresas (HU L01 de Kaizen).

Uso (desde la raiz del proyecto):
    python src/notebook/limpieza/limpiar_empresas.py

Lee data/crudo/empresas_sucio.csv y guarda data/limpio/empresas_limpio.csv.
Opcional: python src/notebook/limpieza/limpiar_empresas.py [entrada] [salida]
"""
import sys
from pathlib import Path

import pandas as pd

# Columnas que no pueden quedar con nulos despues de limpiar.
# "contacto" no esta aqui porque se rellena con "Sin contacto".
OBLIGATORIAS = ["nit", "nombre", "sector", "activa"]

# Raiz del proyecto: limpieza -> notebook -> src -> raiz
RAIZ = Path(__file__).resolve().parents[3]
RUTA_ENTRADA_DEFECTO = RAIZ / "data" / "crudo" / "empresas_sucio.csv"
RUTA_SALIDA_DEFECTO = RAIZ / "data" / "limpio" / "empresas_limpio.csv"


def leer_csv(ruta):
    """Lee el CSV con pandas. Todo entra como texto para no perder ceros
    iniciales en nit/telefono; 'activa' llega como "True"/"False"."""
    return pd.read_csv(ruta, dtype=str)


def diagnostico(df, titulo):
    """Imprime shape, info, nulos por columna y cantidad de duplicados exactos."""
    print(f"\n===== {titulo} =====")
    print("shape:", df.shape)
    print("\ninfo:")
    df.info()
    print("\nnulos por columna:")
    print(df.isna().sum())
    print("\nduplicados exactos:", df.duplicated().sum())


def quitar_duplicados(df):
    """Elimina las filas que son duplicados exactos."""
    return df.drop_duplicates()


def limpiar_nombre(df):
    """Quita los espacios sobrantes al inicio y al final del nombre."""
    df["nombre"] = df["nombre"].str.strip()
    return df


def unificar_sector(df):
    """Unifica el sector: sin espacios sobrantes y con formato Titulo."""
    df["sector"] = df["sector"].str.strip().str.title()
    return df


def limpiar_nit(df):
    """Deja el NIT en un solo formato, sin puntos ni guiones."""
    df["nit"] = df["nit"].str.replace(r"[.\-]", "", regex=True)
    return df


def limpiar_telefono(df):
    """Deja el telefono solo con digitos."""
    df["telefono"] = df["telefono"].str.replace(r"\D", "", regex=True)
    return df


def convertir_activa(df):
    """Convierte 'activa' (texto) a booleano real. Los valores que no se
    reconocen quedan como nulo y luego se eliminan en quitar_nulos_obligatorios."""
    df["activa"] = (
        df["activa"].astype(str).str.strip().str.upper()
        .map({"TRUE": True, "SI": True, "1": True,
              "FALSE": False, "NO": False, "0": False})
    )
    return df


def rellenar_contacto(df):
    """Rellena los contactos vacios (nulos o solo espacios) con 'Sin contacto'."""
    df["contacto"] = df["contacto"].str.strip().replace("", pd.NA)
    df["contacto"] = df["contacto"].fillna("Sin contacto")
    return df


def marcar_correo_valido(df):
    """Crea la columna correo_valido: True si el correo contiene '@'."""
    df["correo_valido"] = df["correo"].str.contains("@", na=False)
    return df


def quitar_nulos_obligatorios(df):
    """Elimina las filas con nulos en las columnas obligatorias."""
    return df.dropna(subset=OBLIGATORIAS)


def main():
    """Ejecuta todo el proceso: leer, diagnosticar, limpiar y guardar."""
    ruta_entrada = Path(sys.argv[1]) if len(sys.argv) > 1 else RUTA_ENTRADA_DEFECTO
    ruta_salida = Path(sys.argv[2]) if len(sys.argv) > 2 else RUTA_SALIDA_DEFECTO

    df = leer_csv(ruta_entrada)
    filas_inicio = len(df)
    diagnostico(df, "DIAGNOSTICO ANTES DE LIMPIAR")

    df = quitar_duplicados(df)
    df = limpiar_nombre(df)
    df = unificar_sector(df)
    df = limpiar_nit(df)
    df = limpiar_telefono(df)
    df = convertir_activa(df)
    df = rellenar_contacto(df)
    df = marcar_correo_valido(df)
    df = quitar_nulos_obligatorios(df)
    # Al normalizar pueden aparecer duplicados nuevos: se quitan otra vez.
    df = quitar_duplicados(df)

    diagnostico(df, "DIAGNOSTICO DESPUES DE LIMPIAR")
    print(f"\nFilas eliminadas: {filas_inicio - len(df)} (de {filas_inicio} a {len(df)})")

    # Guardar el resultado
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta_salida, index=False, encoding="utf-8")
    print(f"\nArchivo limpio guardado en: {ruta_salida}")


if __name__ == "__main__":
    main()