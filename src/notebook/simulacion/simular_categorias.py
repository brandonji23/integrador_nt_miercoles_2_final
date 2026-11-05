import random
import unicodedata
import uuid

import pandas as pd
from faker import Faker

# 1. País e idioma de la simulación
fake = Faker("es_CO")

# 2. Semillas fijas para que sea reproducible
Faker.seed(42)
random.seed(42)

# 3. Constantes
CATEGORIAS = [
    "Tecnología",
    "Educación",
    "Salud",
    "Finanzas",
    "Entretenimiento",
    "Logística",
    "Turismo",
    "Deportes",
    "Comercio",
    "Seguridad",
]
AREAS = [
    "Desarrollo",
    "Recursos Humanos",
    "Marketing",
    "Ventas",
    "Administración",
]


def _sin_tilde(texto):
    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


def _escribir_mal(texto):
    variantes = [
        texto.upper(),             # TECNOLOGÍA
        f" {texto.lower()} ",      # " tecnología "
        _sin_tilde(texto),         # Tecnologia
        _sin_tilde(texto.lower()), # tecnologia
    ]
    return random.choice(variantes)


def _generar_muestra(datos, porcentaje):
    return datos.sample(
        frac=porcentaje, random_state=random.randint(0, 9999)
    ).index


def _ensuciar(datos_df):
    df = datos_df.copy()

    # nombre: 30% con variantes de escritura
    idx = _generar_muestra(df, 0.30)
    df.loc[idx, "nombre"] = df.loc[idx, "nombre"].apply(_escribir_mal)

    # descripcion: 15% nulos
    idx = _generar_muestra(df, 0.15)
    df.loc[idx, "descripcion"] = None

    # area_responsable: 10% nulos
    idx = _generar_muestra(df, 0.10)
    df.loc[idx, "area_responsable"] = None

    # 8% de filas repetidas tal cual (se mantienen las 250 filas)
    n_dup = round(len(df) * 0.08)
    destino = df.sample(n=n_dup, random_state=random.randint(0, 9999)).index
    candidatos = list(df.index.difference(destino))
    for i in destino:
        df.loc[i] = df.loc[random.choice(candidatos)]

    return df


def generar_categorias(n=250):
    registros = []
    for _ in range(n):
        registros.append({
            "id": str(uuid.uuid4()),
            "nombre": random.choice(CATEGORIAS),
            "descripcion": fake.sentence(nb_words=8),
            "area_responsable": random.choice(AREAS),
        })
    df = pd.DataFrame(registros)
    df = _ensuciar(df)
    return df


if __name__ == "__main__":
    df = generar_categorias()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())