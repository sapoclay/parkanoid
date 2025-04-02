import pygame
import sys
import webbrowser
import os
import json

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
ANCHO = 800
ALTO = 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption('Parkanoid')

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
AZUL = (0, 0, 255)
ROJO = (255, 0, 0)
GRIS = (128, 128, 128)

# Cargar logo
LOGO_PATH = os.path.join('assets', 'logo.svg')

# Estados del juego
ESTADO_INICIO = 'inicio'
ESTADO_JUGANDO = 'jugando'
ESTADO_PAUSA = 'pausa'
estado_actual = ESTADO_INICIO

# Variables del juego
global input_activo, input_iniciales
puntuacion = 0
vidas = 3
juego_activo = True
mejores_puntuaciones = []
nivel_actual = 1
velocidad_base = 7
input_iniciales = ''
input_activo = False

# Configuración de la paleta
PALETA_ANCHO = 100
PALETA_ALTO = 20
paleta = pygame.Rect(ANCHO // 2 - PALETA_ANCHO // 2, ALTO - 40, PALETA_ANCHO, PALETA_ALTO)

# Configuración de la pelota
PELOTA_TAMAÑO = 10
pelota = pygame.Rect(ANCHO // 2 - PELOTA_TAMAÑO // 2, ALTO // 2 - PELOTA_TAMAÑO // 2, PELOTA_TAMAÑO, PELOTA_TAMAÑO)
pelota_dx = velocidad_base
pelota_dy = -velocidad_base

# Configuración de los bloques
BLOQUE_ANCHO = 80
BLOQUE_ALTO = 30
bloques = []

def inicializar_bloques():
    global bloques
    bloques = []
    for i in range(5):  # 5 filas
        for j in range(8):  # 8 columnas
            bloque = pygame.Rect(j * (BLOQUE_ANCHO + 2) + 50, i * (BLOQUE_ALTO + 2) + 50,
                                BLOQUE_ANCHO, BLOQUE_ALTO)
            bloques.append(bloque)

def siguiente_nivel():
    global nivel_actual, pelota_dx, pelota_dy, velocidad_base
    nivel_actual += 1
    velocidad_base = 7 + (nivel_actual - 1) * 2
    pelota_dx = velocidad_base if pelota_dx > 0 else -velocidad_base
    pelota_dy = -velocidad_base if pelota_dy < 0 else velocidad_base
    inicializar_bloques()
    pelota.center = (ANCHO // 2, ALTO // 2)

# Menú superior
class Menu:
    def __init__(self):
        self.altura = 30
        self.color = GRIS
        self.fuente = pygame.font.Font(None, 32)
        self.opciones = {
            'Archivo': ['Puntuaciones', 'Salir'],
            'Preferencias': ['About', 'Repositorio']
        }
        self.menu_activo = None
        self.rect_menu = pygame.Rect(0, 0, ANCHO, self.altura)
        self.submenu_visible = False

    def dibujar(self, superficie):
        pygame.draw.rect(superficie, self.color, self.rect_menu)
        x = 10
        for menu, opciones in self.opciones.items():
            texto = self.fuente.render(menu, True, NEGRO)
            superficie.blit(texto, (x, 5))
            
            # Dibujar submenú si está activo
            if self.menu_activo == menu:
                submenu_y = self.altura
                for opcion in opciones:
                    pygame.draw.rect(superficie, GRIS, (x, submenu_y, 150, 25))
                    texto_opcion = self.fuente.render(opcion, True, NEGRO)
                    superficie.blit(texto_opcion, (x + 5, submenu_y + 2))
                    submenu_y += 25
            x += texto.get_width() + 20

    def manejar_click(self, pos):
        x = 10
        for menu, opciones in self.opciones.items():
            ancho_texto = self.fuente.render(menu, True, NEGRO).get_width()
            # Verificar click en el menú principal
            if pygame.Rect(x, 0, ancho_texto, self.altura).collidepoint(pos):
                if self.menu_activo == menu:
                    self.menu_activo = None
                else:
                    self.menu_activo = menu
                return
            
            # Verificar click en submenús
            if self.menu_activo == menu:
                submenu_y = self.altura
                for opcion in opciones:
                    if pygame.Rect(x, submenu_y, 150, 25).collidepoint(pos):
                        if menu == 'Archivo':
                            if opcion == 'Puntuaciones':
                                self.mostrar_puntuaciones()
                            elif opcion == 'Salir':
                                pygame.quit()
                                sys.exit()
                        elif menu == 'Preferencias':
                            if opcion == 'About':
                                self.mostrar_about()
                            elif opcion == 'Repositorio':
                                webbrowser.open('https://github.com/sapoclay/parkanoid')
                        self.menu_activo = None
                        return
                    submenu_y += 25
            x += ancho_texto + 20
        
        # Si se hace clic fuera de cualquier menú, cerrar el menú activo
        if pos[1] > self.altura and self.menu_activo:
            self.menu_activo = None

    def mostrar_about(self):
        ventana_about = pygame.display.set_mode((400, 300))
        pygame.display.set_caption('About Parkanoid')
        ejecutando = True
        while ejecutando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT or \
                   (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                    ejecutando = False

            ventana_about.fill(NEGRO)
            texto = [
                'Parkanoid',
                'Un juego de romper bloques',
                'Versión 1.0',
                'Presiona ESC para cerrar'
            ]

            y = 50
            for linea in texto:
                superficie_texto = self.fuente.render(linea, True, BLANCO)
                ventana_about.blit(superficie_texto, 
                                  (200 - superficie_texto.get_width()//2, y))
                y += 40

            pygame.display.flip()

        pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption('Parkanoid')

    def mostrar_puntuaciones(self):
        try:
            with open('puntuaciones.json', 'r') as f:
                puntuaciones = json.load(f)
        except FileNotFoundError:
            puntuaciones = []

        ventana_puntuaciones = pygame.display.set_mode((400, 300))
        pygame.display.set_caption('Puntuaciones')
        ejecutando = True
        scroll_y = 0
        max_scroll = max(0, len(puntuaciones) * 30 - 200)  # 200 es el espacio disponible para la lista

        while ejecutando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT or \
                   (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                    ejecutando = False
                elif evento.type == pygame.MOUSEWHEEL:
                    scroll_y = max(min(scroll_y - evento.y * 20, max_scroll), 0)

            ventana_puntuaciones.fill(NEGRO)
            texto_titulo = self.fuente.render('Mejores Puntuaciones', True, BLANCO)
            ventana_puntuaciones.blit(texto_titulo, 
                                     (200 - texto_titulo.get_width()//2, 30))

            # Crear superficie para la lista con scroll
            lista_superficie = pygame.Surface((380, 200))
            lista_superficie.fill(NEGRO)

            y = 0
            if not puntuaciones:
                texto = self.fuente.render('No hay puntuaciones guardadas', True, BLANCO)
                lista_superficie.blit(texto, 
                                    (190 - texto.get_width()//2, y))
            else:
                # Asegurarse de que todas las puntuaciones tengan el formato correcto
                puntuaciones_validas = [p for p in puntuaciones if isinstance(p, dict) and 'puntos' in p and 'iniciales' in p]
                puntuaciones_ordenadas = sorted(puntuaciones_validas, key=lambda x: x['puntos'], reverse=True)
                for i, p in enumerate(puntuaciones_ordenadas):
                    texto = self.fuente.render(
                        f'{i+1}. {p["iniciales"]} - {p["puntos"]} puntos', 
                        True, BLANCO
                    )
                    if 0 <= y - scroll_y <= 200:
                        lista_superficie.blit(texto, 
                                            (190 - texto.get_width()//2, y - scroll_y))
                    y += 30

            ventana_puntuaciones.blit(lista_superficie, (10, 80))

            # Dibujar barra de desplazamiento si es necesaria
            if max_scroll > 0:
                total_altura = 200  # Altura del área visible
                scroll_altura = total_altura * (total_altura / (max_scroll + total_altura))
                scroll_pos = (scroll_y / max_scroll) * (total_altura - scroll_altura)
                pygame.draw.rect(ventana_puntuaciones, GRIS, 
                               (390, 80, 5, total_altura))  # Fondo de la barra
                pygame.draw.rect(ventana_puntuaciones, BLANCO, 
                               (390, 80 + scroll_pos, 5, scroll_altura))  # Barra

            texto_salir = self.fuente.render('Presiona ESC para cerrar', True, BLANCO)
            ventana_puntuaciones.blit(texto_salir, 
                                     (200 - texto_salir.get_width()//2, 260))

            pygame.display.flip()

            texto_salir = self.fuente.render('Presiona ESC para cerrar', True, BLANCO)
            ventana_puntuaciones.blit(texto_salir, 
                                     (200 - texto_salir.get_width()//2, 260))

            pygame.display.flip()

        pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption('Parkanoid')

# Crear instancia del menú
menu = Menu()

# Pantalla de inicio
def mostrar_pantalla_inicio():
    pantalla.fill(NEGRO)
    fuente_titulo = pygame.font.Font(None, 74)
    fuente_normal = pygame.font.Font(None, 36)

    titulo = fuente_titulo.render('PARKANOID', True, BLANCO)
    iniciar = fuente_normal.render('Presiona ESPACIO para comenzar', True, BLANCO)
    salir = fuente_normal.render('Presiona ESC para salir', True, BLANCO)

    pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, ALTO//3))
    pantalla.blit(iniciar, (ANCHO//2 - iniciar.get_width()//2, ALTO//2))
    pantalla.blit(salir, (ANCHO//2 - salir.get_width()//2, ALTO//2 + 50))

# Inicializar bloques
inicializar_bloques()

# Bucle principal del juego
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:  # Click izquierdo
                menu.manejar_click(evento.pos)
        elif evento.type == pygame.KEYDOWN:
            if estado_actual == ESTADO_INICIO:
                if evento.key == pygame.K_SPACE:
                    estado_actual = ESTADO_JUGANDO
                elif evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
    # Limpiar pantalla
    pantalla.fill(NEGRO)

    if estado_actual == ESTADO_INICIO:
        mostrar_pantalla_inicio()
    elif estado_actual == ESTADO_JUGANDO and juego_activo:
        # Mover la paleta
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT] and paleta.left > 0:
            paleta.x -= 8
        if teclas[pygame.K_RIGHT] and paleta.right < ANCHO:
            paleta.x += 8

        # Mover la pelota
        pelota.x += pelota_dx
        pelota.y += pelota_dy

        # Colisiones con las paredes
        if pelota.left <= 0 or pelota.right >= ANCHO:
            pelota_dx *= -1
        if pelota.top <= menu.altura:
            pelota_dy *= -1

        # Colisión con la paleta
        if pelota.colliderect(paleta):
            pelota_dy *= -1

        # Colisión con los bloques
        for bloque in bloques[:]:
            if pelota.colliderect(bloque):
                bloques.remove(bloque)
                pelota_dy *= -1
                puntuacion += 10
                break

        # Perder una vida
        if pelota.bottom >= ALTO:
            vidas -= 1
            if vidas > 0:
                pelota.center = (ANCHO // 2, ALTO // 2)
                pelota_dy = -7
            else:
                juego_activo = False
                input_activo = True
                input_iniciales = ''

        # Dibujar elementos del juego
        pygame.draw.rect(pantalla, AZUL, paleta)
        pygame.draw.ellipse(pantalla, BLANCO, pelota)
        for bloque in bloques:
            pygame.draw.rect(pantalla, ROJO, bloque)

        # Mostrar puntuación, vidas y nivel
        fuente = pygame.font.Font(None, 36)
        texto_puntuacion = fuente.render(f'Puntuación: {puntuacion}', True, BLANCO)
        texto_vidas = fuente.render(f'Vidas: {vidas}', True, BLANCO)
        texto_nivel = fuente.render(f'Nivel: {nivel_actual}', True, BLANCO)
        pantalla.blit(texto_puntuacion, (10, ALTO - 30))
        pantalla.blit(texto_vidas, (ANCHO - 100, ALTO - 30))
        pantalla.blit(texto_nivel, (ANCHO // 2 - 50, ALTO - 30))

        # Verificar si se completó el nivel
        if len(bloques) == 0:
            siguiente_nivel()

    # Mostrar mensaje de fin de juego y entrada de iniciales
    if not juego_activo:
        texto_fin = fuente.render('¡Juego Terminado!', True, BLANCO)
        pantalla.blit(texto_fin, (ANCHO // 2 - 100, ALTO // 2 - 40))
        
        if input_activo:
            texto_iniciales = fuente.render(f'Ingresa tus iniciales: {input_iniciales}', True, BLANCO)
            pantalla.blit(texto_iniciales, (ANCHO // 2 - 150, ALTO // 2))
            
            for evento in pygame.event.get():
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_RETURN and len(input_iniciales) == 3:
                        try:
                            with open('puntuaciones.json', 'r') as f:
                                puntuaciones = json.load(f)
                        except FileNotFoundError:
                            puntuaciones = []
                        puntuaciones.append({'iniciales': input_iniciales, 'puntos': puntuacion})
                        with open('puntuaciones.json', 'w') as f:
                            json.dump(puntuaciones, f)
                        input_activo = False
                    elif evento.key == pygame.K_BACKSPACE:
                        input_iniciales = input_iniciales[:-1]
                    elif len(input_iniciales) < 3 and evento.unicode.isalpha():
                        input_iniciales += evento.unicode.upper()
        else:
            reiniciar = fuente.render('Presiona R para reiniciar', True, BLANCO)
            pantalla.blit(reiniciar, (ANCHO // 2 - 100, ALTO // 2 + 40))

        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_r]:
            juego_activo = True
            vidas = 3
            puntuacion = 0
            inicializar_bloques()
            pelota.center = (ANCHO // 2, ALTO // 2)
            paleta.centerx = ANCHO // 2
            pelota_dy = -7

    # Dibujar el menú siempre al final para que esté por encima de todo
    menu.dibujar(pantalla)
    
    pygame.display.flip()
    pygame.time.Clock().tick(60)