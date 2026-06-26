import random
# z grafiki przerabia na dwie mapy podstawę i budynki
# Rozmiar mapy (zgodny z Twoim world.py)
W, H = 100, 100

def create_map():
    # Zaczynamy od czystej trawy
    terrain = [["." for _ in range(W)] for _ in range(H)]
    objects = [[" " for _ in range(W)] for _ in range(H)]

    # Funkcja do tworzenia naturalnie wyglądających plam terenu
    def create_blob(char, num_blobs, min_r, max_r):
        for _ in range(num_blobs):
            cx = random.randint(15, W - 15)
            cy = random.randint(15, H - 25) # Zostawiamy dół na morze
            radius = random.randint(min_r, max_r)
            
            for y in range(H):
                for x in range(W):
                    # Równanie koła z lekkim szumem na brzegach
                    if (x - cx)**2 + (y - cy)**2 < radius**2:
                        if random.random() < 0.85: # 85% szansy na wypełnienie (poszarpane brzegi)
                            terrain[y][x] = char

    # 1. Tworzymy plamy Pustyni ('p') i Bagna ('B')
    create_blob("p", 6, 6, 14)
    create_blob("B", 5, 5, 12)

    # 2. Tworzymy Morze ('M') na samym dole mapy (ostatnie 15-20 wierszy)
    for y in range(H - 18, H):
        for x in range(W):
            # Im niżej, tym większa szansa na morze (gładkie przejście linii brzegowej)
            prob = 0.5 + (y - (H - 18)) * 0.1
            if random.random() < prob:
                terrain[y][x] = "M"
        # Ostatnie 10 linii to już 100% morza
        if y > H - 10:
            for x in range(W):
                terrain[y][x] = "M"

    # 3. Tworzymy wijącą się Rzekę ('W') od góry do morza
    rx = W // 2
    for ry in range(0, H):
        # Przerywamy rzekę, gdy wpadnie do w 100% uformowanego morza
        if terrain[ry][rx] == "M" and ry > H - 12:
            break
            
        # Rzeka ma 2 kafelki szerokości
        terrain[ry][rx] = "W"
        if rx + 1 < W:
            terrain[ry][rx + 1] = "W"
            
        # Rzeka lekko meandruje
        if random.random() < 0.3:
            rx += random.choice([-1, 1])

    # Zapisujemy do plików!
    with open("testowa_terrain.txt", "w", encoding="utf-8") as f:
        for row in terrain:
            f.write("".join(row) + "\n")

    with open("testowa_objects.txt", "w", encoding="utf-8") as f:
        for row in objects:
            f.write("".join(row) + "\n")

    print("Wygenerowano nową mapę: testowa_terrain.txt oraz testowa_objects.txt!")

if __name__ == "__main__":
    create_map()