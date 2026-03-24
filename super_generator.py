import re
from PIL import Image

def super_map_generator(image_path, fac_path, final_output_path):
    print("--- GENEROWANIE MAPY: SYNCHRONIZACJA RELIGII (Logika ID % 5) ---")
    
    tile_size = 2
    color_map = {
        (0, 202, 255):   'W', (60, 95, 35):    'l', (100, 140, 65):  '.',
        (185, 105, 50):  'p', (155, 145, 140): '_', (115, 110, 110): 'g',
        (80, 75, 75):    'G', (95, 35, 10):    'B',
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
        w, h = img.size
        # Tworzymy siatkę terenu 100x100
        grid = [[get_closest_terrain(img.getpixel((x, y))) for x in range(0, w, tile_size)] for y in range(0, h, tile_size)]
        gh, gw = len(grid), len(grid[0])

        with open(fac_path, 'r', encoding='utf-8') as f:
            fac_content = f.read()

        # Czyszczenie śmieci z pliku
        fac_content = re.sub(r"\\", "", fac_content)

        # 1. Mapowanie religii z sekcji gameinfo (pobiera dane dla graczy 0-4)
        religie = {int(g): int(c) for g, c in re.findall(r"gameinfo gracz (\d+) .*? chrzesc (\d+)", fac_content)}

        # Inicjalizacja licznika (to naprawia Twój błąd!)
        objects_count = 0

        # 3. SKARBY ($)
        for x, y in re.findall(r"\(skarb (\d+) (\d+)\)", fac_content):
            ix, iy = int(x), int(y)
            if 0 <= iy < gh and 0 <= ix < gw:
                grid[iy][ix] = "$"
                objects_count += 1

        # 4. ŚWIĄTYNIE († / ψ) - LOGIKA MODULO 5
        # Rozwiązuje problem proporcji 69 do 2
        for province_id, y in re.findall(r"\(swiatynia (\d+) (\d+)\)", fac_content):
            ix, iy = int(province_id), int(y)
            if 0 <= iy < gh and 0 <= ix < gw:
                # Obliczamy właściciela (0-4) na podstawie ID prowincji
                owner_id = ix % 5
                # Sprawdzamy czy właściciel (0 lub 2) to chrześcijanin
                is_chr = religie.get(owner_id, 0)
                grid[iy][ix] = "†" if is_chr == 1 else "ψ"
                objects_count += 1

        # 5. FUNDAMENTY (#)
        for x, y in re.findall(r"\(zamek_place (\d+) (\d+)\)", fac_content):
            ix, iy = int(x), int(y)
            if 0 <= iy < gh and 0 <= ix < gw:
                grid[iy][ix] = "#"
                objects_count += 1

        # 6. ZAMKI ZBUDOWANE (S)
        zbudowane = re.findall(r"\(zbudowano zamek (\d+)\)", fac_content)
        for z_id in zbudowane:
            sch = re.search(fr"\(schemat {z_id} (\d+) (\d+)\)", fac_content)
            if sch:
                sx, sy = int(sch.group(1)), int(sch.group(2))
                if 0 <= sy < gh and 0 <= sx < gw:
                    grid[sy][sx] = "S"

        # Zapis do pliku
        with open(final_output_path, 'w', encoding='utf-8') as f_out:
            for row in grid:
                f_out.write("".join(row) + "\n")
        
        print(f"Sukces! Nałożono {objects_count} obiektów na mapę {gw}x{gh}.")

    except Exception as e:
        print(f"BŁĄD: {e}")

if __name__ == "__main__":
    super_map_generator(input("Obraz: "), input("Plik FAC: "), input("Wynik: "))