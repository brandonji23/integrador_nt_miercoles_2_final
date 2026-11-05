import random
import uuid
import pandas as pd
from faker import Faker
from datetime import timedelta

# 1. Escoger el pais y lenguaje para simular los datos
fake = Faker("es_CO")

# 2. Sembrar semillas
Faker.seed(42)
random.seed(42)

# 3. Constantes: listas fijas para que varios retos compartan empresa, categoria y prioridad
FILAS = 500

ESTADOS = ["Pendiente", "En_proceso", "Completado", "Cancelado"]


def _uuid_fijo(nombre):
    # UUID determinista: siempre es el mismo para el mismo nombre
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, nombre))


IDS_EMPRESA = [_uuid_fijo(f"empresa-{i}") for i in range(1, 5)]
IDS_CATEGORIA = [_uuid_fijo(f"categoria-{c}") for c in ["hardware", "software", "redes", "soporte"]]
IDS_PRIORIDAD = [_uuid_fijo(f"prioridad-{p}") for p in ["baja", "media", "alta", "critica"]]


# 4. Funcion que muestra una parte de los datos (devuelve los indices)
def generar_muestra(datos, porcentaje):
    return datos.sample(
        frac=porcentaje,
        random_state=random.randint(0, 9999)
    ).index


# 5. Funcion que ensucia los datos
def ensuciar(datos_df):
    datos_df = datos_df.copy()

    # Guardamos las fechas reales antes de convertirlas a texto
    inicio_real = datos_df["fecha_inicio"].copy()

    # `nombre`: 10% con espacios sobrantes
    indices = generar_muestra(datos_df, 0.10)
    datos_df.loc[indices, "nombre"] = " " + datos_df.loc[indices, "nombre"] + " "

    # `descripcion`: 12% nulos
    indices = generar_muestra(datos_df, 0.12)
    datos_df.loc[indices, "descripcion"] = None

    # `fecha_fin`: 5% ANTERIOR a fecha_inicio (error logico a detectar).
    # Se elige ANTES de poner los nulos para que el 8% de nulos no se pise.
    cantidad_error = int(len(datos_df) * 0.05)
    indices = datos_df.sample(
        n=cantidad_error,
        random_state=random.randint(0, 9999)
    ).index
    dias_antes = pd.to_timedelta(
        [random.randint(1, 30) for _ in indices], unit="D"
    )
    datos_df.loc[indices, "fecha_fin"] = inicio_real.loc[indices] - dias_antes

    # `fecha_fin`: 8% nulos, solo entre las filas que no tienen error de fecha
    # (asi quedan exactamente 8% nulos y 5% con fecha anterior)
    candidatas = datos_df.drop(index=indices)
    cantidad_nulos = int(len(datos_df) * 0.08)
    indices_nulos = candidatas.sample(
        n=cantidad_nulos,
        random_state=random.randint(0, 9999)
    ).index
    datos_df.loc[indices_nulos, "fecha_fin"] = None

    # `fecha_inicio`: dos formatos mezclados "2026-03-02" y "02/03/2026"
    iso = inicio_real.dt.strftime("%Y-%m-%d")
    latino = inicio_real.dt.strftime("%d/%m/%Y")
    datos_df["fecha_inicio"] = iso
    indices = generar_muestra(datos_df, 0.30)
    datos_df.loc[indices, "fecha_inicio"] = latino.loc[indices]

    # `estado`: variantes sucias
    variantes_estado = ["en_curso", "EN CURSO", " Cerrado "]
    indices = generar_muestra(datos_df, 0.05)
    datos_df.loc[indices, "estado"] = [random.choice(variantes_estado) for _ in indices]

    # 5% de las filas repetidas tal cual (duplicados exactos)
    cantidad_duplicados = int(len(datos_df) * 0.05)
    filas_duplicadas = datos_df.sample(n=cantidad_duplicados, random_state=42)
    datos_df = pd.concat([datos_df, filas_duplicadas], ignore_index=True)

    return datos_df


# 6. Funcion generadora: devuelve el DataFrame sucio
def generar_retos(n=FILAS):
    filas = []

    for _ in range(n):
        fecha_inicio = fake.date_between(start_date="-1y", end_date="+3m")

        filas.append({
            "id": str(uuid.uuid4()),
            "nombre": fake.sentence(nb_words=6).rstrip("."),
            "descripcion": fake.sentence(nb_words=12),
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_inicio + timedelta(days=random.randint(15, 180)),
            "estado": random.choice(ESTADOS),
            "id_empresa": random.choice(IDS_EMPRESA),
            "id_categoria": random.choice(IDS_CATEGORIA),
            "id_prioridad": random.choice(IDS_PRIORIDAD),
        })

    df = pd.DataFrame(filas)
    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"])
    df["fecha_fin"] = pd.to_datetime(df["fecha_fin"])

    df = ensuciar(df)
    return df


if __name__ == "__main__":
    df = generar_retos()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())