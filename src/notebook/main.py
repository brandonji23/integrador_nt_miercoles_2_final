from simulacion.simular_empresas import generar_empresas
from exportacion.exportar_empresas import exportar_empresas
from limpieza.limpiar_empresas import main as limpiar_empresas
from consultas.consultas_empresas import main as consultar_empresas
from graficacion.reporte_empresas import main as graficar_empresas


def main():
    print("=== HU F01: Simulación ===")
    df = generar_empresas(300)
    print(df.shape)
    print(df.head())
    print(df.isna().sum())

    print("\n=== HU X01: Exportación ===")
    exportar_empresas(df)

    print("\n=== HU L01: Limpieza ===")
    limpiar_empresas()

    print("\n=== HU Q01: Consultas ===")
    consultar_empresas()

    print("\n=== HU G01: Gráficas ===")
    graficar_empresas()


if __name__ == "__main__":
    main()