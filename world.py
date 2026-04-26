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

@property
def back_button(self):
    if self.screen == "castle":
        return self.back_button_castle
    return self.back_button_bldg

class World(BuildingsMixin):
    def __init__(self):

        # --- DODAJ TO W __init__ ---
        self.recruitment_scroll = 0
        # Zabezpieczenie - przyciski muszą istnieć przed wszystkim innym
        # Na samym początku __init__, przed wszystkim innym:
        self.back_button_castle = pygame.Rect(45, 690, 130, 74)  # złota ramka
        self.back_button_bldg   = pygame.Rect(46, 685, 190, 91)  # szara ramka
        self.back_button        = self.back_button_bldg           # domyślny alias
        self.destroy_button = pygame.Rect(0, 0, 1, 1)  # placeholder
        self.button_send_army = pygame.Rect(860, 600, 150, 40)
        self.screen = "map"
        self.selected_castle = None
        self.selected_units = []

        self.selected_unit_type = 0
        self.selected_patent_index = None
        self.recruitment_open = False

        # Pobieramy wymiary ekranu dla dynamicznego pozycjonowania
        w = pygame.display.get_surface().get_width()
        h = pygame.display.get_surface().get_height()
        self.castle_gfx = CastleGraphics(w, h)
        self.garrison_gfx = GarrisonGraphics(w, h)
        self.unit_info_window = UnitInfoWindow()
        self.court = CourtHandler(self)
        self.recruitment_manager = RecruitmentManager(self)
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 24)
        self.font_small = pygame.font.SysFont(None, 20)
        self.modal_font = pygame.font.SysFont(None, 32)
        self.btn_font = pygame.font.SysFont(None, 28, bold=True)
        
        try:
            self.back_img_castle_normal  = pygame.transform.scale(
                pygame.image.load("assets/back_castlen.png").convert_alpha(), (130, 74))
            self.back_img_castle_pressed = pygame.transform.scale(
                pygame.image.load("assets/back_castlec.png").convert_alpha(), (130, 74))
            self.back_img_bldg_normal    = pygame.transform.scale(
                pygame.image.load("assets/back_normal.png").convert_alpha(),  (190, 91))
            self.back_img_bldg_pressed   = pygame.transform.scale(
                pygame.image.load("assets/back_clicked.png").convert_alpha(), (190, 91))
            print("Grafiki przycisku powrotu załadowane!")
        except Exception as e:
            print(f"Błąd grafik przycisku: {e}")
            dummy = pygame.Surface((130, 74))
            dummy.fill((140, 80, 80))
            self.back_img_castle_normal  = dummy
            self.back_img_castle_pressed = dummy
            self.back_img_bldg_normal    = dummy
            self.back_img_bldg_pressed   = dummy

        self.back_anim_timer = 0
        self.back_destination = "map"
        self.back_anim_timer = 0
        self.back_destination = "map"

        self.back_anim_timer = 0  # 0 oznacza, że animacja nie trwa
        # --- LOGIKA I DANE ---
        # ====================================================
        #                     ŁADOWANIE GRAFIKI MAPY
        # ====================================================
        self.load_castle_and_tower()
        
        # Inicjalizacja pozostałych list
        self.map = []
        self.units = []
        self.castles = []
        self.castle_locations = []
        self.peasant_groups = []
        self.gold_transports = []
        self.players = []
        self.selected_units = []
        self.screen = "map"
        self.selected_castle = None
        self.selected_unit = None
        self.turn = 1
        self.current_player = 0
        self.camera_x = 0
        self.camera_y = 0
        self.inspected_unit = None  # Dodaj to w sekcji zmiennych logicznych
        # Ładowanie danych
        # =====================================================
        #              SYSTEMOWE PRZYCISKI (STAŁE)
        # =====================================================
        # UNIWERSALNY PRZYCISK POWRÓT (Ten większy i niżej, o który prosiłeś)
        # Przycisk POWRÓT w głównym menu zamku (złota ramka - back_castlen/back_castlec)
        self.back_button_castle = pygame.Rect(45, 690, 130, 74)

        # Przycisk POWRÓT w budynkach (szara ramka - back_normal/back_clicked)
        self.back_button_bldg = pygame.Rect(46, 685, 190, 91)


        # MENU GÓRNE (Mapa)
        self.btn_system = pygame.Rect(10, 0, 100, 40)
        self.btn_mapa = pygame.Rect(115, 0, 100, 40)
        self.next_turn_button = pygame.Rect(w - 220, 0, 200, 45)
        self.top_ui_trigger_area = pygame.Rect(0, 0, w, 10)
        self.top_ui_full_area = pygame.Rect(0, 0, w, 55)
        self.show_top_ui = False
        
        # =====================================================
        #              EKRAN GŁÓWNY ZAMKU
        # =====================================================
        self.garrison_button = pygame.Rect(80, 630, 160, 40)
        self.court_button = pygame.Rect(420, 100, 160, 40)
        self.peasant_button = pygame.Rect(w - 200, h - 110, 160, 40)
        self.menu_button = pygame.Rect(w - 180, 40, 140, 40)

        self.debug_show_masks = False
        # =====================================================
        #              EKRAN GARNIZONU / KOSZAR
        # =====================================================
        self.recruit_button = pygame.Rect(260, 600, 120, 40)
        self.heal_button = pygame.Rect(460, 600, 120, 40)
        self.train_button = pygame.Rect(660, 600, 120, 40)
        self.button_send_army = pygame.Rect(860, 600, 150, 40) # "OPUŚĆ KOSZARY"

        # =====================================================
        #              EKRAN STRAŻNICY -GARNIZONU 
        # =====================================================
        self.release_tower = pygame.Rect
        # =====================================================
        #              EKRAN REKRUTACJI (PATENTY)
        # =====================================================
        self.buy_patent_button = pygame.Rect(160, 630, 140, 35)
        self.remove_patent_button = pygame.Rect(w - 230, 580, 100, 35)        
        self.start_prod_button = pygame.Rect(w - 300, 630, 120, 35)
        self.stop_prod_button = pygame.Rect(w - 160, 630, 120, 35)
        self.info_button = pygame.Rect(120, 590, 100, 30)
        self.scroll_up_button = pygame.Rect(260, 80, 40, 40)
        self.scroll_down_button = pygame.Rect(260, 200, 40, 40)
        self.recruitment_unit_types = list(UNIT_STATS.keys())
        self.patent_rects = []

        # =====================================================
        #              EKRAN CHŁOPÓW (PODATKI / WYSYŁKA)
        # =====================================================
        # +/- dla Wieśniaków, Złota i Podatków
        self.peasants_plus_button = pygame.Rect(300, 200, 40, 40)
        self.peasants_minus_button = pygame.Rect(100, 200, 40, 40)
        self.gold_plus_button = pygame.Rect(300, 300, 40, 40)
        self.gold_minus_button = pygame.Rect(100, 300, 40, 40)
        self.tax_plus_button = pygame.Rect(300, 400, 40, 40)
        self.tax_minus_button = pygame.Rect(100, 400, 40, 40)
        self.send_button = pygame.Rect(100, 500, 160, 45)
        # Przewijanie listy zamków docelowych
        self.castle_up_button = pygame.Rect(800, 150, 40, 40)
        self.castle_down_button = pygame.Rect(800, 450, 40, 40)
        self.castle_list_offset = 0
        self.send_peasants_amount = 10  # Domyślna liczba chłopów do wysłania
        self.send_gold_amount = 100     # Przy okazji dodaj to dla złota, pewnie zaraz wyskoczy
        
        # =====================================================
        #              LOGIKA MENU KONTEKSTOWEGO
        # =====================================================
        self.menu_open = False
        self.build_open = False
        self.build_menu_open = False  # <--- TEJ LINII BRAKOWAŁO
        self.menu_rects = {}
        self.build_rects = {}
        self.active_dropdown = None
        self.menu_options = {
            "System": ["Misja", "Poddanie się", "Zapisz grę", "Wczytaj grę", "Opcje", "Koniec"],
            "Mapa": ["Wszystko", "Budynki", "Jednostki", "Nic"]
        }
        
        # =====================================================
        #              INNE / MAPA
        # =====================================================
        self.ui_panel_rect = pygame.Rect(720, 610, 304, 158)
        # =====================================================
        # --- DOLNY PANEL AKCJI (MAPA) ---
        # =====================================================
        self.action_buttons = []
        button_width = 120
        button_height = 60
        
        # Cały panel to 3 kolumny przycisków i 2 rzędy
        panel_total_width = 3 * button_width   # 360 pikseli
        panel_total_height = 2 * button_height # 120 pikseli
        
        # Ustawiamy margines od krawędzi ekranu (żeby nie dotykały samej ramki)
        margin_right = 0
        margin_bottom = 0
        
        # DYNAMICZNE WYLICZANIE POZYCJI
        # Zamiast sztywnych liczb (np. 664), odejmujemy szerokość panelu od szerokości ekranu (w)
        panel_x = w - panel_total_width - margin_right
        panel_y = h - panel_total_height - margin_bottom

        # Tworzenie przycisków bazując na dynamicznym x i y
        for row in range(2):
            for col in range(3):
                rect = pygame.Rect(panel_x + col * button_width, panel_y + row * button_height, button_width, button_height)
                self.action_buttons.append(rect)
                
        # Zaktualizowanie ewentualnego tła dla tych przycisków, jeśli go używasz
        self.ui_panel_rect = pygame.Rect(panel_x - 10, panel_y - 10, panel_total_width + 20, panel_total_height + 20)
        
        self.show_grid = False
        self.traps = []
        self.trap_backgrounds = {}    # Słownik: (x, y) -> "oryginalny_znak_terenu"
        self.constructions = []
        self.trap_build_mode = False
        self.build_clicked = {}  # Słownik do śledzenia kliknięć w budynki
# DO SPRAWDZENIA !!!
        # ===============================================================
        #                       ŁADOWANIE IKON 
        # ===============================================================
        try:
            self.icon_training = pygame.image.load("assets/swords.png").convert_alpha()
            # Przeskaluj ją, żeby pasowała do slotu (np. 32x32 piksele)
            self.icon_training = pygame.transform.scale(self.icon_training, (32, 32))
        except:
            # Zabezpieczenie: jeśli pliku nie ma, stwórz pustą powierzchnię, żeby gra się nie wywaliła
            self.icon_training = pygame.Surface((32, 32))
            self.icon_training.fill((255, 0, 255)) # Różowy kolor "błędu"
        # --- NOWE KAFFELKI TERENU ---
        base_bg_path = r"assets\BACKGR3_S32_"
        self.terrain_images = {}
        
        try:
            self.terrain_images["$"] = pygame.image.load(f"{base_bg_path}752.png").convert_alpha()
            self.terrain_images["S"] = pygame.image.load(f"{base_bg_path}733.png").convert_alpha()
            self.terrain_images["&"] = pygame.image.load(f"{base_bg_path}736.png").convert_alpha()
            
            # Opcjonalnie skalujemy, by mieć pewność, że pasują do TILE_SIZE
            for key in self.terrain_images:
                self.terrain_images[key] = pygame.transform.scale(self.terrain_images[key], (TILE_SIZE, TILE_SIZE))
        except Exception as e:
            print(f"Błąd ładowania dodatkowych kafelków: {e}")
        
     
# Wewnątrz world.py, w sekcji inicjalizacji graczy:
        num_players = 2  # Na razie wymuszamy 2 graczy
        self.players = []
        player_data = [
            ("Don Marek", (200, 0, 0), "red"),     # ID 0
            ("Lech VI", (0, 0, 200), "blue"),      # ID 1
            ("Mściwój", (0, 150, 0), "green"),     # ID 2
            ("Biały Kieł", (220, 220, 220), "white"),# ID 3
            ("Złoty Pan", (200, 200, 0), "yellow")  # ID 4
        ]

        from player import Player
        for i in range(num_players):
            name, color_rgb, color_name = player_data[i]
            new_player = Player(i, name, color_rgb, color_name)
            self.players.append(new_player)
            
            self.back_destination = "map" # Cel powrotu
   
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
        print("CASTLES:", [type(c) for c in self.castles])

        if not self.players:
            return

        self.turn += 1
        self.current_player = (self.current_player + 1) % len(self.players)
        self.reset_units()

        # --- LOGIKA BUDOWANIA (Wywołujemy funkcję, którą stworzyliśmy) ---
        self.process_construction() 

        # Logika zamków
        for castle in self.castles:
            if not getattr(castle, 'destroyed', False):
                castle.next_turn()
                castle.collect_taxes()
                
        # Odnowienie punktów ruchu jednostek
        for unit in self.units:
            if unit.type in UNIT_STATS:
                unit.move_points = UNIT_STATS[unit.type].get("moves", 5) 
            else:
                unit.move_points = 5

        # --- CZYSZCZENIE UI ---
        self.active_dropdown = None 
        self.build_menu_open = False 
        self.selected_castle = None
        self.selected_unit = None
        self.show_top_ui = False
        self.screen = "map"

    def move_unit(self, unit, dx, dy, cost=1): # <--- Dodajemy parametr cost
        """
        KOMPLETNA LOGIKA RUCHU:
        Łączy ruch gracza, AI, interakcje z obiektami i walkę.
        """
        # 1. Sprawdzenie punktów ruchu (używamy przekazanego kosztu)
        if unit.move_points < cost:
            print(f"DEBUG: Jednostka {unit.type} nie ma wystarczającej liczby punktów ruchu ({cost}).")
            return False

        nx, ny = unit.x + dx, unit.y + dy

        # 2. Granice mapy
        if not (0 <= nx < len(self.map[0]) and 0 <= ny < len(self.map)):
            return False

        # 3. INTERAKCJA Z ZAMKIEM (Obszar 2x2)
        for castle in self.castles:
            if castle.x <= nx <= castle.x + 1 and castle.y <= ny <= castle.y + 1:
                if castle.destroyed:
                    return False

                if hasattr(unit, 'planned_path') and unit.planned_path:
                    final_x, final_y = unit.planned_path[-1]
                    is_targeting_this_castle = (castle.x <= final_x <= castle.x + 1 and 
                                                castle.y <= final_y <= castle.y + 1)
                    
                    if not is_targeting_this_castle:
                        print("Zamek blokuje drogę — musisz go obejść!")
                        return False

                if castle.owner != unit.owner:
                    castle.owner = unit.owner
                    castle.garrison = [None] * 12
                    print(f"Zamek na ({castle.x}, {castle.y}) został PRZEJĘTY!")

                for i in range(len(castle.garrison)):
                    if castle.garrison[i] is None:
                        castle.garrison[i] = unit
                        if unit in self.units: self.units.remove(unit)
                        if unit in unit.owner.units: unit.owner.units.remove(unit)
                        
                        unit.move_points -= cost # <--- ODEJMUJEMY KOSZT
                        if self.selected_unit == unit:
                            self.selected_unit = None
                        return True
                return False

        # 4. TEREN - Lista znaków, po których wolno chodzić
        # Dodałem kropkę, l, g oraz znaki drogi
        walkable_chars = [".", "l", "g", "p", "_", "#", "$", " "] 
        
        # Pobieramy co jest na mapie w miejscu docelowym
        map_char = self.map[ny][nx]

        if map_char not in walkable_chars:
            # Jeśli to np. 'W' (Woda) lub 'M' (Góry), ruch jest zablokowany
            print(f"DEBUG: Blokada! Teren '{map_char}' na ({nx}, {ny}) jest nieprzejezdny.")
            return False

        # 5. WALKA 
        for other in self.units[:]: # Używamy kopii listy do bezpiecznego usuwania
            if other.x == nx and other.y == ny:
                if other.owner != unit.owner:
                    print(f"ATAK! {unit.type} uderza w {other.type}!")
                    self.units.remove(other)
                    if other in other.owner.units:
                        other.owner.units.remove(other)
                else:
                    return False
            
        # 6. ZBIERANIE CHŁOPÓW
        for group in self.peasant_groups[:]:
            if group.x == nx and group.y == ny:
                if group.owner != unit.owner:
                    unit.carried_peasants += group.amount
                    self.peasant_groups.remove(group)
                    print(f"Chłopi ({group.amount}) dołączyli do armii.")

        # 7. PRZEJMOWANIE ZŁOTA
        for t in self.gold_transports[:]:
            if t.x == nx and t.y == ny:
                if t.owner != unit.owner:
                    unit.carried_gold += t.gold
                    self.gold_transports.remove(t)
                    print(f"Przejęto {t.gold} złota z transportu!")

        # 8. FINALIZACJA
        unit.x, unit.y = nx, ny
        unit.move_points -= cost # <--- KLUCZ: Odejmujemy koszt (1 lub 1.5)
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
        # 1. Szukamy pierwszego wolnego slotu (None)
        for i in range(len(castle.garrison)):
            if castle.garrison[i] is None:
                # 2. Wkładamy jednostkę w puste miejsce
                castle.garrison[i] = unit
                
                # 3. Usuwamy z mapy
                if unit in self.units: self.units.remove(unit)
                if unit in unit.owner.units: unit.owner.units.remove(unit)
                
                unit.x, unit.y = -1, -1
                self.selected_unit = None
                print(f"DEBUG: Jednostka schowana w slocie {i}")
                return True
                
        print("DEBUG: Brak wolnych slotów!")
        return False
    
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
            if not pos: continue
            
            nx, ny = pos

            if len(group) == 1:
                # ================= SCENARIUSZ A: SOLO (np. Budowniczy) =================
                solo_unit = group[0]
                
                # --- KLUCZOWA POPRAWKA: USUWANIE ZE SLOTU ---
                for slot_idx in range(len(target.garrison)):
                    if target.garrison[slot_idx] is unit_to_move: # lub solo_unit
                        target.garrison[slot_idx] = None
                        self.garrison_gfx.trigger_door_open(slot_idx) # <--- DODAJ TO
                        break
                # --------------------------------------------

                solo_unit.x, solo_unit.y = nx, ny
                if hasattr(solo_unit, 'rect'):
                    solo_unit.rect.topleft = (nx * TILE_SIZE, ny * TILE_SIZE)
                solo_unit.visible = True
                
                if solo_unit not in self.units:
                    self.units.append(solo_unit)

                if target.owner and solo_unit not in target.owner.units:
                    target.owner.units.append(solo_unit)
                    
                print(f"Wypuszczono solo: {solo_unit.type} i wyczyszczono slot.")

            else:
                # ================= SCENARIUSZ B: GRUPA (ARMIA) =================
                army_type = group[0].type 
                new_army = Unit(army_type, nx, ny, target.owner)
                new_army.garrison = [None] * 10

                for i, unit_to_move in enumerate(group):
                    if i < 10:
                        new_army.garrison[i] = unit_to_move
                        
                        # --- CZYŚCIMY SLOTY W BUDYNKU ---
                        for slot_idx in range(len(target.garrison)):
                            if target.garrison[slot_idx] is unit_to_move: # lub solo_unit
                                target.garrison[slot_idx] = None
                                self.garrison_gfx.trigger_door_open(slot_idx) # <--- DODAJ TO
                                break

                        if unit_to_move in self.units:
                            self.units.remove(unit_to_move)
                
                self.units.append(new_army)
                if target.owner:
                    target.owner.units.append(new_army)

        # --- KLUCZOWA ZMIANA ---
        self.selected_units.clear()
        
        if not stay_in_menu:
            self.screen = "map"
            self.selected_castle = None
        
        print("Jednostki wypuszczone.")

    def find_multiple_spawn_positions(self, castle, num_groups):
        # gdzie wychodzą jednostki
        """Szuka wolnych miejsc dla X grup według Twojej ścisłej kolejności."""
        directions = [
            (0, 2), (1, 2), (2, 2), (-1, 2),
            (2, 1),                 (-1, 1),
            (2, 0),                 (-1, 0),
            (2, -1), (-1, -1), (1, -1), (0, -1)
        ]
        
        results = []
        # Aktualna lista zajętych pól (jednostki na mapie + już przypisane nowe pozycje)
        occupied = {(u.x, u.y) for u in self.units}
        
        for _ in range(num_groups):
            found = False
            for dx, dy in directions:
                nx, ny = castle.x + dx, castle.y + dy
                if 0 <= nx < len(self.map[0]) and 0 <= ny < len(self.map):
                    if (nx, ny) not in occupied and self.map[ny][nx] in [".", "_", "p", "#", "$","l","g"]:
                        results.append((nx, ny))
                        occupied.add((nx, ny)) # Rezerwujemy to miejsce dla kolejnej grupy
                        found = True
                        break
            if not found:
                results.append(None) # Brak miejsca dla tej konkretnej grupy
                
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