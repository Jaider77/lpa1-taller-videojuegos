import pygame, random # pyright: ignore[reportMissingImports]
from core import settings

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="ground"):
        super().__init__()
        if enemy_type == "ground":
            self.image = pygame.image.load("assets/enemy_ground.png").convert_alpha()
        else:
            self.image = pygame.image.load("assets/enemy_flying.png").convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))

        # Atributos
        self.hp = 50
        self.attack = 5
        self.defense = 2
        self.type = enemy_type
        self.speed = random.randint(1, 3)

    def update(self):
        """Movimiento básico hacia abajo"""
        self.rect.y += self.speed
        if self.rect.top > settings.HEIGHT:
            self.kill()
