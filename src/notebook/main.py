from simulacion.simular_prioridades import generar_prioridades
from exportacion.exportar_prioridades import exportar
from limpieza.limpiar_prioridades import main as limpiar_datos
from consultas.consultas_prioridades import main as consultar_datos
from graficacion.reporte_prioridades import main as graficar_datos
from simulacion.simular_empresas import generar_empresas
from exportacion.exportar_empresas import exportar_empresas
from limpieza.limpiar_empresas import main as limpiar_empresas
from consultas.consultas_empresas import main as consultar_empresas
from graficacion.reporte_empresas import main as graficar_empresas


import sys
from importlib import import_module
from pathlib import Path
import pandas as pd

# Para que Python encuentre las carpetas simulacion/, exportacion/, limpieza/, consultas/ y graficacion/
CARPETA_NOTEBOOK = Path(__file__).resolve().parent
if str(CARPETA_NOTEBOOK) not in sys.path:
    sys.path.insert(0, str(CARPETA_NOTEBOOK))

simulacion = import_module("simulacion.simular_categorias")
exportacion = import_module("exportacion.exportar_categorias")
limpieza = import_module("limpieza.limpiar_categorias")
consultas = import_module("consultas.consultas_categorias")
graficacion = import_module("graficacion.reporte_categorias")


def probar_simulacion():
    print("=" * 60)
    print("PRUEBA 1: SIMULACIÓN (HU F01)")
    print("=" * 60)

    df = simulacion.generar_categorias()

    print("shape:", df.shape)
    print(df.head())
    print("\nNulos por columna:")
    print(df.isna().sum())

    duplicados = df.duplicated().sum()
    nombres_limpios = (
        df["nombre"].str.strip().str.lower().map(simulacion._sin_tilde).nunique()
    )

    print("\nVerificaciones:")
    print(f"  250 filas ............ {'PASA' if df.shape[0] == 250 else 'FALLA'}")
    print(f"  4 columnas ........... {'PASA' if df.shape[1] == 4 else 'FALLA'}"
          f" {list(df.columns)}")
    print(f"  nulos descripcion .... {df['descripcion'].isna().sum()} (esperado ~15%)")
    print(f"  nulos area ........... {df['area_responsable'].isna().sum()} (esperado ~10%)")
    print(f"  duplicados exactos ... {duplicados} (esperado 20 = 8%)")
    print(f"  nombres sin variantes  {nombres_limpios} "
          f"{'PASA' if nombres_limpios == 10 else 'FALLA'} (esperado 10)")
    print(f"  variantes de escritura {df['nombre'].nunique()} nombres distintos (> 10 = sucio)")

    return df


def probar_exportacion(df):
    print("\n" + "=" * 60)
    print("PRUEBA 2: EXPORTACIÓN (HU X01)")
    print("=" * 60)

    rutas = exportacion.exportar_categorias(df)
    ruta_csv, ruta_xlsx, ruta_json = rutas

    print("\nLectura de vuelta de los archivos:")
    csv_df = pd.read_csv(ruta_csv)
    xlsx_df = pd.read_excel(ruta_xlsx, sheet_name="categorias")
    json_df = pd.read_json(ruta_json, orient="records")

    for nombre, d in (("csv", csv_df), ("xlsx", xlsx_df), ("json", json_df)):
        estado = "PASA" if d.shape == df.shape else "FALLA"
        print(f"  {nombre:5} -> {d.shape} {estado}")


def probar_limpieza(df_sucio):
    print("\n" + "=" * 60)
    print("PRUEBA 3: LIMPIEZA (HU L01)")
    print("=" * 60)

    # Lee los 3 archivos que dejó la exportación en data/crudo
    crudos = limpieza.leer_archivos()
    limpios = {f: limpieza.limpiar_y_guardar(d, f) for f, d in crudos.items()}

    # Catálogo real (una fila por categoría)
    catalogo = limpios["csv"].drop_duplicates(subset=["nombre"])
    ruta_catalogo = limpieza.CARPETA_LIMPIO / "categorias_catalogo.csv"
    catalogo.to_csv(ruta_catalogo, index=False, encoding="utf-8")

    base = limpios["csv"].reset_index(drop=True)
    iguales = all(
        base.equals(limpios[f].reset_index(drop=True)) for f in ("xlsx", "json")
    )
    esperadas = len(df_sucio) - df_sucio.duplicated().sum()

    print("\nVerificaciones finales:")
    print(f"  filas tras limpiar ... {len(base)} "
          f"{'PASA' if len(base) == esperadas else 'FALLA'} (esperado {esperadas})")
    print(f"  catálogo ............. {len(catalogo)} "
          f"{'PASA' if len(catalogo) == 10 else 'FALLA'} (esperado 10 categorías)")
    print(f"  columna largo_desc ... {'PASA' if 'largo_desc' in base.columns else 'FALLA'}")
    print(f"  3 formatos coinciden . {'PASA' if iguales else 'FALLA'}")
    print(f"  catálogo guardado en . {ruta_catalogo}")


def probar_consultas():
    print("\n" + "=" * 60)
    print("PRUEBA 4: CONSULTAS (HU Q01)")
    print("=" * 60)

    # Lee data/limpio/categorias_limpio.csv que dejó la limpieza
    resultados = consultas.ejecutar_consultas()

    print("\nVerificaciones finales:")
    print(f"  5 consultas ejecutadas ... {'PASA' if len(resultados) == 5 else 'FALLA'}")

    for n in range(1, 6):
        ruta = consultas.CARPETA_LIMPIO / f"categorias_consulta_{n}.csv"
        print(f"  categorias_consulta_{n}.csv .. {'PASA' if ruta.exists() else 'FALLA'}")

    conteo = resultados[0]
    print(f"  consulta 1: categorías ... {len(conteo)} "
          f"{'PASA' if len(conteo) == 10 else 'FALLA'} (esperado 10)")


def probar_graficacion():
    print("\n" + "=" * 60)
    print("PRUEBA 5: GRAFICACIÓN (HU G01)")
    print("=" * 60)

    # Lee data/limpio/categorias_limpio.csv y guarda las imágenes en reportes/
    rutas = graficacion.ejecutar_reporte()

    print("\nVerificaciones finales:")
    print(f"  3 gráficas generadas ..... {'PASA' if len(rutas) == 3 else 'FALLA'}")
    for n, ruta in enumerate(rutas, start=1):
        print(f"  categorias_grafica_{n}.png .. {'PASA' if ruta.exists() else 'FALLA'}")


if __name__ == "__main__":
    tabla = probar_simulacion()
    probar_exportacion(tabla)
    probar_limpieza(tabla)
    probar_consultas()
    probar_graficacion()
    

def main():
    print("=== HU F01: Simulación empresas ===")
    df_empresa = generar_empresas(300)
    print(df_empresa.shape)
    print(df_empresa.head())
    print(df_empresa.isna().sum())

    print("\n=== HU X01: Exportación empresas ===")
    exportar_empresas(df_empresa)

    print("\n=== HU L01: Limpieza empresas ===")
    limpiar_empresas()

    print("\n=== HU Q01: Consultas empresas ===")
    consultar_empresas()

    print("\n=== HU G01: Gráficas empresas===")
    graficar_empresas()

    # 1. Simulación (HU F01)
    df = generar_prioridades()
    print("=== SIMULACIÓN prioridades ===")
    print(df.shape)
    print(df.head(10))
    print("\nNulos por columna:")
    print(df.isna().sum())

    # 2. Exportación (HU X01)
    print("\n=== EXPORTACIÓN prioridades ===")
    exportar(df)

    print("\n=== LIMPIEZA prioridades ===")
    limpiar_datos()

    print("\n=== CONSULTAS prioridades ===")
    consultar_datos()

    print("\n=== GRÁFICAS prioridades ===")
    graficar_datos()


if __name__ == "__main__":
    main()