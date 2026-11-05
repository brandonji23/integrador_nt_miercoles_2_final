import os
import sys
from pathlib import Path
from importlib import import_module

AQUI = Path(__file__).resolve().parent

# simular_retos.py vive en la carpeta hermana "simulacion"
sys.path.insert(0, str(AQUI.parent / "simulacion"))

# Importamos la funcion del script anterior, sin copiar el codigo de generacion
generar_retos = import_module("simular_retos").generar_retos

# Raiz del proyecto: exportacion -> notebook -> src -> raiz
RAIZ = AQUI.parents[2]
CARPETA = RAIZ / "data" / "crudo"


def exportar_retos():
    os.makedirs(CARPETA, exist_ok=True)

    df = generar_retos()

    ruta_csv = CARPETA / "retos_sucio.csv"
    ruta_xlsx = CARPETA / "retos_sucio.xlsx"
    ruta_json = CARPETA / "retos_sucio.json"

    df.to_csv(ruta_csv, index=False, encoding="utf-8")
    df.to_excel(ruta_xlsx, index=False, sheet_name="retos")
    # date_format="iso" evita que fecha_fin salga como numero en el JSON
    df.to_json(ruta_json, orient="records", force_ascii=False, indent=2, date_format="iso")

    for ruta in (ruta_csv, ruta_xlsx, ruta_json):
        print(ruta, df.shape)

    return [ruta_csv, ruta_xlsx, ruta_json]


if __name__ == "__main__":
    exportar_retos()