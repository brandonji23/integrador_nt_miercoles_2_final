import random
import uuid

import pandas as pd
from faker import Faker

# 1. País y lenguaje de la simulación
fake = Faker("es_CO")

# 2. Semillas fijas (reproducibilidad)
Faker.seed(42)
random.seed(42)

# 3. Constantes
ESTADOS = ["pendiente", "aprobado", "rechazado"]
IDS_USUARIO = [str(uuid.UUID(int=random.getrandbits(128), version=4)) for _ in range(50)]
IDS_RETO = [str(uuid.UUID(int=random.getrandbits(128), version=4)) for _ in range(20)]


def _muestra(df, frac):
    """Devuelve los índices de una fracción aleatoria del DataFrame."""
    return df.sample(frac=frac, random_state=random.randint(0, 9999)).index


def generar_registros(n=800):
    # 4. Datos limpios
    filas = []
    for _ in range(n):
        filas.append({
            "id": str(uuid.uuid4()),
            "fecha_registro": fake.date_time_between(start_date="-1y", end_date="now"),
            "observacion": fake.sentence(nb_words=10),
            "estado": random.choice(ESTADOS),
            "id_usuario": random.choice(IDS_USUARIO),
            "id_reto": random.choice(IDS_RETO),
        })
    df = pd.DataFrame(filas)

    # 5. Ensuciar fecha_registro: dos formatos mezclados
    iso = df["fecha_registro"].dt.strftime("%Y-%m-%d %H:%M:%S")
    latino = df["fecha_registro"].dt.strftime("%d/%m/%Y %H:%M")
    df["fecha_registro"] = iso
    idx = _muestra(df, 0.10)
    df.loc[idx, "fecha_registro"] = latino.loc[idx]

    # 6. Ensuciar observacion: 20% nulos
    idx = _muestra(df, 0.20)
    df.loc[idx, "observacion"] = None

    # 7. Ensuciar estado: variantes
    variantes = ["inscrito", "EN PROCESO", " Finalizado "]
    idx = _muestra(df, 0.15)
    df.loc[idx, "estado"] = [random.choice(variantes) for _ in idx]

    # 8. 10% con el par id_usuario + id_reto repetido
    idx = _muestra(df, 0.10)
    origen = df.drop(index=idx).sample(n=len(idx), random_state=random.randint(0, 9999))
    df.loc[idx, "id_usuario"] = origen["id_usuario"].values
    df.loc[idx, "id_reto"] = origen["id_reto"].values

    # 9. 5% de filas duplicadas exactas
    idx = _muestra(df, 0.05)
    df = pd.concat([df, df.loc[idx]], ignore_index=True)

    return df


if __name__ == "__main__":
    df = generar_registros()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())