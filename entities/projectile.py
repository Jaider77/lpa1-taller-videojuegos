import pygame # pyright: ignore[reportMissingImports]
from core import settings

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill(settings.RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -8

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()
