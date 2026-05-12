import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((1000, 400))
pygame.display.set_caption("Warsztat Alchemika - Zamiana Kolorów")

# ============================================================
# 1. USTAWIENIA
# ============================================================
# Wpisz tutaj nazwę pliku, który chcesz badać i naprawiać
PLIK_ZRODLOWY = "DZ_INFO_S32_ZIEL.png" 

# Tutaj wpisujesz kolory zebrane pipetą: (STARY KWASOWY) : (NOWY ŁADNY)
COLOR_MAP = {
    # Przykłady (musisz wpisać dokładne RGB z pipety!):
    #57 linijka
    #dolna obramówka 
(255, 96, 73, 255):(255, 255, 255, 255),
(0, 16, 91, 255):(231, 219, 199, 255),

(105, 136, 97, 255):(190, 199, 166, 255),

(188, 184, 105, 255):(101, 97, 81, 255),

(10, 0, 0, 255):(158, 174, 195, 255),
(12, 18, 28, 255):(178, 182, 150, 255),

(43, 228, 255, 255):(138, 142, 125, 255),

(140, 104, 0, 255):(247, 247, 227, 255),

(159, 115, 72, 255):(77, 81, 60, 255),
(255, 255, 255, 255):(215, 211, 195, 255),

(155, 144, 160, 255):(113, 138, 146, 255),

(43, 31, 0, 255):(190, 211, 231, 255),

(233, 207, 163, 255):(105, 138, 146, 255),

    # 39 linijka
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