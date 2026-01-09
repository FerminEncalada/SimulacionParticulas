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
        color (str): Color asignado para visualización
        generacion (int): Número de generación de la partícula
    """
    
    # Direcciones posibles: arriba, abajo, izquierda, derecha
    DIRECCIONES = [
        (0, -1),   # Arriba
        (0, 1),    # Abajo
        (-1, 0),   # Izquierda
        (1, 0)     # Derecha
    ]
    
    def __init__(self, id, entorno, pos_inicial=None, color=None, generacion=0):
        """
        Inicializa una partícula.
        
        Args:
            id (int): Identificador único
            entorno (Entorno): El entorno de la simulación
            pos_inicial (tuple): Posición inicial. Si es None, se asigna aleatoria
            color (str): Color para visualización
            generacion (int): Número de generación
        """
        self.id = id
        self.entorno = entorno
        self.generacion = generacion
        
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
        self.color = color if color else self._generar_color_aleatorio()
    
    def _generar_color_aleatorio(self):
        """Genera un color RGB aleatorio."""
        return (random.random(), random.random(), random.random())
    
    def realizar_paso(self):
        """
        Realiza un paso aleatorio.
        
        Returns:
            bool: True si el paso fue exitoso, False si no pudo moverse
        """
        if not self.viva:
            return False
        
        # Si está en casa y ya cumplió objetivo, no se mueve
        if self.en_casa and self.comida_consumida >= 1:
            return True
        
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
                
                # Verificar si hay comida
                if self.entorno.hay_comida(nueva_x, nueva_y):
                    if self.entorno.consumir_comida(nueva_x, nueva_y):
                        self.comida_consumida += 1
                
                return True
        
        return False
    
    def evaluar_fin_dia(self):
        """
        Evalúa el estado de la partícula al final del día.
        
        Returns:
            dict: Resultado con 'sobrevive' y 'reproduce'
        """
        resultado = {
            'sobrevive': False,
            'reproduce': False
        }
        
        # Caso 3: Comió al menos 1 y está en casa
        if self.comida_consumida >= 1 and self.en_casa:
            resultado['sobrevive'] = True
            
            # Caso 4: Comió 2 o más y está en casa
            if self.comida_consumida >= 2:
                resultado['reproduce'] = True
        
        # Caso 5: No comió pero está en casa (debe salir de nuevo)
        elif self.comida_consumida == 0 and self.en_casa:
            # La partícula sobrevive pero reinicia su búsqueda
            resultado['sobrevive'] = True
        
        # Casos 1 y 2: Muere por no estar en casa
        else:
            resultado['sobrevive'] = False
        
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
    
    def crear_hijo(self, nuevo_id):
        """
        Crea una partícula hija con las mismas características.
        
        Args:
            nuevo_id (int): ID para la nueva partícula
            
        Returns:
            Particula: Nueva partícula hija
        """
        return Particula(
            id=nuevo_id,
            entorno=self.entorno,
            pos_inicial=self.pos_inicial,
            color=self.color,
            generacion=self.generacion + 1
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
            'color': self.color
        }