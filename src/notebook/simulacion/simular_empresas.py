import random
import uuid

import pandas as pd
from faker import Faker

# Constantes
SECTORES = ["Tecnología", "Salud", "Educación", "Finanzas", "Manufactura",
            "Comercio", "Transporte", "Turismo", "Agricultura", "Energía"]

# Semilla fija para que el archivo sea reproducible
Faker.seed(42)
random.seed(42)
fake = Faker("es_CO")


def _muestra(df, fraccion):
    """Devuelve el índice de una fracción de filas al azar (reproducible)."""
    return df.sample(frac=fraccion, random_state=random.randint(0, 9999)).index


def _variante_sector(texto):
    return random.choice([texto.upper(), texto.lower(), f" {texto.lower()} "])


def _formato_telefono(numero):
    return random.choice([
        numero,                                            # 3001234567
        f"{numero[:3]} {numero[3:6]} {numero[6:]}",        # 300 123 4567
        f"+57 {numero[:3]}-{numero[3:6]}-{numero[6:]}",    # +57 300-123-4567
    ])


def _formato_activa(valor):
    if valor:
        return random.choice(["SI", "1"])
    return random.choice(["No", "0"])


def generar_empresas(n=300):
    # 1. Datos limpios
    filas = []
    for _ in range(n):
        filas.append({
            "id": str(uuid.uuid4()),
            "nombre": fake.company(),
            "nit": fake.numerify("#########-#"),
            "sector": random.choice(SECTORES),
            "contacto": fake.name(),
            "correo": fake.company_email(),
            "telefono": fake.numerify("3#########"),
            "activa": random.choice([True, False]),
        })
    df = pd.DataFrame(filas)

    # 2. Ensuciar
    # nit repetido entre empresas distintas (3%): antes de cambiar el formato
    idx = _muestra(df, 0.03)
    df.loc[idx, "nit"] = random.choices(df["nit"].tolist(), k=len(idx))

    # nombre: 10% con espacios y 15% en mayúsculas
    idx = _muestra(df, 0.10)
    df.loc[idx, "nombre"] = " " + df.loc[idx, "nombre"] + " "
    idx = _muestra(df, 0.15)
    df.loc[idx, "nombre"] = df.loc[idx, "nombre"].str.upper()

    # nit: la mitad con puntos (900.123.456-7), la otra mitad sin nada (9001234567)
    mezcla = df.sample(frac=1, random_state=random.randint(0, 9999)).index
    mitad = len(mezcla) // 2
    con_puntos, sin_nada = mezcla[:mitad], mezcla[mitad:]
    solo_digitos = df["nit"].str.replace("-", "", regex=False)
    df.loc[con_puntos, "nit"] = solo_digitos[con_puntos].map(
        lambda d: f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9]}")
    df.loc[sin_nada, "nit"] = solo_digitos[sin_nada]

    # sector: variantes del mismo sector (40%)
    idx = _muestra(df, 0.40)
    df.loc[idx, "sector"] = df.loc[idx, "sector"].map(_variante_sector)

    # contacto: 8% nulos
    idx = _muestra(df, 0.08)
    df.loc[idx, "contacto"] = None

    # correo: 6% sin arroba
    idx = _muestra(df, 0.06)
    df.loc[idx, "correo"] = df.loc[idx, "correo"].str.replace("@", "", regex=False)

    # telefono: tres formatos mezclados
    df["telefono"] = df["telefono"].map(_formato_telefono)

    # activa: a veces como texto ('SI', 'No', '1', '0')
    df["activa"] = df["activa"].astype(object)
    idx = _muestra(df, 0.30)
    df.loc[idx, "activa"] = df.loc[idx, "activa"].map(_formato_activa)

    # duplicados exactos: 5% de las filas repetidas tal cual
    repetidas = df.sample(frac=0.05, random_state=random.randint(0, 9999))
    df = pd.concat([df, repetidas], ignore_index=True)

    return df


if __name__ == "__main__":
    df = generar_empresas()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())