import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import math

# =========================
# Inicialização
# =========================
pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

pygame.event.set_grab(True)   # trava o mouse (FPS feel)
pygame.mouse.set_visible(False)

gluPerspective(70, display[0] / display[1], 0.1, 100.0)
glEnable(GL_DEPTH_TEST)

clock = pygame.time.Clock()

# =========================
# Estado do jogo
# =========================
pos = [0, 1.8, 5]   # posição do jogador
yaw, pitch = 0, 0   # ângulos da câmera

enemies = []
round_num = 1
spawn_timer = 0

# =========================
# Funções de desenho
# =========================
def draw_floor():
    """Desenha o chão da arena."""
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_QUADS)
    glVertex3f(-20, 0, -20)
    glVertex3f(20, 0, -20)
    glVertex3f(20, 0, 20)
    glVertex3f(-20, 0, 20)
    glEnd()


def draw_cube(x, y, z, size=0.5):
    """Desenha um cubo na posição (x,y,z)."""
    glPushMatrix()
    glTranslatef(x, y, z)

    glBegin(GL_QUADS)
    # frente
    glVertex3f(-size, -size, size)
    glVertex3f(size, -size, size)
    glVertex3f(size, size, size)
    glVertex3f(-size, size, size)

    # trás
    glVertex3f(-size, -size, -size)
    glVertex3f(size, -size, -size)
    glVertex3f(size, size, -size)
    glVertex3f(-size, size, -size)
    glEnd()

    glPopMatrix()


def draw_enemies():
    """Desenha todos os inimigos."""
    glColor3f(1, 0, 0)
    for e in enemies:
        draw_cube(e[0], e[1], e[2], 0.5)

# =========================
# Lógica de inimigos
# =========================
def spawn_enemy():
    """Cria um inimigo em posição aleatória ao redor do jogador."""
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(8, 15)
    x = pos[0] + math.cos(angle) * dist
    z = pos[2] + math.sin(angle) * dist
    enemies.append([x, 0.5, z, 100])  # hp inicial


def move_enemies():
    """Move inimigos em direção ao jogador."""
    for e in enemies:
        dx, dz = pos[0] - e[0], pos[2] - e[2]
        dist = math.sqrt(dx * dx + dz * dz)
        if dist > 0:
            e[0] += (dx / dist) * 0.02
            e[2] += (dz / dist) * 0.02


def shoot():
    """Atira e verifica se algum inimigo foi atingido."""
    global enemies
    hit = []
    for e in enemies:
        dx, dz = e[0] - pos[0], e[2] - pos[2]
        angle_to_enemy = math.degrees(math.atan2(dz, dx))
        diff = (angle_to_enemy - yaw) % 360

        if diff < 10 or diff > 350:  # dentro do campo de visão
            dist = math.sqrt(dx * dx + dz * dz)
            if dist < 10:  # alcance
                e[3] -= 50
                if e[3] <= 0:
                    hit.append(e)

    for e in hit:
        enemies.remove(e)


def next_round():
    """Avança para a próxima rodada e gera novos inimigos."""
    global round_num
    round_num += 1
    for _ in range(round_num * 2):
        spawn_enemy()

# =========================
# Setup inicial
# =========================
for _ in range(3):
    spawn_enemy()

# =========================
# Loop principal
# =========================
running = True
while running:
    dt = clock.tick(60)

    # Movimento da câmera (mouse look)
    mx, my = pygame.mouse.get_rel()
    yaw += mx * 0.1
    pitch = max(-89, min(89, pitch - my * 0.1))

    # Movimento do jogador
    keys = pygame.key.get_pressed()
    speed = 0.1
    forward = [math.cos(math.radians(yaw)), 0, math.sin(math.radians(yaw))]
    right = [-forward[2], 0, forward[0]]

    if keys[K_w]: pos[0] += forward[0] * speed; pos[2] += forward[2] * speed
    if keys[K_s]: pos[0] -= forward[0] * speed; pos[2] -= forward[2] * speed
    if keys[K_a]: pos[0] -= right[0] * speed; pos[2] -= right[2] * speed
    if keys[K_d]: pos[0] += right[0] * speed; pos[2] += right[2] * speed

    # Eventos
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == MOUSEBUTTONDOWN:
            shoot()

    # Lógica dos inimigos
    move_enemies()
    spawn_timer += 1
    if spawn_timer > 120:
        spawn_enemy()
        spawn_timer = 0
    if len(enemies) == 0:
        next_round()

    # Renderização
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glRotatef(pitch, 1, 0, 0)
    glRotatef(-yaw, 0, 1, 0)
    glTranslatef(-pos[0], -pos[1], -pos[2])

    draw_floor()
    draw_enemies()
    pygame.display.flip()

pygame.quit()
