import pygame
import sys

# ============================================================
# USTAWIENIA - Wpisz nazwy swoich plików
# ============================================================
PLIK_ZRODLO = "STAT_S32_27.png"   # np. "STAT_S32_17.png" (ten kwasowy)
PLIK_CEL = "QUEEN_S32_3.png"       # np. "STAT_S32_46.png" (ten ze złotym krzyżem)
PLIK_WYNIKOWY = "GOTOWA_PALETA.txt"

def main():
    pygame.init()
    
    # Tworzymy malutkie, ukryte okno, żeby Pygame nie narzekał na brak wideo
    pygame.display.set_mode((100, 100), pygame.HIDDEN)
    
    # 1. Ładowanie obrazków
    try:
        img_zrodlo = pygame.image.load(PLIK_ZRODLO).convert_alpha()
        img_cel = pygame.image.load(PLIK_CEL).convert_alpha()
    except Exception as e:
        print(f"BŁĄD: Nie udało się załadować obrazków. Szczegóły: {e}")
        pygame.quit()
        return

    # Zabezpieczenie: Sprawdzamy czy obrazki mają te same wymiary
    if img_zrodlo.get_size() != img_cel.get_size():
        print(f"BŁĄD: Obrazki mają różne wymiary!")
        print(f"Źródło: {img_zrodlo.get_width()}x{img_zrodlo.get_height()}")
        print(f"Cel: {img_cel.get_width()}x{img_cel.get_height()}")
        print("Muszą być identyczne, żeby można było połączyć piksele 1 do 1.")
        pygame.quit()
        return

    szerokosc = img_zrodlo.get_width()
    wysokosc = img_zrodlo.get_height()
    
    print("=" * 50)
    print("KOMPLEKSOWY GENERATOR PALETY (PRO)")
    print("=" * 50)
    print(f"Skanuję obrazki: {szerokosc} x {wysokosc} pikseli...")

    paleta = {}
    konflikty = 0

    # 2. Błyskawiczne skanowanie piksel po pikselu
    for x in range(szerokosc):
        for y in range(wysokosc):
            piksel_zrodlo = tuple(img_zrodlo.get_at((x, y)))
            piksel_cel = tuple(img_cel.get_at((x, y)))
            
            # Zapisujemy do słownika
            if piksel_zrodlo not in paleta:
                paleta[piksel_zrodlo] = piksel_cel
            else:
                # Jeśli stary kolor z jakiegoś powodu próbuje zamienić się w inny kolor niż wcześniej
                if paleta[piksel_zrodlo] != piksel_cel:
                    konflikty += 1

    # 3. FILTROWANIE: Wyrzucamy kolory, które się nie zmieniły (np. przezroczyste tło)
    # Zmniejszy to objętość słownika o 90%!
    czysta_paleta = {zrodlo: cel for zrodlo, cel in paleta.items() if zrodlo != cel}

    # 4. Zapis gotowego kodu do pliku
    with open(PLIK_WYNIKOWY, 'w', encoding='utf-8') as f:
        for zrodlo, cel in czysta_paleta.items():
            f.write(f"{zrodlo}: {cel},\n")

    print("-" * 50)
    print(f"Zakończono! W obrazku było {len(paleta)} unikalnych kolorów.")
    print(f"Po usunięciu niezmienionego tła, Twoja paleta ma tylko {len(czysta_paleta)} wpisów!")
    if konflikty > 0:
        print(f"UWAGA: Wykryto {konflikty} konfliktów (ten sam stary kolor próbował przyjąć różne wartości).")
        print("Program zapisał pierwsze wykryte dopasowanie.")
    print("-" * 50)
    print(f"GOTOWE! Otwórz plik: {PLIK_WYNIKOWY} i skopiuj jego zawartość.")
    print("=" * 50)

    pygame.quit()

if __name__ == "__main__":
    main()