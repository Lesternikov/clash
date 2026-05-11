import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((1000, 400))
pygame.display.set_caption("Warsztat Alchemika - Zamiana Kolorów")

# ============================================================
# 1. USTAWIENIA
# ============================================================
# Wpisz tutaj nazwę pliku, który chcesz badać i naprawiać
PLIK_ZRODLOWY = "r1.png" 

# Tutaj wpisujesz kolory zebrane pipetą: (STARY KWASOWY) : (NOWY ŁADNY)
COLOR_MAP = {
(255, 255, 255, 255):(0, 0, 0, 255),
(10, 0, 0, 255):(36, 24, 16, 255),
(33, 17, 0, 255):(215, 203, 158, 255),#
(16, 48, 0, 255):(24, 16, 12, 255),
(66, 57, 0, 255):(16, 8, 0, 255),
(0, 0, 0, 255):(69, 56, 48, 255),
(18, 9, 0, 255):(255, 243, 199, 255),
(43, 31, 0, 255):(154, 142, 105, 255),
(26, 57, 0, 255):(255, 243, 199, 255),
(69, 56, 48, 255):(89, 65, 69, 255),
(66, 57, 0, 255):(101, 85, 56, 255)
}



def main():
    try:
        img = pygame.image.load(PLIK_ZRODLOWY).convert_alpha()
    except Exception as e:
        print(f"Nie udało się załadować {PLIK_ZRODLOWY}: {e}")
        return

    # ============================================================
    # 2. LICZENIE UNIKALNYCH KOLORÓW (Komputerowy detektyw)
    # ============================================================
    unique_colors = set()
    for x in range(img.get_width()):
        for y in range(img.get_height()):
            unique_colors.add(tuple(img.get_at((x, y))))
            
    print("-" * 50)
    print(f"ANALIZA PLIKU: {PLIK_ZRODLOWY}")
    print(f"Komputer znalazł dokładnie: {len(unique_colors)} unikalnych kolorów!")
    print("-" * 50)
    # Jeśli chcesz, odkomentuj poniższą linię, żeby zobaczyć listę wszystkich znalezionych RGB:
    # print("Znalezione kolory:", unique_colors)

    # ============================================================
    # 3. PODMIANA KOLORÓW
    # ============================================================
    new_img = img.copy()
    pixels = pygame.PixelArray(new_img)

    for old_color, new_color in COLOR_MAP.items():
        try:
            old_c = new_img.map_rgb(old_color)
            new_c = new_img.map_rgb(new_color)
            pixels.replace(old_c, new_c)
        except ValueError:
            pass # Kolor nie występuje na obrazku, ignorujemy
            
    pixels.close()

    # Zapisujemy wynik do pliku, żebyś mógł go obejrzeć z bliska
    plik_wynikowy = "NAPRAWIONY_" + PLIK_ZRODLOWY
    pygame.image.save(new_img, plik_wynikowy)
    print(f"Zapisano gotowy plik jako: {plik_wynikowy}")

    # ============================================================
    # 4. WYŚWIETLENIE PODGLĄDU NA EKRANIE
    # ============================================================
    font = pygame.font.SysFont("Arial", 24)
    txt_old = font.render("ORYGINAŁ (Kwasowy)", True, (255, 255, 255))
    txt_new = font.render("PO NAPRAWIE (COLOR_MAP)", True, (255, 255, 255))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill((40, 40, 45))
        
        # Rysujemy oryginał (po lewej)
        screen.blit(txt_old, (50, 50))
        screen.blit(img, (50, 100))
        
        # Rysujemy naprawiony (po prawej)
        przesuniecie_x = 50 + img.get_width() + 50
        screen.blit(txt_new, (przesuniecie_x, 50))
        screen.blit(new_img, (przesuniecie_x, 100))
        
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()