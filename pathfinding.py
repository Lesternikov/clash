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
#
#  Czarne pliki ze zdjęcia — biorę najlepszy z każdej grupy:
#  Grupa A (2-6):   ↗↘↓↙←
#  Grupa B (11-16): ↖↑↗→↘↓
#  Grupa C (19-25): ↙←↙↓↘→↗   (duplikaty kierunków, warianty animacji)
#  Grupa D (29-35): ↖↑↗→↘↙←
#  Grupa E (39-44): ↙←↖↑↗→
#  Grupa F (48-52): ↖↑↗↙↙
#  Grupa G (56-61): ↙←↖↑↗→
#
#  Wybieram grupę B (11-16) i D (29-35) jako najczytelniejsze
#  bo mają pełne 8 kierunków w ciągłym bloku.
#
#  JEŚLI stopa jest ODWRÓCONA lub W ZŁYM KIERUNKU:
#  Zmień numer po prawej stronie na inny z tej samej grupy.
#  Np. góra to 12 — jeśli zła, spróbuj 30, 42, 49, 59
 
# ================================================================
#  SYSTEM STYKÓW — każdy kafel trasy zna kierunek SKĄD i DOKĄD
#
#  Klucz: (skąd_dx, skąd_dy, dokąd_dx, dokąd_dy)
#  Czyli: z jakiego kierunku przyszedłem + w jaki kierunek idę
#
#  Przykład: (1,0, 1,0) = szedłem w prawo i dalej idę w prawo → prosta linia
#            (0,1, 1,0) = szedłem w dół, teraz skręcam w prawo → zakręt
#
#  skąd/dokąd to wartości -1, 0 lub 1
#
#  CZARNE (dotrę w tej turze) — zmień numery jeśli zła grafika
STEP_BLACK = {
    # Format: (skąd_x, skąd_y, dokąd_x, dokąd_y): numer_pliku
    # Zakręty używają grafiki kierunku DOKĄD (stopa "wchodzi" w nowy kierunek)
 
    # === PROSTO ===
    ( 1, 0,  1, 0):  50,  # prawo → prawo 
    (-1, 0, -1, 0):  22,  # lewo  → lewo  
    ( 0, 1,  0, 1):   4,  # dół   → dół   
    ( 0,-1,  0,-1):  32,  # góra  → góra  
    ( 1, 1,  1, 1):  59,  # skos PD → PD  
    (-1, 1, -1, 1):  13,  # skos LD → LD  
    ( 1,-1,  1,-1):  41,  # skos PG → PG  
    (-1,-1, -1,-1):  31,  # skos LG → LG
 
    # === ZAKRĘTY 90° ===
    ( 1, 0,  0,-1):  16,  # prawo  → góra 
    ( 0, 1,  1, 0):  34,  # dół    → prawo
    (-1, 0,  0, 1):  52,  # lewo   → dół  
    ( 0,-1, -1, 0):   6,  # góra   → lewo 
    ( 1, 0,  0, 1):  20,  # prawo  → dół  
    ( 0,-1,  1, 0):   2,  # góra   → prawo
    (-1, 0,  0,-1):  48,  # lewo   → góra 
    ( 0, 1, -1, 0):  38,  # dół    → lewo 
 
    # === ZAKRĘTY ze skosu ===
    ( 1,-1,  0, 1):  12,  # skos PG → dół 
    (-1, 1,  0,-1):  40,  # skos LD → góra
    ( 1, 1, -1, 0):  30,  # skos PD → lewo
    (-1,-1,  1, 0):  58,  # skos LG → prawo
    ( 1,-1, -1, 0):  14,  # skos PG → lewo
    (-1, 1,  1, 0):  42,  # skos LD → prawo
    ( 1, 1,  0,-1):  24,  # skos PD → góra
    (-1,-1,  0, 1):  60,  # skos LG → dół 
}
 
STEP_RED = {
    # === PROSTO ===
    ( 1, 0,  1, 0): 115,  # prawo → prawo 
    (-1, 0, -1, 0):  87,  # lewo  → lewo  
    ( 0, 1,  0, 1):  69,  # dół   → dół   
    ( 0,-1,  0,-1):  97,  # góra  → góra  
    ( 1, 1,  1, 1): 124,  # skos PD → PD  
    (-1, 1, -1, 1):  78,  # skos LD → LD  
    ( 1,-1,  1,-1): 106,  # skos PG → PG  
    (-1,-1, -1,-1):  96,  # skos LG → LG  
 
    # === ZAKRĘTY 90° ===
    ( 1, 0,  0,-1):  97,  # prawo  → góra 
    ( 0, 1,  1, 0): 115,  # dół    → prawo
    (-1, 0,  0, 1):  69,  # lewo   → dół  
    ( 0,-1, -1, 0):  87,  # góra   → lewo 
    ( 1, 0,  0, 1):  69,  # prawo  → dół  
    ( 0,-1,  1, 0): 115,  # góra   → prawo
    (-1, 0,  0,-1):  97,  # lewo   → góra 
    ( 0, 1, -1, 0):  87,  # dół    → lewo 
 
    # === ZAKRĘTY ze skosu ===
    ( 1,-1,  0, 1):  69,  # skos PG → dół 
    (-1, 1,  0,-1):  97,  # skos LD → góra
    ( 1, 1, -1, 0):  87,  # skos PD → lewo
    (-1,-1,  1, 0): 115,  # skos LG → prawo
    ( 1,-1, -1, 0):  87,  # skos PG → lewo
    (-1, 1,  1, 0): 115,  # skos LD → prawo
    ( 1, 1,  0,-1):  97,  # skos PD → góra
    (-1,-1,  0, 1):  69,  # skos LG → dół 
}
 
#  FALLBACK — pierwszy krok trasy (brak poprzedniego kierunku)
STEP_BLACK_SINGLE = {
    ( 0,-1):  32,   ( 1,-1):  41,   ( 1, 0):  50,
    ( 1, 1):  59,   ( 0, 1):   4,   (-1, 1):  13,
    (-1, 0):  22,   (-1,-1):  31,
}
STEP_RED_SINGLE = {
    ( 0,-1):  97,   ( 1,-1): 106,   ( 1, 0): 115,
    ( 1, 1): 124,   ( 0, 1):  69,   (-1, 1):  78,
    (-1, 0):  87,   (-1,-1):  96,
}
 
# ================================================================
#  USTAWIENIA — zmieniaj tu
# ================================================================
 
#  Folder ze stopami — zmień jeśli gdzie indziej
STEP_FOLDER = os.path.join("assets", "STEP_S32")
 
#  Rozmiar stopy na ekranie (oryginał: 64x64)
#  Zwiększ żeby były bardziej widoczne, zmniejsz jeśli za duże
STEP_DISPLAY_SIZE = (32, 32)
 
#  63 i 129 to pliki z X (cel/znacznik) — na razie nieużywane
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
 
        objects       = load_fac_objects(fac_file)
        castle_places = objects.get("zamek_place", [])
        built_indices = objects.get("zbudowano_zamek", [0, 1])
 
        w.castles          = []
        w.castle_locations = []
 
        for i, (x, y) in enumerate(castle_places):
            ix, iy = int(x), int(y)
            if i in built_indices:
                owner_id = built_indices[i]
                if owner_id < len(w.players):
                    c = Castle(ix, iy, w.players[owner_id])
                    c.gold = 20000
                    w.castles.append(c)
                else:
                    w.castle_locations.append((ix, iy))
            else:
                w.castle_locations.append((ix, iy))
 
        print(f"Zbudowano zamków: {len(w.castles)}")
        print(f"Miejsc pod budowę: {len(w.castle_locations)}")
 
    # -------------------------------------------------------
    # POMOCNICZE
    # -------------------------------------------------------
 
    def get_tile_at(self, x, y):
        if 0 <= y < len(self.world.map) and 0 <= x < len(self.world.map[y]):
            return self.world.map[y][x]
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
 
    def is_walkable(self, x, y, unit=None, target_castle=None):
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
        obj_tile = w.map[y][x]
 
        if obj_tile == "_":
            return True
        if "cost" not in TERRAIN_TYPES.get(bg_tile, {}):
            return False
 
        unwalkable = ["S", "&", "R", "W", "G", "B", "M"]
        if obj_tile != " " and obj_tile in unwalkable:
            return False
 
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
                if not self.is_walkable(nx, ny, unit, target_castle):
                    continue
 
                bg_tile  = w.bg_map[ny][nx]
                obj_tile = w.map[ny][nx]
 
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
                   set(STEP_BLACK_SINGLE.values()) | set(STEP_RED_SINGLE.values())
 
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
        }
        print("[Stopy] Załadowano grafiki kroków.")
 
    # -------------------------------------------------------
    # RYSOWANIE TRASY — STOPY zamiast kropek
    # -------------------------------------------------------
 
    def draw_path_dots(self, screen, unit, path):
        """
        Rysuje stopy wzdłuż trasy.
        Każdy kafel dobiera grafikę na podstawie SKĄD i DOKĄD —
        dzięki temu stopy płynnie łączą się w zakrętach (styki).
        """
        w = self.world
 
        if Pathfinder._step_imgs is None:
            self._load_steps()
 
        imgs        = Pathfinder._step_imgs
        current_x, current_y = unit.x, unit.y
        accumulated_cost = 0
 
        # Budujemy listę kroków z poprzednim i następnym kierunkiem
        # path = [(x0,y0), (x1,y1), ...]
        # Dodajemy pozycję startową żeby móc wyliczyć "skąd"
        full = [(unit.x, unit.y)] + list(path)
 
        for i in range(1, len(full)):
            px, py = full[i]
            prev_x, prev_y = full[i-1]
 
            # Kierunek DOKĄD (obecny krok)
            dx = px - prev_x
            dy = py - prev_y
            to_dir = ((dx > 0) - (dx < 0), (dy > 0) - (dy < 0))
 
            # Kierunek SKĄD (skąd przyszedłem na ten kafel)
            # = odwrotność kierunku poprzedniego kroku
            if i >= 2:
                ppx, ppy = full[i-2]
                fdx = prev_x - ppx
                fdy = prev_y - ppy
                from_dir = ((fdx > 0) - (fdx < 0), (fdy > 0) - (fdy < 0))
            else:
                from_dir = None  # pierwszy krok — brak poprzedniego
 
            # Koszt kroku
            tile_char = w.map[py][px]
            base_cost = TERRAIN_TYPES.get(tile_char, {}).get("cost", 4)
            move_mod  = 1.41 if (dx != 0 and dy != 0) else 1.0
            accumulated_cost += base_cost * move_mod
 
            in_range = accumulated_cost <= unit.move_points
            pairs    = imgs["black"]        if in_range else imgs["red"]
            singles  = imgs["black_single"] if in_range else imgs["red_single"]
 
            # Szukamy grafiki — najpierw para (styk), potem pojedynczy kierunek
            img = None
            if from_dir is not None:
                key = (from_dir[0], from_dir[1], to_dir[0], to_dir[1])
                img = pairs.get(key)
            if img is None:
                img = singles.get(to_dir)
 
            # Pozycja na ekranie — środek kafla
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
                # Ostateczny fallback: kółko
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
        if bg_terrain in ["l", "g", "G", "W", "M", "B", "b"]: 
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
