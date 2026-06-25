import pygame
from sys import exit
import random
import math
from pathlib import Path


# ==========================================
# 1. INICIALIZAÇÃO E CONFIGURAÇÃO DA TELA
# ==========================================
pygame.init()
tela = pygame.display.set_mode((1000, 700))
pygame.display.set_caption("Batalha Naval - Pirate Escape")
relogio = pygame.time.Clock()

diretorio_raiz = Path(__file__).parent.resolve()
pasta_arquivos = diretorio_raiz



# ==========================================
# 2. CARREGAMENTO DE ASSETS (SONS E IMAGENS)
# ==========================================

# --- Sons e Música ---
pygame.mixer.music.load(pasta_arquivos / "sons" / "trilhas" / "musica.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)  # Loop infinito

som_ondas = pygame.mixer.Sound(pasta_arquivos / "sons" / "trilhas" / "ondas.mp3")
som_ondas.set_volume(0.2)
som_ondas.play(-1)  # Loop infinito

som_canhao = pygame.mixer.Sound(pasta_arquivos / "sons" / "efeitos" / "disparo.wav")
som_dano = pygame.mixer.Sound(pasta_arquivos /"sons" / "efeitos" / "som_dano.wav")
som_canhao.set_volume(0.5)
som_barco_quebrando = pygame.mixer.Sound(pasta_arquivos / "sons" / "efeitos" / "barco_quebrando.mp3")
som_barco_quebrando.set_volume(0.1)

# --- Capitão ---
capitao_png = pygame.image.load(pasta_arquivos / "sprites" / "sprite_capitao" / "capitao.png")
capitao_png = pygame.transform.scale(capitao_png, (60, 70))
rect_capitao = capitao_png.get_rect()
rect_capitao.x, rect_capitao.y = 400, 500
vel_x_capitao = 0
vel_y_capitao = 0
aceleracao = 0.5    # O quanto ele ganha de velocidade por frame
atrito = 0.95       # O quanto da velocidade ele mantém (0.95 = perde 8% por frame)
velocidade_max = 4.5  # Limite para o barco não virar um foguete

# --- Pirata Inimigo ---
pirata_png = pygame.image.load(pasta_arquivos / "sprites" / "sprite_pirata" / "pirata.png")
pirata_png = pygame.transform.scale(pirata_png, (70, 80))
rect_pirata = pirata_png.get_rect()
rect_pirata.x, rect_pirata.y = random.randint(50, 750), random.randint(50, 300)
velocidade_pirata = 2
timer_tiro_inimigo = 0
balas_inimigo = []

# --- Boss ---
boss_png = pygame.image.load(pasta_arquivos / "sprites" / "sprite_boss"/ "boss.png")
boss_png = pygame.transform.scale(boss_png, (130, 150))
vidas_boss = 20
rect_boss = boss_png.get_rect(center=(500, -150))
velocidade_boss = 1.5

# --- Canhão (Projéteis) ---
bala_img = pygame.image.load(pasta_arquivos / "sprites" / "sprite_canhao" / "bola_canhao.png")
bala_img = pygame.transform.scale(bala_img, (20, 20))
balas_canhao = []
tempo_recarga = 0

# ==========================================
# 3. VARIÁVEIS GLOBAIS, CORES E FONTES
# ==========================================
AZUL_OCEANO = (30, 144, 255)
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (0, 255, 0)
AMARELO = (255, 255, 0)
VERMELHO = (255, 0, 0)
CINZA = (50, 50, 50)
CINZA_ESCURO = (100, 100, 100)

pontos = 0
vidas = 3
vidas_pirata = 5
contador_de_frames = 0
rastros_particulas = []
rastros_piratas = []
timer_flash = 0
timer_flash_inimigo = 0
estagio = "NORMAL" 
angulo_capitao = 0
angulo_pirata = 0
piratas_derrotados = 0
pos_flashI = [0, 0]

fonte_titulo = pygame.font.SysFont("arial", 60, True, False)
fonte_texto = pygame.font.SysFont("arial", 30, False, False)

estado_jogo = "MENU"

# ==========================================
# 4. LOOP PRINCIPAL DO JOGO
# ==========================================
while True:
    relogio.tick(60) 
    
    # 4.1 TRATAMENTO DE EVENTOS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos_mouse = pygame.mouse.get_pos()
            
            # Lógica de tiro do Capitão (dentro do jogo)
            if estado_jogo == "JOGANDO" and tempo_recarga == 0:
                mouse_x, mouse_y = pos_mouse
                dx = mouse_x - rect_capitao.centerx
                dy = mouse_y - rect_capitao.centery
                dist = (dx**2 + dy**2) ** 0.5
                
                if dist != 0:
                    vel_x = (dx / dist) * 10
                    vel_y = (dy / dist) * 10
                    nova_bala = bala_img.get_rect(center=rect_capitao.center)
                    som_canhao.play()
                    balas_canhao.append([nova_bala, vel_x, vel_y])
                    tempo_recarga = 40

        if event.type == pygame.KEYDOWN:
            if estado_jogo == "MENU":
                if event.key == pygame.K_SPACE:
                    rect_capitao.center = (400, 500)
                    rect_pirata.center = (random.randint(50, 750), random.randint(50, 300))
                    pontos = 0
                    vidas = 3
                    vidas_pirata = 5
                    velocidade_pirata = 2
                    estado_jogo = "JOGANDO"
            
            elif estado_jogo == "GAMEOVER":
                if event.key == pygame.K_r:
                    estado_jogo = "MENU"

    # 4.2 LÓGICA DO JOGO (CALCULOS E ATUALIZAÇÕES)
    tela.fill(AZUL_OCEANO) 

    if estado_jogo == "MENU":
        titulo = fonte_titulo.render("PIRATE ESCAPE", True, BRANCO)
        instrucao = fonte_texto.render("Aperte ESPAÇO para navegar", True, PRETO)
        rect_titulo = titulo.get_rect(center=(500, 200))
        rect_instrucao = instrucao.get_rect(center=(500, 300))
        tela.blit(titulo, rect_titulo)
        tela.blit(instrucao, rect_instrucao)

    elif estado_jogo == "JOGANDO":
        # Temporizadores e Pontuação
        contador_de_frames += 1
        timer_tiro_inimigo += 1
        if tempo_recarga > 0:
            tempo_recarga -= 1

        if timer_flash > 0:
            tela.fill((255, 0, 0)) 
            timer_flash -= 1

        if contador_de_frames >= 60:
            pontos += 1
            contador_de_frames = 0
            if pontos % 10 == 0:
                velocidade_pirata += 0.5
        
        # --- LÓGICA DE MOVIMENTAÇÃO DO BOSS
        if estagio == "BOSS":
            if rect_boss.y < 100: # Desce até aparecer
                rect_boss.y += velocidade_boss
            
            # Movimento lateral
            rect_boss.x += velocidade_boss
            if rect_boss.right > 950 or rect_boss.left < 50:
                velocidade_boss *= -1

        # Lógica de Tiro Inimigo
       

        # Partículas de rastro do Barco
        rastros_particulas.append([rect_capitao.centerx, rect_capitao.centery, 15])
        for p in rastros_particulas[:]:
            p[2] -= 0.5
            pygame.draw.circle(tela, BRANCO, (int(p[0]), int(p[1])), int(p[2]))
            if p[2] <= 0:
                rastros_particulas.remove(p)
        
        rastros_piratas.append([rect_pirata.centerx, rect_pirata.centery, 25])
        for t in rastros_piratas [:]:
            t[2] -= 0.5
            pygame.draw.circle(tela, CINZA_ESCURO, (int(t[0]), int(t[1])), int(t[2]))
            if t[2] <= 0:
                rastros_piratas.remove(t)
                

        # --- Movimento Suave do Capitão ---
        teclas = pygame.key.get_pressed()
        
        # Aceleração baseada nas teclas
        if teclas[pygame.K_w]: vel_y_capitao -= aceleracao
        if teclas[pygame.K_s]: vel_y_capitao += aceleracao
        if teclas[pygame.K_a]: vel_x_capitao -= aceleracao
        if teclas[pygame.K_d]: vel_x_capitao += aceleracao

        # Aplica o Atrito (faz o barco parar gradualmente)
        vel_x_capitao *= atrito
        vel_y_capitao *= atrito

        # Limita a velocidade máxima
        vel_x_capitao = max(-velocidade_max, min(vel_x_capitao, velocidade_max))
        vel_y_capitao = max(-velocidade_max, min(vel_y_capitao, velocidade_max))

        # Atualiza a posição real
        rect_capitao.x += vel_x_capitao
        rect_capitao.y += vel_y_capitao
        rect_capitao.clamp_ip(tela.get_rect())

        # Rotação baseada na velocidade acumulada (mais orgânico)
        # Usamos um pequeno "threshold" (0.1) para não resetar o ângulo quando parado
        if abs(vel_x_capitao) > 0.1 or abs(vel_y_capitao) > 0.1:
            angulo_capitao = math.degrees(math.atan2(-vel_y_capitao, vel_x_capitao)) - 90
            
        
        # IA do Pirata 
        # Calcula distância e direção
        if estagio == "NORMAL":
            dx = rect_capitao.centerx - rect_pirata.centerx
            dy = rect_capitao.centery - rect_pirata.centery
            dist = math.hypot(dx, dy) # Função que calcula a hipotenusa (distância)
        
            if dist > 0:
                vx, vy = dx / dist, dy / dist # Vetor direção
                if dist > 250: # Perseguição
                    rect_pirata.x += vx * velocidade_pirata
                    rect_pirata.y += vy * velocidade_pirata
                elif dist < 150: # Afastamento
                    rect_pirata.x -= vx * velocidade_pirata
                    rect_pirata.y -= vy * velocidade_pirata
                else: # Movimento Lateral (Cercar)
                    rect_pirata.x += vy * velocidade_pirata
                    rect_pirata.y -= vx * velocidade_pirata
            angulo_pirata = math.degrees(math.atan2(-vy, vx)) - 90
        

        # Hitboxes e Colisão Direta
        hitbox_capitao = rect_capitao.inflate(-10, -10)
        hitbox_pirata = rect_pirata.inflate(-10, -10)
        if estagio == "NORMAL" and hitbox_capitao.colliderect(hitbox_pirata):
            vidas -= 1
            timer_flash = 5
            som_dano.play()
            rect_pirata.center = (random.randint(50, 750), random.randint(50, 300))
            if vidas <= 0: estado_jogo = "GAMEOVER"

        # Lógica das Balas do Capitão
        for dados_bala in balas_canhao[:]:
            rb = dados_bala[0]
            rb.x += dados_bala[1]
            rb.y += dados_bala[2]
            tela.blit(bala_img, rb)
            removida = False # Controle para não remover a mesma bala duas vezes

            # 1. Colisão com Pirata Comum (Só acontece no estágio Normal)
            if estagio == "NORMAL" and rb.colliderect(hitbox_pirata):
                vidas_pirata -= 1
                pontos += 10
                balas_canhao.remove(dados_bala)
                removida = True
                if vidas_pirata <= 0:
                    som_barco_quebrando.play()
                    pos_flashI = rect_pirata.center
                    piratas_derrotados += 1
                    vidas_pirata = 5
                    timer_flash_inimigo = 10
                    rect_pirata.center = (random.randint(50, 750), random.randint(50, 300))
                    if piratas_derrotados >= 2:
                        print("O Boss apareceu!")
                        estagio = "BOSS"
                        rect_pirata.center = (-1000, -1000)
                        balas_inimigo.clear()

            # 2. Colisão com o BOSS (Só acontece no estágio Boss)
            elif estagio == "BOSS" and rb.colliderect(rect_boss.inflate(-30, -30)):
                vidas_boss -= 1
                balas_canhao.remove(dados_bala)
                removida = True
                if vidas_boss <= 0:
                    # Aqui você pode decidir se o jogo acaba ou se ele vence!
                    estado_jogo = "GAMEOVER" 

            # 3. Remover bala se sair da tela (e se ainda não foi removida por colisão)
            if not removida and not tela.get_rect().colliderect(rb):
                balas_canhao.remove(dados_bala)


        # Lógica das Balas Inimigas
        
        # 1. Momento do Disparo (Só cria a bala se for o estágio NORMAL)
        if estagio == "NORMAL" and timer_tiro_inimigo >= 50:
            som_canhao.play()
            nova_bala_inimiga = bala_img.get_rect(center=rect_pirata.center)
            
            # Cálculo da direção (precisa estar aqui para a bala saber para onde ir)
            dir_x = rect_capitao.centerx - rect_pirata.centerx
            dir_y = rect_capitao.centery - rect_pirata.centery
            distancia = math.hypot(dir_x, dir_y)
            
            if distancia != 0:
                vel_x = (dir_x / distancia) * 7
                vel_y = (dir_y / distancia) * 7
                balas_inimigo.append([nova_bala_inimiga, vel_x, vel_y])
            
            timer_tiro_inimigo = 0 # Reseta o timer após disparar

        # 2. Atualização das Balas (Move e Desenha todas as balas que já existem)
        # Esse for deve ficar FORA do if do timer
        for dados_bala_inimiga in balas_inimigo[:]:
            rbi = dados_bala_inimiga[0]
            rbi.x += dados_bala_inimiga[1]
            rbi.y += dados_bala_inimiga[2]
            tela.blit(bala_img, rbi)

            # Colisão com o Capitão
            if rbi.colliderect(hitbox_capitao):
                vidas -= 1
                timer_flash = 5
                som_dano.play()
                balas_inimigo.remove(dados_bala_inimiga)
                if vidas <= 0: estado_jogo = "GAMEOVER"
            
            # Remove se sair da tela
            elif not tela.get_rect().colliderect(rbi):
                balas_inimigo.remove(dados_bala_inimiga)
                
                
                
        # 4.3 RENDERIZAÇÃO (DESENHO DOS ELEMENTOS NA TELA)
        
        # Sprites
        # 3. RENDERIZAÇÃO COM ROTAÇÃO
        # Desenha Capitão
        img_cap_rot = pygame.transform.rotate(capitao_png, angulo_capitao)
        rect_cap_rot = img_cap_rot.get_rect(center=rect_capitao.center)
        tela.blit(img_cap_rot, rect_cap_rot)

        # Desenha Inimigo
        if estagio == "NORMAL":
            img_pir_rot = pygame.transform.rotate(pirata_png, angulo_pirata)
            rect_pir_rot = img_pir_rot.get_rect(center=rect_pirata.center)
            tela.blit(img_pir_rot, rect_pir_rot)
            
        # Desenha Boss
        tela.blit(boss_png, rect_boss)

        # UI: Barra de Vida Capitão
        cor_barra = VERDE 
        if vidas == 2: cor_barra = AMARELO
        elif vidas == 1: cor_barra = VERMELHO
        pygame.draw.rect(tela, CINZA, (10, 50, 150, 20))   
        pygame.draw.rect(tela, cor_barra, (10, 50, 50 * vidas, 20))

        # UI: Barra de Vida Inimigo
        largura_barra_fundo = 70  # Largura fixa da barra cinza
        largura_vida_atual = (max(0, vidas_pirata) / 5) * largura_barra_fundo
        pygame.draw.rect(tela, CINZA, (rect_pirata.centerx - largura_barra_fundo//2, rect_pirata.y - 15, largura_barra_fundo, 8))
        pygame.draw.rect(tela, VERMELHO, (rect_pirata.centerx - largura_barra_fundo//2, rect_pirata.y - 15, largura_vida_atual, 8))

        # UI: Barra vida BOSS
        if estagio == "BOSS":
            largura_max_boss = 400
            # Regra de 3 para a largura: (vidas_atuais / vidas_totais) * largura_total
            largura_atual_boss = (vidas_boss / 20) * largura_max_boss
            pygame.draw.rect(tela, CINZA, (300, 20, largura_max_boss, 25))
            pygame.draw.rect(tela, VERMELHO, (300, 20, largura_atual_boss, 25))
            
            # Texto "BOSS" em cima da barra
            txt_boss = fonte_texto.render("KRAKEN SHIP", True, BRANCO)
            tela.blit(txt_boss, (430, 45))

        #UI: Flash inimigo
        if timer_flash_inimigo > 0:
            pygame.draw.circle(tela, BRANCO, pos_flashI, 50)
            timer_flash_inimigo -= 1

        # UI: Texto do Placar
        texto_placar = fonte_texto.render(f"Vidas: {vidas} | Mar: {pontos}m", True, BRANCO)
        tela.blit(texto_placar, (10, 10))

    elif estado_jogo == "GAMEOVER":
        titulo = fonte_titulo.render("NAUFRÁGIO!", True, (255, 0, 0))
        instrucao = fonte_texto.render(f"Score: {pontos}m | Aperte 'R' para o Porto", True, BRANCO)
        rect_naufragio = titulo.get_rect(center=(500, 200))
        rect_instrucao = instrucao.get_rect(center=(500, 300))
        tela.blit(titulo, rect_naufragio)
        tela.blit(instrucao, rect_instrucao)

    pygame.display.update()