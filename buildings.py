import pygame
import re
from castle import Castle, BUILDING_TYPES
from unit import Unit
from settings import UNIT_STATS, UNIT_NAMES

# =====================================================
#   BUILDINGS.PY
#   Metody klasy World dotyczące budynków i zamków.
#   Wszystkie funkcje tu są metodami World —
#   wklejasz je do klasy World w world.py
#   LUB importujesz przez mixin (patrz niżej).
# =====================================================

class BuildingsMixin:
    """
    Mixin z metodami budowlanymi dla klasy World.
    Użycie:
        class World(BuildingsMixin, ...):
            pass
    """

    def load_castles_from_fac(self, fac_path):
        with open(fac_path, 'r') as f:
            content = f.read()

        all_places   = re.findall(r"\(zamek_place (\d+) (\d+)\)", content)
        built_indices = [int(i) for i in re.findall(r"\(zbudowano zamek (\d+)\)", content)]
        print(f"DEBUG: Zbudowane zamki: {built_indices}")

        self.castles          = []
        self.castle_locations = []

        for i, (x, y) in enumerate(all_places):
            ix, iy = int(x), int(y)
            if i in built_indices:
                self.castles.append(Castle(ix, iy))
            else:
                self.castle_locations.append((ix, iy))

    def load_castle_and_tower(self):
        base_folder = r"assets\zamekczerwony\BUILDIN1_S32_"
        TARGET_SIZE = (32, 32)

        self.castle_tiles = {0: [], 1: [], 2: [], 3: [], 4: []}
        for stage in range(4):
            for i in range(4):
                file_num = 225 + (stage * 4) + i
                try:
                    img = pygame.image.load(f"{base_folder}{file_num}.png").convert_alpha()
                    img = pygame.transform.scale(img, TARGET_SIZE)
                    self.castle_tiles[stage].append(img)
                except:
                    print(f"Brak pliku zamku: {file_num}")

        for i in range(4):
            try:
                img = pygame.image.load(f"{base_folder}{257 + i}.png").convert_alpha()
                self.castle_tiles[4].append(pygame.transform.scale(img, TARGET_SIZE))
            except:
                pass

        self.tower_tiles = {}
        for i in range(4):
            try:
                img = pygame.image.load(f"{base_folder}{i}.png").convert_alpha()
                self.tower_tiles[i] = pygame.transform.scale(img, TARGET_SIZE)
            except:
                print(f"Brak pliku strażnicy: {i}")

        try:
            img = pygame.image.load(f"{base_folder}8.png").convert_alpha()
            self.tower_tiles[4] = pygame.transform.scale(img, TARGET_SIZE)
        except:
            print("Brak pliku zniszczonej strażnicy (8.png)")

    def demolish_castle(self, castle):
        if not castle:
            return

        all_units = [u for u in castle.garrison if u is not None]
        if all_units:
            groups       = [all_units[:10], all_units[10:]]
            spawn_points = self.find_multiple_spawn_positions(
                castle, len([g for g in groups if g]))

            for i, group in enumerate(groups):
                if group and spawn_points[i]:
                    nx, ny    = spawn_points[i]
                    new_army  = Unit(group[0].type, nx, ny, castle.owner)
                    new_army.garrison = [None] * 10
                    for j, u in enumerate(group):
                        new_army.garrison[j] = u
                    self.units.append(new_army)
                    castle.owner.units.append(new_army)

        castle.destroyed = True
        if castle.owner and castle in castle.owner.castles:
            castle.owner.castles.remove(castle)
        castle.owner    = None
        castle.garrison = [None] * 12

        self.demolish_confirm = False
        self.screen = "map"
        print("Zamek stał się ruiną.")

    def process_construction(self):
        for castle in self.castles:
            if not getattr(castle, 'under_construction', False):
                continue

            builders_count = sum(
                1 for slot in castle.garrison
                if slot and slot.type == "Budowniczy")

            if builders_count > 0:
                castle.work_done    += builders_count
                castle.mury_percent  = min(
                    100, int((castle.work_done / castle.total_work_needed) * 100))
                print(f"Budowa {castle.building_type}: {castle.mury_percent}% murów.")

            if castle.work_done >= castle.total_work_needed:
                castle.under_construction = False
                castle.mury_percent       = 100
                sym  = "H" if castle.building_type == "Strażnica" else "C"
                size = 2 if castle.building_type in ["Twierdza", "Zamek"] else 1
                for dy in range(size):
                    for dx in range(size):
                        self.map[castle.y + dy][castle.x + dx] = sym
                print(f"Budowa ukończona: {castle.building_type}!")

    def start_recruitment(self, index):
        if index is None:
            return
        utype  = list(UNIT_STATS.keys())[index]
        cost   = 50
        castle = self.selected_castle

        if castle.gold < cost:
            print("Za mało złota")
            return

        castle.gold -= cost
        castle.start_production(utype)
        print(f"Rozpoczęto produkcję: {utype}")
        self.screen = "garrison"

    def train_selected(self, castle):
        for unit in self.selected_units:
            castle.start_training(unit)
        self.selected_units.clear()

    def recruit_unit(self):
        if not self.selected_castle:
            print("Nie wybrano zamku")
            return
            
        castle = self.selected_castle # Używamy skarbu zamku
        if len(castle.garrison) >= 12:
            print("Zamek jest pełny")
            return

        if not self.selected_recruit_unit:
            print("Nie wybrano jednostki do rekrutacji")
            return

        player = self.players[self.current_player]
        unit_code = self.selected_recruit_unit 
        full_name = UNIT_NAMES.get(unit_code, "Nieznany")
        unit_data = UNIT_STATS.get(full_name, {})
        cost = unit_data.get("production_cost", 0)

        # KLUCZOWA ZMIANA: Sprawdzamy złoto w zamku, nie u gracza
        if castle.gold < cost:
            print(f"Za mało złota w zamku! Potrzeba {cost}, masz {castle.gold}")
            return

        # Odejmowanie złota ze skarbca zamku
        castle.gold -= cost

        u = Unit(unit_code, castle.x, castle.y, player)
        castle.add_to_garrison(u)
        print(f"Zrekrutowano {full_name} w zamku ({castle.x}, {castle.y})")
        
    def train_selected_garrison_units(self):
        if not self.selected_castle or not self.selected_units:
            print("Błąd: Nie wybrano zamku lub jednostek!")
            return

        # Wykonaj szkolenie
        for unit in list(self.selected_units):
            self.selected_castle.start_training(unit)
        
        # WAŻNE: Nie czyść listy, jeśli chcesz widzieć, że jednostki zniknęły 
        # (przeszły do slotów treningowych) w tym samym widoku.
        self.selected_units.clear()

    def castle_has_patent(self, castle, unit_name):
        for p in castle.patents:
            if isinstance(p, dict) and p["unit_type"] == unit_name:
                return True
            if p == unit_name:
                return True
        return False

    def destroy_straznica(self, castle):

        """Niszczy strażnicę, tworzy jedną armię z jej załogi i zostawia ruiny."""
        from unit import Unit  # Import lokalny, żeby uniknąć problemów
        
        # 1. Sprawdzamy czy w środku ktoś jest
        units_in_garrison = [u for u in castle.garrison if u is not None]
        
        if units_in_garrison:
            print("Ewakuacja: Formowanie armii z garnizonu...")
            
            # Szukamy miejsca wokół strażnicy dla JEDNEJ armii
            spawn_pos = self.find_free_space_around(castle.x, castle.y)
            if spawn_pos:
                nx, ny = spawn_pos
                
                # Tworzymy nową jednostkę-matkę (lidera armii)
                # Jako typ bierzemy typ pierwszej jednostki z garnizonu
                leader_type = units_in_garrison[0].type
                new_army = Unit(leader_type, nx, ny, castle.owner)
                new_army.garrison = [None] * 10
                
                # Przepisujemy jednostki ze slotów strażnicy do slotów nowej armii
                for i, u in enumerate(units_in_garrison):
                    if i < 10:
                        new_army.garrison[i] = u
                
                # Dodajemy nową armię do gry
                self.units.append(new_army)
                castle.owner.units.append(new_army)
                print(f"Armia ewakuowana na pole {nx, ny}")
            else:
                print("Brak miejsca wokół! Garnizon zginął w gruzach.")

        # 2. Usuwamy budynek i zostawiamy ruiny
        if castle in self.castles:
            self.castles.remove(castle)
        
        # Zmieniamy kafel na 'R' (Ruiny)
        self.map[castle.y][castle.x] = "R"
        
        self.selected_castle = None
        self.screen = "map"
        return True
 
    def start_building(self, x, y, b_type, builder=None):
        if b_type not in BUILDING_TYPES:
            return False
        config = BUILDING_TYPES[b_type]

        ix, iy = int(x), int(y)
        anchor_x, anchor_y = ix, iy
        found_foundation = False

        if config.get("size") == 2:
            for dx in [0, -1]:
                for dy in [0, -1]:
                    nx, ny = ix + dx, iy + dy
                    if 0 <= nx < len(self.map[0]) and 0 <= ny < len(self.map):
                        if self.map[ny][nx] == "#":
                            anchor_x, anchor_y = nx, ny
                            found_foundation = True
                            break
                if found_foundation:
                    break
            if not found_foundation:
                print("BŁĄD: Zamek/Twierdza wymaga fundamentów (#)!")
                return False
        else:
            # Strażnica (size 1) - Naprawione odwołanie do pathfindera
            if self.map[iy][ix] in [".", "p", "P", "s"] and \
               not getattr(self.pathfinder, 'is_area_occupied_by_foundation', lambda x,y: False)(ix, iy):
                found_foundation = True
            else:
                print(f"BŁĄD: Strażnica wymaga czystego terenu! Aktualnie jest tu: '{self.map[iy][ix]}'")
                return False

        new_castle = Castle(anchor_x, anchor_y, self.current_player,
                            building_type=b_type)
        new_castle.under_construction = True
        new_castle.total_work_needed  = 12.0
        new_castle.work_done          = 0.0
        new_castle.mury_percent       = 0

        army = self.get_unit_at(ix, iy)
        if army:
            self.enter_castle(army, new_castle)

        self.castles.append(new_castle)

        size = 2 if config.get("size") == 2 else 1
        for dy in range(size):
            for dx in range(size):
                self.map[anchor_y + dy][anchor_x + dx] = "P"

        print(f"Rozpoczęto budowę {b_type}.")
        return True

    def execute_build_action(self, button_index, army):
        if not army: return
        grid_x, grid_y = int(army.x), int(army.y)

        def get_builder(a):
            if getattr(a, 'type', None) == "Budowniczy":
                return a
            if hasattr(a, 'garrison'):
                for slot in a.garrison:
                    if slot and getattr(slot, 'type', None) == "Budowniczy":
                        return slot
            return None

        builder = get_builder(army)
        if not builder:
            print("Brak Budowniczego w armii!")
            return

        # ===============================================
        # NOWOŚĆ: Wyzerowanie trasy marszu i zniknięcie stóp
        # ===============================================
        army.planned_path = []
        army.target_x = None
        army.target_y = None

        # 1. DROGA (Indeks 0) - WŁĄCZ / WYŁĄCZ
        if button_index == 0:           
            if getattr(self, 'road_build_mode', False):
                self.road_build_mode = False 
                self.build_menu_open = False # Odkliknięcie = powrót do 6 przycisków
                print("Wyłączono tryb budowy drogi.")
            else:
                if army.move_points >= 5:
                    self.road_build_mode = True
                    self.trap_build_mode = False 
                    # ZOSTWIAMY MENU OTWARTE! (żeby się świeciło)
                    print("Włączono tryb budowy drogi.")
                else:
                    print("Za mało punktów ruchu!")
            return 

        # 2. PUŁAPKA (Indeks 1) - WŁĄCZ / WYŁĄCZ
        elif button_index == 1:         
            if getattr(self, 'trap_build_mode', False):
                self.trap_build_mode = False 
                self.build_menu_open = False # Odkliknięcie = powrót do 6 przycisków
                print("Wyłączono tryb budowy pułapki.")
            else:
                self.trap_build_mode = True
                self.road_build_mode = False 
                self.active_builder_army = army
                self.active_builder_unit = builder
                # ZOSTWIAMY MENU OTWARTE!
                print("Wybierz pole na pułapkę.")
            return

        # 3. SKARB (Indeks 2)
        elif button_index == 2:         
            if self.map[grid_y][grid_x] == "$":
                army.owner.gold += 500
                self.map[grid_y][grid_x] = "."
                print("Skarb zebrany!")
            else:
                print("Tu nie ma żadnego skarbu.")
            
            # Zawsze czyścimy i wracamy do 6 przycisków
            self.road_build_mode = False
            self.trap_build_mode = False
            self.build_menu_open = False 
            return

        # Pozostałe budynki (Indeksy 3, 4, 5)
        menu_to_type = {3: "Strażnica", 4: "Twierdza", 5: "Zamek"}
        if button_index in menu_to_type:
            building_type = menu_to_type[button_index]
            print(f"Próba budowy: {building_type}")
            
            # Resetujemy strzałki/pułapki na wszelki wypadek
            self.road_build_mode = False
            self.trap_build_mode = False
            
            success = self.start_building(grid_x, grid_y, building_type, builder)
            
            # Po kliknięciu zamku zawsze zamykamy menu budowy
            self.build_menu_open = False
            if success:
                self.selected_unit = None
            return

    def execute_trap_build(self, gx, gy):
        u = self.selected_unit
        dist_x = abs(gx - u.x)
        dist_y = abs(gy - u.y)

        if dist_x <= 1 and dist_y <= 1 and not (dist_x == 0 and dist_y == 0):
            if self.pathfinder.can_build_trap(gx, gy):
                self.trap_backgrounds[(gx, gy)] = self.map[gy][gx]
                self.map[gy][gx] = "X"
                self.remove_unit_or_builder(u, u)
                
                self.trap_build_mode = False
                self.build_menu_open = False # Wraca do 6 przycisków po zbudowaniu
                self.selected_unit = None
                print("Pułapka zastawiona pomyślnie!")
            else:
                print("Zły teren na pułapkę!")
        else:
            print("Poza zasięgiem budowy!")

    def execute_road_build(self, gx, gy):
        u = self.selected_unit
        if u is None: return

        dist_x = abs(gx - u.x)
        dist_y = abs(gy - u.y)

        if (dist_x == 1 and dist_y == 0) or (dist_x == 0 and dist_y == 1):
            if self.pathfinder.can_build_road(gx, gy):
                self.map[u.y][u.x] = "_"
                u.x, u.y = gx, gy
                u.move_points -= 5
                
                if u.move_points < 5:
                    self.road_build_mode = False
                    self.build_menu_open = False # Wraca do 6 przycisków po wyczerpaniu ruchu
                    print("Koniec punktów ruchu. Droga ukończona.")
                else:
                    print("Droga położona. Możesz kontynuować.")
            else:
                print("Tu nie można budować drogi!")
        else:
            print("Buduj drogę na sąsiednim polu (pion/poziom).")

    def handle_building_logic(self, mx, my, gx, gy):
        tile = self.map[gy][gx]
        builder = self.selected_unit # Tutaj już używasz nazwy 'builder'
        mode = getattr(self, "building_mode", None)

        if not builder or builder.type != "Budowniczy":
            return False

        if tile == "#":
            if mode == "Tower":
                print("BŁĄD: Strażnica wymaga wolnego pola!")
                return False
            if mode in ["Zamek", "Twierdza"]:
                # Wywołujemy funkcję, która schowa buildera za nas
                self.start_building(gx, gy, mode, builder)
                return True

        elif tile == ".":
            if mode in ["Zamek", "Twierdza"]:
                print("BŁĄD: Zamek wymaga fundamentów!")
                return False
            if mode == "Tower":
                if self.is_area_occupied_by_foundation(gx, gy):
                    return False
                self.start_building(gx, gy, "Strażnica", builder)
                return True
        return False
            #elif mode == "Foundation":
                # Stawiamy fundamenty pod Zamek/Twierdzę
                #self.map[gy][gx] = "#"
                #print("Postawiono fundamenty (#)")
            # self.building_mode = None
                # Tutaj budowniczy NIE musi znikać, bo to postawienie kafelka, a nie budowa czasowa
                #return True
        return False
     
    def show_foundation_menu(self, gx, gy):
        self.screen = "foundation_selection"
        self.construction_target = (gx, gy) # Zapamiętujemy, gdzie budujemy
    
    def click_on_recruitment(self, mx, my):
        # Sprawdzamy, który z narysowanych slotów został kliknięty
        for i, rect in enumerate(self.unit_list_rects):
            if rect.collidepoint(mx, my):
                return i  # Zwraca numer slotu (0, 1, 2, 3 lub 4)
        return None
  
    def click_on_garrison(self, mx, my):
        castle = self.selected_castle
        if not castle: return None

        rects = getattr(self, 'garrison_slot_rects', 
                        self.garrison_gfx.slot_rects)
        for i, rect in enumerate(rects):
            if rect.collidepoint(mx, my):
                return i
        return None
     
    def handle_peasants_click(self, mx, my):
        if self.back_button.collidepoint(mx, my):
            self.back_destination = "castle"
            self.back_anim_timer = pygame.time.get_ticks()
            return

        if not self.selected_castle:
            return

        print("peasants screen click")

        castle = self.selected_castle

        # ================= SEND AMOUNT =================

        if self.peasants_plus_button.collidepoint(mx, my):
            if self.send_peasants_amount + 10 <= castle.peasants:
                self.send_peasants_amount += 10
            return

        if self.peasants_minus_button.collidepoint(mx, my):
            self.send_peasants_amount = max(0, self.send_peasants_amount - 10)
            return

        if self.gold_plus_button.collidepoint(mx, my):
            if self.send_gold_amount + 10 <= castle.gold:
                self.send_gold_amount += 10
            return

        if self.gold_minus_button.collidepoint(mx, my):
            self.send_gold_amount = max(0, self.send_gold_amount - 10)
            return

        # ================= TAX =================

        if self.tax_plus_button.collidepoint(mx, my):
            castle.tax_rate = min(4.0, castle.tax_rate + 0.1)
            return

        if self.tax_minus_button.collidepoint(mx, my):
            castle.tax_rate = max(0.0, castle.tax_rate - 0.1)
            return

        # ================= SCROLL =================

        owned = [c for c in self.castles if c.owner == self.players[self.current_player]]
        max_offset = max(0, len(owned) - 3)

        if self.castle_up_button.collidepoint(mx, my):
            self.castle_list_offset = max(0, self.castle_list_offset - 1)
            return

        if self.castle_down_button.collidepoint(mx, my):
            self.castle_list_offset = min(max_offset, self.castle_list_offset + 1)
            return

        # ================= SEND =================

        if self.send_button.collidepoint(mx, my):
            if self.send_peasants_amount <= castle.peasants and \
            self.send_gold_amount <= castle.gold:

                castle.peasants -= self.send_peasants_amount
                castle.gold -= self.send_gold_amount

                print("Resources sent!")

                self.send_peasants_amount = 0
                self.send_gold_amount = 0
                     
    def handle_trap_info_click(self, mx, my):
        # W Mixinie 'self' to już jest World, nie potrzebujesz .world!
        
        if hasattr(self, 'btn_trap_stop') and self.btn_trap_stop.collidepoint(mx, my):
            tx, ty = self.active_trap_pos
            original = self.trap_backgrounds.get((tx, ty), ".")
            self.map[ty][tx] = original
            
            if (tx, ty) in self.trap_backgrounds:
                del self.trap_backgrounds[(tx, ty)]
            
            u = getattr(self, 'selected_unit', None)
            if u and u.type == "Budowniczy":
                self.remove_unit_or_builder(u, u)
                self.selected_unit = None
                
            self.screen = "map"

        elif hasattr(self, 'btn_trap_dalej') and self.btn_trap_dalej.collidepoint(mx, my):
            self.screen = "map"

    def handle_castle_click(self, mx, my):
        if not self.selected_castle: return
        castle = self.selected_castle
        built = set(b.lower() for b in castle.buildings)

        # 1. MENU BUDOWANIA (Najwyższy priorytet)
        if getattr(self, 'menu_open', False):
            # NAJPIERW: Sprawdzamy główne menu (ZBURZ ZAMEK itp.)
            for name, rect in getattr(self, 'menu_rects', {}).items():
                if rect.collidepoint(mx, my):
                    if name == "ZBURZ ZAMEK":
                        self.demolish_confirm = True # Aktywujemy okienko!
                        self.menu_open = False
                        return
                        
            # POTEM: Sprawdzamy opcje budowania
            for name, rect in getattr(self, 'build_rects', {}).items():
                if rect.collidepoint(mx, my):
                    if castle.build(name):
                        self.menu_open = False
                    return
            return

        # 2. PRZYCISKI SYSTEMOWE
        if hasattr(self, 'back_button_castle') and self.back_button_castle.collidepoint(mx, my): 
            self.screen = "map"
            self.selected_castle = None
            return  
            
        if hasattr(self, 'menu_button') and self.menu_button.collidepoint(mx, my):
            self.menu_open = not getattr(self, 'menu_open', False)
            return

        # 3. MASKA KOLORÓW - jedyne źródło prawdy o kliknięciu w budynek
        if hasattr(self, 'castle_gfx'):
            clicked_id = self.castle_gfx.get_building_at_pos(mx, my, castle)
        else:
            print("Błąd: brak castle_gfx! Upewnij się, że inicjujesz CastleGraphics.")
            return

        if not clicked_id:
            return  # kliknięto w puste miejsce

        if clicked_id in ("garrison", "koszary"):
            self.screen = "garrison"
        elif clicked_id == "peasants":
            self.screen = "peasants"
        elif clicked_id == "court":
            self.screen = "court"
        elif clicked_id in ("hospital", "workshop", "forge", "school"):
            if clicked_id in built:
                self.screen = clicked_id
            else:
                print(f"Budynek '{clicked_id}' nie jest jeszcze zbudowany.")

    def handle_garrison_click(self, mx, my, button):
        castle = self.selected_castle
        if not castle:
            return

        # ================= BACK =================
        if hasattr(self, 'back_button_castle') and self.back_button_castle.collidepoint(mx, my):
            self.selected_units.clear()
            self.screen = "castle"
            return

        # ================= RECRUITMENT (Poprawione) =================
        if self.garrison_gfx.handle_prod_click(mx, my, castle):
            self.screen = "recruitment"
            self.recruitment_open = True
            self.recruitment_scroll = -2  
            self.selected_unit_type = 0   
            self.selected_patent_index = None
            return

        # ================= HEAL =================
        if "hospital" in castle.buildings and hasattr(self, 'heal_button') and self.heal_button.collidepoint(mx, my):
            for unit in self.selected_units:
                castle.start_healing_unit(unit)
            return

        # ================= TRAIN ================= 
        if "school" in castle.buildings and hasattr(self, 'train_button') and self.train_button.collidepoint(mx, my):
            if self.selected_units:
                castle.start_training_group(self.selected_units) 
                self.selected_units.clear() 
                print("Zakończono wydawanie rozkazów szkolenia")
            else:
                print("Brak zaznaczonych jednostek do szkolenia")
            return
            
        # ================= WYŚLIJ WOJSKO (Poprawione) ======================
        if self.garrison_gfx.handle_release_click(mx, my, self.selected_units):
            self.release_selected_units()
            return
        
        # ================= PRZYCISKI STRAŻNICY =================
        is_release = False
        if hasattr(self, 'release_tower') and isinstance(self.release_tower, pygame.Rect):
            if self.release_tower.collidepoint(mx, my):
                is_release = True
        if is_release:
            self.release_selected_units()
            return

        if hasattr(self, 'destroy_button') and self.destroy_button.collidepoint(mx, my):
            if self.selected_castle and self.selected_castle.building_type == "Strażnica":
                self.destroy_straznica(self.selected_castle)
                return

        # ================= SELEKCJA JEDNOSTEK W SLOTACH =================
        index = self.click_on_garrison(mx, my)
        if index is None or index >= len(self.selected_castle.garrison):
            return

        unit = self.selected_castle.garrison[index]

        # --- PRAWY PRZYCISK: Statystyki ---
        if button == 3: 
            if unit is not None:
                self.inspected_unit = unit  
            else:
                self.inspected_unit = None
            return

        # --- LEWY PRZYCISK: Zaznaczanie ---
        if button == 1:
            self.inspected_unit = None
            if unit is None:
                return

            if unit in self.selected_units:
                self.selected_units.remove(unit)
            else:
                if len(self.selected_units) < getattr(self.selected_castle, 'garrison_limit', 12):
                    self.selected_units.append(unit)
                else:
                    print("DEBUG: Garnizon jest pełen!")

    if __name__ == "__main__":
        import subprocess, sys, os
        main_path = os.path.join(os.path.dirname(__file__), "main.py")
        subprocess.run([sys.executable, main_path])