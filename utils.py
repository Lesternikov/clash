import pygame

def draw_text(screen, text, x, y, color=(0, 0, 0)):
    font = pygame.font.SysFont(None, 24)
    img = font.render(str(text), True, color)
    screen.blit(img, (x, y))

        # Uniwersalny alias - wskazuje na właściwy w zależności od ekranu