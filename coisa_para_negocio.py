import pygame
import sys

# Inicialização do Pygame
pygame.init()

# Configurações da Janela
LARGURA, ALTURA = 800, 400
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Simulador de Pedal de Bicicleta")
pygame.display.set_icon(pygame.image.load("gato_medonho.jpg"))

# Cores
BRANCO = (255, 255, 255)
AZUL = (30, 144, 255)
CINZA = (200, 200, 200)
PRETO = (0, 0, 0)

# Variáveis da Física do Pedal
velocidade = 0.0          # Velocidade atual
aceleracao = 0.8         # O "impulso" dado a cada pedalada
friccao = 0.992           # Redução natural da velocidade (resistência do ar/pneu)
marcha = 1

# Fonte
fonte = pygame.font.SysFont("Arial", 24)

relogio = pygame.time.Clock()

while True:
    tela.fill(BRANCO)
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # Lógica de Input Alternado (Simulando o pé esquerdo e direito)
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_w:
                velocidade += aceleracao
            if evento.key == pygame.K_e:
                if marcha < 8:
                    aceleracao += 0.5
                    marcha += 1
            if evento.key == pygame.K_q:
                if marcha > 0:
                    aceleracao -= 0.5
                    marcha -= 1

    # Aplicar Fricção (a velocidade diminui gradualmente)
    velocidade *= friccao
    if velocidade < 0.1:
        velocidade = 0

    # Interface Visual
    # Barra de Velocidade (Velocímetro)
    pygame.draw.rect(tela, CINZA, (100, 200, 600, 50))
    pygame.draw.rect(tela, AZUL, (100, 200, velocidade * 20, 50)) # Multiplicador para visualização
    
    # Instruções
    texto_instrucao = fonte.render(f"Aperte \"W\" para andar", True, PRETO)
    texto_vel = fonte.render(f"Velocidade: {velocidade:.2f} km/h\nMarcha: {marcha}", True, PRETO)
    
    tela.blit(texto_instrucao, (100, 100))
    tela.blit(texto_vel, (100, 150))
    
    # Desenho visual do "Pedal" (Apenas estético)
    pygame.draw.circle(tela, AZUL, (400, 320), 30)

    pygame.display.flip()
    relogio.tick(60) # 60 FPS