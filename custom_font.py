import pygame
import os

class BitmapFont:
    def __init__(self, folder_path):
        self.chars = {}
        self.folder_path = folder_path
        self.raw_images = {}
        self.palettes = {} 

        # --- PRECYZYJNE MAPOWANIE ---

        # Wielkie litery A-Z
        wielkie = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for i, char in enumerate(wielkie):
            self.chars[char] = f"RED_S32_{33 + i}.png"

        # Małe litery a-z ZACZYNAJĄ SIĘ OD 65
        male = "abcdefghijklmnopqrstuvwxyz"
        for i, char in enumerate(male):
            self.chars[char] = f"RED_S32_{65 + i}.png"

        # Polskie znaki (Twoja lista numerów)
        polskie = {
            "ł":"114","Ł":"124","ą":"102","Ą":"111","ć":"109","Ć":"117",
            "ę":"113","Ę":"112","ś":"126","Ś":"120","ń":"132","Ń":"133",
            "ó":"130","Ó":"131","ż":"135","Ż":"129","ź":"134","Ź":"128"
        }
        for char, num in polskie.items():
            self.chars[char] = f"RED_S32_{num}.png"

        # Interpunkcja
        self.chars["."] = "RED_S32_14.png"
        self.chars[","] = "RED_S32_12.png"
        self.chars[" "] = None

    # 1. STARE CYFRY (żółtawe, z pliku RED_S32)
        cyfrybe = "0123456789"
        for i, char in enumerate(cyfrybe):
            self.chars[f"{char}_be"] = f"RED_S32_{16 + i}.png"

        # 2. NOWE CYFRY (białe) - z pliku cyfry
        cyfry = "0123456789"
        for i, char in enumerate(cyfry):
            self.chars[char] = f"nowy{char}.png"

        self._load_raw_images()

    def _load_raw_images(self):
        for char, filename in self.chars.items():
            if filename:
                if filename.startswith("nowy"):
                    czysta_nazwa = filename.replace("nowy", "") + ".png" if not filename.endswith(".png") else filename.replace("nowy", "")
                    glowny_folder_assets = os.path.dirname(self.folder_path)
                    # Budujemy poprawną ścieżkę: assets / cyfry / 0.png
                    path = os.path.join(glowny_folder_assets, "cyfry", czysta_nazwa)
                    print(f"[DEBUG CZCIONKA] Próba załadowania nowej cyfry '{char}' ze ścieżki: {path}")
                else:
                    path = os.path.join(self.folder_path, filename)
                
                if os.path.exists(path):
                    self.raw_images[char] = pygame.image.load(path).convert_alpha()
                    if char in "0123456789":
                        print(f"[DEBUG CZCIONKA] SUKCES! Załadowano nową cyfrę '{char}'")
                else:
                    print(f"[DEBUG CZCIONKA] BŁĄD! Brak pliku pod ścieżką: {path}")

    def add_palette(self, name, color_map):
        self.palettes[name] = {}
        for char, img in self.raw_images.items():
            new_img = img.copy()
            
            # OCHRONA BIAŁYCH CYFR PRZED PALETĄ
            if char in "0123456789":
                self.palettes[name][char] = new_img
                continue
                
            pixels = pygame.PixelArray(new_img)
            for old_c, new_c in color_map.items():
                pixels.replace(old_c, new_c)
            pixels.close()
            self.palettes[name][char] = new_img

    def render(self, screen, text, x, y, spacing=0, palette_name=None, scale=1.0):
        if not self.palettes: return
        p_name = palette_name if palette_name in self.palettes else list(self.palettes.keys())[0]
        active_set = self.palettes[p_name]
        
        curr_x = x
        for char in text:
            if char == " ":
                curr_x += int(10 * scale)
                continue
            
            # Pobieramy obrazek dokładnie dla takiego znaku, jaki jest w tekście
            # Dzięki temu 'a' pobierze plik 59, a 'A' plik 33
            img = active_set.get(char)

            if img:
                # SKALOWANIE
                if scale != 1.0:
                    new_size = (int(img.get_width() * scale), int(img.get_height() * scale))
                    img = pygame.transform.smoothscale(img, new_size)

                screen.blit(img, (curr_x, y))
                curr_x += img.get_width() + spacing
            else:
                curr_x += int(5 * scale)

if __name__ == "__main__":
        import subprocess, sys, os
        main_path = os.path.join(os.path.dirname(__file__), "main.py")
        subprocess.run([sys.executable, main_path])