"""HU X01: exporta la tabla registros sucia a CSV, XLSX y JSON."""
import os
import sys
from pathlib import Path

# Rutas basadas en la ubicación de este archivo:
# exportacion -> notebook -> src -> raíz del proyecto
RAIZ = Path(__file__).resolve().parents[3]
SRC_NOTEBOOK = Path(__file__).resolve().parents[1]
CARPETA_SALIDA = RAIZ / "data" / "crudo"

# Permite importar la carpeta "simulacion" (funciona con python main.py
# y también ejecutando este archivo directamente)
if str(SRC_NOTEBOOK) not in sys.path:
    sys.path.insert(0, str(SRC_NOTEBOOK))

from simulacion.simular_registros import generar_registros  # noqa: E402


def exportar_registros(df=None):
    """Exporta el DataFrame a data/crudo en tres formatos."""
    if df is None:
        df = generar_registros(n=800)

    os.makedirs(CARPETA_SALIDA, exist_ok=True)

    ruta_csv = CARPETA_SALIDA / "registros_sucio.csv"
    ruta_xlsx = CARPETA_SALIDA / "registros_sucio.xlsx"
    ruta_json = CARPETA_SALIDA / "registros_sucio.json"

    df.to_csv(ruta_csv, index=False, encoding="utf-8")
    df.to_excel(ruta_xlsx, index=False, sheet_name="registros")
    df.to_json(ruta_json, orient="records", force_ascii=False, indent=2)

    for ruta in (ruta_csv, ruta_xlsx, ruta_json):
        print(f"{ruta} -> {df.shape}")

    return df


if __name__ == "__main__":
    exportar_registros()