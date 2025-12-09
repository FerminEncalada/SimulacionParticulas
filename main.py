from entorno import Entorno
from random_walk import RandomWalk
from visualizador import Visualizador


def main():
    """
    Función principal que ejecuta la simulación Random Walk.
    
    Permite al usuario configurar los parámetros de la simulación mediante
    entrada por consola, ejecuta el algoritmo mostrando el progreso paso a
    paso, y muestra los resultados con visualización.
    """
    print("\n" + "="*70)
    print("🚶 SIMULACIÓN SIMPLE RANDOM WALK 2D CON LÍMITES")
    print("   Visualización Gradual del Camino")
    print("="*70 + "\n")
    
    # Configuración del entorno
    try:
        print("📋 CONFIGURACIÓN DEL ENTORNO")
        print("-" * 70)
        ancho = int(input("Ingrese el ancho del entorno (default: 30): ") or "30")
        alto = int(input("Ingrese el alto del entorno (default: 30): ") or "30")
        num_pasos = int(input("Ingrese el número de pasos a simular: "))
        
        print("\n🎮 OPCIONES DE VISUALIZACIÓN")
        print("-" * 70)
        print("1. Mostrar cada paso en consola (detallado)")
        print("2. Mostrar solo resumen cada 10 pasos (rápido)")
        print("3. Sin información en consola (muy rápido)")
        
        opcion = input("\nSeleccione opción (1/2/3) [default: 2]: ") or "2"
        
        if opcion == "1":
            mostrar_progreso = True
            mostrar_cada = 1
        elif opcion == "3":
            mostrar_progreso = False
            mostrar_cada = num_pasos + 1  # No mostrar nada
        else:
            mostrar_progreso = False
            mostrar_cada = 10
        
    except ValueError:
        print("❌ Error: Debe ingresar valores numéricos válidos")
        return
    
    if num_pasos <= 0:
        print("❌ Error: El número de pasos debe ser positivo")
        return
    
    if ancho <= 0 or alto <= 0:
        print("❌ Error: Las dimensiones del entorno deben ser positivas")
        return
    
    # Crear entorno
    entorno = Entorno(ancho=ancho, alto=alto)
    
    # Crear y ejecutar Random Walk
    random_walk = RandomWalk(entorno)
    estadisticas = random_walk.simular(num_pasos, 
                                       mostrar_progreso=mostrar_progreso,
                                       mostrar_cada=mostrar_cada)
    
    # Mostrar estadísticas
    Visualizador.mostrar_estadisticas(estadisticas)
    
    # Preguntar tipo de visualización
    print("🎨 OPCIONES DE VISUALIZACIÓN GRÁFICA")
    print("-" * 70)
    print("1. Gráfico estático (imagen completa)")
    print("2. Animación paso a paso")
    print("3. Ambos")
    print("4. Ninguno")
    
    opcion_visual = input("\nSeleccione opción (1/2/3/4) [default: 2]: ") or "2"
    
    try:
        if opcion_visual in ["1", "3"]:
            print("\n📊 Generando visualización estática...")
            Visualizador.visualizar_camino_estatico(estadisticas, entorno)
        
        if opcion_visual in ["2", "3"]:
            print("\n🎬 Generando animación...")
            intervalo = int(input("Velocidad de animación en ms (default: 70): ") or "70")
            Visualizador.visualizar_camino_animado(estadisticas, entorno, intervalo)
            
    except Exception as e:
        print(f"❌ Error al visualizar: {e}")
        print("💡 Asegúrese de tener matplotlib instalado: pip install matplotlib")
    
    print("\n" + "="*70)
    print("✅ Simulación finalizada.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
