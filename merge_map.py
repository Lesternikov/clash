def merge_maps(terrain_map_path, objects_map_path, output_path):
    try:
        # Wczytujemy mapę terenu (z kolorami/teksturami)
        with open(terrain_map_path, 'r', encoding='utf-8') as f:
            terrain_map = [list(line.strip()) for line in f if line.strip()]

        # Wczytujemy mapę obiektów (z 0.fac)
        with open(objects_map_path, 'r', encoding='utf-8') as f:
            objects_map = [list(line.strip()) for line in f if line.strip()]

        # Sprawdzamy czy wymiary się zgadzają
        rows = min(len(terrain_map), len(objects_map))
        cols = min(len(terrain_map[0]), len(objects_map[0]))

        final_map = []

        # Symbole, które chcemy przenieść na nową mapę
        # # - fundament, & - świątynia, $ - skarb, S - zamek
        allowed_objects = {'#', '&', '$', 'S'}

        for y in range(rows):
            new_row = []
            for x in range(cols):
                obj_char = objects_map[y][x]
                
                # Jeśli w map1.txt jest ważny obiekt, nadpisujemy teren
                if obj_char in allowed_objects:
                    new_row.append(obj_char)
                else:
                    # W przeciwnym razie zostawiamy oryginalny teren z map.txt
                    # (To automatycznie ignoruje 'X' oraz '.')
                    new_row.append(terrain_map[y][x])
            
            final_map.append("".join(new_row))

        # Zapisujemy połączoną mapę
        with open(output_path, 'w', encoding='utf-8') as f_out:
            for row in final_map:
                f_out.write(row + "\n")

        print(f"Sukces! Połączono mapy. Wynik zapisano w: {output_path}")
        print(f"Rozmiar końcowy: {cols}x{rows}")

    except Exception as e:
        print(f"Wystąpił błąd podczas łączenia map: {e}")

if __name__ == "__main__":
    # terrain_map_path -> Twoje map.txt (tekstury)
    # objects_map_path -> Twoje map1.txt (z 0.fac)
    merge_maps("map.txt", "map1.txt", "final_map.txt")