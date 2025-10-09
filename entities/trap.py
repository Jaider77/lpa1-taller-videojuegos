import pygame # pyright: ignore[reportMissingImports]
from core import settings

class Trap(pygame.sprite.Sprite):
    def __init__(self, x, y, damage=30, radius=50):
        super().__init__()
        self.image = pygame.image.load("assets/trap.png").convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))
        self.damage = damage
        self.radius = radius

    def explode(self, group_enemies):
        """Explosión que afecta a enemigos dentro del radio"""
        hits = [enemy for enemy in group_enemies if self.rect.centerx - self.radius < enemy.rect.centerx < self.rect.centerx + self.radius]
        for enemy in hits:
            enemy.hp -= self.damage
            if enemy.hp <= 0:
                enemy.kill()
        self.kill()
