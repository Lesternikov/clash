import re

def generate_full_map(fac_path, output_path):
    size = 100
    # Tworzymy czystą mapę (sama trawa)
    game_map = [["." for _ in range(size)] for _ in range(size)]

    try:
        with open(fac_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Miejsca pod budowę ZAMKU (zamek_place) -> Symbol '#'
        castle_plots = re.findall(r"\(zamek_place (\d+) (\d+)\)", content)
        for x, y in castle_plots:
            ix, iy = int(x), int(y)
            if 0 <= ix < size and 0 <= iy < size:
                game_map[iy][ix] = "#"

        # 2. ŚWIĄTYNIE (swiatynia) -> Symbol '&' (zgodnie z naszą umową)
        temples = re.findall(r"\(swiatynia (\d+) (\d+)\)", content)
        for x, y in temples:
            ix, iy = int(x), int(y)
            if 0 <= ix < size and 0 <= iy < size:
                game_map[iy][ix] = "&"

        # 3. SKARBY (skarb) -> Symbol '$'
        treasures = re.findall(r"\(skarb (\d+) (\d+)\)", content)
        for x, y in treasures:
            ix, iy = int(x), int(y)
            if 0 <= ix < size and 0 <= iy < size:
                game_map[iy][ix] = "$"

        # 4. PUŁAPKI (pulapka) -> Symbol 'X' (zmienione z #, żeby nie mylić z budową)
        traps = re.findall(r"\(pulapka (\d+) (\d+)\)", content)
        for x, y in traps:
            ix, iy = int(x), int(y)
            if 0 <= ix < size and 0 <= iy < size:
                game_map[iy][ix] = "X"

        # 5. ISTNIEJĄCE ZAMKI (S) - na podstawie faktów o zbudowaniu
        # Uwaga: Zazwyczaj w FAC są to współrzędne budynków graczy
        # Jeśli masz konkretne (S x y) w FAC, dodaj je tutaj.

        # Zapis do pliku - WAŻNE: upewnij się, że każda linia ma DOKŁADNIE 100 znaków
        with open(output_path, 'w', encoding='utf-8') as f_out:
            for row in game_map:
                f_out.write("".join(row) + "\n")

        print(f"Sukces! Wygenerowano nową mapę.")
        print(f"Fundamenty (#): {len(castle_plots)}")
        print(f"Świątynie (&): {len(temples)}")
        print(f"Skarby ($): {len(treasures)}")
        print(f"Pułapki (X): {len(traps)}")

    except Exception as e:
        print(f"Wystąpił błąd: {e}")

if __name__ == "__main__":
    generate_full_map("0.FAC", "map.txt")