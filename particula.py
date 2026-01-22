import random

class Particula:
    """
    Representa una partícula (ser vivo) en la simulación.
    
    Attributes:
        id (int): Identificador único de la partícula
        entorno (Entorno): Referencia al entorno
        pos_inicial (tuple): Posición inicial (casa)
        posicion_actual (tuple): Posición actual (x, y)
        comida_consumida (int): Cantidad de comida consumida en el día
        camino (list): Lista de posiciones visitadas
        pasos_realizados (int): Contador de pasos realizados
        viva (bool): Estado de la partícula
        en_casa (bool): Indica si está en casa
        color (tuple): Color asignado para visualización
        generacion (int): Número de generación de la partícula
        mutacion (str): Tipo de mutación ('ninguna', 'velocidad', 'prioridad')
        velocidad_multiplicador (float): Multiplicador de velocidad
    """
    
    # Direcciones posibles: arriba, abajo, izquierda, derecha
    DIRECCIONES = [
        (0, -1),   # Arriba
        (0, 1),    # Abajo
        (-1, 0),   # Izquierda
        (1, 0)     # Derecha
    ]
    
    # Colores según tipo de partícula
    COLOR_NORMAL = (1.0, 1.0, 1.0)      # Blanco
    COLOR_VELOCIDAD = (1.0, 0.0, 0.0)   # Rojo
    COLOR_PRIORIDAD = (0.0, 1.0, 0.0)   # Verde
    
    def __init__(self, id, entorno, pos_inicial=None, generacion=0, mutacion='ninguna'):
        """
        Inicializa una partícula.
        
        Args:
            id (int): Identificador único
            entorno (Entorno): El entorno de la simulación
            pos_inicial (tuple): Posición inicial. Si es None, se asigna aleatoria
            generacion (int): Número de generación
            mutacion (str): Tipo de mutación ('ninguna', 'velocidad', 'prioridad')
        """
        self.id = id
        self.entorno = entorno
        self.generacion = generacion
        self.mutacion = mutacion
        
        # Establecer color según mutación
        if mutacion == 'velocidad':
            self.color = self.COLOR_VELOCIDAD
            self.velocidad_multiplicador = 1.5
        elif mutacion == 'prioridad':
            self.color = self.COLOR_PRIORIDAD
            self.velocidad_multiplicador = 1.0
        else:  # ninguna
            self.color = self.COLOR_NORMAL
            self.velocidad_multiplicador = 1.0
        
        if pos_inicial is None:
            self.pos_inicial = entorno.obtener_posicion_inicial_aleatoria()
        else:
            self.pos_inicial = pos_inicial
        
        self.posicion_actual = self.pos_inicial
        self.comida_consumida = 0
        self.camino = [self.posicion_actual]
        self.pasos_realizados = 0
        self.viva = True
        self.en_casa = True
        self.pasos_extra_disponibles = 0
    
    def realizar_paso(self):
        """
        Realiza un paso aleatorio. Las partículas con mutación de velocidad
        pueden realizar más pasos.
        
        Returns:
            bool: True si el paso fue exitoso, False si no pudo moverse
        """
        if not self.viva:
            return False
        
        # Determinar comida mínima para quedarse en casa según mutación
        if self.mutacion == 'velocidad':
            comida_minima_casa = 2
        else:
            comida_minima_casa = 1
        
        # Si está en casa y ya tiene la comida mínima para sobrevivir, no se mueve
        if self.en_casa and self.comida_consumida >= comida_minima_casa:
            return True
        
        # Calcular cuántos pasos realizar (velocidad)
        pasos_a_realizar = 1
        if self.mutacion == 'velocidad':
            # 50% de probabilidad de hacer un paso extra
            if random.random() < 0.5:
                pasos_a_realizar = 2
        
        exito = False
        for _ in range(pasos_a_realizar):
            if self._realizar_paso_individual():
                exito = True
        
        return exito
    
    def _realizar_paso_individual(self):
        """
        Realiza un paso individual.
        
        Returns:
            bool: True si el paso fue exitoso
        """
        # Intentar movimiento aleatorio
        max_intentos = 100
        for _ in range(max_intentos):
            direccion = random.choice(self.DIRECCIONES)
            dx, dy = direccion
            
            nueva_x = self.posicion_actual[0] + dx
            nueva_y = self.posicion_actual[1] + dy
            
            # Verificar si el movimiento es válido
            if self.entorno.es_posicion_valida(nueva_x, nueva_y):
                self.posicion_actual = (nueva_x, nueva_y)
                self.camino.append(self.posicion_actual)
                self.pasos_realizados += 1
                
                # Verificar si llegó a casa
                if self.entorno.es_casa(nueva_x, nueva_y):
                    self.en_casa = True
                else:
                    self.en_casa = False
                
                # Verificar si hay comida (la lógica de prioridad se maneja en el entorno)
                if self.entorno.hay_comida(nueva_x, nueva_y):
                    # Intentar consumir (puede fallar si otra partícula con prioridad la toma)
                    if self.entorno.consumir_comida(nueva_x, nueva_y, self):
                        self.comida_consumida += 1
                
                return True
        
        return False
    
    def evaluar_fin_dia(self):
        """
        Evalúa el estado de la partícula al final del día.
        
        Returns:
            dict: Resultado con 'sobrevive', 'reproduce' y 'mutacion_hijo'
        """
        resultado = {
            'sobrevive': False,
            'reproduce': False,
            'mutacion_hijo': 'ninguna'
        }
        
        # Determinar requisitos según mutación
        if self.mutacion == 'velocidad':
            # Mutación velocidad: necesita 2 comidas para sobrevivir, 3 para reproducirse
            comida_minima_supervivencia = 2
            comida_minima_reproduccion = 3
        else:
            # Normal y prioridad: 1 comida para sobrevivir, 2 para reproducirse
            comida_minima_supervivencia = 1
            comida_minima_reproduccion = 2
        
        # Verificar supervivencia
        if self.comida_consumida >= comida_minima_supervivencia and self.en_casa:
            resultado['sobrevive'] = True
            
            # Verificar reproducción
            if self.comida_consumida >= comida_minima_reproduccion:
                resultado['reproduce'] = True
                
                # Determinar mutación del hijo
                if self.mutacion == 'velocidad':
                    # Para velocidad, necesita 3+ comidas para mutar al hijo
                    if self.comida_consumida >= 3:
                        # 75% heredar velocidad, 25% sin mutación
                        if random.random() < 0.75:
                            resultado['mutacion_hijo'] = 'velocidad'
                        else:
                            resultado['mutacion_hijo'] = 'ninguna'
                    # Si comió exactamente 2, no hay reproducción para velocidad
                    # (ya que necesita 3 mínimo)
                    else:
                        resultado['reproduce'] = False
                        
                elif self.mutacion == 'prioridad':
                    # Prioridad se reproduce con 2+ comidas
                    if self.comida_consumida >= 3:
                        # Comió 3+: 75% heredar prioridad, 25% sin mutación
                        if random.random() < 0.75:
                            resultado['mutacion_hijo'] = 'prioridad'
                        else:
                            resultado['mutacion_hijo'] = 'ninguna'
                    else:
                        # Comió 2: 75% heredar prioridad, 25% sin mutación
                        if random.random() < 0.75:
                            resultado['mutacion_hijo'] = 'prioridad'
                        else:
                            resultado['mutacion_hijo'] = 'ninguna'
                            
                else:  # ninguna mutación
                    if self.comida_consumida >= 3:
                        # Comió 3+: 50% velocidad, 50% prioridad
                        resultado['mutacion_hijo'] = random.choice(['velocidad', 'prioridad'])
                    else:
                        # Comió 2: hijo sin mutación
                        resultado['mutacion_hijo'] = 'ninguna'
        
        # Caso especial: No comió pero está en casa (debe salir de nuevo)
        elif self.comida_consumida == 0 and self.en_casa:
            resultado['sobrevive'] = True
        
        return resultado
    
    def preparar_nuevo_dia(self):
        """
        Prepara la partícula para un nuevo día.
        """
        self.comida_consumida = 0
        self.camino = [self.pos_inicial]
        self.pasos_realizados = 0
        self.posicion_actual = self.pos_inicial
        self.en_casa = True
    
    def crear_hijo(self, nuevo_id, mutacion_hijo='ninguna'):
        """
        Crea una partícula hija.
        
        Args:
            nuevo_id (int): ID para la nueva partícula
            mutacion_hijo (str): Tipo de mutación del hijo
            
        Returns:
            Particula: Nueva partícula hija
        """
        return Particula(
            id=nuevo_id,
            entorno=self.entorno,
            pos_inicial=self.pos_inicial,
            generacion=self.generacion + 1,
            mutacion=mutacion_hijo
        )
    
    def obtener_info(self):
        """
        Obtiene información de la partícula.
        
        Returns:
            dict: Información de la partícula
        """
        return {
            'id': self.id,
            'generacion': self.generacion,
            'posicion': self.posicion_actual,
            'comida_consumida': self.comida_consumida,
            'pasos_realizados': self.pasos_realizados,
            'viva': self.viva,
            'en_casa': self.en_casa,
            'color': self.color,
            'mutacion': self.mutacion
        }