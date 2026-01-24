import random

class Particula:
    """
    Representa una partícula (ser vivo) en la simulación.
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
    COLOR_DEPREDADOR = (0.0, 0.0, 0.0)  # Negro
    
    def __init__(self, id, entorno, pos_inicial=None, generacion=0, mutacion='ninguna', es_depredador=False):
        """
        Inicializa una partícula.
        
        Args:
            id (int): Identificador único
            entorno (Entorno): El entorno de la simulación
            pos_inicial (tuple): Posición inicial. Si es None, se asigna aleatoria
            generacion (int): Número de generación
            mutacion (str): Tipo de mutación ('ninguna', 'velocidad', 'prioridad')
            es_depredador (bool): Si es un depredador
        """
        self.id = id
        self.entorno = entorno
        self.generacion = generacion
        self.mutacion = mutacion
        self.es_depredador = es_depredador
        self.mordidas_recibidas = 0
        
        # Establecer color según tipo
        if es_depredador:
            self.color = self.COLOR_DEPREDADOR
            self.velocidad_multiplicador = 1.0
        elif mutacion == 'velocidad':
            self.color = self.COLOR_VELOCIDAD
            self.velocidad_multiplicador = 1.5
        elif mutacion == 'prioridad':
            self.color = self.COLOR_PRIORIDAD
            self.velocidad_multiplicador = 1.0
        else:  # ninguna
            self.color = self.COLOR_NORMAL
            self.velocidad_multiplicador = 1.0
        
        if pos_inicial is None:
            self.pos_inicial = entorno.obtener_posicion_inicial_aleatoria(es_depredador=es_depredador)
        else:
            self.pos_inicial = pos_inicial
        
        self.posicion_actual = self.pos_inicial
        self.comida_consumida = 0
        self.camino = [self.posicion_actual]
        self.pasos_realizados = 0
        self.viva = True
        self.en_casa = True
    
    def detectar_depredador_cercano(self, depredadores):
        """
        Detecta si hay un depredador a un paso de distancia.
        
        Args:
            depredadores (list): Lista de depredadores en el mapa
            
        Returns:
            tuple: Posición del depredador más cercano o None
        """
        if not self.mutacion == 'velocidad':
            return None
        
        x, y = self.posicion_actual
        
        for depredador in depredadores:
            dx, dy = depredador.posicion_actual
            # Verificar si está a exactamente un paso
            if abs(x - dx) + abs(y - dy) == 1:
                return depredador.posicion_actual
        
        return None
    
    def huir_de_depredador(self, pos_depredador):
        """
        Intenta moverse en dirección opuesta al depredador.
        
        Args:
            pos_depredador (tuple): Posición del depredador
            
        Returns:
            bool: True si logró huir
        """
        x, y = self.posicion_actual
        dx, dy = pos_depredador
        
        # Calcular dirección opuesta
        dir_x = 0 if x == dx else (1 if x > dx else -1)
        dir_y = 0 if y == dy else (1 if y > dy else -1)
        
        # Intentar moverse en dirección opuesta
        nueva_x = x + dir_x
        nueva_y = y + dir_y
        
        if self.entorno.es_posicion_valida(nueva_x, nueva_y):
            self.posicion_actual = (nueva_x, nueva_y)
            self.camino.append(self.posicion_actual)
            self.pasos_realizados += 1
            
            # Actualizar estado de casa
            if self.entorno.es_casa(nueva_x, nueva_y):
                self.en_casa = True
            else:
                self.en_casa = False
            
            return True
        
        return False
    
    def realizar_paso(self, depredadores=None):
        """
        Realiza un paso aleatorio. Las partículas con mutación de velocidad
        pueden realizar más pasos y huir de depredadores.
        
        Args:
            depredadores (list): Lista de depredadores (solo para partículas con velocidad)
        
        Returns:
            bool: True si el paso fue exitoso, False si no pudo moverse
        """
        if not self.viva:
            return False
        
        # Los depredadores siempre se mueven
        if self.es_depredador:
            return self._realizar_paso_individual()
        
        # Determinar comida mínima para quedarse en casa según mutación
        if self.mutacion == 'velocidad':
            comida_minima_casa = 2
        else:
            comida_minima_casa = 1
        
        # Si está en casa y ya tiene la comida mínima para sobrevivir, no se mueve
        if self.en_casa and self.comida_consumida >= comida_minima_casa:
            return True
        
        # Partículas rojas detectan y huyen de depredadores
        if self.mutacion == 'velocidad' and depredadores:
            pos_depredador = self.detectar_depredador_cercano(depredadores)
            if pos_depredador:
                # Intentar huir
                if self.huir_de_depredador(pos_depredador):
                    # Después de huir, sigue con su movimiento normal
                    pass
        
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
                # RESTRICCIÓN: Los depredadores NO pueden entrar a la zona segura
                if self.es_depredador and self.entorno.es_casa(nueva_x, nueva_y):
                    continue  # Intentar otra dirección
                
                self.posicion_actual = (nueva_x, nueva_y)
                self.camino.append(self.posicion_actual)
                self.pasos_realizados += 1
                
                # Verificar si llegó a casa
                if self.entorno.es_casa(nueva_x, nueva_y):
                    self.en_casa = True
                else:
                    self.en_casa = False
                
                # Solo las partículas normales comen (depredadores no)
                if not self.es_depredador:
                    if self.entorno.hay_comida(nueva_x, nueva_y):
                        if self.entorno.consumir_comida(nueva_x, nueva_y, self):
                            self.comida_consumida += 1
                
                return True
        
        return False
    
    def recibir_mordida(self):
        """
        Recibe una mordida de un depredador.
        
        Returns:
            bool: True si muere por la mordida
        """
        self.mordidas_recibidas += 1
        
        # Blancas y rojas mueren con 1 mordida
        if self.mutacion in ['ninguna', 'velocidad']:
            if self.mordidas_recibidas >= 1:
                self.viva = False
                return True
        # Verdes mueren con 2 mordidas
        elif self.mutacion == 'prioridad':
            if self.mordidas_recibidas >= 2:
                self.viva = False
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
            comida_minima_supervivencia = 2
            comida_minima_reproduccion = 3
        else:
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
                    if self.comida_consumida >= 3:
                        if random.random() < 0.75:
                            resultado['mutacion_hijo'] = 'velocidad'
                        else:
                            resultado['mutacion_hijo'] = 'ninguna'
                    else:
                        resultado['reproduce'] = False
                        
                elif self.mutacion == 'prioridad':
                    if self.comida_consumida >= 3:
                        if random.random() < 0.75:
                            resultado['mutacion_hijo'] = 'prioridad'
                        else:
                            resultado['mutacion_hijo'] = 'ninguna'
                    else:
                        if random.random() < 0.75:
                            resultado['mutacion_hijo'] = 'prioridad'
                        else:
                            resultado['mutacion_hijo'] = 'ninguna'
                            
                else:  # ninguna mutación
                    if self.comida_consumida >= 3:
                        resultado['mutacion_hijo'] = random.choice(['velocidad', 'prioridad'])
                    else:
                        resultado['mutacion_hijo'] = 'ninguna'
        
        # Caso especial: No comió pero está en casa
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
        self.mordidas_recibidas = 0
    
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
            mutacion=mutacion_hijo,
            es_depredador=False
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
            'mutacion': self.mutacion,
            'es_depredador': self.es_depredador,
            'mordidas_recibidas': self.mordidas_recibidas
        }