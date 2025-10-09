# main.py
# Space Adventure - Fondo único animado con transición suave en bucle
# Requiere carpeta assets/ con background11.png, player.png, enemy_ground.png,
# enemy_flying.png, final_boss.png, power_*.png

import pygame
import random
import sys
import os
import math
from math import ceil

pygame.init()
WIDTH, HEIGHT = 1280, 720
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Adventure - Fondo Único Animado")
CLOCK = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# ------------------------- UTILIDADES -------------------------
def load_image(path, size=None):
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    return None

# ✅ Fondo único
bg_img = load_image("assets/background11.png", (WIDTH, HEIGHT))
if not bg_img:
    bg_img = pygame.Surface((WIDTH, HEIGHT))
    bg_img.fill((20, 20, 40))

# Sprites
PLAYER_IMG = load_image("assets/player.png", (64, 64)) or pygame.Surface((64, 64))
ENEMY_GROUND_IMG = load_image("assets/enemy_ground.png", (56, 56)) or pygame.Surface((56, 56))
ENEMY_FLY_IMG = load_image("assets/enemy_flying.png", (56, 56)) or pygame.Surface((56, 56))
BOSS_IMG = load_image("assets/final_boss.png", (260, 260)) or pygame.Surface((260, 260))

def load_power(name):
    img = load_image(f"assets/{name}.png", (36, 36))
    if img: return img
    s = pygame.Surface((36,36), pygame.SRCALPHA)
    pygame.draw.circle(s, (100,200,255), (18,18), 16)
    return s

POWER_DOUBLE_IMG = load_power("power_double")
POWER_HEAL_IMG   = load_power("heal")
POWER_FAST_IMG   = load_power("fast")
POWER_SHIELD_IMG = load_power("power_shield")

# ------------------------- PARÁMETROS -------------------------
NUM_LEVELS = 10
BASE_ENEMIES = 6
PLAYER_BASE_DAMAGE = 1
ENEMY_SPEED_BASE = 1.0
ENEMY_SPEED_INC = 0.35
ENEMY_SHOOT_BASE = 0.006
ENEMY_SHOOT_INC = 0.004
WAVE_PAUSE_BASE_MS = 2500
WAVE_PAUSE_PER_LEVEL_MS = 500

# ------------------------- CLASES -------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = PLAYER_IMG
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
        if keys[pygame.K_LEFT]: self.rect.x -= speed
        if keys[pygame.K_RIGHT]: self.rect.x += speed
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
            for dx in (-18, 18):
                b = Bullet(self.rect.centerx + dx, self.rect.top, self.bullet_speed, (255,0,255), self.damage)
                all_sprites.add(b); bullets.add(b)
        else:
            b = Bullet(self.rect.centerx, self.rect.top, self.bullet_speed, (255,0,255), self.damage)
            all_sprites.add(b); bullets.add(b)

    def apply_powerup(self, ptype):
        now = pygame.time.get_ticks()
        if ptype == "double":
            self.double_shot = True; self.double_timer = now
        elif ptype == "heal":
            self.hp = min(self.hp + 1, 5)
        elif ptype == "fast":
            self.bullet_speed = -20; self.fast_timer = now
        elif ptype == "shield":
            self.shield = True; self.shield_timer = now

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, flying, level):
        super().__init__()
        self.image = ENEMY_FLY_IMG if flying else ENEMY_GROUND_IMG
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speedx = random.choice([-1, 1]) * (1 + level * 0.3)
        self.hp = 1 + (1 if flying else 0) + (level//3)
    def update(self):
        self.rect.x += self.speedx
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.speedx *= -1
            self.rect.y += 18

class Boss(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__()
        self.image = BOSS_IMG
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
        imgs = {"double": POWER_DOUBLE_IMG, "heal": POWER_HEAL_IMG, "fast": POWER_FAST_IMG, "shield": POWER_SHIELD_IMG}
        self.image = imgs.get(ptype, POWER_HEAL_IMG)
        self.rect = self.image.get_rect(center=(x, y))
        self.type = ptype
        self.speed = 2
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

# ------------------------- FUNCIONES -------------------------
def difficulty(level):
    return ENEMY_SPEED_BASE + ENEMY_SPEED_INC * (level-1), ENEMY_SHOOT_BASE + ENEMY_SHOOT_INC * (level-1), PLAYER_BASE_DAMAGE + (level-1)//2

def spawn_wave(level, qty):
    margin_x = 80
    spacing = max(80, (WIDTH - 2*margin_x) // qty)
    y_base = 60
    for i in range(qty):
        x = margin_x + i * spacing
        flying = (i % 3 == 0 and random.random() < 0.6)
        e = Enemy(x, y_base + (i % 3) * 68, flying, level)
        all_sprites.add(e); enemies.add(e)

def maybe_drop_powerup(enemy):
    if random.random() < 0.25:
        ptype = random.choice(["double","heal","fast","shield"])
        pu = PowerUp(enemy.rect.centerx, enemy.rect.centery, ptype)
        all_sprites.add(pu); powerups.add(pu)

def draw_looping_background(bg, scroll_x, scroll_y, offset_x=0):
    """
    Fondo único con bucle vertical muy suave (sin cortes visibles).
    offset_x aplica oscilación horizontal leve.
    """
    x = int(scroll_x + offset_x) % WIDTH
    y = int(scroll_y) % HEIGHT

    WIN.blit(bg, (-x, -y))
    WIN.blit(bg, (-x + WIDTH, -y))
    WIN.blit(bg, (-x, -y + HEIGHT))
    WIN.blit(bg, (-x + WIDTH, -y + HEIGHT))

# ------------------------- BUCLE PRINCIPAL -------------------------
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
powerups = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

current_level = 1
game_won = False
font_default = pygame.font.SysFont(None, 28)
font_big = pygame.font.SysFont(None, 84)

while current_level <= NUM_LEVELS:
    scroll_x = 0.0
    scroll_y = 0.0

    # reset groups
    all_sprites.empty(); bullets.empty(); enemy_bullets.empty(); enemies.empty(); powerups.empty(); boss_group.empty()
    all_sprites.add(player)

    enemy_speed_val, enemy_shoot_chance, player_damage_value = difficulty(current_level)
    player.damage = player_damage_value
    total_waves = current_level
    completed_waves = 0
    enemies_qty_base = BASE_ENEMIES + (current_level - 1) * 2
    spawn_wave(current_level, enemies_qty_base)

    boss_spawned = False
    level_running = True
    waiting_for_next_wave = False
    next_wave_start_time = 0
    wave_pause_ms = WAVE_PAUSE_BASE_MS + (current_level-1)*WAVE_PAUSE_PER_LEVEL_MS

    while level_running:
        CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: player.shoot()

        # Fondo animado
        vertical_speed = min(0.8 + current_level * 0.08, 4.0)
        scroll_y = (scroll_y + vertical_speed) % HEIGHT
        scroll_x += 0.05

        # Oscilación suave
        time_now = pygame.time.get_ticks() / 1000.0
        amplitude = min(6 + current_level * 1.5, 25)
        speed = min(0.25 + current_level * 0.08, 0.9)
        oscillation = int(amplitude * math.sin(time_now * speed))

        # Dibujar fondo
        draw_looping_background(bg_img, scroll_x, scroll_y, offset_x=oscillation)

        # Actualizar sprites y lógica
        all_sprites.update(); bullets.update(); enemy_bullets.update(); powerups.update(); boss_group.update()

        for e in list(enemies):
            if random.random() < (enemy_shoot_chance * 0.5):
                eb = EnemyBullet(e.rect.centerx, e.rect.bottom, 5 + current_level//3)
                all_sprites.add(eb); enemy_bullets.add(eb)

        hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
        for enemy, blist in hits.items():
            enemy.hp -= sum(b.damage for b in blist)
            if enemy.hp <= 0:
                enemy.kill(); player.score += 10*current_level; maybe_drop_powerup(enemy)

        if not enemies and not boss_spawned and not waiting_for_next_wave:
            completed_waves += 1
            if completed_waves < total_waves:
                waiting_for_next_wave = True
                next_wave_start_time = pygame.time.get_ticks() + wave_pause_ms
            else:
                if current_level % 5 == 0:
                    boss = Boss(current_level)
                    all_sprites.add(boss); boss_group.add(boss)
                    boss_spawned = True
                else:
                    level_running = False

        if waiting_for_next_wave:
            now = pygame.time.get_ticks()
            remain = max(0, next_wave_start_time - now)
            secs = ceil(remain / 1000)
            txt_w = font_default.render(f"Siguiente oleada en: {secs}s", True, WHITE)
            WIN.blit(txt_w, (WIDTH//2 - txt_w.get_width()//2, HEIGHT//2 - 40))
            if now >= next_wave_start_time:
                spawn_wave(current_level, enemies_qty_base + completed_waves)
                waiting_for_next_wave = False

        if boss_spawned and boss_group:
            hitsb = pygame.sprite.groupcollide(boss_group, bullets, False, True)
            for bobj, bls in hitsb.items():
                bobj.hp -= sum(b.damage for b in bls)
                if bobj.hp <= 0:
                    bobj.kill()
                    player.score += 500
                    boss_spawned = False
                    if current_level == NUM_LEVELS:
                        game_won = True
                        level_running = False
                        current_level = NUM_LEVELS + 1
                    else:
                        level_running = False

        if not player.shield:
            if pygame.sprite.spritecollide(player, enemy_bullets, True):
                player.hp -= 1
                if player.hp <= 0:
                    level_running = False
                    current_level = NUM_LEVELS + 1

        pups = pygame.sprite.spritecollide(player, powerups, True)
        for pu in pups:
            player.apply_powerup(pu.type)

        # Dibujar todo
        all_sprites.draw(WIN)
        bullets.draw(WIN)
        enemy_bullets.draw(WIN)
        powerups.draw(WIN)
        boss_group.draw(WIN)

        WIN.blit(font_default.render(f"Nivel: {current_level}/{NUM_LEVELS}", True, WHITE), (12,12))
        WIN.blit(font_default.render(f"Vidas: {player.hp}", True, WHITE), (12,40))
        WIN.blit(font_default.render(f"Puntaje: {player.score}", True, WHITE), (12,68))
        WIN.blit(font_default.render(f"Oleadas: {completed_waves}/{total_waves}", True, WHITE), (12,96))

        if player.shield:
            s = pygame.Surface((player.rect.width+30, player.rect.height+30), pygame.SRCALPHA)
            pygame.draw.ellipse(s, (50,180,255,100), s.get_rect())
            WIN.blit(s, (player.rect.x-15, player.rect.y-15))

        pygame.display.flip()

    if player.hp > 0 and not game_won:
        current_level += 1
    else:
        break

# ------------------------- FINAL -------------------------
WIN.fill(BLACK)
font_big = pygame.font.SysFont(None, 72)
msg = font_big.render("🎉 ¡Juego Completado! 🎉" if game_won else "💀 JAJAJA PERDISTE 💀", True, WHITE)
WIN.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - msg.get_height()//2))
pygame.display.flip()
pygame.time.wait(3500)
pygame.quit()
sys.exit()
