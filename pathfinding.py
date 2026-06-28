import heapq
import os
import pygame
from settings import TERRAIN_TYPES, MAP_WIDTH, TILE_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH
from map_loader import load_fac_objects
from castle import Castle
 
 
# ================================================================
#  MAPA KROKÓW (STEP_S32) — 130 plików (0-129)
#
#  CZARNE stopy (0-66)  = jednostka DOTRZE w tej turze
#  CZERWONE stopy (67-129) = ZABRAKNIE punktów ruchu
# ================================================================
#  SYSTEM STYKÓW — każdy kafel trasy zna kierunek SKĄD i DOKĄD
#
#  Klucz: (skąd_dx, skąd_dy, dokąd_dx, dokąd_dy)
#  Czyli: z jakiego kierunku przyszedłem + w jaki kierunek idę
#
#  Przykład: (1,0, 1,0) = szedłem w prawo i dalej idę w prawo → prosta linia
#            (0,1, 1,0) = szedłem w dół, teraz skręcam w prawo → zakręt
#
#  CZARNE (dotrę w tej turze)
#  CZERWONE (nie dotrę w tej turze)
STEP_BLACK = {
    # Format: (skąd_x, skąd_y, dokąd_x, dokąd_y): numer_pliku
    # Zakręty używają grafiki kierunku DOKĄD (stopa "wchodzi" w nowy kierunek)
 
    # === PROSTO ===
    ( 1, 0,  1, 0):  50,  # → do →
    (-1, 0, -1, 0):  22,  # ← do ←
    ( 0, 1,  0, 1):   4,  # ↓ do ↓  
    ( 0,-1,  0,-1):  32,  # ↑ do ↑
    ( 1, 1,  1, 1):  59,  # ↘ do ↘
    (-1, 1, -1, 1):  13,  # ↙ do ↙
    ( 1,-1,  1,-1):  41,  # ↗ do ↗  
    (-1,-1, -1,-1):  31,  # ↖ do ↖
 
    # === ZAKRĘTY 90° ===
    ( 1, 0,  0,-1):  48,  # → do ↑
    (-1, 0,  0, 1):  52,  # ↓ do →
    ( 0, 1,  1, 0):   2,  # ↓ do →
    ( 0,-1, -1, 0):  38,  # ↑ do ←
    ( 1, 0,  0, 1):  20,  # → do ↓
    (-1, 0,  0,-1):  16,  # ← do ↑
    ( 0, 1, -1, 0):   6,  # ↓ do ←
    ( 0,-1,  1, 0):  34,  # ↑ do →

    # === ZE SKOSU W PROSTĄ ===
    ( 1, 1,  1, 0):  58, # ↘ do →
    ( 1, 1,  0, 1):  60, # ↘ do ↓
    (-1, 1, -1, 0):  14, # ↙ do ←
    (-1, 1,  0, 1):  12, # ↙ do ↓
    ( 1,-1,  1, 0):  42, # ↗ do →
    ( 1,-1,  0,-1):  40, # ↗ do ↑
    (-1,-1, -1, 0):  30, # ↖ do ←
    (-1,-1,  0,-1):  24, # ↖ do ↑

    # === Z PROSTEJ W SKOS ===
    ( 0,-1,  1,-1):  33, # ↑ do ↗
    ( 0,-1, -1,-1):  39, # ↑ do ↖
    ( 0, 1,  1, 1):   3, # ↓ do ↘
    ( 0, 1, -1, 1):   5, # ↓ do ↙
    ( 1, 0,  1,-1):  49, # → do ↗
    ( 1, 0,  1, 1):  51, # → do ↘
    (-1, 0, -1, 1):  21, # ← do ↙
    (-1, 0, -1,-1):  23, # ← do ↖

    # === Z SKOSU W SKOS ===
    ( 1,-1, -1,-1):  47, # ↗ do ↖
    (-1,-1,  1,-1):  25, # ↖ do ↗
    ( 1, 1, -1, 1):  61, # ↘ do ↙
    (-1, 1,  1, 1):  11, # ↙ do ↘

    ( 1,-1,  1, 1):  43, # ↗ do ↘
    (-1,-1, -1, 1):  29, # ↖ do ↙
    ( 1, 1,  1,-1):  57, # ↘ do ↗
    (-1, 1, -1,-1):  15, # ↙ do ↖

}

 
STEP_RED = {
    # === PROSTO ===
    ( 1, 0,  1, 0): 115,  # → do → 
    (-1, 0, -1, 0):  87,  # ← do ←  
    ( 0, 1,  0, 1):  69,  # ↓ do ↓  
    ( 0,-1,  0,-1):  97,  # ↑ do ↑
    ( 1, 1,  1, 1): 124,  # ↘ do ↘
    (-1, 1, -1, 1):  78,  # ↙ do ↙
    ( 1,-1,  1,-1): 106,  # ↗ do ↗
    (-1,-1, -1,-1):  96,  # ↖ do ↖
 
    # === ZAKRĘTY 90° ===
    ( 1, 0,  0,-1): 113,  # → do ↑
    (-1, 0,  0, 1):  85,  # ← do ↓
    ( 0, 1,  1, 0):  67,  # ↓ do →
    ( 0,-1, -1, 0): 103,  # ↑ do ←
    ( 1, 0,  0, 1): 117,  # → do ↓
    (-1, 0,  0,-1):  81,  # ← do ↑
    ( 0, 1, -1, 0):  71,  # ↓ do ←
    ( 0,-1,  1, 0):  99,  # ↑ do →

    # === ZE SKOSU W PROSTĄ ===
    ( 1, 1,  1, 0): 123, # ↘ do →
    ( 1, 1,  0, 1): 125, # ↘ do ↓
    (-1, 1, -1, 0):  79, # ↙ do ←
    (-1, 1,  0, 1):  77, # ↙ do ↓
    ( 1,-1,  1, 0): 107, # ↗ do →
    ( 1,-1,  0,-1): 105, # ↗ do ↑
    (-1,-1, -1, 0):  95, # ↖ do ←
    (-1,-1,  0,-1):  89, # ↖ do ↑

    # === Z PROSTEJ W SKOS ===
    ( 0,-1,  1,-1):  98, # ↑ do ↗
    ( 0,-1, -1,-1): 104, # ↑ do ↖
    ( 0, 1,  1, 1):  68, # ↓ do ↘
    ( 0, 1, -1, 1):  70, # ↓ do ↙
    ( 1, 0,  1,-1): 114, # → do ↗
    ( 1, 0,  1, 1): 116, # → do ↘
    (-1, 0, -1, 1):  86, # ← do ↙
    (-1, 0, -1,-1):  88, # ← do ↖

    # === Z SKOSU W SKOS ===
    ( 1,-1, -1,-1): 112, # ↗ do ↖
    (-1,-1,  1,-1):  90, # ↖ do ↗
    ( 1, 1, -1, 1): 126, # ↘ do ↙
    (-1, 1,  1, 1):  76, # ↙ do ↘

    ( 1,-1,  1, 1): 108, # ↗ do ↘
    (-1,-1, -1, 1):  94, # ↖ do ↙
    ( 1, 1,  1,-1): 122, # ↘ do ↗
    (-1, 1, -1,-1):  80, # ↙ do ↖
}
 
#  FALLBACK — pierwszy krok trasy (brak poprzedniego kierunku)
STEP_BLACK_SINGLE = {
    ( 0, 1):   4, # ↓↓↓↓↓↓
    ( 0, 0):  64, # xxxxxx
    ( 0,-1):  32, # ↑↑↑↑↑↑
    ( 1, 1):  59, # ↘↘↘↘↘
    ( 1, 0):  50, # →→→→→→→
    ( 1,-1):  41, # ↗↗↗↗↗
    (-1, 1):  13, # ↙↙↙↙↙
    (-1, 0):  22, # ←←←←←←
    (-1,-1):  31, # ↖↖↖↖↖
}
STEP_RED_SINGLE = {
    ( 0, 1):  69, # ↓↓↓↓↓↓
    ( 0, 0):  64, # xxxxxx
    ( 0,-1):  97, # ↑↑↑↑↑↑
    ( 1, 1): 124, # ↘↘↘↘↘
    ( 1, 0): 115, # →→→→→→→
    ( 1,-1): 106, # ↗↗↗↗↗
    (-1, 1):  78, # ↙↙↙↙↙
    (-1, 0):  87, # ←←←←←←
    (-1,-1):  96, # ↖↖↖↖↖
}
 
# ================================================================
#  USTAWIENIA — zmieniaj tu
# ================================================================
 
#  Folder ze stopami — zmień jeśli gdzie indziej
STEP_FOLDER = os.path.join("assets", "minimum", "STEP_S32")
 
#  Rozmiar stopy na ekranie (oryginał: 64x64)
#  Zwiększ żeby były bardziej widoczne, zmniejsz jeśli za duże
STEP_DISPLAY_SIZE = (32, 32)
 
#  64 i 129 to pliki z X (cel/znacznik) — na razie nieużywane
#  Możesz je przypisać do specjalnych celów w przyszłości
 
# ================================================================
 
 
class Pathfinder:
    _arrow_imgs = None  # grafiki strzałek budowy drogi
    _step_imgs  = None  # grafiki stóp trasy
 
    def __init__(self, world_instance):
        self.world = world_instance
 
    # -------------------------------------------------------
    # ŁADOWANIE MAPY
    # -------------------------------------------------------
 
    def load_map(self, filename):
        game_map = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    clean_line = line.replace('\n', '').replace('\r', '')
                    if clean_line:
                        clean_line = clean_line.ljust(MAP_WIDTH, ' ')
                        game_map.append(list(clean_line))
        except Exception as e:
            print(f"Błąd ładowania mapy {filename}: {e}")
        return game_map
 
    def load(self, map_base_name, fac_file):
        w = self.world
        w.bg_map = self.load_map(f"{map_base_name}_terrain.txt")
        w.map    = self.load_map(f"{map_base_name}_objects.txt")

        objects = load_fac_objects(fac_file)
        castle_places = objects.get("zamek_place", [])
        
        # 1. WSZYSTKIE miejsca z pliku .FAC traktujemy jako puste fundamenty
        w.castle_locations = []
        for x, y in castle_places:
            w.castle_locations.append((int(x), int(y)))

        # 2. RĘCZNE USTAWIENIE STARTOWYCH ZAMKÓW NA MAPIE
        # Format -> ID Gracza : (x, y)
        startowe_zamki = {
            0: (14, 20),  # Czerwony (Don Marek)
            1: (90, 8),  # Niebieski (Lech VI) - prawy górny róg (do poprawki)
            2: (47, 80),  # Zielony (Mściwój) - dół środek (do poprawki)
            3:(14, 24),
            #3: (90, 72),  # Biały (Biały Kieł) - prawy dół (do poprawki)
            #4: (60, 46)   # Żółty (Złoty Pan) - środek prawo (do poprawki)
            4: (20, 20)
        } 

        w.castles = []
        for owner_id, (cx, cy) in startowe_zamki.items():
            # Upewniamy się, że gracz o danym ID został załadowany w world.py
            if owner_id < len(w.players):
                c = Castle(cx, cy, w.players[owner_id])
                c.gold = 250 # Ilość startowego złota w zamku
                w.castles.append(c)

        # === INTELIGENTNE SZUKANIE PORTÓW Z MAPY ("R") ===
        w.ports = []
        zajete_porty = set() 
        
        for y in range(len(w.map)):
            for x in range(len(w.map[y])):
                if w.map[y][x] == "R" and (x, y) not in zajete_porty:
                    
                    # --- PUNKTOWY SKANER WODY ---
                    woda_boki = 0  # Punkty za wodę po bokach (oś X)
                    woda_dol = 0   # Punkty za wodę na dole (oś Y)

                    # Sprawdzamy DÓŁ (pod portem, czyli Y rośnie)
                    if y + 2 < len(w.bg_map):
                        if w.bg_map[y+2][x] in ['W', 'B', 'w', 'b', 'p']: woda_dol += 1
                        if x + 1 < len(w.bg_map[0]) and w.bg_map[y+2][x+1] in ['W', 'B', 'w', 'b', 'p']: woda_dol += 1

                    # Sprawdzamy BOKI (prawo i lewo, czyli X rośnie lub maleje)
                    if x + 2 < len(w.bg_map[0]): # Prawa strona
                        if w.bg_map[y][x+2] in ['W', 'B', 'w', 'b', 'p']: woda_boki += 1
                        if y + 1 < len(w.bg_map) and w.bg_map[y+1][x+2] in ['W', 'B', 'w', 'b', 'p']: woda_boki += 1
                    if x - 1 >= 0: # Lewa strona
                        if w.bg_map[y][x-1] in ['W', 'B', 'w', 'b', 'p']: woda_boki += 1
                        if y + 1 < len(w.bg_map) and w.bg_map[y+1][x-1] in ['W', 'B', 'w', 'b', 'p']: woda_boki += 1

                    # Jeśli jest więcej wody z boku niż na dole, port jest poziomy (2).
                    orientacja = 2 if woda_boki > woda_dol else 1
                    
                    port = {
                        "x": x, 
                        "y": y, 
                        "has_ship": False, 
                        "orientation": orientacja,
                        "garrison": [],   
                        "cooldown": 0     
                    }
                    w.ports.append(port)
                    
                    # Wylewamy beton na 4 kratki w pamięci gry
                    for dy in range(2):
                        for dx in range(2):
                            if y + dy < len(w.map) and x + dx < len(w.map[0]):
                                w.map[y + dy][x + dx] = "R"
                                zajete_porty.add((x + dx, y + dy))
    # -------------------------------------------------------
    # POMOCNICZE
    # -------------------------------------------------------
 
    def get_tile_at(self, x, y):
        if 0 <= y < len(self.world.map) and 0 <= x < len(self.world.map[y]):
            tile = self.world.map[y][x]
            # Oszukujemy system dla dróg: jeśli na drodze leży pułapka, sąsiedzi nadal widzą tu drogę!
            if tile == "X" and getattr(self.world, 'trap_backgrounds', {}).get((x, y)) == "_":
                return "_"
            return tile
        return " "
 
    def get_bg_tile_at(self, x, y):
        if 0 <= y < len(self.world.bg_map) and 0 <= x < len(self.world.bg_map[y]):
            return self.world.bg_map[y][x]
        return None
 
    def is_tile_passable(self, x, y, unit_type):
        tile = self.world.map[y][x]
        if tile == "W": return unit_type == "ship"
        if tile == "V": return False
        return True
 
    def check_collision(self, x, y):
        return self.world.map[y][x] in ("W", "V")
 
    def is_walkable(self, x, y, unit=None, target_castle=None, dest_x=None, dest_y=None):
        w = self.world
        if not (0 <= x < len(w.map[0]) and 0 <= y < len(w.map)):
            return False
 
        if target_castle:
            size = 2 if target_castle.building_type in ["Zamek", "Twierdza"] else 1
            if target_castle.x <= x < target_castle.x + size and \
               target_castle.y <= y < target_castle.y + size:
                return True
 
        for castle in w.castles:
            if target_castle and castle == target_castle:
                continue
            size = 2 if castle.building_type in ["Zamek", "Twierdza"] else 1
            if castle.x <= x < castle.x + size and castle.y <= y < castle.y + size:
                return False
 
        bg_tile  = w.bg_map[y][x]
        raw_obj_tile = w.map[y][x] # Prawdziwy kafel (np. "X")
 
        # =======================================================
        # LOGIKA PUŁAPEK - ZANIM SPRAWDZIMY TEREN!
        # =======================================================
        if raw_obj_tile == "X":
            trap = getattr(w, 'traps', {}).get((x, y))
            if trap:
                current_player = w.players[w.current_player]
                # 1. Nasza pułapka - ZAWSZE traktowana jako przeszkoda (omijamy własne miny)
                if trap["owner"] == current_player:
                    return False 
                # 2. Obca, ale WYKRYTA pułapka - też traktowana jako mur
                if current_player in trap.get("detected_by", set()):
                    return False 

        # Jeśli pułapka jest obca i NIEWYKRYTA, zachowujemy się tak, jakby jej tu nie było!
        # get_tile_at "oszukuje" i zwraca "_" (drogę), jeśli była pod pułapką.
        obj_tile = self.get_tile_at(x, y)
 
        if obj_tile == "_":
            pass # Droga (most) pozwala przejść niezależnie od tego czy to woda
        else:
            if "cost" not in TERRAIN_TYPES.get(bg_tile, {}):
                return False
 
        unwalkable = ["S", "&", "R", "W", "G", "B", "M"] # "X" usunięte z listy blokad!
        if obj_tile != " " and obj_tile in unwalkable:
            if obj_tile == "R" and dest_x is not None and dest_y is not None and x == dest_x and y == dest_y:
                pass
            else:
                return False
            
        # =======================================================
        # Omijanie WSZYSTKICH jednostek (wrogów i sojuszników)
        # =======================================================
        if unit is not None:
            for other in w.units:
                if other.x == x and other.y == y and other != unit:
                    # ZEZWALAMY NA WEJŚCIE TYLKO JEŚLI TO JEST OSTATECZNY CEL MARSZU
                    # (pozwala to na atak wroga lub wywołanie łączenia własnych oddziałów)
                    if dest_x is not None and dest_y is not None and x == dest_x and y == dest_y:
                        pass 
                    else:
                        return False # Każda inna jednostka w połowie drogi działa jak mur!
                            
        return True
  
    # -------------------------------------------------------
    # ZNAJDOWANIE ŚCIEŻKI
    # -------------------------------------------------------
 
    def find_path(self, unit, dest_x, dest_y):
        w = self.world
        target_castle = None
        for c in w.castles:
            if c.x <= dest_x <= c.x + 1 and c.y <= dest_y <= c.y + 1:
                target_castle = c
                break
 
        queue   = [(0, unit.x, unit.y, [])]
        visited = {}
 
        while queue:
            current_cost, cx, cy, path = heapq.heappop(queue)
 
            if (cx, cy) in visited and visited[(cx, cy)] <= current_cost:
                continue
            visited[(cx, cy)] = current_cost
 
            if target_castle:
                if target_castle.x <= cx <= target_castle.x + 1 and \
                   target_castle.y <= cy <= target_castle.y + 1:
                    return path
            elif (cx, cy) == (dest_x, dest_y):
                return path
 
            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]:
                nx, ny = cx + dx, cy + dy
                if not self.is_walkable(nx, ny, unit, target_castle, dest_x, dest_y):
                    continue
 
                bg_tile  = w.bg_map[ny][nx]
                # ZMIANA: używamy get_tile_at, aby niewidoczna pułapka na drodze kosztowała tyle co droga!
                obj_tile = self.get_tile_at(nx, ny) 
 
                base_cost = TERRAIN_TYPES.get("_", {}).get("cost", 3) \
                            if obj_tile == "_" \
                            else TERRAIN_TYPES.get(bg_tile, {}).get("cost", 4)
 
                move_modifier  = 1.41 if (dx != 0 and dy != 0) else 1.0
                new_total_cost = current_cost + base_cost * move_modifier
 
                heapq.heappush(queue, (new_total_cost, nx, ny, path + [(nx, ny)]))
        return []
 
    # -------------------------------------------------------
    # ŁADOWANIE GRAFIK STÓP
    # -------------------------------------------------------
 
    def _load_steps(self):
        """
        Ładuje wszystkie unikalne numery plików z STEP_BLACK i STEP_RED.
        Każdy plik ładowany tylko raz, nawet jeśli używany wielokrotnie.
        """
        # Zbieramy wszystkie unikalne numery
        all_nums = set(STEP_BLACK.values()) | set(STEP_RED.values()) | \
                   set(STEP_BLACK_SINGLE.values()) | set(STEP_RED_SINGLE.values()) | \
                   {64, 129}
        
        raw = {}  # numer -> Surface
        for num in all_nums:
            path = os.path.join(STEP_FOLDER, f"STEP_S32_{num}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                raw[num] = pygame.transform.scale(img, STEP_DISPLAY_SIZE)
            else:
                print(f"[Stopy] BRAK: STEP_S32_{num}.png")
                surf = pygame.Surface(STEP_DISPLAY_SIZE, pygame.SRCALPHA)
                cx, cy = STEP_DISPLAY_SIZE[0]//2, STEP_DISPLAY_SIZE[1]//2
                r = STEP_DISPLAY_SIZE[0]//3
                pygame.draw.circle(surf, (255,255,255), (cx,cy), r+1)
                pygame.draw.circle(surf, (100,100,100), (cx,cy), r)
                raw[num] = surf
 
        # Budujemy słowniki kierunek->Surface
        Pathfinder._step_imgs = {
            "black":        {k: raw[v] for k, v in STEP_BLACK.items()},
            "red":          {k: raw[v] for k, v in STEP_RED.items()},
            "black_single": {k: raw[v] for k, v in STEP_BLACK_SINGLE.items()},
            "red_single":   {k: raw[v] for k, v in STEP_RED_SINGLE.items()},
            "marks":        {64: raw[64], 129: raw[129]},
        }
        print("[Stopy] Załadowano grafiki kroków.")
 
    # -------------------------------------------------------
    # RYSOWANIE TRASY — STOPY zamiast kropek
    # -------------------------------------------------------
 
    def draw_path_dots(self, screen, unit, path):
        w = self.world

        if Pathfinder._step_imgs is None:
            self._load_steps()

        imgs = Pathfinder._step_imgs
        current_x, current_y = unit.x, unit.y
        accumulated_cost = 0

        # === POPRAWKA: Pobieramy limit najsłabszej jednostki! ===
        limit_mp = unit.get_effective_move_points() if hasattr(unit, 'get_effective_move_points') else unit.move_points

        full = [(unit.x, unit.y)] + list(path)

        for i in range(1, len(full)):
            px, py = full[i]
            prev_x, prev_y = full[i-1]

            in_dx = px - prev_x
            in_dy = py - prev_y
            in_dir = ((in_dx > 0) - (in_dx < 0), (in_dy > 0) - (in_dy < 0))

            if i < len(full) - 1:
                next_x, next_y = full[i+1]
                out_dx = next_x - px
                out_dy = next_y - py
                out_dir = ((out_dx > 0) - (out_dx < 0), (out_dy > 0) - (out_dy < 0))
            else:
                out_dir = in_dir

            tile_char = w.map[py][px]
            base_cost = TERRAIN_TYPES.get(tile_char, {}).get("cost", 4)
            move_mod  = 1.41 if (in_dx != 0 and in_dy != 0) else 1.0
            accumulated_cost += base_cost * move_mod

            # === POPRAWKA: Sprawdzamy limit_mp zamiast unit.move_points! ===
            in_range = accumulated_cost <= limit_mp
            
            if i == len(full) - 1:
                img = imgs["marks"][64] if in_range else imgs["marks"][129]
            else:
                pairs   = imgs["black"]        if in_range else imgs["red"]
                singles = imgs["black_single"] if in_range else imgs["red_single"]
                
                key = (in_dir[0], in_dir[1], out_dir[0], out_dir[1])
                img = pairs.get(key)
                
                if img is None:
                    img = singles.get(in_dir)

            screen_x = px * TILE_SIZE + TILE_SIZE // 2 - w.camera_x
            screen_y = py * TILE_SIZE + TILE_SIZE // 2 - w.camera_y

            margin = TILE_SIZE * 2
            if not (-margin < screen_x < SCREEN_WIDTH  + margin and
                    -margin < screen_y < SCREEN_HEIGHT + margin):
                continue

            if img:
                blit_x = screen_x - img.get_width()  // 2
                blit_y = screen_y - img.get_height() // 2
                screen.blit(img, (blit_x, blit_y))
            else:
                color = (0, 0, 0) if in_range else (255, 0, 0)
                pygame.draw.circle(screen, (255,255,255), (screen_x, screen_y), 5)
                pygame.draw.circle(screen, color,         (screen_x, screen_y), 4)
 
    # -------------------------------------------------------
    # STRZAŁKI BUDOWY DROGI
    # -------------------------------------------------------
 
    def _load_arrows(self):
        arrow_files = {
            (0, -1): "assets/MAP_BUTT_S32_27.png",  # góra
            (-1, 0): "assets/MAP_BUTT_S32_30.png",  # lewo
            (0,  1): "assets/MAP_BUTT_S32_29.png",  # dół
            (1,  0): "assets/MAP_BUTT_S32_28.png",  # prawo
        }
        imgs = {}
        for direction, path in arrow_files.items():
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                imgs[direction] = img
            else:
                print(f"[Strzałki] BRAK: {path}")
                surf = pygame.Surface((10, 10), pygame.SRCALPHA)
                surf.fill((200, 200, 200, 180))
                imgs[direction] = surf
        Pathfinder._arrow_imgs = imgs

    def _find_nearest_base_terrain(self, start_x, start_y, base_terrains):
        """Skanuje okolicę promieniście, żeby zgadnąć tło pod obiektem."""
        w = self.world
        for radius in range(1, 4): # Szuka w promieniu 1, 2, 3 kratek
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    nx, ny = start_x + dx, start_y + dy
                    if 0 <= ny < len(w.map) and 0 <= nx < len(w.map[0]):
                        if w.map[ny][nx] in base_terrains:
                            return w.map[ny][nx]
        return "." # Domyślna trawa w razie ekstremalnej sytuacji
      
    def get_river_direction(self, x, y):
        w = self.world
        # Sprawdzamy, z której strony jest najbliższy ląd
        if y > 0 and w.map[y-1][x] in [".", "p", "B"]: return "UP"
        if x > 0 and w.map[y][x-1] in [".", "p", "B"]: return "LEFT"
        if x < len(w.map[0])-1 and w.map[y][x+1] in [".", "p", "B"]: return "RIGHT"
        if y < len(w.map)-1 and w.map[y+1][x] in [".", "p", "B"]: return "DOWN"
        return "UP" # Domyślny, jeśli coś pójdzie nie tak
       
    def is_near_tile(self, x, y, search_type, check_bg=False):
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0: continue
                
                # Skoro jesteśmy w Pathfinderze, wywołujemy po prostu self!
                if check_bg:
                    found_tile = self.get_bg_tile_at(x + dx, y + dy)
                else:
                    found_tile = self.get_tile_at(x + dx, y + dy)
                    
                if found_tile == search_type:
                    return True
        return False
    
    def is_area_occupied_by_foundation(self, gx, gy):
        w = self.world
        """Zwraca True, jeśli pole gx, gy jest częścią (lub samym) fundamentem #."""
        check_positions = [
            (gx, gy),       # Bezpośrednio
            (gx - 1, gy),   # Lewo
            (gx, gy - 1),   # Góra
            (gx - 1, gy - 1)# Skos
        ]
        
        for cx, cy in check_positions:
            if 0 <= cy < len(w.map) and 0 <= cx < len(w.map[0]):
                if w.map[cy][cx] == "#":
                    return True
        return False
    
    def can_build_trap(self, x, y):
        # gdzie można budować pułapkę
        w = self.world
        if not (0 <= y < len(w.map) and 0 <= x < len(w.map[0])): 
            return False
            
        bg_terrain = w.bg_map[y][x] # Warstwa podłoża (lasy, góry, woda)
        obj_terrain = w.map[y][x]   # Warstwa obiektów (zamki, fundamenty)

        # 1. Blokada ze względu na podłoże
        if bg_terrain in ["l", "g", "G", "W", "M", "B", "b", "V"]: 
            if obj_terrain != "_": # Zezwalamy na budowę TYLKO, jeśli jest tam most (droga)!
                return False
            
        # 2. Blokada ze względu na obiekty na mapie
        if obj_terrain in ["#", "&", "S", "x", "X"]: 
            return False
            
        # Nie budujemy na budynkach (duże litery) ani innych pułapkach
        if obj_terrain.isupper() and obj_terrain not in ["P"]: 
            return False
            
        return True
            
    def can_build_road(self, x, y):
        # gdzie można budować drogę
        w = self.world
        if not (0 <= y < len(w.map) and 0 <= x < len(w.map[0])):
            return False
        
        bg_terrain = w.bg_map[y][x]
        obj_terrain = w.map[y][x]
        
        # 1. Blokada ze względu na podłoże
        if bg_terrain in ["l", "g", "G", "W", "M", "B", "b"]: 
            return False
            
        # 2. Blokada ze względu na obiekty na mapie (nie budujemy na drodze "_")
        if obj_terrain in ["#", "&", "S", "x", "X", "_"]: 
            return False
            
        if obj_terrain.isupper() and obj_terrain not in ["P"]: 
            return False
            
        return True       

if __name__ == "__main__":
    import subprocess, sys, os
    main_path = os.path.join(os.path.dirname(__file__), "main.py")
    subprocess.run([sys.executable, main_path])
