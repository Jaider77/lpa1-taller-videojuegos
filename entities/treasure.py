import pygame # pyright: ignore[reportMissingImports]
from core import settings

class Treasure(pygame.sprite.Sprite):
    def __init__(self, x, y, value=100):
        super().__init__()
        self.image = pygame.image.load("assets/treasure.png").convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))
        self.value = value  # valor monetario o puntaje

    def update(self):
        """El tesoro cae lentamente en el espacio"""
        self.rect.y += 2
        if self.rect.top > settings.HEIGHT:
            self.kill()
