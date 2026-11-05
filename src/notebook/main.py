# main.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src" / "notebook"))

from simulacion.simular_registros import generar_registros
from exportacion.exportar_registros import exportar_registros
from limpieza.limpiar_registros import limpiar_registros
from consultas.consultas_registros import consultar_registros
from graficacion.graficar_registros import graficar_registros


def main():
    df = generar_registros(n=800)
    exportar_registros(df)
    limpiar_registros()
    consultar_registros()
    graficar_registros()


if __name__ == "__main__":
    main()