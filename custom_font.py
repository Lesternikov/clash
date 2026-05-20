import pygame
import os

class BitmapFont:
    def __init__(self, folder_path):
        self.chars = {}
        self.folder_path = folder_path
        
        # Duże litery A-Z (33-58)
        for i in range(33, 59):
            char = chr(65 + (i - 33)) 
            self.chars[char] = f"RED_S32_{i}.png"
            
        # Małe litery a-z (59-90)
        for i in range(59, 91):
            char = chr(97 + (i - 59)) 
            self.chars[char] = f"RED_S32_{i}.png"

        self.chars[" "] = None

        # Polskie znaki (dopisz resztę jeśli znajdziesz)
        self.chars["ł"] = "RED_S32_114.png"
        self.chars["ą"] = "RED_S32_102.png"
        self.chars["ć"] = "RED_S32_109.png"
        self.chars["ę"] = "RED_S32_113.png"

        # Tu trzymamy surowe obrazki
        self.raw_images = {}
        
        # Tu trzymamy gotowe, pokolorowane zestawy liter (np. 'gold', 'red', 'blue')
        self.palettes = {} 
        
        self._load_raw_images()

    def _load_raw_images(self):
        """Ładuje oryginały. Jeśli ich nie ma, wypisuje błąd w konsoli."""
        for char, filename in self.chars.items():
            if filename:
                path = os.path.join(self.folder_path, filename)
                if os.path.exists(path):
                    self.raw_images[char] = pygame.image.load(path).convert_alpha()
                else:
                    print(f"OSTRZEŻENIE: Brak pliku {path}")

    def add_palette(self, palette_name, color_map):
        """Tworzy nowy zestaw liter na podstawie Twojego COLOR_MAP."""
        self.palettes[palette_name] = {}
        for char, img in self.raw_images.items():
            colored_img = img.copy()
            # Podmiana kolorów
            for x in range(colored_img.get_width()):
                for y in range(colored_img.get_height()):
                    pixel = tuple(colored_img.get_at((x, y)))
                    if pixel in color_map:
                        colored_img.set_at((x, y), color_map[pixel])
            self.palettes[palette_name][char] = colored_img

    def render(self, screen, text, x, y, spacing=1, palette_name=None):
        # Jeśli nie podasz palety, weź pierwszą dostępną
        if palette_name is None and self.palettes:
            palette_name = list(self.palettes.keys())[0]
        
        if palette_name not in self.palettes:
            return # Nie rysuj nic, jeśli nie ma palet

        active_set = self.palettes[palette_name]
        curr_x = x
        for char in text:
            if char == " ":
                curr_x += 10
                continue
            if char in active_set:
                screen.blit(active_set[char], (curr_x, y))
                curr_x += active_set[char].get_width() + spacing
            else:
                curr_x += 8

                
                
                koniec
                koniec

                koniec

                koniec

                koniec

                koniec

                koniec

                koniec















                koniec


                koniec

                koniec

                koniec


                koniec

                koniec

                koniec
                koniec
                koniec
                koniec
                koniec
                koniec

