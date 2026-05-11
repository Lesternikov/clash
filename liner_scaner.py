import pygame
import sys

# ============================================================
# USTAWIENIA - Wpisz plik, który chcesz badać
# ============================================================
PLIK_ZRODLOWY = "r.png"

def main():
    pygame.init()
    
    # 1. Najpierw ładujemy "surowy" obrazek (bez konwersji)
    try:
        surowy_img = pygame.image.load(PLIK_ZRODLOWY)
    except Exception as e:
        print(f"Nie udało się załadować {PLIK_ZRODLOWY}: {e}")
        return

    # 2. Obliczamy wymiary i DOPIERO TERAZ tworzymy okno gry
    skala = 2
    okno_szer = max(500, surowy_img.get_width() * skala + 50)
    okno_wys = max(300, surowy_img.get_height() * skala + 50)
    screen = pygame.display.set_mode((okno_szer, okno_wys))
    pygame.display.set_caption("Skaner Kolorów (Kliknij w obrazek)")

    # 3. Kiedy okno już istnieje, możemy bezpiecznie przekonwertować obrazek
    img = surowy_img.convert_alpha()
    img_scaled = pygame.transform.scale(img, (img.get_width() * skala, img.get_height() * skala))
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Lewy przycisk myszy
                    mx, my = pygame.mouse.get_pos()
                    
                    if mx < img_scaled.get_width() and my < img_scaled.get_height():
                        oryginalny_y = my // skala
                        
                        kolory_w_linii = set()
                        for x in range(img.get_width()):
                            kolory_w_linii.add(tuple(img.get_at((x, oryginalny_y))))
                        
                        print("\n" + "="*50)
                        print(f"SKANOWANIE LINII Y: {oryginalny_y}")
                        print(f"Znaleziono {len(kolory_w_linii)} unikalnych kolorów w tym rzędzie:")
                        print("-" * 50)
                        for kolor in kolory_w_linii:
                            print(kolor)
                        print("="*50)

        screen.fill((40, 40, 45))
        screen.blit(img_scaled, (0, 0))
        
        mx, my = pygame.mouse.get_pos()
        if mx < img_scaled.get_width() and my < img_scaled.get_height():
            pygame.draw.line(screen, (255, 0, 0), (0, my), (img_scaled.get_width(), my), 1)
            
            font = pygame.font.SysFont("Arial", 16, bold=True)
            txt = font.render(f"Oryginalny wiersz: {my // skala}", True, (255, 255, 0))
            screen.blit(txt, (mx + 15, my - 10))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()