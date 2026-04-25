import heapq
import pygame
from settings import TERRAIN_TYPES, MAP_WIDTH, TILE_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH
from map_loader import load_fac_objects
from castle import Castle


class Pathfinder:
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

    def get_tile_at(self, x, y):
        if 0 <= y < len(self.world.map) and 0 <= x < len(self.world.map[y]):
            return self.world.map[y][x]
        return " "    

    def get_bg_tile_at(self, x, y):
        """Pobiera kafelek tła, całkowicie odporna na błędy wyjścia poza mapę."""
        if 0 <= y < len(self.world.bg_map) and 0 <= x < len(self.world.bg_map[y]):
            return self.world.bg_map[y][x]
        return None # Domyślnie udaje trawę poza mapą

    def is_tile_passable(self, x, y, unit_type):
        tile = self.world.map[y][x]
        if tile == "W":
            return unit_type == "ship" # Tylko statki
        if tile == "V":
            return False # Wodospad blokuje wszystkich (chyba że masz latające jednostki)
        return True

    def check_collision(self, x, y):
        tile = self.world.map[y][x]        
        if tile == "W" or tile == "V":
            return True # Jest kolizja (woda/wodospad blokuje ruch lądowy)
        return False


    # -------------------------------------------------------
    # POMOCNICZE
    # -------------------------------------------------------

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
    # RYSOWANIE ŚCIEŻKI
    # -------------------------------------------------------

    def draw_path_dots(self, screen, unit, path):
        w = self.world
        current_x, current_y = unit.x, unit.y
        accumulated_cost = 0

        for px, py in path:
            dx = px - current_x
            dy = py - current_y

            tile_char    = w.map[py][px]
            terrain_info = TERRAIN_TYPES.get(tile_char, {})
            base_cost    = terrain_info.get("cost", 4)
            move_mod     = 1.41 if (dx != 0 and dy != 0) else 1.0
            accumulated_cost += base_cost * move_mod

            dot_x = (px * TILE_SIZE) + (TILE_SIZE // 2) - w.camera_x
            dot_y = (py * TILE_SIZE) + (TILE_SIZE // 2) - w.camera_y

            color = (0, 0, 0) if accumulated_cost <= unit.move_points else (255, 0, 0)

            if -20 < dot_x < SCREEN_WIDTH + 20 and -20 < dot_y < SCREEN_HEIGHT + 20:
                pygame.draw.circle(screen, (255, 255, 255), (dot_x, dot_y), 5)
                pygame.draw.circle(screen, color, (dot_x, dot_y), 4)

            current_x, current_y = px, py

    def draw_road_arrows(self, screen):
        w = self.world
        u = w.selected_unit
        if not u:
            return

        font = pygame.font.SysFont("Arial", 20)
        directions = [(0, -1, "↑"), (0, 1, "↓"), (-1, 0, "←"), (1, 0, "→")]

        for dx, dy, symbol in directions:
            tx, ty = u.x + dx, u.y + dy
            if self.can_build_road(tx, ty):
                pos_x = tx * TILE_SIZE - w.camera_x
                pos_y = ty * TILE_SIZE - w.camera_y
                rect  = pygame.Rect(pos_x + 4, pos_y + 4, 24, 24)
                pygame.draw.rect(screen, (200, 200, 200), rect)
                txt = font.render(symbol, True, (0, 0, 0))
                screen.blit(txt, (pos_x + 6, pos_y + 4))

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
        if not (0 <= y < len(self.world.map) and 0 <= x < len(self.world.map[0])): return False
        terrain = self.world.map[y][x]
        # Blokada: l (las), g (niskie góry), G (wysokie góry), W (woda)
        if terrain in ["l", "g", "#", "&","S","x","B","b", "G", "W"]: return False
        # Nie budujemy na budynkach (duże litery) ani innych pułapkach
        if terrain == "X" or (terrain.isupper() and terrain not in ["P"]): return False
        return True           
            
    def can_build_road(self, x, y):
        # gdzie można budować drogę
        if not (0 <= y < len(self.world.map) and 0 <= x < len(self.world.map[0])):
            return False
        
        terrain = self.world.map[y][x]
        # Lista zakazana według Twoich wytycznych
        forbidden = ["l", "g", "#", "&", "S", "x", "B", "b", "G", "W"]
        
        if terrain in forbidden:
            return False
            
        # Nie budujemy na już istniejącej drodze (chyba że chcesz naprawiać?)
        if terrain == "_":
            return False
            
        return True
