import os

from simulacion.simular_prioridades import generar_prioridades  

CARPETA = os.path.join("data", "crudo")


def exportar(df):
    os.makedirs(CARPETA, exist_ok=True)

    ruta_csv = os.path.join(CARPETA, "prioridades_sucio.csv")
    ruta_xlsx = os.path.join(CARPETA, "prioridades_sucio.xlsx")
    ruta_json = os.path.join(CARPETA, "prioridades_sucio.json")

    df.to_csv(ruta_csv, index=False, encoding="utf-8")
    df.to_excel(ruta_xlsx, index=False, sheet_name="prioridades")
    df.to_json(ruta_json, orient="records", force_ascii=False, indent=2)

    for ruta in (ruta_csv, ruta_xlsx, ruta_json):
        print(f"{ruta} -> {df.shape}")


if __name__ == "__main__":
    exportar(generar_prioridades())