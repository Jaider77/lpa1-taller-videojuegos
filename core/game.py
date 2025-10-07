import pygame, random # pyright: ignore[reportMissingImports]
from core import settings
from entities.player import Player
from entities.enemy import Enemy
from entities.treasure import Treasure
from entities.trap import Trap

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        pygame.display.set_caption("🚀 Space Shooter RPG")
        self.clock = pygame.time.Clock()

        # Grupos de sprites
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.treasures = pygame.sprite.Group()
        self.traps = pygame.sprite.Group()

        # Crear jugador
        self.player = Player(settings.WIDTH//2, settings.HEIGHT-50)
        self.all_sprites.add(self.player)

        # Spawn inicial de enemigos
        for i in range(5):
            enemy = Enemy(i*100+100, 50, enemy_type="ground")
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)

    def run(self):
        running = True
        while running:
            self.clock.tick(settings.FPS)

            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.player.shoot(self.projectiles)
                        self.all_sprites.add(self.projectiles)

            # Movimiento jugador
            keys = pygame.key.get_pressed()
            self.player.update(keys)

            # Actualizar enemigos, proyectiles, tesoros, trampas
            self.enemies.update()
            self.projectiles.update()
            self.treasures.update()
            self.traps.update()

            # Colisiones proyectil-enemigo
            hits = pygame.sprite.groupcollide(self.enemies, self.projectiles, True, True)
            for enemy in hits:
                # Drop de tesoro o trampa aleatorio
                if random.random() < 0.5:
                    treasure = Treasure(enemy.rect.x, enemy.rect.y, value=50)
                    self.all_sprites.add(treasure)
                    self.treasures.add(treasure)
                else:
                    trap = Trap(enemy.rect.x, enemy.rect.y)
                    self.all_sprites.add(trap)
                    self.traps.add(trap)

                # Recompensa de experiencia y dinero
                self.player.add_exp(50)
                self.player.add_money(20)

            # Colisiones jugador-tesoro
            treasures_collected = pygame.sprite.spritecollide(self.player, self.treasures, True)
            for treasure in treasures_collected:
                self.player.add_money(treasure.value)

            # Colisiones jugador-trampa
            traps_hit = pygame.sprite.spritecollide(self.player, self.traps, True)
            for trap in traps_hit:
                self.player.hp -= trap.damage
                print(f"💥 Has recibido {trap.damage} de daño. HP restante: {self.player.hp}")
                if self.player.hp <= 0:
                    print("☠️ GAME OVER")
                    running = False

            # Dibujar
            self.screen.fill(settings.BLACK)
            self.all_sprites.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
