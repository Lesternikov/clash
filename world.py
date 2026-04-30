from unit import Unit
from castle import Castle, UNIT_REQUIREMENTS
from player import Player
from buildings import BuildingsMixin
from castle import BUILDING_TYPES
import random  # Do losowania drzew (żeby las nie był nudny)
import pygame  # Silnik gry
from settings import UNIT_STATS, UNIT_NAMES, TERRAIN_TYPES, MAP_HEIGHT, MAP_WIDTH, TILE_SIZE, COLOR_TO_ID, SCREEN_HEIGHT, SCREEN_WIDTH
from court import CourtHandler
from controls import ControlsHandler
from UI_components import UnitInfoWindow  
from castle_graphics import CastleGraphics
from garrison_graphics import GarrisonGraphics
from recruitment import RecruitmentManager
from peasant_menu import PeasantMenu

@property
def back_button(self):
    if self.screen == "castle":
        return self.back_button_castle
    return self.back_button_bldg

class World(BuildingsMixin):
    def __init__(self):
        # ====================================================
        # 1. GŁÓWNE ZMIENNE STANU GRY
        # ====================================================
        self.screen = "map"
        self.turn = 1
        self.current_player = 0
        
        self.selected_castle = None
        self.selected_unit = None
        self.inspected_unit = None
        self.selected_units = []

        self.map = []
        self.units = []
        self.castles = []
        self.castle_locations = []
        self.peasant_groups = []
        self.gold_transports = []
        self.players = []

        self.camera_x = 0
        self.camera_y = 0

        # Tryby budowy dróg i pułapek
        self.trap_build_mode = False
        self.road_build_mode = False
        self.build_menu_open = False
        self.menu_open = False
        self.active_dropdown = None

        self.traps = []
        self.trap_backgrounds = {}    
        self.constructions = []
        self.build_clicked = {}  

        self.show_grid = False
        self.show_top_ui = False
        self.merge_mode = False  # Tryb łączenia jednostek
        # ====================================================
        # 2. INICJALIZACJA MENEDŻERÓW I KLAS POMOCNICZYCH
        # ====================================================
        w = pygame.display.get_surface().get_width()
        h = pygame.display.get_surface().get_height()
        
        self.castle_gfx = CastleGraphics(w, h)
        self.garrison_gfx = GarrisonGraphics(w, h)
        self.unit_info_window = UnitInfoWindow()
        self.court = CourtHandler(self)
        self.recruitment_manager = RecruitmentManager(self)
        self.peasant_menu = PeasantMenu(w, h)
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 24)
        self.font_small = pygame.font.SysFont(None, 20)
        self.modal_font = pygame.font.SysFont(None, 32)
        self.btn_font = pygame.font.SysFont(None, 28, bold=True)

        # ====================================================
        # 3. INTERFEJS I PRZYCISKI
        # ====================================================
        # Uniwersalny przycisk powrotu i jego animacja
        self.back_button_castle = pygame.Rect(45, 690, 130, 74)
        self.back_button_bldg   = pygame.Rect(68, 680, 150, 80)
        self.back_button        = self.back_button_bldg
        self.back_anim_timer    = 0
        self.back_destination   = "map"
        
        try:
            self.back_img_castle_normal  = pygame.transform.scale(pygame.image.load("assets/back_castlen.png").convert_alpha(), (130, 74))
            self.back_img_castle_pressed = pygame.transform.scale(pygame.image.load("assets/back_castlec.png").convert_alpha(), (130, 74))
            self.back_img_bldg_normal    = pygame.transform.scale(pygame.image.load("assets/back_normal.png").convert_alpha(),  (150, 80))
            self.back_img_bldg_pressed   = pygame.transform.scale(pygame.image.load("assets/back_clicked.png").convert_alpha(), (150, 80))
            print("Grafiki przycisku powrotu załadowane!")
        except Exception as e:
            print(f"Błąd grafik przycisku: {e}")
            dummy = pygame.Surface((130, 74))
            dummy.fill((140, 80, 80))
            self.back_img_castle_normal  = dummy
            self.back_img_castle_pressed = dummy
            self.back_img_bldg_normal    = dummy
            self.back_img_bldg_pressed   = dummy

        # MENU GÓRNE (Mapa)
        self.btn_system = pygame.Rect(10, 0, 100, 40)
        self.btn_mapa = pygame.Rect(115, 0, 100, 40)
        self.next_turn_button = pygame.Rect(w - 220, 0, 200, 45)
        self.top_ui_trigger_area = pygame.Rect(0, 0, w, 10)
        self.top_ui_full_area = pygame.Rect(0, 0, w, 55)

        # MENU ROZWIJANE (Kontekstowe)
        self.menu_rects = {}
        self.build_rects = {}
        self.menu_options = {
            "System": ["Misja", "Poddanie się", "Zapisz grę", "Wczytaj grę", "Opcje", "Koniec"],
            "Mapa": ["Wszystko", "Budynki", "Jednostki", "Nic"]
        }

        # EKRAN GŁÓWNY ZAMKU
        self.garrison_button = pygame.Rect(80, 630, 160, 40)
        self.court_button = pygame.Rect(420, 100, 160, 40)
        self.peasant_button = pygame.Rect(w - 200, h - 110, 160, 40)
        self.menu_button = pygame.Rect(w - 180, 40, 140, 40)

        # EKRAN GARNIZONU / KOSZAR
        self.recruit_button = pygame.Rect(260, 600, 120, 40)
        self.heal_button = pygame.Rect(460, 600, 120, 40)
        self.train_button = pygame.Rect(660, 600, 120, 40)
        self.button_send_army = pygame.Rect(860, 600, 150, 40)
        self.destroy_button = pygame.Rect(0, 0, 1, 1)  # Dla Strażnicy

        # DOLNY PANEL AKCJI (MAPA)
        self.action_buttons = []
        button_width = 120
        button_height = 60
        panel_total_width = 3 * button_width
        panel_total_height = 2 * button_height
        margin_right = 0
        margin_bottom = 0
        
        panel_x = w - panel_total_width - margin_right
        panel_y = h - panel_total_height - margin_bottom

        for row in range(2):
            for col in range(3):
                rect = pygame.Rect(panel_x + col * button_width, panel_y + row * button_height, button_width, button_height)
                self.action_buttons.append(rect)
                
        self.ui_panel_rect = pygame.Rect(panel_x - 10, panel_y - 10, panel_total_width + 20, panel_total_height + 20)

        # ====================================================
        # 4. ŁADOWANIE MAPY, IKON I GRACZY
        # ====================================================
        self.load_castle_and_tower()

        try:
            self.icon_training = pygame.image.load("assets/swords.png").convert_alpha()
            self.icon_training = pygame.transform.scale(self.icon_training, (32, 32))
        except:
            self.icon_training = pygame.Surface((32, 32))
            self.icon_training.fill((255, 0, 255))

        base_bg_path = r"assets\BACKGR3_S32_"
        self.terrain_images = {}
        try:
            self.terrain_images["$"] = pygame.image.load(f"{base_bg_path}752.png").convert_alpha()
            self.terrain_images["S"] = pygame.image.load(f"{base_bg_path}733.png").convert_alpha()
            self.terrain_images["&"] = pygame.image.load(f"{base_bg_path}736.png").convert_alpha()
            for key in self.terrain_images:
                self.terrain_images[key] = pygame.transform.scale(self.terrain_images[key], (TILE_SIZE, TILE_SIZE))
        except Exception as e:
            print(f"Błąd ładowania dodatkowych kafelków: {e}")

        # Inicjalizacja Graczy
        num_players = 2 
        player_data = [
            ("Don Marek", (200, 0, 0), "red"),
            ("Lech VI", (0, 0, 200), "blue"),
            ("Mściwój", (0, 150, 0), "green"),
            ("Biały Kieł", (220, 220, 220), "white"),
            ("Złoty Pan", (200, 200, 0), "yellow")
        ]

        from player import Player
        for i in range(num_players):
            name, color_rgb, color_name = player_data[i]
            new_player = Player(i, name, color_rgb, color_name)
            self.players.append(new_player)

   
    def setup_starting_units(self):
        """Rozdaje graczom początkowe wojsko pod ich zamkami."""
        for c in self.castles:
            if c.owner:
                owner_obj = self.players[c.owner] if isinstance(c.owner, int) else c.owner
                
                # 1. PIECHOTA (Dwa kafelki pod zamkiem)
                start_x = int(c.x)
                start_y = int(c.y + 2)
                infantry = Unit("INFL", start_x, start_y, owner_obj)
                self.add_unit(infantry)
                
                # Każdy zamek dostaje swojego budowniczego (razem 2 na gracza)
                start_x = int(c.x + 2) # Stawiamy obok zamku
                start_y = int(c.y)
                builder = Unit("BUDOW", start_x, start_y, c.owner)
                self.add_unit(builder)
                

    def add_player(self, player):
        self.players.append(player)

    def add_unit(self, unit):
        # 1. Rejestracja w świecie
        if unit not in self.units:
            self.units.append(unit)
        
        # 2. Bezpieczne przypisanie do właściciela
        # Sprawdzamy czy owner to faktycznie obiekt z listą 'units'
        if unit.owner and hasattr(unit.owner, 'units'):
            if unit not in unit.owner.units:
                unit.owner.units.append(unit)
                print(f"DEBUG: Jednostka {unit.type} przypisana do gracza {unit.owner.name}")
        else:
            # Jeśli tu trafimy, to znaczy, że owner jest źle przypisany (np. jest stringiem)
            print(f"OSTRZEŻENIE: Jednostka {unit.type} ma błędnego właściciela: {unit.owner}")
            
    def next_turn(self):
        if not self.players:
            return

        # Przełączamy gracza
        self.current_player = (self.current_player + 1) % len(self.players)
        
        # resetujemy UI i flagi dla nowego gracza
        self.reset_units()
        self.active_dropdown = None 
        self.build_menu_open = False 
        self.selected_castle = None
        self.selected_unit = None
        self.screen = "map"

        # --- KLUCZ: Logika zamków i budowania odpala się TYLKO raz na rundę ---
        # (Np. gdy kolejka wraca do gracza 0)
        if self.current_player == 0:
            self.turn += 1
            self.process_construction() 

            for castle in self.castles:
                if not getattr(castle, 'destroyed', False):
                    castle.next_turn() # Tu jest process_production()
                    # castle.collect_taxes() # To już masz w castle.next_turn()

    def move_unit(self, unit, dx, dy, cost=1):
        """
        ZAKTUALIZOWANA LOGIKA RUCHU:
        Dodano: Blokadę tur, obsługę pułapek i poprawne przejmowanie zamków.
        """
        # 0. BLOKADA TURY (Bezpieczeństwo)
        # Sprawdzamy, czy jednostka należy do gracza, który ma teraz turę
        if unit.owner != self.players[self.current_player]:
            print("DEBUG: Nie Twoja tura!")
            return False

        # 1. Sprawdzenie punktów ruchu
        if unit.move_points < cost:
            print(f"DEBUG: Jednostka {unit.type} nie ma MP ({unit.move_points} < {cost}).")
            return False

        nx, ny = unit.x + dx, unit.y + dy

        # 2. Granice mapy
        if not (0 <= nx < len(self.map[0]) and 0 <= ny < len(self.map)):
            return False

        # 3. INTERAKCJA Z ZAMKIEM (Obszar 2x2 dla Zamków, 1x1 dla Strażnic)
        for castle in self.castles:
            size = 2 if castle.building_type in ["Zamek", "Twierdza"] else 1
            if castle.x <= nx < castle.x + size and castle.y <= ny < castle.y + size:
                if getattr(castle, 'destroyed', False):
                    return False

                # Jeśli zamek jest wrogi -> PRZEJMUJEMY
                if castle.owner != unit.owner:
                    print(f"Zamek na ({castle.x}, {castle.y}) został ZDOBYTY przez {unit.owner.color}!")
                    castle.owner = unit.owner
                    # Czyścimy garnizon wroga
                    castle.garrison = [None] * castle.garrison_limit 
                    # Przerywamy wrogą produkcję
                    castle.production_enabled = False
                    castle.production_unit_type = None

                # Próba wejścia do garnizonu (automatyczna, jeśli jest miejsce)
                for i in range(len(castle.garrison)):
                    if castle.garrison[i] is None:
                        castle.garrison[i] = unit
                        if unit in self.units: self.units.remove(unit)
                        if unit in unit.owner.units: unit.owner.units.remove(unit)
                        
                        unit.move_points -= cost
                        if self.selected_unit == unit:
                            self.selected_unit = None
                        return True
                
                print("Garnizon pełny! Nie możesz wejść.")
                return False

        # 4. TEREN
        walkable_chars = [".", "l", "g", "p", "_", "#", "$","x", " "] 
        map_char = self.map[ny][nx]
        if map_char not in walkable_chars:
            return False

        # 5. PUŁAPKI (Nowość!)
        pos = (nx, ny)
        if pos in self.traps and self.traps[pos]["active"]:
            # Jeśli wdepnęliśmy w pułapkę wroga
            if self.traps[pos]["owner"] != unit.owner:
                self.trap_active = True
                self.unit_on_trap = unit
                # Ruch zostaje przerwany - reszta logiki obsłużona w pop-upie
                unit.x, unit.y = nx, ny
                print("Wdepnięto w pułapkę!")
                return True # Zwracamy True, żeby jednostka "stanęła" na polu

        # 6. WALKA 
        for other in self.units[:]:
            if other.x == nx and other.y == ny:
                if other.owner != unit.owner:
                    # To jest wróg -> Walka (zostawiasz jak masz)
                    self.units.remove(other)
                    # ...
                else:
                    return False # Nie można wejść na sojusznika
            
        # 7. ZBIERANIE ZASOBÓW (Chłopi / Złoto)
        for group in self.peasant_groups[:]:
            if group.x == nx and group.y == ny and group.owner != unit.owner:
                unit.carried_peasants += group.amount
                self.peasant_groups.remove(group)

        for t in self.gold_transports[:]:
            if t.x == nx and t.y == ny and t.owner != unit.owner:
                unit.carried_gold += t.gold
                self.gold_transports.remove(t)

        # 8. FINALIZACJA RUCHU
        unit.x, unit.y = nx, ny
        unit.move_points -= cost
        return True
    
    def reset_units(self):
        for u in self.units:
            if u.x < 0:
                continue
            u.move_points = 5

    def select_unit(self, x, y):
        for u in self.units:
            # --- BLOKADA: Ignoruj jednostki w trakcie pracy ---
            if getattr(u, 'is_building', False):
                continue 

            if u.x == x and u.y == y:
                if u.owner == self.players[self.current_player]:
                    self.selected_unit = u
                    print(f"Wybrano jednostkę: {u.type}")
                    return
                else:
                    print("To nie jest twoja jednostka")
                    return

        print("Brak jednostki na tym polu")

    def spawn_unit_near_castle(self, unit, castle):
        spawn_positions = [
            (castle.x, castle.y - 1),
            (castle.x, castle.y + 1),
            (castle.x - 1, castle.y),
            (castle.x + 1, castle.y),
        ]

        for sx, sy in spawn_positions:
            if 0 <= sy < len(self.map) and 0 <= sx < len(self.map[0]):
                if self.map[sy][sx] == ".":
                    unit.x = sx
                    unit.y = sy
                    self.add_unit(unit)
                    return True

        return False
        
    def get_castle(self, x, y):
        for c in self.castles:
            if c.x == x and c.y == y:
                return c
            
    def select_garrison_unit(self, unit):
        if len(self.selected_units) >= 10:
            print("Limit zaznaczenia to 10")
            return

        if unit not in self.selected_units:
            self.selected_units.append(unit)

    def clear_selection(self):
        self.selected_units.clear()

    def get_unit_at_pixel(self, mx, my):
        # Skoro jesteś wewnątrz klasy World, używasz po prostu self.units
        for u in self.units: 
            # Przeliczamy pozycję jednostki na piksele ekranu
            # Pamiętaj, żeby TILE_SIZE i camera_x były dostępne (self.camera_x)
            ux = int(u.x) * 32 - self.camera_x 
            uy = int(u.y) * 32 - self.camera_y
            
            # Tworzymy prostokąt kolizji dla jednostki
            unit_rect = pygame.Rect(ux, uy, 32, 32)
            
            if unit_rect.collidepoint(mx, my):
                return u
        return None   

              
    def select_castle(self, x, y):
            for c in self.castles:
                # Pobieramy rozmiar zamku (1 to 32px, 2 to 64px itd.)
                # Zakładam, że TILE_SIZE to 32.
                size_in_pixels = 32
                if hasattr(c, 'building_type') and c.building_type in ["Zamek", "Twierdza"]:
                    size_in_pixels = 64 # Zamki są duże (2x2)

                # Sprawdzamy, czy kliknięcie myszki mieści się w kwadracie zamku
                if c.x <= x < c.x + size_in_pixels and c.y <= y < c.y + size_in_pixels:
                    self.selected_castle = c
                    print(f" Wybrano zamek: {c.x}, {c.y}")
                    
                    # WAŻNE: Tutaj musisz przełączyć grę w tryb zamku!
                    # np. self.show_castle_menu = True (zależnie jak to nazwałeś u siebie)
                    
                    return

            self.selected_castle = None
            print("Pudło! Kliknięto w:", x, y)

    def create_unit(self, unit_type, x, y, owner):
        u = Unit(unit_type, x, y, owner)
        self.add_unit(u)
        return u
     
    def handle_garrison_click(self, mx, my, button):
        castle = self.selected_castle
        if not castle:
            return

        # ================= BACK =================
        if hasattr(self, 'back_button_castle') and self.back_button_castle.collidepoint(mx, my):
            self.selected_units.clear()
            self.screen = "castle"
            return

        # ================= RECRUITMENT =================
        if self.garrison_gfx.handle_prod_click(mx, my, castle):
            self.prod_anim_timer = pygame.time.get_ticks() # Nowy stoper dla animacji
            return

        # ================= HEAL =================
        if self.garrison_gfx.handle_hosp_click(mx, my, castle):
            for unit in self.selected_units:
                castle.start_healing_unit(unit)
            return

        # ================= TRAIN ================= 
        if self.garrison_gfx.handle_school_click(mx, my, castle):
            if self.selected_units:
                castle.start_training_group(self.selected_units) 
                self.selected_units.clear() 
                print("Zakończono wydawanie rozkazów szkolenia")
            else:
                print("Brak zaznaczonych jednostek do szkolenia")
            return
        
    def get_unit_at(self, x, y):
        for unit in self.units:
            # Ignoruj jednostki, które są w trakcie budowy!
            if getattr(unit, 'is_building', False):
                continue
                
            if unit.x == x and unit.y == y:
                return unit
        return None

    def check_unit_castle_entry(self, unit):
        """Sprawdza czy jednostka powinna zostać przeniesiona do garnizonu zamku."""
        for castle in self.castles:
            # Sprawdzamy czy jednostka stoi na którymś z 4 pól zamku
            if castle.x <= unit.x <= castle.x + 1 and castle.y <= unit.y <= castle.y + 1:
                if castle.owner == unit.owner:
                    print(f"{unit.type} wchodzi do garnizonu.")
                    # Dodajemy do listy garnizonu (musisz mieć tę listę w klasie Castle)
                    if not hasattr(castle, 'garrison'):
                        castle.garrison = []
                    
                    castle.add_to_garrison(unit)
                    # Usuwamy z mapy świata
                    if unit in unit.owner.units:
                        unit.owner.units.remove(unit)
                    
                    self.selected_unit = None # Odznaczamy po wejściu
                    return True
        return False  
                  
    def enter_castle(self, unit, castle):
        """Przenosi lidera i wszystkich jego pasażerów do osobnych slotów w zamku."""
        # 1. Przygotowujemy listę wszystkich jednostek, które chcą wejść
        to_enter = [unit]
        if hasattr(unit, 'garrison') and unit.garrison:
            # Wyciągamy wszystkich pasażerów, którzy nie są None
            to_enter.extend([u for u in unit.garrison if u is not None])

        # 2. Sprawdzamy, czy w zamku jest dość miejsca dla wszystkich
        free_slots = [i for i, slot in enumerate(castle.garrison) if slot is None]
        
        if len(to_enter) > len(free_slots):
            print(f"Brak miejsca w zamku! Próbujesz wprowadzić {len(to_enter)} oddziałów, a wolnych jest {len(free_slots)}.")
            return False

        # 3. Rozpakowujemy jednostki do osobnych slotów zamku
        for idx, u_to_add in enumerate(to_enter):
            target_slot = free_slots[idx]
            castle.garrison[target_slot] = u_to_add
            
            # Czyścimy dane jednostki o pozycji na mapie
            u_to_add.x, u_to_add.y = -1, -1
            
            # Jeśli jednostka była fizycznie na mapie (lider), usuwamy ją ze świata
            if u_to_add in self.units:
                self.units.remove(u_to_add)
            if u_to_add.owner and u_to_add in u_to_add.owner.units:
                u_to_add.owner.units.remove(u_to_add)

        # 4. Czyścimy garnizon lidera, bo teraz wszyscy są już w zamku jako osobne byty
        if hasattr(unit, 'garrison'):
            unit.garrison = [None] * 10

        self.selected_unit = None
        print(f"DEBUG: Pomyślnie wprowadzono i rozpakowano {len(to_enter)} jednostek w zamku.")
        return True
 
    def remove_unit_or_builder(self, army, builder):
        # Jeśli armia to po prostu jeden budowniczy
        if army == builder:
            if army in self.units:
                self.units.remove(army)
            return

        # Jeśli armia to grupa (zakładam, że ma listę 'members')
        if hasattr(army, 'members'):
            for unit in army.members:
                if unit.type == "Budowniczy":
                    army.members.remove(unit) # Ginie tylko ten jeden
                    print("Poświęcono jednego budowniczego z armii.")
                    
                    # Jeśli armia została pusta, usuń ją z mapy
                    if len(army.members) == 0:
                        if army in self.units:
                            self.units.remove(army)
                    return
  
    def spawn_unit(self, unit_type, x, y, owner):
        """Główna i jedyna funkcja do tworzenia jednostek w świecie."""
        from unit import Unit
        
        # Tworzymy jednostkę: unit_type to kod (np. "INFL"), x, y to liczby, owner to obiekt
        new_unit = Unit(unit_type, x, y, owner)
        
        self.add_unit(new_unit) 
        print(f"Zrekrutowano: {unit_type} na pozycji ({x}, {y}) dla gracza {owner}")
        
        return new_unit # Zwracamy obiekt, żeby można go było przypisać np. do zmiennej
   
    def count_builders_near(self, pos):
        px, py = pos
        # Szukamy budowniczych dokładnie na kafelku placu budowy
        return sum(1 for u in self.units if u.x == px and u.y == py and u.type.lower() == "budowniczy") 
    
    def release_selected_units(self, stay_in_menu=True):        
        target = self.selected_castle or getattr(self, 'active_building', None)
        if not target or not self.selected_units:
            return

        # 1. Podział na grupy
        chłopi_group = [u for u in self.selected_units if u.type == "Chłop"]
        złoto_group = [u for u in self.selected_units if u.type == "Złoto"]
        wojsko_group = [u for u in self.selected_units if u.type not in ["Chłop", "Złoto"]]
        groups_to_spawn = [g for g in [chłopi_group, złoto_group, wojsko_group] if g]
        
        spawn_positions = self.find_multiple_spawn_positions(target, len(groups_to_spawn))
        from unit import Unit
        
        for idx, group in enumerate(groups_to_spawn):
            pos = spawn_positions[idx] if idx < len(spawn_positions) else None
            
            # --- ZABEZPIECZENIE: Jeśli nie ma wolnego miejsca, informujemy gracza ---
            if not pos: 
                print(f"BŁĄD: Brak wolnego terenu na mapie! Oddział {idx + 1} utknął w zamku.")
                continue
            
            nx, ny = pos

            if len(group) == 1:
                # ================= SCENARIUSZ A: SOLO (np. pojedynczy Budowniczy) =================
                solo_unit = group[0]
                
                # Usuwanie ze slotu zamku
                for slot_idx in range(len(target.garrison)):
                    if target.garrison[slot_idx] is solo_unit:
                        target.garrison[slot_idx] = None
                        if hasattr(self, 'garrison_gfx'):
                            self.garrison_gfx.trigger_door_open(slot_idx)
                        break

                solo_unit.x, solo_unit.y = nx, ny
                if hasattr(solo_unit, 'rect'):
                    solo_unit.rect.topleft = (nx * TILE_SIZE, ny * TILE_SIZE)
                solo_unit.visible = True
                
                if solo_unit not in self.units:
                    self.units.append(solo_unit)

                if target.owner and solo_unit not in target.owner.units:
                    target.owner.units.append(solo_unit)
                    
                print(f"Wypuszczono solo: {solo_unit.type} na pole ({nx}, {ny}).")

            else:
                # ================= SCENARIUSZ B: GRUPA (ARMIA) =================
                # Bierzemy pierwszą jednostkę z grupy jako Lidera (ona będzie widoczna na mapie)
                leader = group[0]
                leader.x, leader.y = nx, ny
                leader.garrison = [None] * 10 # Inicjujemy jej garnizon
                
                # Wszystkie jednostki z grupy (wliczając lidera) muszą zniknąć ze slotów zamku
                # Wszystkie jednostki z grupy (wliczając lidera) muszą zniknąć ze slotów zamku
                for unit_to_clear in group:
                    for slot_idx in range(len(target.garrison)):
                        if target.garrison[slot_idx] is unit_to_clear:
                            target.garrison[slot_idx] = None
                            
                            # DODANE: Animacja drzwi działa teraz też dla całych armii!
                            if hasattr(self, 'garrison_gfx'):
                                self.garrison_gfx.trigger_door_open(slot_idx)
                                
                            break
                # Resztę jednostek (od indeksu 1) chowamy do garnizonu lidera
                for i, unit_to_hide in enumerate(group[1:]):
                    if i < 10:
                        leader.garrison[i] = unit_to_hide
                        unit_to_hide.x, unit_to_hide.y = -1, -1 # Pasażerowie znikają z mapy
                        if unit_to_hide in self.units:
                            self.units.remove(unit_to_hide)

                # Tylko Lidera dodajemy do świata na mapę
                if leader not in self.units:
                    self.units.append(leader)
                if target.owner and leader not in target.owner.units:
                    target.owner.units.append(leader)
                
                print(f"Wypuszczono oddział: Lider {leader.type} prowadzi {len(group)-1} jednostek.")
        # --- Finał ---
        self.selected_units.clear()
        
        if not stay_in_menu:
            self.screen = "map"
            self.selected_castle = None

    def find_multiple_spawn_positions(self, castle, num_groups):
        """Szuka wolnych miejsc dla X grup promieniście, powiększając obszar."""
        results = []
        occupied = {(u.x, u.y) for u in self.units}
        
        # Ustalamy rozmiar zamku (Zamek/Twierdza = 2x2, Strażnica = 1x1)
        size = 2 if getattr(castle, 'building_type', 'Zamek') in ["Zamek", "Twierdza"] else 1
        
        # DOZWOLONE TERENY (dodano spację " ", żeby krawędzie mapy nie blokowały)
        allowed = [".", "_", "p", "#", "$", "l", "g", " "]
        
        # Skanujemy otoczenie (od 1 kafelka od murów, aż do 5 kafelków w głąb mapy)
        for radius in range(1, 6):
            if len(results) >= num_groups:
                break
                
            min_x = int(castle.x) - radius
            max_x = int(castle.x) + size + radius - 1
            min_y = int(castle.y) - radius
            max_y = int(castle.y) + size + radius - 1
            
            for dy in range(min_y, max_y + 1):
                for dx in range(min_x, max_x + 1):
                    # Sprawdzamy tylko obwódkę (ignorujemy środek, gdzie stoi zamek)
                    if dx == min_x or dx == max_x or dy == min_y or dy == max_y:
                        if 0 <= dx < len(self.map[0]) and 0 <= dy < len(self.map):
                            if (dx, dy) not in occupied and self.map[dy][dx] in allowed:
                                if len(results) < num_groups:
                                    results.append((dx, dy))
                                    occupied.add((dx, dy)) # Rezerwujemy na przyszłość
                                    
        # Wypełniamy ewentualne braki wartością None, żeby program nie crashował
        while len(results) < num_groups:
            results.append(None)
            
        return results

# Dodaj te funkcje do klasy World:

    def is_far_from_enemies(self, unit, min_dist):
        """Sprawdza, czy w promieniu min_dist nie ma jednostek przeciwnika."""
        for other in self.units:
            if other.owner != unit.owner: # To jest wróg
                # Proste obliczenie dystansu (Euklidesowe lub Manhattan)
                dist = ((unit.x - other.x)**2 + (unit.y - other.y)**2)**0.5
                if dist < min_dist:
                    return False
        return True

    def has_builder(self, u):
        """Sprawdza, czy w oddziale/armii jest budowniczy."""
        if not u: return False
        if u.type == "BUDOW" or u.type == "Budowniczy":
            return True
        if hasattr(u, 'garrison'):
            return any(slot and (slot.type == "BUDOW" or slot.type == "Budowniczy") for slot in u.garrison)
        return False
    
    def merge_units(self, moving_unit, target_unit, cost):
        """Łączy jednostkę ruchomą z docelową bez duplikowania liderów."""
        
        # 1. Przygotowujemy listę jednostek do dodania (ruchomy lider + jego ewentualny garnizon)
        to_add = [moving_unit]
        if hasattr(moving_unit, 'garrison') and moving_unit.garrison:
            to_add.extend([u for u in moving_unit.garrison if u is not None])
            # Czyścimy stary garnizon wędrowca, bo teraz staje się on zwykłym żołnierzem
            moving_unit.garrison = [None] * 10 

        # 2. Upewniamy się, że jednostka docelowa (target) ma miejsce w środku
        if not hasattr(target_unit, 'garrison') or not target_unit.garrison:
            target_unit.garrison = [None] * 10
            
        free_slots = [i for i, slot in enumerate(target_unit.garrison) if slot is None]
        
        if len(to_add) > len(free_slots):
            print(f"Brak miejsca! Próbujesz dodać {len(to_add)} oddziałów, a masz {len(free_slots)} wolnych slotów.")
            self.merge_mode = False
            return False

        # 3. Przenosimy jednostki do środka target_unit
        for i, unit_to_hide in enumerate(to_add):
            slot_idx = free_slots[i]
            target_unit.garrison[slot_idx] = unit_to_hide
            
            # Jednostka wchodząca do środka znika z mapy głównej
            unit_to_hide.x, unit_to_hide.y = -1, -1
            if unit_to_hide in self.units:
                self.units.remove(unit_to_hide)
            if unit_to_hide.owner and unit_to_hide in unit_to_hide.owner.units:
                unit_to_hide.owner.units.remove(unit_to_hide)

        # 4. Finalizacja
        self.merge_mode = False
        self.selected_unit = target_unit # Kamera zostaje na "nowej" armii
        target_unit.move_points = min(target_unit.move_points, moving_unit.move_points - cost)
        
        print(f"Połączono! Liderem jest {target_unit.type}. W środku: {10 - target_unit.garrison.count(None)} oddziałów.")
        return True
    
    def center_camera_on(self, tx, ty):
        """Centruje kamerę na podanych współrzędnych kafelka."""
        from settings import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE
        
        # Przeliczamy pozycję kafelka na piksele
        target_px = tx * TILE_SIZE
        target_py = ty * TILE_SIZE
        
        # Ustawiamy kamerę tak, by środek ekranu celował w ten piksel
        self.camera_x = target_px - (SCREEN_WIDTH // 2)
        self.camera_y = target_py - (SCREEN_HEIGHT // 2)
        
        # Zabezpieczenie przed wyjechaniem kamery poza mapę
        if self.map and self.map[0]:
            max_x = len(self.map[0]) * TILE_SIZE - SCREEN_WIDTH
            max_y = len(self.map) * TILE_SIZE - SCREEN_HEIGHT
            self.camera_x = max(0, min(self.camera_x, max_x))
            self.camera_y = max(0, min(self.camera_y, max_y))

    def select_next_active_unit(self):
        """Wybiera następną jednostkę gracza, która ma punkty ruchu."""
        current_owner = self.players[self.current_player]
        
        # Tworzymy listę jednostek na mapie (x >= 0), które mają ruch i należą do nas
        active_units = [u for u in self.units if u.owner == current_owner and u.move_points > 0 and u.x >= 0]
        
        if not active_units:
            print("Żadna Twoja jednostka nie ma już punktów ruchu!")
            return

        # Szukamy indeksu aktualnie zaznaczonej jednostki w naszej aktywnej liście
        start_idx = -1
        if self.selected_unit in active_units:
            start_idx = active_units.index(self.selected_unit)

        # Wybieramy następną z rzędu (modulo zapewnia zapętlenie listy na koniec)
        next_idx = (start_idx + 1) % len(active_units)
        next_u = active_units[next_idx]
        
        # Zaznaczamy i centrujemy
        self.selected_unit = next_u
        self.center_camera_on(next_u.x, next_u.y)
        print(f"Centrowanie na: {next_u.type} (Punkty ruchu: {next_u.move_points})")

    def select_next_building(self):
        """Wybiera następny budynek gracza (Zamek, Twierdza, Strażnica)."""
        current_owner = self.players[self.current_player]
        
        # Zbieramy wszystkie nasze nieniszczone zamki
        my_castles = [c for c in self.castles if c.owner == current_owner and not getattr(c, 'destroyed', False)]
        
        if not my_castles:
            print("Nie posiadasz żadnych budynków!")
            return
            
        start_idx = -1
        if self.selected_castle in my_castles:
            start_idx = my_castles.index(self.selected_castle)
            
        next_idx = (start_idx + 1) % len(my_castles)
        next_c = my_castles[next_idx]
        
        # Wybieramy budynek i centrujemy
        self.selected_castle = next_c
        self.center_camera_on(next_c.x, next_c.y)
        print(f"Centrowanie na: {next_c.building_type} na pozycji ({next_c.x}, {next_c.y})")

# --- URUCHOMIENIE ---
# generuj_las_precyzyjny("final_map1.txt", "mapa_tlo.png", "mapa_finalna_z_lasem.png")

# PRZYKŁAD UŻYCIA:
# coords = [(random.randint(0, 2000), random.randint(0, 2000)) for _ in range(1500)]
# generate_forest("mapa_base.png", "grafiki/trees", coords, "mapa_z_lasem.png")
    #def draw_map
    #jeśli chce aby kratki były tak jak w oryginale
        #keys = pygame.key.get_pressed()
        #if keys[pygame.K_g]:
            #for x range ...


         # Sterowanie jednostką przyciskami 
        # --- RUCH JEDNOSTKĄ ---
            #if self.screen == "map" and self.selected_unit:
            #   if event.key == pygame.K_UP:    self.move_unit(self.selected_unit, 0, -1)
            #   elif event.key == pygame.K_DOWN:  self.move_unit(self.selected_unit, 0, 1)
            #   elif event.key == pygame.K_LEFT:  self.move_unit(self.selected_unit, -1, 0)
            #   elif event.key == pygame.K_RIGHT: self.move_unit(self.selected_unit, 1, 0)

 # --- 2. RUCH MYSZY (HOVER) wyświetlanie krótkiej informacji gdy się najedzie myszką na jednostkę
           # elif event.type == pygame.MOUSEMOTION:
              #  mx, my = event.pos
               # if self.screen == "garrison":
                     # Tutaj tylko podświetlamy ramkę (jeśli masz taką logikę)
                    #self.handle_mouse_hover(mx, my)

if __name__ == "__main__":
    import subprocess, sys, os
    main_path = os.path.join(os.path.dirname(__file__), "main.py")
    subprocess.run([sys.executable, main_path])


    # 4. TEREN (POPRAWKA 2: Delegujemy sprawdzanie do profesjonalnego Pathfindera)
       # if hasattr(self, 'pathfinder'):
         #   if not self.pathfinder.is_walkable(nx, ny, unit):
        #        print(f"DEBUG: Blokada! Teren na ({nx}, {ny}) jest nieprzejezdny.")
       #         return False

        # ==========================================
        # 4.5. INTERAKCJA Z PUŁAPKĄ (BUM!)
        # ==========================================
      #  if self.map[ny][nx] == "X":
     #       print(f"BUM! Jednostka {unit.type} wpadła w pułapkę na ({nx}, {ny})!")
            
            # 1. Usuwamy jednostkę z gry (ginie)
    #        if unit in self.units: 
   #             self.units.remove(unit)
  #          if unit in unit.owner.units: 
 #               unit.owner.units.remove(unit)
#            if self.selected_unit == unit: 
            #    self.selected_unit = None
                
            # 2. Usuwamy pułapkę z mapy i przywracamy oryginalne tło
           # original_bg = getattr(self, 'trap_backgrounds', {}).get((nx, ny), ".")
          #  self.map[ny][nx] = original_bg
            
            # 3. Zwracamy True, bo ruch się wykonał (choć jednostka go nie przeżyła)
         #   return True

        # 5. WALKA 
        #for other in self.units[:]: