import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random

pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

# Configuração da câmera
gluPerspective(60, (display[0] / display[1]), 0.1, 100.0)
glTranslatef(0.0, -2, -12)

# Ativar profundidade e iluminação
glEnable(GL_DEPTH_TEST)
glEnable(GL_LIGHTING)
glEnable(GL_LIGHT0)

# Luz
glLightfv(GL_LIGHT0, GL_POSITION, (0, 5, 5, 1))
glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))

clock = pygame.time.Clock()

lane_positions = [-2, 0, 2]
current_lane = 1
player_x = 0
spawnable = False

obstacles = []
road_offset = 0
# No seu setup inicial
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)


def draw_cube(x, y, z, size=1):
    glPushMatrix()
    glTranslatef(x, y, z)

    glBegin(GL_QUADS)

    # Normais ajudam na iluminação
    # Frente
    glNormal3f(0, 0, 1)
    glVertex3f(-size, -size, size)
    glVertex3f(size, -size, size)
    glVertex3f(size, size, size)
    glVertex3f(-size, size, size)

    # Trás
    glNormal3f(0, 0, -1)
    glVertex3f(-size, -size, -size)
    glVertex3f(size, -size, -size)
    glVertex3f(size, size, -size)
    glVertex3f(-size, size, -size)

    # Topo
    glNormal3f(0, 1, 0)
    glVertex3f(-size, size, -size)
    glVertex3f(size, size, -size)
    glVertex3f(size, size, size)
    glVertex3f(-size, size, size)

    # Base
    glNormal3f(0, -1, 0)
    glVertex3f(-size, -size, -size)
    glVertex3f(size, -size, -size)
    glVertex3f(size, -size, size)
    glVertex3f(-size, -size, size)

    glEnd()
    glPopMatrix()


def draw_player():
    glColor3f(0.2, 0.6, 1.0)

    # Corpo
    draw_cube(player_x, 0, 0, 0.7)

    # Cabeça
    draw_cube(player_x, 1.2, 0, 0.4)


def draw_road():
    global road_offset, road_tex

    glDisable(GL_LIGHTING)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, road_tex) # ID da textura carregada

    # Asfalto com textura animada
    glColor3f(1.0, 1.0, 1.0) # Resetar cor para não tingir a textura
    
    # Ajuste este fator para controlar a velocidade aparente
    tex_movement = road_offset * 0.1

    glBegin(GL_QUADS)
    # glTexCoord2f(U, V + movimento)
    # O valor '20' abaixo faz a textura repetir 20 vezes ao longo da pista
    glTexCoord2f(0, 0 + tex_movement); glVertex3f(-4, -1, 7)
    glTexCoord2f(1, 0 + tex_movement); glVertex3f(4, -1, 7)
    glTexCoord2f(1, 20 + tex_movement); glVertex3f(4, -1, -100)
    glTexCoord2f(0, 20 + tex_movement); glVertex3f(-4, -1, -100)
    glEnd()

    glDisable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING)

def draw_scenery():
    global road_offset, grass_tex
    
    glDisable(GL_LIGHTING)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, grass_tex)
    
    glColor3f(1.0, 1.0, 1.0)
    
    # Velocidade do movimento da grama (mesma do asfalto para sincronia)
    tex_move = road_offset * 0.1 
    
    glBegin(GL_QUADS)
    
    # --- Grama Esquerda ---
    glTexCoord2f(0, 0 + tex_move);    glVertex3f(-80, -1.01, 7)    # Um tiquinho abaixo do asfalto (-1.01)
    glTexCoord2f(5, 0 + tex_move);    glVertex3f(-4, -1.01, 7)     # para evitar "Z-fighting"
    glTexCoord2f(5, 20 + tex_move);   glVertex3f(-4, -1.01, -100)
    glTexCoord2f(0, 20 + tex_move);   glVertex3f(-80, -1.01, -100)

    # --- Grama Direita ---
    glTexCoord2f(0, 0 + tex_move);    glVertex3f(4, -1.01, 7)
    glTexCoord2f(5, 0 + tex_move);    glVertex3f(80, -1.01, 7)
    glTexCoord2f(5, 20 + tex_move);   glVertex3f(80, -1.01, -110)
    glTexCoord2f(0, 20 + tex_move);   glVertex3f(4, -1.01, -110)
    
    glEnd()
    glDisable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING)

def spawn_obstacle():
    lane = random.choice(lane_positions)
    obstacles.append([lane, 0, -80])


def move_obstacles(speed):
    global obstacles
    for obs in obstacles:
        obs[2] += speed
    obstacles = [obs for obs in obstacles if obs[2] < 5]


def draw_obstacles():
    glColor3f(1, 0.2, 0.2)
    for obs in obstacles:
        draw_cube(obs[0], 0, obs[2], 0.8)


def check_collision():
    for obs in obstacles:
        if abs(obs[0] - player_x) < 1 and -2 < obs[2] < 1:
            return True
    return False

def texture_2d(path):
    surface = pygame.image.load(path)
    image_data = pygame.image.tostring(surface, "RGBA", True)
    width, height = surface.get_size()
    
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    
    # Configurações de repetição (importante para o asfalto)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    # Cria a textura propriamente dita
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)

    # Filtros de redimensionamento
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    return tex_id

road_tex = texture_2d("gato_medonho.jpg")
grass_tex = texture_2d("cachorro.jpg")

spawn_timer = 0
speed = 0.0
acel = 0.2
fric = 0.992
running = True

while running:
    clock.tick(30)
    glClearColor(0.5, 0.8, 1.0, 1)  # céu
    glClear(GL_COLOR_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                speed += acel
            if event.key == pygame.K_LEFT and current_lane > 0:
                current_lane -= 1
            if event.key == pygame.K_RIGHT and current_lane < 2:
                current_lane += 1
    keys = pygame.key.get_pressed()
    fric = 0.9 if keys[pygame.K_s] else 0.992
    speed *= fric
    if speed < 0.1:
        speed = 0.0
    if speed == 0.0:
        spawnable = False
    else:
        spawnable = True

    player_x = lane_positions[current_lane]

    spawn_timer += 1
    
    if spawn_timer > 50:
        spawn_obstacle()
        spawn_timer = 0

    move_obstacles(speed)

    road_offset += speed * 2

    draw_scenery()
    draw_road()
    draw_player()
    draw_obstacles()

    if check_collision():
        print("Game Over!")
        running = False

    pygame.display.flip()

pygame.quit()