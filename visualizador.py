import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider
import numpy as np

class Visualizador:
    """
    Clase para visualizar la simulación de población en tiempo real.
    """
    
    @staticmethod
    def simular_visualmente(simulacion):
        """
        Ejecuta y visualiza la simulación en tiempo real hasta que todas las partículas mueran.
        
        Args:
            simulacion (Simulacion): La simulación a ejecutar
        """
        entorno = simulacion.entorno
        pasos_por_dia = simulacion.pasos_por_dia
        
        # Crear figura más grande con espacio para el slider
        fig = plt.figure(figsize=(18, 17))
        
        # Crear el eje principal para la simulación
        ax = plt.subplot2grid((20, 1), (0, 0), rowspan=18)
        
        # Crear el eje para el slider de velocidad
        ax_slider = plt.subplot2grid((20, 1), (19, 0))
        
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
        ax.add_patch(patches.Rectangle((0, 0), entorno.ancho, grosor_casa, 
                                      color=casa_color, alpha=0.7, zorder=1))
        ax.add_patch(patches.Rectangle((0, entorno.alto - grosor_casa), entorno.ancho, grosor_casa, 
                                      color=casa_color, alpha=0.7, zorder=1))
        ax.add_patch(patches.Rectangle((0, 0), grosor_casa, entorno.alto, 
                                      color=casa_color, alpha=0.7, zorder=1))
        ax.add_patch(patches.Rectangle((entorno.ancho - grosor_casa, 0), grosor_casa, entorno.alto, 
                                      color=casa_color, alpha=0.7, zorder=1))
        
        ax.set_xlabel('X', fontsize=14, fontweight='bold')
        ax.set_ylabel('Y', fontsize=14, fontweight='bold')
        
        # Título principal
        titulo = ax.text(0.5, 1.06, '', transform=ax.transAxes, 
                        fontsize=16, fontweight='bold', ha='center',
                        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        # Panel de información
        contador_texto = ax.text(0.02, 0.98, '', transform=ax.transAxes,
                                fontsize=13, fontweight='bold', 
                                verticalalignment='top',
                                bbox=dict(boxstyle='round,pad=0.8', 
                                        facecolor='white', alpha=0.95,
                                        edgecolor='black', linewidth=2),
                                zorder=10,
                                family='monospace')
        
        # Scatter para comida
        scatter_comida = ax.scatter([], [], c='#ff6b35', s=80, alpha=0.9, 
                                   marker='o', zorder=3, 
                                   edgecolors='#c44616', linewidths=1.5)
        
        # Leyenda compacta
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor='white', 
                   markersize=8, label='Normal', markeredgecolor='black', linewidth=1.5),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='red', 
                   markersize=8, label='Velocidad', markeredgecolor='black', linewidth=1.5),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='green', 
                   markersize=8, label='Prioridad', markeredgecolor='black', linewidth=1.5),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='black', 
                   markersize=8, label='Depredador', markeredgecolor='black', linewidth=1.5),
            Line2D([0], [0], marker='X', color='red', markersize=8, 
                   label='Muerto', linewidth=0),
        ]
        ax.legend(handles=legend_elements, loc='lower right', fontsize=8, 
                 framealpha=0.85, ncol=5, borderpad=0.3, labelspacing=0.2,
                 columnspacing=0.5, handletextpad=0.3)
        
        # SLIDER DE VELOCIDAD con sistema que SÍ funciona
        # Número de frames a saltar (skip)
        frame_skip = {'valor': 0}  # 0 = no saltar, 1 = saltar 1 frame, etc.
        
        velocidad_slider = Slider(
            ax=ax_slider,
            label='Velocidad (derecha = mas rapido)',
            valmin=0,
            valmax=10,
            valinit=0,
            valstep=1,
            color='lightblue'
        )
        
        def update_speed(val):
            frame_skip['valor'] = int(val)
        
        velocidad_slider.on_changed(update_speed)
        
        # Variables de estado
        paso_en_dia = [0]
        dia_actual = [1]
        elementos_particulas = []
        simulacion_activa = [True]
        particulas_muertas_depredador = []
        frame_counter = [0]
        
        # Variable para el hover
        hover_annotation = ax.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",
                                      bbox=dict(boxstyle="round", fc="white", alpha=0.95, 
                                               edgecolor='black', linewidth=2),
                                      fontsize=9, fontweight='bold', zorder=100, visible=False)
        
        def on_mouse_move(event):
            """Maneja el movimiento del mouse para mostrar IDs"""
            if event.inaxes != ax:
                hover_annotation.set_visible(False)
                fig.canvas.draw_idle()
                return
            
            if not simulacion.particulas and not simulacion.depredadores:
                hover_annotation.set_visible(False)
                fig.canvas.draw_idle()
                return
            
            todas_entidades = list(simulacion.particulas) + list(simulacion.depredadores)
            for entidad in todas_entidades:
                x, y = entidad.posicion_actual
                if event.xdata is not None and event.ydata is not None:
                    dist = ((event.xdata - x)**2 + (event.ydata - y)**2)**0.5
                    if dist < 2.0:
                        if entidad.es_depredador:
                            info_text = f"Depredador #{entidad.id}"
                        else:
                            tipo = ""
                            if entidad.mutacion == 'velocidad':
                                tipo = " (Velocidad)"
                            elif entidad.mutacion == 'prioridad':
                                tipo = " (Prioridad)"
                            info_text = f"#{entidad.id}{tipo}\nComida: {entidad.comida_consumida}"
                            if entidad.mordidas_recibidas > 0:
                                info_text += f"\nMordidas: {entidad.mordidas_recibidas}"
                        
                        hover_annotation.xy = (x, y)
                        hover_annotation.set_text(info_text)
                        hover_annotation.set_visible(True)
                        fig.canvas.draw_idle()
                        return
            
            hover_annotation.set_visible(False)
            fig.canvas.draw_idle()
        
        fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)
        
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
            nonlocal elementos_particulas, particulas_muertas_depredador
            
            if not simulacion_activa[0]:
                return [scatter_comida, titulo, contador_texto]
            
            # Sistema de skip frames para velocidad
            skip = frame_skip['valor']
            
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
                    f'Dia final: {dia_actual[0] - 1}\n'
                    f'Particulas: 0\n'
                    f'Estado: EXTINCION'
                )
                simulacion_activa[0] = False
                print(f"\n{'='*70}")
                print("SIMULACION TERMINADA - EXTINCION TOTAL")
                print(f"{'='*70}\n")
                
                # Dibujar partículas muertas
                for pos, particula in particulas_muertas_depredador:
                    x, y = pos
                    punto = ax.scatter([x], [y], c=[particula.color], 
                                     s=300, edgecolors='gray', linewidths=2, 
                                     zorder=4, alpha=0.3)
                    elementos_particulas.append(punto)
                    
                    x_marca = ax.scatter([x], [y], c='red', s=600, marker='X', 
                                        linewidths=5, zorder=9, alpha=1.0, edgecolors='darkred')
                    elementos_particulas.append(x_marca)
                
                return [scatter_comida, titulo, contador_texto, hover_annotation] + elementos_particulas
            
            # Realizar múltiples pasos según la velocidad
            pasos_a_realizar = 1 + skip
            
            for _ in range(pasos_a_realizar):
                if len(simulacion.particulas) == 0:
                    break
                
                # Guardar estado anterior
                particulas_vivas_antes = {p.id: (p, p.posicion_actual) for p in simulacion.particulas if p.viva}
                
                # Realizar pasos
                for particula in simulacion.particulas:
                    particula.realizar_paso(depredadores=simulacion.depredadores)
                
                for depredador in simulacion.depredadores:
                    depredador.realizar_paso()
                
                # Procesar ataques
                simulacion._procesar_ataques_depredadores()
                
                # Detectar muertes
                for pid, (particula, pos_anterior) in particulas_vivas_antes.items():
                    if not particula.viva:
                        particulas_muertas_depredador.append((particula.posicion_actual, particula))
                        print(f"  Particula #{particula.id} murio por depredador")
                
                paso_en_dia[0] += 1
                
                # Verificar fin de día
                if paso_en_dia[0] >= pasos_por_dia:
                    muertes_depredador = simulacion._procesar_ataques_depredadores()
                    num_depredadores = len(simulacion.depredadores)
                    simulacion.depredadores = []
                    particulas_muertas_depredador.clear()
                    
                    sobrevivientes = []
                    reproducciones = 0
                    muertes = 0
                    mutaciones_velocidad = 0
                    mutaciones_prioridad = 0
                    
                    for particula in simulacion.particulas:
                        if not particula.viva:
                            muertes += 1
                            continue
                        
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
                                
                                if resultado['mutacion_hijo'] == 'velocidad':
                                    mutaciones_velocidad += 1
                                elif resultado['mutacion_hijo'] == 'prioridad':
                                    mutaciones_prioridad += 1
                        else:
                            muertes += 1
                            particula.viva = False
                    
                    simulacion.particulas = sobrevivientes
                    
                    normales = sum(1 for p in simulacion.particulas if p.mutacion == 'ninguna')
                    velocidad_count = sum(1 for p in simulacion.particulas if p.mutacion == 'velocidad')
                    prioridad = sum(1 for p in simulacion.particulas if p.mutacion == 'prioridad')
                    
                    estadisticas = {
                        'dia': dia_actual[0],
                        'particulas_finales': len(simulacion.particulas),
                        'muertes': muertes,
                        'reproducciones': reproducciones,
                        'comida_restante': entorno.comida_actual,
                        'comida_inicial': entorno.comida_total,
                        'porcentaje_comida': entorno.porcentaje_comida_actual,
                        'tipo_dia': entorno.obtener_info_comida()['tipo_dia'],
                        'normales': normales,
                        'velocidad': velocidad_count,
                        'prioridad': prioridad,
                        'nuevas_mutaciones_velocidad': mutaciones_velocidad,
                        'nuevas_mutaciones_prioridad': mutaciones_prioridad,
                        'depredadores_aparecidos': num_depredadores,
                        'muertes_por_depredador': muertes_depredador
                    }
                    simulacion.historial_dias.append(estadisticas)
                    
                    print(f"\n{'='*70}")
                    print(f"FIN DEL DIA {dia_actual[0]}")
                    print(f"{'='*70}")
                    print(f"Sobrevivientes: {len(simulacion.particulas)}")
                    print(f"Muertes: {muertes}")
                    if muertes_depredador > 0:
                        print(f"  - Por depredadores: {muertes_depredador}")
                    print(f"Reproducciones: {reproducciones}")
                    print(f"{'='*70}\n")
                    
                    entorno.reestablecer_comida()
                    info_comida = entorno.obtener_info_comida()
                    print(f"Comida reestablecida: {entorno.comida_actual} unidades")
                    
                    if simulacion._generar_depredadores():
                        print(f"APARECEN {len(simulacion.depredadores)} DEPREDADOR(ES)")
                    print()
                    
                    dia_actual[0] += 1
                    paso_en_dia[0] = 0
                    simulacion.dia_actual = dia_actual[0]
                    
                    for particula in simulacion.particulas:
                        particula.preparar_nuevo_dia()
                    
                    break  # Salir del bucle de pasos múltiples
            
            # Actualizar comida
            if entorno.posiciones_comida:
                comida_x = [pos[0] for pos in entorno.posiciones_comida]
                comida_y = [pos[1] for pos in entorno.posiciones_comida]
                scatter_comida.set_offsets(np.column_stack([comida_x, comida_y]))
            else:
                scatter_comida.set_offsets(np.empty((0, 2)))
            
            # Dibujar partículas muertas
            for pos, particula in particulas_muertas_depredador:
                x, y = pos
                punto = ax.scatter([x], [y], c=[particula.color], 
                                 s=300, edgecolors='gray', linewidths=2, 
                                 zorder=4, alpha=0.3)
                elementos_particulas.append(punto)
                
                x_marca = ax.scatter([x], [y], c='red', s=600, marker='X', 
                                    linewidths=5, zorder=9, alpha=1.0, edgecolors='darkred')
                elementos_particulas.append(x_marca)
            
            # Dibujar partículas vivas
            todas_entidades = list(simulacion.particulas) + list(simulacion.depredadores)
            
            for entidad in todas_entidades:
                if len(entidad.camino) > 1:
                    xs = [pos[0] for pos in entidad.camino]
                    ys = [pos[1] for pos in entidad.camino]
                    linea, = ax.plot(xs, ys, '-', linewidth=2.5, 
                                   color=entidad.color, alpha=0.6, zorder=2)
                    elementos_particulas.append(linea)
                
                x, y = entidad.posicion_actual
                tamano = 400 if entidad.es_depredador else 300
                
                color_actual = entidad.color
                borde_color = 'black'
                borde_grosor = 3
                
                if not entidad.es_depredador and entidad.mutacion == 'prioridad' and entidad.mordidas_recibidas == 1:
                    color_actual = (0.0, 0.5, 0.0)
                    borde_color = 'red'
                    borde_grosor = 6
                
                punto = ax.scatter([x], [y], c=[color_actual], 
                                 s=tamano, edgecolors=borde_color, linewidths=borde_grosor, 
                                 zorder=5, alpha=1.0)
                elementos_particulas.append(punto)
                
                if not entidad.es_depredador and entidad.comida_consumida > 0:
                    comida_text = ax.text(x, y, f'{entidad.comida_consumida}', 
                                        fontsize=10, ha='center', va='center',
                                        color='white', fontweight='bold',
                                        zorder=7,
                                        bbox=dict(boxstyle='circle,pad=0.1', 
                                                facecolor='black', alpha=0.7, edgecolor='none'))
                    elementos_particulas.append(comida_text)
                
                if not entidad.es_depredador and entidad.mordidas_recibidas > 0:
                    mordida_text = ax.text(x + 1.2, y - 1.2, f'!{entidad.mordidas_recibidas}', 
                                          fontsize=11, ha='center', va='center',
                                          color='red', fontweight='bold', zorder=8)
                    elementos_particulas.append(mordida_text)
            
            # Actualizar título
            progreso = (paso_en_dia[0] / pasos_por_dia) * 100
            titulo.set_text(f'Simulacion de Poblacion - DIA {dia_actual[0]} - {progreso:.1f}% completado')
            
            contador_texto.set_text(
                f'Particulas: {len(simulacion.particulas)}\n'
                f'Depredadores: {len(simulacion.depredadores)}\n'
                f'Comida: {len(entorno.posiciones_comida)}\n'
                f'Dia: {dia_actual[0]}\n'
                f'Paso: {paso_en_dia[0]}/{pasos_por_dia}\n'
                f'Velocidad: x{1+skip}'
            )
            
            return [scatter_comida, titulo, contador_texto, hover_annotation] + elementos_particulas
        
        print(f"\n{'='*70}")
        print("INICIANDO SIMULACION VISUAL")
        print(f"{'='*70}")
        print("Usa el SLIDER para cambiar la velocidad:")
        print("  - 0 = Normal (1 paso por frame)")
        print("  - 5 = Rapido (6 pasos por frame)")
        print("  - 10 = Muy rapido (11 pasos por frame)")
        print(f"{'='*70}\n")
        
        # Crear animación
        anim = FuncAnimation(
            fig, 
            animate, 
            init_func=init,
            frames=100000,
            interval=30,  # Intervalo fijo de 30ms
            blit=False,
            repeat=False,
            cache_frame_data=False
        )
        
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
        
        normales = [d.get('normales', 0) for d in historial]
        velocidad = [d.get('velocidad', 0) for d in historial]
        prioridad = [d.get('prioridad', 0) for d in historial]
        
        muertes_depredador = [d.get('muertes_por_depredador', 0) for d in historial]
        
        # Crear figura con mejor espaciado
        fig = plt.figure(figsize=(20, 11))
        fig.patch.set_facecolor('white')
        
        # Espaciado mejorado - SIN título general
        plt.subplots_adjust(hspace=0.4, wspace=0.35, top=0.96, bottom=0.08, left=0.08, right=0.96)
        
        # Gráfico 1: Población
        ax1 = plt.subplot(2, 3, 1)
        ax1.plot(dias, particulas, 'b-o', linewidth=2.5, markersize=7)
        ax1.set_xlabel('Dia', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Particulas', fontsize=12, fontweight='bold')
        ax1.set_title('Evolucion de la Poblacion', fontsize=13, fontweight='bold', pad=15)
        ax1.grid(True, alpha=0.3)
        
        # Gráfico 2: Muertes y Reproducciones
        ax2 = plt.subplot(2, 3, 2)
        ax2.plot(dias, muertes, 'r-o', label='Muertes', linewidth=2.5, markersize=7)
        ax2.plot(dias, reproducciones, 'g-o', label='Reproducciones', linewidth=2.5, markersize=7)
        ax2.set_xlabel('Dia', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Cantidad', fontsize=12, fontweight='bold')
        ax2.set_title('Muertes y Reproducciones', fontsize=13, fontweight='bold', pad=15)
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        # Gráfico 3: Distribución de Tipos
        ax3 = plt.subplot(2, 3, 3)
        ax3.plot(dias, normales, 'gray', linewidth=2.5, marker='o', markersize=7, label='Normales')
        ax3.plot(dias, velocidad, 'red', linewidth=2.5, marker='o', markersize=7, label='Velocidad')
        ax3.plot(dias, prioridad, 'green', linewidth=2.5, marker='o', markersize=7, label='Prioridad')
        ax3.set_xlabel('Dia', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Cantidad', fontsize=12, fontweight='bold')
        ax3.set_title('Distribucion de Tipos', fontsize=13, fontweight='bold', pad=15)
        ax3.legend(fontsize=10)
        ax3.grid(True, alpha=0.3)
        
        # Gráfico 4: Comida
        comida_restante = [d['comida_restante'] for d in historial]
        ax4 = plt.subplot(2, 3, 4)
        ax4.plot(dias, comida_restante, 'orange', linewidth=2.5, marker='o', markersize=7)
        ax4.set_xlabel('Dia', fontsize=12, fontweight='bold')
        ax4.set_ylabel('Comida', fontsize=12, fontweight='bold')
        ax4.set_title('Comida Restante al Final del Dia', fontsize=13, fontweight='bold', pad=15)
        ax4.grid(True, alpha=0.3)
        
        # Gráfico 5: MUERTES POR DEPREDADORES
        ax5 = plt.subplot(2, 3, 5)
        ax5.bar(dias, muertes_depredador, color='darkred', alpha=0.8, edgecolor='black', linewidth=1.5)
        ax5.set_xlabel('Dia', fontsize=12, fontweight='bold')
        ax5.set_ylabel('Muertes', fontsize=12, fontweight='bold')
        ax5.set_title('Muertes Causadas por Depredadores', fontsize=13, fontweight='bold', pad=15)
        ax5.grid(True, alpha=0.3, axis='y')
        
        if len(muertes_depredador) > 1 and sum(muertes_depredador) > 0:
            ax5.plot(dias, muertes_depredador, 'r-', linewidth=2, alpha=0.6, label='Tendencia')
            ax5.legend(fontsize=10)
        
        # Gráfico 6: Resumen (SIN EMOJIS)
        ax6 = plt.subplot(2, 3, 6)
        ax6.axis('off')
        
        total_dias = len(historial)
        particulas_final = historial[-1]['particulas_finales']
        total_muertes = sum(muertes)
        total_reproducciones = sum(reproducciones)
        total_muertes_depredador = sum(muertes_depredador)
        
        if particulas_final > 0:
            pct_normales = (normales[-1] / particulas_final * 100)
            pct_velocidad = (velocidad[-1] / particulas_final * 100)
            pct_prioridad = (prioridad[-1] / particulas_final * 100)
        else:
            pct_normales = pct_velocidad = pct_prioridad = 0
        
        # RESUMEN SIN EMOJIS
        resumen = f"""
RESUMEN GENERAL

Dias simulados: {total_dias}

POBLACION:
  Finales: {particulas_final}
  Muertes totales: {total_muertes}
  Reproducciones: {total_reproducciones}

DISTRIBUCION FINAL:
  Normales: {normales[-1] if normales else 0} ({pct_normales:.1f}%)
  Velocidad: {velocidad[-1] if velocidad else 0} ({pct_velocidad:.1f}%)
  Prioridad: {prioridad[-1] if prioridad else 0} ({pct_prioridad:.1f}%)

DEPREDADORES:
  Muertes causadas: {total_muertes_depredador}
  Impacto: {(total_muertes_depredador/total_muertes*100) if total_muertes > 0 else 0:.1f}%

{'POBLACION SOBREVIVIO' if particulas_final > 0 else 'EXTINCION TOTAL'}
        """
        
        ax6.text(0.5, 0.5, resumen, transform=ax6.transAxes,
                fontsize=11, verticalalignment='center', horizontalalignment='center',
                bbox=dict(boxstyle='round,pad=1.2', facecolor='lightblue', 
                         alpha=0.8, edgecolor='darkblue', linewidth=2),
                family='monospace', fontweight='bold')
        
        # SIN título general (eliminado plt.suptitle)
        
        plt.show()
    
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
        
        ax.set_xlim(-1, entorno.ancho)
        ax.set_ylim(-1, entorno.alto)
        ax.set_aspect('equal')
        ax.set_facecolor('#f0f0f0')
        fig.patch.set_facecolor('white')
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        
        casa_color = '#90EE90'
        ax.add_patch(patches.Rectangle((0, 0), entorno.ancho - 1, 0.5, 
                                      color=casa_color, alpha=0.5, label='Casa'))
        ax.add_patch(patches.Rectangle((0, entorno.alto - 1), entorno.ancho - 1, 0.5, 
                                      color=casa_color, alpha=0.5))
        ax.add_patch(patches.Rectangle((0, 0), 0.5, entorno.alto - 1, 
                                      color=casa_color, alpha=0.5))
        ax.add_patch(patches.Rectangle((entorno.ancho - 1, 0), 0.5, entorno.alto - 1, 
                                      color=casa_color, alpha=0.5))
        
        if mostrar_comida and len(entorno.posiciones_comida) > 0:
            comida_x = [pos[0] for pos in entorno.posiciones_comida]
            comida_y = [pos[1] for pos in entorno.posiciones_comida]
            ax.scatter(comida_x, comida_y, c='orange', s=20, alpha=0.6, 
                      marker='o', label='Comida')
        
        for particula in particulas:
            if len(particula.camino) > 1:
                xs = [pos[0] for pos in particula.camino]
                ys = [pos[1] for pos in particula.camino]
                ax.plot(xs, ys, '-', linewidth=1.5, color=particula.color, alpha=0.6)
        
        for particula in particulas:
            x, y = particula.posicion_actual
            ax.scatter(x, y, c=[particula.color], s=100, 
                      edgecolors='black', linewidths=1.5, zorder=5)
            ax.text(x, y - 1, f'ID:{particula.id}', 
                   fontsize=8, ha='center', va='top')
        
        ax.set_title(f'Simulacion de Poblacion - Dia {simulacion.dia_actual}\n' +
                    f'Particulas: {len(particulas)} | Comida: {entorno.comida_actual}',
                    fontsize=14, fontweight='bold', pad=20)
        
        ax.set_xlabel('X', fontsize=12)
        ax.set_ylabel('Y', fontsize=12)
        ax.legend(loc='upper right')
        ax.invert_yaxis()
        
        plt.tight_layout()
        plt.show()