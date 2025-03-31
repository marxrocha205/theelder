# Importa a biblioteca principal do Pygame Zero para rodar o jogo.
import pgzrun
# Importa funções auxiliares da biblioteca pgzhelper (se usada/necessária).
from pgzhelper import *
# Importa a biblioteca 'time' para funções relacionadas a tempo (ex: cooldowns, animações).
import time
# REMOVIDO: import pygame

# Define a largura da tela do jogo em pixels.
WIDTH = 800
# Define a altura da tela do jogo em pixels.
HEIGHT = 600

# Cria uma lista com os nomes dos arquivos de imagem para a animação do jogador parado.
idle_images = ["pidle1.png", "pidle2.png"]
# Cria uma lista com os nomes dos arquivos de imagem para a animação do jogador correndo.
run_images = ["prun1.png", "prun2.png"]
# Define o nome do arquivo de imagem para o martelo.
hammer_image = "hammer.png"
# Define o nome do arquivo de imagem para o ícone do martelo (coletável).
icon_hammer_image = "hammer.png"

# Cria o objeto (Actor) do jogador, definindo a imagem inicial e a posição (x, y).
player = Actor(idle_images[0], (100, 300))
# Cria o objeto do martelo, iniciando fora da tela.
hammer = Actor(hammer_image, (-100, -100))
# Define a escala (tamanho) do martelo para 50% do original.
hammer.scale = 0.5
# Cria o objeto do ícone do martelo coletável, definindo imagem e posição.
icon_hammer = Actor(icon_hammer_image, (200, 350))
# Define a escala do ícone do martelo para 50%.
icon_hammer.scale = 0.5
# Cria o objeto (Actor) do inimigo, definindo imagem inicial e posição.
enemy = Actor(idle_images[0], (650, 400))
# Define a direção inicial do inimigo (-1 para esquerda, 1 para direita).
enemy.direction = -1
# Define a velocidade de movimento horizontal do inimigo.
enemy.speed = 1.5
# Define o estado inicial do inimigo como vivo.
enemy.alive = True
# Define se a imagem do inimigo deve ser espelhada horizontalmente no início (True para olhar à esquerda).
enemy.flip_x = True
# Define a velocidade vertical inicial do inimigo (para cálculos de gravidade).
enemy_vy = 0
# Define o estado inicial do inimigo como não estando no chão.
enemy_on_ground = False

# Cria um objeto Rect (retângulo) para representar a área clicável do botão de reset na tela de game over.
reset_button = Rect((WIDTH // 2 - 80, HEIGHT // 2 + 50), (160, 50))

# Define o estado inicial do jogo como "start" (mostrando a tela de início).
game_state = "start"
# Variável (não usada diretamente na lógica final) para potencialmente controlar a animação de corrida.
is_running = False
# Contador de frames, usado para controlar o tempo das animações.
frame = 0
# Variável para guardar a última direção horizontal que o jogador estava olhando (para espelhamento da imagem). False = Direita, True = Esquerda.
pmirror = False
# Define se o martelo já foi coletado pelo jogador (inicialmente não).
hammer_collected = False
# Define se o martelo está atualmente arremessado (inicialmente não).
hammer_thrown = False
# Define se o jogador está no chão (começa True, assumindo a posição inicial).
on_ground = True
# Define a velocidade vertical inicial do jogador (0 = parado verticalmente).
vy = 0
# Define a força da gravidade que afeta jogador e inimigo a cada frame.
gravity = 0.5
# Define a força inicial do pulo (velocidade vertical negativa).
jump_strength = -12
# Define o número inicial de vidas do jogador.
player_lives = 3
# Define se o jogo está em estado de "Game Over" (inicialmente não).
game_over = False

# Define se o jogador está executando um dash (inicialmente não).
is_dashing = False
# Define a velocidade do jogador durante o dash.
dash_speed = 10
# Define a velocidade normal de movimento horizontal do jogador.
normal_speed = 5
# Define o tempo (em segundos) de espera antes de poder usar o dash novamente.
dash_cooldown = 1.5
# Armazena o tempo (timestamp) em que o último dash foi iniciado (0 no início).
last_dash_time = 0
# Cria uma lista vazia para armazenar informações das sombras do efeito de dash.
shadows = []

# Cria uma lista de objetos Rect (retângulos) que representam as plataformas físicas do jogo.
platforms = [
    Rect((0, 400), (200, 50)), # Plataforma 1: posição (x,y), dimensões (largura, altura)
    Rect((300, 350), (200, 50)), # Plataforma 2
    Rect((600, 450), (200, 50)), # Plataforma 3
    Rect((0, HEIGHT - 50), (WIDTH, 50)) # Plataforma do chão (base da tela)
]

# Define o início da função 'start_music'.
def start_music():
    # Inicia um bloco para tentar executar código que pode gerar erro (ex: arquivo não encontrado).
    try:
        # Tenta tocar o arquivo de música chamado "music" (procura na pasta 'music').
        music.play("music")
        # Define o volume da música para 30% do máximo.
        music.set_volume(0.5
                         )
    # Captura qualquer erro (Exceção) que ocorra no bloco 'try'.
    except Exception as e:
        # Imprime uma mensagem de aviso no console informando o erro ocorrido.
        print(f"Aviso: Erro ao iniciar música 'music': {e}")

# Define o início da função 'throw_hammer'.
def throw_hammer():
    # Declara que a função usará e/ou modificará as variáveis globais listadas.
    global hammer_thrown, hammer_collected, player
    # Verifica se o martelo foi coletado PELO jogador E se não está atualmente arremessado.
    if hammer_collected and not hammer_thrown:
        # Define a posição inicial do martelo arremessado como a posição atual do jogador.
        hammer.pos = player.pos
        # Define a orientação horizontal inicial do martelo (espelhamento) igual à do jogador.
        hammer.flip_x = player.flip_x
        # Define a velocidade horizontal do martelo (-8 se jogador olhando esquerda, 8 se direita).
        hammer.vx = -8 if player.flip_x else 8
        # Define o estado do martelo como arremessado.
        hammer_thrown = True
        # Inicia um bloco de tentativa para tocar o som.
        try:
            # Tenta tocar o arquivo de som chamado "throw" (procura na pasta 'sounds').
            sounds.throw.play()
        # Captura qualquer erro ao tentar tocar o som.
        except Exception as e:
            # Imprime uma mensagem de aviso se tocar o som falhar.
            print(f"Aviso: Erro ao tocar som 'throw': {e}")

# Define o início da função 'reset_game'.
def reset_game():
    # Declara as variáveis globais que serão modificadas (resetadas) pela função.
    global player_lives, game_over, hammer_collected, hammer_thrown, frame, enemy, shadows, vy, enemy_vy, on_ground, pmirror, is_dashing, player, icon_hammer

    # Reseta a posição do jogador para a inicial.
    player.pos = (100, 300);
    # Reseta a orientação horizontal do jogador para a direita (não espelhado).
    player.flip_x = False;
    # Reseta a variável de espelhamento para direita.
    pmirror = False
    # Reseta a velocidade vertical do jogador para 0.
    vy = 0;
    # Força o recálculo da colisão com o chão no próximo frame.
    on_ground = False
    # Reseta a posição do martelo para fora da tela.
    hammer.pos = (-100, -100);
    # Reseta o ângulo de rotação do martelo.
    hammer.angle = 0;
    # Reseta a orientação horizontal do martelo.
    hammer.flip_x = False
    # Reseta o estado de arremesso do martelo.
    hammer_thrown = False;
    # Reseta o estado de coleta do martelo.
    hammer_collected = False
    # Reseta a posição do ícone coletável do martelo.
    icon_hammer.pos = (200, 350)
    # Reseta o número de vidas do jogador para 3.
    player_lives = 3
    # Reseta a posição do inimigo para a inicial.
    enemy.pos = (650, 400);
    # Reseta o estado de vida do inimigo para vivo.
    enemy.alive = True;
    # Reseta a direção inicial do inimigo para esquerda.
    enemy.direction = -1;
    # Reseta a orientação inicial do inimigo para esquerda.
    enemy.flip_x = True
    # Reseta a velocidade vertical do inimigo.
    enemy_vy = 0;
    # Reseta o estado do inimigo em relação ao chão.
    enemy_on_ground = False
    # Reseta o estado de dash do jogador.
    is_dashing = False
    # Reseta o contador de frames.
    frame = 0
    # Limpa (esvazia) a lista de sombras do dash.
    shadows.clear()
    # Define o estado de "Game Over" como falso.
    game_over = False
    # Chama a função para (re)iniciar a música do jogo.
    start_music()

# Define o início da função 'update', chamada automaticamente a cada frame pelo Pygame Zero.
def update():
    # Declara todas as variáveis globais que podem ser lidas OU modificadas dentro desta função.
    global game_state, game_over, frame, player_lives, vy, on_ground, pmirror, is_dashing, last_dash_time, hammer_collected, hammer_thrown, enemy_vy, enemy_on_ground, shadows
    global player, enemy, icon_hammer

    # Verifica se o estado atual do jogo é "playing". A lógica principal só roda neste estado.
    if game_state == "playing":
        # Dentro do estado "playing", verifica se a flag "game_over" está ativa.
        if game_over:
            # Se for "Game Over", interrompe a execução da função 'update' para este frame (congela o jogo).
            return

        # --- Lógica Principal do Jogo ---
        # Obtém o tempo atual em segundos desde uma época de referência (usado para cooldowns, durações).
        current_time = time.time()
        # Define a velocidade horizontal atual do jogador como a velocidade normal (pode mudar no dash).
        current_speed = normal_speed

        # --- Lógica do Dash ---
        # Calcula se o tempo desde o último dash é maior que o cooldown permitido.
        can_dash = current_time - last_dash_time > dash_cooldown
        # Flag para indicar se um dash foi iniciado *neste* frame específico.
        perform_dash = False
        # Verifica se (Shift pressionado) E (Direita OU Esquerda pressionada) E (Cooldown terminou) E (Jogador está no chão).
        if (keyboard.lshift or keyboard.rshift) and (keyboard.right or keyboard.left) and can_dash and on_ground:
            # Ativa o estado de dash.
            is_dashing = True;
            # Armazena o tempo em que este dash começou.
            last_dash_time = current_time;
            # Marca que um dash foi iniciado neste frame.
            perform_dash = True
            # Verifica qual tecla de direção foi pressionada para definir a orientação do jogador.
            if keyboard.left: player.flip_x = True # Vira para esquerda.
            else: player.flip_x = False # Vira para direita.
            # Atualiza a variável de espelhamento com a direção do dash.
            pmirror = player.flip_x
            # Tenta tocar o som do dash.
            try: sounds.dash.play()
            # Captura e avisa sobre erros ao tocar som.
            except Exception as e: print(f"Aviso: Erro som 'dash': {e}")
            # Adiciona um dicionário com informações da sombra inicial do dash à lista 'shadows'.
            shadows.append({"x": player.x, "y": player.y, "time": current_time, "alpha": 200, "flip_x": player.flip_x})

        # Verifica se o jogador está atualmente em estado de dash.
        if is_dashing:
            # Define a duração do efeito do dash em segundos.
            dash_duration = 0.15
            # Verifica se o tempo desde o início do dash é menor ou igual à duração definida.
            if current_time - last_dash_time <= dash_duration:
                # Define a velocidade atual como a velocidade de dash (mais rápida).
                current_speed = dash_speed
                # Define a direção do movimento do dash (-1 para esquerda, 1 para direita) baseado na orientação do jogador.
                dash_move_direction = -1 if player.flip_x else 1
                # Move o jogador horizontalmente com a velocidade e direção do dash.
                player.x += dash_speed * dash_move_direction
                # Verifica se o número do frame é múltiplo de 3 (cria sombras intermitentes).
                if frame % 3 == 0:
                     # Adiciona outra sombra à lista durante o dash.
                     shadows.append({"x": player.x, "y": player.y, "time": current_time, "alpha": 150, "flip_x": player.flip_x})
            # Se o tempo do dash já passou.
            else:
                # Desativa o estado de dash.
                is_dashing = False

        # --- Movimento Normal do Jogador ---
        # Flag para indicar se houve movimento horizontal normal neste frame.
        moving_x = False
        # Só permite controle de movimento normal se o dash não estiver ativo.
        if not is_dashing:
            # Verifica se a tecla direita está pressionada.
            if keyboard.right:
                # Move o jogador para a direita com a velocidade atual (normal).
                player.x += current_speed;
                # Define a variável de espelhamento como False (olhando para direita).
                pmirror = False;
                # Define a orientação visual do jogador para a direita.
                player.flip_x = False;
                # Indica que houve movimento horizontal.
                moving_x = True
            # Verifica se a tecla esquerda está pressionada.
            elif keyboard.left:
                # Move o jogador para a esquerda com a velocidade atual.
                player.x -= current_speed;
                # Define a variável de espelhamento como True (olhando para esquerda).
                pmirror = True;
                # Define a orientação visual do jogador para a esquerda.
                player.flip_x = True;
                # Indica que houve movimento horizontal.
                moving_x = True

        # --- Animação do Jogador ---
        # Se está dando dash OU se movendo normalmente.
        if is_dashing or moving_x:
            # Define a imagem do jogador para um frame da animação de corrida (alterna baseado no frame).
            player.image = run_images[(frame // 6) % len(run_images)]
        # Se não está correndo nem dando dash (está parado).
        else:
            # Define a imagem do jogador para um frame da animação parado (alterna baseado no frame).
            player.image = idle_images[(frame // 15) % len(idle_images)];
            # Garante que a orientação visual (flip_x) corresponde à última direção (pmirror) quando parado.
            player.flip_x = pmirror

        # --- Pulo ---
        # Verifica se a tecla Espaço OU Seta Cima foi pressionada E se o jogador está no chão.
        if (keyboard.space or keyboard.up) and on_ground:
            # Define a velocidade vertical inicial para o valor de 'jump_strength' (negativo para subir).
            vy = jump_strength;
            # Define que o jogador não está mais no chão.
            on_ground = False
            # Tenta tocar o som de pulo.
            try: sounds.jump.play()
            # Captura e avisa sobre erros.
            except Exception as e: print(f"Aviso: Erro som 'jump': {e}")

        # --- Física do Jogador (Gravidade e Colisão com Plataformas) ---
        # Aplica a força da gravidade à velocidade vertical atual.
        vy += gravity;
        # Atualiza a posição vertical do jogador com base na velocidade vertical.
        player.y += vy
        # Assume que o jogador não está no chão até que uma colisão confirme o contrário.
        on_ground = False
        # Cria uma cópia do retângulo do jogador para verificar a colisão no próximo frame (ligeiramente abaixo).
        player_rect_next_frame = player.copy(); player_rect_next_frame.y += 1
        # Itera sobre cada plataforma na lista 'platforms'.
        for platform in platforms:
            # Verifica se o retângulo previsto do jogador colide com a plataforma atual.
            if player_rect_next_frame.colliderect(platform):
                # Verifica se o jogador estava caindo (vy >= 0) E se a parte de baixo do jogador está próxima ou abaixo do topo da plataforma.
                if vy >= 0 and player.bottom <= platform.top + (vy + gravity + 1):
                    # Verifica se o centro horizontal do jogador está dentro dos limites da plataforma (evita prender na lateral).
                    if player.centerx > platform.left and player.centerx < platform.right:
                        # Ajusta a posição da base do jogador para ficar exatamente sobre o topo da plataforma.
                        player.bottom = platform.top;
                        # Zera a velocidade vertical, pois o jogador pousou.
                        vy = 0;
                        # Define que o jogador está no chão.
                        on_ground = True;
                        # Interrompe o loop de verificação de plataformas, pois o chão foi encontrado.
                        break
                # Se estava subindo (vy < 0) E colidiu com a parte de baixo da plataforma.
                elif vy < 0 and player.top >= platform.bottom + vy - 1:
                     # Verifica se a colisão foi horizontalmente sobre a plataforma.
                     if player.centerx > platform.left and player.centerx < platform.right:
                        # Ajusta a posição do topo do jogador para ficar encostado na base da plataforma (bateu a cabeça).
                        player.top = platform.bottom;
                        # Zera a velocidade vertical.
                        vy = 0;
                        # Interrompe o loop.
                        break

        # --- Coleta e Arremesso do Martelo ---
        # Verifica se o jogador está colidindo com o ícone do martelo E se o martelo ainda não foi coletado.
        if player.colliderect(icon_hammer) and not hammer_collected:
            # Marca o martelo como coletado.
            hammer_collected = True;
            # Move o ícone do martelo para fora da tela para que não possa ser coletado novamente.
            icon_hammer.pos = (-100, -100)
            # Tenta tocar o som de coleta.
            try: sounds.collect.play()
            # Captura e avisa sobre erros.
            except Exception as e: print(f"Aviso: Erro som 'collect': {e}")
        # Verifica se a tecla 'Z' está pressionada.
        if keyboard.z:
            # Chama a função para tentar arremessar o martelo.
            throw_hammer()

        # --- Movimentação do Martelo ---
        # Verifica se o martelo está no estado arremessado.
        if hammer_thrown:
            # Move o martelo horizontalmente com base na sua velocidade 'vx'.
            hammer.x += hammer.vx;
            # Rotaciona o martelo adicionando 15 graus ao seu ângulo.
            hammer.angle += 15
            # Verifica se o martelo saiu completamente dos limites da tela (esquerda, direita, cima, baixo).
            if hammer.right<0 or hammer.left>WIDTH or hammer.bottom<0 or hammer.top>HEIGHT:
                # Marca o martelo como não arremessado.
                hammer_thrown = False;
                # Move o martelo para fora da tela.
                hammer.pos = (-100, -100)
        # Se o martelo foi coletado, MAS NÃO está arremessado (está sendo segurado).
        elif hammer_collected:
            # Mantém o martelo sem rotação (ângulo 0).
            hammer.angle = 0;
            # Define a orientação horizontal (espelhamento) do martelo igual à do jogador.
            hammer.flip_x = player.flip_x
            # Verifica a direção do jogador para posicionar o martelo.
            if player.flip_x: # Se jogador olhando para esquerda.
                # Posiciona o martelo um pouco à esquerda do centro do jogador.
                hammer.x = player.x - 15
            # Se jogador olhando para direita.
            else:
                # Posiciona o martelo um pouco à direita do centro do jogador.
                hammer.x = player.x + 15
            # Posiciona o martelo verticalmente um pouco abaixo do centro Y do jogador.
            hammer.y = player.y + 5

        # --- Física e Movimento do Inimigo ---
        # Verifica se o inimigo está vivo para processar sua lógica.
        if enemy.alive:
            # Armazena a velocidade vertical anterior (útil para detecção de pouso).
            enemy_vy_prev = enemy_vy;
            # Aplica a gravidade à velocidade vertical do inimigo.
            enemy_vy += gravity;
            # Atualiza a posição vertical do inimigo.
            enemy.y += enemy_vy
            # Variável para armazenar a plataforma em que o inimigo está (se houver).
            current_platform = None;
            # Assume que o inimigo não está no chão até que a colisão confirme.
            enemy_on_ground = False
            # Cria uma cópia do retângulo do inimigo para previsão de colisão vertical.
            enemy_rect_next_frame = enemy.copy(); enemy_rect_next_frame.y += 1
            # Itera sobre todas as plataformas.
            for platform in platforms:
                # Verifica se o inimigo (na posição prevista) colide com a plataforma.
                if enemy_rect_next_frame.colliderect(platform):
                    # Verifica se estava caindo (velocidade anterior >= 0) E colidiu com o topo da plataforma.
                    if enemy_vy_prev >= 0 and enemy.bottom <= platform.top + (enemy_vy + gravity + 1):
                        # Verifica se está horizontalmente sobre a plataforma.
                        if enemy.centerx > platform.left and enemy.centerx < platform.right:
                            # Ajusta a posição do inimigo para ficar sobre a plataforma.
                            enemy.bottom = platform.top;
                            # Zera a velocidade vertical.
                            enemy_vy = 0;
                            # Marca que está no chão.
                            enemy_on_ground = True;
                            # Armazena a referência da plataforma atual.
                            current_platform = platform;
                            # Sai do loop de plataformas.
                            break
                    # Verifica se estava subindo (vy < 0) E colidiu com a base da plataforma.
                    elif enemy_vy < 0 and enemy.top >= platform.bottom + enemy_vy - 1:
                        # Verifica se está horizontalmente sob a plataforma.
                        if enemy.centerx > platform.left and enemy.centerx < platform.right:
                            # Ajusta a posição do topo do inimigo.
                            enemy.top = platform.bottom;
                            # Zera a velocidade vertical.
                            enemy_vy = 0;
                            # Sai do loop.
                            break
            # Se o inimigo está no chão E sabemos em qual plataforma ele está.
            if enemy_on_ground and current_platform is not None:
                # Verifica se está indo para a direita E atingiu a borda direita da plataforma atual.
                if enemy.direction == 1 and enemy.right >= current_platform.right:
                    # Ajusta a posição para não ultrapassar a borda.
                    enemy.right = current_platform.right;
                    # Inverte a direção para esquerda.
                    enemy.direction = -1;
                    # Vira o sprite do inimigo para a esquerda.
                    enemy.flip_x = True
                # Verifica se está indo para a esquerda E atingiu a borda esquerda da plataforma atual.
                elif enemy.direction == -1 and enemy.left <= current_platform.left:
                    # Ajusta a posição para não ultrapassar a borda.
                    enemy.left = current_platform.left;
                    # Inverte a direção para direita.
                    enemy.direction = 1;
                    # Vira o sprite do inimigo para a direita.
                    enemy.flip_x = False
                # Move o inimigo horizontalmente na direção e velocidade atuais.
                enemy.x += enemy.direction * enemy.speed;
                # Define a imagem do inimigo para a animação de corrida.
                enemy.image = run_images[(frame // 10) % len(run_images)]
            # Se o inimigo não está no chão (está caindo).
            elif not enemy_on_ground:
                 # Define a imagem do inimigo para a animação de parado/queda.
                 enemy.image = idle_images[0]

        # --- Colisões de Combate ---
        # Verifica se o martelo está arremessado, se o inimigo está vivo E se há colisão entre eles.
        if hammer_thrown and enemy.alive and hammer.colliderect(enemy):
            # Marca o inimigo como morto.
            enemy.alive = False;
            # Marca o martelo como não arremessado (para após atingir).
            hammer_thrown = False;
            # Move o martelo para fora da tela.
            hammer.pos = (-100, -100)
            # Tenta tocar o som de acerto.
            try: sounds.hit.play()
            # Captura e avisa sobre erros.
            except Exception as e: print(f"Aviso: Erro som 'hit': {e}")
        # Verifica se o inimigo está vivo E se há colisão entre jogador e inimigo.
        if enemy.alive and player.colliderect(enemy):
            # Verifica se o jogador está caindo (vy > 1) E se a colisão foi na parte superior do inimigo (pulo na cabeça).
            if vy > 1 and player.bottom < enemy.centery + 5 and player.bottom > enemy.top:
                # Marca o inimigo como morto.
                enemy.alive = False;
                # Faz o jogador dar um pequeno pulo após derrotar o inimigo.
                vy = jump_strength * 0.7;
                # Marca o jogador como não estando no chão.
                on_ground = False
                # Tenta tocar o som de pisão.
                try: sounds.stomp.play()
                # Captura e avisa sobre erros.
                except Exception as e: print(f"Aviso: Erro som 'stomp': {e}")
            # Se a colisão não foi na cabeça E o jogador não está dando dash (invulnerável).
            elif not is_dashing :
                # Jogador perde uma vida.
                player_lives -= 1
                # Verifica o lado da colisão para aplicar o empurrão (knockback).
                if player.centerx < enemy.centerx: player.x -= 30 # Empurra para esquerda.
                else: player.x += 30 # Empurra para direita.
                # Faz o jogador dar um pequeno pulo para trás/cima.
                vy = -5;
                # Marca o jogador como não estando no chão.
                on_ground = False
                # Tenta tocar o som de dano.
                try: sounds.damage.play()
                # Captura e avisa sobre erros.
                except Exception as e: print(f"Aviso: Erro som 'damage': {e}")
                # Verifica se as vidas do jogador acabaram.
                if player_lives <= 0:
                    # Define o estado de Game Over como True.
                    game_over = True
                    # Tenta parar a música e tocar o som de game over.
                    try: music.stop(); sounds.gameover.play()
                    # Captura e avisa sobre erros.
                    except Exception as e: print(f"Aviso: Erro sons/música gameover: {e}")

        # --- Limites da Tela e Queda ---
        # Verifica se o jogador ultrapassou o limite esquerdo da tela.
        if player.left < 0: player.left = 0 # Corrige a posição para 0.
        # Verifica se o jogador ultrapassou o limite direito da tela.
        if player.right > WIDTH: player.right = WIDTH # Corrige a posição para WIDTH.
        # Verifica se o jogador caiu para fora da tela por baixo (com uma margem de tolerância).
        if player.top > HEIGHT + 50:
             # Jogador perde uma vida.
             player_lives -=1
             # Verifica se as vidas acabaram após cair.
             if player_lives <= 0:
                 # Ativa o Game Over.
                 game_over = True
                 # Tenta parar a música e tocar o som de game over.
                 try: music.stop(); sounds.gameover.play()
                 # Captura e avisa sobre erros.
                 except Exception as e: print(f"Aviso: Erro sons/música gameover: {e}")
             # Se ainda tem vidas após cair.
             else:
                 # Reseta a posição do jogador para a inicial.
                 player.pos = (100, 300);
                 # Zera a velocidade vertical.
                 vy = 0

        # --- Atualizar Sombras ---
        # Cria uma lista temporária para armazenar as sombras que devem permanecer.
        new_shadows = []
        # Itera sobre cada dicionário de sombra na lista 'shadows'.
        for s in shadows:
            # Reduz o valor alfa (opacidade) da sombra, garantindo que não fique negativo.
            s["alpha"] = max(0, s["alpha"] - 20)
            # Verifica se a sombra ainda é recente (menos de 0.4s) E ainda está visível (alfa > 10).
            if time.time() - s["time"] < 0.4 and s["alpha"] > 10:
                # Garante que a chave 'flip_x' exista no dicionário (para compatibilidade).
                if "flip_x" not in s: s["flip_x"] = False
                # Adiciona a sombra (atualizada) à nova lista.
                new_shadows.append(s)
        # Substitui a lista antiga de sombras pela nova (removendo efetivamente as sombras antigas/invisíveis).
        shadows = new_shadows

        # --- Atualizar Frame ---
        # Incrementa o contador de frames.
        frame += 1

    # (Fim do bloco 'if game_state == "playing"')

# Define o início da função 'draw', chamada automaticamente para desenhar cada frame.
def draw():
    # Limpa a tela, removendo todos os desenhos do frame anterior.
    screen.clear()
    # Preenche toda a tela com uma cor de fundo (azul céu claro).
    screen.fill((135, 206, 235))

    # Verifica se o estado do jogo é "start" (tela de início).
    if game_state == "start":
        # Desenha o texto do título do jogo, centralizado na parte superior.
        screen.draw.text("The Mine Scrolls : teste",
                         center=(WIDTH // 2, HEIGHT // 3), fontsize=60, color="white", owidth=1.5, ocolor="black")
        # Calcula um valor pulsante entre 0 e 1, variando com o tempo.
        pulsate = abs(int(time.time() * 2) % 2 - 0.5) * 2
        # Calcula um valor alfa (transparência/brilho) baseado no valor pulsante.
        alpha = int(100 + 155 * pulsate)
        # Cria uma tupla de cor (RGBA) com o alfa variável para efeito de brilho.
        start_color = (255, 255, int(150 * pulsate), alpha)
        # Desenha o texto "Pressione ENTER para Iniciar" com a cor pulsante.
        screen.draw.text("Pressione ENTER para Iniciar",
                         center=(WIDTH // 2, HEIGHT * 2 // 3), fontsize=40, color=start_color, owidth=1, ocolor="black")

    # Se o estado do jogo for "playing" (inclui o jogo rodando e a tela de game over).
    elif game_state == "playing":
        # Itera sobre todas as plataformas definidas.
        for platform in platforms:
            # Tenta desenhar a plataforma usando uma textura de imagem.
            try:
                # Define a largura da imagem de textura (tile).
                tile_width = 32;
                # Obtém as coordenadas horizontais da plataforma (convertidas para inteiro).
                start_x = int(platform.left); end_x = int(platform.right)
                # Itera sobre a largura da plataforma em passos do tamanho da textura.
                for i in range(start_x, end_x, tile_width):
                    # Calcula a largura a ser desenhada neste passo (importante para a última parte que pode ser menor que tile_width).
                    draw_width = min(tile_width, end_x - i)
                    # Define a área da imagem de textura a ser usada (para recortar se draw_width < tile_width).
                    texture_area = Rect(0, 0, draw_width, platform.height)
                    # Desenha (blit) a imagem 'grass' na posição correta, usando a área definida.
                    screen.blit('grass', (i, platform.top), area=texture_area)
            # Se ocorrer qualquer erro ao tentar usar a textura (ex: arquivo 'grass.png' não encontrado).
            except Exception:
                # Desenha um retângulo verde sólido como alternativa (fallback).
                screen.draw.filled_rect(platform, (34, 139, 34))

        # Itera sobre a lista de dicionários de sombras.
        for s in shadows:
            # Obtém o valor de 'flip_x' do dicionário da sombra (ou False se a chave não existir).
            shadow_flip_x = s.get("flip_x", False)
            # Cria um objeto Actor temporário para representar a sombra (facilita aplicar opacidade e flip).
            shadow_actor = Actor(player.image, pos=(s["x"], s["y"]), anchor=('center', 'center'))
            # Define a opacidade (transparência) da sombra (alfa 0-255 convertido para 0.0-1.0).
            shadow_actor.opacity = s["alpha"] / 255.0;
            # Define a orientação horizontal da sombra.
            shadow_actor.flip_x = shadow_flip_x
            # Desenha a sombra na tela.
            shadow_actor.draw()

        # Se o martelo ainda não foi coletado.
        if not hammer_collected:
            # Desenha o ícone do martelo na sua posição atual.
            icon_hammer.draw()
        # Se o inimigo está vivo.
        if enemy.alive:
            # Desenha o inimigo.
            enemy.draw()
        # Desenha o jogador.
        player.draw()
        # Se o martelo foi coletado.
        if hammer_collected:
            # Desenha o martelo (pode sobrepor o jogador se estiver sendo segurado, pois é desenhado depois).
            hammer.draw()
        # Desenha o texto que mostra o número de vidas restantes 
        screen.draw.text(f"Vidas: {player_lives}", (10, 10), fontsize=40, color="white", owidth=1, ocolor="black")

        # Se o estado de game over estiver ativo (ainda dentro de game_state == "playing").
        if game_over:
            # Define o retângulo que cobre toda a tela.
            overlay_rect = Rect(0, 0, WIDTH, HEIGHT)
            # Define a cor preta com transparência (150 de 255).
            overlay_color = (0, 0, 0, 150)
            # Desenha o retângulo preenchido semi-transparente sobre toda a tela.
            screen.draw.filled_rect(overlay_rect, overlay_color)

            # Desenha o texto "GAME OVER" centralizado e em vermelho.
            screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 2 - 50), fontsize=80, color="red", owidth=1.5, ocolor="white")
            # Desenha o retângulo de fundo do botão "Reiniciar".
            screen.draw.filled_rect(reset_button, (200, 0, 0))
            # Desenha o texto "Reiniciar" sobre o botão.
            screen.draw.text("Reiniciar", center=reset_button.center, fontsize=40, color="white")

# Define a função 'on_key_down', chamada pelo Pygame Zero sempre que uma tecla é pressionada.
def on_key_down(key):
    # Declara que a função vai modificar a variável global 'game_state'.
    global game_state
    # Verifica se o jogo está na tela de início ('start') E se a tecla pressionada foi ENTER (RETURN) ou ESPAÇO.
    if game_state == "start" and (key == keys.RETURN or key == keys.SPACE):
        # Muda o estado do jogo para "playing".
        game_state = "playing"
        # Chama a função para iniciar a música do jogo.
        start_music()

# Define a função 'on_mouse_down', chamada pelo Pygame Zero quando um botão do mouse é pressionado.
def on_mouse_down(pos, button):
    # Declara que a função vai ler/usar as variáveis globais 'game_state' e 'game_over'.
    global game_state, game_over
    # Tenta obter a constante que representa o botão esquerdo do mouse (pode variar).
    try: click_button = mouse.LEFT
    # Se a constante 'mouse.LEFT' não for encontrada, usa o valor numérico 1 como fallback.
    except NameError: click_button = 1
    # Verifica se o estado é "playing", se é "game over", se a posição do clique (pos) está dentro do retângulo do botão de reset E se o botão pressionado foi o esquerdo.
    if game_state == "playing" and game_over and reset_button.collidepoint(pos) and button == click_button:
        # Chama a função para reiniciar todas as variáveis e o estado do jogo.
        reset_game()


# Inicia o loop principal do jogo Pygame Zero, que começa a chamar update() e draw() repetidamente.
pgzrun.go()