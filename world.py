from unit import Unit
from castle import Castle, UNIT_REQUIREMENTS
from player import Player
from buildings import BuildingsMixin
from castle import BUILDING_TYPES
import random  # Do losowania drzew (żeby las nie był nudny)
import pygame  # Silnik gry
import os
from settings import UNIT_STATS, UNIT_NAMES, TERRAIN_TYPES, MAP_HEIGHT, MAP_WIDTH, TILE_SIZE, COLOR_TO_ID, SCREEN_HEIGHT, SCREEN_WIDTH
from court import CourtHandler
from controls import ControlsHandler
from UI_components import UnitInfoWindow  
from castle_graphics import CastleGraphics
from garrison_graphics import GarrisonGraphics
from recruitment import RecruitmentManager
from peasant_menu import PeasantMenu
from court_graphics import CourtGraphics
from loot_manager import LootManager
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
        self.visited_temples = set()
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
        self.ports = []
        self.camera_x = 0
        self.camera_y = 0

        # Tryby budowy dróg i pułapek
        self.trap_build_mode = False
        self.road_build_mode = False
        self.build_menu_open = False
        self.menu_open = False
        self.active_dropdown = None

        self.traps = {}
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
        self.court_gfx = CourtGraphics(w, h)
        from combat_setup import CombatSetupMenu
        self.combat_menu = CombatSetupMenu(w, h)
        
        # Zmienne przechowujące stan zawieszonej walki
        self.combat_attacker = None
        self.combat_defender = None
        self.combat_nx = 0
        self.combat_ny = 0
        self.combat_cost = 0

        self.font = pygame.font.SysFont("Arial", 24)
        self.font_small = pygame.font.SysFont(None, 20)
        self.modal_font = pygame.font.SysFont(None, 32)
        self.btn_font = pygame.font.SysFont(None, 28, bold=True)
        self.font_title = pygame.font.SysFont("Times New Roman", 40, bold=True) # <--- DODAJ TĘ LINIJKĘ
        self.font_main = pygame.font.SysFont("Arial", 26)  # <--- DODAJ TĘ LINIJKĘ

        # ====================================================
        # 3. INTERFEJS I PRZYCISKI
        # ====================================================
        # Uniwersalny przycisk powrotu i jego animacja
        self.back_button_castle = pygame.Rect(45, 690, 130, 74)
        self.back_button_bldg   = pygame.Rect(68, 680, 150, 80)

        # >>> NOWY PRZYCISK TYLKO DLA GARNIZONU <<<
        # Tu możesz swobodnie edytować X (np. 68) i Y (np. 680), żeby załatać czarną dziurę!
        self.back_button_garrison = pygame.Rect(62, 679, 154, 83) 
        
        self.back_button        = self.back_button_bldg
        self.back_anim_timer    = 0
        self.back_destination   = "map"
        
        try:
            self.back_img_bldg_normal    = pygame.transform.scale(pygame.image.load("assets/back_normal.png").convert_alpha(),  (150, 80))
            self.back_img_bldg_pressed   = pygame.transform.scale(pygame.image.load("assets/back_clicked.png").convert_alpha(), (150, 80))
            # >>> NOWE: GRAFIKI TYLKO DLA GARNIZONU <<<
            # (Podmień nazwy plików na te, których chcesz użyć)
            self.back_img_garrison_normal  = pygame.image.load("assets/przyciski/PRZ_1.png").convert_alpha()
            self.back_img_garrison_pressed = pygame.image.load("assets/przyciski/PRZ_2.png").convert_alpha()
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
        self.btn_system = pygame.Rect(500, 0, 100, 40)
        self.btn_mapa = pygame.Rect(305, 0, 100, 40)
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

        base_bg_path = r"assets/normal/BACKGR3_S32/BACKGR3_S32_"
        self.terrain_images = {}
        try:
            self.terrain_images["$"] = pygame.image.load(f"{base_bg_path}752.png").convert_alpha()
            self.terrain_images["S"] = pygame.image.load(f"{base_bg_path}733.png").convert_alpha()
            self.terrain_images["&"] = pygame.image.load(f"{base_bg_path}736.png").convert_alpha()
            for key in self.terrain_images:
                self.terrain_images[key] = pygame.transform.scale(self.terrain_images[key], (TILE_SIZE, TILE_SIZE))
        except Exception as e:
            print(f"Błąd ładowania dodatkowych kafelków: {e}")

        # Inicjalizacja Graczy z przypisaniem frakcji
        num_players = 5
        player_data = [
            ("Don Marek", (200, 0, 0), "red", "catholic"),  # Katolik
            ("Lech VI", (0, 0, 200), "blue", "pagan"),      # Poganin
            ("Mściwój", (0, 150, 0), "green", "pagan"),
            ("Biały Kieł", (220, 220, 220), "white", "pagan"),
            ("Złoty Pan", (200, 200, 0), "yellow", "catholic")
        ]

        for i in range(num_players):
            name, color_rgb, color_name, faction = player_data[i]
            # Przekazujemy frakcję prosto do nowej, czystej klasy Player
            new_player = Player(i, name, color_rgb, color_name, faction)
            self.players.append(new_player)
            
        # ==========================================
        # WYCINANIE GRAFIK Z_IKO_PCX.png (Spritesheet)
        # ==========================================
        try:
            z_iko_sheet = pygame.image.load(os.path.join("assets", "Z_IKO_PCX.png")).convert_alpha()
            
            # 1. PRZYCISK POWROTU DLA ZAMKU (Rozdzielony na wciśnięty i odciśnięty)
            # ZMIANA: Przypisujemy do back_img_castle, a NIE do back_img_bldg!
            self.back_img_castle_normal = z_iko_sheet.subsurface(pygame.Rect(8, 431, 78, 45))
            self.back_img_castle_pressed = z_iko_sheet.subsurface(pygame.Rect(90, 431, 78, 45))
            
            # 2. PASEK NAZWY BUDYNKU
            self.title_bar_img = z_iko_sheet.subsurface(pygame.Rect(180, 446, 285, 32))
            
            # 3. ANIMACJA ZIELONEGO MENU
            self.menu_frames = [
                z_iko_sheet.subsurface(pygame.Rect(509, 1, 123, 68)),
                z_iko_sheet.subsurface(pygame.Rect(509, 72, 123, 68)),
                z_iko_sheet.subsurface(pygame.Rect(509, 144, 123, 68)),
                z_iko_sheet.subsurface(pygame.Rect(509, 216, 123, 68)),
                z_iko_sheet.subsurface(pygame.Rect(509, 288, 123, 68)),
                z_iko_sheet.subsurface(pygame.Rect(509, 360, 123, 68))
            ]
            print("Wycinki z arkusza Z_IKO załadowane pomyślnie!")
        
        except Exception as e:
            print(f"Błąd wycinania z Z_IKO_PCX: {e}")
            self.title_bar_img = None
            self.menu_frames = []
            
        self.back_btn = pygame.Rect(0, 0, 0, 0)
        self.release_btn = pygame.Rect(0, 0, 0, 0)
        self.destroy_btn = pygame.Rect(0, 0, 0, 0)
        # ==========================================
        # GRAFIKI ŚWIĄTYNI (Wydarzenie)
        # ==========================================
       
        self.loot_manager = LootManager()
        try:
            # Upewnij się, że ścieżki do plików są poprawne!
            self.temple_scroll_l = pygame.image.load("assets/minimum/TEMPLE_S32/TEMPLE_S32_22.png").convert_alpha()
            self.temple_scroll_r = pygame.image.load("assets/minimum/TEMPLE_S32/TEMPLE_S32_23.png").convert_alpha()
            self.temple_hands = pygame.image.load("assets/minimum/TEMPLE_S32/TEMPLE_S32_24.png").convert_alpha()
            self.temple_lightning = pygame.image.load("assets/minimum/TEMPLE_S32/TEMPLE_S32_0.png").convert_alpha() # [cite: image_1.png]
            self.temple_chest = pygame.image.load("assets/minimum/TEMPLE_S32/TEMPLE_S32_16.png").convert_alpha()

        except Exception as e:
            print(f"Błąd ładowania grafik świątyni: {e}")
            # Puste powierzchnie awaryjne w razie braku plików
            self.temple_scroll_l = pygame.Surface((100, 200))
            self.temple_scroll_r = pygame.Surface((100, 200))
            self.temple_hands = pygame.Surface((50, 50))
            # Awaryjna błyskawica
            self.temple_lightning = pygame.Surface((50, 50)) # [cite: image_1.png]
            self.temple_lightning.fill((0, 0, 255)) # Niebieska plama jako failsafe [cite: image_1.png]
        # ==========================================
        # ŁADOWANIE GRAFIK PORTU (12 plików)
        # ==========================================
        self.port_tiles = {}
        # Wpisz tu poprawne numery z końcówek plików normal/BACKGR3_S32/_***.png
        port_gfx = {
            "pos1_base": ["716", "717", "720", "721"], # Baza Pozycji 1 (L-Góra, P-Góra, L-Dół, P-Dół)
            "pos1_ship": ["718", "719"],               # Statki dla Pozycji 1 (Lewy Dół, Prawy Dół)
            "pos2_base": ["722", "723", "726", "727"], # Baza Pozycji 2 
            "pos2_ship": ["724", "725"]                # <--- Wpisz tu poprawne numery statków dla portu nr 2!
        }
        
        for key, numbers in port_gfx.items():
            self.port_tiles[key] = []
            for num in numbers:
                # Upewnij się, że ścieżka pasuje do Twojego folderu (np. "assets" lub "assets/minimum/...")
                path = os.path.join("assets", "normal", "BACKGR3_S32", f"BACKGR3_S32_{num}.png") 
                try:
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                    self.port_tiles[key].append(img)
                except Exception as e:
                    print(f"Błąd portu (plik {num}): {e}")

        # Nowa zmienna do przechowywania efektu dla renderera
        self.temple_current_effect = None

        # --- IZOLACJA WIĘZIEŃ DLA KAŻDEGO GRACZA (ZAPOBIEGA BLEEDINGOWI) ---
        self.court_states = {}
        for p in self.players:
            p_slots = []
            for old_slot in self.court.prison_slots:
                # Tworzymy czysty, nowy obiekt tej samej klasy celi więziennej
                new_slot = old_slot.__class__()
                new_slot.general = None
                p_slots.append(new_slot)
                
            self.court_states[p.id] = {
                "slots": p_slots,
                "action": None
            }
        
        # Aktywujemy na start lochy pierwszego gracza
        if self.players:
            self.court.prison_slots = self.court_states[self.players[0].id]["slots"]
            self.court.selected_prison_action = self.court_states[self.players[0].id]["action"]
        self.units_to_split = [] # Tu trafiają jednostki zaznaczone kliknięciem w panelu
    
        #dodajemy słownik przejęcia zamku przez innych graczy
        self.castle_color_frames = {
            "blue": {"captured_by": {}},
            "red": {"captured_by": {}},
            "yellow": {"captured_by": {}},
            "white": {"captured_by": {}},
            "green": {"captured_by": {}}
    }

# Dzięki temu każdy kolor ma już gotową "szufladkę" na captured_by

    def spawn_port_reinforcements(self, port):
        """Generuje tylko INFORMACJĘ o liczbie jednostek w porcie."""
        import random
        ilosc = random.randint(3, 5)
        
        # Zamiast tworzyć wojsko, port po prostu zapamiętuje "ilość czekających skrzyń z posiłkami"
        port["pending_count"] = ilosc
        port["garrison"] = [] # Czyścimy stary system, jeśli gdzieś został
        
        port["has_ship"] = True
        port["ship_timer"] = 1 # Statek będzie widoczny tylko przez 1 turę!
        print(f"Statek przywiózł posiłki! W porcie czeka {ilosc} tajemniczych najemników.")

    def update_ports_turn(self):
        """Aktualizuje liczniki portów (WYWOŁAJ TO NA POCZĄTKU NOWEJ TURY)."""
        if not hasattr(self, 'ports'): return
        for port in self.ports:
            if port.get("ship_timer", 0) > 0:
                port["ship_timer"] -= 1
                if port["ship_timer"] <= 0:
                    port["has_ship"] = False
                    print("Statek odpłynął, ale najemnicy czekają w porcie.")
                    
            if port.get("cooldown", 0) > 0:
                port["cooldown"] -= 1
                if port["cooldown"] <= 0:
                    self.spawn_port_reinforcements(port)
                    
    def unload_port(self, port, triggering_unit):
        print("Wojska odebrane na ląd! Rozpoczynam rekrutację...")
        
        import random
        from unit import Unit
        
        # =======================================================
        # NOWOŚĆ: Losujemy jednostki DOPIERO TERAZ i od razu
        # przypisujemy je do gracza, który ich odebrał!
        # =======================================================
        mozliwe_jednostki = [
            "Posp. ruszenie", "Lekka piechota", "Ciężka piechota", "Pikinier", 
            "Halbardnik", "Lekka jazda", "Rycerstwo", "Dragon", "Łucznik", 
            "Kusznik", "Leśnik", "Góral", "Budowniczy"
        ]
        
        ilosc = port.get("pending_count", 0)
        # Zabezpieczenie dla starych zapisów
        if ilosc == 0 and port.get("garrison"): 
            ilosc = len(port["garrison"])
            
        nowy_garnizon = []
        for _ in range(ilosc):
            typ = random.choice(mozliwe_jednostki)
            # Tworzymy nową jednostkę już z poprawnym kolorem (triggering_unit.owner)
            nowa_jednostka = Unit(typ, -1, -1, triggering_unit.owner)
            nowy_garnizon.append(nowa_jednostka)
                
        # 1. INTELIGENTNE SZUKANIE WOLNEGO LĄDU PRZED PORTEM
        wolne_pole = None
        walkable_tiles = [".", "l", "g", "p", "_", "B", "P", "G"] 
        
        for radius in range(1, 4):
            for dy in range(-radius, radius + 2): 
                for dx in range(-radius, radius + 2):
                    px, py = port["x"] + dx, port["y"] + dy
                    if 0 <= py < len(self.map) and 0 <= px < len(self.map[0]):
                        obj_tile = self.map[py][px]
                        bg_tile = self.bg_map[py][px] if hasattr(self, 'bg_map') else "."
                        
                        if obj_tile in walkable_tiles or bg_tile in walkable_tiles:
                            if obj_tile not in ["W", "w", "M", "R", "S", "&", "#"] and bg_tile not in ["W", "w"]:
                                if not any(u.x == px and u.y == py for u in self.units):
                                    wolne_pole = (px, py)
                                    break
                if wolne_pole: break
            if wolne_pole: break
            
        if not wolne_pole:
            print("Brzeg zapchany! Uruchamiam awaryjne szukanie miejsca...")
            wolne_pole = self.find_free_space_around(port["x"], port["y"], radius=3)
            
        # 2. Tworzenie nowej armii na bezpiecznym brzegu
        lider = nowy_garnizon[0]
        lider.x, lider.y = wolne_pole[0], wolne_pole[1]
        lider.garrison = [None] * 10
        
        for i, u in enumerate(nowy_garnizon[1:]):
            if i < 10:
                lider.garrison[i] = u
                
        self.units.append(lider)
        if hasattr(lider, 'owner') and lider.owner:
            lider.owner.units.append(lider)
            
        # 3. START ODLICZANIA 10 TUR!
        port["pending_count"] = 0
        port["garrison"] = []
        port["has_ship"] = False
        port["ship_timer"] = 0
        port["cooldown"] = 10 
        
        triggering_unit.planned_path = []
        triggering_unit.target_x = None
        triggering_unit.target_y = None

    def setup_starting_units(self):
        """Rozdaje graczom początkowe wojsko pod ich zamkami."""
        generals_created = [] # Zbieramy generałów, żeby jednego od razu uwięzić do testów
        # --- NOWOŚĆ: STARTOWY STATEK W PORCIE ---
        if hasattr(self, 'ports'):
            for port in self.ports:
                self.spawn_port_reinforcements(port)

        for c in self.castles:
            if c.owner:
                owner_obj = self.players[c.owner] if isinstance(c.owner, int) else c.owner
                
                # 1. PIECHOTA
                start_x = int(c.x)
                start_y = int(c.y + 2)
                infantry = Unit("INFL", start_x, start_y, owner_obj)
                self.add_unit(infantry)
                
                # 2. BUDOWNICZY
                start_x = int(c.x + 2)
                start_y = int(c.y)
                builder = Unit("BUDOW", start_x, start_y, owner_obj)
                self.add_unit(builder)               
                
                # 3. GENERAŁ (NOWOŚĆ)
                gen_x = int(c.x + 1)
                gen_y = int(c.y + 2)
                general = Unit("Generał", gen_x, gen_y, owner_obj)
                general.is_general = True
                general.hp = 200 # Generał zazwyczaj jest dużo wytrzymalszy
                self.add_unit(general)
                
                generals_created.append(general)

        # ========================================================
        # TYMCZASOWE NA POTRZEBY WALKI - NIEBIESKI BUDOWNICZY
        # ========================================================
        # 1. Szukamy niebieskiego gracza
        blue_player = None
        for p in self.players:
            if getattr(p, 'color_name', '').lower() == 'blue':
                blue_player = p
                break

        # 2. Szukamy czerwonego zamku
        red_castle = None
        for c in self.castles:
            owner = self.players[c.owner] if isinstance(c.owner, int) else c.owner
            if getattr(owner, 'color_name', '').lower() == 'red':
                red_castle = c
                break

        # 3. Dodajemy go na mapę!
        if red_castle and blue_player:
            spawn_x = int(red_castle.x + 3)
            spawn_y = int(red_castle.y)
            
            new_builder = Unit("BUDOW", spawn_x, spawn_y, blue_player)
            self.add_unit(new_builder) # Używamy bezpiecznej funkcji gry
            
            print(f"DEBUG: Dodano niebieskiego Budowniczego na pozycję ({spawn_x}, {spawn_y}) obok Czerwonego Zamku!")
                
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
      
        # --- 1. ZAPISUJEMY LOCHY I AKCJE GRACZA, KTÓRY KOŃCZY TURĘ ---
        old_player = self.players[self.current_player]
        if hasattr(self, 'court_states') and old_player.id in self.court_states:
            self.court_states[old_player.id]["slots"] = list(self.court.prison_slots)
            self.court_states[old_player.id]["action"] = self.court.selected_prison_action

        # Przełączamy gracza (TYLKO JEDEN RAZ!)
        self.current_player = (self.current_player + 1) % len(self.players)
        
        # --- 2. WCZYTUJEMY LOCHY I AKCJE GRACZA, KTÓRY ZACZYNA TURĘ ---
        new_player = self.players[self.current_player]
        if hasattr(self, 'court_states') and new_player.id in self.court_states:
            self.court.prison_slots = self.court_states[new_player.id]["slots"]
            self.court.selected_prison_action = self.court_states[new_player.id]["action"]
        
        # ZMIANA: Przekazujemy gracza kończącego turę!
        self.reset_units(old_player)
        # ================================================
        self.active_dropdown = None 
        self.build_menu_open = False 
        self.selected_castle = None
        self.selected_unit = None
        self.screen = "map"
        
      # =========================================================
        # ---> DODAJ TE 4 LINIJKI: Twardy reset trybów budowy <---
        # =========================================================
        self.road_build_mode = False
        self.trap_build_mode = False
        self.active_builder_army = None
        self.active_builder_unit = None
        # =========================================================

        # ---> KLUCZOWA POPRAWKA 3: Twardy reset krzyżyków w koszarach! <---
        self.selected_units.clear()

        # --- KLUCZ: Logika zamków i budowania odpala się TYLKO raz na rundę ---
        if self.current_player == 0:
            self.turn += 1
            self.process_construction() 
            self.update_ports_turn() # <--- TEGO BRAKOWAŁO (Znika statek po 1 turze!)
            for castle in self.castles:
                if not getattr(castle, 'destroyed', False):
                    if hasattr(castle, 'next_turn'):
                        castle.next_turn() 
                    
                   # ---> KLUCZOWA POPRAWKA 2: Przetwarzanie leczenia i szkolenia <---
                    for u in getattr(castle, 'garrison', []):
                        if u:
                            # ================================================
                            # ZMIANA: Odpoczynek w zamku zdejmuje aż 50 zmęczenia!
                            # ================================================
                            u.fatigue = max(0, getattr(u, 'fatigue', 0) - 50)
                            
                            # Odzyskiwanie morale do poziomu podstawowego
                            base_morale = 10 
                            from settings import UNIT_STATS
                            u_name = getattr(u, 'type_code', getattr(u, 'type', ''))
                            if u_name in UNIT_STATS:
                                base_morale = UNIT_STATS[u_name].get("morale", 10)
                                
                            if getattr(u, 'morale', 10) < base_morale:
                                u.morale += 1

                            base_moves = getattr(u, 'moves', 5)
                            u.move_points = base_moves
                            u.turn_start_mp = base_moves
                            # ================================================

                            # Przetwarzanie Leczenia (Szpital - Serduszka)
                            if getattr(u, 'healing_turns', 0) > 0:
                                u.healing_turns -= 1
                                if u.healing_turns <= 0:
                                    u.hp = getattr(u, 'max_hp', 100) # Leczmy na 100%
                                    print(f"[{castle.x},{castle.y}] Wyleczono jednostkę: {u.type}")
                            
                            # Przetwarzanie Szkolenia (Szkoła - Miecze)
                            if getattr(u, 'training_turns', 0) > 0:
                                u.training_turns -= 1
                                if u.training_turns <= 0:
                                    # Złoty posąg to max 12 pkt doświadczenia
                                    u.experience = min(12, getattr(u, 'experience', 0) + 3) 
                                    print(f"[{castle.x},{castle.y}] Wyszkolono jednostkę: {u.type}")
        self.check_trap_detection()

    def move_unit(self, unit, dx, dy, cost=1):
        # 0. BLOKADA ZOMBIE I TURY (Bezpieczeństwo absolutne)
        if getattr(unit, 'hp', 100) <= 0:
            print("Mroczne siły zablokowane: Zombie nie mają prawa ruchu!")
            if self.selected_unit == unit:
                self.selected_unit = None
            return False

        if unit.owner != self.players[self.current_player]:
            print("DEBUG: Nie Twoja tura!")
            return False

        nx, ny = unit.x + dx, unit.y + dy

        # Sprawdzamy czy na tym polu stoi wróg (jednostka lub budowany zamek)
        is_attack = False
        for other in self.units:
            if other.x == nx and other.y == ny and other.owner != unit.owner:
                is_attack = True
                break
                
        if not is_attack:
            for castle in self.castles:
                size = 2 if getattr(castle, 'building_type', 'Zamek') in ["Zamek", "Twierdza"] else 1
                if castle.x <= nx < castle.x + size and castle.y <= ny < castle.y + size:
                    if castle.owner != unit.owner and getattr(castle, 'under_construction', False):
                        is_attack = True
                        break

        # 1. Sprawdzenie punktów ruchu (Ignorujemy przy ataku na sąsiada!)
        if not is_attack:
            if unit.move_points < cost:
                print(f"DEBUG: Jednostka {unit.type} nie ma MP ({unit.move_points} < {cost}).")
                return False
            if unit.has_fatigue_paralysis():
                print("Armia nie może się ruszyć - ktoś jest skrajnie wyczerpany!")
                return False
            effective_mp = unit.get_effective_move_points()
            if effective_mp < cost:
                print("Armia nie może się ruszyć - ogranicza ją najsłabszy członek!")
                return False
        # ========================================================

        nx, ny = unit.x + dx, unit.y + dy

        # 2. Granice mapy
        if not (0 <= nx < len(self.map[0]) and 0 <= ny < len(self.map)):
            return False

       # 3. INTERAKCJA Z ZAMKIEM (Obszar 2x2 dla Zamków, 1x1 dla Strażnic)
        for castle in self.castles:
            size = 2 if getattr(castle, 'building_type', 'Zamek') in ["Zamek", "Twierdza"] else 1
            if castle.x <= nx < castle.x + size and castle.y <= ny < castle.y + size:
                if getattr(castle, 'destroyed', False):
                    continue

                # ==========================================
                # --- ZAMEK SOJUSZNIKA ---
                # ==========================================
                if castle.owner == unit.owner:
                    # BLOKADA WEJŚCIA: Jeśli trwa budowa, sojusznik nie może wejść!
                    if getattr(castle, 'under_construction', False):
                        print("Plac budowy - sojusznicy nie mogą wchodzić dopóki nie zostanie ukończony!")
                        return False # Zatrzymujemy jednostkę bez pobierania punktów ruchu
                        
                    # Jeśli to gotowy zamek - wchodzimy normalnie
                    unit.move_points -= cost 
                    if self.enter_castle(unit, castle):
                        return True
                    else:
                        unit.move_points += cost
                        print("Brak miejsca w garnizonie! Armia zostaje przed zamkiem.")
                        return False

                # ==========================================
                # --- ZAMEK WROGA ---
                # ==========================================
                else:
                    if getattr(castle, 'under_construction', False):
                        print("Wróg atakuje plac budowy!")
                        # Wyciągamy obrońców (budowniczych) z zamku by stanęli do walki
                        defenders = [u for u in castle.garrison if u is not None]
                        if defenders:
                            def_leader = defenders[0]
                            def_leader.x, def_leader.y = nx, ny
                            def_leader.garrison = [None] * 10
                            for i, d in enumerate(defenders[1:]):
                                if i < 10: def_leader.garrison[i] = d
                            
                            self.combat_attacker = unit
                            self.combat_defender = def_leader
                            self.combat_nx = nx
                            self.combat_ny = ny
                            self.combat_cost = cost
                            self.screen = "combat_setup"
                            self.center_camera_on(nx, ny)
                            self.combat_target_castle = castle
                            return False
                        else:
                            # Pusty plac budowy - niszczymy od razu!
                            print("Zniszczono pusty plac budowy wroga!")
                            castle.destroyed = True
                            if castle in self.castles:
                                self.castles.remove(castle)
                            for dy in range(size):
                                for dx in range(size):
                                    self.map[castle.y + dy][castle.x + dx] = "."
                            unit.x, unit.y = nx, ny
                            unit.move_points -= cost
                            return True
                    else:
                        # Normalne zdobycie gotowego zamku
                        print(f"Zamek na ({castle.x}, {castle.y}) został ZDOBYTY przez {unit.owner.color_name}!")
                        
                        # ========================================================
                        # KLUCZOWA POPRAWKA: Zapamiętanie "Pierworodnego" twórcy
                        # zanim zmienimy flagę na wieży!
                        # ========================================================
                        if not hasattr(castle, 'original_owner') or castle.original_owner is None:
                            castle.original_owner = castle.owner
                            
                        castle.owner = unit.owner
                        castle.garrison = [None] * getattr(castle, 'garrison_limit', 12) 
                        castle.production_enabled = False
                        castle.production_unit_type = None
                        
                        unit.move_points -= cost
                        if self.enter_castle(unit, castle):
                            return True
                        else:
                            # Zamek jest broniony!
                            print(f"Zamek jest broniony przez {defenders} jednostek! Nie można przejąć bez walki.")
                            return False
                        
       # ==========================================
        # 4. INTERAKCJA Z PORTEM (Odbieranie wojska)
        # ==========================================
        if self.map[ny][nx] == "R":
            target_port = next((p for p in getattr(self, 'ports', []) if p["x"] <= nx <= p["x"]+1 and p["y"] <= ny <= p["y"]+1), None)
            
            if target_port:
                # ZMIANA: Sprawdzamy nową zmienną z liczbą (oraz starą awaryjnie)
                if target_port.get("pending_count", 0) > 0 or target_port.get("garrison"): 
                    self.unload_port(target_port, unit)
                else:
                    print("Port jest pusty, czekamy na posiłki.")
            
            # Jednostka zostaje na brzegu
            return False

        # ==========================================
        # 4.5. INTERAKCJA Z PUŁAPKĄ (BUM!)
        # ==========================================
        if self.map[ny][nx] == "X":
            trap = getattr(self, 'traps', {}).get((nx, ny))
            
            if trap and trap["owner"] != unit.owner:
                
                # ---> NOWOŚĆ: Awaryjne hamowanie! <---
                # Jeśli pułapka została już odkryta przez nasz radar, zatrzymujemy marsz!
                if unit.owner in trap.get("detected_by", set()):
                    print("Dowódca: Zauważono pułapkę! Zatrzymuję oddział.")
                    unit.planned_path = [] # Kasujemy dotychczasowy plan marszu
                    return False # Jednostka się zatrzymuje przed pułapką, nie tracąc PA!
                
                print(f"BUM! Jednostka {unit.type} wpadła w pułapkę na ({nx}, {ny})!")
                
                # Zbieramy całą armię (lider + pasażerowie)
                army_in_trap = [unit]
                if hasattr(unit, 'garrison'):
                    army_in_trap.extend([u for u in unit.garrison if u is not None])
                
                import random
                for u in army_in_trap:
                    obrona = getattr(u, 'defense', 5) 
                    
                    if obrona < 3: dmg_pct = random.randint(95, 100)
                    elif 3 <= obrona <= 5: dmg_pct = random.randint(70, 85)
                    elif 6 <= obrona <= 9: dmg_pct = random.randint(50, 60)
                    elif 10 <= obrona <= 15: dmg_pct = random.randint(35, 45)
                    else: dmg_pct = random.randint(12, 20)
                    
                    max_hp = getattr(u, 'max_hp', 100)
                    dmg_value = int(max_hp * (dmg_pct / 100.0))
                    u.hp -= dmg_value
                    
                    if u.hp <= 0:
                        if u in self.units: self.units.remove(u)
                        if u.owner and u in u.owner.units: u.owner.units.remove(u)
                        if self.selected_unit == u: self.selected_unit = None
                        if hasattr(unit, 'garrison') and u in unit.garrison:
                            unit.garrison[unit.garrison.index(u)] = None

                original_bg = getattr(self, 'trap_backgrounds', {}).get((nx, ny), ".")
                self.map[ny][nx] = original_bg
                if (nx, ny) in self.traps:
                    del self.traps[(nx, ny)]
                
                # ========================================================================
                # KLUCZ: Zatrzymujemy jednostkę bezwzględnie w miejscu wybuchu!
                # ========================================================================
                unit.planned_path = []
                unit.target_x = None
                unit.target_y = None
                
                if unit.hp <= 0:
                    ocalali = [u for u in getattr(unit, 'garrison', []) if u is not None and u.hp > 0]
                    
                    if ocalali:
                        nowy_lider = ocalali[0]
                        nowy_lider.x, nowy_lider.y = nx, ny 
                        nowy_lider.garrison = [None] * 10
                        for i, u in enumerate(ocalali[1:]):
                            if i < 10: nowy_lider.garrison[i] = u
                        
                        if nowy_lider not in self.units: self.units.append(nowy_lider)
                        if nowy_lider.owner and nowy_lider not in nowy_lider.owner.units:
                            nowy_lider.owner.units.append(nowy_lider)
                            
                        self.selected_unit = nowy_lider 
                        print(f"Nowym dowódcą armii na polu ({nx}, {ny}) zostaje: {nowy_lider.type}!")
                    else:
                        print("Oddział unicestwiony.")
                        if self.selected_unit == unit: self.selected_unit = None
                        
                    return True # Wychodzimy, bo stary lider nie żyje
                
                # Reszta kodu rusza się na pole wybuchu jeśli przeżyła, ale już NIE PÓJDZIE DALEJ
                
        # ==========================================
        # 5. TEREN (Zwykłe chodzenie po mapie)
        # ==========================================
        # Dodałem "X" do listy, aby zapobiec ewentualnym błędom silnika
        walkable_chars = [".", "l", "g", "p", "_", "#", "$", "x", "X", " "] 
        map_char = self.map[ny][nx]
        if map_char not in walkable_chars:
            return False

        # ==========================================
        # 6. NIEWIDOCZNE PUŁAPKI (Zatrzymanie i pop-up)
        # ==========================================
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
        
        # 6. WALKA I ŁĄCZENIE
        for other in self.units[:]:
            if other.x == nx and other.y == ny:
                if other.owner != unit.owner:
                    # ==========================================
                    # TO JEST WRÓG -> WYWOŁANIE EKRANU WALKI
                    # ==========================================
                    # Zawieszamy ruch, zapisujemy parametry bitwy i pokazujemy pergamin!
                    self.combat_attacker = unit
                    self.combat_defender = other
                    self.combat_nx = nx
                    self.combat_ny = ny
                    self.combat_cost = cost
                    self.screen = "combat_setup"
                    
                    self.center_camera_on(nx, ny) # Centrujemy kamerę, by ładnie wyglądało w tle
                    return False # Zatrzymujemy jednostkę w miejscu. Walka dokończy się po kliknięciu!
                    # Jeśli przeżył, skrypt pójdzie dalej i poprawnie postawi go na nowym polu!
                    
                else:
                    # TO JEST SOJUSZNIK! Sprawdzamy czy chcieliśmy się łączyć
                    if getattr(self, 'merge_mode', False):
                        self.merge_units(unit, other, cost)
                        return False 
                    else:
                        return False # Blokada - nie można wejść na sojusznika bez łączenia
                        
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
        
        # --- NOWOŚĆ: Zużywamy PA wszystkim w armii! ---
        if hasattr(unit, 'garrison'):
            for pas in unit.garrison:
                if pas is not None:
                    pas.move_points -= cost
        self.check_trap_detection()
        return True
    
    def check_trap_detection(self):
        """Uruchamia radar jednostek i wykrywa ukryte pułapki."""
        current_player = self.players[self.current_player]
        my_units = [u for u in self.units if u.owner == current_player and u.x >= 0]
        
        zlote_ladowe = ["Rycerstwo", "Dragon", "Mag", "Kapłan", "Mnich", "Kusznik z gildii"]
        zlote_latajace = ["Gryf", "Orzeł", "Smok", "Pegaz", "Ważka"]
        
        for tx, ty in list(getattr(self, 'traps', {}).keys()):
            trap = self.traps[(tx, ty)]
            if trap["owner"] == current_player: continue
            if current_player in trap.get("detected_by", set()): continue
            
            for u in my_units:
                dystans = ((u.x - tx)**2 + (u.y - ty)**2)**0.5
                zasieg_radaru = 0
                
                # ---> ZMIENIONE: Weterani (lvl >= 12) i Generał widzą pułapkę z 3,5 pola <---
                if u.type in zlote_latajace: 
                    zasieg_radaru = 6.5
                elif u.type in zlote_ladowe or u.type == "Generał" or getattr(u, 'is_general', False) or getattr(u, 'experience', 0) >= 12: 
                    zasieg_radaru = 3.5
                
                if zasieg_radaru > 0 and dystans <= zasieg_radaru:
                    if "detected_by" not in trap: trap["detected_by"] = set()
                    trap["detected_by"].add(current_player)
                    print(f"!!! Pułapka na ({tx},{ty}) została WYKRYTA przez {u.type} !!!")
                    break

    def reset_units(self, old_player=None):
        # Funkcja wewnętrzna resetująca pojedynczego żołnierza (nawet tego w armii)
        def _reset_single(u_obj):
            if old_player and u_obj.owner == old_player:
                start_mp = getattr(u_obj, 'turn_start_mp', getattr(u_obj, 'moves', 5))
                
                # 1. Jeśli jednostka W OGÓLE się nie ruszyła (odpoczynek w polu)
                if u_obj.move_points >= start_mp:
                    u_obj.fatigue = max(0, getattr(u_obj, 'fatigue', 0) - 20)
                # 2. Jeśli jednostce zostało MNIEJ niż 4 PA (rośnie zmęczenie)
                elif u_obj.move_points < 4:
                    u_obj.fatigue = min(100, getattr(u_obj, 'fatigue', 0) + 10)
                # 3. W przeciwnym razie (ruszyła się, ale ma 4 lub więcej PA) -> zmęczenie bez zmian.
            
            # Wpływ zmęczenia na max punkty ruchu w nowej turze
            base_moves = getattr(u_obj, 'moves', 5)
            fatigue = getattr(u_obj, 'fatigue', 0)
            if fatigue >= 100: new_mp = 0
            elif fatigue >= 90: new_mp = int(base_moves * 0.5)
            elif fatigue >= 80: new_mp = int(base_moves * 0.75)
            else: new_mp = base_moves
            
            u_obj.move_points = new_mp
            u_obj.turn_start_mp = new_mp

        # Pętla przez wszystkie jednostki na mapie oraz ich pasażerów w armii
        for u in self.units:
            if u.x < 0:
                continue
            _reset_single(u)
            if hasattr(u, 'garrison'):
                for pas in u.garrison:
                    if pas is not None:
                        _reset_single(pas)

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

    def update_castle_visuals(self, castle, new_owner):
        """
        Aktualizuje grafikę zamku.
        Sprawdza, czy istnieje specjalna grafika dla przejęcia (captured_by),
        w przeciwnym razie używa grafiki dla aktualnego etapu budowy.
        """
        current_color = castle.owner.color.lower()
        new_color = new_owner.color.lower()
        
        # Pobieramy bazowy słownik dla koloru zamku
        color_data = self.castle_color_frames.get(current_color, {})
        
        # Sprawdzamy czy istnieje sekcja 'captured_by' i czy jest tam wpis dla nowego właściciela
        if "captured_by" in color_data and new_color in color_data["captured_by"]:
            # Zastosuj grafikę dla przejęcia
            castle.current_tiles = color_data["captured_by"][new_color]
        else:
            # W przeciwnym razie użyj standardowego etapu budowy
            stage = getattr(castle, 'construction_stage', 0)
            castle.current_tiles = color_data.get(stage, [0, 0, 0, 0])
            
        print(f"DEBUG: Zamek na ({castle.x}, {castle.y}) zmieniony na {new_color}")

    def create_unit(self, unit_type, x, y, owner):
        u = Unit(unit_type, x, y, owner)
        self.add_unit(u)
        return u
     
    def handle_garrison_click(self, mx, my, button):
        castle = self.selected_castle
        if not castle:
            return

        # ================= BACK =================
        if hasattr(self, 'back_button_garrison') and self.back_button_garrison.collidepoint(mx, my):
            self.selected_units.clear() 
            # --- ZMIANA: Zamek ZAWSZE wraca na dziedziniec ---
            self.screen = "castle"
            
            if hasattr(self, 'recruitment_manager'):
                self.recruitment_manager.selected_patent_index = None
            return

        # ================= RECRUITMENT =================
        if self.garrison_gfx.handle_prod_click(mx, my, castle):
            
            # --- POPRAWIONA NAZWA ---
            if hasattr(self, 'recruitment_manager'):
                self.recruitment_manager.selected_patent_index = None
                
            self.prod_anim_timer = pygame.time.get_ticks() 
            return

        # ================= HEAL =================
        if self.garrison_gfx.handle_hosp_click(mx, my, castle):
            if self.selected_units:
                for u in self.selected_units:
                    if getattr(u, 'hp', 100) < getattr(u, 'max_hp', 100):
                        u.healing_turns = 3 
                        u.training_turns = 0  # <--- NOWOŚĆ: Leczenie wyłącza szkolenie
                self.selected_units.clear() 
                print("Rozpoczęto leczenie (Szkolenie przerwane)")
            return

        # ================= TRAIN ================= 
        if self.garrison_gfx.handle_school_click(mx, my, castle):
            if self.selected_units:
                # ... (twoja logika szkolenia) ...
                for u in self.selected_units:
                    u.training_turns = 3  
                    u.healing_turns = 0  # <--- NOWOŚĆ: Szkolenie wyłącza leczenie
                self.selected_units.clear() 
                print("Rozpoczęto szkolenie (Leczenie przerwane)")
            return
        
        # ================= WYPUŚĆ WOJSKO =================
        if self.garrison_gfx.handle_release_click(mx, my, self.selected_units):
            print("Akcja: Wypuszczanie zaznaczonych jednostek z garnizonu")
            self.release_selected_units(stay_in_menu=True) 
            return
        
        # ================= SELEKCJA JEDNOSTEK W SLOTACH =================
        rects = getattr(self, 'garrison_slot_rects', self.garrison_gfx.slot_rects)
        index = None
        for i, rect in enumerate(rects):
            if rect.collidepoint(mx, my):
                index = i
                break
                
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
                # ---> KLUCZOWA POPRAWKA 1: Sztywny limit 10 jednostek do armii! <---
                if len(self.selected_units) < 10:
                    self.selected_units.append(unit)
                else:
                    print("Maksymalna wielkość armii (10) osiągnięta! Nie możesz zaznaczyć więcej.")

    def handle_straznica_click(self, mx, my, button):
        castle = self.selected_castle
        if not castle:
            return

        # Ta funkcja NIE SPRAWDZA przycisków Powrotu/Wypuść.
        # Obsługuje wyłącznie kafelki jednostek w Strażnicy!

        # ================= SELEKCJA JEDNOSTEK W SLOTACH =================
        # Pobieramy prostokąty wygenerowane w renderer.py
        rects = getattr(self, 'garrison_slot_rects', [])
        index = None
        for i, rect in enumerate(rects):
            if rect.collidepoint(mx, my):
                index = i
                break
                
        if index is None or index >= len(castle.garrison):
            return

        unit = castle.garrison[index]

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
                # Sztywny limit 10 jednostek do armii!
                if len(self.selected_units) < 10:
                    self.selected_units.append(unit)
                else:
                    print("Maksymalna wielkość armii (10) osiągnięta! Nie możesz zaznaczyć więcej.")
    
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
        # Ignorujemy jednostki, których już nie ma fizycznie na mapie
        if unit.x < 0 or unit.y < 0:
            return False
            
        for castle in self.castles:
            size = 2 if getattr(castle, 'building_type', 'Zamek') in ["Zamek", "Twierdza"] else 1
            if castle.x <= unit.x < castle.x + size and castle.y <= unit.y < castle.y + size:
                if castle.owner == unit.owner:
                    print(f"[{unit.type}] Osiągnięto cel - wchodzę do garnizonu!")
                    # Używamy tej samej funkcji rozpakowującej!
                    return self.enter_castle(unit, castle)
        return False
                  
    def enter_castle(self, unit, castle):
        """Przenosi lidera i wojsko do garnizonu, a Złoto do skarbca."""
        
        # 1. Zbieramy całą armię z pola
        raw_to_enter = [unit]
        if hasattr(unit, 'garrison') and unit.garrison:
            raw_to_enter.extend([u for u in unit.garrison if u is not None])

        # ============================================================
        # NOWOŚĆ: Oddzielamy Złoto od wojska! Złoto zasila skarbiec.
        # ============================================================
        # ============================================================
        # NOWOŚĆ: Oddzielamy Złoto i Chłopów od wojska! 
        # ============================================================
        to_enter = []
        for u in raw_to_enter:
            # --- ZŁOTO ---
            if u.type == "Złoto" or getattr(u, 'type_code', '') == "GOLD":
                wartosc_zlota = getattr(u, 'hp', 100)
                castle.gold += wartosc_zlota
                print(f"[{castle.x},{castle.y}] Do skarbca trafiło {wartosc_zlota} złota! Obecny stan: {castle.gold}")
                
                u.x, u.y = -1, -1
                if u in self.units: self.units.remove(u)
                if u.owner and u in u.owner.units: u.owner.units.remove(u)
            
            # --- CHŁOPI ---
            elif u.type == "Chłop" or getattr(u, 'type_code', '') == "PEAS":
                ilosc_chlopow = getattr(u, 'hp', 100) # Ilość przechowujemy w HP
                castle.peasants = getattr(castle, 'peasants', 0) + ilosc_chlopow
                print(f"[{castle.x},{castle.y}] Do zamku weszło {ilosc_chlopow} chłopów! Obecny stan: {castle.peasants}")
                
                u.x, u.y = -1, -1
                if u in self.units: self.units.remove(u)
                if u.owner and u in u.owner.units: u.owner.units.remove(u)
                
            # --- PRAWDZIWE WOJSKO ---
            else:
                to_enter.append(u) 

        # Jeśli do zamku wjechał TYLKO sam zasób, zamykamy operację z sukcesem.
        if not to_enter:
            if hasattr(unit, 'garrison'): unit.garrison = [None] * 10
            self.selected_unit = None
            return True
        
        # 2. Sprawdzamy wolne miejsca dla prawdziwego wojska
        free_slots = [i for i, slot in enumerate(castle.garrison) if slot is None]
        
        if len(to_enter) > len(free_slots):
            print(f"Brak miejsca w zamku! Próbujesz wprowadzić {len(to_enter)} oddziałów, a wolnych jest {len(free_slots)}.")
            return False

        # 3. Rozpakowujemy wojsko do osobnych slotów
        for idx, u_to_add in enumerate(to_enter):
            target_slot = free_slots[idx]
            castle.garrison[target_slot] = u_to_add
            
            u_to_add.x, u_to_add.y = -1, -1
            if u_to_add in self.units: self.units.remove(u_to_add)
            if u_to_add.owner and u_to_add in u_to_add.owner.units: u_to_add.owner.units.remove(u_to_add)

        # 4. Czyścimy "plecak" dowódcy
        if hasattr(unit, 'garrison'):
            unit.garrison = [None] * 10

        self.selected_unit = None
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
                
                # Usuwanie ze slotu zamku (Szukamy, w którym slocie siedział)
                for slot_idx in range(len(target.garrison)):
                    if target.garrison[slot_idx] is solo_unit:
                        
                        # 1. ŁAPIEMY DUCHA
                        ghost_to_save = target.garrison[slot_idx]
                        
                        # 2. CZYŚCIMY SLOT ZAMKU
                        target.garrison[slot_idx] = None
                        
                        # 3. ZAMYKAMY DRZWI (Z naszym duchem!)
                        if hasattr(self, 'garrison_gfx'):
                            self.garrison_gfx.trigger_door_close(slot_idx, ghost_to_save)
                            
                        break
                # ---> NOWOŚĆ: Reset statusów przy wyjściu <---
                solo_unit.healing_turns = 0
                solo_unit.training_turns = 0
                
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
                leader = group[0]
                leader.x, leader.y = nx, ny
                leader.garrison = [None] * 10 
                
                for unit_to_clear in group:
                    # ---> NOWOŚĆ: Reset statusów dla każdego członka armii <---
                    unit_to_clear.healing_turns = 0
                    unit_to_clear.training_turns = 0
                    for slot_idx in range(len(target.garrison)):
                        if target.garrison[slot_idx] is unit_to_clear:
                            
                            # 1. ŁAPIEMY DUCHA
                            ghost_to_save = target.garrison[slot_idx]
                            
                            # 2. CZYŚCIMY SLOT ZAMKU
                            target.garrison[slot_idx] = None
                            
                            # 3. ZAMYKAMY DRZWI (Z naszym duchem!)
                            if hasattr(self, 'garrison_gfx'):
                                self.garrison_gfx.trigger_door_close(slot_idx, ghost_to_save)
                                
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
        """Łączy dwie armie w jedną, zachowując indywidualne punkty ruchu."""
        # 1. Przygotowanie listy: Lider + jego garnizon
        to_add = [moving_unit]
        if hasattr(moving_unit, 'garrison') and moving_unit.garrison:
            to_add.extend([u for u in moving_unit.garrison if u is not None])

        # 2. NAPRAWA: Zabezpieczenie przed pustą listą [] (Dzięki temu łączy armie!)
        if not hasattr(target_unit, 'garrison') or not target_unit.garrison:
            target_unit.garrison = [None] * 10
            
        free_slots = [i for i, slot in enumerate(target_unit.garrison) if slot is None]
        
        if len(to_add) > len(free_slots):
            print(f"Brak miejsca! Próbujesz dodać {len(to_add)} jedn., a masz tylko {len(free_slots)} slotów.")
            self.merge_mode = False
            return False 

        # 3. Jeśli jest miejsce - przenosimy jednostki
        for unit_to_add in to_add:
            slot_idx = free_slots.pop(0) 
            target_unit.garrison[slot_idx] = unit_to_add
            
            unit_to_add.x, unit_to_add.y = -1, -1
            if unit_to_add in self.units:
                self.units.remove(unit_to_add)
            if unit_to_add.owner and unit_to_add in unit_to_add.owner.units:
                unit_to_add.owner.units.remove(unit_to_add)

        # 4. Czyścimy starego lidera
        if hasattr(moving_unit, 'garrison'):
            moving_unit.garrison = [None] * 10 

        # 5. NAPRAWA: ZABIERAMY TYLKO KOSZT RUCHU (Nie wyrównujemy wszystkim w dół!)
        # Świeże jednostki zachowają swoje PA, będą miały szare krzyżyki i dadzą się odłączyć!
        for u in to_add:
            u.move_points = max(0, u.move_points - cost)

        self.merge_mode = False
        self.selected_unit = target_unit 
        print("Połączono pomyślnie armie!")
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

    def capture_prisoner(self, captured_unit, captor_player):
        """Wtrąca pojmanego generała do lochu gracza, który wygrał bitwę."""
        if not getattr(captured_unit, 'is_general', False):
            return False 
            
        # Pobieramy magazyn lochów dedykowany dla gracza, który dokonał pojmania
        if hasattr(self, 'court_states') and captor_player.id in self.court_states:
            slots = self.court_states[captor_player.id]["slots"]
        else:
            slots = self.court.prison_slots # failsafe
                
        for slot in slots:
            if slot.general is None:
                slot.general = captured_unit
                
                # Ukrywamy jednostkę w lochu (zdejmujemy z planszy mapy świata)
                captured_unit.x, captured_unit.y = -1, -1
                if captured_unit in self.units:
                    self.units.remove(captured_unit)
                if captured_unit.owner and captured_unit in captured_unit.owner.units:
                    captured_unit.owner.units.remove(captured_unit)
                    
                print(f"BITWA: Generał gracza {captured_unit.owner.name} zamknięty w lochu u {captor_player.name}!")
                return True
                
        print("BITWA: Brak wolnych cel! Generał uciekł.")
        return False

    def kill_unit(self, unit, killer_player=None):
        """Uniwersalna funkcja do zabijania jednostek. Sprawdza, czy to generał do wzięcia w niewolę."""
        if getattr(unit, 'is_general', False) and killer_player:
            # Jeśli to generał, próbujemy wziąć do niewoli
            captured = self.capture_prisoner(unit, killer_player)
            if captured: 
                return # Sukces, wylądował w lochu, nie zabijamy go!
            
        # Standardowe usuwanie (śmierć)
        unit.x, unit.y = -1, -1
        if unit in self.units:
            self.units.remove(unit)
        if unit.owner and unit in unit.owner.units:

            unit.owner.units.remove(unit)

    # world.py -> update the visit_temple function

    def visit_temple(self, unit, gx, gy):
        # =======================================================
        # 0. KONTROLA DOSTĘPU: Kto próbuje wejść?
        # =======================================================
        army = [unit]
        if hasattr(unit, 'garrison') and unit.garrison:
            army.extend([u for u in unit.garrison if u is not None])
            
        has_combat_unit = False
        for u in army:
            u_type = getattr(u, 'type', '')
            is_gen = getattr(u, 'is_general', False)
            if u_type not in ["Generał", "Złoto", "Chłop"] and not is_gen:
                has_combat_unit = True
                break
                
        if not has_combat_unit:
            # Otwieramy normalny pergamin, ale z informacją o odrzuceniu!
            self.temple_title = "Zakaz wstępu"
            self.temple_desc = "Święte miejsca mogą badać tylko wojownicy. Chłopi, wóz ze złotem ani sam głównodowodzący nie mogą tam wejść bez zbrojnej eskorty!"
            self.temple_current_effect = None 
            self.screen = "temple_event"
            return # Przerywamy funkcję - miejsce pozostaje "niezbadane" i czeka na wojsko!

        # 1. SPRAWDZAMY LIMIT: Czy ktoś już tu był?
        if (gx, gy) in self.visited_temples:
            self.temple_title = "Pusta Świątynia"
            self.temple_desc = "Ołtarz jest pusty. Ktoś już zabrał stąd dary."
            self.temple_current_effect = None # Pusty pergamin
            self.screen = "temple_event"
            return 

        # 2. ZAPISUJEMY ŚWIĄTYNIĘ JAKO ODWIEDZONĄ
        self.visited_temples.add((gx, gy))
        
        loot = self.loot_manager.get_temple_loot() 
        temple_type = self.map[gy][gx]
        player = self.players[self.current_player]
        
        # Logika sprawdzenia frakcji
        is_worthy = (temple_type == "S" and player.faction == "catholic") or \
                    (temple_type == "&" and player.faction == "pagan")

        if is_worthy:
            self.temple_title = loot["title"]
            
            if isinstance(loot["desc"], list):
                import random
                self.temple_desc = random.choice(loot["desc"])
            else:
                self.temple_desc = loot["desc"]
                
            self.temple_current_effect = loot["img"]
            img_id = loot.get("img_id")
            
            # --- ZBIERAMY CAŁY ODDZIAŁ DO KUPY ---
            army = [unit]
            if hasattr(unit, 'garrison') and unit.garrison:
                army.extend([u for u in unit.garrison if u is not None])

            # --- APLIKUJEMY EFEKTY ---
            if img_id == 1:
                wylosowane = self.spawn_temple_army(player, gx, gy)
                if wylosowane:
                    nazwy = ", ".join(wylosowane)
                    self.temple_desc += f" Dołączają do Ciebie: {nazwy}!"
                    
            # ID 13, 14, 15 to Nagrody Pieniężne
            elif img_id in [13, 14, 15]:
                import re
                liczby = [int(n) for n in re.findall(r'\d+', self.temple_desc)]
                ilosc_zlota = max(liczby) if liczby else 100
                
                print(f"[DEBUG ŚWIĄTYNIA] Znalezione liczby: {liczby}. Wybrano: {ilosc_zlota}")
                self.spawn_gold_chunks(player, gx, gy, ilosc_zlota)

            if img_id in [2, 3, 4, 8, 12]:
                for u in army:
                    u.hp = getattr(u, 'max_hp', 100) 
                    
            if img_id in [3, 8, 11, 26]:
                for u in army:
                    u.fatigue = 0 
                    u.move_points = getattr(u, 'moves', 5) 
            
            if img_id in [5, 6]:
                for u in army:
                    u.experience = min(12, getattr(u, 'experience', 0) + 3) 
            elif img_id == 10:
                for u in army:
                    u.experience = min(12, getattr(u, 'experience', 0) + 2)

            if img_id in [7, 9]:
                for u in army:
                    u.morale = min(10, getattr(u, 'morale', 5) + 2) 
                    
            if img_id == 19:
                for u in army:
                    u.morale = max(0, getattr(u, 'morale', 5) - 2)
            elif img_id == 20:
                for u in army:
                    u.morale = 0
            elif img_id == 21: 
                for u in army:
                    u.morale = max(0, getattr(u, 'morale', 5) - 1)
                    u.fatigue = min(100, getattr(u, 'fatigue', 0) + 50) 
        else:
            # --- GRACZ JEST NIEGODNY (ZŁA FRAKCJA) ---
            self.temple_title = "Jesteś Niegodny"
            self.temple_desc = "Głupcze! Jak śmiałeś zakłócać spokój boski. Świętokradcy zostali ukarani bezwzględną śmiercią!"
            self.temple_current_effect = getattr(self, 'temple_lightning', None)
            
            # =======================================================
            # NOWOŚĆ: Piorun całkowicie unicestwia armię!
            # =======================================================
            do_usuniecia = [unit]
            if hasattr(unit, 'garrison') and unit.garrison:
                do_usuniecia.extend([u for u in unit.garrison if u is not None])
                
            for u in do_usuniecia:
                u.hp = 0
                u.x, u.y = -1, -1 # Ściągamy z mapy
                
                # Usuwamy ze świata i z zasobów gracza
                if u in self.units: 
                    self.units.remove(u)
                if u.owner and u in u.owner.units: 
                    u.owner.units.remove(u)
                
            # Odznaczamy jednostkę, żeby gracz nie miał podglądu na "ducha"
            if self.selected_unit == unit:
                self.selected_unit = None

        # =========================================================
        # 3. ZAWSZE OTWIERAMY EKRAN ŚWIĄTYNI NA KONIEC!
        # =========================================================
        self.screen = "temple_event"
    
    def trigger_treasure_ui(self, unit, gx, gy):
        loot = self.loot_manager.get_digging_loot()
        
        # --- DEBUG ---
        print(f"\n[DEBUG KOPANIA] Wylosowano skarb: {loot.get('title')}, ID: {loot.get('img_id')}")
        
        self.temple_title = loot["title"]
        if isinstance(loot["desc"], list):
            import random
            self.temple_desc = random.choice(loot["desc"])
        else:
            self.temple_desc = loot["desc"]
            
        self.temple_current_effect = loot["img"]
        
        # 1. Usuwamy skarb z mapy
        self.map[gy][gx] = "."
        
       # 2. GENEROWANIE ZŁOTA NA MAPIE (dla skarbu ID 15, 16)
        if loot.get("img_id") in [15, 16]: 
            import re
            # Zbieramy wszystkie liczby z tekstu i wybieramy najwyższą!
            liczby = [int(n) for n in re.findall(r'\d+', self.temple_desc)]
            ilosc_zlota = max(liczby) if liczby else 100
            
            print(f"[DEBUG KOPANIA] Znalezione liczby: {liczby}. Wybrano: {ilosc_zlota}")
            self.spawn_gold_chunks(unit.owner, gx, gy, ilosc_zlota)

        # 3. Otwieramy ekran
        self.screen = "temple_event"

    # --- NOWA FUNKCJA POMOCNICZA DO RODZENIA JEDNOSTEK ---
    def _spawn_unit_near(self, unit_name, owner, start_x, start_y):
        sasiedzi = [(start_x, start_y), (start_x-1, start_y), (start_x+1, start_y), 
                    (start_x, start_y-1), (start_x, start_y+1), (start_x-1, start_y-1), 
                    (start_x+1, start_y+1), (start_x-1, start_y+1), (start_x+1, start_y-1)]
        
        try:
            from unit import Unit 
        except ImportError as e:
            print(f"[DEBUG SPAWN] Błąd importu klasy Unit: {e}")
            return False
            
        for nx, ny in sasiedzi:
            if 0 <= nx < len(self.map[0]) and 0 <= ny < len(self.map):
                # POPRAWKA: Akceptujemy kropkę, podkreślnik i spację jako wolny teren!
                znak_mapy = self.map[ny][nx]
                if znak_mapy in [".", "_", " ","B", "b", "p", "P", "s", "l", "g", "G"]:
                    czy_zajete = any(u.x == nx and u.y == ny for u in self.units)
                    if not czy_zajete:
                        try:
                            # Tworzymy jednostkę
                            nowa_jednostka = Unit(unit_name, nx, ny, owner)
                            self.units.append(nowa_jednostka)
                            print(f"[DEBUG SPAWN] Sukces! [{unit_name}] pojawiło się na ({nx}, {ny})!")
                            
                            # ========================================================
                            # TUTAJ BYŁ BŁĄD: Zwracamy obiekt zamiast słowa "True"!
                            # ========================================================
                            return nowa_jednostka 
                        except Exception as e:
                            print(f"[DEBUG SPAWN] Błąd podczas tworzenia jednostki {unit_name}: {e}")
                            return False
                            
        print(f"[DEBUG SPAWN] Brak wolnego miejsca dla [{unit_name}] wokół ({start_x}, {start_y})!")
        return None
        
    def spawn_gold_chunks(self, owner, start_x, start_y, total_gold):
        print(f"\n--- [SYSTEM ZŁOTA] Pakowanie {total_gold} sztuk ---")
        
        chunks = []
        while total_gold > 0:
            chunk_val = min(total_gold, 100)
            chunks.append(chunk_val)
            total_gold -= chunk_val
            
        if not chunks:
            return
            
        print(f"Utworzono paczki: {chunks}")
            
        # 1. Tworzymy TYLKO JEDNĄ jednostkę fizycznie na mapie
        lider = self._spawn_unit_near("Złoto", owner, start_x, start_y)
        if lider:
            lider.hp = chunks[0]
            lider.max_hp = chunks[0]
            lider.garrison = [None] * 10
            
            # 2. Resztę ładujemy do garnizonu
            from unit import Unit
            for i, chunk_val in enumerate(chunks[1:]):
                if i < 10:
                    dodatkowe_zloto = Unit("Złoto", -1, -1, owner)
                    dodatkowe_zloto.hp = chunk_val
                    dodatkowe_zloto.max_hp = chunk_val
                    
                    lider.garrison[i] = dodatkowe_zloto
                    
                    if dodatkowe_zloto not in self.units:
                        self.units.append(dodatkowe_zloto)
                    if owner and dodatkowe_zloto not in owner.units:
                        owner.units.append(dodatkowe_zloto)
                        
            pasazerowie = sum(1 for u in lider.garrison if u is not None)
            print(f"SUKCES! Stos na mapie (HP: {lider.hp}). Wewnątrz dodatkowe paczki: {pasazerowie}\n")
        else:
            print("BŁĄD: Brak miejsca na mapie!")

    def spawn_peasant_group(self, owner, start_x, start_y, total_peasants):
        print(f"\n--- [SYSTEM CHŁOPÓW] Wysyłanie {total_peasants} chłopów z zamku ---")
        
        chunks = []
        while total_peasants > 0:
            chunk_val = min(total_peasants, 100)
            chunks.append(chunk_val)
            total_peasants -= chunk_val
            
        if not chunks:
            return
            
        print(f"Utworzono grupy chłopów: {chunks}")
            
        # 1. Tworzymy TYLKO JEDNĄ jednostkę na mapie (Lidera grupy)
        lider = self._spawn_unit_near("Chłopi", owner, start_x, start_y)
        if lider:
            lider.hp = chunks[0]
            lider.max_hp = chunks[0]
            lider.garrison = [None] * 10
            
            # 2. Resztę ładujemy do garnizonu (plecaka) lidera
            from unit import Unit
            for i, chunk_val in enumerate(chunks[1:]):
                if i < 10:
                    dodatkowi_chlopi = Unit("Chłopi", -1, -1, owner)
                    dodatkowi_chlopi.hp = chunk_val
                    dodatkowi_chlopi.max_hp = chunk_val
                    
                    lider.garrison[i] = dodatkowi_chlopi
                    
                    if dodatkowi_chlopi not in self.units:
                        self.units.append(dodatkowi_chlopi)
                    if owner and dodatkowi_chlopi not in owner.units:
                        owner.units.append(dodatkowi_chlopi)
                        
            pasazerowie = sum(1 for u in lider.garrison if u is not None)
            print(f"SUKCES! Grupa chłopów na mapie (Zasoby: {lider.hp}). Zapas w plecaku: {pasazerowie}\n")
        else:
            print("BŁĄD: Brak miejsca wokół zamku, by postawić chłopów!")

    def spawn_temple_army(self, owner, start_x, start_y):
        import random
        allowed_units = ["Skorpion", "Szkielet", "Troll", "Cyklop", "Ważka"]
        
        count = random.randint(1, 5)
        chosen_troops = []
        counts = {u: 0 for u in allowed_units}
        
        for _ in range(count):
            available = [u for u in allowed_units if counts[u] < 3]
            if not available: 
                break
            choice = random.choice(available)
            chosen_troops.append(choice)
            counts[choice] += 1
            
        print(f"Bogowie zsyłają oddział: {chosen_troops}")
        
        # 1. Pierwszy wylosowany potwór staje się LIDEREM na mapie
        lider_name = chosen_troops[0]
        lider = self._spawn_unit_near(lider_name, owner, start_x, start_y)
        
        if lider:
            # Upewniamy się, że lider ma pusty garnizon na 10 miejsc
            if not hasattr(lider, 'garrison') or not lider.garrison:
                lider.garrison = [None] * 10
            
            # 2. Resztę potworów tworzymy jako prawdziwe obiekty Unit i chowamy do garnizonu
            from unit import Unit
            for i, potwor_name in enumerate(chosen_troops[1:]):
                if i < 10:
                    # Tworzymy jednostkę "poza mapą" (-1, -1), bo siedzi w środku lidera
                    nowy_potwor = Unit(potwor_name, -1, -1, owner)
                    lider.garrison[i] = nowy_potwor
                    
                    # Rejestrujemy jednostki w świecie (by gra je widziała w bitwie)
                    if nowy_potwor not in self.units:
                        self.units.append(nowy_potwor)
                    if owner and nowy_potwor not in owner.units:
                        owner.units.append(nowy_potwor)
                        
        return chosen_troops # Zwracamy listę, żeby pokazać ją na ekranie gry!

    def split_unit_from_army(self, unit, target_slot_index):
            """Wyjmuje jednostkę z garnizonu lidera i stawia na mapie."""
            if unit in self.selected_unit.garrison:
                self.selected_unit.garrison[target_slot_index] = None
                unit.x, unit.y = self.selected_unit.x, self.selected_unit.y # Stawiamy obok lidera
                self.add_unit(unit)
                print(f"Rozdzielono: {unit.type} wyszedł z armii!")

    def execute_army_split(self, tx, ty):
        origin = self.selected_unit
        if not origin or not hasattr(self, 'units_to_split') or not self.units_to_split: 
            return
            
        dx = abs(origin.x - tx)
        dy = abs(origin.y - ty)
        
        if dx > 1 or dy > 1:
            print("Możesz rozdzielić armię tylko na sąsiednie pole!")
            return
            
        # ========================================================
        # NOWOŚĆ: Dynamiczny koszt zależny od terenu!
        # ========================================================
        tile_char = self.map[ty][tx]
        base_cost = TERRAIN_TYPES.get(tile_char, {}).get("cost", 4)
        move_mod = 1.5 if (dx != 0 and dy != 0) else 1.0 # Mnożnik *1.5 dla skosów
        koszt_podzialu = int(base_cost * move_mod)
        
        target_army = self.get_unit_at(tx, ty)
        if target_army:
            print("Pole zajęte! Aby dodać jednostki do tej armii, użyj przycisku Połącz.")
            return

        # Zabraniamy odłączenia, jeśli brakuje PA (według nowego kosztu!)
        for u in self.units_to_split:
            if u.move_points < koszt_podzialu:
                print(f"Jednostka {u.type} jest zbyt zmęczona (wymaga {koszt_podzialu} PA).")
                return

        if target_army:
            free_slots = [i for i, slot in enumerate(target_army.garrison) if slot is None]
            if len(self.units_to_split) > len(free_slots):
                print("Brak miejsca w docelowej armii sojusznika!")
                return

        # ========================================================
        # ROZDZIELENIE: Dowódcę też można zabrać!
        # ========================================================
        # Zbieramy wszystkie jednostki na tym polu
        all_origin_units = [origin] + [u for u in getattr(origin, 'garrison', []) if u is not None]
        staying_units = [u for u in all_origin_units if u not in self.units_to_split]
        leaving_units = self.units_to_split[:] # Kopia wychodzących

        # --- A. OGARNIANIE POLA STARTOWEGO (Tych co zostają) ---
        if not staying_units:
            # Cała armia poszła, pole zostaje puste
            if origin in self.units: self.units.remove(origin)
            if origin.owner and origin in origin.owner.units: origin.owner.units.remove(origin)
        else:
            # Jeśli ktoś zostaje, pierwsza jednostka awansuje na Nowego Lidera
            new_origin_leader = staying_units[0]
            new_origin_leader.x, new_origin_leader.y = origin.x, origin.y
            new_origin_leader.garrison = [None] * 10
            for i, u in enumerate(staying_units[1:]):
                if i < 10: new_origin_leader.garrison[i] = u
            
            # Rejestracja zmiany w świecie gry (Tylko jeśli lider faktycznie się zmienił)
            if new_origin_leader != origin:
                if origin in self.units: self.units.remove(origin)
                if origin.owner and origin in origin.owner.units: origin.owner.units.remove(origin)
                
                if new_origin_leader not in self.units: self.units.append(new_origin_leader)
                if new_origin_leader.owner and new_origin_leader not in new_origin_leader.owner.units:
                    new_origin_leader.owner.units.append(new_origin_leader)
            
            self.selected_unit = new_origin_leader # Utrzymujemy podgląd na starym polu

        # --- B. OGARNIANIE POLA DOCELOWEGO (Tych co idą) ---
        for u in leaving_units:
            u.move_points -= koszt_podzialu
            u.x, u.y = -1, -1 # Domyślnie znikają w garnizonie
            
        if target_army:
            # Dołączają do sojusznika
            free_slots = [i for i, slot in enumerate(target_army.garrison) if slot is None]
            for i, u in enumerate(leaving_units):
                target_army.garrison[free_slots[i]] = u
            print(f"Jednostki ({len(leaving_units)}) dołączyły do sojusznika obok!")
        else:
            # Tworzą nową armię na pustym kafelku
            new_target_leader = leaving_units[0]
            new_target_leader.x, new_target_leader.y = tx, ty
            new_target_leader.garrison = [None] * 10
            for i, u in enumerate(leaving_units[1:]):
                if i < 10: new_target_leader.garrison[i] = u
                
            if new_target_leader not in self.units: self.units.append(new_target_leader)
            if new_target_leader.owner and new_target_leader not in new_target_leader.owner.units:
                new_target_leader.owner.units.append(new_target_leader)
            print("Utworzono nowy oddział na mapie.")

        # --- ZAKOŃCZENIE ---
        self.units_to_split.clear()
        
        # Jeśli całe pole startowe opustoszało, przenosimy "kamerę/podgląd" na nową armię
        if not staying_units:
            self.selected_unit = target_army if target_army else leaving_units[0]

    def find_free_space_around(self, start_x, start_y, radius=1):
        """
        Przeszukuje kratki w określonym promieniu wokół podanych współrzędnych 
        i zwraca pierwszą wolną kratkę (x, y), na której można postawić jednostkę.
        """
        # Kafelki, na których jednostki mogą stać (trawa, las, góry, piasek, droga)
        walkable_tiles = [".", "l", "g", "p", "_", "P", "G", "B"] 
        
        # Szukamy dookoła w zadanym promieniu (np. od -1 do 1, tworząc kwadrat 3x3)
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                px = start_x + dx
                py = start_y + dy
                
                # Zabezpieczenie przed wyjściem poza mapę
                if 0 <= py < len(self.map) and 0 <= px < len(self.map[0]):
                    
                    # Sprawdzamy czy to odpowiedni teren (nie woda, nie góra)
                    if self.pathfinder.get_bg_tile_at(px, py) in walkable_tiles or self.map[py][px] in walkable_tiles:
                        # Upewniamy się, że to pole nie jest budynkiem (S, &, zamek itp)
                        unwalkable_objs = ["S", "&", "R", "#", "PORT_WALL"]
                        if self.map[py][px] not in unwalkable_objs:
                            
                            # Sprawdzamy czy nie stoi tam już jakaś inna jednostka
                            if not any(u.x == px and u.y == py for u in self.units):
                                return (px, py) # Znaleziono wolne pole!
                                
        # Jeśli wszystko dookoła jest absolutnie zajęte lub zablokowane,
        # awaryjnie wyrzucamy jednostkę dokładnie w miejscu zniszczenia.
        return (start_x, start_y)

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

       

        # 5. WALKA 
        #for other in self.units[:]:



    