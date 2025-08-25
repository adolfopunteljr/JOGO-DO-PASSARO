import math
import os
import random
import sys
import pygame

# Inicialização do Pygame
pygame.init()
pygame.mixer.init()

# Configurações da tela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("JOGO DO PASSARO")

# Cores
SKY_BLUE = (113, 197, 207)
WHITE = (255, 255, 255)
GREEN = (34, 153, 84)
DARK_GREEN = (23, 107, 58)
BROWN = (165, 42, 42)
YELLOW = (255, 204, 0)
ORANGE = (255, 128, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
LIGHT_BLUE = (173, 216, 230)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
GOLD = (255, 215, 0)
BLUE = (70, 130, 200)

# Relógio para controlar FPS
clock = pygame.time.Clock()
FPS = 60

# Variáveis do jogo
gravity = 0.5
scroll_speed = 3
ground_scroll = 0
high_score = 0
particles = []

# Novas Variáveis
sound_volume = 0.8
music_volume = 0.5
music_enabled = True
sound_enabled = True

# Sistema de níveis
LEVELS = [
    {
        "score": 0,
        "name": "INICIANTE",
        "theme": "day",
        "difficulty": 1.0,
        "pipe_color": GREEN,
    },
    {
        "score": 10,
        "name": "FACÍL",
        "theme": "evening",
        "difficulty": 1.6,
        "pipe_color": (200, 100, 50),
    },
    {
        "score": 20,
        "name": "MÉDIO",
        "theme": "sunset",
        "difficulty": 2.4,
        "pipe_color": (255, 100, 50),
    },
    {
        "score": 30,
        "name": "DIFICÍL",
        "theme": "night",
        "difficulty": 4.6,
        "pipe_color": (70, 70, 150),
    },
    {
        "score": 40,
        "name": "IMPOSSÍVEL",
        "theme": "dawn",
        "difficulty": 6.8,
        "pipe_color": (120, 70, 150),
    },
]

current_level = 0
selected_character = "bird"

# Estado do jogo
MENU = 0
GAME = 1
GAME_OVER = 2
SCORE_BOARD = 3
CHARACTER_SELECT = 4
SETTINGS = 5
CONTROLS = 6

game_state = MENU

# Parallax
parallax_positions = [0, 0, 0]
parallax_speeds = [0.5, 1.0, 1.5]


# Função para criar assets padrão
def create_default_assets():
    """Cria assets padrão se não existirem"""
    # Criar diretórios se não existirem
    directories = [
        "assets",
        "assets/characters",
        "assets/parallax",
        "assets/sounds",
        "assets/ui",
    ]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

    # Mensagem informativa
    print("Dica: Adicione arquivos de som na pasta assets/sounds/")
    print("Nomes sugeridos: flap.wav, score.wav, hit.wav, music.mp3")


# Carregar assets externos
def load_assets():
    assets = {}

    # Criar assets padrão se necessário
    create_default_assets()

    # Carregar personagens
    assets["characters"] = {}
    character_files = ["bird.png", "dragon.png", "plane.png", "fairy.png", "fish.png"]

    for char_file in character_files:
        char_name = char_file.split(".")[0]
        if os.path.exists(f"assets/characters/{char_file}"):
            try:
                assets["characters"][char_name] = pygame.image.load(
                    f"assets/characters/{char_file}"
                ).convert_alpha()
                # Redimensionar se necessário
                if assets["characters"][char_name].get_size() != (40, 40):
                    assets["characters"][char_name] = pygame.transform.scale(
                        assets["characters"][char_name], (40, 40)
                    )
            except:
                print(f"Erro ao carregar {char_file}, usando fallback")
                assets["characters"][char_name] = create_fallback_character(char_name)
        else:
            assets["characters"][char_name] = create_fallback_character(char_name)

    # Carregar parallax
    assets["parallax"] = {}
    themes = ["day", "evening", "sunset", "night", "dawn"]

    for theme in themes:
        assets["parallax"][theme] = []
        for layer in range(3):
            if os.path.exists(f"assets/parallax/{theme}_{layer}.png"):
                try:
                    img = pygame.image.load(
                        f"assets/parallax/{theme}_{layer}.png"
                    ).convert_alpha()
                    # Ajustar altura se necessário
                    if img.get_height() != HEIGHT:
                        scale_factor = HEIGHT / img.get_height()
                        new_width = int(img.get_width() * scale_factor)
                        img = pygame.transform.scale(img, (new_width, HEIGHT))
                    assets["parallax"][theme].append(img)
                except:
                    print(f"Erro ao carregar parallax {theme}_{layer}.png")
                    assets["parallax"][theme].append(
                        create_parallax_fallback(layer, theme)
                    )
            else:
                assets["parallax"][theme].append(create_parallax_fallback(layer, theme))

    # Carregar sons
    try:
        # Nomes mais comuns para sons
        sound_files = {
            "flap_sound": ["flap.wav", "jump.wav", "wing.wav"],
            "score_sound": ["score.wav", "point.wav", "success.wav"],
            "hit_sound": ["hit.wav", "crash.wav", "die.wav", "fail.wav"],
        }

        for sound_name, possible_files in sound_files.items():
            loaded = False
            for file_name in possible_files:
                if os.path.exists(f"assets/sounds/{file_name}"):
                    try:
                        assets[sound_name] = pygame.mixer.Sound(
                            f"assets/sounds/{file_name}"
                        )
                        assets[sound_name].set_volume(
                            sound_volume if sound_enabled else 0
                        )
                        loaded = True
                        print(f"Som carregado: {file_name} como {sound_name}")
                        break
                    except:
                        continue

            if not loaded:
                print(f"Nenhum arquivo de som encontrado para {sound_name}")
                assets[sound_name] = None

    except pygame.error as e:
        print(f"Erro ao carregar sons: {e}")
        assets["flap_sound"] = None
        assets["score_sound"] = None
        assets["hit_sound"] = None

    # CARREGAR MÚSICA
    try:
        # Nomes comuns para música
        music_files = ["music.mp3", "background.mp3", "theme.mp3", "song.mp3"]
        music_loaded = False

        for file_name in music_files:
            if os.path.exists(f"assets/sounds/{file_name}"):
                try:
                    pygame.mixer.music.load(f"assets/sounds/{file_name}")
                    pygame.mixer.music.play(-1)
                    pygame.mixer.music.set_volume(music_volume if music_enabled else 0)
                    music_loaded = True
                    print(f"Música carregada: {file_name}")
                    break
                except Exception as e:
                    print(f"Erro ao carregar música {file_name}: {e}")
                    continue

        if not music_loaded:
            print("Nenhum arquivo de música encontrado")

    except Exception as e:
        print(f"Erro ao carregar música: {e}")

    # Carregar UI
    if os.path.exists("assets/ui/button.png"):
        assets["button_img"] = pygame.image.load("assets/ui/button.png").convert_alpha()
    else:
        assets["button_img"] = None

    if os.path.exists("assets/ui/logo.png"):
        assets["logo_img"] = pygame.image.load("assets/ui/logo.png").convert_alpha()
    else:
        assets["logo_img"] = None

    return assets


def create_fallback_character(char_name):
    """Cria personagem fallback"""
    surface = pygame.Surface((40, 40), pygame.SRCALPHA)

    if char_name == "dragon":
        pygame.draw.circle(surface, (255, 100, 100), (20, 20), 15)
        pygame.draw.polygon(surface, (255, 150, 150), [(30, 20), (38, 15), (38, 25)])
    elif char_name == "plane":
        pygame.draw.rect(surface, (200, 200, 200), (5, 15, 25, 10))
        pygame.draw.polygon(surface, (150, 150, 150), [(30, 20), (38, 17), (38, 23)])
    elif char_name == "fairy":
        pygame.draw.circle(surface, (255, 230, 230), (20, 20), 12)
        pygame.draw.ellipse(surface, (200, 230, 255, 150), (5, 10, 30, 15))
    elif char_name == "fish":
        pygame.draw.ellipse(surface, (100, 150, 255), (5, 15, 25, 10))
        pygame.draw.polygon(surface, (80, 130, 230), [(30, 20), (38, 17), (38, 23)])
    else:  # bird
        pygame.draw.circle(surface, YELLOW, (20, 20), 15)
        pygame.draw.circle(surface, WHITE, (28, 15), 8)
        pygame.draw.circle(surface, BLACK, (30, 15), 4)
        pygame.draw.polygon(surface, ORANGE, [(30, 20), (38, 17), (38, 23)])

    return surface


def create_parallax_fallback(layer, theme):
    """Cria fallback para parallax"""
    surface = pygame.Surface((WIDTH * 2, HEIGHT), pygame.SRCALPHA)

    if theme == "day":
        if layer == 0:
            surface.fill((135, 206, 235))  # Céu
            for i in range(5):
                x = i * 200
                height = random.randint(100, 180)
                pygame.draw.polygon(
                    surface,
                    (100, 120, 150),
                    [(x, HEIGHT), (x + 100, HEIGHT - height), (x + 200, HEIGHT)],
                )
        elif layer == 1:
            for i in range(8):
                x = i * 150
                tree_height = random.randint(120, 180)
                pygame.draw.rect(
                    surface,
                    (90, 60, 30),
                    (x + 60, HEIGHT - tree_height, 30, tree_height),
                )
                pygame.draw.circle(
                    surface, (60, 130, 50), (x + 75, HEIGHT - tree_height - 40), 50
                )
        elif layer == 2:
            for i in range(15):
                x = i * 80
                height = random.randint(30, 60)
                pygame.draw.line(
                    surface,
                    (30, 120, 40),
                    (x + 20, HEIGHT),
                    (x + 20, HEIGHT - height),
                    3,
                )

    elif theme == "night":
        if layer == 0:
            surface.fill((25, 25, 50))
            for i in range(100):
                x = random.randint(0, WIDTH * 2)
                y = random.randint(0, HEIGHT - 200)
                size = random.randint(1, 3)
                pygame.draw.circle(surface, (255, 255, 255), (x, y), size)
            pygame.draw.circle(surface, (220, 220, 220), (600, 80), 30)
        elif layer == 1:
            for i in range(10):
                x = i * 120
                building_height = random.randint(150, 250)
                pygame.draw.rect(
                    surface,
                    (50, 50, 80),
                    (x + 30, HEIGHT - building_height, 60, building_height),
                )
                for j in range(5):
                    for k in range(3):
                        if random.random() > 0.5:
                            pygame.draw.rect(
                                surface,
                                (255, 255, 100),
                                (
                                    x + 40 + k * 15,
                                    HEIGHT - building_height + 30 + j * 30,
                                    10,
                                    15,
                                ),
                            )
        elif layer == 2:
            for i in range(20):
                x = i * 60
                height = random.randint(20, 40)
                pygame.draw.line(
                    surface,
                    (60, 70, 120),
                    (x + 15, HEIGHT),
                    (x + 15, HEIGHT - height),
                    2,
                )

    else:  # Para outros temas
        if layer == 0:
            surface.fill((100, 150, 200))
        elif layer == 1:
            surface.fill((120, 180, 100))
        elif layer == 2:
            surface.fill((150, 200, 100))

    return surface


# Carregar assets
assets = load_assets()


# Classe para partículas
class Particle:
    def __init__(self, x, y, color, velocity, size, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.size = size
        self.lifetime = lifetime
        self.age = 0

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.age += 1
        self.size = max(0, self.size - 0.1)
        return self.age < self.lifetime

    def draw(self, surface):
        alpha = 255 * (1 - self.age / self.lifetime)
        pygame.draw.circle(
            surface,
            (*self.color, int(alpha)),
            (int(self.x), int(self.y)),
            int(self.size),
        )


# Classe para o pássaro
class Bird:
    def __init__(self, x, y, character_type="bird"):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x - 20, y - 20, 40, 40)
        self.movement = 0
        self.character_type = character_type
        self.alive = True
        self.score = 0
        self.angle = 0

    def flap(self):
        self.movement = -8
        self.angle = -30

        # Partículas ao bater asas
        for _ in range(5):
            velocity = [random.uniform(-1, 1), random.uniform(-2, 0)]
            particles.append(
                Particle(self.x, self.y, WHITE, velocity, random.randint(2, 4), 30)
            )

        if assets["flap_sound"] and sound_enabled:
            assets["flap_sound"].play()

    def update(self):
        self.movement += gravity
        self.y += self.movement
        self.rect.y = self.y

        # Atualizar ângulo
        if self.movement < 0:
            self.angle = max(-30, self.angle - 2)
        else:
            self.angle = min(45, self.angle + 2)

    def draw(self):
        # Rotacionar sprite
        sprite = assets["characters"][self.character_type]
        rotated_sprite = pygame.transform.rotate(sprite, -self.angle)

        # Desenhar sprite
        screen.blit(
            rotated_sprite,
            (
                self.x - rotated_sprite.get_width() // 2,
                self.y - rotated_sprite.get_height() // 2,
            ),
        )


# Classe para os tubos
class Pipe:
    def __init__(self, x, level_index=0):
        self.gap = 200
        self.height = random.randint(150, 400)
        self.level_index = level_index

        self.top_pipe = pygame.Rect(x, 0, 70, self.height - self.gap // 2)
        self.bottom_pipe = pygame.Rect(
            x, self.height + self.gap // 2, 70, HEIGHT - (self.height + self.gap // 2)
        )

        self.passed = False

    def update(self):
        self.top_pipe.x -= scroll_speed
        self.bottom_pipe.x -= scroll_speed

    def draw(self):
        level = LEVELS[self.level_index]
        pipe_color = level.get("pipe_color", GREEN)

        # Desenhar tubos
        pygame.draw.rect(screen, pipe_color, self.top_pipe)
        pygame.draw.rect(
            screen,
            DARK_GREEN,
            (self.top_pipe.x, self.top_pipe.height - 40, self.top_pipe.width, 50),
        )

        pygame.draw.rect(screen, pipe_color, self.bottom_pipe)
        pygame.draw.rect(
            screen,
            DARK_GREEN,
            (self.bottom_pipe.x, self.bottom_pipe.y, self.bottom_pipe.width, 50),
        )

    def check_collision(self, bird_rect):
        return bird_rect.colliderect(self.top_pipe) or bird_rect.colliderect(
            self.bottom_pipe
        )

    def check_score(self, bird_x):
        if not self.passed and bird_x > self.top_pipe.x + self.top_pipe.width:
            self.passed = True

            # Partículas de pontuação
            center_y = self.height
            for _ in range(10):
                velocity = [random.uniform(-1, 1), random.uniform(-2, 2)]
                particles.append(
                    Particle(
                        self.top_pipe.x + 35,
                        center_y,
                        GOLD,
                        velocity,
                        random.randint(3, 6),
                        40,
                    )
                )

            if assets["score_sound"] and sound_enabled:
                assets["score_sound"].play()

            return True
        return False


# Classe para o botão do menu
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color

        # Usar imagem de botão se disponível
        if assets["button_img"]:
            img = pygame.transform.scale(
                assets["button_img"], (self.rect.width, self.rect.height)
            )
            surface.blit(img, self.rect)
        else:
            pygame.draw.rect(surface, color, self.rect, border_radius=10)
            pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)

        # Ajustar tamanho da fonte se necessário
        font_size = 24
        font = pygame.font.SysFont("Arial", font_size, bold=True)
        text_surface = font.render(self.text, True, BLACK)

        while text_surface.get_width() > self.rect.width - 20 and font_size > 16:
            font_size -= 1
            font = pygame.font.SysFont("Arial", font_size, bold=True)
            text_surface = font.render(self.text, True, BLACK)

        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def check_click(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False


# Função para desenhar parallax
def draw_parallax(level_index):
    global parallax_positions

    theme = LEVELS[level_index]["theme"]

    # Atualizar posições
    for i in range(3):
        parallax_positions[i] = (parallax_positions[i] - parallax_speeds[i]) % WIDTH

        # Desenhar duas cópias para efeito contínuo
        screen.blit(assets["parallax"][theme][i], (parallax_positions[i] - WIDTH, 0))
        screen.blit(assets["parallax"][theme][i], (parallax_positions[i], 0))


# Função para desenhar o placar
def draw_score(score, x, y, color=WHITE):
    font = pygame.font.SysFont("Arial", 30, bold=True)
    score_surface = font.render(f"Score: {score}", True, color)
    score_rect = score_surface.get_rect(center=(x, y))

    shadow_surface = font.render(f"Score: {score}", True, BLACK)
    shadow_rect = shadow_surface.get_rect(center=(x + 2, y + 2))

    screen.blit(shadow_surface, shadow_rect)
    screen.blit(score_surface, score_rect)


# Função para desenhar o chão
def draw_ground():
    ground_rect = pygame.Rect(0, HEIGHT - 100, WIDTH, 100)
    pygame.draw.rect(screen, GREEN, ground_rect)

    for i in range(-20, WIDTH + 20, 20):
        pygame.draw.line(
            screen,
            DARK_GREEN,
            (i + ground_scroll, HEIGHT - 100),
            (i + ground_scroll, HEIGHT - 110),
            3,
        )


# Função para desenhar nuvens
def draw_clouds():
    time = pygame.time.get_ticks() / 1000
    for i in range(5):
        x = (time * 20 + i * 200) % (WIDTH + 100) - 50
        y = 100 + i * 40
        pygame.draw.circle(screen, WHITE, (x, y), 20)
        pygame.draw.circle(screen, WHITE, (x + 15, y - 10), 15)
        pygame.draw.circle(screen, WHITE, (x + 15, y + 10), 15)
        pygame.draw.circle(screen, WHITE, (x - 15, y), 15)


# Função para desenhar o sol
def draw_sun():
    x = 700
    y = 80
    pygame.draw.circle(screen, (255, 255, 200), (x, y), 30)
    pygame.draw.circle(screen, (255, 223, 0), (x, y), 25)

    for i in range(12):
        angle = math.radians(i * 30)
        start_x = x + 30 * math.cos(angle)
        start_y = y + 30 * math.sin(angle)
        end_x = x + 45 * math.cos(angle)
        end_y = y + 45 * math.sin(angle)
        pygame.draw.line(screen, (255, 223, 0), (start_x, start_y), (end_x, end_y), 3)


# Função para verificar e mudar de nível
def check_level_up(score):
    global current_level, scroll_speed

    for i, level in enumerate(LEVELS):
        if score >= level["score"]:
            current_level = i
            scroll_speed = 3 * LEVELS[current_level]["difficulty"]

    return current_level


# Função para o menu principal
def main_menu():
    global game_state, ground_scroll

    # Botões principais (apenas modo 1 jogador)
    button_width, button_height = 300, 45
    button_x = WIDTH // 2 - button_width // 2
    button_spacing = 60

    buttons = [
        Button(
            button_x,
            200,
            button_width,
            button_height,
            "JOGAR",
            LIGHT_BLUE,
            (200, 230, 255),
        ),
        Button(
            button_x,
            200 + button_spacing,
            button_width,
            button_height,
            "PERSONAGENS",
            (200, 180, 255),
            (220, 200, 255),
        ),
        Button(
            button_x,
            200 + button_spacing * 2,
            button_width,
            button_height,
            "CONFIGURAÇÕES",
            LIGHT_GRAY,
            WHITE,
        ),
        Button(
            button_x,
            200 + button_spacing * 3,
            button_width,
            button_height,
            "PLACARES",
            (180, 255, 180),
            (200, 255, 200),
        ),
        Button(
            button_x,
            200 + button_spacing * 4,
            button_width,
            button_height,
            "SAIR",
            (255, 150, 150),
            (255, 180, 180),
        ),
    ]

    # Animação do pássaro no menu
    bird_y = HEIGHT // 2 + math.sin(pygame.time.get_ticks() / 500) * 20

    running = True
    while running and game_state == MENU:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # TECLA ESC PARA VOLTAR
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                # Atalhos de teclado para menu
                if event.key == pygame.K_j or event.key == pygame.K_RETURN:
                    game_state = GAME
                    running = False
                if event.key == pygame.K_p:
                    game_state = CHARACTER_SELECT
                    running = False
                if event.key == pygame.K_c:
                    game_state = SETTINGS
                    running = False
                if event.key == pygame.K_l:
                    game_state = SCORE_BOARD
                    running = False

            # Verificar cliques nos botões
            for i, button in enumerate(buttons):
                if button.check_click(mouse_pos, event):
                    if i == 0:  # JOGAR
                        game_state = GAME
                        running = False
                    elif i == 1:  # PERSONAGENS
                        game_state = CHARACTER_SELECT
                        running = False
                    elif i == 2:  # CONFIGURAÇÕES
                        game_state = SETTINGS
                        running = False
                    elif i == 3:  # PLACARES
                        game_state = SCORE_BOARD
                        running = False
                    elif i == 4:  # SAIR
                        pygame.quit()
                        sys.exit()

        # Atualizar scroll do chão
        ground_scroll = (ground_scroll - 2) % 20

        # Desenhar fundo
        draw_parallax(0)

        # Desenhar elementos decorativos
        draw_clouds()
        draw_sun()

        # Desenhar título
        if assets["logo_img"]:
            logo = pygame.transform.scale(assets["logo_img"], (400, 150))
            screen.blit(logo, (WIDTH // 2 - 200, 50))
        else:
            font = pygame.font.SysFont("Arial", 60, bold=True)
            title = font.render("JOGO DO PASSARO", True, BLACK)
            title_shadow = font.render("JOGO DO PASSARO", True, GOLD)
            screen.blit(title_shadow, (WIDTH // 2 - title.get_width() // 2 + 3, 63))
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

        # Desenhar instruções de atalho
        font_small = pygame.font.SysFont("Arial", 14)
        shortcuts = [
            "Dica: Use teclas de atalho para navegar mais rápido!",
            "J - Jogar | P - Personagens | C - Configurações | L - Placar",
        ]

        for i, text in enumerate(shortcuts):
            text_surface = font_small.render(text, True, BLACK)
            screen.blit(
                text_surface, (WIDTH // 2 - text_surface.get_width() // 2, 150 + i * 20)
            )

        # Desenhar personagem selecionado
        char_img = assets["characters"][selected_character]
        screen.blit(char_img, (WIDTH // 2 - 20, bird_y - 20))

        # Desenhar botões
        for button in buttons:
            button.check_hover(mouse_pos)
            button.draw(screen)

        # Desenhar chão
        draw_ground()

        pygame.display.update()
        clock.tick(FPS)


# Função para seleção de personagem
def character_select():
    global game_state, selected_character

    # Botões de personagem
    character_buttons = []
    char_options = list(assets["characters"].keys())
    char_spacing = 100
    start_x = WIDTH // 2 - (len(char_options) * char_spacing) // 2

    for i, char_name in enumerate(char_options):
        character_buttons.append(
            {
                "rect": pygame.Rect(start_x + i * char_spacing, 300, 80, 80),
                "name": char_name,
                "selected": char_name == selected_character,
            }
        )

    # Botão voltar
    back_button = Button(WIDTH // 2 - 100, 500, 200, 50, "VOLTAR", LIGHT_GRAY, WHITE)

    running = True
    while running and game_state == CHARACTER_SELECT:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            #  TECLA ESC PARA VOLTAR
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = MENU
                    running = False

            if back_button.check_click(mouse_pos, event):
                game_state = MENU
                running = False

            # Verificar clique em personagens
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for char_btn in character_buttons:
                    if char_btn["rect"].collidepoint(mouse_pos):
                        selected_character = char_btn["name"]
                        # Atualizar estado de seleção
                        for btn in character_buttons:
                            btn["selected"] = btn["name"] == selected_character

        # Desenhar fundo
        draw_parallax(0)

        # Desenhar título
        font = pygame.font.SysFont("Arial", 40, bold=True)
        title = font.render("ESCOLHA SEU PERSONAGEM", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        # Desenhar personagens
        for char_btn in character_buttons:
            # Desenhar borda se selecionado
            if char_btn["selected"]:
                pygame.draw.rect(screen, GOLD, char_btn["rect"], 4, border_radius=15)
            else:
                pygame.draw.rect(screen, BLACK, char_btn["rect"], 2, border_radius=15)

            # Desenhar personagem
            char_img = assets["characters"][char_btn["name"]]
            screen.blit(char_img, (char_btn["rect"].x + 20, char_btn["rect"].y + 20))

            # Nome do personagem
            name_font = pygame.font.SysFont("Arial", 16, bold=True)
            name_text = name_font.render(char_btn["name"].upper(), True, BLACK)
            screen.blit(
                name_text,
                (
                    char_btn["rect"].centerx - name_text.get_width() // 2,
                    char_btn["rect"].y + 85,
                ),
            )

        # Desenhar botão voltar
        back_button.check_hover(mouse_pos)
        back_button.draw(screen)

        # Desenhar chão
        draw_ground()

        pygame.display.update()
        clock.tick(FPS)


# Função para a tela de game over
def game_over_screen(score):
    global game_state, high_score

    # Atualizar recorde
    if score > high_score:
        high_score = score

    # Botões
    retry_button = Button(
        WIDTH // 2 - 150, 400, 140, 50, "Tentar Novamente", LIGHT_GRAY, WHITE
    )
    menu_button = Button(WIDTH // 2 + 10, 400, 140, 50, "Menu", LIGHT_GRAY, WHITE)

    running = True
    while running and game_state == GAME_OVER:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            #  TECLA ESC PARA VOLTAR
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = MENU
                    running = False

            if retry_button.check_click(mouse_pos, event):
                game_state = GAME
                running = False

            if menu_button.check_click(mouse_pos, event):
                game_state = MENU
                running = False

        # Desenhar fundo
        draw_parallax(current_level)

        # Desenhar texto de game over
        font = pygame.font.SysFont("Arial", 60, bold=True)
        game_over_text = font.render("GAME OVER", True, RED)
        game_over_shadow = font.render("GAME OVER", True, BLACK)
        screen.blit(
            game_over_shadow, (WIDTH // 2 - game_over_text.get_width() // 2 + 3, 103)
        )
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, 100))

        # Desenhar pontuação
        score_font = pygame.font.SysFont("Arial", 36, bold=True)
        score_text = score_font.render(f"Pontuação: {score}", True, WHITE)
        score_shadow = score_font.render(f"Pontuação: {score}", True, BLACK)
        screen.blit(score_shadow, (WIDTH // 2 - score_text.get_width() // 2 + 2, 182))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 180))

        # Desenhar recorde se for maior
        if score == high_score:
            record_text = score_font.render("NOVO RECORDE!", True, GOLD)
            record_shadow = score_font.render("NOVO RECORDE!", True, BLACK)
            screen.blit(
                record_shadow, (WIDTH // 2 - record_text.get_width() // 2 + 2, 232)
            )
            screen.blit(record_text, (WIDTH // 2 - record_text.get_width() // 2, 230))

        # Desenhar botões
        retry_button.check_hover(mouse_pos)
        menu_button.check_hover(mouse_pos)
        retry_button.draw(screen)
        menu_button.draw(screen)

        # Desenhar chão
        draw_ground()

        pygame.display.update()
        clock.tick(FPS)


# Função para a tela de placares
def score_board():
    global game_state

    # Botão de voltar
    back_button = Button(WIDTH // 2 - 100, 500, 200, 50, "VOLTAR", LIGHT_GRAY, WHITE)

    running = True
    while running and game_state == SCORE_BOARD:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            #  TECLA ESC PARA VOLTAR
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = MENU
                    running = False

            if back_button.check_click(mouse_pos, event):
                game_state = MENU
                running = False

        # Desenhar fundo
        draw_parallax(0)

        # Desenhar título
        font = pygame.font.SysFont("Arial", 60, bold=True)
        title = font.render("PLACARES", True, BLACK)
        title_shadow = font.render("PLACARES", True, GOLD)
        screen.blit(title_shadow, (WIDTH // 2 - title.get_width() // 2 + 3, 63))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

        # Desenhar recordes
        score_font = pygame.font.SysFont("Arial", 36, bold=True)

        # Apenas 1 jogador
        score_text = score_font.render(f"Recorde: {high_score}", True, WHITE)
        score_shadow = score_font.render(f"Recorde: {high_score}", True, BLACK)
        screen.blit(score_shadow, (WIDTH // 2 - score_text.get_width() // 2 + 2, 152))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 150))

        # Desenhar botão voltar
        back_button.check_hover(mouse_pos)
        back_button.draw(screen)

        # Desenhar chão
        draw_ground()

        pygame.display.update()
        clock.tick(FPS)


#  FUNÇÃO DE CONFIGURAÇÕES
def settings_menu():
    global game_state, sound_volume, music_volume, sound_enabled, music_enabled

    # Sliders para volume
    sound_slider = pygame.Rect(WIDTH // 2 - 100, 200, 200, 20)
    music_slider = pygame.Rect(WIDTH // 2 - 100, 280, 200, 20)

    # Botões
    back_button = Button(WIDTH // 2 - 100, 400, 200, 50, "VOLTAR", LIGHT_GRAY, WHITE)
    controls_button = Button(
        WIDTH // 2 - 100, 470, 200, 50, "CONTROLES", LIGHT_GRAY, WHITE
    )
    toggle_sound = Button(
        WIDTH // 2 + 120, 195, 30, 30, "✓" if sound_enabled else "✗", LIGHT_GRAY, WHITE
    )
    toggle_music = Button(
        WIDTH // 2 + 120, 275, 30, 30, "✓" if music_enabled else "✗", LIGHT_GRAY, WHITE
    )

    # Botões de teste de som
    test_sound_button = Button(
        WIDTH // 2 - 100, 340, 200, 40, "TESTAR SOM", (150, 200, 150), (180, 230, 180)
    )

    dragging_sound = False
    dragging_music = False

    running = True
    while running and game_state == SETTINGS:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            #  TECLA ESC PARA VOLTAR
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = MENU
                    running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if sound_slider.collidepoint(mouse_pos):
                    dragging_sound = True
                if music_slider.collidepoint(mouse_pos):
                    dragging_music = True
                if toggle_sound.check_click(mouse_pos, event):
                    sound_enabled = not sound_enabled
                    toggle_sound.text = "✓" if sound_enabled else "✗"
                    # Atualizar sons
                    volume = sound_volume if sound_enabled else 0
                    if assets["flap_sound"]:
                        assets["flap_sound"].set_volume(volume)
                    if assets["score_sound"]:
                        assets["score_sound"].set_volume(volume)
                    if assets["hit_sound"]:
                        assets["hit_sound"].set_volume(volume)
                if toggle_music.check_click(mouse_pos, event):
                    music_enabled = not music_enabled
                    toggle_music.text = "✓" if music_enabled else "✗"
                    pygame.mixer.music.set_volume(music_volume if music_enabled else 0)

                # Testar som
                if (
                    test_sound_button.check_click(mouse_pos, event)
                    and assets["flap_sound"]
                    and sound_enabled
                ):
                    assets["flap_sound"].play()

            if event.type == pygame.MOUSEBUTTONUP:
                dragging_sound = False
                dragging_music = False

            if event.type == pygame.MOUSEMOTION:
                if dragging_sound:
                    sound_volume = max(
                        0, min(1, (mouse_pos[0] - sound_slider.x) / sound_slider.width)
                    )
                    # Atualizar volume dos sons
                    volume = sound_volume if sound_enabled else 0
                    if assets["flap_sound"]:
                        assets["flap_sound"].set_volume(volume)
                    if assets["score_sound"]:
                        assets["score_sound"].set_volume(volume)
                    if assets["hit_sound"]:
                        assets["hit_sound"].set_volume(volume)

                if dragging_music:
                    music_volume = max(
                        0, min(1, (mouse_pos[0] - music_slider.x) / music_slider.width)
                    )
                    # Atualizar volume da música
                    volume = music_volume if music_enabled else 0
                    pygame.mixer.music.set_volume(volume)

            if back_button.check_click(mouse_pos, event):
                game_state = MENU
                running = False

            if controls_button.check_click(mouse_pos, event):
                game_state = CONTROLS
                running = False

        # Desenhar fundo
        draw_parallax(0)

        # Título
        font = pygame.font.SysFont("Arial", 50, bold=True)
        title = font.render("CONFIGURAÇÕES", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        # Volume dos efeitos sonoros
        font = pygame.font.SysFont("Arial", 25)
        sound_text = font.render("Efeitos Sonoros:", True, WHITE)
        screen.blit(sound_text, (WIDTH // 2 - 150, 170))

        pygame.draw.rect(screen, GRAY, sound_slider)
        pygame.draw.rect(
            screen,
            GREEN,
            (
                sound_slider.x,
                sound_slider.y,
                sound_slider.width * sound_volume,
                sound_slider.height,
            ),
        )

        # Indicador de volume numérico
        vol_text = font.render(f"{int(sound_volume * 100)}%", True, WHITE)
        screen.blit(vol_text, (WIDTH // 2 + 160, 170))

        # Volume da música
        music_text = font.render("Música:", True, WHITE)
        screen.blit(music_text, (WIDTH // 2 - 150, 250))

        pygame.draw.rect(screen, GRAY, music_slider)
        pygame.draw.rect(
            screen,
            BLUE,
            (
                music_slider.x,
                music_slider.y,
                music_slider.width * music_volume,
                music_slider.height,
            ),
        )

        # Indicador de volume numérico
        vol_text = font.render(f"{int(music_volume * 100)}%", True, WHITE)
        screen.blit(vol_text, (WIDTH // 2 + 160, 250))

        # Status dos sons
        status_font = pygame.font.SysFont("Arial", 16)
        if assets["flap_sound"] is None:
            status_text = status_font.render(
                "Sons não encontrados! Coloque na pasta assets/sounds/", True, RED
            )
            screen.blit(status_text, (WIDTH // 2 - status_text.get_width() // 2, 310))
        elif not sound_enabled:
            status_text = status_font.render("Sons desativados", True, YELLOW)
            screen.blit(status_text, (WIDTH // 2 - status_text.get_width() // 2, 310))
        else:
            status_text = status_font.render("Sons ativados", True, GREEN)
            screen.blit(status_text, (WIDTH // 2 - status_text.get_width() // 2, 310))

        # Botões
        back_button.check_hover(mouse_pos)
        controls_button.check_hover(mouse_pos)
        toggle_sound.check_hover(mouse_pos)
        toggle_music.check_hover(mouse_pos)
        test_sound_button.check_hover(mouse_pos)

        back_button.draw(screen)
        controls_button.draw(screen)
        toggle_sound.draw(screen)
        toggle_music.draw(screen)
        test_sound_button.draw(screen)

        # Desenhar chão
        draw_ground()

        pygame.display.update()
        clock.tick(FPS)


#  FUNÇÃO DE CONTROLES
def controls_menu():
    global game_state

    # Botão voltar
    back_button = Button(WIDTH // 2 - 100, 500, 200, 50, "VOLTAR", LIGHT_GRAY, WHITE)

    running = True
    while running and game_state == CONTROLS:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            #  TECLA ESC PARA VOLTAR
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = SETTINGS
                    running = False

            if back_button.check_click(mouse_pos, event):
                game_state = SETTINGS
                running = False

        # Desenhar fundo
        draw_parallax(0)

        # Título
        font = pygame.font.SysFont("Arial", 50, bold=True)
        title = font.render("CONTROLES", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        # Controles
        font = pygame.font.SysFont("Arial", 24)
        controls = [
            "🎮 CONTROLES PRINCIPAIS:",
            "   ESPAÇO ou CLIQUE - Voar",
            "",
            "🎮 CONTROLES GERAIS:",
            "   ESC - Pausar/Voltar",
            "   M - Mute/Desmute música",
            "   S - Mute/Desmute sons",
            "   R - Reiniciar jogo",
            "",
            "🎮 ATALHOS DO MENU:",
            "   J - Iniciar Jogo",
            "   P - Seleção de Personagem",
            "   C - Configurações",
            "   L - Ver Placares",
        ]

        for i, line in enumerate(controls):
            text = font.render(line, True, WHITE)
            screen.blit(text, (WIDTH // 2 - 250, 150 + i * 30))

        # Informações sobre arquivos de som
        info_font = pygame.font.SysFont("Arial", 16)
        info_text = info_font.render(
            "Arquivos de som devem estar em: assets/sounds/ com nomes: flap.wav, score.wav, hit.wav, music.mp3",
            True,
            YELLOW,
        )
        screen.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, 550))

        # Botão voltar
        back_button.check_hover(mouse_pos)
        back_button.draw(screen)

        # Desenhar chão
        draw_ground()

        pygame.display.update()
        clock.tick(FPS)


# Função para lidar com atalhos globais
def handle_global_shortcuts(event):
    global sound_enabled, music_enabled

    if event.type == pygame.KEYDOWN:
        # Mute/Unmute música
        if event.key == pygame.K_m:
            music_enabled = not music_enabled
            pygame.mixer.music.set_volume(music_volume if music_enabled else 0)
            print(f"Música {'ativada' if music_enabled else 'desativada'}")

        # Mute/Unmute sons
        if event.key == pygame.K_s:
            sound_enabled = not sound_enabled
            volume = sound_volume if sound_enabled else 0
            if assets["flap_sound"]:
                assets["flap_sound"].set_volume(volume)
            if assets["score_sound"]:
                assets["score_sound"].set_volume(volume)
            if assets["hit_sound"]:
                assets["hit_sound"].set_volume(volume)
            print(f"Sons {'ativados' if sound_enabled else 'desativados'}")


# Função principal do jogo
def game():
    global game_state, ground_scroll, scroll_speed, particles

    # Inicializar pássaro
    bird = Bird(100, HEIGHT // 2, selected_character)

    # Inicializar tubos
    pipes = []
    pipe_timer = 0
    pipe_interval = 1500  # ms

    # Pontuação
    score = 0

    running = True
    while running and game_state == GAME:
        current_time = pygame.time.get_ticks()

        # Verificar e atualizar nível
        check_level_up(score)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            #  TECLA ESC PARA VOLTAR
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = MENU
                    running = False
                    break

                if event.key == pygame.K_SPACE:
                    bird.flap()

            if event.type == pygame.MOUSEBUTTONDOWN:
                bird.flap()

        if not running:
            break

        # Atualizar partículas
        for particle in particles[:]:
            if not particle.update():
                particles.remove(particle)

        # Atualizar pássaro
        bird.update()

        # Gerar tubos
        if current_time - pipe_timer > pipe_interval:
            pipes.append(Pipe(WIDTH, current_level))
            pipe_timer = current_time

        # Atualizar tubos
        for pipe in pipes[:]:
            pipe.update()

            # Verificar colisão
            if pipe.check_collision(bird.rect):
                if assets["hit_sound"] and sound_enabled:
                    assets["hit_sound"].play()
                game_state = GAME_OVER
                running = False

            # Verificar pontuação
            if pipe.check_score(bird.x):
                score += 1
                if assets["score_sound"] and sound_enabled:
                    assets["score_sound"].play()

            # Remover tubos fora da tela
            if pipe.top_pipe.x < -100:
                pipes.remove(pipe)

        # Verificar se o pássaro saiu da tela
        if bird.y > HEIGHT - 100 or bird.y < 0:
            if assets["hit_sound"] and sound_enabled:
                assets["hit_sound"].play()
            game_state = GAME_OVER
            running = False

        # Atualizar scroll do chão
        ground_scroll = (ground_scroll - scroll_speed) % 20

        # Desenhar fundo
        draw_parallax(current_level)

        # Desenhar elementos decorativos
        if current_level < 2:  # Nuvens só de dia/tarde
            draw_clouds()
        if current_level < 3:  # Sol só de dia/tarde/entardecer
            draw_sun()

        # Desenhar tubos
        for pipe in pipes:
            pipe.draw()

        # Desenhar partículas
        for particle in particles:
            particle.draw(screen)

        # Desenhar pássaro
        bird.draw()

        # Desenhar placar
        draw_score(score, WIDTH // 2, 50)

        # Desenhar nível atual
        level_font = pygame.font.SysFont("Arial", 20, bold=True)
        level_text = level_font.render(
            f"Nível: {LEVELS[current_level]['name']}", True, WHITE
        )
        screen.blit(level_text, (WIDTH - level_text.get_width() - 10, 50))

        # Desenhar chão
        draw_ground()

        pygame.display.update()
        clock.tick(FPS)

    # Ao sair do jogo, mostrar tela de game over
    if not running and game_state == GAME_OVER:
        game_over_screen(score)


# Loop principal do jogo
def main():
    global game_state

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Manipular atalhos globais
            handle_global_shortcuts(event)

        if game_state == MENU:
            main_menu()
        elif game_state == GAME:
            game()
        elif game_state == CHARACTER_SELECT:
            character_select()
        elif game_state == SCORE_BOARD:
            score_board()
        elif game_state == SETTINGS:
            settings_menu()
        elif game_state == CONTROLS:
            controls_menu()
        elif game_state == GAME_OVER:
            # Este estado é tratado dentro das funções de jogo
            pass

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
