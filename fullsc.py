import pygame
import sys

# ============================================================
# USTAWIENIA 
# ============================================================
PLIK_ZRODLOWY = "STAT_S32_24.png"
PLIK_WYNIKOWY = "CEL.txt"

def main():
    pygame.init()
    #--- DODAJ TĘ LINIJKĘ ---
    # Tworzymy malutkie, ukryte okno, żeby Pygame mógł użyć .convert_alpha()
    pygame.display.set_mode((100, 100), pygame.HIDDEN)
    # 1. Ładowanie obrazka
    try:
        img = pygame.image.load(PLIK_ZRODLOWY).convert_alpha()
    except Exception as e:
        print(f"Nie udało się załadować {PLIK_ZRODLOWY}: {e}")
        return

    szerokosc = img.get_width()
    wysokosc = img.get_height()
    wszystkie_piksele = szerokosc * wysokosc

    print("=" * 50)
    print("HARDKOROWY SKANER CAŁEGO OBRAZKA")
    print("=" * 50)
    print(f"Obrazek: {PLIK_ZRODLOWY}")
    print(f"Wymiary: {szerokosc} x {wysokosc}")
    print(f"Do przeskanowania: {wszystkie_piksele} pikseli!")
    print(f"Pracuję... Zapisuję do pliku {PLIK_WYNIKOWY}...")

    # 2. Otwieramy plik tekstowy do zapisu
    with open(PLIK_WYNIKOWY, "w", encoding="utf-8") as plik:
        plik.write(f"RAPORT Z OBRAZKA: {PLIK_ZRODLOWY}\n")
        plik.write("-" * 40 + "\n")
        
        # 3. Pętla przez każdy wiersz (Y), a w nim przez każdą kolumnę (X)
        for y in range(wysokosc):
            # Opcjonalnie: Zapisujemy nagłówek dla każdej nowej linii Y, żeby łatwiej było czytać plik
            plik.write(f"\n--- LINIA Y: {y} ---\n")
            
            for x in range(szerokosc):
                piksel = tuple(img.get_at((x, y)))
                # Zapisujemy w formacie przyjaznym dla Twojego generatora palety!
                plik.write(f"Piksel {x}: \t\t{piksel}\n")

    print("-" * 50)
    print(f"GOTOWE! Pomyślnie wygenerowano plik: {PLIK_WYNIKOWY}")
    print("Możesz go teraz otworzyć w Notatniku.")
    print("-" * 50)
    
    pygame.quit()

if __name__ == "__main__":
    main()