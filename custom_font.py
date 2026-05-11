import pygame
import os

class BitmapFont:
    def __init__(self, folder_path):
        self.chars = {}
        self.folder_path = folder_path
        
        # Mapowanie: klucz to znak, wartość to numer pliku
        # Duże litery A-Z (33-58)
        for i in range(33, 59):
            char = chr(65 + (i - 33)) # 65 to 'A' w ASCII
            self.chars[char] = f"RED_S32_{i}.png"
            
        # Małe litery a-z (59-90)
        for i in range(59, 91):
            char = chr(97 + (i - 59)) # 97 to 'a' w ASCII
            self.chars[char] = f"RED_S32_{i}.png"

        # Dodatkowe znaki (możesz dopisać więcej, jeśli odkryjesz numery)
        self.chars[" "] = None # Spacja - obsłużona logiką odstępu

        self.chars["ł"] = "RED_S32_114.png"
        self.chars["ą"] = "RED_S32_102.png"
        self.chars["ć"] = "RED_S32_109.png"
        self.chars["ę"] = "RED_S32_113.png"

        # Słownik na załadowane obrazki (cache)
        self.images = {}
        self._load_images()

    def _load_images(self):
        for char, filename in self.chars.items():
            if filename:
                path = os.path.join(self.folder_path, filename)
                if os.path.exists(path):
                    # Ładujemy i od razu możemy podbić kolor na biały/złoty jeśli trzeba
                    img = pygame.image.load(path).convert_alpha()
                    self.images[char] = img

    def render(self, screen, text, x, y, spacing=2):
        current_x = x
        for char in text:
            if char == " ":
                current_x += 10 # Szerokość spacji
                continue
                
            if char in self.images:
                img = self.images[char]
                screen.blit(img, (current_x, y))
                current_x += img.get_width() + spacing
            else:
                # Jeśli znaku nie ma, przesuń o stałą wartość, żeby nie było dziury
                current_x += 8