import random

class Entorno:
    """
    Clase que representa el entorno donde se realiza la simulación de población.
    
    Attributes:
        ancho (int): Ancho del entorno (número de celdas en X)
        alto (int): Alto del entorno (número de celdas en Y)
        porcentaje_comida (float): Porcentaje del mapa ocupado por comida
        posiciones_comida (set): Conjunto de posiciones (x, y) con comida
        comida_total (int): Cantidad total de comida inicial
        comida_actual (int): Cantidad de comida restante
        particulas_en_posicion (dict): Diccionario de posiciones -> lista de partículas
    """
    
    def __init__(self, ancho=100, alto=100, porcentaje_comida=0.20):
        """
        Inicializa el entorno con dimensiones y comida.
        
        Args:
            ancho (int): Ancho del entorno. Default: 100
            alto (int): Alto del entorno. Default: 100
            porcentaje_comida (float): Porcentaje de celdas con comida. Default: 0.20
        """
        self.ancho = ancho
        self.alto = alto
        self.porcentaje_comida = porcentaje_comida
        self.posiciones_comida = set()
        self.comida_total = 0
        self.comida_actual = 0
        self.particulas_en_posicion = {}
        
        self._generar_comida()
    
    def _generar_comida(self):
        """
        Genera comida aleatoriamente SOLO en el área interna (no en los bordes).
        """
        # Generar solo en el área interna (excluyendo los bordes)
        posiciones_internas = [
            (x, y) 
            for x in range(1, self.ancho - 1) 
            for y in range(1, self.alto - 1)
        ]
        
        total_celdas_internas = len(posiciones_internas)
        cantidad_comida = int(total_celdas_internas * self.porcentaje_comida)
        
        # Asegurar que haya al menos algo de comida
        if cantidad_comida == 0 and total_celdas_internas > 0:
            cantidad_comida = 1
        
        # Generar posiciones aleatorias únicas para la comida
        if cantidad_comida > 0 and len(posiciones_internas) > 0:
            posiciones_seleccionadas = random.sample(posiciones_internas, 
                                                    min(cantidad_comida, len(posiciones_internas)))
            self.posiciones_comida = set(posiciones_seleccionadas)
        else:
            self.posiciones_comida = set()
        
        self.comida_total = len(self.posiciones_comida)
        self.comida_actual = self.comida_total
    
    def reestablecer_comida(self):
        """
        Reestablece la comida a la cantidad inicial en posiciones aleatorias nuevas.
        """
        self._generar_comida()
    
    def es_posicion_valida(self, x, y):
        """
        Verifica si una posición está dentro de los límites del entorno.
        
        Args:
            x (int): Coordenada X
            y (int): Coordenada Y
            
        Returns:
            bool: True si la posición es válida, False si está fuera de límites
        """
        return 0 <= x < self.ancho and 0 <= y < self.alto
    
    def es_casa(self, x, y):
        """
        Verifica si una posición es casa (las paredes/bordes del mapa).
        
        Args:
            x (int): Coordenada X
            y (int): Coordenada Y
            
        Returns:
            bool: True si la posición es casa (borde del mapa)
        """
        return (x == 0 or x == self.ancho - 1 or 
                y == 0 or y == self.alto - 1)
    
    def hay_comida(self, x, y):
        """
        Verifica si hay comida en una posición específica.
        
        Args:
            x (int): Coordenada X
            y (int): Coordenada Y
            
        Returns:
            bool: True si hay comida en esa posición
        """
        return (x, y) in self.posiciones_comida
    
    def consumir_comida(self, x, y, particula):
        """
        Consume la comida en una posición si existe, considerando prioridad.
        
        Args:
            x (int): Coordenada X
            y (int): Coordenada Y
            particula (Particula): La partícula que intenta consumir
            
        Returns:
            bool: True si se consumió comida, False si no había comida o perdió por prioridad
        """
        if (x, y) not in self.posiciones_comida:
            return False
        
        # Registrar que esta partícula está en esta posición
        pos_key = (x, y)
        if pos_key not in self.particulas_en_posicion:
            self.particulas_en_posicion[pos_key] = []
        
        # Verificar si ya hay partículas con prioridad en esta posición
        particulas_aqui = self.particulas_en_posicion[pos_key]
        
        # Si la partícula actual tiene prioridad
        if particula.mutacion == 'prioridad':
            # Consume la comida sin importar quién más esté
            self.posiciones_comida.remove((x, y))
            self.comida_actual -= 1
            # Limpiar registro de esta posición
            if pos_key in self.particulas_en_posicion:
                del self.particulas_en_posicion[pos_key]
            return True
        else:
            # Si no tiene prioridad, verificar si hay alguien con prioridad
            for p in particulas_aqui:
                if p.mutacion == 'prioridad':
                    # Hay una partícula con prioridad, esta no come
                    return False
            
            # No hay partículas con prioridad, puede comer
            self.posiciones_comida.remove((x, y))
            self.comida_actual -= 1
            # Limpiar registro de esta posición
            if pos_key in self.particulas_en_posicion:
                del self.particulas_en_posicion[pos_key]
            return True
    
    def registrar_particula_en_posicion(self, x, y, particula):
        """
        Registra una partícula en una posición específica.
        
        Args:
            x (int): Coordenada X
            y (int): Coordenada Y
            particula (Particula): La partícula a registrar
        """
        pos_key = (x, y)
        if pos_key not in self.particulas_en_posicion:
            self.particulas_en_posicion[pos_key] = []
        if particula not in self.particulas_en_posicion[pos_key]:
            self.particulas_en_posicion[pos_key].append(particula)
    
    def limpiar_registro_posiciones(self):
        """
        Limpia el registro de partículas en posiciones.
        """
        self.particulas_en_posicion = {}
    
    def obtener_dimensiones(self):
        """
        Retorna las dimensiones del entorno.
        
        Returns:
            tuple: (ancho, alto)
        """
        return (self.ancho, self.alto)
    
    def obtener_posicion_inicial_aleatoria(self):
        """
        Retorna una posición aleatoria en los bordes del mapa (casa).
        
        Returns:
            tuple: (x, y) posición inicial en un borde
        """
        borde = random.choice(['arriba', 'abajo', 'izquierda', 'derecha'])
        
        if borde == 'arriba':
            return (random.randint(0, self.ancho - 1), 0)
        elif borde == 'abajo':
            return (random.randint(0, self.ancho - 1), self.alto - 1)
        elif borde == 'izquierda':
            return (0, random.randint(0, self.alto - 1))
        else:  # derecha
            return (self.ancho - 1, random.randint(0, self.alto - 1))