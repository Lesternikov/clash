import re
import os
from PIL import Image

def super_map_generator(image_name, fac_name, output_base):
    print("--- GENEROWANIE MAPY (Inteligentne łatanie dróg) ---")
    
    image_path = image_name if image_name.lower().endswith(('.png', '.jpg', '.bmp')) else f"{image_name}.png"
    fac_path = fac_name if fac_name.lower().endswith('.fac') else f"{fac_name}.FAC"
    output_base = output_base[:-4] if output_base.lower().endswith('.txt') else output_base
    
    out_terrain_path = f"{output_base}_terrain.txt"
    out_objects_path = f"{output_base}_objects.txt"

    # JEDEN KAFELEK = KWADRAT 2x2 PIKSELE NA OBRAZKU
    tile_size = 2 
    
    # SŁOWNIK IDEALNIE DOPASOWANY DO PLIKU !Karkhan.png
    color_map = {
        (0, 199, 251):   'W', # Woda
        (73, 109, 44):   'l', # Las
        (93, 134, 60):   '.', # Trawa
        (190, 101, 44):  'p', # Pustynia
        (158, 146, 138): '_', # Droga
        (109, 101, 101): 'g', # Niskie góry
        (81, 69, 69):    'G', # Wysokie góry
        (101, 28, 0):    'B'  # Bagno
    }

    def get_average_color(img, start_x, start_y, size):
        r, g, b = 0, 0, 0
        count = 0
        for y in range(start_y, min(start_y + size, img.height)):
            for x in range(start_x, min(start_x + size, img.width)):
                pr, pg, pb = img.getpixel((x, y))[:3]
                r += pr; g += pg; b += pb
                count += 1
        if count == 0: return (0, 0, 0)
        return (r // count, g // count, b // count)

    def get_closest_terrain(pixel_color):
        min_dist = float('inf')
        best_char = '.'
        for color, char in color_map.items():
            dist = sum((p - c) ** 2 for p, c in zip(pixel_color, color))
            if dist < min_dist:
                min_dist = dist
                best_char = char
        return best_char

    try:
        img = Image.open(image_path).convert('RGB')
        w, h = img.size
        print(f"Oryginalny obraz: {w}x{h} px. Tworzę mapę {w//tile_size}x{h//tile_size}.")
        
        # 1. BUDOWA SIATKI
        grid_terrain = []
        for y in range(0, h, tile_size):
            row = []
            for x in range(0, w, tile_size):
                avg_color = get_average_color(img, x, y, tile_size)
                row.append(get_closest_terrain(avg_color))
            grid_terrain.append(row)
            
        gh, gw = len(grid_terrain), len(grid_terrain[0])
        grid_objects = [[" " for _ in range(gw)] for _ in range(gh)]

        # --- NOWA, INTELIGENTNA FUNKCJA ŁATAJĄCA ---
        def get_patch_terrain(grid, x, y):
            up = grid[y-1][x] if y > 0 else "."
            down = grid[y+1][x] if y < gh-1 else "."
            left = grid[y][x-1] if x > 0 else "."
            right = grid[y][x+1] if x < gw-1 else "."
            
            # A. Weryfikacja mostu (Woda z dwóch przeciwnych stron)
            if (up == "W" and down == "W") or (left == "W" and right == "W"):
                return "W"
                
            # B. Zliczanie okolicznego terenu (Tylko płaskie, ignorujemy góry i lasy!)
            flat_terrains = {".": 0, "p": 0, "B": 0}
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < gh and 0 <= nx < gw:
                        t = grid[ny][nx]
                        if t in flat_terrains:
                            flat_terrains[t] += 1
                            
            # Wybieramy ten, którego jest najwięcej (np. droga na granicy pustyni i trawy)
            best_terrain = "."
            max_count = -1
            for t, count in flat_terrains.items():
                if count > max_count:
                    max_count = count
                    best_terrain = t
            return best_terrain

        # 2. TRANSFER DRÓG I ŁATANIE DZIUR
        for y in range(gh):
            for x in range(gw):
                if grid_terrain[y][x] == "_":
                    grid_objects[y][x] = "_"
                    # Zastępujemy starą, prymitywną logikę naszą nową funkcją
                    grid_terrain[y][x] = get_patch_terrain(grid_terrain, x, y)

        # 3. WCZYTYWANIE DANYCH Z PLIKU .FAC (Zostaje bez zmian)
        if os.path.exists(fac_path):
            with open(fac_path, 'r', encoding='utf-8') as f:
                fac_content = f.read()
            fac_content = re.sub(r"\\", "", fac_content)

            religie = {int(g): int(c) for g, c in re.findall(r"gameinfo gracz (\d+) .*? chrzesc (\d+)", fac_content)}
            objects_count = 0

            for x, y in re.findall(r"\(pulapka (\d+) (\d+)\)", fac_content):
                ix, iy = int(x), int(y)
                if 0 <= iy < gh and 0 <= ix < gw:
                    grid_objects[iy][ix] = "X"
                    objects_count += 1

            for x, y in re.findall(r"\(skarb (\d+) (\d+)\)", fac_content):
                ix, iy = int(x), int(y)
                if 0 <= iy < gh and 0 <= ix < gw:
                    grid_objects[iy][ix] = "$"
                    objects_count += 1

            for province_id, y in re.findall(r"\(swiatynia (\d+) (\d+)\)", fac_content):
                ix, iy = int(province_id), int(y)
                if 0 <= iy < gh and 0 <= ix < gw:
                    owner_id = ix % 5
                    is_chr = religie.get(owner_id, 0)
                    grid_objects[iy][ix] = "†" if is_chr == 1 else "ψ"
                    objects_count += 1

            for x, y in re.findall(r"\(zamek_place (\d+) (\d+)\)", fac_content):
                ix, iy = int(x), int(y)
                if 0 <= iy < gh and 0 <= ix < gw:
                    grid_objects[iy][ix] = "#"
                    objects_count += 1

            zbudowane = re.findall(r"\(zbudowano zamek (\d+)\)", fac_content)
            for z_id in zbudowane:
                sch = re.search(fr"\(schemat {z_id} (\d+) (\d+)\)", fac_content)
                if sch:
                    sx, sy = int(sch.group(1)), int(sch.group(2))
                    if 0 <= sy < gh and 0 <= sx < gw:
                        grid_objects[sy][sx] = "S"
                        objects_count += 1
                        
            print(f"Załadowano {objects_count} obiektów z FAC.")

        # 4. ZAPIS DO PLIKÓW TXT
        with open(out_terrain_path, 'w', encoding='utf-8') as f_out:
            for row in grid_terrain: f_out.write("".join(row) + "\n")
                
        with open(out_objects_path, 'w', encoding='utf-8') as f_out:
            for row in grid_objects: f_out.write("".join(row) + "\n")
        
        print(f"Sukces! Generowanie zakończone.")

    except Exception as e:
        print(f"BŁĄD: {e}")

if __name__ == "__main__":
    super_map_generator(input("Plik obrazu: "), input("Plik FAC: "), input("Nazwa mapy: "))