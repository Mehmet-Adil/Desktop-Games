import pygame
import Settings
from UI import put_text
pygame.init()

money = 600
MONEY_FONT = pygame.font.Font("Fonts/Anton-Regular.ttf", round(Settings.ICON_WIDTH // 4))


def update_money_text():
    box_rect = pygame.Rect(Settings.SCREEN_SIZE[0] - Settings.ICON_WIDTH * 4 - Settings.ICON_LEFT_GAP * 2, Settings.ICON_TOP_GAP * 2,
                           Settings.ICON_WIDTH * 4, round(Settings.ICON_HEIGHT*0.75))
    text_pos = (Settings.SCREEN_SIZE[0] - Settings.ICON_WIDTH * 4, Settings.ICON_TOP_GAP * 2 + round(Settings.ICON_HEIGHT*0.75)//2)

    pygame.draw.rect(Settings.SCREEN, "WHITE", rect=box_rect)
    put_text(Settings.SCREEN, MONEY_FONT, text_pos, f"Money: {money}$", "GOLD", True, "midleft")
