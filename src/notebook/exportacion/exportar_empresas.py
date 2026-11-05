import os
import sys

# Permite importar la carpeta "simulacion" aunque corras este archivo directo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulacion.simular_empresas import generar_empresas

# Raíz del proyecto: exportacion -> notebook -> src -> raíz
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def exportar_empresas(df=None):
    carpeta = os.path.join(RAIZ, "data", "crudo")
    os.makedirs(carpeta, exist_ok=True)

    if df is None:
        df = generar_empresas()

    base = os.path.join(carpeta, "empresas_sucio")
    df.to_csv(f"{base}.csv", index=False, encoding="utf-8")
    df.to_excel(f"{base}.xlsx", index=False, sheet_name="empresas")
    df.to_json(f"{base}.json", orient="records", force_ascii=False, indent=2)

    for ext in ("csv", "xlsx", "json"):
        print(f"{base}.{ext} -> {df.shape}")
    return df


if __name__ == "__main__":
    exportar_empresas()