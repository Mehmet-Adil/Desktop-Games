import pygame
import Settings


class SafeZone:
    def __init__(self, pos):
        self.pos = pos

        self.image = pygame.image.load(r"Graphics\Safe Zones.png").convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (Settings.ICON_WIDTH, Settings.ICON_HEIGHT))

        self.rect = self.image.get_rect(topleft=self.pos)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
