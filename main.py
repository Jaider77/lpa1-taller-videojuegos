# main.py
# Space Adventure - Version niveles con waves por nivel, pausa entre waves, bosses en nivel 5 y 10
# Resolución: 1280x720
# Requiere carpeta assets/ con background.png ... background10.png, player.png, enemy_ground.png, enemy_flying.png, final_boss.png, power_*.png

import pygame
import random
import sys
import os
from math import ceil

pygame.init()
WIDTH, HEIGHT = 1280, 720
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Adventure - Niveles & Oleadas")
CLOCK = pygame.time.Clock()
FPS = 60

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# -------------------------
# Utilidades de carga
# -------------------------
def load_image(path, size=None):
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    return None

# cargar backgrounds 1..10 con fallback a background.png o un color placeholder
backgrounds = []
for i in range(1, 11):
    p = "assets/background.png" if i == 1 else f"assets/background{i}.png"
    img = load_image(p, (WIDTH, HEIGHT))
    if not img:
        img = load_image("assets/background.png", (WIDTH, HEIGHT))
        if not img:
            base = pygame.Surface((WIDTH, HEIGHT))
            base.fill(((20*i) % 255, (10*i) % 255, (30*i) % 255))
            img = base
    backgrounds.append(img)

# sprites/ powerups
PLAYER_IMG = load_image("assets/player.png", (64,64)) or pygame.Surface((64,64))
ENEMY_GROUND_IMG = load_image("assets/enemy_ground.png", (56,56)) or pygame.Surface((56,56))
ENEMY_FLY_IMG = load_image("assets/enemy_flying.png", (56,56)) or pygame.Surface((56,56))
BOSS_IMG = load_image("assets/final_boss.png", (260,260)) or pygame.Surface((260,260))

POWER_DOUBLE_IMG = load_image("assets/power_double.png", (36,36))
POWER_HEAL_IMG   = load_image("assets/heal.png", (36,36))
POWER_FAST_IMG   = load_image("assets/fast.png", (36,36))
POWER_SHIELD_IMG = load_image("assets/power_shield.png", (36,36))

def power_image_or_placeholder(img):
    if img:
        return img
    s = pygame.Surface((36,36), pygame.SRCALPHA)
    pygame.draw.circle(s, (100,200,255), (18,18), 16)
    return s

POWER_DOUBLE_IMG = power_image_or_placeholder(POWER_DOUBLE_IMG)
POWER_HEAL_IMG   = power_image_or_placeholder(POWER_HEAL_IMG)
POWER_FAST_IMG   = power_image_or_placeholder(POWER_FAST_IMG)
POWER_SHIELD_IMG = power_image_or_placeholder(POWER_SHIELD_IMG)

# -------------------------
# Parámetros (ajustables)
# -------------------------
NUM_LEVELS = 10
BASE_ENEMIES = 6
PLAYER_BASE_DAMAGE = 1

ENEMY_SPEED_BASE = 1.0
ENEMY_SPEED_INC = 0.35
ENEMY_SHOOT_BASE = 0.006
ENEMY_SHOOT_INC = 0.004

# pausa entre oleadas (ms) base y factor por nivel: cada nivel hace la pausa más larga
WAVE_PAUSE_BASE_MS = 2500
WAVE_PAUSE_PER_LEVEL_MS = 500

# -------------------------
# Clases
# -------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = PLAYER_IMG.copy() if isinstance(PLAYER_IMG, pygame.Surface) else PLAYER_IMG
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT-80))
        self.hp = 5
        self.score = 0
        self.damage = PLAYER_BASE_DAMAGE
        self.last_shot = 0
        self.shoot_delay = 300
        self.bullet_speed = -12
        self.double_shot = False
        self.double_timer = 0
        self.fast_timer = 0
        self.shield = False
        self.shield_timer = 0

    def update(self):
        keys = pygame.key.get_pressed()
        speed = 6
        if keys[pygame.K_LEFT]:
            self.rect.x -= speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += speed
        # límites
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WIDTH, self.rect.right)

        now = pygame.time.get_ticks()
        if self.double_shot and now - self.double_timer > 10000:
            self.double_shot = False
        if self.fast_timer and now - self.fast_timer > 10000:
            self.bullet_speed = -12
            self.fast_timer = 0
        if self.shield and now - self.shield_timer > 10000:
            self.shield = False

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot < self.shoot_delay:
            return
        self.last_shot = now
        if self.double_shot:
            b1 = Bullet(self.rect.centerx - 18, self.rect.top, self.bullet_speed, (255,0,255), damage=self.damage)
            b2 = Bullet(self.rect.centerx + 18, self.rect.top, self.bullet_speed, (255,0,255), damage=self.damage)
            all_sprites.add(b1, b2); bullets.add(b1, b2)
        else:
            b = Bullet(self.rect.centerx, self.rect.top, self.bullet_speed, (255,0,255), damage=self.damage)
            all_sprites.add(b); bullets.add(b)

    def apply_powerup(self, ptype):
        now = pygame.time.get_ticks()
        if ptype == "double":
            self.double_shot = True
            self.double_timer = now
        elif ptype == "heal":
            self.hp = min(self.hp + 1, 5)
        elif ptype == "fast":
            self.bullet_speed = -20
            self.fast_timer = now
        elif ptype == "shield":
            self.shield = True
            self.shield_timer = now

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, flying, level):
        super().__init__()
        self.image = ENEMY_FLY_IMG if flying else ENEMY_GROUND_IMG
        self.image = pygame.transform.scale(self.image, (56,56))
        self.rect = self.image.get_rect(topleft=(x,y))
        base_speed = ENEMY_SPEED_BASE + ENEMY_SPEED_INC * (level-1)
        self.speedx = random.choice([-1, 1]) * max(1, int(round(base_speed)))
        self.hp = 1 + (1 if flying else 0) + (level//3)
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.rect.x += self.speedx
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.speedx *= -1
            self.rect.y += 18

class Boss(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__()
        self.image = pygame.transform.scale(BOSS_IMG, (260,260))
        self.rect = self.image.get_rect(center=(WIDTH//2, 140))
        self.hp = 80 + level * 40
        self.level = level
        self.move_dir = 1
        self.speedx = 2 + level//2
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.rect.x += self.speedx * self.move_dir
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.move_dir *= -1
        now = pygame.time.get_ticks()
        interval = max(1200 - (self.level-1)*100, 400)
        if now - self.last_shot > interval:
            spread = 1 + (self.level-1)
            offsets = [i*25 for i in range(-spread, spread+1)]
            for off in offsets:
                eb = EnemyBullet(self.rect.centerx + off, self.rect.bottom, 6 + self.level//2)
                all_sprites.add(eb); enemy_bullets.add(eb)
            self.last_shot = now

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, color, damage=1):
        super().__init__()
        surf = pygame.Surface((8,18), pygame.SRCALPHA)
        surf.fill(color)
        self.image = surf
        self.rect = self.image.get_rect(center=(x,y))
        self.speedy = speed
        self.damage = damage

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        surf = pygame.Surface((8,14))
        surf.fill((255,80,80))
        self.image = surf
        self.rect = self.image.get_rect(center=(x,y))
        self.speedy = speed
    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, ptype):
        super().__init__()
        self.type = ptype
        if ptype == "double":
            self.image = POWER_DOUBLE_IMG
        elif ptype == "heal":
            self.image = POWER_HEAL_IMG
        elif ptype == "fast":
            self.image = POWER_FAST_IMG
        elif ptype == "shield":
            self.image = POWER_SHIELD_IMG
        else:
            self.image = pygame.Surface((36,36))
            self.image.fill((100,200,255))
        self.rect = self.image.get_rect(center=(x,y))
        self.speed = 2
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

# -------------------------
# Grupos globales (se re-inicializan por nivel)
# -------------------------
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
powerups = pygame.sprite.Group()
boss_group = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# -------------------------
# Mecánicas de spawn y difficulty
# -------------------------
def difficulty(level):
    enemy_speed = ENEMY_SPEED_BASE + ENEMY_SPEED_INC * (level-1)
    enemy_shoot_chance = ENEMY_SHOOT_BASE + ENEMY_SHOOT_INC * (level-1)
    player_damage = PLAYER_BASE_DAMAGE + (level-1) // 2
    return enemy_speed, enemy_shoot_chance, player_damage

def spawn_wave(level, qty):
    margin_x = 80
    spacing = max(80, (WIDTH - 2*margin_x) // qty)
    y_base = 60
    for i in range(qty):
        x = margin_x + i*spacing
        flying = (i % 3 == 0 and random.random() < 0.6)
        e = Enemy(x, y_base + (i % 3)*68, flying, level)
        all_sprites.add(e); enemies.add(e)

def maybe_drop_powerup(enemy):
    if random.random() < 0.25:
        ptype = random.choice(["double","heal","fast","shield"])
        pu = PowerUp(enemy.rect.centerx, enemy.rect.centery, ptype)
        all_sprites.add(pu); powerups.add(pu)

# -------------------------
# Fade util
# -------------------------
def fade_in(surface, duration=600):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0,0,0))
    steps = max(1, int(duration / 16))
    for i in range(steps, -1, -1):
        alpha = int(255 * (i / steps))
        overlay.set_alpha(alpha)
        WIN.blit(surface, (0,0))
        WIN.blit(overlay, (0,0))
        pygame.display.flip()
        CLOCK.tick(FPS)

# -------------------------
# Juego principal con oleadas por nivel
# -------------------------
current_level = 1
game_won = False
bg_list = backgrounds  # index 0..9 -> level 1..10

font_default = pygame.font.SysFont(None, 28)
font_big = pygame.font.SysFont(None, 84)

while current_level <= NUM_LEVELS:
    bg_img = bg_list[current_level-1]
    scroll_y = 0

    # reset groups for level (keep player persistent)
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    boss_group = pygame.sprite.Group()
    all_sprites.add(player)

    # difficulty and player damage adjust
    enemy_speed_val, enemy_shoot_chance, player_damage_value = difficulty(current_level)
    player.damage = player_damage_value

    # waves in this level = current_level (level 1 -> 1 wave, level2 -> 2 waves, ...)
    total_waves = current_level
    completed_waves = 0

    # prepare first wave immediately
    enemies_qty_base = BASE_ENEMIES + (current_level - 1) * 2
    spawn_wave(current_level, enemies_qty_base)

    # show level title with fade
    lvl_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    txt = font_big.render(f"Nivel {current_level}", True, WHITE)
    lvl_surf.blit(bg_img, (0,0))
    lvl_surf.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - txt.get_height()//2))
    fade_in(lvl_surf, duration=700)

    boss_spawned = False
    level_running = True

    # inter-wave timing variables
    waiting_for_next_wave = False
    next_wave_start_time = 0
    wave_pause_ms = WAVE_PAUSE_BASE_MS + (current_level-1) * WAVE_PAUSE_PER_LEVEL_MS

    while level_running:
        CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player.shoot()

        # background scroll
        scroll_y += 1 + current_level*0.08
        if scroll_y >= HEIGHT:
            scroll_y = 0
        WIN.blit(bg_img, (0, scroll_y))
        WIN.blit(bg_img, (0, scroll_y - HEIGHT))

        # update sprites
        all_sprites.update()
        bullets.update()
        enemy_bullets.update()
        powerups.update()
        boss_group.update()

        # enemies shooting based on chance (per-frame prob scaled by level)
        for e in list(enemies):
            if random.random() < (enemy_shoot_chance * 0.5):  # scaling to reduce frequency
                eb = EnemyBullet(e.rect.centerx, e.rect.bottom, 5 + current_level//3)
                all_sprites.add(eb); enemy_bullets.add(eb)

        # collisions bullets vs enemies
        hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
        for enemy, blist in hits.items():
            total_dmg = sum(b.damage for b in blist)
            enemy.hp -= total_dmg
            if enemy.hp <= 0:
                enemy.kill()
                player.score += 10 * current_level
                maybe_drop_powerup(enemy)

        # if no enemies currently alive and not boss, we finished a wave
        if not enemies and not boss_spawned and not waiting_for_next_wave:
            completed_waves += 1
            # if completed waves < total_waves -> schedule next wave with pause
            if completed_waves < total_waves:
                waiting_for_next_wave = True
                next_wave_start_time = pygame.time.get_ticks() + wave_pause_ms
            else:
                # all waves completed for this level -> spawn boss if level is multiple of 5, otherwise finish level
                if current_level % 5 == 0:
                    boss = Boss(current_level)
                    all_sprites.add(boss); boss_group.add(boss)
                    boss_spawned = True
                else:
                    level_running = False

        # handle waiting_for_next_wave countdown
        if waiting_for_next_wave:
            now = pygame.time.get_ticks()
            remain = max(0, next_wave_start_time - now)
            secs = ceil(remain / 1000)
            # show countdown on screen
            txt_w = font_default.render(f"Siguiente oleada en: {secs}s   (Oleada {completed_waves+1}/{total_waves})", True, WHITE)
            WIN.blit(txt_w, (WIDTH//2 - txt_w.get_width()//2, HEIGHT//2 - 40))
            if now >= next_wave_start_time:
                # spawn next wave, increase difficulty slightly per wave within level
                next_qty = enemies_qty_base + completed_waves  # each wave adds 1 enemy
                spawn_wave(current_level, next_qty)
                waiting_for_next_wave = False

        # boss collisions
        if boss_spawned and boss_group:
            hitsb = pygame.sprite.groupcollide(boss_group, bullets, False, True)
            for bobj, bls in hitsb.items():
                total = sum(b.damage for b in bls)
                bobj.hp -= total
                if bobj.hp <= 0:
                    bobj.kill()
                    player.score += 500
                    boss_spawned = False
                    # if final level boss -> win
                    if current_level == NUM_LEVELS:
                        game_won = True
                        level_running = False
                        current_level = NUM_LEVELS + 1
                    else:
                        level_running = False

        # enemy bullets vs player
        if not player.shield:
            if pygame.sprite.spritecollide(player, enemy_bullets, True):
                player.hp -= 1
                if player.hp <= 0:
                    level_running = False
                    current_level = NUM_LEVELS + 1  # force exit outer loop

        # player - powerups
        pups = pygame.sprite.spritecollide(player, powerups, True)
        for pu in pups:
            player.apply_powerup(pu.type)

        # draw sprites
        all_sprites.draw(WIN)
        bullets.draw(WIN)
        enemy_bullets.draw(WIN)
        powerups.draw(WIN)
        boss_group.draw(WIN)

        # HUD
        WIN.blit(font_default.render(f"Nivel: {current_level}/{NUM_LEVELS}", True, WHITE), (12,12))
        WIN.blit(font_default.render(f"Vidas: {player.hp}", True, WHITE), (12,40))
        WIN.blit(font_default.render(f"Puntaje: {player.score}", True, WHITE), (12,68))
        WIN.blit(font_default.render(f"Oleadas: {completed_waves}/{total_waves}", True, WHITE), (12,96))

        # shield visual
        if player.shield:
            s = pygame.Surface((player.rect.width+30, player.rect.height+30), pygame.SRCALPHA)
            pygame.draw.ellipse(s, (50,180,255,100), s.get_rect())
            WIN.blit(s, (player.rect.x-15, player.rect.y-15))

        pygame.display.flip()

    # end of level loop -> advance if alive and not finished all levels
    if player.hp > 0 and not game_won:
        current_level += 1
    else:
        break

# final screen
WIN.fill(BLACK)
font_big = pygame.font.SysFont(None, 72)
if game_won and player.hp > 0:
    msg = font_big.render("🎉 ¡Juego Completado! 🎉", True, WHITE)
else:
    msg = font_big.render("💀 GAME OVER 💀", True, WHITE)
WIN.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - msg.get_height()//2))
pygame.display.flip()
pygame.time.wait(3500)

pygame.quit()
sys.exit()
