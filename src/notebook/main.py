from simulacion.simular_prioridades import generar_prioridades
from exportacion.exportar_prioridades import exportar
from limpieza.limpiar_prioridades import main as limpiar_datos
from consultas.consultas_prioridades import main as consultar_datos
from graficacion.reporte_prioridades import main as graficar_datos

def main():
    # 1. Simulación (HU F01)
    df = generar_prioridades()
    print("=== SIMULACIÓN ===")
    print(df.shape)
    print(df.head(10))
    print("\nNulos por columna:")
    print(df.isna().sum())

    # 2. Exportación (HU X01)
    print("\n=== EXPORTACIÓN ===")
    exportar(df)

    print("\n=== LIMPIEZA ===")
    limpiar_datos()

    print("\n=== CONSULTAS ===")
    consultar_datos()

    print("\n=== GRÁFICAS ===")
    graficar_datos()


if __name__ == "__main__":
    main()

    