import pygame
from random import randint

messages = []


class DamageIndicator:
    def __init__(self, pos, font, text, color, anti_aliasing, rotation, alive_duration):
        if font:
            self.font = font
        else:
            self.font = pygame.font.Font(None, 15)

        self.text = text
        self.color = color
        self.pos = pos

        if rotation == -1:
            self.rotation = randint(-45, 45)
        else:
            self.rotation = rotation

        self.anti_aliasing = anti_aliasing

        self.image = self.font.render(self.text, self.anti_aliasing, self.color)
        self.image = pygame.transform.rotate(self.image, self.rotation)
        self.rect = self.image.get_rect(center=self.pos)

        self.alive_duration = alive_duration
        self.alive_since = 0

    def check_death(self):
        if self.alive_since >= self.alive_duration:
            messages.remove(self)

            return True

    def update(self, fps, display):
        if self.alive_since >= self.alive_duration / 2:
            if self.check_death():
                return

            # 255 <- Max Alpha
            # (1 - (self.alive_since - self.alive_duration / 2) / (self.alive_duration / 2)) Finds fraction, e.g. 0.5
            alpha = 255 * (1 - (self.alive_since - self.alive_duration / 2) / (self.alive_duration / 2))
            self.image.set_alpha(alpha)

        self.alive_since += 1 / fps

        self.draw(display)

    def draw(self, display):
        display.blit(self.image, self.rect)
