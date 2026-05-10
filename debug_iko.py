import pygame
import sys
import os

# Konfiguracja okna
SCREEN_W, SCREEN_H = 1024, 768
pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("CELOWNIK WSPÓŁRZĘDNYCH - Z_IKO_PCX.png")

# Ładowanie obrazka
img_path = os.path.join("assets", "Z_IKO_PCX.png")
if not os.path.exists(img_path):
    print(f"BŁĄD: Nie znaleziono pliku {img_path}")
    sys.exit()

sheet = pygame.image.load(img_path).convert_alpha()
font = pygame.font.SysFont("Arial", 16, bold=True)

# =================================================================
# TUTAJ ZMIENIAJ LICZBY (X, Y, Szerokość, Wysokość)
# =================================================================

RECTS_TO_TEST = {
    # 1. BANERY MENU (Po prawej stronie, pionowo)
    "MENU_FRAME_1": (508, 1, 129, 69),   # Pierwszy od góry
    "MENU_FRAME_2": (508, 72, 129, 69), # Drugi od góry
    "MENU_FRAME_3": (508, 143, 129, 69), # Trzeci
    "MENU_FRAME_4": (508, 215, 129, 69), # Trzeci
    "MENU_FRAME_5": (508, 287, 129, 69), # Trzeci
    "MENU_FRAME_6": (508, 359, 129, 69), # Trzeci
    
    # 2. PRZYCISKI BACK (Dół, lewa strona)
    "BACK_NORMAL":  (7, 430, 80, 48),    # Pierwszy od lewej na dole
    "BACK_PRESSED": (89, 430, 80, 48),  # Drugi od lewej na dole
    
    # 3. PASEK NAZWY BUDYNKU (Dół, środek)
    "TITLE_BAR":    (180, 446, 285, 32),
    
    # 4. FLAGI (Dół, prawa strona)
    "FLAGS_AREA":   (466, 441, 50, 36),
}
# =================================================================

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    # 1. Czyścimy i rysujemy cały arkusz
    screen.fill((50, 50, 50)) # Ciemne tło, żeby widzieć krawędzie arkusza
    screen.blit(sheet, (0, 0))
    
    # 2. Rysujemy czerwone ramki testowe
    for name, coords in RECTS_TO_TEST.items():
        rect = pygame.Rect(coords)
        
        # Ramka
        pygame.draw.rect(screen, (255, 0, 0), rect, 2)
        
        # Podpis z nazwą i współrzędnymi nad ramką
        label = font.render(f"{name}: {coords}", True, (255, 0, 0))
        # Czarny pasek pod tekstem dla czytelności
        pygame.draw.rect(screen, (0,0,0), (rect.x, rect.y - 20, label.get_width(), 18))
        screen.blit(label, (rect.x, rect.y - 20))

    pygame.display.flip()

pygame.quit()