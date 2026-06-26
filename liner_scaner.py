import pygame
import sys
#sprawdza jedną linijkę w grafice
# ============================================================
# USTAWIENIA - Wpisz plik, który chcesz badać
# ============================================================
PLIK_ZRODLOWY = "STAT_S32_17.png"

def main():
    pygame.init()
    
    # 1. Ładowanie obrazka
    try:
        surowy_img = pygame.image.load(PLIK_ZRODLOWY)
    except Exception as e:
        print(f"Nie udało się załadować {PLIK_ZRODLOWY}: {e}")
        return

    # 2. Tworzenie okna
    skala = 3 # Zwiększyłem skalę dla lepszej widoczności małych ikon
    okno_szer = max(500, surowy_img.get_width() * skala + 50)
    okno_wys = max(300, surowy_img.get_height() * skala + 50)
    screen = pygame.display.set_mode((okno_szer, okno_wys))
    pygame.display.set_caption("Skaner Kolorów (Piksel po pikselu)")

    # Konwertujemy z kanałem Alpha
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
                        
                        print("\n" + "="*50)
                        print(f"SKANOWANIE LINII Y: {oryginalny_y}")
                        print("-" * 50)
                        
                        # --- PROSTA LOGIKA: WYPISZ KAŻDY PIKSEL ---
                        for x in range(img.get_width()):
                            piksel = tuple(img.get_at((x, oryginalny_y)))
                            # Format idealnie dopasowany pod Twój generator palety
                            print(f"Piksel {x}: \t\t{piksel}")
                            
                        print("="*50)

        screen.fill((40, 40, 45))
        screen.blit(img_scaled, (0, 0))
        
        mx, my = pygame.mouse.get_pos()
        if mx < img_scaled.get_width() and my < img_scaled.get_height():
            pygame.draw.line(screen, (255, 0, 0), (0, my), (img_scaled.get_width(), my), 1)
            
            font = pygame.font.SysFont("Arial", 16, bold=True)
            txt = font.render(f"Wiersz Y: {my // skala}", True, (255, 255, 0))
            screen.blit(txt, (mx + 15, my - 10))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()