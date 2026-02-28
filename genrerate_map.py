import re  # Ta linijka naprawia błąd "name 're' is not defined"

def generate_full_map(fac_path, output_path):
    size = 100
    # Tworzymy czystą mapę (sama trawa)
    game_map = [["." for _ in range(size)] for _ in range(size)]

    try:
        with open(fac_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Wyciągamy PUŁAPKI (oznaczamy jako '#' - blokada)
        traps = re.findall(r"\(pulapka (\d+) (\d+)\)", content)
        for x, y in traps:
            ix, iy = int(x), int(y)
            if 0 <= ix < size and 0 <= iy < size:
                game_map[iy][ix] = "#"

        # 2. Wyciągamy SKARBY (oznaczamy jako '$')
        treasures = re.findall(r"\(skarb (\d+) (\d+)\)", content)
        for x, y in treasures:
            ix, iy = int(x), int(y)
            if 0 <= ix < size and 0 <= iy < size:
                game_map[iy][ix] = "$"

        # 3. Wyciągamy ŚWIĄTYNIE (oznaczamy jako 'S')
        temples = re.findall(r"\(swiatynia (\d+) (\d+)\)", content)
        for x, y in temples:
            ix, iy = int(x), int(y)
            if 0 <= ix < size and 0 <= iy < size:
                game_map[iy][ix] = "S"

        # Zapis do pliku
        with open(output_path, 'w', encoding='utf-8') as f_out:
            for row in game_map:
                f_out.write("".join(row) + "\n")

        print(f"Sukces! Wygenerowano mapę 100x100.")
        print(f"Przetworzono: {len(traps)} pułapek, {len(treasures)} skarbów, {len(temples)} świątyń.")

    except Exception as e:
        print(f"Wystąpił błąd: {e}")

if __name__ == "__main__":
    generate_full_map("0.FAC", "map.txt")