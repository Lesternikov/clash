from unit import Unit
from castle import Castle, UNIT_REQUIREMENTS
from player import Player
from buildings import BuildingsMixin
from castle import BUILDING_TYPES
import random  # Do losowania drzew (żeby las nie był nudny)
import pygame  # Silnik gry
from UI_components import UnitInfoWindow
from settings import UNIT_STATS, UNIT_NAMES, TERRAIN_TYPES, MAP_HEIGHT, MAP_WIDTH, TILE_SIZE, COLOR_TO_ID, SCREEN_HEIGHT, SCREEN_WIDTH
from court import CourtHandler
from controls import ControlsHandler
from garrison_graphics import GarrisonGraphics
from castle_graphics import CastleGraphics
import map_graphics

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
        # --- DOLNY PANEL AKCJI (MAPA) ---
        self.ui_panel_rect = pygame.Rect(720, 610, 304, 158)
        
        self.unit_info_window = UnitInfoWindow()
        self.action_buttons = []
        
        
        # Odstępy między przyciskami (muszą być większe niż szerokość/wysokość)
        # column_spacing = 130 # 120 szerokości + 10 przerwy
        # row_spacing = 90    # 82 wysokości + 8 przerwy
        
        # Jeśli używałeś siatki 2x3 po prawej stronie:
        panel_x = 800 # Startowa pozycja X
        panel_y = 620 # Startowa pozycja Y

        for row in range(2):
            for col in range(3):
                # Tworzymy szersze prostokąty
                # Używamy kol * odstęp, żeby się nie nakładały
                rect = pygame.Rect(panel_x + col * 70, panel_y + row * 70, button_width, button_height)
                self.action_buttons.append(rect)
                
        # Aktualizujemy też tło panelu, żeby pasowało do nowych, szerszych przycisków
        # (3 kolumny * 130 + margines)
        self.ui_panel_rect = pygame.Rect(790, 610, 400, 190)
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
        self.players = []
        player_data = [
            ("Don Marek", (200, 0, 0), "red"),     # ID 0
            ("Lech VI", (0, 0, 200), "blue"),      # ID 1
            ("Mściwój", (0, 150, 0), "green"),     # ID 2
            ("Biały Kieł", (220, 220, 220), "white"),# ID 3
            ("Złoty Pan", (200, 200, 0), "yellow")  # ID 4
        ]

        from player import Player
        for i, (name, color_rgb, color_name) in enumerate(player_data):
            # Przekazujemy teraz też color_name
            new_player = Player(i, name, color_rgb, color_name)
            self.players.append(new_player)

            self.back_destination = "map" # Cel powrotu
    
    def _find_nearest_base_terrain(self, start_x, start_y, base_terrains):
        """Skanuje okolicę promieniście, żeby zgadnąć tło pod obiektem."""
        for radius in range(1, 4): # Szuka w promieniu 1, 2, 3 kratek
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    nx, ny = start_x + dx, start_y + dy
                    if 0 <= ny < len(self.map) and 0 <= nx < len(self.map[0]):
                        if self.map[ny][nx] in base_terrains:
                            return self.map[ny][nx]
        return "." # Domyślna trawa w razie ekstremalnej sytuacji
  
    def get_river_direction(self, x, y):
        # Sprawdzamy, z której strony jest najbliższy ląd
        if y > 0 and self.map[y-1][x] in [".", "p", "B"]: return "UP"
        if x > 0 and self.map[y][x-1] in [".", "p", "B"]: return "LEFT"
        if x < len(self.map[0])-1 and self.map[y][x+1] in [".", "p", "B"]: return "RIGHT"
        if y < len(self.map)-1 and self.map[y+1][x] in [".", "p", "B"]: return "DOWN"
        return "UP" # Domyślny, jeśli coś pójdzie nie tak
    
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
                
                # 2. BUDOWNICZY (Jeden kafelek w prawo, jeden w dół od zamku)
                # Zmieniamy c.x na c.x + 1, żeby nie stał NA zamku
                builder_x = int(c.x + 5)
                builder_y = int(c.y - 65)
                builder = Unit("BUDOW", builder_x, builder_y, owner_obj)
                self.add_unit(builder)
                
                print(f"Rozstawiono jednostki dla: {owner_obj.color_name} na ({builder_x}, {builder_y})")

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
    
    def recruit_unit(self):
        if not self.selected_castle:
            print("Nie wybrano zamku")
            return
            
        if len(self.selected_castle.garrison) >= 12:
            print("Zamek jest pełny")
            return

        if not self.selected_recruit_unit:
            print("Nie wybrano jednostki do rekrutacji")
            return

        player = self.players[self.current_player]
        unit_code = self.selected_recruit_unit  # np. "INFL"

        # 1. Pobieramy pełną nazwę, bo UNIT_STATS używa nazw (np. "Lekka piechota")
        full_name = UNIT_NAMES.get(unit_code, "Nieznany")

        # 2. Pobieramy statystyki dla tej nazwy
        unit_data = UNIT_STATS.get(full_name, {})

        # 3. Pobieramy koszt (w Twoim settings.py to "production_cost")
        cost = unit_data.get("production_cost", 0)

        if player.gold < cost:
            print(f"Za mało złota! Potrzeba {cost}, masz {player.gold}")
            return

        # 4. Odejmowanie złota i tworzenie jednostki
        player.gold -= cost

        u = Unit(
            unit_code,            # Zmieniono z unit_type na unit_code!            
            self.selected_castle.x,
            self.selected_castle.y,
            player
        )

        self.selected_castle.add_to_garrison(u)
        print(f"Zrekrutowano {full_name}") # full_name ładniej wygląda w konsoli

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
                
    def handle_trap_info_click(self, mx, my):
        # działanie pułapki
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

    def handle_map_logic_combined(self, mx, my, button):
        # --- NOWOŚĆ: Jeśli to prawy klik, nie rób nic więcej na mapie ---
        # Podgląd został już ustawiony w handle_events, 
        # więc tutaj przerywamy, żeby nie wywołać ruchu/odznaczenia.
        if button == 3:
            return
        # specjalne zdolności budowniczego
        gx = (mx + self.camera_x) // TILE_SIZE
        gy = (my + self.camera_y) // TILE_SIZE

        # 1. Tryby specjalne (Budowa dróg / pułapek)
        if getattr(self, 'trap_build_mode', False):
            self.execute_trap_build(gx, gy)
            return
        
        if getattr(self, 'road_build_mode', False):
            self.execute_road_build(gx, gy)
            return

        # 2. Kliknięcie w interaktywne obiekty mapy (Pułapka X)
        if self.map[gy][gx] == "X":
            self.screen = "trap_info"
            self.active_trap_pos = (gx, gy)
            return

    def execute_trap_build(self, gx, gy):
        u = self.selected_unit
        dist_x = abs(gx - u.x)
        dist_y = abs(gy - u.y)

        # Sprawdzamy zasięg 1 pola i czy to nie jest pole budowniczego
        if dist_x <= 1 and dist_y <= 1 and not (dist_x == 0 and dist_y == 0):
            # Sprawdzamy teren za pomocą Twojej funkcji sprawdzającej
            if self.can_build_trap(gx, gy):
                # Budujemy!
                self.trap_backgrounds[(gx, gy)] = self.map[gy][gx]
                self.map[gy][gx] = "X"
                
                # Usuwamy jednego budowniczego (Twoja specjalna funkcja)
                self.remove_unit_or_builder(u, u)
                
                self.trap_build_mode = False
                self.selected_unit = None
                print("Pułapka zastawiona pomyślnie!")
            else:
                print("Zły teren na pułapkę!")
        else:
            print("Poza zasięgiem budowy!")
            self.trap_build_mode = False

    def execute_road_build(self, gx, gy):
        u = self.selected_unit
        
        # STRAŻNIK: Jeśli u jest None, po prostu wyjdź z funkcji
        if u is None:
            print("DEBUG: Próba budowy drogi bez zaznaczonej jednostki!")
            return

        dist_x = abs(gx - u.x)
        dist_y = abs(gy - u.y)

        # Sprawdzamy czy kliknięto dokładnie 1 pole obok (kierunek N, S, E, W)
        if (dist_x == 1 and dist_y == 0) or (dist_x == 0 and dist_y == 1):
            if self.can_build_road(gx, gy):
                # 1. Stawiamy drogę na aktualnym polu budowniczego
                self.map[u.y][u.x] = "_"
                
                # 2. Przesuwamy budowniczego na nowe pole
                u.x, u.y = gx, gy
                
                # 3. Zabieramy punkty ruchu (koszt budowy drogi u Ciebie to 5)
                u.move_points -= 5
                
                # 4. Sprawdzamy czy może budować dalej w tej turze
                if u.move_points < 5:
                    self.road_build_mode = False
                    print("Koniec punktów ruchu. Droga ukończona.")
                else:
                    print("Droga położona. Możesz kontynuować budowę.")
            else:
                print("Tu nie można budować drogi!")
                self.road_build_mode = False
        else:
            # Jeśli gracz kliknął za daleko, wyłączamy tryb
            self.road_build_mode = False        

    def handle_garrison_click(self, mx, my, button):

        castle = self.selected_castle
        if not castle:
            return

        # ================= BACK =================
        if self.back_button.collidepoint(mx, my):
            self.selected_units.clear()
            self.screen = "castle"
            return

        # ================= RECRUITMENT =================
        if ("koszary" in castle.buildings
            and self.recruit_button.collidepoint(mx, my)):
            self.screen = "recruitment"
            self.recruitment_open = True
            self.recruitment_scroll = -2  # To sprawi, że pierwsza jednostka będzie na środku
            self.selected_unit_type = 0   # Od razu zaznacza pierwszą jednostkę
            self.selected_patent_index = None

            return

        # ================= HEAL =================
        if "hospital" in castle.buildings:
            if self.heal_button.collidepoint(mx, my):
                for unit in self.selected_units:
                    castle.start_healing_unit(unit)
                return

        # ================= TRAIN ================= 
        if "school" in castle.buildings:
            if self.train_button.collidepoint(mx, my):
                if self.selected_units:
                    # Używamy pętli, aby przeszkolić każdą zaznaczoną jednostkę z osobna
                    if self.selected_units:
                        castle.start_training_group(self.selected_units) # Jedno wywołanie, Castle zajmie się resztą
                    self.selected_units.clear() # Czyścimy dopiero PO przeszkoleniu wszystkich
                    print("Zakończono wydawanie rozkazów szkolenia")
                else:
                    print("Brak zaznaczonych jednostek do szkolenia")
                return
        #=================wyślij wojsko======================
        
        if self.button_send_army.collidepoint(mx, my):
            self.release_selected_units()
            return
        
        # =====================================================
        # POPRAWIONA LOGIKA SELEKCJI I STATYSTYK
        # =====================================================
        index = self.click_on_garrison(mx, my,)
        print(f"DEBUG: Kliknięto w slot {index} przyciskiem {button}") # DODAJ TO
        if index is None or index >= len(self.selected_castle.garrison):
            return

        unit = self.selected_castle.garrison[index]

        # --- PRAWY PRZYCISK: Statystyki ---
        if button == 3: 
            if unit is not None:
                self.inspected_unit = unit  # ZMIANA: z show_unit_stats na inspected_unit
                print(f"DEBUG: Podglądam {unit.type}")
            else:
                self.inspected_unit = None
            return

        # --- LEWY PRZYCISK: Zaznaczanie ---
        if button == 1:
            self.inspected_unit = None
            if unit is None:
                return

            # ZMIANA: Używamy listy, bo garrison używa selected_units
            if unit in self.selected_units:
                self.selected_units.remove(unit)
                print(f"DEBUG: Odznaczono: {unit.type}")
            else:
                if len(self.selected_units) < self.selected_castle.garrison_limit:
                    # DODAJEMY DOKŁADNIE TEN OBIEKT Z GARNIZONU
                    self.selected_units.append(unit)
                    print(f"DEBUG: Zaznaczono: {unit.type}")
                else:
                    print("DEBUG: Garnizon jest pełen!")

    def draw_garrison(self, screen):
        castle = self.selected_castle
        if not castle: return

        slot_rects = self.garrison_gfx.draw(
            screen, castle,
            self.selected_units,
            self.inspected_unit
        )
        # Zapisujemy recty do obsługi kliknięć
        self.garrison_slot_rects = slot_rects

        # Przyciski funkcyjne
        built = [b.lower() for b in castle.buildings]
        if "koszary" in built:
            self.draw_button(screen, "RECRUIT", self.recruit_button, (240, 120, 20))
        if "hospital" in built:
            self.draw_button(screen, "HEAL", self.heal_button, (80, 160, 80))
        if "school" in built:
            self.draw_button(screen, "TRAIN", self.train_button, (160, 160, 80))
        self.draw_building_footer(screen)
  
    def draw_castle_on_map(self, screen, castle):
        """Rysuje zamek (2x2) lub strażnicę (1x1) na mapie świata."""
        px = int(castle.x * TILE_SIZE) - self.camera_x
        py = int(castle.y * TILE_SIZE) - self.camera_y
        
        # Optymalizacja: nie rysuj, jeśli zamek jest daleko poza ekranem
        if px < -100 or px > SCREEN_WIDTH + 100 or py < -100 or py > SCREEN_HEIGHT + 100:
            return

        is_tower = getattr(castle, 'building_type', 'Zamek') == "Strażnica"
        
        # Wybór stanu budynku (0 to faza budowy, 3 to gotowy, 4 to ruiny)
        if getattr(castle, 'destroyed', False):
            s_idx = 4
        elif getattr(castle, 'under_construction', False):
            s_idx = 0 
        else:
            s_idx = 3 

        # Rysowanie właściwej grafiki
        if is_tower:
            # STRAŻNICA (1x1 kafel)
            img = self.tower_tiles.get(s_idx)
            if img:
                screen.blit(img, (px, py))
        else:
            # ZAMEK / TWIERDZA (2x2 kafle)
            tiles = self.castle_tiles.get(s_idx, [])
            if len(tiles) == 4:
                offsets = [(0,0), (1,0), (0,1), (1,1)]
                for i in range(4):
                    dx, dy = offsets[i]
                    screen.blit(tiles[i], (px + dx*TILE_SIZE, py + dy*TILE_SIZE))
 
    def is_near_tile(self, x, y, search_type, check_bg=False):
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0: continue
                
                # Wybieramy, na którą warstwę patrzymy
                if check_bg:
                    found_tile = self.pathfinder.get_bg_tile_at(x + dx, y + dy)
                else:
                    found_tile = self.pathfinder.get_tile_at(x + dx, y + dy)
                    
                if found_tile == search_type:
                    return True
        return False
            
    def draw_castle_interface(self, screen):
        castle = self.selected_castle
        if not castle: 
            return
        
        # Pobieramy aktualną pozycję myszy dla całego interfejsu
        mx, my = pygame.mouse.get_pos()

        # --- WARSTWA 1: DYNAMICZNA GRAFIKA ZAMKU (Tło i mury) ---
        # To rysujemy ZAWSZE jako pierwsze. Plik castle_graphics sam nałoży warstwy.
        if hasattr(self, 'castle_gfx'):
            self.castle_gfx.draw(screen, castle)
        else:
            screen.fill((60, 50, 40)) # Rezerwowy brąz, jeśli grafika zawiedzie

        # --- WARSTWA 2: WOJSKO (Garnizon) ---
        # Jeśli masz już gotową funkcję do rysowania jednostek w zamku, odkomentuj poniżej:
        # self.draw_garrison_units_on_screen(screen, castle)

        # --- WARSTWA 3: STAŁY INTERFEJS (Tytuł i przyciski budynków) ---
        font = pygame.font.SysFont(None, 28)
        title = font.render(f"{castle.building_type.upper()}", True, (255, 255, 255))
        screen.blit(title, (40, 40))

        # Przyciski funkcyjne

        if castle.building_type == "Zamek":
            self.peasant_button = pygame.Rect(screen.get_width() - 200, screen.get_height() - 110, 160, 40)
            self.draw_button(screen, "CHŁOPI", self.peasant_button, (160, 140, 60))

        # Przyciski konkretnych wybudowanych budynków (Ich stałe pozycje na ekranie)
        if hasattr(self, 'castle_gfx'):
            # Przekazujemy naszą flagę do funkcji draw
            self.castle_gfx.draw(screen, self.selected_castle, debug_mode=self.debug_show_masks)
        # --- WARSTWA 4: SYSTEM ROZWIJANEGO MENU (Na samym wierzchu) ---
        
        # Sprawdzamy, czy mysz jest nad przyciskiem MENU lub nad otwartym menu
        mouse_over_ui = False
        if self.menu_button.collidepoint(mx, my):
            self.menu_open = True
            mouse_over_ui = True

        if getattr(self, 'menu_open', False):
            # Rysujemy Twoje menu z opcjami "Buduj", "Zburz" itp.
            self.draw_castle_menu(screen, mx, my)
            
            # Sprawdzamy czy mysz jest nad opcjami menu, żeby go nie zamknąć
            for rect in self.menu_rects.values():
                if rect.collidepoint(mx, my): mouse_over_ui = True
            if getattr(self, 'build_open', False):
                for rect in self.build_rects.values():
                    if rect.collidepoint(mx, my): mouse_over_ui = True
            
            # Mostek bezpieczeństwa
            bridge_rect = pygame.Rect(self.menu_button.x - 20, self.menu_button.y, 30, 200)
            if bridge_rect.collidepoint(mx, my): mouse_over_ui = True

        # Jeśli mysz ucieknie poza UI, zamykamy menu
        if not mouse_over_ui:
            self.menu_open = False
            self.build_open = False

        # Rysujemy sam przycisk MENU
        self.draw_button(screen, "MENU", self.menu_button)

        # 6. STOPKA (Przycisk POWRÓT na mapę)
        self.draw_building_footer(screen)
     
    def castle_has_patent(self, castle, unit_name):
        for p in castle.patents:
            if isinstance(p, dict) and p["unit_type"] == unit_name:
                return True
            if p == unit_name:
                return True
        return False

    def update_selected_from_scroll(self):
        center_offset = self.visible_recruitment_count // 2
        idx = self.recruitment_scroll + center_offset
        
        # Sprawdzamy, czy wyliczony indeks faktycznie mieści się w liście jednostek
        if 0 <= idx < len(self.recruitment_unit_types):
            self.selected_unit_type = idx
        else:
            # Jeśli na środku jest "pustka" (przewinięte za mocno), nic nie jest zaznaczone
            self.selected_unit_type = None

    def center_on_selected_unit(self):
        visible = self.visible_recruitment_count
        max_scroll = max(0, len(self.recruitment_unit_types) - visible)

        self.recruitment_scroll = max(
            0,
            min(
                self.selected_unit_type - visible // 2,
                max_scroll
            )
        )
    # =======================
    # DRAW RECRUITMENT
    # =======================
    def draw_recruitment(self, screen):
        screen.fill((60, 50, 40)) 
        font = pygame.font.SysFont(None, 24)
        castle = self.selected_castle
        if not castle: return
        w, h = screen.get_size()

        # 1. Przygotowanie listy jednostek
        all_units = list(UNIT_STATS.keys())
        unit_types = [u for u in all_units if self.castle_has_patent(castle, u) or castle.is_patent_available(u)]
        self.recruitment_unit_types = unit_types

        # 2. PANEL PATENTÓW (Prawy bok)
        self.patent_rects = [] 
        for i in range(12):
            x = w - 300 + (i % 4) * 60
            y = 30 + (i // 4) * 90 + 50
            rect = pygame.Rect(x, y, 50, 80)
            self.patent_rects.append(rect) 
            pygame.draw.rect(screen, (40, 30, 20), rect) 
            r_color = (255, 255, 0) if self.selected_patent_index == i else (100, 100, 100)
            pygame.draw.rect(screen, r_color, rect, 2 if self.selected_patent_index == i else 1)

            if i < len(castle.patents) and castle.patents[i] is not None:
                p = castle.patents[i]
                name = p["unit_type"] if isinstance(p, dict) else p
                screen.blit(font.render(name[:5], True, (255, 255, 0)), (x + 2, y + 30))

        can_start = False
        if self.selected_patent_index is not None:
            if self.selected_patent_index < len(castle.patents) and castle.patents[self.selected_patent_index] is not None:
                can_start = True

        # Rysowanie tła przycisków
        for btn, col in [(self.info_button, (120,120,120)), 
                        (self.buy_patent_button, (80,140,80)), (self.remove_patent_button, (120,80,80)),
                        (self.stop_prod_button, (140,80,80))]:
            pygame.draw.rect(screen, col, btn)
        
        pygame.draw.rect(screen, (80, 140, 80) if can_start else (60, 60, 60), self.start_prod_button)
        # WYWOŁAJ PO PROSTU:
        self.draw_building_footer(screen)
        # Napisy na przyciskach
        screen.blit(font.render("INFO", True, (255, 255, 255)), (150, 595))
        screen.blit(font.render("KUP PATENT", True, (255, 255, 255)), (170, 635))
        screen.blit(font.render("USUŃ", True, (255, 255, 255)), (w - 210, 595))
        screen.blit(font.render("START", True, (255, 255, 255) if can_start else (120, 120, 120)), (w - 270, 635))
        screen.blit(font.render("STOP", True, (255, 255, 255)), (w - 130, 635))

        # --- PRODUKCJA INFO ---
        if castle.production_enabled and castle.production_unit_type:
            p_text = f"Produkcja: {castle.production_unit_type} ({castle.production_turns_left} tur)"
            p_color = (0, 255, 0)
        else:
            p_text = "Produkcja nieaktywna"
            p_color = (200, 200, 200)
        screen.blit(font.render(p_text, True, p_color), (w - 300, 380))

        # 4. LISTA JEDNOSTEK (Lewa strona)
        self.unit_list_rects = [] # Ważne: resetujemy listę przed ponownym wypełnieniem
        start_x, start_y, box_w, box_h, gap = 30, 80, 220, 30, 2
        center_index = 2

        for i in range(5):
            scroll_index = self.recruitment_scroll + i
            if 0 <= scroll_index < len(unit_types):
                unit_name = unit_types[scroll_index]
                rect = pygame.Rect(start_x, start_y + i * (box_h + gap), box_w, box_h)
                self.unit_list_rects.append(rect) # Rejestrujemy recty do klikania
                
                has_p = self.castle_has_patent(castle, unit_name)
                t_col = (255, 255, 255) if i == center_index else ((90, 90, 90) if has_p else (180, 180, 180))
                
                pygame.draw.rect(screen, (30, 30, 30), rect)
                screen.blit(font.render(unit_name, True, t_col), (rect.x + 10, rect.y + 8))

                # 5. STATYSTYKI (Wewnątrz draw_recruitment)
        center_index = 2
        idx_on_center = self.recruitment_scroll + center_index

        if 0 <= idx_on_center < len(unit_types):
            unit_to_show = unit_types[idx_on_center]
            stats = UNIT_STATS.get(unit_to_show, {}) # Pobieramy słownik danych
            
            # A. Rysujemy główną tabelkę (Uniwersalna funkcja)
            self.draw_unit_stats_table(screen, 20, 250, unit_to_show, stats)

            # B. Rysujemy koszty (TYLKO TUTAJ - pod tabelką)
            if stats:
                # Panel tła dla kosztów (Twoja zielona ramka)
                cost_rect = pygame.Rect(20, 480, 450, 50)
                pygame.draw.rect(screen, (0, 30, 0), cost_rect) 
                pygame.draw.rect(screen, (200, 180, 100), cost_rect, 5)

                # Linie pionowe wewnątrz kosztów
                pygame.draw.line(screen, (200, 180, 100), (cost_rect.x + 150, cost_rect.y), (cost_rect.x + 150, cost_rect.bottom), 2)
                pygame.draw.line(screen, (200, 180, 100), (cost_rect.x + 300, cost_rect.y), (cost_rect.x + 300, cost_rect.bottom), 2)

                # Pobieranie wartości bezpośrednio ze słownika stats
                p_cost = stats.get('patent_cost', 0)
                m_cost = stats.get('production_cost', 0)
                time = stats.get('production_time', 0)

                # Renderowanie (używamy czcionki, która jest dostępna w Twoim draw_recruitment)
                screen.blit(font.render(f"Patent: {p_cost}", True, (255, 255, 0)), (cost_rect.x + 10, cost_rect.y + 15))
                screen.blit(font.render(f"Prod: {m_cost}", True, (255, 255, 0)), (cost_rect.x + 160, cost_rect.y + 15))
                screen.blit(font.render(f"Tury: {time}", True, (255, 255, 0)), (cost_rect.x + 310, cost_rect.y + 15))
                
                panel_rect = pygame.Rect(470, 620, 120, 60)
                pygame.draw.rect(screen, (40, 30, 25), panel_rect) # Brązowe wypełnienie
                pygame.draw.rect(screen, (200, 180, 100), panel_rect, 3)
                # 6. RESZTA (Poza ifem statystyk - rzeczy stałe)
        screen.blit(font.render(f"Gold: {castle.gold}", True, (255, 215, 0)), (w // 2 - 30, 640))
        
        pygame.draw.rect(screen, (100, 100, 100), self.scroll_up_button)
        pygame.draw.rect(screen, (100, 100, 100), self.scroll_down_button)
        screen.blit(font.render("▲", True, (255, 255, 255)), (self.scroll_up_button.x + 12, self.scroll_up_button.y + 8))
        screen.blit(font.render("▼", True, (255, 255, 255)), (self.scroll_down_button.x + 12, self.scroll_down_button.y + 8))
        
    def draw_unit_stats_table(self, screen, x, y, unit_name, stats_source):
        """
        Nowa wersja tabelki statystyk - używa grafik INFO_S32_0 / INFO_S32_1.
        x, y: gdzie na ekranie ma się pojawić lewy górny róg tabelki.
        stats_source: obiekt klasy Unit lub słownik ze statystykami.
        """
        if not stats_source:
            return

        # 1. Określamy tryb (SIMPLE dla chłopów/złota, COMBAT dla reszty)
        # Sprawdzamy kod jednostki - z obiektu lub ze słownika
        u_type = getattr(stats_source, 'type_code', None)
        if not u_type and isinstance(stats_source, dict):
            # Jeśli to słownik (np. z rekrutacji), szukamy klucza identyfikującego
            u_type = stats_source.get('type_code') 

        mode = "COMBAT"
        if u_type in ["GOLD", "PEAS", "SPECK", "SPECM"]:
            mode = "SIMPLE"

        # 2. Wywołujemy naszą profesjonalną tabelkę
        # self.unit_info_window to instancja klasy UnitInfoWindow, którą stworzyliśmy wcześniej
        self.unit_info_window.draw(screen, x, y, stats_source, mode)
                
    def draw_peasants(self, screen):
        font = pygame.font.SysFont(None, 24)

        castle = self.selected_castle
        if not castle:
            return

        w = screen.get_width()
        h = screen.get_height()

        happiness_factor = 0.5 + (castle.happiness / 100) * 0.5
        tax_income = int(castle.peasants * 0.1 * castle.tax_rate * happiness_factor)

        # =====================================================
        # TOP HUD
        # =====================================================

        screen.blit(font.render(f"Peasants: {castle.peasants}", True, (255,255,255)), (w//2 - 60, 20))
        screen.blit(font.render(f"Happiness: {castle.happiness}%", True, (200,255,200)), (w//2 - 70, 45))
        screen.blit(font.render(f"Gold: {castle.gold}", True, (255,215,0)), (w - 120, 20))

        # =====================================================
        # TAX PANEL (LEFT)
        # =====================================================

        screen.blit(font.render("TAX", True, (255,255,255)), (60, h//2 - 80))
        screen.blit(font.render(f"{castle.tax_rate:.1f}", True, (255,255,255)), (70, h//2 - 20))
        screen.blit(font.render(f"+{tax_income}/turn", True, (255,255,0)), (40, h//2 + 10))

        self.tax_minus_button.topleft = (20, h//2 - 40)
        self.tax_plus_button.topleft = (140, h//2 - 40)

        pygame.draw.rect(screen, (120,120,120), self.tax_minus_button)
        pygame.draw.rect(screen, (120,120,120), self.tax_plus_button)

        screen.blit(font.render("-", True, (0,0,0)), self.tax_minus_button.move(12,5))
        screen.blit(font.render("+", True, (0,0,0)), self.tax_plus_button.move(12,5))

        # =====================================================
        # CASTLE LIST (CENTER)
        # =====================================================

        panel_rect = pygame.Rect(w//2 - 150, h//2 - 60, 300, 120)
        pygame.draw.rect(screen, (70,50,40), panel_rect)

        owned = [c for c in self.castles if c.owner == self.players[self.current_player]]

        visible = owned[self.castle_list_offset:self.castle_list_offset+3]

        owned = [
            c for c in self.castles
            if c.owner == self.players[self.current_player] and not c.destroyed
        ]

        for i, c in enumerate(visible):
            txt = f"Castle ({c.x},{c.y})  P:{c.peasants} G:{c.gold}"
            screen.blit(font.render(txt, True, (255,255,255)),
                        (w//2 - 130, h//2 - 40 + i*30))

        self.castle_up_button.topleft = (w//2 + 160, h//2 - 60)
        self.castle_down_button.topleft = (w//2 + 160, h//2)

        pygame.draw.rect(screen,(120,120,120),self.castle_up_button)
        pygame.draw.rect(screen,(120,120,120),self.castle_down_button)

        screen.blit(font.render("^",True,(255,255,255)),self.castle_up_button.move(12,5))
        screen.blit(font.render("v",True,(255,255,255)),self.castle_down_button.move(12,5))

        # =====================================================
        # SEND PANEL (RIGHT)
        # =====================================================

        self.peasants_minus_button.topleft = (w - 180, h//2 - 40)
        self.peasants_plus_button.topleft = (w - 140, h//2 - 40)

        self.gold_minus_button.topleft = (w - 180, h//2 + 10)
        self.gold_plus_button.topleft = (w - 140, h//2 + 10)

        self.send_button.center = (w - 120, h//2 + 80)

        pygame.draw.rect(screen, (120,120,120), self.peasants_minus_button)
        pygame.draw.rect(screen, (120,120,120), self.peasants_plus_button)
        pygame.draw.rect(screen, (120,120,120), self.gold_minus_button)
        pygame.draw.rect(screen, (120,120,120), self.gold_plus_button)
        pygame.draw.rect(screen, (80,140,80), self.send_button)

        screen.blit(font.render("-", True, (0,0,0)), self.peasants_minus_button.move(12,5))
        screen.blit(font.render("+", True, (0,0,0)), self.peasants_plus_button.move(12,5))
        screen.blit(font.render("-", True, (0,0,0)), self.gold_minus_button.move(12,5))
        screen.blit(font.render("+", True, (0,0,0)), self.gold_plus_button.move(12,5))

        screen.blit(font.render("SEND", True, (255,255,255)), self.send_button.move(30,10))

        screen.blit(font.render(f"P: {self.send_peasants_amount}", True, (255,255,255)),
                    (w-120, h//2 - 60))
        screen.blit(font.render(f"G: {self.send_gold_amount}", True, (255,255,0)),
                    (w-120, h//2 - 15))

        # =====================================================
        # BACK BUTTON
        # =====================================================

        self.draw_building_footer(screen)

    def draw_demolish_confirm(self, screen):
        font = pygame.font.SysFont(None, 28)
        win_w, win_h = 320, 160
        win_x = (screen.get_width() // 2) - (win_w // 2)
        win_y = (screen.get_height() // 2) - (win_h // 2)
        
        # Tło okna
        rect = pygame.Rect(win_x, win_y, win_w, win_h)
        pygame.draw.rect(screen, (40, 40, 40), rect) # Ciemne tło
        pygame.draw.rect(screen, (255, 0, 0), rect, 2) # Czerwona ramka ostrzegawcza

        # Tekst pytania
        text = font.render("Zburzyć ten zamek?", True, (255, 255, 255))
        screen.blit(text, (win_x + 60, win_y + 30))

        # Przyciski (używamy tych samych rectów co w handle_mouse_click!)
        self.demolish_yes = pygame.Rect(win_x + 40, win_y + 90, 100, 40)
        self.demolish_no = pygame.Rect(win_x + 180, win_y + 90, 100, 40)

        pygame.draw.rect(screen, (0, 150, 0), self.demolish_yes) # Zielony TAK
        pygame.draw.rect(screen, (150, 0, 0), self.demolish_no)  # Czerwony NIE

        screen.blit(font.render("TAK", True, (255,255,255)), (win_x + 70, win_y + 100))
        screen.blit(font.render("NIE", True, (255,255,255)), (win_x + 210, win_y + 100))

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
        
    def get_unit_at(self, x, y):
        for unit in self.units:
            # Ignoruj jednostki, które są w trakcie budowy!
            if getattr(unit, 'is_building', False):
                continue
                
            if unit.x == x and unit.y == y:
                return unit
        return None

    def draw_castle_menu(self, screen, mx, my):
        if self.screen != "castle":
            return 

        # 1. Definicja opcji (Te same co wcześniej)
        options = ["Buduj", "ZBURZ ZAMEK", "ROZBUDUJ MURY"]
        self.menu_rects.clear()

        # Parametry (sub_h i krok pętli są identyczne = 35px, aby nie było dziur)
        menu_w, menu_h = 180, 35
        menu_x = self.menu_button.x
        menu_y = self.menu_button.y + 40

        # 2. Rysujemy główne opcje
        for i, opt in enumerate(options):
            # i * menu_h sprawia, że przyciski idealnie do siebie przylegają
            rect = pygame.Rect(menu_x, menu_y + i * menu_h, menu_w, menu_h)
            self.draw_button(screen, opt, rect)
            self.menu_rects[opt] = rect

        # --- PRZYPISANIE PRZYCISKÓW DLA handle_mouse (To czego brakowało) ---
        self.demolish_button = self.menu_rects.get("ZBURZ ZAMEK")
        self.wall_button = self.menu_rects.get("ROZBUDUJ MURY")

        # 3. Logika Submenu (Buduj)
        buduj_rect = self.menu_rects["Buduj"]
        
        # Szeroki obszar bezpieczny: od przycisku Buduj w lewo aż do końca submenu
        safe_zone_to_submenu = pygame.Rect(menu_x - 165, menu_y, 170, 200)

        if buduj_rect.collidepoint(mx, my) or (getattr(self, "build_open", False) and safe_zone_to_submenu.collidepoint(mx, my)):
            self.build_open = True
            self.draw_build_submenu(screen, menu_x, menu_y)
        else:
            # Zamykamy tylko jeśli myszka wyjdzie poza obszar pionowy głównego menu i submenu
            if mx > menu_x: 
                self.build_open = False
        
    def draw_build_submenu(self, screen, menu_x, menu_y):
        castle = self.selected_castle
        if not castle: return

        sub_w, sub_h = 160, 40 # Wysokość 40
        sub_x = menu_x - sub_w
        sub_y = menu_y

        buildings = ["hospital", "school", "koszary", "forge", "workshop"]
        self.build_rects.clear()

        for i, b in enumerate(buildings):
            # i * sub_h sprawia, że przyciski stykają się idealnie (brak dziur)
            rect = pygame.Rect(sub_x, sub_y + i * sub_h, sub_w, sub_h)
            
            is_built = b in castle.buildings
            
            if is_built:
                # WERSJA WYGASZONA:
                # Ciemniejszy szary, brak reakcji na myszkę, ten sam font
                pygame.draw.rect(screen, (50, 50, 50), rect) # Ciemne tło
                pygame.draw.rect(screen, (80, 80, 80), rect, 1) # Ciemniejsza ramka
                
                # Renderujemy sam tekst (ten sam styl co w draw_button, ale szary)
                small_font = pygame.font.SysFont(None, 20)
                txt_surf = small_font.render(b, True, (100, 100, 100)) # Szary tekst
                screen.blit(txt_surf, txt_surf.get_rect(center=rect.center))
            else:
                # WERSJA AKTYWNA:
                # Twoja standardowa funkcja z efektem hover
                self.draw_button(screen, b, rect)

            self.build_rects[b] = rect
         
    def handle_recruitment_click(self, mx, my):
        castle = self.selected_castle
        unit_types = self.recruitment_unit_types
        if not castle: return

       # 1. PRZYCISK INFO (Podąża za środkiem listy po lewej)
        if self.info_button.collidepoint(mx, my):
            # Obliczamy środek listy dokładnie tak samo jak w statystykach
            center_idx = self.recruitment_scroll + 2
            
            if 0 <= center_idx < len(unit_types):
                u_name = unit_types[center_idx]
                
                # Sprawdzamy czy opis istnieje w UNIT_STATS
                if u_name in UNIT_STATS and 'description' in UNIT_STATS[u_name]:
                    self.unit_info_text = UNIT_STATS[u_name]['description']
                    self.screen = "unit_info"
                else:
                    print(f"Brak opisu dla jednostki: {u_name}")
            return

        if self.back_button.collidepoint(mx, my):
            self.screen = "garrison"; return

        if self.buy_patent_button.collidepoint(mx, my):
            # Logika: Kupujemy jednostkę, która jest aktualnie wycelowana na środku (indeks 2)
            center_idx = self.recruitment_scroll + 2
            
            if 0 <= center_idx < len(unit_types):
                u_name = unit_types[center_idx]
                
                # Sprawdzamy status patentu
                if not self.castle_has_patent(castle, u_name):
                    print(f"Kupuję patent ze środka listy: {u_name}")
                    castle.buy_patent(u_name)
                else:
                    print(f"Patent na {u_name} jest już kupiony (wygaszony na liście).")
            return

        
        if self.garrison_gfx.handle_prod_click(mx, my, castle):
            if self.selected_patent_index is not None:
                p = castle.patents[self.selected_patent_index]
                u_name = p["unit_type"] if isinstance(p, dict) else p
                if u_name:
                    castle.start_production(u_name)
                    print(f"Uruchomiono produkcję: {u_name}")
            else:
                print("Najpierw zaznacz patent!")
            return

        if self.stop_prod_button.collidepoint(mx, my):
            castle.stop_production(); return

        if self.remove_patent_button.collidepoint(mx, my):
            if self.selected_patent_index is not None:
                p = castle.patents[self.selected_patent_index]
                u_name = p["unit_type"] if isinstance(p, dict) else p
                
                # Zatrzymaj produkcję TYLKO jeśli usuwamy to, co się właśnie buduje
                if castle.production_enabled and castle.production_unit_type == u_name:
                    castle.stop_production()
                    
                castle.patents[self.selected_patent_index] = None
                self.selected_patent_index = None
            return

        # KLIKNIĘCIE W PATENT (Prawa strona)
        for i, rect in enumerate(self.patent_rects):
            if rect.collidepoint(mx, my):
                if i < len(castle.patents) and castle.patents[i]:
                    self.selected_patent_index = i
                    self.selected_unit_type = None # Resetujemy wybór z lewej listy
                    
                    # JEDNORAZOWY SKOK LISTY:
                    u_name = castle.patents[i]["unit_type"] if isinstance(castle.patents[i], dict) else castle.patents[i]
                    if u_name in unit_types:
                        target_idx = unit_types.index(u_name)
                        self.recruitment_scroll = target_idx - 2 # Ustaw na środku
                    return

        # 3. SCROLL
        if self.scroll_up_button.collidepoint(mx, my):
            self.recruitment_scroll = max(-2, self.recruitment_scroll - 1); return
        if self.scroll_down_button.collidepoint(mx, my):
            self.recruitment_scroll = min(len(unit_types)-3, self.recruitment_scroll + 1); return

        # 4. NA KOŃCU LISTA PO LEWEJ (Matematyczne sprawdzanie obszaru)
        start_x, start_y = 30, 80
        box_w, box_h, gap = 220, 30, 2
        
        if start_x <= mx <= start_x + box_w:
            relative_y = my - start_y
            slot_index = relative_y // (box_h + gap)
            if 0 <= slot_index < 5:
                clicked_unit_idx = self.recruitment_scroll + int(slot_index)
                if 0 <= clicked_unit_idx < len(unit_types):
                    self.recruitment_scroll = clicked_unit_idx - 2 # Centrowanie
                    self.selected_unit_type = clicked_unit_idx
                    # self.selected_patent_index = None
                    return
   
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
 
    def handle_camera(self):
        keys = pygame.key.get_pressed()
        
        # --- ZMIANA PRĘDKOŚCI KAMERY ---
        scroll_speed = 30  # <--- Zmień tę liczbę, aby przyspieszyć/zwolnić (np. 10, 15, 20)
        
        # Osobne flagi dla ruchu w poziomie (X) i pionie (Y)
        moving_x = False
        moving_y = False
# === OGRANICZENIA MAPY (GRANICE KAFELKOWE) ===
        # Zakładamy, że kafelki mają 32x32 piksele
        TILE_SIZE = 32
        
        # Pobieramy prawdziwą wielkość mapy z Twojej listy (np. 64 na 64)
        if hasattr(self, 'map') and self.map:
            map_width_tiles = len(self.map[0])
            map_height_tiles = len(self.map)
        else:
            # Awaryjnie, gdyby mapy nie było, ustawiamy sztywny rozmiar (np. 64)
            map_width_tiles = 64
            map_height_tiles = 64

        # Obliczamy maksymalny wychył kamery. 
        # Od szerokości całej mapy w pikselach ODEJMUJEMY szerokość Twojego okna (1024x768).
        max_x = (map_width_tiles * TILE_SIZE) - 1024
        max_y = (map_height_tiles * TILE_SIZE) - 768

        # Zabezpieczenie: jeśli zrobisz mapę testową, która jest mniejsza niż ekran,
        # max_x/max_y byłyby na minusie. To nie pozwala im spaść poniżej 0.
        max_x = max(0, max_x)
        max_y = max(0, max_y)

        # Twarda blokada (Clamp): nie pozwalamy kamerze spaść poniżej 0 (lewa krawędź)
        # ani przekroczyć max_x (prawa krawędź).
        self.camera_x = max(0, min(self.camera_x, max_x))
        self.camera_y = max(0, min(self.camera_y, max_y))
        
        # --- RUCH W POZIOMIE (Oś X) ---
        # Używamy elif, żeby ubezpieczyć się przed wciśnięciem 'A' i 'D' jednocześnie
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.camera_x -= scroll_speed
            moving_x = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.camera_x += scroll_speed
            moving_x = True

        # --- RUCH W PIONIE (Oś Y) ---
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.camera_y -= scroll_speed
            moving_y = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.camera_y += scroll_speed
            moving_y = True

        # === NIEZALEŻNE DOCIĄGANIE (Snapping) ===
        # Puszczasz klawisze lewo/prawo? Wyrównujemy tylko oś X!
        if not moving_x:
            self.camera_x = round(self.camera_x / 32) * 32
            
        # Puszczasz klawisze góra/dół? Wyrównujemy tylko oś Y!
        if not moving_y:
            self.camera_y = round(self.camera_y / 32) * 32

        # ============================================
        # TUTAJ MOŻESZ ODKOMENTOWAĆ OGRANICZENIA MAPY
        map_pixel_width = MAP_WIDTH * TILE_SIZE
        map_pixel_height = MAP_HEIGHT * TILE_SIZE
        self.camera_x = max(0, min(self.camera_x, map_pixel_width - 1024))
        self.camera_y = max(0, min(self.camera_y, map_pixel_height - 768))
   
    def check_unit_info(self, mx, my):
        self.inspected_unit = None # Reset na start
        
        # 1. Najpierw sprawdź garnizon (jeśli jesteś w zamku)
        if self.screen == "garrison":
            castle = self.selected_castle
            if castle:
                start_x, start_y = 100, 120
                offset_x, offset_y = 130, 210
                col = (mx - start_x) // offset_x
                row = (my - start_y) // offset_y
                if 0 <= col < 6 and 0 <= row < 2:
                    idx = row * 6 + col
                    if idx < len(castle.garrison):
                        self.inspected_unit = castle.garrison[idx]

        # 2. Jeśli nie garnizon, sprawdź mapę
        if not self.inspected_unit:
            self.inspected_unit = self.find_unit_at(mx, my)

        # 3. Jeśli coś znalazłeś, ustal tryb
        if self.inspected_unit:
            if self.inspected_unit.type_code in ["GOLD", "PEAS", "SPECK", "SPECM"]:
                self.info_mode = "SIMPLE"
            else:
                self.info_mode = "COMBAT"

    def handle_recruitment_scroll(self, event):
        # Pobieramy aktualną listę dostępnych jednostek dla wybranego zamku
        castle = self.selected_castle
        if not castle: return

        # Filtrujemy listę dokładnie tak samo jak w draw_recruitment
        available_units = [u for u in UNIT_STATS.keys() if 
                        self.castle_has_patent(castle, u) or 
                        castle.is_patent_available(u)]
        
        # Ile jednostek mamy łącznie
        total_units = len(available_units)
        # Widzimy 5 jednostek na raz, więc max_scroll to różnica
        max_scroll = max(0, total_units - 3)
        

        if event.button == 4: # GÓRA
            if self.recruitment_scroll > -2:
                self.recruitment_scroll -= 1
        elif event.button == 5: # DÓŁ
            if self.recruitment_scroll < max_scroll:
                self.recruitment_scroll += 1
           
    def handle_tryb_mapy_button(self):
        """Wyłącza zaznaczenie jednostki, pozwalając na klikanie w zamki."""
        self.selected_unit = None
        self.selected_castle = None
        print("Tryb mapy: Odznaczono jednostki.") 

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

    def handle_dropdown_clicks(self, mx, my):
        #tu jest dokłana obsługa
        # def execute_menu_command(self, menu, index):
        # Sprawdzamy menu System
        #if menu == "System":
         #   if index == 5:  # "Koniec" (szósta opcja, więc indeks 5)
          #      print("Zamykanie gry...")
           #     pygame.quit()
            #    import sys
             #   sys.exit()
                
           # elif index == 2: # Zapisz grę
            #    print("Zapisywanie stanu gry...")
                # Tutaj w przyszłości dodasz self.save_game()
                    
        # Sprawdzamy menu Mapa
       # elif menu == "Mapa":
        #    opcja = self.menu_options['Mapa'][index]
         #   print(f"Wybrano opcję mapy: {opcja}")
            
          #  if index == 3: # "Nic"
           #     print("Ukrywam elementy mapy...")

        """Obsługuje kliknięcia wewnątrz rozwiniętych list System i Mapa."""
        if not self.active_dropdown:
            return False

        # Pobieramy przyciski dla aktualnie otwartego menu
        buttons_to_check = {}
        if self.active_dropdown == "System":
            buttons_to_check = getattr(self, 'system_buttons', {})
        elif self.active_dropdown == "Mapa":
            buttons_to_check = getattr(self, 'mapa_buttons', {})

        # Sprawdzamy kolizję dla każdej opcji w słowniku
        for name, rect in buttons_to_check.items():
            if rect.collidepoint(mx, my):
                print(f"DEBUG {self.active_dropdown}: Wybrano opcję -> {name}")
                
                # Tymczasowe zamykanie gry dla testów
                pygame.quit()
                import sys
                sys.exit()
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
    
    def handle_action_button_click(self, button_index):
        """button_index: od 0 do 5 (odpowiada self.action_buttons po prawej stronie)"""
        u = self.selected_unit
        if not u: return

        # Sprawdzamy, czy w armii jest budowniczy (jeśli u to armia)
        has_builder = False
        if u.type == "Budowniczy":
            has_builder = True
        elif hasattr(u, 'garrison'):
            has_builder = any(slot is not None and slot.type == "Budowniczy" for slot in u.garrison)

        if self.build_menu_open:
            # MENU BUDOWANIA: ["DROGA", "PUŁAPKA", "SKARB", "WIEŻA", "TWIERDZA", "ZAMEK"]
            self.execute_build_action(button_index, u)
        else:
            # MENU GŁÓWNE: ["TRYB MAPY", "ATK", "SPL", "WAIT", "BUILD", "REC"]
            if button_index == 0:
                self.handle_tryb_mapy_button()
                
            elif button_index == 4: # Przycisk BUILD
                if has_builder:
                    self.build_menu_open = True
                    print(f"Otwarto menu budowania dla {u.type}.")
                else:
                    print("Ta jednostka/armia nie posiada Budowniczego!")
                    
            elif button_index == 5: # Przycisk REC (możesz tu dać np. ROZFORMOWANIE)
                self.execute_disband_army(u)
 
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

    def draw_trap_popup(self, screen):
        # Sprawdź czy self.font istnieje, jeśli nie, użyj systemowej
        font = getattr(self, 'font', pygame.font.SysFont(None, 32))
        
        # Rozmiar okna (na środku ekranu)
        w, h = 300, 200
        x = (SCREEN_WIDTH - w) // 2
        y = (SCREEN_HEIGHT - h) // 2
        
        popup_rect = pygame.Rect(x, y, w, h)
        
        # Rysujemy tło okna
        pygame.draw.rect(screen, (50, 50, 50), popup_rect) # Szary
        pygame.draw.rect(screen, (255, 255, 255), popup_rect, 3) # Biała ramka
        
        # Tekst
        title = font.render("PUŁAPKA", True, (255, 255, 255))
        screen.blit(title, (popup_rect.centerx - title.get_width()//2, popup_rect.y + 20))
        
        # Przyciski
        self.btn_trap_stop = pygame.Rect(x + 20, y + 100, 110, 50)
        self.btn_trap_dalej = pygame.Rect(x + 170, y + 100, 110, 50)
        
        pygame.draw.rect(screen, (150, 0, 0), self.btn_trap_stop) # Czerwony
        pygame.draw.rect(screen, (0, 150, 0), self.btn_trap_dalej) # Zielony
        
        # Tekst na przyciskach
        stop_txt = font.render("STOP", True, (255, 255, 255))
        dalej_txt = font.render("DALEJ", True, (255, 255, 255))
        
        screen.blit(stop_txt, (self.btn_trap_stop.centerx - stop_txt.get_width()//2, self.btn_trap_stop.centery - stop_txt.get_height()//2))
        screen.blit(dalej_txt, (self.btn_trap_dalej.centerx - dalej_txt.get_width()//2, self.btn_trap_dalej.centery - dalej_txt.get_height()//2))
       
    def count_builders_near(self, pos):
        px, py = pos
        # Szukamy budowniczych dokładnie na kafelku placu budowy
        return sum(1 for u in self.units if u.x == px and u.y == py and u.type.lower() == "budowniczy")
        
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
                        
    def handle_castle_entry(self, mx, my):
        """Sprawdza kliknięcie w budynki na mapie. Zwraca True, jeśli wejdzie do środka."""
        for castle in self.castles:
            # POBIERAMY TYP: Jeśli to Strażnica, obszar to 1x1, inaczej 2x2
            b_type = str(castle.building_type).strip()
            size = TILE_SIZE if b_type == "Strażnica" else TILE_SIZE * 2
            
            # Tworzymy prostokąt kolizji o odpowiednim rozmiarze
            rect = pygame.Rect(
                (castle.x * TILE_SIZE) - self.camera_x, 
                (castle.y * TILE_SIZE) - self.camera_y, 
                size, size
            )
            
            if rect.collidepoint(mx, my) and not getattr(castle, 'destroyed', False):
                self.selected_castle = castle
                self.selected_unit = None
                # Wybór odpowiedniego ekranu
                self.screen = "Strażnica" if b_type == "Strażnica" else "castle"
                print(f"Wejście do: {b_type} na {castle.x},{castle.y}")
                return True
        return False

    def draw_garrison_only(self, screen):
        # --- KLUCZOWA POPRAWKA ---
        castle = self.selected_castle
        if not castle:
            self.screen = "map" # Jeśli jakimś cudem nie ma zamku, wracamy
            return
        # --------------------------

        screen.fill((30, 30, 35)) # Ciemniejsze tło dla Strażnicy
        font = pygame.font.SysFont(None, 32)
        
        title = font.render(f"GARNIZON: {castle.building_type.upper()}", True, (200, 200, 200))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 50))

        # Rysujemy 10 slotów (2 rzędy po 5)
        start_x = 150
        start_y = 200
        gap = 20
        slot_size = 120

        for i in range(10):  # Zawsze rysuj 10 slotów
            col = i % 5
            row = i // 5
            slot_rect = pygame.Rect(150 + col * 140, 200 + row * 140, 120, 120)
            
            # 1. Rysuj tło slotu (Zawsze widoczne!)
            pygame.draw.rect(screen, (50, 50, 60), slot_rect)
            pygame.draw.rect(screen, (100, 100, 120), slot_rect, 2)
            
            # 2. Rysuj jednostkę, jeśli istnieje
            if i < len(castle.garrison) and castle.garrison[i]:
                unit = castle.garrison[i]
                
                # Rysowanie ikonki (jeśli masz unit.image) lub tekstu
                # Jeśli używasz tekstu:
                u_txt = font.render(unit.type[:5], True, (255, 255, 255))
                screen.blit(u_txt, (slot_rect.centerx - u_txt.get_width()//2, 
                                    slot_rect.centery - u_txt.get_height()//2))

                # --- NOWOŚĆ: Obwódka jeśli jednostka jest zaznaczona do wyjścia ---
                if unit in self.selected_units:
                    pygame.draw.rect(screen, (0, 255, 0), slot_rect, 4) # Zielona ramka

        # Przycisk POWRÓT (już masz)
        # TYLKO w __init__:
        self.draw_building_footer(screen)

        # Przycisk RELEASE
        self.release_tower = pygame.Rect(screen.get_width()//2 - 80, 650, 160, 45)
        self.draw_button(screen, "RELEASE", self.release_tower)

        
        # Przycisk ZNISZCZ
        self.destroy_button = pygame.Rect(screen.get_width()//2 + 90, 650, 160, 45)
        # Rysujemy na czerwono
        pygame.draw.rect(screen, (150, 0, 0), self.destroy_button)
        txt = font.render("ZNISZCZ", True, (255, 255, 255))
        screen.blit(txt, (self.destroy_button.centerx - txt.get_width()//2, 
                        self.destroy_button.centery - txt.get_height()//2))

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

    def draw_building_footer(self, screen):
        if self.screen == "castle":
            self.draw_button(screen, "", self.back_button_castle, style="castle")
        else:
            self.draw_button(screen, "", self.back_button_bldg, style="bldg")

        if self.selected_castle and getattr(self.selected_castle, 'building_type', "") == "Strażnica":
            self.draw_button(screen, "ZBURZ", self.destroy_button, (100, 40, 40))

        if self.screen == "garrison":                          # ← DODAJ TO
            pass  # przycisk wypuść jest w garrison_gfx.draw()

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
                    if target.garrison[slot_idx] is solo_unit: # 'is' sprawdza konkretny obiekt
                        target.garrison[slot_idx] = None
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
                            if target.garrison[slot_idx] is unit_to_move:
                                target.garrison[slot_idx] = None
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
  
    def show_foundation_menu(self, gx, gy):
        self.screen = "foundation_selection"
        self.construction_target = (gx, gy) # Zapamiętujemy, gdzie budujemy

    def draw_build_system(self, screen):
    # 1. Rysuj siatkę (opcjonalnie, tylko gdy budowniczy jest wybrany)
        if self.selected_unit and self.selected_unit.type == "Budowniczy":
            self.draw_grid_lines(screen)
            
            # 2. Logika podglądu (Universal Preview)
            mx, my = pygame.mouse.get_pos()
            gx = (mx + self.camera_x) // TILE_SIZE
            gy = (my + self.camera_y) // TILE_SIZE
            
            draw_x = gx * TILE_SIZE - self.camera_x
            draw_y = gy * TILE_SIZE - self.camera_y
            
            # Oblicz dystans (zasięg 1 pola)
            u = self.selected_unit
            dist_x = abs(gx - u.x)
            dist_y = abs(gy - u.y)
            
            # Warunki: w zasięgu (ale nie na sobie) i poprawny teren
            is_in_range = dist_x <= 1 and dist_y <= 1 and not (dist_x == 0 and dist_y == 0)
            
            # Sprawdzamy czy to nie fundamenty zamku 2x2!
            is_foundation = self.is_area_occupied_by_foundation(gx, gy)
            is_valid_terrain = self.can_build_trap(gx, gy) and not is_foundation

            preview_rect = pygame.Rect(draw_x, draw_y, TILE_SIZE, TILE_SIZE)

            if is_in_range and is_valid_terrain:
                # DOZWOLONE: Biała ramka
                pygame.draw.rect(screen, (255, 255, 255), preview_rect, 2)
            else:
                # NIEDOZWOLONE: Czerwone pole z kropkami
                s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                s.fill((255, 0, 0, 80)) # Półprzezroczysty czerwony
                
                # Wzorek kropek (z draw_build_system)
                for dx in range(4, TILE_SIZE, 8):
                    for dy in range(4, TILE_SIZE, 8):
                        pygame.draw.circle(s, (150, 0, 0), (dx, dy), 1)
                
                screen.blit(s, (draw_x, draw_y))
                pygame.draw.rect(screen, (255, 0, 0), preview_rect, 2)

    def can_build_trap(self, x, y):
        # gdzie można budować pułapkę
        if not (0 <= y < len(self.map) and 0 <= x < len(self.map[0])): return False
        terrain = self.map[y][x]
        # Blokada: l (las), g (niskie góry), G (wysokie góry), W (woda)
        if terrain in ["l", "g", "#", "&","S","x","B","b", "G", "W"]: return False
        # Nie budujemy na budynkach (duże litery) ani innych pułapkach
        if terrain == "X" or (terrain.isupper() and terrain not in ["P"]): return False
        return True           
            
    def can_build_road(self, x, y):
        # gdzie można budować drogę
        if not (0 <= y < len(self.map) and 0 <= x < len(self.map[0])):
            return False
        
        terrain = self.map[y][x]
        # Lista zakazana według Twoich wytycznych
        forbidden = ["l", "g", "#", "&", "S", "x", "B", "b", "G", "W"]
        
        if terrain in forbidden:
            return False
            
        # Nie budujemy na już istniejącej drodze (chyba że chcesz naprawiać?)
        if terrain == "_":
            return False
            
        return True

    def is_area_occupied_by_foundation(self, gx, gy):
        # mówi gdzie są fundamenty
        """Zwraca True, jeśli pole gx, gy jest częścią (lub samym) fundamentem #."""
        # Sprawdzamy: samo pole, lewo, góra, skos lewa-góra
        check_positions = [
            (gx, gy),       # Bezpośrednio
            (gx - 1, gy),   # Lewo
            (gx, gy - 1),   # Góra
            (gx - 1, gy - 1)# Skos
        ]
        
        for cx, cy in check_positions:
            if 0 <= cy < len(self.map) and 0 <= cx < len(self.map[0]):
                if self.map[cy][cx] == "#":
                    return True
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