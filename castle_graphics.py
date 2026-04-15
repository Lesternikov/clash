import pygame

class CastleGraphics:
    def __init__(self, assets_path="."):
        # 1. Tutaj ładujemy tło (tylko raz na starcie gry!)
        try:
            raw_bg = pygame.image.load(f"{assets_path}/Z_01_GFX.png").convert()
            self.bg = pygame.transform.scale(raw_bg, (1024, 768))
        except pygame.error:
            print("Błąd ładowania tła zamku.")
            self.bg = pygame.Surface((1024, 768))
            self.bg.fill((50, 50, 50))

        # 2. Tu w przyszłości załadujemy przezroczyste budynki
        # self.b_koszary = pygame.image.load(f"{assets_path}/b_koszary.png").convert_alpha()
        # self.b_kuznia = pygame.image.load(...)

    def draw_background(self, screen):
        """Tylko rysuje tło."""
        screen.blit(self.bg, (0, 0))

    def draw_buildings(self, screen, current_castle):
        """Sprawdza co zamek ma zbudowane i rysuje odpowiednie grafiki."""
        if not current_castle:
            return

        # Przykład na przyszłość:
        # if "Koszary" in current_castle.buildings:
        #     screen.blit(self.b_koszary, (400, 300))