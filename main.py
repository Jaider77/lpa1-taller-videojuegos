# ...existing code...
import pygame
import random
import sys
import os
import math
from math import ceil

# Inicializar pygame (video y fuentes)
pygame.init()

# Intentar inicializar el mixer de forma segura (no detener ejecución si falla)
mixer_ok = True
try:
    pygame.mixer.init()
except Exception as e:
    print(f"[ADVERTENCIA] No se pudo inicializar el mixer: {e}")
    mixer_ok = False

# Función auxiliar para cargar sonidos de forma segura
def load_sound(path):
    if not mixer_ok:
        return None
    if os.path.exists(path):
        try:
            return pygame.mixer.Sound(path)
        except Exception as e:
            print(f"[ADVERTENCIA] Error al cargar sonido {path}: {e}")
            return None
    else:
        print(f"[ADVERTENCIA] No se encontró el sonido: {path}")
        return None

# Carga los sonidos disponibles (pueden ser None si faltan o mixer no disponible)
snd_shoot = load_sound("assets/sounds/shoot.wav")
snd_enemy_shoot = load_sound("assets/sounds/shoot_enemy.wav")
snd_final_boss_shoot = load_sound("assets/sounds/shoot_final_boss.wav")
snd_powerup = load_sound("assets/sounds/powerup.wav")

# Ajustar volumen (si existen)
if snd_shoot: snd_shoot.set_volume(0.4)
if snd_enemy_shoot: snd_enemy_shoot.set_volume(0.5)
if snd_final_boss_shoot: snd_final_boss_shoot.set_volume(0.6)
if snd_powerup: snd_powerup.set_volume(0.5)

# --------------------------------------------------
WIDTH, HEIGHT = 1280, 720
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Adventure - Fondo Simple y Elegante + Ráfaga")
CLOCK = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# ------------------------- UTILIDADES -------------------------
def load_image(path, size=None):
    """Carga una imagen si existe; devuelve None si no."""
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        return img
    return None

# ------------------------- FONDO (estrellas + planetas) -------------------------
class SimpleStarfield:
    def __init__(self, width, height, num_stars=120, num_planets=2):
        self.width = width
        self.height = height
        self.stars = [
            [random.uniform(0, width), random.uniform(0, height),
             random.uniform(0.15, 1.2), random.randint(1, 3),
             random.randint(150, 240)]
            for _ in range(num_stars)
        ]
        pal = [(12, 18, 36), (40, 18, 60), (80, 24, 28), (50, 30, 10)]
        self.planets = [
            [random.uniform(80, width - 80), random.uniform(60, height//2),
             random.randint(36, 80), random.choice(pal), random.uniform(0.02, 0.12)]
            for _ in range(num_planets)
        ]
        self.osc_angle = 0.0
        self.osc_amp = 10.0
        self.osc_speed = 0.5
        self.palette = [(12, 18, 36), (40, 18, 60), (80, 24, 28), (50, 30, 10)]
        self.current_color = self.palette[0]
        self.target_color = self.palette[0]
        self.color_t = 1.0
        self.bg_img = load_image("assets/background11.png")
        if self.bg_img:
            self.bg_img = pygame.transform.smoothscale(self.bg_img, (width, height))
        self.y_offset = 0.0
        self.scroll_speed = 0.6

    def set_level(self, level, total_levels):
        idx = min(int((level - 1) / max(1, total_levels - 1) * (len(self.palette) - 1)), len(self.palette) - 1)
        self.target_color = self.palette[idx]
        self.color_t = 0.0

    def update(self, vertical_speed_factor=1.0):
        if self.color_t < 1.0:
            self.color_t = min(1.0, self.color_t + 0.01)
            r = int(self.current_color[0] + (self.target_color[0] - self.current_color[0]) * self.color_t)
            g = int(self.current_color[1] + (self.target_color[1] - self.current_color[1]) * self.color_t)
            b = int(self.current_color[2] + (self.target_color[2] - self.current_color[2]) * self.color_t)
            self.current_color = (r, g, b)

        self.y_offset = (self.y_offset + self.scroll_speed * vertical_speed_factor) % self.height
        self.osc_angle += 0.01 * self.osc_speed

        for s in self.stars:
            s[1] += s[2] * vertical_speed_factor
            if s[1] > self.height:
                s[0] = random.uniform(0, self.width)
                s[1] = -1.0
                s[2] = random.uniform(0.15, 1.2)
                s[3] = random.randint(1, 3)
                s[4] = random.randint(150, 240)

        for p in self.planets:
            p[1] += p[4] * vertical_speed_factor
            p[0] += math.sin(self.osc_angle * 0.3 + p[0]*0.001) * 0.1
            if p[1] > self.height + p[2]:
                p[0] = random.uniform(80, self.width - 80)
                p[1] = -p[2]

    def draw(self, surf):
        base = pygame.Surface((self.width, self.height))
        base.fill(self.current_color)
        surf.blit(base, (0,0))

        if self.bg_img:
            img = self.bg_img.copy()
            img.set_alpha(120)
            y1 = -int(self.y_offset)
            y2 = y1 + self.height
            surf.blit(img, (0, y1))
            surf.blit(img, (0, y2))

        grad = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for i in range(self.height):
            a = int(30 * (i / self.height))
            grad.fill((0, 0, 0, a), rect=(0, i, self.width, 1))
        surf.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

        for px, py, pr, col, _ in self.planets:
            safe_col = tuple(max(0, min(255, int(c))) for c in col)
            planet_s = pygame.Surface((pr*2, pr*2), pygame.SRCALPHA)
            pygame.draw.circle(planet_s, safe_col + (160,), (pr, pr), pr)
            pygame.draw.circle(planet_s, (255,255,255,30), (int(pr*0.7), int(pr*0.6)), int(pr*0.25))
            surf.blit(planet_s, (int(px - pr), int(py - pr - (self.y_offset % self.height))))

        # corregido: usar bright en las tres componentes
        for sx, sy, spd, size, bright in self.stars:
            y = (sy - self.y_offset) % self.height
            c = max(0, min(255, int(bright)))
            color = (c, c, c)
            pygame.draw.circle(surf, color, (int(sx), int(y)), size)

# ------------------------- SPRITES / CARGA -------------------------
PLAYER_IMG = load_image("assets/player.png", (64, 64)) or pygame.Surface((64, 64), pygame.SRCALPHA)
ENEMY_GROUND_IMG = load_image("assets/enemy_ground.png", (56, 56)) or pygame.Surface((56, 56), pygame.SRCALPHA)
ENEMY_FLY_IMG = load_image("assets/enemy_flying.png", (56, 56)) or pygame.Surface((56, 56), pygame.SRCALPHA)
BOSS_IMG = load_image("assets/final_boss.png", (260, 260)) or pygame.Surface((260, 260), pygame.SRCALPHA)

def load_power(name):
    img = load_image(f"assets/{name}.png", (36, 36))
    if img:
        return img
    s = pygame.Surface((36,36), pygame.SRCALPHA)
    pygame.draw.circle(s, (100,200,255), (18,18), 16)
    return s

POWER_DOUBLE_IMG = load_power("power_double")
POWER_HEAL_IMG   = load_power("heal")
POWER_FAST_IMG   = load_power("fast")
POWER_SHIELD_IMG = load_power("power_shield")
POWER_RAFAGA_IMG = load_power("rafaga")

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

# ------------------------- CLASES JUEGO -------------------------
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy, color=(255,0,255), damage=1):
        super().__init__()
        surf = pygame.Surface((8,18), pygame.SRCALPHA)
        surf.fill(color)
        self.image = surf
        self.rect = self.image.get_rect(center=(x,y))
        self.vx = vx
        self.vy = vy
        self.damage = damage

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if (self.rect.bottom < 0 or self.rect.top > HEIGHT or
            self.rect.right < 0 or self.rect.left > WIDTH):
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
        imgs = {"double": POWER_DOUBLE_IMG, "heal": POWER_HEAL_IMG, "fast": POWER_FAST_IMG, "shield": POWER_SHIELD_IMG, "rafaga": POWER_RAFAGA_IMG}
        self.image = imgs.get(ptype, POWER_HEAL_IMG)
        self.rect = self.image.get_rect(center=(x, y))
        self.type = ptype
        self.speed = 2
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self, start_x=WIDTH//2, target_y=HEIGHT-80, initial_entry=True):
        super().__init__()
        self.image = PLAYER_IMG
        self.rect = self.image.get_rect(center=(start_x, -120 if initial_entry else target_y))
        self.target_y = target_y
        self.is_entering = initial_entry
        self.entry_speed = 5
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
        self.rafaga_active = False
        self.rafaga_timer = 0
        self.rafaga_duration = 10000
        self.rafaga_shot_delay = 300
        self.rafaga_last_shot = 0
        self.trail = []
        self.trail_length = 14

    def update(self):
        if self.is_entering:
            self.rect.y += self.entry_speed
            self.trail.append((self.rect.centerx, self.rect.bottom))
            if len(self.trail) > self.trail_length:
                self.trail.pop(0)
            if self.rect.y >= self.target_y:
                self.rect.y = self.target_y
                self.is_entering = False
            return

        keys = pygame.key.get_pressed()
        speed = 6
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += speed

        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > WIDTH: self.rect.right = WIDTH
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > HEIGHT: self.rect.bottom = HEIGHT

        now = pygame.time.get_ticks()
        if self.double_shot and now - self.double_timer > 10000:
            self.double_shot = False
        if self.fast_timer and now - self.fast_timer > 10000:
            self.bullet_speed = -12
            self.fast_timer = 0
        if self.shield and now - self.shield_timer > 10000:
            self.shield = False

        if self.rafaga_active and now - self.rafaga_timer > self.rafaga_duration:
            self.rafaga_active = False

        if self.rafaga_active and (now - self.rafaga_last_shot >= self.rafaga_shot_delay):
            self.fire_rafaga_front()
            self.rafaga_last_shot = now

        self.trail.append((self.rect.centerx, self.rect.bottom))
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)

    def draw_trail(self, surface):
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(200 * (i / max(1, self.trail_length - 1)))
            color = (100, 200, 255, alpha)
            trail_surface = pygame.Surface((10, 24), pygame.SRCALPHA)
            pygame.draw.ellipse(trail_surface, color, (0, 0, 10, 24))
            surface.blit(trail_surface, (tx - 5, ty - 12))

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot < self.shoot_delay:
            return
        self.last_shot = now
        if self.double_shot:
            b1 = Bullet(self.rect.centerx - 18, self.rect.top, 0, self.bullet_speed, (255,0,255), damage=self.damage)
            b2 = Bullet(self.rect.centerx + 18, self.rect.top, 0, self.bullet_speed, (255,0,255), damage=self.damage)
            all_sprites.add(b1, b2); bullets.add(b1, b2)
        else:
            b = Bullet(self.rect.centerx, self.rect.top, 0, self.bullet_speed, (255,0,255), damage=self.damage)
            all_sprites.add(b); bullets.add(b)
        if snd_shoot:
            snd_shoot.play()

    def fire_rafaga_front(self):
        origin_x = self.rect.centerx
        origin_y = self.rect.top - 6
        angles_deg = [-30, -15, 0, 15, 30]
        speed = 10.0
        color = (80, 180, 255)
        for a in angles_deg:
            rad = math.radians(a)
            vx = speed * math.sin(rad)
            vy = -speed * math.cos(rad)
            b = Bullet(origin_x, origin_y, vx, vy, color, damage=self.damage)
            all_sprites.add(b); bullets.add(b)
        # no sonido de ráfaga separado; si quieres, reutiliza snd_shoot o crea uno nuevo

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
        elif ptype == "rafaga":
            self.rafaga_active = True
            self.rafaga_timer = now
            self.rafaga_last_shot = 0
        if snd_powerup:
            snd_powerup.play()

    def reset_entry(self):
        self.rect.y = -120
        self.is_entering = True
        self.trail.clear()

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
            if snd_final_boss_shoot:
                snd_final_boss_shoot.play()
            self.last_shot = now

# ------------------------- AUX y BUCLE -------------------------
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
        ptype = random.choice(["double","heal","fast","shield","rafaga"])
        pu = PowerUp(enemy.rect.centerx, enemy.rect.centery, ptype)
        all_sprites.add(pu); powerups.add(pu)

all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
powerups = pygame.sprite.Group()
boss_group = pygame.sprite.Group()

player = Player(initial_entry=True)
all_sprites.add(player)
starfield = SimpleStarfield(WIDTH, HEIGHT, num_stars=120, num_planets=2)

current_level = 1
game_won = False
font_default = pygame.font.SysFont(None, 28)
font_big = pygame.font.SysFont(None, 84)

while current_level <= NUM_LEVELS:
    scroll_x = 0.0
    scroll_y = 0.0
    all_sprites.empty(); bullets.empty(); enemy_bullets.empty(); enemies.empty(); powerups.empty(); boss_group.empty()
    all_sprites.add(player)
    starfield.set_level(current_level, NUM_LEVELS)
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
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not player.is_entering:
                    player.shoot()

        vertical_speed = min(0.8 + current_level * 0.08, 4.0)
        starfield.scroll_speed = vertical_speed * 0.9
        starfield.update(vertical_speed)
        starfield.draw(WIN)

        all_sprites.update()
        bullets.update()
        enemy_bullets.update()
        powerups.update()
        boss_group.update()

        for e in list(enemies):
            if random.random() < (enemy_shoot_chance * 0.5):
                eb = EnemyBullet(e.rect.centerx, e.rect.bottom, 5 + current_level//3)
                all_sprites.add(eb); enemy_bullets.add(eb)
                if snd_enemy_shoot:
                    snd_enemy_shoot.play()

        hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
        for enemy, blist in hits.items():
            total_dmg = sum(b.damage for b in blist)
            enemy.hp -= total_dmg
            if enemy.hp <= 0:
                enemy.kill()
                player.score += 10 * current_level
                maybe_drop_powerup(enemy)

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

        player.draw_trail(WIN)

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

        if player.rafaga_active:
            WIN.blit(font_default.render("⚡ RÁFAGA ACTIVA ⚡", True, (100,200,255)), (WIDTH//2 - 90, 20))

        pygame.display.flip()

    if player.hp > 0 and not game_won:
        current_level += 1
    else:
        break

WIN.fill(BLACK)
font_big = pygame.font.SysFont(None, 72)
msg = font_big.render("🎉 ¡Juego Completado! 🎉" if game_won else "💀 JAJAJA PERDISTE 💀", True, WHITE)
WIN.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - msg.get_height()//2))
pygame.display.flip()
pygame.time.wait(3500)
pygame.quit()
sys.exit()
# ...existing code...