import pygame # pyright: ignore[reportMissingImports]
from core import settings

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("assets/player.png").convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5

        # Atributos RPG
        self.hp = 100
        self.attack = 10
        self.defense = 5
        self.level = 1
        self.exp = 0
        self.money = 0
        self.inventory = []

    def update(self, keys):
        """Mueve al jugador con las teclas"""
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < settings.WIDTH:
            self.rect.x += self.speed

    def shoot(self, projectile_group):
        """Dispara proyectiles"""
        from entities.projectile import Projectile
        projectile = Projectile(self.rect.centerx, self.rect.top)
        projectile_group.add(projectile)

    def add_exp(self, amount):
        self.exp += amount
        if self.exp >= self.level * 100:
            self.level += 1
            self.hp += 20
            self.attack += 5
            self.defense += 2
            print(f"⚡ Subiste al nivel {self.level}!")

    def add_money(self, amount):
        self.money += amount
        print(f"💰 Dinero actual: {self.money}")
