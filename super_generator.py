import re
from PIL import Image

def super_map_generator(image_path, fac_path, final_output_path):
    print("--- ROZPOCZĘCIE GENEROWANIA MAPY ---")
    
    # --- KROK 1: KONWERSJA OBRAZU NA TEREN ---
    tile_size = 2
    # Definicja kolorów terenu (z Twojej palety)
    color_map = {
        (0, 202, 255):   'W', # Woda
        (60, 95, 35):    'l', # Las
        (100, 140, 65):  '.', # Trawa
        (185, 105, 50):  'p', # Ziemia
        (155, 145, 140): '_', # Drogi
        (115, 110, 110): 'g', # Skały
        (80, 75, 75):    'G', # Góry
        (95, 35, 10):    'B', # Bagna
    }

    def get_closest_terrain(pixel):
        if pixel in color_map: return color_map[pixel]
        min_dist = float('inf')
        best_char = '.'
        for color, char in color_map.items():
            dist = sum((p - c) ** 2 for p, c in zip(pixel, color))
            if dist < min_dist:
                min_dist = dist
                best_char = char
        return best_char

    try:
        img = Image.open(image_path).convert('RGB')
        width, height = img.size
        # Budujemy matrycę terenu
        terrain_grid = []
        for y in range(0, height, tile_size):
            row = []
            for x in range(0, width, tile_size):
                pixel = img.getpixel((x, y))
                row.append(get_closest_terrain(pixel))
            terrain_grid.append(row)
        
        grid_h = len(terrain_grid)
        grid_w = len(terrain_grid[0])
        print(f"1. Teren przetworzony ({grid_w}x{grid_h})")

        # --- KROK 2: ODCZYT OBIEKTÓW Z 0.FAC ---
        with open(fac_path, 'r', encoding='utf-8') as f:
            fac_content = f.read()

        # Definiujemy co chcemy nałożyć (bez pułapek 'X')
        object_defs = [
            ("Fundamenty (#)", r"\(zamek_place (\d+) (\d+)\)", "#"),
            ("Świątynie (&)", r"\(swiatynia (\d+) (\d+)\)", "&"),
            ("Skarby ($)", r"\(skarb (\d+) (\d+)\)", "$"),
            ("Zamki (S)", r"\(zbudowano zamek (\d+) (\d+)\)", "S")
        ]

        # --- KROK 3: FUZJA (NAKŁADANIE) ---
        objects_count = 0
        for name, pattern, symbol in object_defs:
            matches = re.findall(pattern, fac_content)
            for x, y in matches:
                ix, iy = int(x), int(y)
                # Nakładamy tylko jeśli mieści się w granicach obrazu
                if 0 <= ix < grid_w and 0 <= iy < grid_h:
                    terrain_grid[iy][ix] = symbol
                    objects_count += 1
        
        print(f"2. Nałożono {objects_count} obiektów z pliku {fac_path}")

        # --- KROK 4: ZAPIS KOŃCOWY ---
        with open(final_output_path, 'w', encoding='utf-8') as f_out:
            for row in terrain_grid:
                f_out.write("".join(row) + "\n")
        
        print(f"3. Sukces! Finalna mapa zapisana w: {final_output_path}")

    except Exception as e:
        print(f"BŁĄD: {e}")

if __name__ == "__main__":
    plik_fac = input("Podaj nazwę pliku FAC (np. 0.FAC): ")
    if not plik_fac.endswith("0.FAC"):
        plik_fac += "0.FAC"
        
    super_map_generator('!Karkhan.png', plik_fac, 'final_map1.txt')

import main