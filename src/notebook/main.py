
from simulacion.simular_retos import generar_retos
from exportacion.exportar_retos import exportar_retos
from limpieza.limpiar_retos import main as limpiar_retos, RUTA_SALIDA, COLUMNAS_OBLIGATORIAS
from consultas.consultar_retos import main as consultar_retos, CARPETA_LIMPIO
from graficacion.graficar_retos import main as graficar_retos, CARPETA as CARPETA_REPORTES
from simulacion.simular_registros import generar_registros
from exportacion.exportar_registros import exportar_registros
from limpieza.limpiar_registros import limpiar_registros
from consultas.consultas_registros import consultar_registros
from graficacion.graficar_registros import graficar_registros
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

COLUMNAS = [
    "id", "nombre", "descripcion", "fecha_inicio", "fecha_fin",
    "estado", "id_empresa", "id_categoria", "id_prioridad",
]


def comprobar(nombre, condicion):
    print(f"[{'PASA' if condicion else 'FALLA'}] {nombre}")


def probar_simulacion():
    print("\n=== HU F01: simulacion ===")
    df = generar_retos()

    print(df.shape)
    print(df.head())
    print(df.isna().sum())

    comprobar("devuelve un DataFrame", isinstance(df, pd.DataFrame))
    comprobar("tiene las 9 columnas de la HU", list(df.columns) == COLUMNAS)
    comprobar("525 filas (500 + 5% duplicados)", len(df) == 525)
    comprobar("25 duplicados exactos", df.duplicated().sum() == 25)
    comprobar("hay nulos en descripcion", df["descripcion"].isna().any())
    comprobar("hay nulos en fecha_fin", df["fecha_fin"].isna().any())
    comprobar(
        "fecha_inicio mezcla dos formatos",
        df["fecha_inicio"].astype(str).str.contains("/").any()
        and df["fecha_inicio"].astype(str).str.contains("-").any(),
    )
    comprobar(
        "estado tiene variantes sucias",
        df["estado"].isin(["en_curso", "EN CURSO", " Cerrado "]).any(),
    )
    comprobar("nombre tiene espacios sobrantes", (df["nombre"] != df["nombre"].str.strip()).any())

    return df


def probar_exportacion():
    print("\n=== HU X01: exportacion ===")
    rutas = exportar_retos()

    for ruta in rutas:
        comprobar(f"existe {ruta.name}", ruta.exists())

    csv, xlsx, json = rutas
    comprobar("CSV se lee con 525 filas", pd.read_csv(csv).shape == (525, 9))
    comprobar("XLSX se lee con 525 filas", pd.read_excel(xlsx, sheet_name="retos").shape == (525, 9))
    comprobar("JSON se lee con 525 filas", pd.read_json(json, orient="records").shape == (525, 9))


def probar_limpieza():
    print("\n=== HU L01: limpieza ===")
    # Lee data/crudo/retos_sucio.csv (lo que acaba de crear la exportacion)
    limpiar_retos()

    comprobar("existe retos_limpio.csv", RUTA_SALIDA.exists())

    limpio = pd.read_csv(RUTA_SALIDA)
    comprobar("tiene 11 columnas (9 + duracion_dias + fecha_valida)", limpio.shape[1] == 11)
    comprobar("se eliminaron filas (menos de 525)", limpio.shape[0] < 525)
    comprobar("no quedan duplicados exactos", limpio.duplicated().sum() == 0)
    comprobar("sin nulos en columnas obligatorias", limpio[COLUMNAS_OBLIGATORIAS].isna().sum().sum() == 0)
    comprobar("sin nulos en descripcion", limpio["descripcion"].isna().sum() == 0)
    comprobar(
        "estado sin espacios y en mayusculas",
        (limpio["estado"] == limpio["estado"].str.strip().str.upper()).all()
        and not limpio["estado"].str.contains(" ").any(),
    )
    comprobar(
        "fechas convertidas a formato AAAA-MM-DD",
        limpio["fecha_inicio"].str.match(r"^\d{4}-\d{2}-\d{2}$").all()
        and limpio["fecha_fin"].str.match(r"^\d{4}-\d{2}-\d{2}$").all(),
    )
    comprobar(
        "fecha_valida coincide con duracion_dias >= 0",
        (limpio["fecha_valida"] == (limpio["duracion_dias"] >= 0)).all(),
    )


def probar_consultas():
    print("\n=== HU Q01: consultas ===")
    # Lee data/limpio/retos_limpio.csv (lo que acaba de crear la limpieza)
    consultar_retos()

    total = len(pd.read_csv(RUTA_SALIDA))
    rutas = [CARPETA_LIMPIO / f"retos_consulta_{n}.csv" for n in range(1, 6)]

    for ruta in rutas:
        comprobar(f"existe {ruta.name}", ruta.exists())

    c1, c2, c3, c4, c5 = [pd.read_csv(r) for r in rutas]

    comprobar("consulta 1: solo retos EN_CURSO", (c1["estado"] == "EN_CURSO").all())
    comprobar("consulta 2: 10 retos ordenados de mayor a menor duracion",
              len(c2) == 10 and c2["duracion_dias"].is_monotonic_decreasing)
    comprobar("consulta 3: los conteos por estado suman todas las filas", c3["cantidad"].sum() == total)
    comprobar("consulta 4: groupby por estado cuenta todas las filas", c4["count"].sum() == total)
    comprobar("consulta 4: tiene count, mean, min y max",
              {"count", "mean", "min", "max"}.issubset(c4.columns))
    comprobar("consulta 5: groupby por mes cuenta todas las filas", c5["cantidad"].sum() == total)


def probar_graficas():
    print("\n=== HU G01: graficas ===")
    # Lee data/limpio/retos_limpio.csv y guarda las imagenes en reportes/
    graficar_retos()

    for n in range(1, 4):
        ruta = CARPETA_REPORTES / f"retos_grafica_{n}.png"
        comprobar(f"existe {ruta.name} y no esta vacia", ruta.exists() and ruta.stat().st_size > 0)


# Para que Python encuentre las carpetas simulacion/, exportacion/, limpieza/, consultas/ y graficacion/
CARPETA_NOTEBOOK = Path(__file__).resolve().parent
if str(CARPETA_NOTEBOOK) not in sys.path:
    sys.path.insert(0, str(CARPETA_NOTEBOOK))

sys.path.insert(0, str(Path(__file__).resolve().parent / "src" / "notebook"))

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

    print("\n=== DATOS REGISTRO ===")
    df = generar_registros(n=800)
    exportar_registros(df)
    limpiar_registros()
    consultar_registros()
    graficar_registros()

    print("\n=== DATOS RETOS ===")
    probar_simulacion()
    probar_exportacion()
    probar_limpieza()
    probar_consultas()
    probar_graficas()



if __name__ == "__main__":
    main()