from particula import Particula
import copy

class Simulacion:
    """
    Controla la simulación de población.
    
    Attributes:
        entorno (Entorno): El entorno de la simulación
        particulas (list): Lista de partículas activas
        depredadores (list): Lista de depredadores activos
        num_particulas_inicial (int): Número inicial de partículas
        pasos_por_dia (int): Número de pasos que dura un día
        dia_actual (int): Día actual de la simulación
        contador_id (int): Contador para asignar IDs únicos
        historial_dias (list): Historial de estadísticas por día
        todas_particulas_dias (list): Lista de todas las partículas por día (para animación)
        frecuencia_depredadores (int): Cada cuántos días aparecen depredadores
        cantidad_depredadores (int): Cuántos depredadores aparecen
    """
    
    def __init__(self, entorno, num_particulas_inicial=10, pasos_por_dia=100, 
                 frecuencia_depredadores=2, cantidad_depredadores=1):
        """
        Inicializa la simulación.
        
        Args:
            entorno (Entorno): El entorno donde se realizará la simulación
            num_particulas_inicial (int): Número de partículas al inicio
            pasos_por_dia (int): Cuántos pasos dura un día
            frecuencia_depredadores (int): Cada cuántos días aparecen depredadores
            cantidad_depredadores (int): Cuántos depredadores aparecen
        """
        self.entorno = entorno
        self.num_particulas_inicial = num_particulas_inicial
        self.pasos_por_dia = pasos_por_dia
        self.dia_actual = 1
        self.contador_id = 0
        self.historial_dias = []
        self.todas_particulas_dias = []
        self.frecuencia_depredadores = frecuencia_depredadores
        self.cantidad_depredadores = cantidad_depredadores
        self.depredadores = []
        
        # Crear partículas iniciales
        self.particulas = []
        self._crear_particulas_iniciales()
    
    def _crear_particulas_iniciales(self):
        """Crea las partículas iniciales de la simulación."""
        for _ in range(self.num_particulas_inicial):
            particula = Particula(
                id=self._obtener_nuevo_id(),
                entorno=self.entorno,
                es_depredador=False
            )
            self.particulas.append(particula)
    
    def _generar_depredadores(self):
        """Genera depredadores si corresponde al día actual."""
        if self.frecuencia_depredadores > 0 and self.dia_actual % self.frecuencia_depredadores == 0:
            for _ in range(self.cantidad_depredadores):
                depredador = Particula(
                    id=self._obtener_nuevo_id(),
                    entorno=self.entorno,
                    es_depredador=True
                )
                self.depredadores.append(depredador)
            return True
        return False
    
    def _procesar_ataques_depredadores(self):
        """Procesa los ataques de depredadores a partículas.
        Los depredadores solo pueden atacar FUERA de la zona segura."""
        muertes_por_depredador = 0
        
        for depredador in self.depredadores:
            pos_dep = depredador.posicion_actual
            
            # Verificar que el depredador NO esté en zona segura
            if self.entorno.es_casa(pos_dep[0], pos_dep[1]):
                continue  # No puede atacar desde la zona segura
            
            # Buscar partículas en la misma posición
            for particula in self.particulas:
                if particula.viva and particula.posicion_actual == pos_dep:
                    # La partícula tampoco debe estar en zona segura
                    if not self.entorno.es_casa(particula.posicion_actual[0], particula.posicion_actual[1]):
                        if particula.recibir_mordida():
                            muertes_por_depredador += 1
        
        return muertes_por_depredador
    
    def _obtener_nuevo_id(self):
        """Obtiene un nuevo ID único para una partícula."""
        nuevo_id = self.contador_id
        self.contador_id += 1
        return nuevo_id
    
    def simular_dia(self, mostrar_progreso=False):
        """
        Simula un día completo.
        
        Args:
            mostrar_progreso (bool): Si True, muestra información del progreso
            
        Returns:
            dict: Estadísticas del día
        """
        if mostrar_progreso:
            print(f"\n{'='*70}")
            print(f"DÍA {self.dia_actual}")
            print(f"{'='*70}")
            print(f"Partículas vivas: {len(self.particulas)}")
            print(f"Pasos por día: {self.pasos_por_dia}")
            print(f"Comida disponible: {self.entorno.comida_actual}")
        
        # Generar depredadores si corresponde
        num_depredadores_generados = 0
        if self._generar_depredadores():
            num_depredadores_generados = len(self.depredadores)
            if mostrar_progreso:
                print(f"APARECEN {num_depredadores_generados} DEPREDADOR(ES)")
        
        # Guardar copia profunda de las partículas para animación
        particulas_dia_copia = []
        for p in self.particulas:
            p_copia = Particula(p.id, self.entorno, p.pos_inicial, p.generacion, p.mutacion)
            p_copia.camino = [p.pos_inicial]
            p_copia.pasos_realizados = 0
            p_copia.comida_consumida = 0
            particulas_dia_copia.append(p_copia)
        
        # Contador de muertes por depredador
        muertes_por_depredador_total = 0
        
        # Simular todos los pasos del día
        for paso in range(self.pasos_por_dia):
            # Mover partículas normales
            for i, particula in enumerate(self.particulas):
                particula.realizar_paso(depredadores=self.depredadores)
                # Sincronizar con la copia
                if i < len(particulas_dia_copia):
                    particulas_dia_copia[i].camino = particula.camino.copy()
                    particulas_dia_copia[i].posicion_actual = particula.posicion_actual
                    particulas_dia_copia[i].comida_consumida = particula.comida_consumida
                    particulas_dia_copia[i].en_casa = particula.en_casa
            
            # Mover depredadores
            for depredador in self.depredadores:
                depredador.realizar_paso()
            
            # Procesar ataques después de cada paso
            muertes_paso = self._procesar_ataques_depredadores()
            muertes_por_depredador_total += muertes_paso
            
            if mostrar_progreso and (paso + 1) % 20 == 0:
                progreso = ((paso + 1) / self.pasos_por_dia) * 100
                print(f"  Progreso del día: {progreso:.0f}%")
        
        # Guardar las partículas de este día
        self.todas_particulas_dias.append(particulas_dia_copia)
        
        # Evaluar resultados del día
        estadisticas = self._evaluar_fin_dia(mostrar_progreso, num_depredadores_generados, muertes_por_depredador_total)
        
        # Limpiar depredadores al final del día
        self.depredadores = []
        
        # Preparar siguiente día
        self._preparar_siguiente_dia()
        
        return estadisticas
    
    def _evaluar_fin_dia(self, mostrar_info=False, num_depredadores=0, muertes_por_depredador=0):
        """
        Evalúa qué partículas sobreviven y se reproducen al final del día.
        
        Args:
            mostrar_info (bool): Si True, muestra información
            num_depredadores (int): Número de depredadores que aparecieron
            muertes_por_depredador (int): Número de muertes causadas por depredadores
            
        Returns:
            dict: Estadísticas del día
        """
        sobrevivientes = []
        reproducciones = 0
        muertes = 0
        comida_total_consumida = 0
        mutaciones_velocidad = 0
        mutaciones_prioridad = 0
        
        for particula in self.particulas:
            # Solo evaluar partículas que siguen vivas
            if not particula.viva:
                muertes += 1
                continue
            
            resultado = particula.evaluar_fin_dia()
            comida_total_consumida += particula.comida_consumida
            
            if resultado['sobrevive']:
                sobrevivientes.append(particula)
                
                if resultado['reproduce']:
                    # Crear partícula hija
                    hijo = particula.crear_hijo(
                        self._obtener_nuevo_id(),
                        mutacion_hijo=resultado['mutacion_hijo']
                    )
                    sobrevivientes.append(hijo)
                    reproducciones += 1
                    
                    # Contar nuevas mutaciones
                    if resultado['mutacion_hijo'] == 'velocidad':
                        mutaciones_velocidad += 1
                    elif resultado['mutacion_hijo'] == 'prioridad':
                        mutaciones_prioridad += 1
            else:
                muertes += 1
                particula.viva = False
        
        # Actualizar lista de partículas
        self.particulas = sobrevivientes
        
        # Contar tipos de partículas
        normales = sum(1 for p in self.particulas if p.mutacion == 'ninguna')
        velocidad_count = sum(1 for p in self.particulas if p.mutacion == 'velocidad')
        prioridad = sum(1 for p in self.particulas if p.mutacion == 'prioridad')
        
        estadisticas = {
            'dia': self.dia_actual,
            'particulas_iniciales': len(self.particulas) + muertes,
            'particulas_finales': len(self.particulas),
            'muertes': muertes,
            'reproducciones': reproducciones,
            'comida_consumida': comida_total_consumida,
            'comida_restante': self.entorno.comida_actual,
            'comida_inicial': self.entorno.comida_total,
            'porcentaje_comida': self.entorno.porcentaje_comida_actual,
            'tipo_dia': self.entorno.obtener_info_comida()['tipo_dia'],
            'normales': normales,
            'velocidad': velocidad_count,
            'prioridad': prioridad,
            'nuevas_mutaciones_velocidad': mutaciones_velocidad,
            'nuevas_mutaciones_prioridad': mutaciones_prioridad,
            'depredadores_aparecidos': num_depredadores,
            'muertes_por_depredador': muertes_por_depredador
        }
        
        self.historial_dias.append(estadisticas)
        
        if mostrar_info:
            print(f"\n  RESUMEN DEL DÍA {self.dia_actual}:")
            print(f"  Partículas al inicio: {estadisticas['particulas_iniciales']}")
            print(f"  Muertes: {muertes}")
            if muertes_por_depredador > 0:
                print(f"    - Por depredadores: {muertes_por_depredador}")
            print(f"  Reproducciones: {reproducciones}")
            print(f"  Partículas sobrevivientes: {len(self.particulas)}")
            print(f"  Comida consumida: {comida_total_consumida}")
            print(f"  Comida restante: {self.entorno.comida_actual}")
        
        return estadisticas
    
    def _preparar_siguiente_dia(self):
        """Prepara todas las partículas para el siguiente día."""
        self.dia_actual += 1
        # Reestablecer comida
        self.entorno.reestablecer_comida()
        # Preparar partículas
        for particula in self.particulas:
            particula.preparar_nuevo_dia()
    
    def ejecutar_simulacion_completa(self, max_dias=100, mostrar_progreso=True):
        """
        Ejecuta la simulación completa hasta que no queden partículas o se alcance el límite.
        
        Args:
            max_dias (int): Número máximo de días a simular
            mostrar_progreso (bool): Si True, muestra el progreso
            
        Returns:
            list: Historial completo de la simulación
        """
        print(f"\n{'='*70}")
        print("INICIANDO SIMULACIÓN DE POBLACIÓN")
        print(f"{'='*70}")
        print(f"Dimensiones del entorno: {self.entorno.obtener_dimensiones()}")
        print(f"Partículas iniciales: {self.num_particulas_inicial}")
        print(f"Pasos por día: {self.pasos_por_dia}")
        print(f"Comida inicial: {self.entorno.comida_total}")
        print(f"{'='*70}\n")
        
        while len(self.particulas) > 0 and self.dia_actual <= max_dias:
            estadisticas = self.simular_dia(mostrar_progreso=mostrar_progreso)
            
            if not mostrar_progreso and self.dia_actual % 5 == 0:
                print(f"Día {self.dia_actual - 1}: {estadisticas['particulas_finales']} partículas vivas")
        
        print(f"\n{'='*70}")
        print("SIMULACIÓN FINALIZADA")
        print(f"{'='*70}")
        
        if len(self.particulas) == 0:
            print(f"Todas las partículas han muerto en el día {self.dia_actual - 1}")
        else:
            print(f"Simulación detenida en el día {self.dia_actual - 1}")
            print(f"Partículas sobrevivientes: {len(self.particulas)}")
        
        print(f"{'='*70}\n")
        
        return self.historial_dias
    
    def obtener_estado_actual(self):
        """
        Obtiene el estado actual de la simulación.
        
        Returns:
            dict: Estado actual
        """
        return {
            'dia': self.dia_actual,
            'num_particulas': len(self.particulas),
            'particulas': [p.obtener_info() for p in self.particulas],
            'comida_restante': self.entorno.comida_actual,
            'historial': self.historial_dias
        }