import pygame
import sys
import os

# Konfiguracja okna
SCREEN_W, SCREEN_H = 1024, 768
pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("CELOWNIK WSPÓŁRZĘDNYCH - Z_IKO_PCX.png")

# Ładowanie obrazka
img_path = os.path.join("assets","minimum","STAT_S32", "STAT_S32_41.png")
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
    "BACK_1": (6, 55, 76, 43),   # Pierwszy od góry
    "BACK_2": (187, 58, 78, 44), # Drugi od góry
    "KAT_1": (28, 156, 73, 34), # Trzeci
    "KAT_2":    (328, 362, 73, 34),
    "TORTURY_1": (422, 49, 73, 34), # Trzeci
    "TORTURY_2": (328, 402, 73, 34), # Trzeci
    "KUP_1": (367, 222, 83, 34), # Trzeci
    "KUP_2":   (318, 441, 83, 34),
    "WIĘZIEŃ":  (86, 239, 55, 62),  
    "COLOR_W1": (41, 381, 20, 10),  # Drugi od lewej na dole
    "COLOR_W2": (272, 381, 20, 10),
    "COLOR_W3": (496, 381, 20, 10),
    # 3. PASEK NAZWY BUDYNKU (Dół, środek)
    
    
    # 4. FLAGI (Dół, prawa strona)
    
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