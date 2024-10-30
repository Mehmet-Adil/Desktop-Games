import pygame

ui_elements = []


def put_text(surface: pygame.Surface, text_font: pygame.font.Font, pos: tuple = (0, 0),
             text: str = "Default", color: tuple = (0, 0, 0), text_aa: bool = True, alignment: str = "center"):
    """
    This puts text on the screen.
    """
    if not text_font:
        # If there is no font make a default one
        text_font = pygame.font.Font(None, 40)

    text_surf = text_font.render(text, text_aa, color)
    text_rect = text_surf.get_rect(**{alignment: pos})

    surface.blit(text_surf, text_rect)


class Bar:
    def __init__(self, pos: tuple, fill_color: tuple = (255, 0, 0), max_value: int = 100, fill_value: int = 0,
                 scale_factor: float = 1, rotation: float = 0, group: iter = (), owner="UNKNOWN"):
        self.pos = pos

        self.max_value = max_value
        self.fill_value = fill_value

        self.fill_color = fill_color

        self.scale_factor = scale_factor

        self.frame_image = pygame.image.load("Graphics/Bar/Bar Frame.png").convert_alpha()
        self.frame_image = pygame.transform.rotozoom(self.frame_image, 0, self.scale_factor)
        self.frame_width, self.frame_height = self.frame_image.get_size()

        self.image = None
        self.rect = None

        self.rotation = rotation

        self.group = group
        self.owner = owner

    def check_owner(self):
        if self.owner not in self.group:
            ui_elements.remove(self)

    def draw(self, display: pygame.Surface):
        self.check_owner()

        # Fill of the bar
        fill_area = (self.frame_width * (self.fill_value / self.max_value), self.frame_height)
        fill_surf = pygame.Surface(fill_area)
        fill_surf.fill(self.fill_color)

        # Make the image
        image = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
        image.blit(fill_surf, (0, 0))
        image.blit(self.frame_image, (0, 0))

        self.image = pygame.transform.rotate(image, self.rotation)
        self.rect = self.image.get_rect(center=self.pos)

        display.blit(self.image, self.rect)
