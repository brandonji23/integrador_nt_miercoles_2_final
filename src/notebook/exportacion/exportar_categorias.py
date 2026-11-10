import os
import sys
from importlib import import_module
from pathlib import Path

# Permite importar la carpeta hermana "simulacion" aunque este archivo
# se ejecute solo (python src/notebook/exportacion/exportar_categorias.py)
CARPETA_NOTEBOOK = Path(__file__).resolve().parents[1]
if str(CARPETA_NOTEBOOK) not in sys.path:
    sys.path.insert(0, str(CARPETA_NOTEBOOK))

generar_categorias = import_module("simulacion.simular_categorias").generar_categorias

# Raíz del proyecto: integrador_kevin_moncada/data/crudo
CARPETA = str(Path(__file__).resolve().parents[3] / "data" / "crudo")


def exportar_categorias(df=None):
    if df is None:
        df = generar_categorias()

    os.makedirs(CARPETA, exist_ok=True)

    ruta_csv = f"{CARPETA}/categorias_sucio.csv"
    ruta_xlsx = f"{CARPETA}/categorias_sucio.xlsx"
    ruta_json = f"{CARPETA}/categorias_sucio.json"

    df.to_csv(ruta_csv, index=False, encoding="utf-8")
    df.to_excel(ruta_xlsx, index=False, sheet_name="categorias")
    df.to_json(ruta_json, orient="records", force_ascii=False, indent=2)

    for ruta in (ruta_csv, ruta_xlsx, ruta_json):
        print(f"{ruta} -> {df.shape}")

    return [ruta_csv, ruta_xlsx, ruta_json]


if __name__ == "__main__":
    exportar_categorias()