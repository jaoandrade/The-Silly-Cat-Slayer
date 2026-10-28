import pygame
import sys
import random

pygame.init()
pygame.mixer.init()

explosion_sound = pygame.mixer.Sound("assets/sounds/explosion.wav")
arrow_sound = pygame.mixer.Sound("assets/sounds/flecha.wav")
meow_sound = pygame.mixer.Sound("assets/sounds/meow.wav")
meow_sounds = [
    pygame.mixer.Sound("assets/sounds/meowmeow1.wav"),
    pygame.mixer.Sound("assets/sounds/meowmeow2.wav"),
    pygame.mixer.Sound("assets/sounds/meowmeow3.wav"),
    pygame.mixer.Sound("assets/sounds/meowmeow4.wav"),
    pygame.mixer.Sound("assets/sounds/meowmeow5.wav")
]
hurt_sound = pygame.mixer.Sound("assets/sounds/hurt.wav")

tracks = [0, 178, 304, 510, 679, 839]
current_track_index = random.choice(range(len(tracks)))
pygame.mixer.music.load("assets/sounds/background.mp3")
pygame.mixer.music.play(-1, start=tracks[current_track_index])

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My First Game - João Andrade")
icone = pygame.image.load("assets/icon.png")
pygame.display.set_icon(icone)
clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 72)
invincible_font = pygame.font.Font(None, int(36 * 0.62))
death_score_font = pygame.font.Font(None, int(72 * 0.6))

WORLD_WIDTH = 1600
WORLD_HEIGHT = 1200
world_rect = pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT)

zoom = 2.5
fullscreen = False
bg_muted = False
sfx_muted = False
music_volume = 1.0

def update_sfx_volume():
    vol = 0 if sfx_muted else 1.0
    explosion_sound.set_volume(vol)
    arrow_sound.set_volume(vol)
    meow_sound.set_volume(vol)
    hurt_sound.set_volume(vol)
    for s in meow_sounds:
        s.set_volume(vol)

update_sfx_volume()

def load_single_image(path):
    return pygame.image.load(path).convert_alpha()

def load_spritesheet(path, frame_width, frame_height):
    sheet = pygame.image.load(path).convert_alpha()
    sheet_width, _ = sheet.get_size()
    num_frames = sheet_width // frame_width
    frames = []
    for i in range(num_frames):
        frame = sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
        frames.append(frame.copy())
    return frames

def scale_frames_list(frames, scale):
    return [pygame.transform.scale(f, (int(f.get_width()*scale), int(f.get_height()*scale))) for f in frames]

background_img = load_single_image("assets/background/background.png")
background_img = pygame.transform.scale(background_img, (int(background_img.get_width()*zoom), int(background_img.get_height()*zoom)))
menu_bg_img = load_single_image("assets/background/backgroundmenu.png")
menu_bg_img = pygame.transform.scale(menu_bg_img, (WIDTH, HEIGHT))
menu_cat_img = load_single_image("assets/catholder/sillycat1.png")
menu_cat_img = pygame.transform.scale(menu_cat_img, (int(WIDTH * 0.35), int(HEIGHT * 0.4)))
death_bg_img = load_single_image("assets/background/backgrounddeath.png")
death_bg_img = pygame.transform.scale(death_bg_img, (WIDTH, HEIGHT))
death_cat_img = load_single_image("assets/catholder/sillycat2.png")
death_cat_img = pygame.transform.scale(death_cat_img, (int(WIDTH * 0.35), int(HEIGHT * 0.4)))

FRAME_WIDTH, FRAME_HEIGHT = 32, 32
idle_up = scale_frames_list([load_single_image("assets/jogador/idle/hero_idle_UP.png")], zoom)
idle_down = scale_frames_list([load_single_image("assets/jogador/idle/hero_idle_DOWN.png")], zoom)
idle_left = scale_frames_list([load_single_image("assets/jogador/idle/hero_idle_LEFT.png")], zoom)
idle_right = scale_frames_list([load_single_image("assets/jogador/idle/hero_idle_RIGHT.png")], zoom)
walk_up = scale_frames_list(load_spritesheet("assets/jogador/walk/hero_walk_UP.png", FRAME_WIDTH, FRAME_HEIGHT), zoom)
walk_down = scale_frames_list(load_spritesheet("assets/jogador/walk/hero_walk_DOWN.png", FRAME_WIDTH, FRAME_HEIGHT), zoom)
walk_left = scale_frames_list(load_spritesheet("assets/jogador/walk/hero_walk_LEFT.png", FRAME_WIDTH, FRAME_HEIGHT), zoom)
walk_right = scale_frames_list(load_spritesheet("assets/jogador/walk/hero_walk_RIGHT.png", FRAME_WIDTH, FRAME_HEIGHT), zoom)
bow_up = scale_frames_list(load_spritesheet("assets/jogador/bow/hero_Bow_UP.png", FRAME_WIDTH, FRAME_HEIGHT), zoom)
bow_down = scale_frames_list(load_spritesheet("assets/jogador/bow/hero_Bow_DOWN.png", FRAME_WIDTH, FRAME_HEIGHT), zoom)
bow_left = scale_frames_list(load_spritesheet("assets/jogador/bow/hero_Bow_LEFT.png", FRAME_WIDTH, FRAME_HEIGHT), zoom)
bow_right = scale_frames_list(load_spritesheet("assets/jogador/bow/hero_Bow_RIGHT.png", FRAME_WIDTH, FRAME_HEIGHT), zoom)

player_animations = {
    "idle": {"up": idle_up, "down": idle_down, "left": idle_left, "right": idle_right},
    "walk": {"up": walk_up, "down": walk_down, "left": walk_left, "right": walk_right},
    "bow": {"up": bow_up, "down": bow_down, "left": bow_left, "right": bow_right}
}

explosion_frames = []
for i in range(1, 11):
    e_img = load_single_image(f"assets/explosions/Explosion_{i}.png")
    explosion_frames.append(e_img)
explosion_frames = scale_frames_list(explosion_frames, 0.5)

def draw_tiled_background(surface, bg_img, ox, oy):
    bw, bh = bg_img.get_size()
    sx = int(-ox) // bw * bw - bw
    sy = int(-oy) // bh * bh - bh
    ex = sx + WIDTH + bw * 2
    ey = sy + HEIGHT + bh * 2
    for x in range(sx, ex, bw):
        for y in range(sy, ey, bh):
            surface.blit(bg_img, (x + ox, y + oy))

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, anims):
        super().__init__()
        self.animations = anims
        self.state = "idle"
        self.direction = "down"
        self.speed = 5
        self.frame_index = 0
        self.image = self.animations[self.state][self.direction][self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))
        self.frame_counter = 0
        self.frame_delay_normal = 1
        self.frame_delay_bow = 2
        self.arrow_fired = False
        self.bowing = False
        self.bow_duration = 20
        self.bow_timer = 0
        self.lives = 3
        self.invincible = False
        self.invincible_time = 2000
        self.invincible_start = 0

    def update(self, keys, object_group, arrow_group):
        old_rect = self.rect.copy()
        dx, dy = 0, 0
        if not self.bowing:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -self.speed
                self.direction = "left"
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = self.speed
                self.direction = "right"
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -self.speed
                self.direction = "up"
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = self.speed
                self.direction = "down"
        if self.bowing:
            self.state = "bow"
            delay = self.frame_delay_bow
        else:
            self.state = "walk" if (dx or dy) else "idle"
            delay = self.frame_delay_normal
        self.rect.move_ip(dx, dy)
        self.rect.clamp_ip(world_rect)
        collided = pygame.sprite.spritecollide(self, object_group, False)
        if collided:
            self.rect = old_rect
        anim_list = self.animations[self.state][self.direction]
        self.frame_counter += 1
        if self.frame_counter >= delay:
            self.frame_counter = 0
            self.frame_index = (self.frame_index + 1) % len(anim_list)
        self.image = anim_list[self.frame_index]
        if self.bowing and not self.arrow_fired:
            mid = len(anim_list) // 2
            if self.frame_index == mid:
                arrow = Arrow(self.rect.centerx, self.rect.centery, self.direction)
                arrow_group.add(arrow)
                self.arrow_fired = True
                arrow_sound.play()
        if self.bowing:
            self.bow_timer -= 1
            if self.bow_timer <= 0:
                self.bowing = False
                self.arrow_fired = False
                self.frame_index = 0
        if self.invincible and pygame.time.get_ticks() - self.invincible_start >= self.invincible_time:
            self.invincible = False

class Arrow(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = load_single_image(f"assets/arrow/shot/arrow_shot_{direction.upper()}.png")
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width()*2.2), int(self.image.get_height()*1.2)))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10
        self.direction = direction

    def update(self):
        if self.direction == "up":
            self.rect.y -= self.speed
        elif self.direction == "down":
            self.rect.y += self.speed
        elif self.direction == "left":
            self.rect.x -= self.speed
        elif self.direction == "right":
            self.rect.x += self.speed
        if not world_rect.colliderect(self.rect):
            self.kill()

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        filename = f"assets/objetos/objeto{random.randint(1,6)}.png"
        image = load_single_image(filename)
        self.image = pygame.transform.scale(image, size)
        self.rect = self.image.get_rect(center=(x, y))
        self.vx = random.choice([-1, -0.5, 0.5, 1])
        self.vy = random.choice([-1, -0.5, 0.5, 1])
        self.behavior = "chase" if random.random() < 0.2 else "normal"
        self.stuck_counter = 0
        self.invulnerable = False
        self.invuln_timer = 0

    def update(self, object_group):
        old_rect = self.rect.copy()
        bonus = 0
        if game_time >= 30000:
            bonus = 0.3 + ((game_time - 30000) // 60000) * 0.3
        if self.behavior == "chase":
            base_speed = 0.5 * player.speed
            total_speed = min(base_speed + bonus, 1.7 * player.speed)
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            dist = (dx**2 + dy**2)**0.5 or 1
            self.vx = dx / dist * total_speed
            self.vy = dy / dist * total_speed
            self.rect.x += int(self.vx)
            self.rect.y += int(self.vy)
        else:
            base_speed = 0.5 * player.speed
            total_speed = min(base_speed + bonus, 1.7 * player.speed)
            self.rect.x += int(self.vx * total_speed)
            self.rect.y += int(self.vy * total_speed)
            collided = pygame.sprite.spritecollide(self, object_group, False)
            for obj in collided:
                if obj != self:
                    self.vx = -self.vx
                    self.vy = -self.vy
                    self.rect = old_rect
        if self.rect.left < 0 or self.rect.right > WORLD_WIDTH:
            self.vx = -self.vx
            self.rect = old_rect
        if self.rect.top < 0 or self.rect.bottom > WORLD_HEIGHT:
            self.vy = -self.vy
            self.rect = old_rect
        if (self.rect.left <= 0 or self.rect.right >= WORLD_WIDTH or
            self.rect.top <= 0 or self.rect.bottom >= WORLD_HEIGHT):
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0
        if self.invulnerable:
            self.invuln_timer += 1
            if self.invuln_timer >= 90:
                self.invulnerable = False
                self.invuln_timer = 0
        elif self.stuck_counter > 90:
            self.invulnerable = True
            self.invuln_timer = 0
        if self.rect.colliderect(player.rect):
            if self.behavior == "chase":
                self.vx = -abs(self.vx)
                self.vy = -abs(self.vy)
            else:
                self.vx = -self.vx
                self.vy = -self.vy
            self.rect = old_rect
            if not player.invincible and not self.invulnerable:
                player.lives -= 1
                player.invincible = True
                player.invincible_start = pygame.time.get_ticks()
                expl = Explosion(self.rect.centerx, self.rect.centery)
                explosion_group.add(expl)
                all_sprites.add(expl)
                hurt_sound.play()
                explosion_sound.play()
                self.kill()
            else:
                self.vx = -self.vx
                self.vy = -self.vy
                self.rect = old_rect

class Grass(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        idx = random.randint(1,32)
        filename = f"assets/relva/grassandflowers{idx}.png"
        self.image = load_single_image(filename)
        self.rect = self.image.get_rect(center=(x, y))
        self.rect.inflate_ip(-self.rect.width, -self.rect.height)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = explosion_frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))
        self.counter = 0
        self.frame_delay = 2

    def update(self):
        self.counter += 1
        if self.counter >= self.frame_delay:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.kill()
                return
            self.image = self.frames[self.frame_index]

def get_valid_spawn_position(group, player, min_distance=80):
    margin = 50
    for _ in range(100):
        x = random.randint(margin, WORLD_WIDTH - margin)
        y = random.randint(margin, WORLD_HEIGHT - margin)
        valid = True
        for spr in group:
            dist = ((x - spr.rect.centerx)**2 + (y - spr.rect.centery)**2)**0.5
            if dist < min_distance:
                valid = False
                break
        pdist = ((x - player.rect.centerx)**2 + (y - player.rect.centery)**2)**0.5
        if pdist < min_distance:
            valid = False
        if valid:
            return x, y
    return None, None

def spawn_initial_enemies():
    for _ in range(10):
        pos = get_valid_spawn_position(object_group, player, min_distance=80)
        if pos is not None:
            ox, oy = pos
            obj = Object(ox, oy, player_size)
            object_group.add(obj)
            all_sprites.add(obj)

def check_chasers():
    desired = 2 + (game_time // 60000)
    chasers = [o for o in object_group if o.behavior == "chase"]
    if len(object_group) >= 3 and len(chasers) < desired:
        needed = desired - len(chasers)
        non_chasers = [o for o in object_group if o.behavior != "chase"]
        non_chasers_sorted = sorted(non_chasers, key=lambda o: ((o.rect.centerx - player.rect.centerx)**2 + (o.rect.centery - player.rect.centery)**2))
        for o in non_chasers_sorted[:needed]:
            o.behavior = "chase"

def iniciar_jogo():
    global all_sprites, grass_group, player_group, arrow_group, object_group, explosion_group
    global player, player_size, score, game_time, difficulty
    all_sprites = pygame.sprite.Group()
    grass_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    arrow_group = pygame.sprite.Group()
    object_group = pygame.sprite.Group()
    explosion_group = pygame.sprite.Group()
    for i in range(40):
        if i % 5 == 0:
            bx = random.randint(0, WORLD_WIDTH)
            by = random.randint(0, WORLD_HEIGHT)
            for j in range(random.randint(2,5)):
                ox = random.randint(-30, 30)
                oy = random.randint(-30, 30)
                gx = bx + ox
                gy = by + oy
                if 0 <= gx <= WORLD_WIDTH and 0 <= gy <= WORLD_HEIGHT:
                    g = Grass(gx, gy)
                    grass_group.add(g)
                    all_sprites.add(g)
        else:
            gx = random.randint(0, WORLD_WIDTH)
            gy = random.randint(0, WORLD_HEIGHT)
            g = Grass(gx, gy)
            grass_group.add(g)
            all_sprites.add(g)
    px = WORLD_WIDTH // 2
    py = WORLD_HEIGHT // 2
    player = Player(px, py, player_animations)
    player.invincible = True
    player.invincible_start = pygame.time.get_ticks()
    player_group.add(player)
    all_sprites.add(player)
    player_size = (player.rect.width, player.rect.height)
    score = 0
    game_time = 0
    difficulty = 0
    spawn_initial_enemies()

def draw_text_with_outline(text, fnt, col, out_col, center):
    base = fnt.render(text, True, col)
    outl = fnt.render(text, True, out_col)
    rect = base.get_rect(center=center)
    for dx in [-2, 0, 2]:
        for dy in [-2, 0, 2]:
            if dx or dy:
                r2 = rect.copy()
                r2.x += dx
                r2.y += dy
                screen.blit(outl, r2)
    screen.blit(base, rect)

def draw_menu():
    screen.blit(menu_bg_img, (0, 0))
    draw_text_with_outline("The Silly Cat Slayer", title_font, (255,255,255), (0,0,0), (WIDTH//2, HEIGHT//3))
    play_text = font.render("Play", True, (255,255,255))
    settings_text = font.render("Settings", True, (255,255,255))
    quit_text = font.render("Quit", True, (255,255,255))
    play_rect = play_text.get_rect(center=(WIDTH//2, HEIGHT//2))
    settings_rect = settings_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
    quit_rect = quit_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 100))
    for dx in [-2, 0, 2]:
        for dy in [-2, 0, 2]:
            if dx or dy:
                r1 = play_rect.copy(); r1.x += dx; r1.y += dy
                screen.blit(font.render("Play", True, (0,0,0)), r1)
                r2 = settings_rect.copy(); r2.x += dx; r2.y += dy
                screen.blit(font.render("Settings", True, (0,0,0)), r2)
                r3 = quit_rect.copy(); r3.x += dx; r3.y += dy
                screen.blit(font.render("Quit", True, (0,0,0)), r3)
    screen.blit(play_text, play_rect)
    screen.blit(settings_text, settings_rect)
    screen.blit(quit_text, quit_rect)
    lines = ["Move - WASD", "Space - Arrow", "Menu - M"]
    sx, sy = 10, 10
    ls = 40
    for i, txt in enumerate(lines):
        tsurf = font.render(txt, True, (255,255,255))
        trect = tsurf.get_rect(topleft=(sx, sy + i*ls))
        draw_text_with_outline(txt, font, (255,255,255), (0,0,0), (trect.centerx, trect.centery))
    cat_rect = menu_cat_img.get_rect(bottomright=(WIDTH, HEIGHT))
    screen.blit(menu_cat_img, cat_rect)
    credit_font = pygame.font.Font(None, 22)
    credits_text = "Credits - João Andrade"
    draw_text_with_outline(credits_text, credit_font, (255,255,255), (0,0,0), (WIDTH-100, 20))
    return play_rect, settings_rect, quit_rect

def draw_settings_menu():
    screen.blit(menu_bg_img, (0, 0))
    draw_text_with_outline("Settings", title_font, (255,255,255), (0,0,0), (WIDTH//2, HEIGHT//5))
    lines = [
        [f"Fullscreen: {'On' if fullscreen else 'Off'}"],
        [f"Mute BG: {'On' if bg_muted else 'Off'}"],
        [f"Mute SFX: {'On' if sfx_muted else 'Off'}"],
        [f"Music Volume: {int(music_volume*100)}%", "Volume Up", "Volume Down"],
        ["Tracks:", "Previous Track", "Next Track"],
        ["Back"]
    ]
    rects = {}
    start_y = HEIGHT // 3
    ls = 50
    spacing = 30
    for i, items in enumerate(lines):
        surfs = []
        for it in items:
            s = font.render(it, True, (255,255,255))
            surfs.append((it, s))
        total_width = sum(s.get_width() for _, s in surfs) + (len(items)-1)*spacing
        x_start = (WIDTH - total_width) // 2
        y_pos = start_y + i * ls
        for it, s in surfs:
            r = s.get_rect(topleft=(x_start, y_pos))
            for dx in [-2,0,2]:
                for dy in [-2,0,2]:
                    if dx or dy:
                        rr = r.copy()
                        rr.x += dx
                        rr.y += dy
                        screen.blit(font.render(it, True, (0,0,0)), rr)
            screen.blit(s, r)
            rects[it] = r
            x_start += s.get_width() + spacing
    return rects

def draw_death_menu(final_score):
    screen.blit(death_bg_img, (0, 0))
    draw_text_with_outline("Game Over", title_font, (255,255,255), (0,0,0), (WIDTH//2, HEIGHT//3))
    draw_text_with_outline(f"Score: {final_score}", death_score_font, (255,0,0), (0,0,0), (WIDTH//2, HEIGHT//3 + 60))
    retry_text = font.render("Retry", True, (255,255,255))
    back_text = font.render("Back to Menu", True, (255,255,255))
    retry_rect = retry_text.get_rect(center=(WIDTH//2, HEIGHT//2))
    back_rect = back_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
    for dx in [-2,0,2]:
        for dy in [-2,0,2]:
            if dx or dy:
                r1 = retry_rect.copy(); r1.x += dx; r1.y += dy
                screen.blit(font.render("Retry", True, (0,0,0)), r1)
                r2 = back_rect.copy(); r2.x += dx; r2.y += dy
                screen.blit(font.render("Back to Menu", True, (0,0,0)), r2)
    screen.blit(retry_text, retry_rect)
    screen.blit(back_text, back_rect)
    cat_rect = death_cat_img.get_rect(bottomright=(WIDTH, HEIGHT))
    screen.blit(death_cat_img, cat_rect)
    return retry_rect, back_rect

game_state = "menu"
arrow_cooldown = 500
last_arrow_time = 0
running = True
score = 0
chase_check_timer = 0
game_time = 0
difficulty = 0

while running:
    dt = clock.tick(30)
    if game_state == "menu":
        pr, sr, qr = draw_menu()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if pr.collidepoint((mx, my)):
                    iniciar_jogo()
                    game_state = "playing"
                    last_arrow_time = pygame.time.get_ticks()
                    chase_check_timer = 0
                elif sr.collidepoint((mx, my)):
                    game_state = "settings"
                elif qr.collidepoint((mx, my)):
                    running = False
    elif game_state == "settings":
        rects = draw_settings_menu()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for opt, r in rects.items():
                    if r.collidepoint((mx, my)):
                        if opt.startswith("Fullscreen"):
                            fullscreen = not fullscreen
                            if fullscreen:
                                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                            else:
                                screen = pygame.display.set_mode((WIDTH, HEIGHT))
                        elif opt.startswith("Mute BG"):
                            bg_muted = not bg_muted
                            pygame.mixer.music.set_volume(0 if bg_muted else music_volume)
                        elif opt.startswith("Mute SFX"):
                            sfx_muted = not sfx_muted
                            update_sfx_volume()
                        elif opt.startswith("Volume Up"):
                            music_volume = min(1.0, music_volume + 0.1)
                            if not bg_muted:
                                pygame.mixer.music.set_volume(music_volume)
                        elif opt.startswith("Volume Down"):
                            music_volume = max(0.0, music_volume - 0.1)
                            if not bg_muted:
                                pygame.mixer.music.set_volume(music_volume)
                        elif opt.startswith("Previous Track"):
                            current_track_index = (current_track_index - 1) % len(tracks)
                            pygame.mixer.music.set_pos(tracks[current_track_index])
                        elif opt.startswith("Next Track"):
                            current_track_index = (current_track_index + 1) % len(tracks)
                            pygame.mixer.music.set_pos(tracks[current_track_index])
                        elif opt == "Back":
                            game_state = "menu"
    elif game_state == "playing":
        game_time += dt
        difficulty = min(game_time // 10000, 10)
        chase_check_timer += 1
        if chase_check_timer >= 150:
            check_chasers()
            chase_check_timer = 0
        minutes = game_time // 60000
        target_count = 10 + minutes * 5
        if len(object_group) < target_count and random.random() < 0.05:
            pos = get_valid_spawn_position(object_group, player, min_distance=80)
            if pos is not None:
                ox, oy = pos
                o = Object(ox, oy, player_size)
                object_group.add(o)
                all_sprites.add(o)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    now = pygame.time.get_ticks()
                    if now - last_arrow_time >= arrow_cooldown and not player.bowing:
                        player.bowing = True
                        player.bow_timer = player.bow_duration
                        player.arrow_fired = False
                        last_arrow_time = now
                elif event.key == pygame.K_m:
                    game_state = "menu"
        keys = pygame.key.get_pressed()
        player.update(keys, object_group, arrow_group)
        arrow_group.update()
        for obj in object_group:
            obj.update(object_group)
        explosion_group.update()
        hits = pygame.sprite.groupcollide(arrow_group, object_group, True, True)
        if hits:
            for a, objs in hits.items():
                for en in objs:
                    random.choice(meow_sounds).play()
                    expl = Explosion(en.rect.centerx, en.rect.centery)
                    explosion_group.add(expl)
                    all_sprites.add(expl)
                    explosion_sound.play()
            score += sum(len(v) for v in hits.values())
        offset_x = -player.rect.centerx + WIDTH//2
        offset_y = -player.rect.centery + HEIGHT//2
        draw_tiled_background(screen, background_img, offset_x, offset_y)
        for g in grass_group:
            screen.blit(g.image, (g.rect.x + offset_x, g.rect.y + offset_y))
        for s in all_sprites:
            if s not in grass_group:
                screen.blit(s.image, (s.rect.x + offset_x, s.rect.y + offset_y))
        for a in arrow_group:
            screen.blit(a.image, (a.rect.x + offset_x, a.rect.y + offset_y))
        boundary_rect = pygame.Rect(world_rect.x + offset_x, world_rect.y + offset_y, world_rect.width, world_rect.height)
        pygame.draw.rect(screen, (0,0,0), boundary_rect, 3)
        score_surf = font.render(f"Score: {score}", True, (255,255,255))
        life_color = (255, 0, 0) if player.invincible else (255,255,255)
        lifes_surf = font.render(f"Lifes: {player.lives}", True, life_color)
        timer_surf = font.render(f"Time: {int(game_time/1000)}s", True, (255,255,255))
        hud_x = WIDTH - 10
        hud_y = 10
        s_rect = score_surf.get_rect(topright=(hud_x, hud_y))
        l_rect = lifes_surf.get_rect(topright=(hud_x, s_rect.bottom + 5))
        t_rect = timer_surf.get_rect(topright=(hud_x, l_rect.bottom + 5))
        screen.blit(score_surf, s_rect)
        screen.blit(lifes_surf, l_rect)
        screen.blit(timer_surf, t_rect)
        if player.invincible:
            inv_surf = invincible_font.render("*INVINCIBLE*", True, (255,0,0))
            inv_rect = inv_surf.get_rect(center=(player.rect.centerx + offset_x, player.rect.y + offset_y + 0))
            screen.blit(inv_surf, inv_rect)
        if player.lives <= 0:
            game_state = "death"
        pygame.display.flip()
    elif game_state == "death":
        rr, br = draw_death_menu(score)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if rr.collidepoint((mx, my)):
                    iniciar_jogo()
                    game_state = "playing"
                    last_arrow_time = pygame.time.get_ticks()
                    chase_check_timer = 0
                    score = 0
                elif br.collidepoint((mx, my)):
                    game_state = "menu"

pygame.quit()
sys.exit()
