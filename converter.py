from PIL import Image

def convert_with_strict_palette(image_path, output_path):
    img = Image.open(image_path).convert('RGB')
    width, height = img.size
    tile_size = 2 
    
    # PEŁNA PALETA KOLORÓW Z TWOJEGO ZDJĘCIA
    color_map = {
        (0, 202, 255):   'W', # Woda - MUSI BYĆ BŁĘKITNA
        (60, 95, 35):    'l', # Ciemny las
        (100, 140, 65):  '.', # Jasna trawa
        (185, 105, 50):  'p', # Pustynia / Ziemia
        (155, 145, 140): '_', # Drogi (Jasnoszary)
        (115, 110, 110): 'g', # Skały (Średni szary)
        (80, 75, 75):    'G', # Góry (Ciemnoszary)
        (95, 35, 10):    'B', # Bagna / Ciemny brąz
        (255, 255, 0):   'S', # Żółty (Jednostka)
        (255, 255, 255): 'U', # Biały (Zamek/Wróg)
        (255, 0, 0):     '$', # Czerwony (Skarb)
    }

    def get_strict_char(pixel):
        # 1. Próbujemy znaleźć idealne dopasowanie
        if pixel in color_map:
            return color_map[pixel]
        
        # 2. Jeśli nie ma ideału (np. przez rozmycie), szukamy najbliższego,
        # ale z bardzo małą tolerancją
        min_dist = float('inf')
        best_char = '?'
        for color, char in color_map.items():
            dist = sum((p - c) ** 2 for p, c in zip(pixel, color))
            if dist < min_dist:
                min_dist = dist
                best_char = char
        return best_char

    map_data = []
    for y in range(0, height, tile_size):
        line = ""
        for x in range(0, width, tile_size):
            # Bierzemy kolor punktu wewnątrz kafelka (nie średnią!)
            # Średnia brudzi kolory na krawędziach rzeki
            pixel = img.getpixel((x, y))
            line += get_strict_char(pixel)
        map_data.append(line)

    with open(output_path, 'w') as f:
        f.write("\n".join(map_data))
    
    print(f"Konwersja zakończona. Sprawdź plik {output_path}")

# Uruchom na pliku ho.png lub image_9cbdf4.png
convert_with_strict_palette('ho.png', 'map.txt')