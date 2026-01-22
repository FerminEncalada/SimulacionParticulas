import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import numpy as np

class Visualizador:
    """
    Clase para visualizar la simulación de población en tiempo real.
    """
    
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import numpy as np

class Visualizador:
    """
    Clase para visualizar la simulación de población en tiempo real.
    """
    
    @staticmethod
    def simular_visualmente(simulacion, intervalo=30):
        """
        Ejecuta y visualiza la simulación en tiempo real hasta que todas las partículas mueran.
        
        Args:
            simulacion (Simulacion): La simulación a ejecutar
            intervalo (int): Milisegundos entre frames
        """
        entorno = simulacion.entorno
        pasos_por_dia = simulacion.pasos_por_dia
        
        # Crear figura más grande
        fig, ax = plt.subplots(figsize=(18, 16))
        
        # Configurar límites con más espacio
        margen = 2
        ax.set_xlim(-margen, entorno.ancho + margen)
        ax.set_ylim(-margen, entorno.alto + margen)
        ax.set_aspect('equal')
        ax.set_facecolor('#e8f4f8')
        fig.patch.set_facecolor('white')
        ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
        ax.invert_yaxis()
        
        # Dibujar casa (bordes verdes más visibles) - CORREGIDO para cubrir toda la zona
        casa_color = '#2ecc71'
        grosor_casa = 0.8
        # Borde superior
        ax.add_patch(patches.Rectangle((0, 0), entorno.ancho, grosor_casa, 
                                      color=casa_color, alpha=0.7, label='Casa (Zona Segura)', zorder=1))
        # Borde inferior
        ax.add_patch(patches.Rectangle((0, entorno.alto - grosor_casa), entorno.ancho, grosor_casa, 
                                      color=casa_color, alpha=0.7, zorder=1))
        # Borde izquierdo
        ax.add_patch(patches.Rectangle((0, 0), grosor_casa, entorno.alto, 
                                      color=casa_color, alpha=0.7, zorder=1))
        # Borde derecho
        ax.add_patch(patches.Rectangle((entorno.ancho - grosor_casa, 0), grosor_casa, entorno.alto, 
                                      color=casa_color, alpha=0.7, zorder=1))
        
        ax.set_xlabel('X', fontsize=14, fontweight='bold')
        ax.set_ylabel('Y', fontsize=14, fontweight='bold')
        
        # Título principal
        titulo = ax.text(0.5, 1.06, '', transform=ax.transAxes, 
                        fontsize=16, fontweight='bold', ha='center',
                        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        # Panel de información más grande y visible
        contador_texto = ax.text(0.02, 0.98, '', transform=ax.transAxes,
                                fontsize=13, fontweight='bold', 
                                verticalalignment='top',
                                bbox=dict(boxstyle='round,pad=0.8', 
                                        facecolor='white', alpha=0.95,
                                        edgecolor='black', linewidth=2),
                                zorder=10,
                                family='monospace')
        
        # Scatter para comida (más grande y visible)
        scatter_comida = ax.scatter([], [], c='#ff6b35', s=80, alpha=0.9, 
                                   marker='o', label='Comida', zorder=3, 
                                   edgecolors='#c44616', linewidths=1.5)
        
        ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
        
        # Variables de estado
        paso_en_dia = 0
        dia_actual = 1
        elementos_particulas = []
        simulacion_activa = True
        
        def init():
            # Mostrar comida inicial
            if entorno.posiciones_comida:
                comida_x = [pos[0] for pos in entorno.posiciones_comida]
                comida_y = [pos[1] for pos in entorno.posiciones_comida]
                scatter_comida.set_offsets(np.column_stack([comida_x, comida_y]))
            
            titulo.set_text('Simulacion de Poblacion - INICIANDO...')
            contador_texto.set_text(
                f'Particulas: {len(simulacion.particulas)}\n'
                f'Comida: {len(entorno.posiciones_comida)}\n'
                f'Dia: 1\n'
                f'Paso: 0/{pasos_por_dia}'
            )
            return [scatter_comida, titulo, contador_texto]
        
        def animate(frame):
            nonlocal paso_en_dia, dia_actual, elementos_particulas, simulacion_activa
            
            if not simulacion_activa:
                return [scatter_comida, titulo, contador_texto]
            
            # Limpiar elementos anteriores
            for elemento in elementos_particulas:
                try:
                    elemento.remove()
                except:
                    pass
            elementos_particulas.clear()
            
            # Verificar si hay partículas
            if len(simulacion.particulas) == 0:
                titulo.set_text('SIMULACION FINALIZADA - Todas las particulas murieron')
                contador_texto.set_text(
                    f'Dia final: {dia_actual - 1}\n'
                    f'Particulas: 0\n'
                    f'Estado: EXTINCION'
                )
                simulacion_activa = False
                print(f"\n{'='*70}")
                print("SIMULACION TERMINADA - EXTINCION TOTAL")
                print(f"{'='*70}\n")
                return [scatter_comida, titulo, contador_texto]
            
            # Realizar un paso para cada partícula
            for particula in simulacion.particulas:
                particula.realizar_paso()
            
            paso_en_dia += 1
            
            # Actualizar visualización de comida
            if entorno.posiciones_comida:
                comida_x = [pos[0] for pos in entorno.posiciones_comida]
                comida_y = [pos[1] for pos in entorno.posiciones_comida]
                scatter_comida.set_offsets(np.column_stack([comida_x, comida_y]))
            else:
                scatter_comida.set_offsets(np.empty((0, 2)))
            
            # Dibujar partículas y sus caminos
            for i, particula in enumerate(simulacion.particulas):
                # Dibujar camino completo (más grueso y visible)
                if len(particula.camino) > 1:
                    xs = [pos[0] for pos in particula.camino]
                    ys = [pos[1] for pos in particula.camino]
                    linea, = ax.plot(xs, ys, '-', linewidth=2.5, 
                                   color=particula.color, alpha=0.6, zorder=2)
                    elementos_particulas.append(linea)
                
                # Dibujar posición actual (más grande)
                x, y = particula.posicion_actual
                punto = ax.scatter([x], [y], c=[particula.color], 
                                 s=300, edgecolors='black', linewidths=3, 
                                 zorder=5, alpha=1.0)
                elementos_particulas.append(punto)
                
                # Mostrar ID (más visible)
                texto = ax.text(x, y - 2.5, f'#{particula.id}', 
                              fontsize=10, ha='center', va='top', fontweight='bold',
                              bbox=dict(boxstyle='round,pad=0.4', 
                                      facecolor='white', alpha=0.9, 
                                      edgecolor='black', linewidth=1.5),
                              zorder=6)
                elementos_particulas.append(texto)
                
                # Indicador de comida consumida (sin emoji problemático)
                if particula.comida_consumida > 0:
                    comida_text = ax.text(x, y + 2.5, f'x{particula.comida_consumida}', 
                                        fontsize=11, ha='center', va='bottom',
                                        bbox=dict(boxstyle='round,pad=0.3', 
                                                facecolor='#ffeb3b', alpha=0.9,
                                                edgecolor='#f57c00', linewidth=1.5),
                                        zorder=6, fontweight='bold')
                    elementos_particulas.append(comida_text)
            
            # Actualizar título
            progreso = (paso_en_dia / pasos_por_dia) * 100
            titulo.set_text(f'Simulacion de Poblacion - DIA {dia_actual} - {progreso:.1f}% completado')
            
            # Actualizar contador
            contador_texto.set_text(
                f'Particulas: {len(simulacion.particulas)}\n'
                f'Comida: {len(entorno.posiciones_comida)}\n'
                f'Dia: {dia_actual}\n'
                f'Paso: {paso_en_dia}/{pasos_por_dia}'
            )
            
            # Verificar si terminó el día
            if paso_en_dia >= pasos_por_dia:
                # Evaluar fin del día
                sobrevivientes = []
                reproducciones = 0
                muertes = 0
                mutaciones_velocidad = 0
                mutaciones_prioridad = 0
                
                for particula in simulacion.particulas:
                    resultado = particula.evaluar_fin_dia()
                    
                    if resultado['sobrevive']:
                        sobrevivientes.append(particula)
                        
                        if resultado['reproduce']:
                            hijo = particula.crear_hijo(
                                simulacion._obtener_nuevo_id(),
                                mutacion_hijo=resultado['mutacion_hijo']
                            )
                            sobrevivientes.append(hijo)
                            reproducciones += 1
                            
                            # Contar mutaciones
                            if resultado['mutacion_hijo'] == 'velocidad':
                                mutaciones_velocidad += 1
                            elif resultado['mutacion_hijo'] == 'prioridad':
                                mutaciones_prioridad += 1
                    else:
                        muertes += 1
                        particula.viva = False
                
                # Actualizar partículas
                simulacion.particulas = sobrevivientes
                
                # Contar partículas por tipo
                normales = sum(1 for p in simulacion.particulas if p.mutacion == 'ninguna')
                velocidad = sum(1 for p in simulacion.particulas if p.mutacion == 'velocidad')
                prioridad = sum(1 for p in simulacion.particulas if p.mutacion == 'prioridad')
                
                # Guardar estadísticas
                estadisticas = {
                    'dia': dia_actual,
                    'particulas_finales': len(simulacion.particulas),
                    'muertes': muertes,
                    'reproducciones': reproducciones,
                    'comida_restante': entorno.comida_actual,
                    'normales': normales,
                    'velocidad': velocidad,
                    'prioridad': prioridad,
                    'nuevas_mutaciones_velocidad': mutaciones_velocidad,
                    'nuevas_mutaciones_prioridad': mutaciones_prioridad
                }
                simulacion.historial_dias.append(estadisticas)
                
                print(f"\n{'='*70}")
                print(f"FIN DEL DIA {dia_actual}")
                print(f"{'='*70}")
                print(f"Sobrevivientes: {len(simulacion.particulas)}")
                print(f"Muertes: {muertes}")
                print(f"Reproducciones: {reproducciones}")
                print(f"  - Nuevas mutaciones velocidad (rojas): {mutaciones_velocidad}")
                print(f"  - Nuevas mutaciones prioridad (verdes): {mutaciones_prioridad}")
                print(f"Poblacion actual:")
                print(f"  - Normales (blancas): {normales} [Necesitan: 1 comida=sobrevivir, 2=reproducir]")
                print(f"  - Velocidad (rojas): {velocidad} [Necesitan: 2 comidas=sobrevivir, 3=reproducir]")
                print(f"  - Prioridad (verdes): {prioridad} [Necesitan: 1 comida=sobrevivir, 2=reproducir]")
                print(f"Comida restante: {entorno.comida_actual}")
                print(f"{'='*70}\n")
                
                # REESTABLECER COMIDA para el nuevo día
                entorno.reestablecer_comida()
                print(f"Comida reestablecida: {entorno.comida_actual} unidades\n")
                
                # Preparar siguiente día
                dia_actual += 1
                paso_en_dia = 0
                simulacion.dia_actual = dia_actual
                
                for particula in simulacion.particulas:
                    particula.preparar_nuevo_dia()
            
            return [scatter_comida, titulo, contador_texto] + elementos_particulas
        
        # Frames infinitos (se detendrá cuando no haya partículas)
        frames_totales = 100000  # Número muy alto para simular infinito
        
        print(f"\n{'='*70}")
        print("INICIANDO SIMULACION VISUAL EN TIEMPO REAL")
        print(f"{'='*70}")
        print(f"Dimensiones: {entorno.ancho}x{entorno.alto}")
        print(f"Particulas iniciales: {len(simulacion.particulas)}")
        print(f"Comida inicial: {entorno.comida_total}")
        print(f"Pasos por dia: {pasos_por_dia}")
        print(f"Velocidad: {intervalo}ms por frame")
        print(f"{'='*70}")
        print("Observa como las particulas se mueven, comen y sobreviven")
        print("Los bordes VERDES son la CASA (zona segura)")
        print("Los puntos NARANJAS son COMIDA")
        print("La comida se RESTABLECE cada dia en nuevas posiciones")
        print("")
        print("TIPOS DE PARTICULAS:")
        print("  - BLANCAS (normales): 1 comida=sobrevivir, 2=reproducirse")
        print("  - ROJAS (velocidad): 2 comidas=sobrevivir, 3=reproducirse, se mueven 1.5x mas rapido")
        print("  - VERDES (prioridad): 1 comida=sobrevivir, 2=reproducirse, ganan en competencia por comida")
        print("")
        print("La simulacion continuara hasta que todas las particulas mueran")
        print("Presiona CTRL+C en la consola o cierra la ventana para detener")
        print(f"{'='*70}\n")
        
        anim = FuncAnimation(fig, animate, init_func=init, 
                           frames=frames_totales,
                           interval=intervalo, blit=False, repeat=False)
        
        plt.tight_layout()
        plt.show()
        
        return anim
        """
        Ejecuta y visualiza la simulación en tiempo real.
        
        Args:
            simulacion (Simulacion): La simulación a ejecutar
            max_dias (int): Días máximos a simular
            intervalo (int): Milisegundos entre frames
        """
        entorno = simulacion.entorno
        pasos_por_dia = simulacion.pasos_por_dia
        
        # Crear figura más grande
        fig, ax = plt.subplots(figsize=(18, 16))
        
        # Configurar límites con más espacio
        margen = 2
        ax.set_xlim(-margen, entorno.ancho + margen)
        ax.set_ylim(-margen, entorno.alto + margen)
        ax.set_aspect('equal')
        ax.set_facecolor('#e8f4f8')
        fig.patch.set_facecolor('white')
        ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
        ax.invert_yaxis()
        
        # Dibujar casa (bordes verdes más visibles)
        casa_color = '#2ecc71'
        grosor_casa = 0.8
        ax.add_patch(patches.Rectangle((0, 0), entorno.ancho - 1, grosor_casa, 
                                      color=casa_color, alpha=0.7, label='Casa (Zona Segura)', zorder=1))
        ax.add_patch(patches.Rectangle((0, entorno.alto - grosor_casa), entorno.ancho - 1, grosor_casa, 
                                      color=casa_color, alpha=0.7, zorder=1))
        ax.add_patch(patches.Rectangle((0, 0), grosor_casa, entorno.alto - 1, 
                                      color=casa_color, alpha=0.7, zorder=1))
        ax.add_patch(patches.Rectangle((entorno.ancho - grosor_casa, 0), grosor_casa, entorno.alto - 1, 
                                      color=casa_color, alpha=0.7, zorder=1))
        
        ax.set_xlabel('X', fontsize=14, fontweight='bold')
        ax.set_ylabel('Y', fontsize=14, fontweight='bold')
        
        # Título principal
        titulo = ax.text(0.5, 1.06, '', transform=ax.transAxes, 
                        fontsize=16, fontweight='bold', ha='center',
                        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        # Panel de información más grande y visible
        contador_texto = ax.text(0.02, 0.98, '', transform=ax.transAxes,
                                fontsize=13, fontweight='bold', 
                                verticalalignment='top',
                                bbox=dict(boxstyle='round,pad=0.8', 
                                        facecolor='white', alpha=0.95,
                                        edgecolor='black', linewidth=2),
                                zorder=10,
                                family='monospace')
        
        # Scatter para comida (más grande y visible)
        scatter_comida = ax.scatter([], [], c='#ff6b35', s=80, alpha=0.9, 
                                   marker='o', label='Comida', zorder=3, 
                                   edgecolors='#c44616', linewidths=1.5)
        
        ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
        
        # Variables de estado
        paso_en_dia = 0
        dia_actual = 1
        elementos_particulas = []
        simulacion_activa = True
        
        def init():
            # Mostrar comida inicial
            if entorno.posiciones_comida:
                comida_x = [pos[0] for pos in entorno.posiciones_comida]
                comida_y = [pos[1] for pos in entorno.posiciones_comida]
                scatter_comida.set_offsets(np.column_stack([comida_x, comida_y]))
            
            titulo.set_text('🌍 Simulación de Población - INICIANDO...')
            contador_texto.set_text(
                f'🟢 Partículas: {len(simulacion.particulas)}\n'
                f'🍎 Comida: {len(entorno.posiciones_comida)}\n'
                f'📅 Día: 1\n'
                f'⏱️ Paso: 0/{pasos_por_dia}'
            )
            return [scatter_comida, titulo, contador_texto]
        
        def animate(frame):
            nonlocal paso_en_dia, dia_actual, elementos_particulas, simulacion_activa
            
            if not simulacion_activa:
                return [scatter_comida, titulo, contador_texto]
            
            # Limpiar elementos anteriores
            for elemento in elementos_particulas:
                try:
                    elemento.remove()
                except:
                    pass
            elementos_particulas.clear()
            
            # Verificar si hay partículas
            if len(simulacion.particulas) == 0:
                titulo.set_text('💀 SIMULACIÓN FINALIZADA - Todas las partículas murieron')
                contador_texto.set_text(
                    f'Día final: {dia_actual - 1}\n'
                    f'Partículas: 0\n'
                    f'Estado: EXTINCIÓN'
                )
                simulacion_activa = False
                return [scatter_comida, titulo, contador_texto]
            
            # Verificar límite de días
            if dia_actual > max_dias:
                titulo.set_text(f'✅ SIMULACIÓN FINALIZADA - Límite de {max_dias} días alcanzado')
                contador_texto.set_text(
                    f'Día final: {dia_actual - 1}\n'
                    f'Partículas: {len(simulacion.particulas)}\n'
                    f'Estado: POBLACIÓN SOBREVIVIÓ'
                )
                simulacion_activa = False
                return [scatter_comida, titulo, contador_texto]
            
            # Realizar un paso para cada partícula
            for particula in simulacion.particulas:
                particula.realizar_paso()
            
            paso_en_dia += 1
            
            # Actualizar visualización de comida
            if entorno.posiciones_comida:
                comida_x = [pos[0] for pos in entorno.posiciones_comida]
                comida_y = [pos[1] for pos in entorno.posiciones_comida]
                scatter_comida.set_offsets(np.column_stack([comida_x, comida_y]))
            else:
                scatter_comida.set_offsets(np.empty((0, 2)))
            
            # Dibujar partículas y sus caminos
            for i, particula in enumerate(simulacion.particulas):
                # Dibujar camino completo (más grueso y visible)
                if len(particula.camino) > 1:
                    xs = [pos[0] for pos in particula.camino]
                    ys = [pos[1] for pos in particula.camino]
                    linea, = ax.plot(xs, ys, '-', linewidth=2.5, 
                                   color=particula.color, alpha=0.6, zorder=2)
                    elementos_particulas.append(linea)
                
                # Dibujar posición actual (más grande)
                x, y = particula.posicion_actual
                punto = ax.scatter([x], [y], c=[particula.color], 
                                 s=300, edgecolors='black', linewidths=3, 
                                 zorder=5, alpha=1.0)
                elementos_particulas.append(punto)
                
                # Mostrar ID (más visible)
                texto = ax.text(x, y - 2.5, f'#{particula.id}', 
                              fontsize=10, ha='center', va='top', fontweight='bold',
                              bbox=dict(boxstyle='round,pad=0.4', 
                                      facecolor='white', alpha=0.9, 
                                      edgecolor='black', linewidth=1.5),
                              zorder=6)
                elementos_particulas.append(texto)
                
                # Indicador de comida consumida
                if particula.comida_consumida > 0:
                    comida_text = ax.text(x, y + 2.5, f'🍎×{particula.comida_consumida}', 
                                        fontsize=11, ha='center', va='bottom',
                                        bbox=dict(boxstyle='round,pad=0.3', 
                                                facecolor='#ffeb3b', alpha=0.9,
                                                edgecolor='#f57c00', linewidth=1.5),
                                        zorder=6, fontweight='bold')
                    elementos_particulas.append(comida_text)
            
            # Actualizar título
            progreso = (paso_en_dia / pasos_por_dia) * 100
            titulo.set_text(f'🌍 Simulación de Población - DÍA {dia_actual} - {progreso:.1f}% completado')
            
            # Actualizar contador
            contador_texto.set_text(
                f'🟢 Partículas: {len(simulacion.particulas)}\n'
                f'🍎 Comida: {len(entorno.posiciones_comida)}\n'
                f'📅 Día: {dia_actual}\n'
                f'⏱️ Paso: {paso_en_dia}/{pasos_por_dia}'
            )
            
            # Verificar si terminó el día
            if paso_en_dia >= pasos_por_dia:
                # Evaluar fin del día
                sobrevivientes = []
                reproducciones = 0
                muertes = 0
                
                for particula in simulacion.particulas:
                    resultado = particula.evaluar_fin_dia()
                    
                    if resultado['sobrevive']:
                        sobrevivientes.append(particula)
                        
                        if resultado['reproduce']:
                            hijo = particula.crear_hijo(simulacion._obtener_nuevo_id())
                            sobrevivientes.append(hijo)
                            reproducciones += 1
                    else:
                        muertes += 1
                        particula.viva = False
                
                # Actualizar partículas
                simulacion.particulas = sobrevivientes
                
                # Guardar estadísticas
                estadisticas = {
                    'dia': dia_actual,
                    'particulas_finales': len(simulacion.particulas),
                    'muertes': muertes,
                    'reproducciones': reproducciones,
                    'comida_restante': entorno.comida_actual
                }
                simulacion.historial_dias.append(estadisticas)
                
                print(f"\n{'='*70}")
                print(f"🌙 FIN DEL DÍA {dia_actual}")
                print(f"{'='*70}")
                print(f"✅ Sobrevivientes: {len(simulacion.particulas)}")
                print(f"💀 Muertes: {muertes}")
                print(f"👶 Reproducciones: {reproducciones}")
                print(f"🍎 Comida restante: {entorno.comida_actual}")
                print(f"{'='*70}\n")
                
                # REESTABLECER COMIDA para el nuevo día
                entorno.reestablecer_comida()
                print(f"🔄 Comida reestablecida: {entorno.comida_actual} unidades en nuevas posiciones")
                
                # Preparar siguiente día
                dia_actual += 1
                paso_en_dia = 0
                simulacion.dia_actual = dia_actual
                
                for particula in simulacion.particulas:
                    particula.preparar_nuevo_dia()
            
            return [scatter_comida, titulo, contador_texto] + elementos_particulas
        
        # Calcular frames totales
        frames_totales = max_dias * pasos_por_dia * 2
        
        print(f"\n{'='*70}")
        print("🎬 INICIANDO SIMULACIÓN VISUAL EN TIEMPO REAL")
        print(f"{'='*70}")
        print(f"📐 Dimensiones: {entorno.ancho}x{entorno.alto}")
        print(f"🟢 Partículas iniciales: {len(simulacion.particulas)}")
        print(f"🍎 Comida inicial: {entorno.comida_total}")
        print(f"⏱️ Pasos por día: {pasos_por_dia}")
        print(f"📅 Días máximos: {max_dias}")
        print(f"⚡ Velocidad: {intervalo}ms por frame")
        print(f"{'='*70}")
        print("💡 Observa cómo las partículas se mueven, comen y sobreviven")
        print("💡 Los bordes VERDES son la CASA (zona segura)")
        print("💡 Los puntos NARANJAS son COMIDA")
        print("💡 La comida se RESTABLECE cada día en nuevas posiciones")
        print(f"{'='*70}\n")
        
        anim = FuncAnimation(fig, animate, init_func=init, 
                           frames=frames_totales,
                           interval=intervalo, blit=False, repeat=False)
        
        plt.tight_layout()
        plt.show()
        
        return anim
        """
        Ejecuta y visualiza la simulación en tiempo real.
        
        Args:
            simulacion (Simulacion): La simulación a ejecutar
            max_dias (int): Días máximos a simular
            intervalo (int): Milisegundos entre frames
        """
        entorno = simulacion.entorno
        pasos_por_dia = simulacion.pasos_por_dia
        
        fig, ax = plt.subplots(figsize=(16, 14))
        
        # Configurar límites
        ax.set_xlim(-1, entorno.ancho)
        ax.set_ylim(-1, entorno.alto)
        ax.set_aspect('equal')
        ax.set_facecolor('#f0f0f0')
        fig.patch.set_facecolor('white')
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        ax.invert_yaxis()
        
        # Dibujar casa (estático) - bordes verdes
        casa_color = '#90EE90'
        ax.add_patch(patches.Rectangle((0, 0), entorno.ancho - 1, 0.5, 
                                      color=casa_color, alpha=0.5, label='Casa', zorder=1))
        ax.add_patch(patches.Rectangle((0, entorno.alto - 1), entorno.ancho - 1, 0.5, 
                                      color=casa_color, alpha=0.5, zorder=1))
        ax.add_patch(patches.Rectangle((0, 0), 0.5, entorno.alto - 1, 
                                      color=casa_color, alpha=0.5, zorder=1))
        ax.add_patch(patches.Rectangle((entorno.ancho - 1, 0), 0.5, entorno.alto - 1, 
                                      color=casa_color, alpha=0.5, zorder=1))
        
        ax.set_xlabel('X', fontsize=12)
        ax.set_ylabel('Y', fontsize=12)
        
        # Título y contadores
        titulo = ax.text(0.5, 1.05, '', transform=ax.transAxes, 
                        fontsize=14, fontweight='bold', ha='center')
        
        contador_texto = ax.text(0.02, 0.98, '', transform=ax.transAxes,
                                fontsize=11, fontweight='bold', 
                                verticalalignment='top',
                                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9),
                                zorder=10)
        
        # Scatter para comida
        scatter_comida = ax.scatter([], [], c='orange', s=40, alpha=0.8, 
                                   marker='o', label='Comida', zorder=3, edgecolors='darkorange')
        
        ax.legend(loc='upper right', fontsize=10)
        
        # Variables de estado
        paso_global = 0
        dia_actual = 1
        paso_en_dia = 0
        elementos_particulas = []
        
        # Inicializar comida
        comida_inicial = set(entorno.posiciones_comida.copy())
        
        def init():
            # Mostrar comida inicial
            if comida_inicial:
                comida_x = [pos[0] for pos in comida_inicial]
                comida_y = [pos[1] for pos in comida_inicial]
                scatter_comida.set_offsets(np.column_stack([comida_x, comida_y]))
            
            titulo.set_text('Simulación de Población - Iniciando...')
            contador_texto.set_text(f'Partículas Vivas: {len(simulacion.particulas)}\nComida: {len(comida_inicial)}\nDía: 1')
            return [scatter_comida, titulo, contador_texto]
        
        def animate(frame):
            nonlocal paso_global, dia_actual, paso_en_dia, elementos_particulas
            
            # Limpiar elementos anteriores
            for elemento in elementos_particulas:
                elemento.remove()
            elementos_particulas.clear()
            
            # Si no hay partículas, detener
            if len(simulacion.particulas) == 0:
                titulo.set_text('Simulación Finalizada - Todas las partículas murieron')
                contador_texto.set_text(f'Día final: {dia_actual - 1}\nPartículas: 0\nComida: {entorno.comida_actual}')
                return [scatter_comida, titulo, contador_texto]
            
            # Si alcanzamos max_dias, detener
            if dia_actual > max_dias:
                titulo.set_text(f'Simulación Finalizada - Límite de {max_dias} días alcanzado')
                contador_texto.set_text(f'Día final: {dia_actual - 1}\nPartículas: {len(simulacion.particulas)}\nComida: {entorno.comida_actual}')
                return [scatter_comida, titulo, contador_texto]
            
            # Realizar un paso para cada partícula
            for particula in simulacion.particulas:
                particula.realizar_paso()
            
            paso_en_dia += 1
            
            # Actualizar visualización de comida
            if entorno.posiciones_comida:
                comida_x = [pos[0] for pos in entorno.posiciones_comida]
                comida_y = [pos[1] for pos in entorno.posiciones_comida]
                scatter_comida.set_offsets(np.column_stack([comida_x, comida_y]))
            else:
                scatter_comida.set_offsets(np.empty((0, 2)))
            
            # Dibujar partículas y sus caminos
            for particula in simulacion.particulas:
                # Dibujar camino completo
                if len(particula.camino) > 1:
                    xs = [pos[0] for pos in particula.camino]
                    ys = [pos[1] for pos in particula.camino]
                    linea, = ax.plot(xs, ys, '-', linewidth=2, 
                                   color=particula.color, alpha=0.5, zorder=2)
                    elementos_particulas.append(linea)
                
                # Dibujar posición actual
                x, y = particula.posicion_actual
                punto = ax.scatter([x], [y], c=[particula.color], 
                                 s=200, edgecolors='black', linewidths=2.5, 
                                 zorder=5, alpha=1.0)
                elementos_particulas.append(punto)
                
                # Mostrar ID
                texto = ax.text(x, y - 2, f'ID:{particula.id}', 
                              fontsize=9, ha='center', va='top', fontweight='bold',
                              bbox=dict(boxstyle='round,pad=0.3', 
                                      facecolor='white', alpha=0.8, edgecolor='black', linewidth=0.5),
                              zorder=6)
                elementos_particulas.append(texto)
                
                # Indicador de comida consumida
                if particula.comida_consumida > 0:
                    comida_text = ax.text(x, y + 2, f'🍎×{particula.comida_consumida}', 
                                        fontsize=8, ha='center', va='bottom',
                                        bbox=dict(boxstyle='round,pad=0.2', 
                                                facecolor='yellow', alpha=0.7),
                                        zorder=6)
                    elementos_particulas.append(comida_text)
            
            # Actualizar título
            progreso = (paso_en_dia / pasos_por_dia) * 100
            titulo.set_text(f'Simulación de Población - DÍA {dia_actual}\n' +
                          f'Paso {paso_en_dia}/{pasos_por_dia} ({progreso:.1f}%)')
            
            # Actualizar contador
            contador_texto.set_text(
                f'🟢 Partículas Vivas: {len(simulacion.particulas)}\n'
                f'🍎 Comida Restante: {entorno.comida_actual}\n'
                f'📅 Día: {dia_actual}\n'
                f'⏱️ Paso: {paso_en_dia}/{pasos_por_dia}'
            )
            
            # Verificar si terminó el día
            if paso_en_dia >= pasos_por_dia:
                # Evaluar fin del día
                sobrevivientes = []
                reproducciones = 0
                muertes = 0
                
                for particula in simulacion.particulas:
                    resultado = particula.evaluar_fin_dia()
                    
                    if resultado['sobrevive']:
                        sobrevivientes.append(particula)
                        
                        if resultado['reproduce']:
                            hijo = particula.crear_hijo(simulacion._obtener_nuevo_id())
                            sobrevivientes.append(hijo)
                            reproducciones += 1
                    else:
                        muertes += 1
                        particula.viva = False
                
                # Actualizar partículas
                simulacion.particulas = sobrevivientes
                
                # Guardar estadísticas
                estadisticas = {
                    'dia': dia_actual,
                    'particulas_finales': len(simulacion.particulas),
                    'muertes': muertes,
                    'reproducciones': reproducciones,
                    'comida_restante': entorno.comida_actual
                }
                simulacion.historial_dias.append(estadisticas)
                
                print(f"\n{'='*60}")
                print(f"FIN DEL DÍA {dia_actual}")
                print(f"{'='*60}")
                print(f"Partículas vivas: {len(simulacion.particulas)}")
                print(f"Muertes: {muertes}")
                print(f"Reproducciones: {reproducciones}")
                print(f"Comida restante: {entorno.comida_actual}")
                print(f"{'='*60}\n")
                
                # Preparar siguiente día
                dia_actual += 1
                paso_en_dia = 0
                simulacion.dia_actual = dia_actual
                
                for particula in simulacion.particulas:
                    particula.preparar_nuevo_dia()
            
            return [scatter_comida, titulo, contador_texto] + elementos_particulas
        
        # Calcular frames totales aproximados
        frames_totales = max_dias * pasos_por_dia
        
        print(f"\n{'='*70}")
        print("🎬 INICIANDO SIMULACIÓN VISUAL")
        print(f"{'='*70}")
        print(f"Dimensiones: {entorno.ancho}x{entorno.alto}")
        print(f"Partículas iniciales: {len(simulacion.particulas)}")
        print(f"Comida inicial: {entorno.comida_total}")
        print(f"Pasos por día: {pasos_por_dia}")
        print(f"Días máximos: {max_dias}")
        print(f"{'='*70}\n")
        
        anim = FuncAnimation(fig, animate, init_func=init, 
                           frames=frames_totales,
                           interval=intervalo, blit=False, repeat=False)
        
        plt.tight_layout()
        plt.show()
        
        return anim
    
    @staticmethod
    def visualizar_dia_estatico(simulacion, mostrar_comida=True):
        """
        Visualiza el estado actual de un día de forma estática.
        
        Args:
            simulacion (Simulacion): La simulación a visualizar
            mostrar_comida (bool): Si True, muestra la comida en el mapa
        """
        entorno = simulacion.entorno
        particulas = simulacion.particulas
        
        fig, ax = plt.subplots(figsize=(14, 14))
        
        # Configurar límites
        ax.set_xlim(-1, entorno.ancho)
        ax.set_ylim(-1, entorno.alto)
        ax.set_aspect('equal')
        
        # Fondo
        ax.set_facecolor('#f0f0f0')
        fig.patch.set_facecolor('white')
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        
        # Dibujar área de casa (bordes)
        casa_color = '#90EE90'
        # Borde superior
        ax.add_patch(patches.Rectangle((0, 0), entorno.ancho - 1, 0.5, 
                                      color=casa_color, alpha=0.5, label='Casa'))
        # Borde inferior
        ax.add_patch(patches.Rectangle((0, entorno.alto - 1), entorno.ancho - 1, 0.5, 
                                      color=casa_color, alpha=0.5))
        # Borde izquierdo
        ax.add_patch(patches.Rectangle((0, 0), 0.5, entorno.alto - 1, 
                                      color=casa_color, alpha=0.5))
        # Borde derecho
        ax.add_patch(patches.Rectangle((entorno.ancho - 1, 0), 0.5, entorno.alto - 1, 
                                      color=casa_color, alpha=0.5))
        
        # Dibujar comida
        if mostrar_comida and len(entorno.posiciones_comida) > 0:
            comida_x = [pos[0] for pos in entorno.posiciones_comida]
            comida_y = [pos[1] for pos in entorno.posiciones_comida]
            ax.scatter(comida_x, comida_y, c='orange', s=20, alpha=0.6, 
                      marker='o', label='Comida')
        
        # Dibujar caminos de partículas
        for particula in particulas:
            if len(particula.camino) > 1:
                xs = [pos[0] for pos in particula.camino]
                ys = [pos[1] for pos in particula.camino]
                ax.plot(xs, ys, '-', linewidth=1.5, color=particula.color, alpha=0.6)
        
        # Dibujar partículas
        for particula in particulas:
            x, y = particula.posicion_actual
            ax.scatter(x, y, c=[particula.color], s=100, 
                      edgecolors='black', linewidths=1.5, zorder=5)
            
            # Mostrar ID de partícula
            ax.text(x, y - 1, f'ID:{particula.id}', 
                   fontsize=8, ha='center', va='top')
        
        # Título con información
        ax.set_title(f'Simulación de Población - Día {simulacion.dia_actual}\n' +
                    f'Partículas Vivas: {len(particulas)} | ' +
                    f'Comida Restante: {entorno.comida_actual}',
                    fontsize=14, fontweight='bold', pad=20)
        
        ax.set_xlabel('X', fontsize=12)
        ax.set_ylabel('Y', fontsize=12)
        ax.legend(loc='upper right')
        ax.invert_yaxis()
        
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def visualizar_simulacion_animada(entorno, todas_particulas_dias, historial, intervalo=50):
        """
        Crea una animación completa de toda la simulación día por día.
        
        Args:
            entorno (Entorno): El entorno de la simulación
            todas_particulas_dias (list): Lista de listas con partículas por día
            historial (list): Historial de estadísticas
            intervalo (int): Milisegundos entre frames
        """
        fig, ax = plt.subplots(figsize=(16, 14))
        
        # Configurar límites
        ax.set_xlim(-1, entorno.ancho)
        ax.set_ylim(-1, entorno.alto)
        ax.set_aspect('equal')
        ax.set_facecolor('#f0f0f0')
        fig.patch.set_facecolor('white')
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        ax.invert_yaxis()
        
        # Dibujar casa (estático)
        casa_color = '#90EE90'
        ax.add_patch(patches.Rectangle((0, 0), entorno.ancho - 1, 0.5, 
                                      color=casa_color, alpha=0.5, label='Casa'))
        ax.add_patch(patches.Rectangle((0, entorno.alto - 1), entorno.ancho - 1, 0.5, 
                                      color=casa_color, alpha=0.5))
        ax.add_patch(patches.Rectangle((0, 0), 0.5, entorno.alto - 1, 
                                      color=casa_color, alpha=0.5))
        ax.add_patch(patches.Rectangle((entorno.ancho - 1, 0), 0.5, entorno.alto - 1, 
                                      color=casa_color, alpha=0.5))
        
        ax.set_xlabel('X', fontsize=12)
        ax.set_ylabel('Y', fontsize=12)
        
        # Título y contador
        titulo = ax.text(0.5, 1.05, '', transform=ax.transAxes, 
                        fontsize=14, fontweight='bold', ha='center')
        
        contador_texto = ax.text(0.02, 0.98, '', transform=ax.transAxes,
                                fontsize=12, fontweight='bold', 
                                verticalalignment='top',
                                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Elementos para comida
        scatter_comida = ax.scatter([], [], c='orange', s=30, alpha=0.7, 
                                   marker='o', label='Comida', zorder=3)
        
        # Elementos dinámicos para partículas
        elementos_particulas = []
        
        ax.legend(loc='upper right')
        
        def init():
            scatter_comida.set_offsets(np.empty((0, 2)))
            titulo.set_text('')
            contador_texto.set_text('')
            return [scatter_comida, titulo, contador_texto]
        
        def animate(frame):
            # Limpiar elementos anteriores de partículas
            for elemento in elementos_particulas:
                elemento.remove()
            elementos_particulas.clear()
            
            # Determinar día y paso actual
            dia_idx = 0
            paso_acumulado = 0
            
            for i, particulas_dia in enumerate(todas_particulas_dias):
                pasos_en_dia = max([len(p.camino) for p in particulas_dia]) if particulas_dia else 1
                if frame < paso_acumulado + pasos_en_dia:
                    dia_idx = i
                    paso_en_dia = frame - paso_acumulado
                    break
                paso_acumulado += pasos_en_dia
            else:
                # Último frame
                dia_idx = len(todas_particulas_dias) - 1
                paso_en_dia = max([len(p.camino) for p in todas_particulas_dias[-1]]) - 1 if todas_particulas_dias[-1] else 0
            
            particulas_dia = todas_particulas_dias[dia_idx]
            dia_actual = dia_idx + 1
            
            # Obtener posiciones de comida actuales para este frame
            comida_x = []
            comida_y = []
            
            # Simular qué comida ya fue consumida hasta este punto
            comida_restante = set(entorno.posiciones_comida)  # Copiar comida inicial
            
            for i in range(dia_idx):
                # Días anteriores: toda la comida consumida
                for p in todas_particulas_dias[i]:
                    for pos in p.camino:
                        if pos in comida_restante:
                            comida_restante.discard(pos)
            
            # Día actual: comida consumida hasta el paso actual
            for p in particulas_dia:
                if paso_en_dia < len(p.camino):
                    for pos in p.camino[:paso_en_dia+1]:
                        if pos in comida_restante:
                            comida_restante.discard(pos)
            
            if comida_restante:
                comida_x = [pos[0] for pos in comida_restante]
                comida_y = [pos[1] for pos in comida_restante]
            
            scatter_comida.set_offsets(np.column_stack([comida_x, comida_y]) if comida_x else np.empty((0, 2)))
            
            # Dibujar partículas y sus caminos
            particulas_vivas = 0
            for particula in particulas_dia:
                if paso_en_dia < len(particula.camino):
                    # Dibujar camino
                    camino_actual = particula.camino[:paso_en_dia+1]
                    xs = [pos[0] for pos in camino_actual]
                    ys = [pos[1] for pos in camino_actual]
                    
                    if len(xs) > 1:
                        linea, = ax.plot(xs, ys, '-', linewidth=1.5, 
                                       color=particula.color, alpha=0.6)
                        elementos_particulas.append(linea)
                    
                    # Dibujar posición actual
                    if len(xs) > 0:
                        punto = ax.scatter([xs[-1]], [ys[-1]], c=[particula.color], 
                                         s=150, edgecolors='black', linewidths=2, zorder=5)
                        elementos_particulas.append(punto)
                        
                        # ID de partícula
                        texto = ax.text(xs[-1], ys[-1] - 1.5, f'ID:{particula.id}', 
                                      fontsize=8, ha='center', va='top',
                                      bbox=dict(boxstyle='round,pad=0.3', 
                                              facecolor='white', alpha=0.7, edgecolor='none'))
                        elementos_particulas.append(texto)
                        particulas_vivas += 1
            
            # Actualizar título
            pasos_totales = max([len(p.camino) for p in particulas_dia]) if particulas_dia else 1
            progreso = (paso_en_dia / pasos_totales * 100) if pasos_totales > 0 else 0
            
            titulo.set_text(f'Simulación de Población - Día {dia_actual}\n' +
                          f'Paso {paso_en_dia}/{pasos_totales} ({progreso:.1f}%)')
            
            # Actualizar contador
            if dia_idx < len(historial):
                stats = historial[dia_idx]
                contador_texto.set_text(
                    f'Partículas Vivas: {particulas_vivas}\n'
                    f'Comida Restante: {len(comida_restante)}\n'
                    f'Día {dia_actual}/{len(todas_particulas_dias)}'
                )
            
            return [scatter_comida, titulo, contador_texto] + elementos_particulas
        
        # Calcular frames totales
        frames_totales = sum([max([len(p.camino) for p in particulas]) if particulas else 1 
                             for particulas in todas_particulas_dias])
        
        anim = FuncAnimation(fig, animate, init_func=init, 
                           frames=frames_totales,
                           interval=intervalo, blit=False, repeat=False)
        
        plt.tight_layout()
        plt.show()
        
        return anim
    
    @staticmethod
    def graficar_estadisticas(historial):
        """
        Crea gráficos de las estadísticas de la simulación.
        
        Args:
            historial (list): Historial de días de la simulación
        """
        if not historial:
            print("No hay datos para graficar")
            return
        
        dias = [d['dia'] for d in historial]
        particulas = [d['particulas_finales'] for d in historial]
        muertes = [d['muertes'] for d in historial]
        reproducciones = [d['reproducciones'] for d in historial]
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.patch.set_facecolor('white')
        
        # Gráfico 1: Población por día
        ax1.plot(dias, particulas, 'b-o', linewidth=2, markersize=6)
        ax1.set_xlabel('Día', fontsize=12)
        ax1.set_ylabel('Número de Partículas', fontsize=12)
        ax1.set_title('Evolución de la Población', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Gráfico 2: Muertes y Reproducciones
        ax2.plot(dias, muertes, 'r-o', label='Muertes', linewidth=2, markersize=6)
        ax2.plot(dias, reproducciones, 'g-o', label='Reproducciones', linewidth=2, markersize=6)
        ax2.set_xlabel('Día', fontsize=12)
        ax2.set_ylabel('Cantidad', fontsize=12)
        ax2.set_title('Muertes y Reproducciones por Día', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Gráfico 3: Comida Restante
        comida_restante = [d['comida_restante'] for d in historial]
        ax3.plot(dias, comida_restante, 'orange', linewidth=2, marker='o', markersize=6)
        ax3.set_xlabel('Día', fontsize=12)
        ax3.set_ylabel('Comida Restante', fontsize=12)
        ax3.set_title('Comida Disponible por Día', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        
        # Gráfico 4: Resumen
        ax4.axis('off')
        
        total_dias = len(historial)
        particulas_final = historial[-1]['particulas_finales']
        total_muertes = sum(muertes)
        total_reproducciones = sum(reproducciones)
        
        resumen = f"""
        RESUMEN DE LA SIMULACIÓN
        
        Días simulados: {total_dias}
        
        Partículas finales: {particulas_final}
        Total de muertes: {total_muertes}
        Total de reproducciones: {total_reproducciones}
        
        Estado final: {'POBLACIÓN SOBREVIVIÓ' if particulas_final > 0 else 'EXTINCIÓN'}
        """
        
        ax4.text(0.5, 0.5, resumen, transform=ax4.transAxes,
                fontsize=14, verticalalignment='center', horizontalalignment='center',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5),
                family='monospace')
        
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def mostrar_resumen_final(historial):
        """
        Muestra un resumen final de la simulación.
        
        Args:
            historial (list): Historial de la simulación
        """
        if not historial:
            print("No hay datos para mostrar")
            return
        
        print(f"\n{'='*70}")
        print("RESUMEN FINAL DE LA SIMULACIÓN")
        print(f"{'='*70}")
        
        dias_totales = len(historial)
        particulas_inicial = historial[0]['particulas_iniciales']
        particulas_final = historial[-1]['particulas_finales']
        
        total_muertes = sum([d['muertes'] for d in historial])
        total_reproducciones = sum([d['reproducciones'] for d in historial])
        total_comida = sum([d['comida_consumida'] for d in historial])
        
        print(f"Días simulados: {dias_totales}")
        print(f"Partículas iniciales: {particulas_inicial}")
        print(f"Partículas finales: {particulas_final}")
        print(f"Total de muertes: {total_muertes}")
        print(f"Total de reproducciones: {total_reproducciones}")
        print(f"Total de comida consumida: {total_comida}")
        
        if particulas_final > 0:
            print(f"\nLa población sobrevivió {dias_totales} días")
        else:
            print(f"\nLa población se extinguió en el día {dias_totales}")
        
        print(f"{'='*70}\n")