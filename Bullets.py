import pygame
from math import cos, sin, radians, sqrt

import Settings

bullets = []


class CannonBall:
    def __init__(self, pos, angle, power):
        self.image = pygame.image.load("Graphics/Towers/Cannon/CannonBall.png").convert_alpha()
        self.default_size = self.image.get_size()

        self.image = pygame.transform.rotozoom(self.image, angle, 1)
        self.rect = self.image.get_rect(center=pos)

        self.angle = angle
        self.angle_clockwise_radians = radians(360 - angle)

        self.direction = pygame.Vector2(sin(self.angle_clockwise_radians), -cos(self.angle_clockwise_radians))

        self.power = power
        self.pos = pygame.Vector2(pos)

        self.speed = 30

    def is_out_of_screen(self):
        max_x, max_y = Settings.SCREEN_SIZE

        if self.rect.right <= 0:
            bullets.remove(self)
        elif self.rect.bottom <= 0:
            bullets.remove(self)
        elif self.rect.left >= max_x:
            bullets.remove(self)
        elif self.rect.top >= max_y:
            bullets.remove(self)

    def move(self):
        dist_magnitude = sqrt(abs(self.direction[0])**2 + abs(self.direction[1])**2)
        self.pos += (self.direction[0] / dist_magnitude * self.speed, self.direction[1] / dist_magnitude * self.speed)
        self.rect.center = self.pos

    def update(self, display):
        self.move()
        self.draw(display)
        self.is_out_of_screen()

    def draw(self, display):
        display.blit(self.image, self.rect)
