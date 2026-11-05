"""Consultas de la HU Q01 sobre la tabla registros (archivo LIMPIO).

Ubicación: src/notebook/consultas/consultas_registros.py
Lee:       data/limpio/registros_limpio.csv
Guarda:    data/limpio/registros_consulta_N.csv  (N = 1 a 5)

Se puede ejecutar de dos formas (desde cualquier carpeta):
    python src/notebook/consultas/consultas_registros.py
    o importando consultar_registros() desde main.py
"""
from pathlib import Path

import pandas as pd

# consultas -> notebook -> src -> raíz del proyecto
RAIZ = Path(__file__).resolve().parents[3]
RUTA_ENTRADA = RAIZ / "data" / "limpio" / "registros_limpio.csv"
CARPETA_SALIDA = RAIZ / "data" / "limpio"

# Máximo de filas que se muestran en consola por consulta
# (el CSV siempre se guarda completo).
MAX_FILAS_CONSOLA = 20


def leer_registros(ruta=RUTA_ENTRADA):
    """Lee el CSV limpio y valida que existan las columnas necesarias."""
    ruta = Path(ruta)
    if not ruta.is_file():
        raise SystemExit(f"Error: no existe '{ruta}'. Ejecuta primero la limpieza.")

    df = pd.read_csv(ruta)
    requeridas = {"id", "id_usuario", "id_reto", "estado", "mes"}
    faltan = requeridas - set(df.columns)
    if faltan:
        raise SystemExit(f"Error: faltan columnas en el CSV: {sorted(faltan)}")
    return df


def mostrar(resultado):
    """Imprime el resultado de la consulta (recortado si es muy largo)."""
    if len(resultado) == 0:
        print("(sin resultados)")
    elif len(resultado) <= MAX_FILAS_CONSOLA:
        print(resultado.to_string(index=False))
    else:
        print(resultado.head(MAX_FILAS_CONSOLA).to_string(index=False))
        print(f"... ({len(resultado)} filas en total; el CSV tiene todas)")


def guardar(resultado, n, carpeta=CARPETA_SALIDA):
    """Guarda el resultado de la consulta N como registros_consulta_N.csv."""
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"registros_consulta_{n}.csv"
    resultado.to_csv(ruta, index=False, encoding="utf-8")
    print(f"[guardado: {ruta}]")


def consulta_1_finalizados(df):
    """Consulta 1: participaciones que ya están FINALIZADAS."""
    print("\n=== Consulta 1 — Participaciones ya finalizadas ===")
    print("Pregunta: ¿Qué participaciones ya están finalizadas?")
    finalizados = df[df["estado"] == "FINALIZADO"]
    return finalizados


def consulta_2_repetidos(df):
    """Consulta 2: participaciones repetidas (mismo usuario en el mismo reto)."""
    print("\n=== Consulta 2 — Participaciones repetidas ===")
    print("Pregunta: ¿Qué participaciones están repetidas (mismo usuario en el mismo reto)?")
    repetidos = df[df.duplicated(subset=["id_usuario", "id_reto"], keep=False)]
    return repetidos.sort_values(["id_usuario", "id_reto"])


def consulta_3_por_estado(df):
    """Consulta 3: cuántas participaciones hay por estado."""
    print("\n=== Consulta 3 — Participaciones por estado ===")
    print("Pregunta: ¿Cuántas participaciones hay por estado?")
    conteo = df["estado"].value_counts()
    return conteo.rename_axis("estado").reset_index(name="participaciones")


def consulta_4_top_retos(df):
    """Consulta 4 (GROUPBY): los 10 retos con más participantes."""
    print("\n=== Consulta 4 — Top 10 retos con más participantes ===")
    print("Pregunta: ¿Cuáles son los 10 retos con más participantes?")
    top_retos = df.groupby("id_reto")["id"].count().nlargest(10)
    return top_retos.rename_axis("id_reto").reset_index(name="participantes")


def consulta_5_por_mes(df):
    """Consulta 5 (GROUPBY): cuántas participaciones hubo cada mes."""
    print("\n=== Consulta 5 — Participaciones por mes ===")
    print("Pregunta: ¿Cuántas participaciones hubo cada mes?")
    por_mes = df.groupby("mes")["id"].count()
    return por_mes.rename_axis("mes").reset_index(name="participaciones")


def consultar_registros(ruta_entrada=RUTA_ENTRADA, carpeta_salida=CARPETA_SALIDA):
    """Lee el CSV limpio, corre las cinco consultas en orden y guarda los resultados."""
    df = leer_registros(ruta_entrada)

    consultas = [
        consulta_1_finalizados,
        consulta_2_repetidos,
        consulta_3_por_estado,
        consulta_4_top_retos,
        consulta_5_por_mes,
    ]
    for n, funcion in enumerate(consultas, start=1):
        resultado = funcion(df)  # la función imprime su título y su pregunta
        mostrar(resultado)
        guardar(resultado, n, carpeta_salida)


if __name__ == "__main__":
    consultar_registros()