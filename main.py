from entorno import Entorno
from simulacion import Simulacion
from visualizador import Visualizador


def main():
    """
    Función principal que ejecuta la simulación de población de forma visual.
    """
    print("\n" + "="*70)
    print("🌍 SIMULACIÓN VISUAL DE POBLACIÓN CON RANDOM WALK")
    print("   Sistema de Supervivencia y Reproducción en Tiempo Real")
    print("="*70 + "\n")
    
    # ==================== CONFIGURACIÓN ====================
    try:
        print("📋 CONFIGURACIÓN DEL ENTORNO")
        print("-" * 70)
        ancho = int(input("Ancho del entorno (default: 40): ") or "40")
        alto = int(input("Alto del entorno (default: 40): ") or "40")
        porcentaje_comida = float(input("Porcentaje de comida 0-1 (default: 0.15): ") or "0.15")
        
        print("\n📋 CONFIGURACIÓN DE LA SIMULACIÓN")
        print("-" * 70)
        num_particulas = int(input("Número de partículas iniciales (default: 3): ") or "3")
        pasos_por_dia = int(input("Pasos por día (default: 80): ") or "80")
        max_dias = int(input("Días máximos a simular (default: 20): ") or "20")
        
        print("\n🎬 CONFIGURACIÓN DE VISUALIZACIÓN")
        print("-" * 70)
        print("💡 Velocidades sugeridas:")
        print("   - 10ms: Muy rápido (observación general)")
        print("   - 30ms: Rápido (recomendado)")
        print("   - 50ms: Medio (buena visibilidad)")
        print("   - 100ms: Lento (análisis detallado)")
        intervalo = int(input("\nVelocidad en ms (default: 30): ") or "30")
        
    except ValueError:
        print("❌ Error: Debe ingresar valores numéricos válidos")
        return
    
    # Validaciones
    if ancho <= 0 or alto <= 0:
        print("❌ Error: Las dimensiones deben ser positivas")
        return
    
    if porcentaje_comida < 0 or porcentaje_comida > 1:
        print("❌ Error: El porcentaje de comida debe estar entre 0 y 1")
        return
    
    if num_particulas <= 0 or pasos_por_dia <= 0:
        print("❌ Error: Número de partículas y pasos deben ser positivos")
        return
    
    # ==================== CREAR SIMULACIÓN ====================
    print("\n🔧 Inicializando simulación...")
    entorno = Entorno(ancho=ancho, alto=alto, porcentaje_comida=porcentaje_comida)
    simulacion = Simulacion(
        entorno=entorno,
        num_particulas_inicial=num_particulas,
        pasos_por_dia=pasos_por_dia
    )
    
    # ==================== EJECUTAR SIMULACIÓN VISUAL ====================
    print("\n" + "="*70)
    print("🎬 PREPARANDO VENTANA DE SIMULACIÓN...")
    print("="*70)
    print("⚠️  La ventana se abrirá en unos segundos")
    print("⚠️  NO cierres esta consola, aquí verás los reportes de cada día")
    print("="*70 + "\n")
    
    try:
        Visualizador.simular_visualmente(
            simulacion=simulacion,
            max_dias=max_dias,
            intervalo=intervalo
        )
        
    except Exception as e:
        print(f"\n❌ Error durante la simulación: {e}")
        print("💡 Asegúrese de tener matplotlib instalado: pip install matplotlib")
        import traceback
        traceback.print_exc()
        return
    
    # ==================== MOSTRAR RESULTADOS ====================
    print("\n" + "="*70)
    print("✅ SIMULACIÓN FINALIZADA")
    print("="*70)
    
    if simulacion.historial_dias:
        print(f"\n📊 ESTADÍSTICAS FINALES:")
        print(f"{'='*70}")
        print(f"Días simulados: {len(simulacion.historial_dias)}")
        print(f"Partículas finales: {simulacion.historial_dias[-1]['particulas_finales']}")
        
        total_muertes = sum([d['muertes'] for d in simulacion.historial_dias])
        total_reproducciones = sum([d['reproducciones'] for d in simulacion.historial_dias])
        
        print(f"Total de muertes: {total_muertes}")
        print(f"Total de reproducciones: {total_reproducciones}")
        print(f"{'='*70}")
        
        if simulacion.historial_dias[-1]['particulas_finales'] > 0:
            print("\n🎉 ¡LA POBLACIÓN SOBREVIVIÓ!")
        else:
            print("\n💀 LA POBLACIÓN SE EXTINGUIÓ")
    
    print("="*70 + "\n")
    
    # ==================== OPCIONES POST-SIMULACIÓN ====================
    while True:
        print("📊 OPCIONES POST-SIMULACIÓN")
        print("-" * 70)
        print("1. Ver gráficas de estadísticas")
        print("2. Ver resumen detallado día por día")
        print("3. Salir")
        
        opcion = input("\nSeleccione opción (1/2/3) [default: 3]: ") or "3"
        
        if opcion == "1":
            if simulacion.historial_dias:
                try:
                    print("\n📊 Generando gráficas...")
                    Visualizador.graficar_estadisticas(simulacion.historial_dias)
                except Exception as e:
                    print(f"❌ Error al generar gráficas: {e}")
            else:
                print("⚠️  No hay datos para graficar")
        
        elif opcion == "2":
            if simulacion.historial_dias:
                print(f"\n{'='*70}")
                print("📋 RESUMEN DETALLADO POR DÍA")
                print(f"{'='*70}")
                
                for dia in simulacion.historial_dias:
                    print(f"\n🌅 DÍA {dia['dia']}:")
                    print(f"   Partículas al final: {dia['particulas_finales']}")
                    print(f"   Muertes: {dia['muertes']}")
                    print(f"   Reproducciones: {dia['reproducciones']}")
                    print(f"   Comida restante al final: {dia['comida_restante']}")
                
                print(f"\n{'='*70}")
            else:
                print("⚠️  No hay datos para mostrar")
        
        else:
            break
    
    print("\n" + "="*70)
    print("✅ Programa finalizado. ¡Gracias por usar el simulador!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()