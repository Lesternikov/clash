import pygame
import os

# =================================================================
# 1. ORYGINALNE "MAGICZNE" KOLORY Z SZABLONU (Musisz je sprawdzić pipetą)
# =================================================================
# Przykładowe wartości z oryginalnej grafiki (zmień na właściwe RGB)
MASK_BASE = (85, 85, 255, 255)     # Główny kolor (np. ten niebieski ze środka strzałki)
MASK_LIGHT = (255, 255, 85, 255)   # Jasny kolor (np. żółty odblask)
MASK_SHADOW = (0, 170, 0, 255)     # Ciemny kolor (np. zielony cień)

# =================================================================
# 2. DEFINICJE KOLORÓW DLA GRACZY
# =================================================================
PLAYER_PALETTES = {
    "RED": {
        MASK_BASE: (200, 0, 0, 255),       # Środek czerwony
        MASK_LIGHT: (255, 100, 100, 255),  # Jasny czerwony odblask
        MASK_SHADOW: (100, 0, 0, 255)      # Ciemny czerwony cień
    },
    "BLUE": {
        MASK_BASE: (0, 0, 200, 255),
        MASK_LIGHT: (100, 100, 255, 255),
        MASK_SHADOW: (0, 0, 100, 255)
    },
    "GREEN": {
        MASK_BASE: (0, 180, 0, 255),
        MASK_LIGHT: (100, 255, 100, 255),
        MASK_SHADOW: (0, 80, 0, 255)
    }
    # Tutaj możesz dodać kolejnych graczy ("YELLOW", "BLACK", itp.)
}

# =================================================================
# 3. GŁÓWNA KLASA ZARZĄDZAJĄCA KOLORAMI (I PAMIĘCIĄ RAM)
# =================================================================
class ColorManager:
    def __init__(self):
        # Słownik, w którym przechowujemy raz pokolorowane grafiki (żeby nie liczyć ich 100x na sekundę)
        self.cached_images = {}

    def get_colored_image(self, image_path, color_name):
        """Pobiera i koloruje obrazek z dysku dla danego gracza, a potem go zapamiętuje."""
        
        # Unikalny klucz do pamięci np. "assets/strzalka.png_RED"
        cache_key = f"{image_path}_{color_name}"
        
        # 1. ZWROT Z PAMIĘCI (Jeśli już to kiedyś zrobiliśmy - najszybsza opcja)
        if cache_key in self.cached_images:
            return self.cached_images[cache_key]

        # 2. ŁADOWANIE ORYGINAŁU (Jeśli to pierwszy raz)
        try:
            original_img = pygame.image.load(image_path).convert_alpha()
        except Exception as e:
            print(f"[ColorManager] Błąd ładowania obrazka {image_path}: {e}")
            return None

        # 3. ZABEZPIECZENIE (Jeśli nie mamy takiego koloru gracza w bazie, oddaj oryginał)
        if color_name not in PLAYER_PALETTES:
            return original_img

        # 4. PROCES KOLOROWANIA PIKSEL PO PIKSELU
        new_img = original_img.copy()
        palette = PLAYER_PALETTES[color_name]
        
        # Blokujemy obrazek na chwilę do edycji
        pixels = pygame.PixelArray(new_img)
        for old_color, new_color in palette.items():
            try:
                # Zamiana starych pikseli na nowe
                old_c = new_img.map_rgb(old_color)
                new_c = new_img.map_rgb(new_color)
                pixels.replace(old_c, new_c)
            except ValueError:
                pass # Ignorujemy, jeśli dany kolor nie występuje na tym obrazku
        
        # Odblokowujemy obrazek
        pixels.close()

        # Opcjonalnie: ustawienie przezroczystości dla beżowego tła z oryginału
        # Zmień te wartości RGB na dokładny kolor tła (z pipety)!
        # new_img.set_colorkey((230, 208, 176)) 

        # 5. ZAPIS DO PAMIĘCI I ZWROT GOTOWEJ GRAFIKI
        self.cached_images[cache_key] = new_img
        return new_img