import pygame
from os import listdir, path
from typing import Union


def load_animations(folder_path: str) -> tuple:
    animation = listdir(folder_path)
    animation = tuple(pygame.image.load(path.join(folder_path, frame)).convert_alpha() for frame in animation)

    return animation


class Animation:
    def __init__(self, animation_folder: str, speed: float, pos: Union[tuple, pygame.math.Vector2],
                 loop: bool = False, fps: int = 60, resize: float = 1):
        self.FPS = fps
        self.animation = tuple(pygame.transform.rotozoom(frame, 0, resize) for frame in load_animations(animation_folder))

        self.speed = speed

        self.current_frame = 0

        self.image = None
        self.rect = None

        self.pos = pos

        self.loop = loop

    def get_frame(self) -> Union[pygame.Surface, None]:
        self.current_frame += self.speed * 10 / self.FPS

        if self.current_frame >= len(self.animation):
            if not self.loop:
                return

            self.current_frame = 0

        return self.animation[int(self.current_frame)]

    def play(self, screen: pygame.Surface):
        self.image = self.get_frame()

        if not self.image:
            return

        self.rect = self.image.get_rect(center=self.pos)

        screen.blit(self.image, self.rect)
