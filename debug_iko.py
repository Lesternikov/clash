import pygame
import sys
import os

# Konfiguracja okna
SCREEN_W, SCREEN_H = 1024, 768
pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("CELOWNIK WSPÓŁRZĘDNYCH - Z_IKO_PCX.png")

# Ładowanie obrazka
img_path = os.path.join("DWOR.png")
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
    "KROLOWA1": (1, 135, 95, 133),   # Pierwszy od góry
    "KROLOWA2": (99, 135, 95, 133), # Drugi od góry
    "KROLOWA3": (187, 135, 95, 133), # Trzeci
    "KROLOWA4": (283, 135, 95, 133),
    "KROLOWA5": (378, 135, 95, 133), # Trzeci
    "KROLOWA6": (470, 135, 95, 133), # Trzeci
    "KROLOWA7": (561, 135, 95, 133),
    "KROLOWA8": (654, 135, 95, 133),
    "KROLOWA9": (748, 135, 95, 133),  
    "CZERWONYK": (144, 44, 42, 22),  # Drugi od lewej na dole
    "CZERWONYP": (145, 76, 42, 22),
    "CZERWONYW": (11, 34, 20, 10),
    "NIEBIESKIK": (67, 36, 42, 22),
    "NIEBIESKIP": (272, 41, 42, 22),
    "NIEBIESKIW": (13, 14, 20, 10),
    "ŻÓŁTYK": (415, 40, 42, 22),
    "ŻÓŁTYP": (146, 10, 42, 22),
    "ŻÓŁTYW": (41, 22, 20, 10),
    "ZIELONYK": (77, 86, 42, 22),
    "ZIELONYP": (211, 36, 42, 22),
    "ZIELONYW": (496, 381, 20, 10),
    "BIAŁYK": (355, 45, 42, 22),
    "BIAŁYP": (211, 74, 42, 22),
    "BIAŁYW": (78, 12, 20, 10),
    "CZERWONY_PASEK": (552, 23, 120, 11),
    "NIEBIESKI_PASEK": (552, 36, 120, 11),
    "ŻÓŁTY_PASEK": (552, 49, 120, 11),
    "BIAŁY_PASEK": (552, 62, 120, 11),
    "ZIELONY_PASEK":(552, 75, 120, 11),

    
    
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