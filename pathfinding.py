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
 
STEP_BLACK = {
    # (dx, dy) : numer_pliku    # kierunek    # alternatywy z innych grup
    ( 0, -1):  32,  # góra          
    ( 1, -1):  41,  # góra-prawo    
    ( 1,  0):  50,  # prawo         
    ( 1,  1):  59,  # dół-prawo     
    ( 0,  1):   4,  # dół           
    (-1,  1):  13,  # dół-lewo      
    (-1,  0):  22,  # lewo          
    (-1, -1):  31,  # góra-lewo     
}
 
STEP_RED = {
    # Czerwone zaczynają się od 67, ta sama kolejność co czarne
    # (dx, dy) : numer_pliku    # kierunek    # alternatywy
    ( 0, -1):  97,  # góra        ← spróbuj: 97, 112
    ( 1, -1): 106,  # góra-prawo  ← spróbuj: 98, 113
    ( 1,  0): 115,  # prawo       ← spróbuj: 99, 114
    ( 1,  1): 124,  # dół-prawo   ← spróbuj: 100
    ( 0,  1):  69,  # dół         ← spróbuj: 71, 88
    (-1,  1):  78,  # dół-lewo    ← spróbuj: 72, 86, 95
    (-1,  0):  87,  # lewo        ← spróbuj: 87, 96
    (-1, -1):  96,  # góra-lewo   ← spróbuj: 76, 96, 106
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
        Ładuje grafiki stóp jeden raz.
        Przy błędnym kierunku zmień numer w STEP_BLACK / STEP_RED na górze pliku.
        Fallback = stare kółko jeśli plik nie istnieje.
        """
        def load_one(number, fallback_color):
            path = os.path.join(STEP_FOLDER, f"STEP_S32_{number}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, STEP_DISPLAY_SIZE)
            else:
                print(f"[Stopy] BRAK: STEP_S32_{number}.png — używam kółka")
                surf = pygame.Surface(STEP_DISPLAY_SIZE, pygame.SRCALPHA)
                cx = STEP_DISPLAY_SIZE[0] // 2
                cy = STEP_DISPLAY_SIZE[1] // 2
                r  = STEP_DISPLAY_SIZE[0] // 3
                pygame.draw.circle(surf, (255, 255, 255), (cx, cy), r + 1)
                pygame.draw.circle(surf, fallback_color,  (cx, cy), r)
                return surf
 
        black_imgs = {d: load_one(n, (20, 20, 20))    for d, n in STEP_BLACK.items()}
        red_imgs   = {d: load_one(n, (220, 30, 30))   for d, n in STEP_RED.items()}
 
        Pathfinder._step_imgs = {"black": black_imgs, "red": red_imgs}
        print("[Stopy] Załadowano grafiki kroków.")
 
    # -------------------------------------------------------
    # RYSOWANIE TRASY — STOPY zamiast kropek
    # -------------------------------------------------------
 
    def draw_path_dots(self, screen, unit, path):
        w = self.world
 
        if Pathfinder._step_imgs is None:
            self._load_steps()
 
        black_imgs = Pathfinder._step_imgs["black"]
        red_imgs   = Pathfinder._step_imgs["red"]
 
        current_x, current_y = unit.x, unit.y
        accumulated_cost = 0
 
        for px, py in path:
            dx = px - current_x
            dy = py - current_y
 
            # Koszt kroku
            tile_char = w.map[py][px]
            base_cost = TERRAIN_TYPES.get(tile_char, {}).get("cost", 4)
            move_mod  = 1.41 if (dx != 0 and dy != 0) else 1.0
            accumulated_cost += base_cost * move_mod
 
            # Pozycja na ekranie — środek kafla
            screen_x = px * TILE_SIZE + TILE_SIZE // 2 - w.camera_x
            screen_y = py * TILE_SIZE + TILE_SIZE // 2 - w.camera_y
 
            # Poza ekranem — pomijamy
            margin = TILE_SIZE * 2
            if not (-margin < screen_x < SCREEN_WIDTH  + margin and
                    -margin < screen_y < SCREEN_HEIGHT + margin):
                current_x, current_y = px, py
                continue
 
            # Kierunek → normalizujemy do -1/0/1
            direction = ((dx > 0) - (dx < 0), (dy > 0) - (dy < 0))
 
            in_range = accumulated_cost <= unit.move_points
            img      = (black_imgs if in_range else red_imgs).get(direction)
 
            if img:
                blit_x = screen_x - img.get_width()  // 2
                blit_y = screen_y - img.get_height() // 2
                screen.blit(img, (blit_x, blit_y))
            else:
                # Fallback: stare kółka
                color = (0, 0, 0) if in_range else (255, 0, 0)
                pygame.draw.circle(screen, (255, 255, 255), (screen_x, screen_y), 5)
                pygame.draw.circle(screen, color,           (screen_x, screen_y), 4)
 
            current_x, current_y = px, py
 
    # -------------------------------------------------------
    # STRZAŁKI BUDOWY DROGI
    # -------------------------------------------------------
 
    def _load_arrows(self):
        arrow_files = {
            (0, -1): "assets/MAP_BUTT_S32_27.png",  # góra
            (-1, 0): "assets/MAP_BUTT_S32_28.png",  # lewo
            (0,  1): "assets/MAP_BUTT_S32_29.png",  # dół
            (1,  0): "assets/MAP_BUTT_S32_30.png",  # prawo
        }
        imgs = {}
        for direction, path in arrow_files.items():
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                imgs[direction] = img
            else:
                print(f"[Strzałki] BRAK: {path}")
                surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                surf.fill((200, 200, 200, 180))
                imgs[direction] = surf
        Pathfinder._arrow_imgs = imgs
 
    def draw_road_arrows(self, screen):
        w = self.world
        u = w.selected_unit
        if not u:
            return
 
        if Pathfinder._arrow_imgs is None:
            self._load_arrows()
 
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            tx, ty = u.x + dx, u.y + dy
            if not w.can_build_road(tx, ty):
                continue
 
            pos_x = tx * TILE_SIZE - w.camera_x
            pos_y = ty * TILE_SIZE - w.camera_y
 
            if pos_x < -TILE_SIZE or pos_x > SCREEN_WIDTH or \
               pos_y < -TILE_SIZE or pos_y > SCREEN_HEIGHT:
                continue
 
            img = Pathfinder._arrow_imgs.get((dx, dy))
            if img:
                offset_x = (TILE_SIZE - img.get_width())  // 2
                offset_y = (TILE_SIZE - img.get_height()) // 2
                screen.blit(img, (pos_x + offset_x, pos_y + offset_y))

if __name__ == "__main__":
    import subprocess, sys, os
    main_path = os.path.join(os.path.dirname(__file__), "main.py")
    subprocess.run([sys.executable, main_path])