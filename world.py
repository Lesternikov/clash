import main
from unit import Unit, UNIT_STATS
from castle import Castle, UNIT_REQUIREMENTS
from player import Player
from map_loader import load_map, load_fac_objects
from castle import BUILDINGS
from castle import BUILDING_TYPES
import sys
import heapq
import os      # Obsługa ścieżek do plików (to naprawi Twój błąd)
import random  # Do losowania drzew (żeby las nie był nudny)
import pygame  # Silnik gry
from castle_graphics import CastleGraphics

TILE_SIZE = 32
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800
# Rozmiar Twojej logicznej mapy (listy w self.map)
MAP_WIDTH = 100 
MAP_HEIGHT = 100

TERRAIN_TYPES = {
    "&": {"name": "kult", "color": (139, 69, 19)},
    "S": {"name": "świątynia","color": (255, 255, 255)},
    "$": {"name": "złoto", "color": (255, 215, 0),"cost": 4},
    "_": {"name": "droga","color": (185, 185, 185),"cost": 3},
    "x": {"name": "pułapka","color": (25, 25, 25)},
    ".": {"name": "trawa", "color": (34, 139, 34),"cost": 4},
    "l": {"name": "las", "color": (0, 100, 0),"cost": 6},
    "p": {"name": "pustynia","color": (210, 105, 30),"cost": 5},
    "W": {"name": "woda", "color": (0, 199, 255)},
    "B": {"name": "bagno","color": (255, 0, 0)},
    "b": {"name": "bagno płytkie","color": (169, 169, 169),"cost": 7},
    "G": {"name": "góry","color": (85, 85, 85)},
    "g": {"name": "góry niskie","color":(119, 119, 119),"cost": 8},
    "#": {"name": "zamek","color":(34, 139, 34), "cost": 4}, # Dodaj to!
}

def draw_text(screen, text, x, y, color=(0, 0, 0)):
    font = pygame.font.SysFont(None, 24)
    img = font.render(str(text), True, color)
    screen.blit(img, (x, y))

class PrisonSlot:
    def __init__(self, general=None):
        self.general = general
        self.turns_in_prison = 0

class World:
    def __init__(self):
        # Pobieramy wymiary ekranu dla dynamicznego pozycjonowania
        w = pygame.display.get_surface().get_width()
        h = pygame.display.get_surface().get_height()
        
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 24)
        self.font_small = pygame.font.SysFont(None, 20)
        self.modal_font = pygame.font.SysFont(None, 32)
        self.btn_font = pygame.font.SysFont(None, 28, bold=True)

        # --- LOGIKA I DANE ---
        # ====================================================
        #                     ŁADOWANIE GRAFIKI MAPY
        # ====================================================
    
        self.deep_water_images = []
        # 1. Najpierw definiujemy puste listy/słowniki
        self.water_layers = [[] for _ in range(13)] # 12 brzegów + 1 morze
        self.water_frame_index = 0
        self.grass_frame_index = 0
        self.water_tile_mapping = {}
        self.terrain_mappings = {}
        self.grass_tile_mapping = {}

        self.road_gfx = {"grass": {}, "swamp": [], "desert_trans": []} # Inicjalizacja pustego słownika
        self.load_all_assets()
        self.load_road_graphics() # <--- TO MUSI TU BYĆ       
        self.load_all_water_assets()
        self.load_castle_and_tower()
        self.castle_gfx = CastleGraphics(SCREEN_WIDTH, SCREEN_HEIGHT)

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
        self.castle_gfx = CastleGraphics("assets")
        # Ładowanie danych
        # =====================================================
        #              SYSTEMOWE PRZYCISKI (STAŁE)
        # =====================================================
        # UNIWERSALNY PRZYCISK POWRÓT (Ten większy i niżej, o który prosiłeś)
        self.back_button = pygame.Rect(40, 710, 180, 45)
        
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
        
        # Pozycje budynków wewnątrz zamku (Recty na stałe)
        self.forge_button = pygame.Rect(750, 500, 160, 40)
        self.workshop_button = pygame.Rect(290, 480, 160, 40)
        self.hospital_button = pygame.Rect(110, 350, 160, 40)
        self.school_button = pygame.Rect(830, 250, 160, 40)

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
        #              EKRAN DWÓR / WIĘZIENIE
        # =====================================================
        self.prison_slots = [PrisonSlot(), PrisonSlot(), PrisonSlot()]
        self.victories = 0
        self.defeats = 0
        self.court_back_button = pygame.Rect(15, 125, 105, 55)
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
        self.action_buttons = []
        
        # Tworzymy 6 przycisków w siatce 2x3 (tak jak miałeś wcześniej)
        panel_x = 800
        panel_y = 640
        for row in range(2):
            for col in range(3):
                # 70x70 to rozmiar, 65 i 55 to odstępy - dopasuj pod swoją grafikę
                rect = pygame.Rect(panel_x + col * 65, panel_y + row * 55, 70, 70)
                self.action_buttons.append(rect)
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
        base_bg_path = r"D:\clash reverse\assets\BACKGR3_S32_"
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
        # ==================================================================
        #                    ŁADOWANIE ANIMACJI ZAMKU
        # ==================================================================
        base_path = r"D:\clash reverse\assets\zamekczerwony\BUILDIN1_S32_"
        
        # --- GRAFIKI ZAMKU (2x2) ---
        self.castle_tiles = {0: [], 1: [], 2: [], 3: [], 4: []}
        for stage in range(4):
            for i in range(4):
                file_num = 225 + (stage * 4) + i
                try:
                    img = pygame.image.load(f"{base_path}{file_num}.png").convert_alpha()
                    self.castle_tiles[stage].append(img)
                except:
                    print(f"Brak pliku zamku: {file_num}")

        # Zniszczony zamek (257-260)
        for i in range(4):
            try:
                img = pygame.image.load(f"{base_path}{257 + i}.png").convert_alpha()
                self.castle_tiles[4].append(img)
            except: pass

        # --- GRAFIKI STRAŻNICY (1x1) ---
        self.tower_tiles = {}
        # Ładujemy pliki 0, 1, 2, 3 (Budowa + Gotowa)
        for i in range(4): 
            try:
                img = pygame.image.load(f"{base_path}{i}.png").convert_alpha()
                # 0, 1, 2 to etapy budowy, 3 to gotowa wieża
                self.tower_tiles[i] = img
            except:
                print(f"Brak pliku strażnicy: {i}")
        
        # Zniszczona strażnica (plik nr 8)
        try:
            self.tower_tiles[4] = pygame.image.load(f"{base_path}8.png").convert_alpha()
        except:
            print("Brak pliku zniszczonej strażnicy (8.png)")
        
     
# --- INICJALIZACJA GRACZY (Poprawiona pod Player.py) ---
        self.players = []
        player_data = [
            ("Don Marek", (200, 0, 0)),    # ID 0
            ("Lech VI", (0, 0, 200)),      # ID 1
            ("Mściwój", (0, 150, 0)),      # ID 2
            ("Biały Kieł", (220, 220, 220)),# ID 3
            ("Złoty Pan", (200, 200, 0))   # ID 4
        ]

        from player import Player
        for i, (name, color) in enumerate(player_data):
            # i to nasze player_id (0, 1, 2, 3, 4)
            new_player = Player(i, name, color)
            self.players.append(new_player)
    
    def load_all_assets(self):
        
        # --- WARSTWA 0: FUNDAMENTY ---
        # Trawa: ładujemy tylko grafiki środka (np. pliki 20, 21, 22 - dostosuj numery!)
        # Jeśli Twoje warianty trawy to BACKGR3_S32_13, 14, 15:
        path_base = os.path.join("assets", "BACKGR3_S32")
        self.grass_variants = [
            self.load_single_img(os.path.join(path_base, "BACKGR3_S32_0.png")),
            self.load_single_img(os.path.join(path_base, "BACKGR3_S32_1.png")),
            self.load_single_img(os.path.join(path_base, "BACKGR3_S32_3.png")),]


        # Woda: Twoja animacja (klatki 595-603)
        self.river_anim = self.load_river_animation() 
        self.sea_anim = self.load_sea_animation() # <--- DODAJ TĘ LINIJKĘ
        self.load_sea_cliffs()
        self.edges = {}   # Tu trzymamy tylko brzegi (pliki 0-11 z zestawu)
        self.centers = {} # Tu trzymamy tylko pełne środki (Twoja ręczna kontrola)

        self.edges["."] = self.load_edge_only_set(20) 
        self.centers["."] = self.grass_variants # Środek to nadal Twoje losowe kępki

        # --- GÓRY WYSOKIE (G) ---
        # Brzegi i skosy (pliki 187-198)
        self.edges["G"] = self.load_edge_only_set(187)
        # Ręczna kontrola środków (możesz dać kilka wariantów!)
        self.centers["G"] = [
            self.load_single_img(os.path.join("assets","BACKGR3_S32","BACKGR3_S32_699.png")),
            self.load_single_img(os.path.join("assets","BACKGR3_S32","BACKGR3_S32_700.png"))]
        # 1. Wysokie góry na trawie
        self.high_mountain_grass_edges = self.load_edge_only_set(187) # Przykładowe ID
        # 2. Wysokie góry na pustyni
        self.high_mountain_desert_edges = self.load_edge_only_set(211) # Przykładowe ID
        # 3. Wysokie góry na bagnie
        self.high_mountain_swamp_edges = self.load_edge_only_set(199)  # Przykładowe ID
        # --- PRZYKŁAD: PUSTYNIA (p) ---
        # Ładujemy brzegi (12 plików, od 20 do 31)
        self.edges["p"] = self.load_edge_only_set(8) 
        # Ręcznie definiujemy środki dla pustyni (np. plik 32, 33)
        self.centers["p"] = [self.load_single_img(os.path.join("assets","BACKGR3_S32","BACKGR3_S32_4.png"))]

        self.edges["P"] = self.load_edge_only_set(32) 
        # Ręcznie definiujemy środki dla pustyni (np. plik 32, 33)
        self.centers["P"] = [self.load_single_img(os.path.join("assets","BACKGR3_S32","BACKGR3_S32_44.png"))]

        # --- LAS (l) ---
        self.edges["l"] = self.load_edge_only_set(45) 
        # NADPISUJEMY ID 0, żeby zawsze rysowało Twoje wybrane samotne drzewo
        self.edges["l"][0] = self.load_single_img("assets/BACKGR3_S32/BACKGR3_S32_58.png")

        # Środki lasu (gęstwina)
        self.centers["l"] = [
            self.load_single_img("assets/BACKGR3_S32/BACKGR3_S32_54.png"),
            self.load_single_img("assets/BACKGR3_S32/BACKGR3_S32_56.png")
]
        
        # Ładujemy brzegi bagna (12 plików, od 20 do 31)
        self.edges["B"] = self.load_edge_only_set(24) 
        # Ręcznie definiujemy środki dla pustyni (np. plik 32, 33)
        self.centers["B"] = [self.load_single_img(os.path.join("assets","BACKGR3_S32", "BACKGR3_S32_7.png"))]

        # Góry stykające się z trawą (np. Twój stary zestaw)
        self.mountain_grass_edges = self.load_edge_only_set(174) # przykładowe ID
        
        # Góry stykające się z pustynią (nowy zestaw)
        self.mountain_desert_edges = self.load_edge_only_set(161) # przykładowe ID
        # 3. NOWOŚĆ: Góry na bagnie (podaj ID pierwszego pliku z zestawu bagiennego)
        self.mountain_swamp_edges = self.load_edge_only_set(199) # Przykładowe ID
        # Ręcznie definiujemy środki dla pustyni (np. plik 32, 33)
        self.centers["g"] = [self.load_single_img(os.path.join("assets","BACKGR3_S32", "BACKGR3_S32_173.png"))]
        # Rejestrujemy oba w edges, żeby system wiedział, że "g" ma autotiling
        self.edges["g"] = self.mountain_grass_edges # Domyślny
        # Świątynia (szukaj w okolicy kafelka 144/145 lub podobnych)
        self.temple_img = self.load_single_img(os.path.join("assets", "BACKGR3_S32", "BACKGR3_S32_732.png"))
        self.temple2_img = self.load_single_img(os.path.join("assets", "BACKGR3_S32", "BACKGR3_S32_737.png"))

        # Skarby (Złoto) - słownik wariantów
        self.treasure_imgs = {
            ".": self.load_single_img(os.path.join("assets", "BACKGR3_S32", "BACKGR3_S32_752.png")), # Wariant na trawie
            "p": self.load_single_img(os.path.join("assets", "BACKGR3_S32", "BACKGR3_S32_755.png"))  # Wariant na pustyni (Wpisz poprawny plik!)
        }
        
        # Ruiny - słownik wariantów
        self.ruins_img = self.load_single_img(os.path.join("assets", "zamekczerwony", "BUILDIN1_S32_8.png")),

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
            
    def load_edge_only_set(self, start_id):
        path_base = os.path.join("assets", "BACKGR3_S32")
        imgs = []
        # Ładujemy 12 kafelków (0-7 to krawędzie/rogi zewn., 8-11 to Twoje skosy)
        for i in range(start_id, start_id + 12):
            imgs.append(self.load_single_img(os.path.join(path_base, f"BACKGR3_S32_{i}.png")))
        
        return {
            # Krawędzie proste
            1: imgs[1], 6: imgs[6], 3: imgs[3], 4: imgs[4],
            # Rogi Zewnętrzne (Wypukłe)
            0: imgs[0], 2: imgs[2], 5: imgs[5], 7: imgs[7],
            # ROGI WEWNĘTRZNE (Twoje skosy z "czarnym polem")
            11: imgs[11], 10: imgs[10], 9: imgs[9], 8: imgs[8]
        }
    
    def draw_custom_overlay(self, screen, x, y, pos, overlay_dict, edge_id):
        """Rysuje nakładkę z obsługą losowego środka."""
        data = overlay_dict.get(edge_id)
        
        if not data:
            return

        if isinstance(data, list):
            # To jest środek (lista wariantów)
            # Używamy x i y jako ziarna, żeby kafelki się nie zmieniały co klatkę
            random.seed(x * 1000 + y)
            img = random.choice(data)
            # Resetujemy seed, żeby nie psuć losowości w innych częściach gry
            random.seed() 
        else:
            # To jest zwykły brzeg (pojedynczy Surface)
            img = data

        screen.blit(img, pos)

    def get_tile_connection_id(self, x, y, target_type, base_type=None):
        # 1. Definiujemy relacje przyjaźni (kto z kim się łączy bez brzegu)
        friends = {
            # Pustynia widzi góry i inną pustynię jako "przyjaciół"
            "p": ["p", "P","_", "g", "G", "W","S", "&", "$", None], 
            "P": ["P", "p", "g","_", "G", "W", "S", "&", "$", None],
            "B": ["B", "_", "S", "&", "#", "R", "V",".", "l", "p", "W", "g", "G", "S", "&", "$", "R", "#", "_", None],
            # Góry muszą odwzajemnić tę miłość, inaczej góra na styku z pustynią narysuje brzeg!
            "g": ["g" , "P", "W", None],
            "G": ["G", "P", None],
            "_": ["B","G", "g", None],
            "l": ["l", "S", "&","_", "#", "W", None],
            ".": ["_", "S", "&", "#", "R", "V",".", "l", "p", "W", "g", "G", "S", "&", "$", "R", "#", ".","","M", None],
            "M": ["w", "V", "M", "", None],
            "W": ["W", "M", "V", None], # <--- DODAJ TĘ LINIJKĘ DLA RZEKI!
        }
        
        
        # Pobieramy listę przyjaciół dla aktualnie rysowanego typu
        current_friends = friends.get(target_type, [target_type])

        def is_friendly(tx, ty):
            # ZMIANA: Autotiling musi patrzeć na tło, a nie obiekty!
            neighbor = self.get_bg_tile_at(tx, ty)
            return neighbor in current_friends

        # Sprawdzanie sąsiadów
        U = is_friendly(x, y-1)
        D = is_friendly(x, y+1)
        L = is_friendly(x-1, y)
        R = is_friendly(x+1, y)
        
        # Skosy (potrzebne do Twoich nowych kafelków 8-11)
        UL = is_friendly(x-1, y-1)
        UR = is_friendly(x+1, y-1)
        DL = is_friendly(x-1, y+1)
        DR = is_friendly(x+1, y+1)

       # --- LOGIKA DOPASOWANIA INDEKSU (0-12) ---

        # 1. NAJPIERW ROGI WEWNĘTRZNE (te z czarnym tłem, ID 8-11)
        if U and L and not UL: return 11
        if U and R and not UR: return 10
        if D and L and not DL: return 9
        if D and R and not DR: return 8

        # 2. POTEM ROGI ZEWNĘTRZNE (Twoje "cypelki" - w tym ten brakujący lewy górny!)
        # Muszą być przed krawędziami prostymi, bo róg to technicznie dwie krawędzie proste naraz.
        if not U and not L: return 0  # To jest Twój lewy górny róg
        if not U and not R: return 2  # Prawy górny róg
        if not D and not L: return 5  # Lewy dolny róg
        if not D and not R: return 7  # Prawy dolny róg

        # 3. NA SAMYM KOŃCU KRAWĘDZIE PROSTE
        if not U: return 1
        if not D: return 6
        if not L: return 3
        if not R: return 4

        # 4. Jeśli nic powyższego nie pasuje, to znaczy, że kafel jest otoczony (środek)
        return 12
    
    def get_tile_at(self, x, y):
        if 0 <= y < len(self.map) and 0 <= x < len(self.map[y]):
            return self.map[y][x]
        return " "

    def get_bg_tile_at(self, x, y):
        """Pobiera kafelek tła, całkowicie odporna na błędy wyjścia poza mapę."""
        if 0 <= y < len(self.bg_map) and 0 <= x < len(self.bg_map[y]):
            return self.bg_map[y][x]
        return None # Domyślnie udaje trawę poza mapą
    
    def get_road_tile(self, x, y):
        # 1. Połączenia dróg zostają bez zmian
        n = 1 if self.get_tile_at(x, y-1) == "_" else 0
        e = 2 if self.get_tile_at(x+1, y) == "_" else 0
        s = 4 if self.get_tile_at(x, y+1) == "_" else 0
        w = 8 if self.get_tile_at(x-1, y) == "_" else 0
        connections = n + e + s + w

        # 2. POBIERAMY TŁO Z UKRYTEJ MAPY! Koniec ze zgadywaniem!
        # Wiemy DOKŁADNIE, na czym leży lewy sąsiad (nawet jeśli stoi tam góra lub skarb)
        bg_left   = self.bg_map[y][x-1] if x > 0 else "."
        bg_right  = self.bg_map[y][x+1] if x < len(self.map[0])-1 else "."
        bg_up     = self.bg_map[y-1][x] if y > 0 else "."
        bg_down   = self.bg_map[y+1][x] if y < len(self.map)-1 else "."

        # Dokładnie wiemy, na czym leży SAMA DROGA
        bg_center = self.bg_map[y][x]

        pustynia_warianty = ["p", "P", "s"]
        trawa_warianty = ["."]

        # 3. --- LOGIKA PRZEJŚĆ (TRANSITIONS) ---
        if connections == 10: # POZIOMA
            if bg_up in trawa_warianty and bg_down in pustynia_warianty: return self.road_gfx["trans"]["poziom_trawa_gora_pustynia_dol"]
            if bg_up in pustynia_warianty and bg_down in trawa_warianty: return self.road_gfx["trans"]["poziom_pustynia_gora_trawa_dol"]
            if bg_left in pustynia_warianty and bg_right in trawa_warianty: return self.road_gfx["trans"]["poziom_pustynia_lewo_trawa_prawo"]
            if bg_left in trawa_warianty and bg_right in pustynia_warianty: return self.road_gfx["trans"]["poziom_trawa_lewo_pustynia_prawo"]

        elif connections == 5: # PIONOWA
            if bg_left in trawa_warianty and bg_right in pustynia_warianty: return self.road_gfx["trans"]["pion_trawa_lewo_pustynia_prawo"]
            if bg_left in pustynia_warianty and bg_right in trawa_warianty: return self.road_gfx["trans"]["pion_pustynia_lewo_trawa_prawo"]
            if bg_up in trawa_warianty and bg_down in pustynia_warianty: return self.road_gfx["trans"]["pion_trawa_gora_pustynia_dol"]
            if bg_up in pustynia_warianty and bg_down in trawa_warianty: return self.road_gfx["trans"]["pion_pustynia_gora_trawa_dol"]

        # 4. --- STANDARDOWA DROGA ---
        logical_terrain = "p" if bg_center in pustynia_warianty else "."
        if bg_center == "B" or bg_center == "b": logical_terrain = "B"

        terrain_dict = self.road_gfx.get(logical_terrain, self.road_gfx["."])
        return terrain_dict.get(connections, terrain_dict.get(10))
    
    def load_single_img(self, path, alpha=True):
        """Ładuje obrazek i ZAWSZE skaluje go do 32x32."""
        TARGET_SIZE = (32, 32)
        if os.path.exists(path):
            img = pygame.image.load(path)
            # Kluczowe: convert_alpha() zachowuje przezroczystość dla drzew/gór
            img = img.convert_alpha() if alpha else img.convert()
            return pygame.transform.scale(img, TARGET_SIZE)
        
        # Failsafe: różowy kwadrat
        s = pygame.Surface(TARGET_SIZE)
        s.fill((255, 0, 255))
        return s
    
    def load_road_graphics(self):
        self.road_gfx = {".": {}, "B": {}, "p": {}, "trans": {}}
        
        # PERFEKCYJNY SZABLON CLASH'A (N=1, E=2, S=4, W=8)
        road_template = {
            # Maska : Offset pliku (względem start_id)
            6: 0,   # Zakręt S-E (819)
            12: 1,  # Zakręt S-W (820)
            3: 2,   # Zakręt N-E (821)
            9: 3,   # Zakręt N-W (822)
            5: 4,   # Pionowa (823)
            10: 5,  # Pozioma (824)
            7: 6,   # T-Prawo (825)
            13: 7,  # T-Lewo (826)
            14: 9,  # T-Dół (827)
            11: 8,  # T-Góra (828)
            15: 10, # Skrzyżowanie X (829)
            1: 12,  # Koniec N (830)
            4: 11,  # Koniec S (831)
            2: 14,  # Koniec E (832)
            8: 13,  # Koniec W (833)
            0: 5    # Brak połączeń - awaryjnie wstawiamy poziomą drogę (offset 5)
        }

        # Wpisz tu poprawne numery startowe dla reszty terenów:
        terrain_starts = {
            ".": 819, # Start dla trawy
            "B": 834, # Start dla bagna (podmień na właściwy z Twojego folderu!)
            "p": 851  # Start dla pustyni (podmień na właściwy z Twojego folderu!)
        }

        path = os.path.join("assets", "BACKGR3_S32")

        # Ładujemy systematycznie wszystkie tereny
        for terrain, start_id in terrain_starts.items():
            for mask, offset in road_template.items():
                img_id = start_id + offset
                p = os.path.join(path, f"BACKGR3_S32_{img_id}.png")
                self.road_gfx[terrain][mask] = self.load_single_img(p)

        # Na koniec możesz tu załadować przejścia (trans), tak jak rozmawialiśmy wcześniej
        # 2. GRAFIKI PRZEJŚCIOWE (Transitions) Trawa <-> Pustynia (949 - 956)
        path = os.path.join("assets", "BACKGR3_S32")
        
        # A) Drogi idące RÓWNOLEGLE po granicy terenów
        self.road_gfx["trans"]["poziom_trawa_gora_pustynia_dol"] = self.load_single_img(os.path.join(path, "BACKGR3_S32_949.png"))
        self.road_gfx["trans"]["poziom_pustynia_gora_trawa_dol"] = self.load_single_img(os.path.join(path, "BACKGR3_S32_950.png"))
        self.road_gfx["trans"]["pion_trawa_lewo_pustynia_prawo"] = self.load_single_img(os.path.join(path, "BACKGR3_S32_951.png"))
        self.road_gfx["trans"]["pion_pustynia_lewo_trawa_prawo"] = self.load_single_img(os.path.join(path, "BACKGR3_S32_952.png"))

        # B) Drogi PRZECINAJĄCE granicę (wchodzące w drugi teren)
        self.road_gfx["trans"]["pion_trawa_gora_pustynia_dol"] = self.load_single_img(os.path.join(path, "BACKGR3_S32_953.png"))
        self.road_gfx["trans"]["pion_pustynia_gora_trawa_dol"] = self.load_single_img(os.path.join(path, "BACKGR3_S32_954.png"))
        self.road_gfx["trans"]["poziom_pustynia_lewo_trawa_prawo"] = self.load_single_img(os.path.join(path, "BACKGR3_S32_955.png"))
        self.road_gfx["trans"]["poziom_trawa_lewo_pustynia_prawo"] = self.load_single_img(os.path.join(path, "BACKGR3_S32_956.png"))
    
    def load_river_animation(self):

        """Ładuje klatki animacji rzeki (595-603)."""
        path_base = os.path.join("assets", "BACKGR3_S32")
        frames = []
        # Zakładamy 8-9 klatek animacji
        for i in range(595, 603):
            p = os.path.join(path_base, f"BACKGR3_S32_{i}.png")
            if os.path.exists(p):
                frames.append(self.load_single_img(p))
        
        # Jeśli nie znalazło plików, zwróć listę z jednym pustym Surface, żeby gra nie wywaliła błędu
        if not frames:
            print("OSTRZEŻENIE: Nie znaleziono klatek animacji rzeki (595-603)!")
            frames.append(pygame.Surface((TILE_SIZE, TILE_SIZE)))
            
        return frames   
             
    def load_sea_animation(self):
        """Ładuje klatki animacji ciemnego morza."""
        path_base = os.path.join("assets", "BACKGR3_S32")
        frames = []
        
        # UWAGA: Wpisz tutaj poprawne numery ID dla ciemnej wody z Clasha!
        # Ja strzelam, że to mogą być klatki np. od 604 do 612.
        for i in range(587, 595): 
            p = os.path.join(path_base, f"BACKGR3_S32_{i}.png")
            if os.path.exists(p):
                frames.append(self.load_single_img(p))
        
        # Failsafe: Jeśli nie znajdzie plików, stworzy ciemnoniebieski kwadrat
        if not frames:
            print("OSTRZEŻENIE: Nie znaleziono klatek animacji morza!")
            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            s.fill((0, 50, 150)) 
            frames.append(s)
            
        return frames

    def load_sea_cliffs(self):
        """Ładuje 8 klatek animacji dla każdego z 12 brzegów klifu (skok = 12)."""
        path_base = os.path.join("assets", "BACKGR3_S32")
        self.sea_cliffs_anim = {}
        
        # Standardowe mapowanie krawędzi Autotilingu (od 0 do 11) dopasowane do plików Clasha
        mapping = {
            1: 1, 6: 6, 3: 3, 4: 4,
            0: 0, 2: 2, 5: 5, 7: 7,
            11: 11, 10: 10, 9: 9, 8: 8
        }
        
        start_id = 223
        step = 12  # Twój potwierdzony krok!
        
        for edge_id, offset in mapping.items():
            frames = []
            for f in range(8):
                # Wyliczamy ID: np. dla lewego górnego (offset 0), klatka 2 to 223 + 0 + 12 = 235
                img_id = start_id + offset + (f * step)
                p = os.path.join(path_base, f"BACKGR3_S32_{img_id}.png")
                
                # Bezpiecznik: jeśli twórcy zapomnieli jakiejś klatki, gra użyje pierwszej (223+)
                if not os.path.exists(p):
                    fallback_id = start_id + offset
                    p = os.path.join(path_base, f"BACKGR3_S32_{fallback_id}.png")
                
                frames.append(self.load_single_img(p))
            
            self.sea_cliffs_anim[edge_id] = frames

    def load_all_water_assets(self):
        path_base = os.path.join("assets", "BACKGR3_S32")
        self.waterfall_gfx = {"N": {}, "S": {}, "W": {}, "E": {}}
        
        # ==========================================
        # WODOSPAD POŁUDNIOWY (S) - Twój oryginalny, poprawny układ!
        # ==========================================
        fragments_S = {
            "TOP_L": 419,
            "BOT_L": 416,
            "MID_L": 417,
            "MID_R": 418,
            "TOP_R": 420,
            "BOT_R": 415,
            "TOP_C": 421,
            "BOT_C": 422,
        }
        
        for name, start_id in fragments_S.items():
            self.waterfall_gfx["S"][name] = [
                self.load_single_img(os.path.join(path_base, f"BACKGR3_S32_{start_id + (f * 16)}.png")) 
                for f in range(8)
            ]
            
        # ==========================================
        # ŚRODKI WODOSPADÓW (MID_C) dla wszystkich 4 kierunków
        # ==========================================
        self.waterfall_gfx["N"]["MID_C"] = [self.load_single_img(os.path.join(path_base, f"BACKGR3_S32_{643 + f}.png")) for f in range(8)]
        self.waterfall_gfx["W"]["MID_C"] = [self.load_single_img(os.path.join(path_base, f"BACKGR3_S32_{667 + f}.png")) for f in range(8)]
        self.waterfall_gfx["E"]["MID_C"] = [self.load_single_img(os.path.join(path_base, f"BACKGR3_S32_{659 + f}.png")) for f in range(8)]
        
        # Uzupełniamy brakujący środek dla głównego wodospadu
        self.waterfall_gfx["S"]["MID_C"] = [self.load_single_img(os.path.join(path_base, f"BACKGR3_S32_{651 + f}.png")) for f in range(8)]

        # --- ZABEZPIECZENIE DLA INNYCH KIERUNKÓW ---
        for kier in ["N", "W", "E"]:
            for seg in ["TOP", "BOT"]:
                self.waterfall_gfx[kier][f"{seg}_C"] = self.waterfall_gfx[kier]["MID_C"]
            for seg in ["TOP", "MID", "BOT"]:
                self.waterfall_gfx[kier][f"{seg}_L"] = self.waterfall_gfx[kier]["MID_C"]
                self.waterfall_gfx[kier][f"{seg}_R"] = self.waterfall_gfx[kier]["MID_C"]

        # ==========================================
        # 5. NAKŁADKI NA RZEKĘ (Płaskie brzegi lądu wchodzące na wodę 'W')
        # ==========================================
        overlay_starts = {
            ".": 563,  # Trawa
            "l": 563,  # Las (używa identycznych brzegów co trawa!) <--- DODAJ TO
            "p": 543,  # Pustynia
            "P": 543,  # Wydmy (korzystają z brzegów pustyni)
            "B": 575,  # Bagno
            "b": 575,  # Płytkie bagno
            "g": 575,  # Niskie góry (zaczynają się od 585!)
            "G": 575   # Wysokie góry
        }

        self.river_overlays = {}
        for terrain_type, start_id in overlay_starts.items():
            # Ładujemy ciągiem 12 kafelków dla każdego terenu
            self.river_overlays[terrain_type] = [
                self.load_single_img(os.path.join(path_base, f"BACKGR3_S32_{start_id + i}.png"))
                for i in range(12)
            ]
        self.bridge_gfx = {
            "H_L": self.load_single_img(os.path.join(path_base, "BACKGR3_S32_877.png")),
            "H_C": self.load_single_img(os.path.join(path_base, "BACKGR3_S32_878.png")),
            "H_R": self.load_single_img(os.path.join(path_base, "BACKGR3_S32_879.png")),
            "V_T": self.load_single_img(os.path.join(path_base, "BACKGR3_S32_880.png")),
            "V_C": self.load_single_img(os.path.join(path_base, "BACKGR3_S32_881.png")),
            "V_B": self.load_single_img(os.path.join(path_base, "BACKGR3_S32_882.png"))
        }
    
    def get_waterfall_context(self, x, y):
        # Sprawdzamy sąsiadów, żeby określić jak narysowałeś wodospad na mapie
        v_up = self.get_bg_tile_at(x, y-1) == "V"
        v_down = self.get_bg_tile_at(x, y+1) == "V"
        v_left = self.get_bg_tile_at(x-1, y) == "V"
        v_right = self.get_bg_tile_at(x+1, y) == "V"

        # 1. WODOSPAD POZIOMY (np. 3 kafelki szerokości, ułożone wschód-zachód)
        # Zgodnie z Twoją regułą: Zawsze krawędzie na bokach. Środek gdy dłuższy.
        if v_left or v_right:
            if not v_left: return "S", "TOP_L"  # Lewy klif (415)
            if not v_right: return "S", "TOP_R" # Prawy klif (419)
            return "W", "MID_C"                 # Środek klifu (667)

        # 2. WODOSPAD PIONOWY (ułożony północ-południe)
        # Zgodnie z Twoją regułą: Zawsze góra i rozbryzg. Środek (651) gdy dłuższy.
        if v_up or v_down:
            if not v_up: return "S", "TOP_C"    # Początek spadku wody (421)
            if not v_down: return "S", "BOT_C"  # Rozbryzg na dole (422)
            return "S", "MID_C"                 # Czysta lecąca woda (Twoje 651)

        # Zabezpieczenie dla pojedynczego kafelka 'V' na mapie
        return "S", "TOP_C"
    
    def is_tile_passable(self, x, y, unit_type):
        tile = self.map[y][x]
        if tile == "W":
            return unit_type == "ship" # Tylko statki
        if tile == "V":
            return False # Wodospad blokuje wszystkich (chyba że masz latające jednostki)
        return True

    def get_river_direction(self, x, y):
        # Sprawdzamy, z której strony jest najbliższy ląd
        if y > 0 and self.map[y-1][x] in [".", "p", "B"]: return "UP"
        if x > 0 and self.map[y][x-1] in [".", "p", "B"]: return "LEFT"
        if x < len(self.map[0])-1 and self.map[y][x+1] in [".", "p", "B"]: return "RIGHT"
        if y < len(self.map)-1 and self.map[y+1][x] in [".", "p", "B"]: return "DOWN"
        return "UP" # Domyślny, jeśli coś pójdzie nie tak
                        
    def draw_water_tile(self, screen, x, y, pos, tile_type):
        t = pygame.time.get_ticks()
        
        # --- WARSTWA 1: BAZA (Woda lub Morze) ---
        if tile_type == "M" and hasattr(self, 'sea_anim') and self.sea_anim:
            f_sea = (t // 200) % len(self.sea_anim)
            screen.blit(self.sea_anim[f_sea], pos)
        elif hasattr(self, 'river_anim') and self.river_anim:
            f_riv = (t // 200) % len(self.river_anim)
            screen.blit(self.river_anim[f_riv], pos)

        # --- WARSTWA 2A: KLIFY MORSKIE (Tylko dla Morza 'M') ---
        if tile_type == "M" and hasattr(self, 'sea_cliffs_anim'):
            # Morze używa tego samego skanera co góry i pustynie!
            edge_id = self.get_tile_connection_id(x, y, "M")
            if edge_id != 12: # Jeśli nie jest to środek oceanu (czyli dotyka lądu)
                frames = self.sea_cliffs_anim.get(edge_id)
                if frames and len(frames) > 0:
                    idx = (t // 200) % len(frames)
                    screen.blit(frames[idx], pos)

        # --- WARSTWA 2B: PŁASKIE BRZEGI RZEKI (Tylko dla Rzeki 'W') ---
        elif tile_type == "W":
            # Używamy naszego perfekcyjnego skanera terenu!
            edge_id = self.get_tile_connection_id(x, y, "W") 
            
            # Jeśli edge_id to 12, to znaczy że rzeka jest otoczona wodą (środek)
            if edge_id != 12:
                # Sprawdzamy, z jakim twardym lądem sąsiadujemy
                neighbor_land = self.get_dominant_land_neighbor(x, y, "W") 
                
                # Pobieramy zestaw nakładek i rysujemy odpowiedni kafel!
                if neighbor_land in self.river_overlays:
                    overlay_img = self.river_overlays[neighbor_land][edge_id]
                    screen.blit(overlay_img, pos)

        # --- WARSTWA 3: MOST (Rysujemy, jeśli na mapie obiektów jest droga) ---
        if self.get_tile_at(x, y) == "_":
            bridge_part_key = self.get_bridge_tile(x, y)
            if hasattr(self, 'bridge_gfx'):
                bridge_img = self.bridge_gfx.get(bridge_part_key)
                if bridge_img:
                    screen.blit(bridge_img, pos)

   
    def get_bridge_tile(self, x, y):
        """Ustala, czy narysować rampę (zjazd), czy środek mostu."""
        
        def is_bridge(nx, ny):
            has_road = self.get_tile_at(nx, ny) == "_"
            has_water = self.get_bg_tile_at(nx, ny) in ["W", "V"]
            return has_road and has_water

        bridge_up = is_bridge(x, y-1)
        bridge_down = is_bridge(x, y+1)
        bridge_left = is_bridge(x-1, y)
        bridge_right = is_bridge(x+1, y)

        road_up = self.get_tile_at(x, y-1) == "_"
        road_down = self.get_tile_at(x, y+1) == "_"
        road_left = self.get_tile_at(x-1, y) == "_"
        road_right = self.get_tile_at(x+1, y)

        # LOGIKA PIONOWA
        if road_up or road_down:
            if road_up and not bridge_up: return "V_T"     # Ląd na górze -> Górna rampa
            if road_down and not bridge_down: return "V_B" # Ląd na dole -> Dolna rampa
            return "V_C"

        # LOGIKA POZIOMA
        if road_left or road_right:
            if road_left and not bridge_left: return "H_L"   # Ląd z lewej -> Lewa rampa
            if road_right and not bridge_right: return "H_R" # Ląd z prawej -> Prawa rampa
            return "H_C"

        return "H_C"
    
    def get_dominant_land_neighbor(self, x, y, tile_type):
        priority = ["B", "b", "p", "P", "s", "l", ".", "g", "G"] 
        for terrain in priority:
            if tile_type == terrain: continue
            # ZMIANA: Skanujemy 8 kierunków (dodane skosy: -1,-1 itd.)
            for dx, dy in [(0,-1), (0,1), (-1,0), (1,0), (-1,-1), (1,-1), (-1,1), (1,1)]:
                if self.get_bg_tile_at(x + dx, y + dy) == terrain:
                    return terrain
        return "."

    def load_castle_and_tower(self):
        # ==================================================================
        #           ŁADOWANIE ANIMACJI ZAMKU (SKALOWANE DO 32x32)
        # ==================================================================
        base_path = r"D:\clash reverse\assets\zamekczerwony\BUILDIN1_S32_"
        TARGET_SIZE = (32, 32)
        
        # --- GRAFIKI ZAMKU (2x2) ---
        self.castle_tiles = {0: [], 1: [], 2: [], 3: [], 4: []}
        for stage in range(4):
            for i in range(4):
                file_num = 225 + (stage * 4) + i
                try:
                    img = pygame.image.load(f"{base_path}{file_num}.png").convert_alpha()
                    # KLUCZOWA POPRAWKA: Skalujemy każdy fragment do 32x32
                    img = pygame.transform.scale(img, TARGET_SIZE)
                    self.castle_tiles[stage].append(img)
                except:
                    print(f"Brak pliku zamku: {file_num}")

        # Zniszczony zamek (257-260)
        for i in range(4):
            try:
                img = pygame.image.load(f"{base_path}{257 + i}.png").convert_alpha()
                img = pygame.transform.scale(img, TARGET_SIZE)
                self.castle_tiles[4].append(img)
            except: pass

        # --- GRAFIKI STRAŻNICY (1x1) ---
        self.tower_tiles = {}
        for i in range(4): 
            try:
                img = pygame.image.load(f"{base_path}{i}.png").convert_alpha()
                # Strażnica też musi mieć 32x32, żeby pasowała do siatki
                self.tower_tiles[i] = pygame.transform.scale(img, TARGET_SIZE)
            except:
                print(f"Brak pliku strażnicy: {i}")
        
        # Zniszczona strażnica (plik nr 8)
        try:
            img = pygame.image.load(f"{base_path}8.png").convert_alpha()
            self.tower_tiles[4] = pygame.transform.scale(img, TARGET_SIZE)
        except:
            print("Brak pliku zniszczonej strażnicy (8.png)")
    def update(self):
        # --- ANIMACJA WODY ---
        # Zwiększamy licznik. 0.1 to spokojna fala, 0.3 to wzburzone morze.
        self.water_frame_index += 0.1 
        
        # Zapętlamy licznik, żeby nie urósł do gigantycznych liczb (pamięć!)
        # 200 to bezpieczny limit, bo masz około tyle klatek łącznie.
        if self.water_frame_index >= 200:
            self.water_frame_index = 0

        # --- TWOJA LOGIKA RUCHU KAMERY ---
        keys = pygame.key.get_pressed()
        moving = False
        speed = 8  

        if keys[pygame.K_LEFT]:
            self.camera_x -= speed
            moving = True
        if keys[pygame.K_RIGHT]:
            self.camera_x += speed
            moving = True
        if keys[pygame.K_UP]:
            self.camera_y -= speed
            moving = True
        if keys[pygame.K_DOWN]:
            self.camera_y += speed
            moving = True

        # DOCIĄGANIE (Snapping)
        if not moving:
            self.camera_x = round(self.camera_x / 32) * 32 
            self.camera_y = round(self.camera_y / 32) * 32

    def load_map(self, filename):
        game_map = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    clean_line = line.replace('\n', '').replace('\r', '')
                    if len(clean_line) > 0:
                        # KLUCZOWE: Wyrównujemy do 100 znaków! Chroni przed uciętymi spacjami.
                        clean_line = clean_line.ljust(MAP_WIDTH, ' ')
                        game_map.append(list(clean_line))
            return game_map
        except Exception as e:
            print(f"Błąd ładowania mapy {filename}: {e}")
            return []
        
    def load(self, map_base_name, fac_file):
        # 1. Ładujemy obie warstwy mapy! (Nazwy generowane automatycznie)
        self.bg_map = self.load_map(f"{map_base_name}_terrain.txt")
        self.map = self.load_map(f"{map_base_name}_objects.txt")

        # 2. Reszta Twojej logiki z pliku FAC (zostaje bez zmian)
        self.objects = load_fac_objects(fac_file)

        castle_places = self.objects.get("zamek_place", [])
        built_indices = self.objects.get("zbudowano_zamek", [0, 1])

        self.castles = []
        self.castle_locations = []

        for i, (x, y) in enumerate(castle_places):
            if i in built_indices:
                owner_id = built_indices[i] 
                if owner_id < len(self.players):
                    c = Castle(x, y, self.players[owner_id]) 
                    c.gold = 20000
                    self.castles.append(c)
                else:
                    self.castle_locations.append((x, y))

        for c in self.castles:
            if c.owner:
                owner_obj = self.players[c.owner] if isinstance(c.owner, int) else c.owner
                self.add_unit(Unit("lekka piechota", c.x, c.y + 2, owner_obj))

        print(f"Zbudowano zamków: {len(self.castles)}")
        print(f"Miejsc pod budowę: {len(self.castle_locations)}")

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

        # 4. TEREN
        walkable_chars = [".", "l", "p", "#", "$", "_", "g"]
        if self.map[ny][nx] not in walkable_chars:
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
        unit_type = self.selected_recruit_unit

        cost = Unit.UNIT_COSTS.get(unit_type, 0)

        if player.gold < cost:
            print("Za mało złota")
            return

        player.gold -= cost

        u = Unit(
            unit_type,
            self.selected_castle.x,
            self.selected_castle.y,
            player
        )

        self.selected_castle.add_to_garrison(u)
        print(f"Zrekrutowano {unit_type}")

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

    def train_selected(self, castle):
        for unit in self.selected_units:
            castle.start_training(unit)

        self.clear_selection()

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

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit(); import sys; sys.exit()
            
            # --- 1. KLAWIATURA ---
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # SZYBKI POWRÓT (ESC)
                    if self.screen in ["recruitment", "garrison", "forge", "workshop", "hospital", "school", "peasants", "court"]:
                        self.screen = "castle"
                        self.inspected_unit = None # Czyścimy podgląd przy wyjściu
                    elif self.screen == "castle":
                        self.screen = "map"
                    elif getattr(self, 'demolish_confirm', False):
                        self.demolish_confirm = False

                elif event.key == pygame.K_SPACE:
                    if self.selected_unit:
                        self.selected_unit = None
                    else:
                        self.next_turn()

                elif event.key == pygame.K_g:
                    if self.screen == "map":
                        self.show_grid = not self.show_grid
                        print(f"Siatka: {self.show_grid}")
                elif event.key == pygame.K_b:
                    # Dodaj tę flagę w __init__: self.show_only_biome = False
                    self.show_only_biome = not getattr(self, 'show_only_biome', False)
                    print(f"Widok samej mapy biomów: {self.show_only_biome}")

            # --- 3. WCIŚNIĘCIE MYSZY ---
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                
                if event.button == 3: # Prawy przycisk
                    self.inspected_unit = None # Czyścimy poprzedni podgląd przed szukaniem nowego
                    
                    if self.screen == "garrison":
                        self.check_unit_info(mx, my)
                    
                    elif self.screen == "map":
                        # 1. Dolny pasek
                        if my >= 610 and hasattr(self, 'army_slot_rects'):
                            u = self.selected_unit
                            if u:
                                garrison = [u] + getattr(u, 'garrison', [])
                                display_units = [unit for unit in garrison if unit is not None]
                                for i, rect in enumerate(self.army_slot_rects):
                                    if rect.collidepoint(mx, my) and i < len(display_units):
                                        self.inspected_unit = display_units[i]
                                        break
                        
                        # 2. Mapa (tylko jeśli nie znaleźliśmy nic na pasku)
                        if not self.inspected_unit:
                            self.inspected_unit = self.get_unit_at_pixel(mx, my)

                # Wykonanie standardowej logiki (zaznaczanie/ruch)
                self.handle_mouse_click(mx, my, event.button)
            # --- 4. PUSZCZENIE MYSZY (HOLD END) ---
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    # Puszczasz przycisk - statystyki znikają
                    self.inspected_unit = None

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
    
    def handle_mouse_click(self, mx, my, button):
        if button != 1 and button != 3: return 

        # 1. PRIORYTET: Ekrany specjalne
        if self.screen == "trap_info":
            self.handle_trap_info_click(mx, my)
            return
        
        if self.screen == "unit_info":
            self.screen = "recruitment"
            return
        if self.screen == "court":
            # Sprawdzamy specjalny przycisk Dworu
            if hasattr(self, 'court_back_button') and self.court_back_button.collidepoint(mx, my):
                self.screen = "castle"
                return
            # Tutaj opcjonalnie wywołanie specyficznej logiki dworu
            self.handle_court_click(mx, my) 
            return
        # 2. EKRAN MAPY
        if self.screen == "map":
            if self.handle_ui_click(mx, my): return 
            self.handle_map_logic_combined(mx, my, button)
            return

        # 3. OBSŁUGA PRZYCISKU POWRÓT (Poprawiona)
        back_rect = pygame.Rect(650, 530, 120, 40) if self.screen == "court" else self.back_button
        
        if back_rect.collidepoint(mx, my):
            # A. Jeśli jesteśmy w REKRUTACJI -> zawsze wracamy do GARNIZONU
            if self.screen == "recruitment":
                self.screen = "garrison"
            
            # B. Jeśli jesteśmy w GARNIZONIE -> wybór zależy od typu budynku
            elif self.screen == "garrison":
                if self.selected_castle and self.selected_castle.building_type == "Strażnica":
                    self.screen = "map" # Strażnica nie ma menu głównego
                    self.selected_castle = None
                else:
                    self.screen = "castle" # Zamek ma menu główne
            
            # C. Jeśli jesteśmy w menu GŁÓWNYM Zamku -> wracamy na MAPĘ
            elif self.screen == "castle":
                self.screen = "map"
                self.selected_castle = None

            # D. Jeśli jesteśmy w budynkach rzemieślniczych -> ZAWSZE do menu GŁÓWNEGO Zamku
            elif self.screen in ["forge", "hospital", "school", "peasants", "workshop", "court"]:
                self.screen = "castle"
            
            self.selected_units.clear()
            return

        # 4. LOGIKA GŁÓWNEGO MENU ZAMKU / STRAŻNICY
        if self.screen == "castle":
            if self.selected_castle and self.selected_castle.building_type == "Strażnica":
                if hasattr(self, 'garrison_button') and self.garrison_button.collidepoint(mx, my):
                    self.screen = "garrison"
                return 
            
            self.handle_castle_main_click(mx, my)
            return

        # 5. LOGIKA POD-EKRANÓW (Tylko te, które mają PRAWDZIWĄ mechanikę)
        if self.screen == "recruitment":
            self.handle_recruitment_click(mx, my)
            return
        
        elif self.screen == "garrison":
            # Sprawdzamy, czy to Rect ZANIM wywołamy collidepoint
            is_release = False
            if hasattr(self, 'release_tower') and isinstance(self.release_tower, pygame.Rect):
                if self.release_tower.collidepoint(mx, my):
                    is_release = True
            if is_release:
                print("Akcja: Wypuszczanie zaznaczonych jednostek na mapę")
                self.release_selected_units()
                return

            # 2. Przycisk ZBURZ / ZNISZCZ (Tylko dla Strażnicy)
            if hasattr(self, 'destroy_button') and self.destroy_button.collidepoint(mx, my):
                if self.selected_castle and self.selected_castle.building_type == "Strażnica":
                    print("Akcja: Burzenie Strażnicy")
                    self.destroy_straznica(self.selected_castle)
                    return

            # 3. Jeśli nie przyciski akcji, to sprawdzamy kliknięcie w kafelki jednostek
            self.handle_garrison_click(mx, my, button)
            return

        # 6. BLOKADA DLA RESZTY (Forge, Hospital, School, Workshop, Court, Peasants)
        # Skoro mają tylko tekst i powrót (który obsłużyliśmy wyżej), 
        # po prostu blokujemy kliknięcia, żeby nie "przebijały" na mapę.
        info_screens = ["forge", "hospital", "school", "workshop", "peasants", "court"]
        if self.screen in info_screens:
            return
                
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

        # 3. Standardowa obsługa (Ruch i zaznaczanie) - Twoja zunifikowana funkcja
        self.handle_map_click(mx, my, button)

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

    def handle_castle_main_click(self, mx, my):
        # obsługa menu zamku
        # A. Potwierdzenie zburzenia
        if getattr(self, 'demolish_confirm', False):
            win_w, win_h = 320, 160
            win_x, win_y = (1024//2)-(win_w//2), (768//2)-(win_h//2)
            btn_yes = pygame.Rect(win_x + 40, win_y + 85, 90, 45)
            btn_no = pygame.Rect(win_x + 190, win_y + 85, 90, 45)

            if btn_yes.collidepoint(mx, my):
                self.demolish_castle(self.selected_castle)
                self.screen = "map"; self.selected_castle = None; self.demolish_confirm = False
            elif btn_no.collidepoint(mx, my):
                self.demolish_confirm = False
            return

        # B. Główne menu zamku (ZBURZ, MURY)
        if getattr(self, 'menu_open', False):
            if self.menu_button.collidepoint(mx, my):
                self.menu_open = False
                return
            for opt_name, rect in self.menu_rects.items():
                if rect.collidepoint(mx, my):
                    if opt_name == "ZBURZ ZAMEK":
                        self.demolish_confirm = True
                        self.menu_open = False
                    return

        # C. Przyciski budynków (Recruitment, Forge itd.)
        for b in ['forge', 'workshop', 'hospital', 'school', 'court', 'peasants']:
            btn = getattr(self, f'{b}_button', None)
            if btn and btn.collidepoint(mx, my):
                self.screen = b
                return

        if getattr(self, 'recruit_button', None) and self.recruit_button.collidepoint(mx, my):
            self.selected_patent_index = None
            self.screen = "recruitment"
            return

        # D. Kliknięcie w grafikę zamku (ostatnia szansa)
        self.handle_castle_click(mx, my)

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
        if ("Koszary" in castle.buildings
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
    def calculate_army_power(self, player):
        power = 0
        for u in player.units:
            power += u.attack + u.defense + u.experience
        return power
    
    def calculate_gold(self, player):
        return sum(castle.gold for castle in player.castles)

    def draw_garrison(self, screen):
        castle = self.selected_castle 
        if not castle: 
            return
    
        start_x = 100
        start_y = 120
        cols = 6
        rows = 2
        slot_w = 100
        slot_h = 180
        offset_x = 130
        offset_y = 210

        font = pygame.font.SysFont(None, 20)
        t_font = pygame.font.SysFont("Arial", 22, bold=True) # Czcionka do tur

        for row in range(rows):
            for col in range(cols):
                index = row * cols + col
                
                # Pobieramy to, co siedzi w szufladce
                unit = None
                if index < len(castle.garrison):
                    unit = castle.garrison[index] # Może tu być Pikinier albo None

                x = start_x + col * offset_x
                y = start_y + row * offset_y
                rect = pygame.Rect(x, y, slot_w, slot_h)

                # 1. Rysujemy ramkę ZAWSZE (szara dla pustych, żółta dla wybranych)
                color = (255, 255, 0) if unit and unit in self.selected_units else (200, 200, 200)
                pygame.draw.rect(screen, color, rect, 2)

                # 2. Rysujemy jednostkę TYLKO jeśli slot NIE JEST None
                if unit is not None:
                    # Niebieski kwadrat pikiniera
                    pygame.draw.rect(screen, (80, 120, 200), (x + 20, y + 20, 60, 60))
                    
                    # Tekst (np. PIK)
                    text = font.render(unit.type[:3].upper(), True, (255,255,255))
                    screen.blit(text, (x + 35, y + 90))

                    # 3. STATUS SZKOLENIA (Overlay)
                    if unit in castle.training:
                        # Overlay musi mieć rozmiar taki sam jak ramka (slot_w, slot_h)
                        overlay = pygame.Surface((slot_w, slot_h), pygame.SRCALPHA)
                        overlay.fill((0, 0, 0, 160)) 
                        screen.blit(overlay, (x, y)) # Rysujemy dokładnie na pozycji ramki

                        # Miecze (ikona) na środku tego konkretnego slotu
                        if self.icon_training:
                            icon_x = rect.centerx - self.icon_training.get_width() // 2
                            icon_y = rect.centery - self.icon_training.get_height() // 2
                            screen.blit(self.icon_training, (icon_x, icon_y))
                            
                            # Licznik tur pod mieczami
                            tury_left = castle.training[unit]
                            text_surf = t_font.render(str(tury_left), True, (255, 255, 0))
                            screen.blit(text_surf, (icon_x + 15, icon_y + 40))

        # --- PRZYCISKI NA DOLE (Rysujemy raz poza pętlą) ---
        # Przyciski funkcyjne (Tylko jeśli budynek istnieje)
        if "Koszary" in castle.buildings:
            self.draw_button(screen, "RECRUIT", self.recruit_button, (240, 120, 20))
        if "hospital" in castle.buildings:
            self.draw_button(screen, "HEAL", self.heal_button, (80, 160, 80))
        if "school" in castle.buildings:
            self.draw_button(screen, "TRAIN", self.train_button, (160, 160, 80))
        
        self.draw_building_footer(screen) # Rysuje BACK i RELEASE w stałych miejscach

    def draw_map(self, screen):
        tiles_on_screen_x = SCREEN_WIDTH // TILE_SIZE + 1
        tiles_on_screen_y = SCREEN_HEIGHT // TILE_SIZE + 1
        start_x = max(0, self.camera_x // TILE_SIZE)
        start_y = max(0, self.camera_y // TILE_SIZE)
        end_x = min(len(self.map[0]), start_x + tiles_on_screen_x)
        end_y = min(len(self.map), start_y + tiles_on_screen_y)

        current_time = pygame.time.get_ticks()

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                pos = ((x * TILE_SIZE) - self.camera_x, (y * TILE_SIZE) - self.camera_y)
                
                # POBIERAMY ZNAKI Z OBU WARSTW!
                bg_tile = self.get_bg_tile_at(x, y) # NATURA
                obj_tile = self.get_tile_at(x, y)   # CYWILIZACJA

                # --- TRYB DEBUGOWANIA (Widok samego biomu) ---
                if getattr(self, 'show_only_biome', False):
                    if bg_tile in ["p", "P", "s"]: 
                        screen.blit(self.centers["p"][0], pos)
                    elif bg_tile in ["B", "b"]: 
                        screen.blit(self.centers["B"][0], pos)
                    elif bg_tile == "W": 
                        screen.blit(self.river_anim[0], pos)
                    elif bg_tile == "M": # <--- PODGLĄD DLA MORZA
                        screen.blit(self.sea_anim[0], pos)
                    elif bg_tile in ["G", "g"]: 
                        # Używamy środka gór
                        screen.blit(self.centers["g"][0], pos) 
                    elif bg_tile == "l": 
                        # Używamy gęstego lasu
                        screen.blit(self.centers["l"][0], pos)
                    else: 
                        screen.blit(self.grass_variants[0], pos)
                    continue 

                # ==========================================
                # WARSTWA 1: TŁO (Biom z bg_map)
                # ==========================================
                # --- ZMIANA TUTAJ ---
                if bg_tile in ["W", "M"]:
                    self.draw_water_tile(screen, x, y, pos, bg_tile)
                # --------------------
                elif bg_tile == "V":
                    # --- KLUCZOWA POPRAWKA WODOSPADU ---
                    kier, full_key = self.get_waterfall_context(x, y)
                    if kier in self.waterfall_gfx and full_key in self.waterfall_gfx[kier]:
                        wf_frames = self.waterfall_gfx[kier][full_key]
                        
                        # Zabezpieczenie przed pustą listą klatek
                        if wf_frames and len(wf_frames) > 0:
                            wf_idx = (current_time // 160) % len(wf_frames)
                            screen.blit(wf_frames[wf_idx], pos)
                else:
                    # 1. Absolutne tło (żeby nie było czarnych dziur)
                    screen.blit(self.grass_variants[0], pos)

                    # 2. Autotiling Trawy
                    grass_edge_id = self.get_tile_connection_id(x, y, ".")
                    grass_full_set = self.edges["."].copy()
                    grass_full_set[12] = self.centers.get(".", self.grass_variants)
                    self.draw_custom_overlay(screen, x, y, pos, grass_full_set, grass_edge_id)

                    # 3. Nakładanie reszty (Pustynia, Bagno, Góry, Las)
                    if bg_tile in self.edges and bg_tile != ".":
                        edge_id = self.get_tile_connection_id(x, y, bg_tile)
                        
                        # --- SPECJALNA LOGIKA DLA GÓR ---
                        if bg_tile in ["g", "G"]:
                            if bg_tile == "G":
                                swamp_set = getattr(self, 'high_mountain_swamp_edges', self.mountain_grass_edges)
                                desert_set = getattr(self, 'high_mountain_desert_edges', self.mountain_grass_edges)
                                grass_set = getattr(self, 'high_mountain_grass_edges', self.mountain_grass_edges)
                            else:
                                swamp_set = getattr(self, 'mountain_swamp_edges', self.mountain_grass_edges)
                                desert_set = getattr(self, 'mountain_desert_edges', self.mountain_grass_edges)
                                grass_set = getattr(self, 'mountain_grass_edges', self.edges["g"])

                            # ZMIANA: Szukamy, jakiego terenu dotyka góra!
                            neighbor = self.get_dominant_land_neighbor(x, y, bg_tile)

                            # Wybieramy zestaw brzegów na podstawie sąsiada
                            if neighbor in ["B", "b"]: 
                                current_set = swamp_set.copy()
                            elif neighbor in ["p", "P", "s"]: 
                                current_set = desert_set.copy()
                            else: 
                                current_set = grass_set.copy()

                            # Zabezpieczenie na wypadek, gdyby środek był listą
                            center_img = self.centers.get(bg_tile)
                            if center_img:
                                current_set[12] = center_img
                                
                            self.draw_custom_overlay(screen, x, y, pos, current_set, edge_id)
                        
                        else:
                            # Standardowy teren (Las, Bagno, Pustynia)
                            full_set = self.edges[bg_tile].copy()
                            full_set[12] = self.centers.get(bg_tile, self.grass_variants)
                            self.draw_custom_overlay(screen, x, y, pos, full_set, edge_id)

                # ==========================================
                # WARSTWA 2: OBIEKTY (z map_objects)
                # ==========================================
                if obj_tile == " ":
                    continue # Nic nie ma, idziemy dalej
                
                if obj_tile == "_":
                    # --- KLUCZOWA ZMIANA ---
                    # Rysujemy zwykłą drogę TYLKO jeśli pod spodem NIE MA rzeki.
                    # Jeśli jest rzeka, most został już narysowany w draw_water_tile!
                    if bg_tile != "W":
                        road_img = self.get_road_tile(x, y)
                        if road_img: screen.blit(road_img, pos)
                    
                elif obj_tile in ["S", "&", "R"]:
                    if obj_tile == "S": screen.blit(self.temple_img, pos) 
                    elif obj_tile == "&": screen.blit(self.temple2_img, pos) 
                    elif obj_tile == "R": 
                        if hasattr(self, 'ruins_img'): screen.blit(self.ruins_img, pos)

                elif obj_tile == "$":
                    logical_bg = "p" if bg_tile in ["p", "P", "s"] else "."
                    img = self.treasure_imgs.get(logical_bg, self.treasure_imgs["."])
                    screen.blit(img, pos)

        # --- KONIEC PĘTLI KAFELKÓW ---
        random.seed()

        for castle in self.castles:
            self.draw_castle_on_map(screen, castle)

            #else:
                            # Jeśli to samotny las (ID 0), a masz przygotowaną listę samotników:
                          #  if tile_type == "l" and edge_id == 0:
                          #      random.seed(x * 1000 + y)
                          #      img = random.choice(self.lonely_trees) # Lista Twoich samotnych drzew
                          #  else:
                          #      img = self.edges[tile_type].get(edge_id)
                            
                          #  if img: screen.blit(img, pos)

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
                    found_tile = self.get_bg_tile_at(x + dx, y + dy)
                else:
                    found_tile = self.get_tile_at(x + dx, y + dy)
                    
                if found_tile == search_type:
                    return True
        return False
    
    def check_collision(self, x, y):
        tile = self.map[y][x]
        if tile == "W" or tile == "V":
            return True # Jest kolizja (woda/wodospad blokuje ruch lądowy)
        return False
    
    def draw_castle(self, screen, castle):
        """Ta funkcja rysuje tylko OBIEKT na mapie świata."""
        # Obliczamy pozycję na ekranie względem kamery
        px = castle.x * TILE_SIZE - self.camera_x
        py = castle.y * TILE_SIZE - self.camera_y
        
        # Wybieramy obrazek (np. stan zniszczenia)
        s_idx = 3 # domyślny stan 'gotowy'
        if getattr(castle, 'destroyed', False): s_idx = 4
        
        # Rysujemy
        tiles = self.castle_tiles.get(s_idx, [])
        if len(tiles) == 4:
            offsets = [(0,0), (1,0), (0,1), (1,1)]
            for i in range(4):
                dx, dy = offsets[i]
                screen.blit(tiles[i], (px + dx*TILE_SIZE, py + dy*TILE_SIZE))
            
    def draw_castle_interface(self, screen): # Usunąłem parametr castle, bo bierzesz go z self
        
        castle = self.selected_castle
        if not castle: 
            return
        
        # NOWE: grafika tła zamku
        self.castle_gfx.draw(screen, castle)

        # 1. Specjalny widok dla Strażnicy
        if castle.building_type == "Strażnica":
            # Upewnij się, że ta funkcja nie nazywa się tak samo jak inna!
            self.draw_garrison_only(screen) 
            return

       

        # 3. PRZYCISKI W TWOICH ORYGINALNYCH MIEJSCACH
        
        # DWÓR - Środek góra
        self.court_button = pygame.Rect(420, 100, 160, 40)
        self.draw_button(screen, "DWÓR", self.court_button, (20, 80, 80))

        # GARNIZON - Nad powrotem (lewy dół, ale nieco wyżej)
        self.garrison_button = pygame.Rect(80, 630, 160, 40)
        self.draw_button(screen, "GARNIZON", self.garrison_button, (80, 80, 160))

        # CHŁOPI - Prawy dół (tylko w Zamku)
        if castle.building_type == "Zamek":
            self.peasant_button = pygame.Rect(screen.get_width() - 200, screen.get_height() - 110, 160, 40)
            self.draw_button(screen, "CHŁOPI", self.peasant_button, (160, 140, 60))

        # 4. BUDYNKI (Forge, Workshop itd.) - Ich stare pozycje
        if "forge" in castle.buildings:
            self.forge_button = pygame.Rect(750, 500, 160, 40)
            self.draw_button(screen, "KUŹNIA", self.forge_button, (100, 100, 100))
        
        if "workshop" in castle.buildings:
            self.workshop_button = pygame.Rect(290, 480, 160, 40)
            self.draw_button(screen, "WARSZTAT", self.workshop_button, (90, 90, 140))
            
        if "hospital" in castle.buildings:
            self.hospital_button = pygame.Rect(110, 350, 160, 40)
            self.draw_button(screen, "SZPITAL", self.hospital_button, (200, 60, 60))
            
        if "school" in castle.buildings:
            self.school_button = pygame.Rect(830, 250, 160, 40)
            self.draw_button(screen, "SZKOŁA", self.school_button, (90, 90, 240))

        # 5. SYSTEM MENU (Prawy dół/środek)
        mx, my = pygame.mouse.get_pos()
        
        # Hover na główny przycisk MENU otwiera je
        if self.menu_button.collidepoint(mx, my):
            self.menu_open = True

        # Logika zamykania menu (naprawiona)
        mouse_over_ui = False
        if self.menu_button.collidepoint(mx, my): mouse_over_ui = True
        
        if getattr(self, 'menu_open', False):
            self.draw_castle_menu(screen, mx, my)
            # Sprawdzamy czy mysz jest nad opcjami menu
            for rect in self.menu_rects.values():
                if rect.collidepoint(mx, my): mouse_over_ui = True
            for rect in self.build_rects.values():
                if rect.collidepoint(mx, my): mouse_over_ui = True
            
            # Twój mostek bezpieczeństwa
            bridge_rect = pygame.Rect(self.menu_button.x - 20, self.menu_button.y, 30, 200)
            if bridge_rect.collidepoint(mx, my): mouse_over_ui = True

        if not mouse_over_ui:
            self.menu_open = False
            self.build_open = False

        self.draw_button(screen, "MENU", self.menu_button)

        # 6. FOOTER (BACK na samym dole)
        self.draw_building_footer(screen)
    
    def draw_unit(self, screen, u):
        """Rysuje jednostkę na mapie świata z uwzględnieniem kamery."""
        # 1. Obliczamy pozycję na ekranie
        px = int(u.x * TILE_SIZE) - self.camera_x
        py = int(u.y * TILE_SIZE) - self.camera_y

        # 2. Rysujemy grafikę jednostki (jeśli istnieje)
        # Zakładam, że u.walk_frames to lista obrazków dla animacji
        if hasattr(u, 'walk_frames') and u.walk_frames:
            # Prosta animacja oparta na czasie gry
            frame_idx = (pygame.time.get_ticks() // 150) % len(u.walk_frames)
            img = u.walk_frames[frame_idx]
            screen.blit(img, (px, py))
        else:
            # Failsafe: Jeśli jednostka nie ma grafiki, rysujemy kolorowy kwadrat
            # owner.color to kolor gracza (np. czerwony dla wroga, niebieski dla Ciebie)
            owner_color = (200, 200, 200)
            if hasattr(u, 'owner') and u.owner:
                owner_color = getattr(u.owner, 'color', (200, 200, 200))
            
            pygame.draw.rect(screen, owner_color, (px + 4, py + 4, 24, 24))
            pygame.draw.rect(screen, (0, 0, 0), (px + 4, py + 4, 24, 24), 1)

        # 3. Pasek życia (opcjonalnie)
        if hasattr(u, 'health') and hasattr(u, 'max_health'):
            health_pct = max(0, u.health / u.max_health)
            pygame.draw.rect(screen, (255, 0, 0), (px, py - 5, TILE_SIZE, 4))
            pygame.draw.rect(screen, (0, 255, 0), (px, py - 5, int(TILE_SIZE * health_pct), 4))

        # 4. Ramka zaznaczenia (jeśli to aktualnie wybrana jednostka)
        if u == getattr(self, 'selected_unit', None):
            pygame.draw.rect(screen, (255, 255, 255), (px, py, TILE_SIZE, TILE_SIZE), 2)

    def draw_button(self, screen, text, rect, color=(90, 90, 90)):
        # 1. Sprawdzamy hover
        mx, my = pygame.mouse.get_pos()
        is_hovered = rect.collidepoint(mx, my)
        
        # 2. Obliczamy kolor (jeśli hover, to rozjaśniamy bazowy kolor)
        # Używamy min(c+30, 255), żeby nie przekroczyć wartości 255
        if is_hovered:
            display_color = (min(color[0]+30, 255), min(color[1]+30, 255), min(color[2]+30, 255))
        else:
            display_color = color
            
        border_color = (200, 200, 200) # Twoja elegancka ramka
        
        # 3. Rysowanie przycisku
        pygame.draw.rect(screen, display_color, rect)
        pygame.draw.rect(screen, border_color, rect, 1) 
        
        # 4. Renderowanie tekstu
        small_font = pygame.font.SysFont(None, 20)
        txt_surface = small_font.render(text, True, (255, 255, 255))
        
        # 5. Centrowanie
        txt_rect = txt_surface.get_rect(center=rect.center)
        screen.blit(txt_surface, txt_rect)

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
        # Statystyki jednostki
        """
        Rysuje tabelkę statystyk. 
        unit_name: str (nazwa do wyświetlenia)
        stats_source: słownik (z UNIT_STATS) LUB obiekt klasy Unit
        """
        if not stats_source:
            return

        # Panel tła
        panel_rect = pygame.Rect(x, y, 420, 220)
        pygame.draw.rect(screen, (40, 30, 25), panel_rect) # Brązowe wypełnienie
        pygame.draw.rect(screen, (200, 180, 100), panel_rect, 3) # Złota ramka

        # Pomocnicza funkcja do pobierania danych (obsługuje słownik i obiekt)
        def get_v(key, attr_name=None):
            if isinstance(stats_source, dict):
                return stats_source.get(key, 0)
            return getattr(stats_source, attr_name if attr_name else key, 0)

        # --- GEOMETRIA LINII (Twoja oryginalna) ---
        section_w = panel_rect.width // 3 - 50 
        section_h = panel_rect.height // 3 - 40

        line1_x = panel_rect.x + section_w
        line0_x = panel_rect.x + section_w - 20
        line2_x = panel_rect.x + 2 * section_w + 15
        line3_x = panel_rect.x + 3 * section_w + 30
        line1_y = panel_rect.y + section_h
        line2_y = panel_rect.y + 2 * section_h + 55
        line3_y = panel_rect.y + 4 * section_h + 30

        # Rysowanie Twoich linii
        color = (200, 180, 100)
        pygame.draw.line(screen, color, (line1_x, panel_rect.y), (line1_x, panel_rect.bottom), 2)
        pygame.draw.line(screen, color, (line0_x, panel_rect.y), (line0_x, panel_rect.bottom), 2)
        pygame.draw.line(screen, color, (line2_x, panel_rect.y + 33), (line2_x, panel_rect.bottom), 2)
        pygame.draw.line(screen, color, (line3_x, panel_rect.y + 33), (line3_x, panel_rect.bottom), 2)
        
        pygame.draw.line(screen, color, (panel_rect.x + 93, line1_y), (panel_rect.right, line1_y), 2)
        pygame.draw.line(screen, color, (panel_rect.x + 93, line2_y), (panel_rect.right, line2_y), 2)
        pygame.draw.line(screen, color, (panel_rect.x, line3_y), (panel_rect.right - 350, line3_y), 2)

        # --- WYŚWIETLANIE DANYCH ---
        # Używamy czcionki, którą masz w klasie (np. self.font)
        font = pygame.font.SysFont("Arial", 20, bold=True)
        
        # Nagłówek
        screen.blit(font.render(f"Jednostka: {unit_name}", True, (255, 255, 255)), (panel_rect.x + 130, panel_rect.y + 10))
        
        # Statystyki - używamy get_v, żeby brało dane niezależnie od źródła
        # 1. ATK i DEF
        screen.blit(font.render(f"ATK: {get_v('attack')}", True, (255, 255, 255)), (panel_rect.x + 90, panel_rect.y + 60))
        screen.blit(font.render(f"DEF: {get_v('defense')}", True, (255, 255, 255)), (panel_rect.x + 90, panel_rect.y + 140))
        
        # 2. HP i MORALE
        screen.blit(font.render(f"HP: {get_v('hp')}", True, (255, 255, 255)), (panel_rect.x + 200, panel_rect.y + 60))
        screen.blit(font.render(f"MOR: {get_v('morale')}", True, (255, 255, 255)), (panel_rect.x + 200, panel_rect.y + 140))
        
        # 3. MOVES i DODATKOWE
        # Dodajemy int(), aby uciąć ułamki przy wyświetlaniu
        moves_raw = get_v('moves', 'move_points') 
        moves_val = int(moves_raw) if moves_raw is not None else 0

        screen.blit(font.render(f"MOV: {moves_val}", True, (255, 255, 255)), (panel_rect.x + 310, panel_rect.y + 60))
                
        if not isinstance(stats_source, dict):
            # Jeśli to obiekt Unit (np. w garnizonie), pokazujemy EXP
            screen.blit(font.render(f"EXP: {get_v('experience')}", True, (255, 255, 0)), (panel_rect.x + 310, panel_rect.y + 140))
        else:
            # Jeśli to rekrutacja, powtarzamy ATK jako ATC wg Twojego kodu
            screen.blit(font.render(f"ATC: {get_v('attack')}", True, (255, 255, 255)), (panel_rect.x + 310, panel_rect.y + 140))
            
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

    def draw_court(self, screen):
        # 1. Tło i panele (najpierw grafika!)
        screen.fill((30, 30, 30))
        self.draw_court_players_header(screen)
        self.draw_court_stats(screen)
        self.draw_queen_panel(screen)
        self.draw_prison_sections(screen)

        # 2. Przycisk POWRÓT (w miejscu czerwonej strzałki)
        # Jeśli nie masz jeszcze grafiki strzałki, użyjemy tekstu:
        self.draw_button(screen, "<-", self.court_back_button, (140, 40, 40))

    def draw_court_players_header(self, screen):
        font = pygame.font.SysFont(None, 26)

        start_x = 140
        start_y = 20
        slot_w = 240
        slot_h = 90
        
        for i in range(5):
            # Obliczanie rzędu i kolumny
            row = i // 3
            col = i % 3 

            current_x = start_x + col * slot_w 
            if row == 1:
                current_x += slot_w // 2  # Przesunięcie dolnego rzędu o pół slotu dla lepszego wyglądu

            current_y = start_y + row * slot_h
            
            rect = pygame.Rect(current_x, current_y, 200, 60)
            
            # Rysowanie tła slotu (szary dla pustych)
            pygame.draw.rect(screen, (120, 120, 120), rect)

            # Rysowanie danych gracza, jeśli istnieje
            if i < len(self.players):
                p = self.players[i]
                pygame.draw.rect(screen, p.color, rect)
                # Zakładam, że draw_text to Twoja pomocnicza funkcja lub używasz font.render
                draw_text(screen, p.name, rect.x + 10, rect.y + 5)

    def draw_queen_panel(self, screen):
        w = screen.get_width()

        rect = pygame.Rect(w//2 - 290, 370, 600, 180)
        pygame.draw.rect(screen, (210,200,160), rect)

        draw_text(screen, "Nie ma królowej", rect.x + 250, rect.y + 20)

    def draw_court_stats(self, screen):
        screen_w = screen.get_width()
        section_width = screen_w // 3
        top_y = 190

        font_title = pygame.font.SysFont(None, 28)
        font = pygame.font.SysFont(None, 22)

        titles = ["SIŁA ARMII", "ZŁOTO", "BILANS"]

        for i in range(3):
            x =120 + i * section_width

            # Tytuł sekcji
            title_surface = font_title.render(titles[i], True, (255,255,255))
            screen.blit(title_surface, (x - 100, top_y + 100))

            # Linie graczy
            for index in range(5):

                player_y = top_y + 40 + index * 28

                if index < len(self.players):
                    player = self.players[index]

                    if i == 0:
                        value = self.calculate_army_power(player)

                    elif i == 1:
                        value = self.calculate_gold(player)

                    elif i == 2:
                        value = player.wins - player.losses if hasattr(player, "wins") else 0

                    text = f"{player.name}: {value}"

                else:
                    text = "-"

                surface = font.render(text, True, (200,200,200))
                screen.blit(surface, (x + 20, player_y))

    def draw_prison_sections(self, screen):
        font = pygame.font.SysFont(None, 24)

        start_y = 600
        section_w = 250
        gap = 40
        start_x = 60

        for i, slot in enumerate(self.prison_slots):
            x = start_x + i*(section_w + gap)
            y = start_y

            pygame.draw.rect(screen, (90,90,90), (x, y, section_w, 120))

            # info o więźniu
            if slot.general:
                draw_text(screen, slot.general.name, x+10, y+10)
                draw_text(screen, "Okup: 500", x+10, y+40)
            else:
                draw_text(screen, "Brak więźnia", x+10, y+10)

            # przyciski
            # Najpierw definiujemy obszar przycisku
            sciecie_rect = pygame.Rect(x+130, y+10, 100, 25)
            tortury_rect = pygame.Rect(x+130, y+45, 100, 25)
            przekup_rect = pygame.Rect(x+130, y+80, 100, 25)
            # Potem wywołujemy Twoją gotową funkcję (ona sama narysuje prostokąt i tekst)
            self.draw_button(screen, "SCIECIE", sciecie_rect)
            self.draw_button(screen, "TORTURY", tortury_rect)
            self.draw_button(screen, "PRZEKUP", przekup_rect)
            # Opcjonalnie zapisz rect, żeby móc obsłużyć kliknięcie w handle_mouse_click
            self.prison_sciecie_rect = sciecie_rect
            self.prison_sciecie_rect = tortury_rect
            self.prison_sciecie_rect = przekup_rect

    def execute_general(self, slot):
        slot.general = None

    def torture_general(self, slot):
        print("Informacje zdobyte")

    def bribe_general(self, slot):
        print("Generał zmienił stronę")

    def draw(self, screen):
        # WARSTWA 0: Tło absolutne
        screen.fill((30, 30, 30)) 

        # --- WARSTWA 1: MAPA I JEDNOSTKI ---
        # Rysujemy mapę ZAWSZE, chyba że jesteś w jakimś menu, które ma całkowicie ją zasłonić.
        # Jeśli chcesz widzieć mapę pod spodem menu, usuń warunek if self.screen == "map".
        
        # Lista ekranów, na których mapa ma być widoczna w tle:
        screens_with_bg = ["map", "trap_info", "castle", "garrison", "unit_info", "forge", "workshop"]
        
        if self.screen in screens_with_bg:
            self.draw_map(screen)
            for unit in self.units:
                if getattr(unit, 'visible', True) and not getattr(unit, 'is_building', False):
                    unit.draw(screen)

        # --- WARSTWA 2: INTERFEJSY SPECIFICZNE (Menu/Okna) ---
        # Tutaj używamy if/elif, bo naraz może być otwarte tylko jedno główne menu
        
        if self.screen == "map":
            self.draw_top_bar(screen)
            self.draw_ui(screen)

        elif self.screen == "trap_info":
            self.draw_top_bar(screen)
            self.draw_ui(screen)
            self.draw_trap_popup(screen)

        elif self.screen == "castle":
            self.draw_castle_interface(screen) 
            if getattr(self, "menu_open", False):
                mx, my = pygame.mouse.get_pos()
                self.draw_castle_menu(screen, mx, my)

        elif self.screen == "garrison" or self.screen == "Strażnica":
            if self.selected_castle and getattr(self.selected_castle, 'building_type', "") == "Strażnica":
                self.draw_garrison_only(screen)
            else:
                self.draw_garrison(screen)

        elif self.screen == "recruitment":
            self.draw_recruitment(screen)

        elif self.screen == "court":
            self.draw_court(screen)
        
        elif self.screen == "peasants":
            self.draw_peasants(screen)

        elif self.screen in ["forge", "workshop", "hospital", "school"]:
            # Dynamiczne wywołanie metody na podstawie nazwy ekranu
            draw_func = getattr(self, f"draw_{self.screen}", None)
            if draw_func:
                draw_func(screen)

        elif self.screen == "unit_info":
            self.draw_unit_info(screen)

        # --- WARSTWA 3: NAKŁADKI (Zawsze na samym wierzchu) ---
        
        # Tabela statystyk (Overlay)
        if getattr(self, 'inspected_unit', None):
            stats_x, stats_y = (300, 380) if self.screen == "garrison" else (150, 200)
            self.draw_unit_stats_table(
                screen, stats_x, stats_y, 
                self.inspected_unit.type, self.inspected_unit
            )

        # Potwierdzenie wyburzenia
        if getattr(self, "demolish_confirm", False):
            self.draw_demolish_confirm(screen)

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

    def start_recruitment(self, index):
        
        if index is None:
            return
        
        utype = UNIT_STATS[index]
        cost = 50
        castle = self.selected_castle

        if castle.gold < cost:
            print("Za mało złota")
            return
        
        castle.gold -= cost
        castle.start_production(utype)

        print("Rozpoczęto produkcję:", utype)
        self.screen = "garrison"

    def click_on_garrison(self, mx, my):
        castle = self.selected_castle
        if not castle: return None

        # --- JEŚLI TO STRAŻNICA (Używamy współrzędnych z draw_garrison_only) ---
        if castle.building_type == "Strażnica":
            start_x = 150
            start_y = 200
            gap = 20
            slot_size = 120
            
            for i in range(10):
                col = i % 5
                row = i // 5
                rect = pygame.Rect(start_x + col * (slot_size + gap), 
                                start_y + row * (slot_size + gap), 
                                slot_size, slot_size)
                if rect.collidepoint(mx, my):
                    return i

        # --- JEŚLI TO ZAMEK (Używamy Twoich starych współrzędnych) ---
        else:
            start_x = 100
            start_y = 120
            cols = 6
            slot_w, slot_h = 100, 180
            off_x, off_y = 130, 210
            
            for i in range(12):
                col = i % cols
                row = i // cols
                rect = pygame.Rect(start_x + col * off_x, start_y + row * off_y, slot_w, slot_h)
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

# Przykład: funkcja rysująca widok zamku (u Ciebie może się nazywać draw_castle_ui itp.)
    def draw_castle_menu(self, screen, mx, my):
        
        # 1. Nasz "Malarz" z pliku castle_graphics.py maluje tło
        if hasattr(self, 'castle_gfx'):
            self.castle_gfx.draw_background(screen)
            
            # 2. Przekazujemy mu self.selected_castle, żeby narysował odpowiednie budynki!
            self.castle_gfx.draw_buildings(screen, self.selected_castle)

        # -----------------------------------------------------------
        # 3. TUTAJ ZACZYNA SIĘ TWÓJ STARY KOD (Nic nie kasuj!)
        # -----------------------------------------------------------
        # pygame.draw.rect(screen, (100, 100, 100), self.button_rect)
        # screen.blit(self.font.render(f"Złoto: {self.selected_castle.gold}", ...))
        # itd.
        # 1. Zewnętrzny plik rysuje całą grafikę zamku! (Czysto i elegancko)
        self.castle_gfx.draw_background(screen)
        
        # Tutaj przekażesz obiekt zamku, w którym aktualnie jesteś
        self.castle_gfx.draw_buildings(screen, self.select_castle)

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

        buildings = ["hospital", "school", "Koszary", "forge", "workshop"]
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
        
    def handle_court_click(self, mx, my):
        # Używamy zmiennej, którą zdefiniowaliśmy w draw_court
        if hasattr(self, 'back_button') and self.court_back_button.collidepoint(mx, my):
            self.screen = "castle"
            return

        # więzienie
        start_y = 380
        for i, slot in enumerate(self.prison_slots):
            y = start_y + i * 80

            if pygame.Rect(50, y, 200, 20).collidepoint(mx, my):
                self.execute_general(slot)

            if pygame.Rect(50, y+20, 200, 20).collidepoint(mx, my):
                self.torture_general(slot)

            if pygame.Rect(50, y+40, 200, 20).collidepoint(mx, my):
                self.bribe_general(slot)
    
    def handle_map_click(self, mx, my, button):
        tile_x = (mx + self.camera_x) // TILE_SIZE
        tile_y = (my + self.camera_y) // TILE_SIZE

        # --- 1. PRAWY PRZYCISK (Podgląd statystyk) ---
        if button == 3:
            target_unit = self.get_unit_at(tile_x, tile_y)
            if target_unit:
                # TYLKO ustawiamy jednostkę. 
                # NIE zmieniamy self.screen, żeby mapa została pod spodem!
                self.inspected_unit = target_unit
            return # Kończymy, żeby nie odpalić logiki ruchu prawym przyciskiem

        # --- 2. LEWY PRZYCISK ---
        if button == 1:
            # A. NAJPIERW: Sprawdzamy, czy kliknięto w JEDNOSTKĘ (zmiana wyboru)
            # Przeszukujemy wszystkich graczy, aby móc np. zaznaczyć wroga do ataku lub zmienić wybór
            for player in self.players:
                for unit in player.units:
                    if unit.x == tile_x and unit.y == tile_y:
                        # Jeśli kliknięto w jednostkę, ZAWSZE ją zaznaczamy i PRZERYWAMY
                        if unit.owner == self.players[self.current_player]:
                            self.selected_unit = unit
                            unit.target_x = unit.target_y = None
                            unit.planned_path = []
                            print(f"Zmieniono wybór na: {unit.type}")
                            return # To wyjście jest kluczowe!

            # B. POTEM: Jeśli kliknięto w puste pole (lub zamek) i mamy kogoś wybranego -> RUCH
            if self.selected_unit:
                u = self.selected_unit
                
                # Potwierdzenie ruchu (drugi klik)
                if tile_x == getattr(u, 'target_x', None) and tile_y == getattr(u, 'target_y', None):
                    u.move_along_path(self)
                    self.check_unit_castle_entry(u)
                    return

                # Pierwszy klik - planowanie trasy
                u.target_x, u.target_y = tile_x, tile_y
                u.planned_path = self.find_path(u, tile_x, tile_y)
                return

            # C. NA KOŃCU: Wejście do obiektu (Zamek lub Strażnica)
            for castle in self.castles:
                # Sprawdzamy czy kliknięto w pole zajmowane przez budynek
                # (Dla strażnicy 1x1, dla zamku może być 2x2)
                size = 2 if castle.building_type == "Zamek" else 1
                
                if castle.x <= tile_x < castle.x + size and castle.y <= tile_y < castle.y + size:
                    if not castle.destroyed:
                        self.selected_castle = castle
                        
                        # --- KLUCZOWY ROZDRZIAŁ ---
                        if castle.building_type == "Strażnica":
                            self.screen = "garrison" # Idziemy od razu do slotów
                            print("Wchodzisz bezpośrednio do Garnizonu Strażnicy")
                        else:
                            self.screen = "castle" # Idziemy do menu głównego Zamku
                            print(f"Wchodzisz do menu obiektu: {castle.building_type}")
                        return

    def handle_castle_click(self, mx, my):
        if not self.selected_castle:
            return

        # 1. POWRÓT (BACK)
        # Obsługa standardowego przycisku BACK
        if self.back_button.collidepoint(mx, my):
            self.screen = "map"
            self.selected_castle = None
            return

        # Specjalny powrót dla DWORU (ten wyżej, obok portretu)
        if self.screen == "court" and self.court_back_button.collidepoint(mx, my):
            self.screen = "castle"
            return

        # 2. GARNIZON
        if self.garrison_button and self.garrison_button.collidepoint(mx, my):
            self.screen = "garrison"
            return

        # 3. KUŹNIA
        if self.forge_button and self.forge_button.collidepoint(mx, my):
            self.screen = "forge"
            return

        # 4. REKRUTACJA (Naprawiony błąd koszary_button)
        # Jeśli koszary_button to u Ciebie to samo co garrison_button, 
        # możesz użyć tej nazwy. Jeśli to osobny przycisk, musi mieć Rect w init!
        if "Koszary" in self.selected_castle.buildings:
            # Sprawdzamy czy kliknięto w garrison_button (używając go jako wejścia do rekrutacji)
            if self.garrison_button and self.garrison_button.collidepoint(mx, my):
                self.screen = "recruitment"
                self.recruitment_open = True
                self.recruitment_scroll = -2
                self.selected_unit_type = 0
                self.selected_patent_index = None
                return

        # 5. CHŁOPI
        if self.peasant_button.collidepoint(mx, my):
            self.screen = "peasants"
            return

        # 6. DWÓR
        if self.court_button.collidepoint(mx, my):
            self.screen = "court"
            return

        # 7. MENU BUDOWANIA
        if self.menu_open:
            for name, rect in self.build_rects.items():
                if rect.collidepoint(mx, my):
                    if self.selected_castle.build(name):
                        self.build_clicked[name] = True
                        self.menu_open = False
                        self.build_open = False
                    return
    # =======================
    # HANDLE CLICKS
    # =======================
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

        
        if self.start_prod_button.collidepoint(mx, my):
            # Przycisk zadziała TYLKO jeśli masz wybraną złotą ramkę (index nie jest None)
            if self.selected_patent_index is not None:
                p = castle.patents[self.selected_patent_index]
                u_name = p["unit_type"] if isinstance(p, dict) else p
                
                if u_name:
                    castle.start_production(u_name)
                    print(f"Ręcznie uruchomiono produkcję: {u_name}")
            else:
                print("BŁĄD: Musisz najpierw kliknąć w patent, aby go podświetlić!")
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

    def demolish_castle(self, castle):
        if not castle: return
        from unit import Unit

        # 1. PRZYGOTOWANIE WOJSKA (Filtrujemy None)
        all_units = [u for u in castle.garrison if u is not None]
        
        if all_units:
            # Dzielimy na dwie grupy: pierwsza 10, druga reszta (max 2)
            groups = [all_units[:10], all_units[10:]]
            
            # Szukamy 2 wolnych miejsc wokół zamku
            spawn_points = self.find_multiple_spawn_positions(castle, len([g for g in groups if g]))
            
            for i, group in enumerate(groups):
                if group and spawn_points[i]:
                    nx, ny = spawn_points[i]
                    
                    # Tworzymy nową armię (liderem jest pierwszy w grupie)
                    new_army = Unit(group[0].type, nx, ny, castle.owner)
                    new_army.garrison = [None] * 10
                    
                    # Wkładamy jednostki do slotów nowej armii
                    for j, u in enumerate(group):
                        new_army.garrison[j] = u
                    
                    # Rejestracja armii na mapie
                    self.units.append(new_army)
                    castle.owner.units.append(new_army)
                    print(f"Grupa ewakuacyjna {i+1} opuściła zamek na poz: {nx, ny}")

        # 2. LOGIKA NISZCZENIA ZAMKU
        castle.destroyed = True
        if castle.owner and castle in castle.owner.castles:
            castle.owner.castles.remove(castle)
            
        castle.owner = None
        castle.garrison = [None] * 12 # Czyścimy zamek
        
        self.demolish_confirm = False
        self.screen = "map"
        print("Zamek stał się ruiną. Wojsko sformowało do dwóch grup ucieczkowych.")

    def draw_building_template(self, screen, title, lines, theme_color=(100, 100, 130), border_color=(180, 180, 220)):
        # Ogólny zarys każdego budynku w zamku
        # 1. Tło ogólne
        screen.fill((60, 60, 80))

        # 2. Czcionki (najlepiej zdefiniuj je raz w __init__ jako self.font_title itd.)
        font_title = pygame.font.SysFont(None, 48)
        font_text = pygame.font.SysFont(None, 24)

        # 3. Panel środkowy
        panel = pygame.Rect(120, 80, 760, 420)
        pygame.draw.rect(screen, theme_color, panel)
        pygame.draw.rect(screen, border_color, panel, 6)

        # 4. Tytuł (zawsze wycentrowany)
        title_surface = font_title.render(title.upper(), True, border_color)
        screen.blit(title_surface, (panel.centerx - title_surface.get_width() // 2, panel.y - 40))

        # 5. Tekst (automatyczne linie)
        y = panel.y + 30
        for line in lines:
            txt = font_text.render(line, True, (255, 255, 255))
            screen.blit(txt, (panel.x + 30, y))
            y += 28

        # 6. Stopka (Twoje przyciski)
        self.draw_building_footer(screen)

    def draw_forge(self, screen):
        lines = [
            "Dzień i noc słychać rytmiczne uderzenia żelaznych młotów –",
            "to ławrowni kowale w pocie czoła pokuwają bojowe rumaki.",
            "Dzięki ich wysiłkom będziesz mógł rozpocząć produkcję",
            "oddziałów konnych, bardzo przydatnych w bojowych zmaganiach.",
            "",
            "Jednocześnie łowisarze z górskich krain wytapiają tu stal",
            "na pancerze i wytwarzają broń palną. Daje Ci to możliwość",
            "produkowania w koszarach artylerii oraz ciężko opancerzonych",
            "oddziałów."
        ]
        # Używamy brązowych kolorów dla Kuźni
        self.draw_building_template(screen, "Forge", lines, (120, 90, 60), (200, 170, 90))

    def draw_workshop(self, screen):
        lines = [
            "Pracują tu znakomici rzemieślnicy ze starego kraju.",
            "Dzięki ich kunsztowi staniesz się posiadaczem łuków, kusz,",
            "oszczepów oraz strzał niespotykanych wcześniej w tej części",
            "kontynentu. Daje Ci to możliwość rozpoczęcia produkcji",
            "oddziałów rażących wroga na dystans a także rozmaitych",
            "machin."
        ]
        self.draw_building_template(screen, "Workshop", lines)

    def draw_hospital(self, screen):
        lines = [
            "Zapach rozcieranych ziół da się odczuć we wszystkich zakamarkach Twojego dziedzinca.",
            "Powstające tu specyfiki i mikstury robione są według bardzo starych receptur...",
            "Owe lekarstwa pomogą odzyskać Twoim rycerzom pełnię sił.",
            "Ponadto troskliwi kapłani roztoczyli swą opiekę nad mieszkańcami wsi."
        ]
        self.draw_building_template(screen, "Szpital", lines)

    def draw_school(self, screen):
        lines = [
            "Dzięki wykładanym tu naukom, możliwe będzie szkolenie",
            "Twoich wojsk w rzemiośle rycerskim. Wprawieni w sztuce",
            "wojennej weterani bitew borbijskich sprawią, że byle żołdak w",
            "szybkim tempie nauczy się wprawnie posługiwać posiadanym",
            "orężem.",
            "",
            "Ponadto, dzięki wysiłkom uczonych waldzkich, którzy tu",
            "także przebywają, możliwe będzie osiągnięcie wyższego",
            "poziomu technologii w Twoim królestwie."
        ]
        self.draw_building_template(screen, "Szkoła", lines)

    def draw_unit_info(self, screen):
        # Historyczne informacje o jednostce w koszarach.
        screen.fill((20,20,20))
        0
        # Jeśli tekst jest pusty, zainicjuj go bezpiecznym komunikatem
        if not hasattr(self, 'unit_info_text') or not self.unit_info_text:
            self.unit_info_text = "Brak informacji\nNie wybrano jednostki."

        font_title = pygame.font.SysFont(None, 48)
        font_text = pygame.font.SysFont(None, 28)

        lines = self.unit_info_text.split("\n")
        y = 120

        # Nagłówek (pierwsza linia)
        if lines:
            screen.blit(font_title.render(lines[0], True, (255,255,0)), (120, y)) # Zmieniłem na żółty, żeby się wyróżniał
            y += 80

        # Opis (reszta linii)
        for line in lines[1:]:
            # Proste zawijanie tekstu: jeśli linia jest za długa, można by ją dzielić, 
            # ale na razie renderujemy linia po linii.
            txt_surf = font_text.render(line, True, (200,200,200))
            screen.blit(txt_surf, (120, y))
            y += 35

        info = font_text.render("Kliknij dowolny klawisz lub przycisk myszy, aby wrócić", True, (120,120,120))
        screen.blit(info, (120, screen.get_height()-80))

    def load_castles_from_fac(self, fac_path):
        import re
        with open(fac_path, 'r') as f:
            content = f.read()

        # Szukamy wszystkich zdefiniowanych miejsc 
        all_places = re.findall(r"\(zamek_place (\d+) (\d+)\)", content)
        # Szukamy indeksów tych, które są już gotowe 
        built_indices = re.findall(r"\(zbudowano zamek (\d+)\)", content)
        built_indices = [int(i) for i in built_indices]
        print(f"DEBUG: Zbudowane zamki to: {built_indices}") # <--- DODAJ TO
        self.castles = []           # Tu obiekty z garnizonem
        self.castle_locations = []  # Tu tylko koordynaty pustych miejsc

        for i, (x, y) in enumerate(all_places):
            ix, iy = int(x), int(y)
                    # Wewnątrz load_castles_from_fac
            if i in built_indices:
                self.castles.append(Castle(ix, iy)) # Tu idzie ZBUDOWANY
            else:
                self.castle_locations.append((ix, iy)) # Tu idzie PUSTY PLAC

    def handle_camera(self):
        keys = pygame.key.get_pressed()
        scroll_speed = 10 

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.camera_x -= scroll_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.camera_x += scroll_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.camera_y -= scroll_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.camera_y += scroll_speed

        # AUTOMATYCZNE OBLICZANIE GRANIC:
        # Szerokość mapy w pikselach = liczba kafelków * 32
        map_pixel_width = len(self.map[0]) * TILE_SIZE
        map_pixel_height = len(self.map) * TILE_SIZE

        # Ograniczenia (800 i 600 to wymiary Twojego okna)
        self.camera_x = max(0, min(self.camera_x, map_pixel_width - 800))
        self.camera_y = max(0, min(self.camera_y, map_pixel_height - 600))

    def draw_top_bar(self, screen):
        mx, my = pygame.mouse.get_pos()
    
        # 1. Logika pokazywania: jeśli dotkniesz góry
        if self.top_ui_trigger_area.collidepoint(mx, my):
            self.show_top_ui = True
        
        # 2. POPRAWKA: Logika chowania
        # Pasek znika tylko jeśli: myszka jest poza obszarem paska I nie mamy otwartego dropdowna
        elif not self.top_ui_full_area.collidepoint(mx, my) and self.active_dropdown is None:
            self.show_top_ui = False

        if self.show_top_ui:
            # Rysujemy tło paska (teraz nie zniknie pod dropdownem)
            pygame.draw.rect(screen, (40, 40, 40), (0, 0, 1024, 40))
            # 1. Przycisk SYSTEM
            pygame.draw.rect(screen, (100, 100, 100), self.btn_system)
            screen.blit(self.font.render("System", True, (255, 255, 255)), (self.btn_system.x + 5, 10))

            # 2. Przycisk MAPA
            pygame.draw.rect(screen, (100, 100, 100), self.btn_mapa)
            screen.blit(self.font.render("Mapa", True, (255, 255, 255)), (self.btn_mapa.x + 15, 10))

            # 3. Przycisk KONIEC TURY (Twój zwój)
            pygame.draw.rect(screen, (139, 69, 19), self.next_turn_button)
            pygame.draw.rect(screen, (212, 175, 55), self.next_turn_button, 2)
            txt = self.font.render(f"Koniec tury {self.turn}", True, (255, 255, 255))
            screen.blit(txt, (self.next_turn_button.x + 10, 10))

            if self.show_top_ui:
                # Rysujemy przyciski główne (System, Mapa, Koniec Tury)
                pygame.draw.rect(screen, (100, 100, 100), self.btn_system)
                screen.blit(self.font.render("System", True, (255, 255, 255)), (self.btn_system.x + 5, 10))
                
                pygame.draw.rect(screen, (100, 100, 100), self.btn_mapa)
                screen.blit(self.font.render("Mapa", True, (255, 255, 255)), (self.btn_mapa.x + 15, 10))
            # Rysowanie dropdowna (jeśli aktywny)
        if self.active_dropdown in self.menu_options:
            options = self.menu_options[self.active_dropdown]
            start_x = self.btn_system.x if self.active_dropdown == "System" else self.btn_mapa.x
            
            # CZYŚCIMY stare słowniki przed ponownym przypisaniem (ważne!)
            self.system_buttons = {}
            self.mapa_buttons = {}

            for i, opt in enumerate(options):
                rect = pygame.Rect(start_x, 40 + (i * self.option_height), 150, self.option_height)
                
                # ZAPISUJEMY RECT DO ODPOWIEDNIEGO SŁOWNIKA
                if self.active_dropdown == "System":
                    self.system_buttons[opt] = rect
                else:
                    self.mapa_buttons[opt] = rect

                # Reszta Twojego kodu rysowania...
                is_hovered = rect.collidepoint(mx, my)
                color = (150, 150, 150) if is_hovered else (80, 80, 80)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (200, 200, 200), rect, 1)
                txt = self.font.render(opt, True, (255, 255, 255))
                screen.blit(txt, (rect.x + 10, rect.y + 5))

    def draw_bottom_bar(self, screen):

        # Wybór napisów w zależności od stanu
        if self.build_menu_open:
            labels = ["DROGA", "PUŁAPKA", "SKARB", "WIEŻA", "TWIERDZA", "ZAMEK"]
            header_text = "BUDOWANIE:"
        else:
            labels = ["TRYB MAPY", "ATK", "SPL", "WAIT", "BUILD", "REC"]

        for i, rect in enumerate(self.action_buttons):
            mx, my = pygame.mouse.get_pos()
            
            # Inny kolor dla menu budowania, żeby gracz wiedział, że coś się zmieniło
            if self.build_menu_open:
                color = (34, 139, 34) if not rect.collidepoint(mx, my) else (50, 205, 50) # Zielenie
            else:
                color = (139, 69, 19) if not rect.collidepoint(mx, my) else (160, 82, 45) # Brązy
            
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (212, 175, 55), rect, 2)
            
            txt = self.font.render(labels[i], True, (255, 255, 255))
            text_rect = txt.get_rect(center=rect.center)
            screen.blit(txt, text_rect)

    def handle_mouse_up(self, mx, my):
        if self.active_dropdown:
            options = self.menu_options[self.active_dropdown]
            start_x = self.btn_system.x if self.active_dropdown == "System" else self.btn_mapa.x
            
            # Sprawdzamy, na której opcji puściliśmy przycisk
            for i, opt in enumerate(options):
                rect = pygame.Rect(start_x, 40 + (i * self.option_height), 150, self.option_height)
                if rect.collidepoint(mx, my):
                    print(f"Wybrano z menu {self.active_dropdown}: {opt}")
                    self.execute_menu_command(self.active_dropdown, i)
                    break
            
            # Po puszczeniu myszki zawsze zamykamy menu
            self.active_dropdown = None

    def check_unit_info(self, mx, my):
        castle = self.selected_castle
        if not castle: return

        # MUSZĄ być identyczne jak w draw_garrison
        start_x, start_y = 100, 120
        offset_x, offset_y = 130, 210
        cols = 6

        col = (mx - start_x) // offset_x
        row = (my - start_y) // offset_y

        if 0 <= col < cols and 0 <= row < 2:
            index = row * cols + col
            if index < len(castle.garrison):
                # Przypisujemy jednostkę (może to być obiekt Unit ALBO None)
                self.inspected_unit = castle.garrison[index]
                
                # POPRAWKA: Sprawdzamy, czy slot nie jest pusty zanim zrobimy print
                if self.inspected_unit is not None:
                    print(f"DEBUG: Znaleziono jednostkę: {self.inspected_unit.type}")
                else:
                    print("DEBUG: Kliknięto pusty slot")
            else:
                self.inspected_unit = None
        else:
            self.inspected_unit = None
            
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

    def draw_path_dots(self, screen, unit, path):
        """Rysuje kropki trasy z uwzględnieniem wag terenu i skosów."""
        TILE_SIZE = 32
        
        # Startujemy od obecnej pozycji jednostki
        current_x, current_y = unit.x, unit.y
        accumulated_cost = 0  # Tu sumujemy koszt drogi
        
        for px, py in path:
            # 1. OBLICZAMY KOSZT TEGO KROKU
            dx = px - current_x
            dy = py - current_y
            
            # Pobieramy koszt terenu (pamiętaj o world. lub self. przed TERRAIN_TYPES)
            tile_char = self.map[py][px]
            terrain_info = TERRAIN_TYPES.get(tile_char, {})
            base_cost = terrain_info.get("cost", 4)
            
            # Modyfikator skosu
            move_modifier = 1.41 if (dx != 0 and dy != 0) else 1.0
            
            step_cost = base_cost * move_modifier
            accumulated_cost += step_cost
            
            # 2. POZYCJA NA EKRANIE
            dot_x = (px * TILE_SIZE) + (TILE_SIZE // 2) - self.camera_x
            dot_y = (py * TILE_SIZE) + (TILE_SIZE // 2) - self.camera_y
            
            # 3. LOGIKA KOLORÓW (Bazujemy na skumulowanym koszcie!)
            if accumulated_cost <= unit.move_points:
                color = (0, 0, 0)       # Czarna - wejdziesz w tej turze
            else:
                color = (255, 0, 0)     # Czerwona - braknie MP w tej turze
                
            # 4. RYSOWANIE
            if -20 < dot_x < SCREEN_WIDTH + 20 and -20 < dot_y < SCREEN_HEIGHT + 20:
                pygame.draw.circle(screen, (255, 255, 255), (dot_x, dot_y), 5) 
                pygame.draw.circle(screen, color, (dot_x, dot_y), 4)
                
            # 5. AKTUALIZACJA POZYCJI (ważne dla poprawnego liczenia skosów w następnej kropce)
            current_x, current_y = px, py

    def find_path(self, unit, dest_x, dest_y):
        target_castle = None
        for c in self.castles:
            if c.x <= dest_x <= c.x + 1 and c.y <= dest_y <= c.y + 1:
                target_castle = c
                break

        # Kolejka przechowuje: (łączny_koszt, x, y, lista_kroków)
        queue = [(0, unit.x, unit.y, [])]
        visited = {} # Przechowuje najniższy koszt dotarcia do danego pola

        while queue:
            current_cost, cx, cy, path = heapq.heappop(queue)

            if (cx, cy) in visited and visited[(cx, cy)] <= current_cost:
                continue
            visited[(cx, cy)] = current_cost

            # Cel osiągnięty
            if target_castle:
                if target_castle.x <= cx <= target_castle.x + 1 and target_castle.y <= cy <= target_castle.y + 1:
                    return path
            elif (cx, cy) == (dest_x, dest_y):
                return path

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                nx, ny = cx + dx, cy + dy
                
                if self.is_walkable(nx, ny, unit, target_castle):
                    tile_char = self.map[ny][nx]
                    
                    # WYCIĄGAMY KOSZT Z TWOJEGO SŁOWNIKA
                    # Jeśli kafel nie ma zdefiniowanego kosztu (np. zamek '#'), dajemy domyślnie 4
                    base_cost = TERRAIN_TYPES.get(tile_char, {}).get("cost", 4)
                    
                    # Modyfikator skosu (geometryczny wzrost dystansu)
                    move_modifier = 1.41 if (dx != 0 and dy != 0) else 1.0
                    
                    step_cost = base_cost * move_modifier
                    new_total_cost = current_cost + step_cost
                    
                    heapq.heappush(queue, (new_total_cost, nx, ny, path + [(nx, ny)]))

        return []
    
    def is_walkable(self, x, y, unit=None, target_castle=None):
        # 1. Jeśli badany kafel (x, y) należy do zamku, do którego idziemy -> MOŻNA WEJŚĆ
        if target_castle:
            if target_castle.x <= x <= target_castle.x + 1 and target_castle.y <= y <= target_castle.y + 1:
                return True

        # 2. Granice mapy
        if not (0 <= x < len(self.map[0]) and 0 <= y < len(self.map)):
            return False

        # 3. Blokada innych zamków (żeby nie skracać sobie drogi przez środek innego miasta)
        for castle in self.castles:
            if target_castle and castle == target_castle: continue # Ten ignorujemy
            if castle.x <= x <= castle.x + 1 and castle.y <= y <= castle.y + 1:
                return False

        tile_char = self.map[y][x]
        # Jeśli kafel nie ma zdefiniowanego kosztu w TERRAIN_TYPES, 
        # uznajemy go za nieprzejezdny (np. Góry, Woda)
        if "cost" not in TERRAIN_TYPES.get(tile_char, {}):
            return False
        
        return True
            
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
    
    def handle_ui_click(self, mx, my, button=1):  # DODAJ button=1
        # 1. DROPDOWNY (Góra)
        if self.handle_dropdown_clicks(mx, my):
            return True

        # 2. GÓRNY PASEK
        if self.show_top_ui and self.top_ui_full_area.collidepoint(mx, my):
            if self.btn_system.collidepoint(mx, my):
                self.active_dropdown = "System" if self.active_dropdown != "System" else None
            elif self.btn_mapa.collidepoint(mx, my):
                self.active_dropdown = "Mapa" if self.active_dropdown != "Mapa" else None
            elif self.next_turn_button.collidepoint(mx, my):
                self.next_turn()
            return True

        # --- BEZPIECZNIK ---
        if self.selected_unit is None:
            return False 

        # 3. SPRAWDZANIE DOLNEJ STREFY (y >= 610)
        if my >= 610:
            # PRZYCISKI AKCJI (zawsze sprawdzamy kolizję)
            for i, rect in enumerate(self.action_buttons):
                if rect.collidepoint(mx, my):
                    if button == 1: self.handle_action_button_click(i)
                    return True

            # SLOTY ARMII
            u = self.selected_unit
            if u and hasattr(self, 'army_slot_rects'):
                garrison = getattr(u, 'garrison', [])
                # display_units to lider + jego garnizon
                display_units = [unit for unit in ([u] + garrison) if unit is not None]
                
                for i, rect in enumerate(self.army_slot_rects):
                    if rect.collidepoint(mx, my):
                        # Jeśli trafiliśmy w konkretny slot:
                        if i < len(display_units):
                            if button == 3:
                                self.inspected_unit = display_units[i]
                            elif button == 1:
                                print(f"Wybrano: {display_units[i].type}")
                        # Zwracamy True, bo kliknęliśmy w OBSZAR slotu (nawet pustego)
                        return True

            # KLUCZOWA ZMIANA: 
            # Jeśli my >= 610, ale NIE trafiliśmy w żaden przycisk ani slot, 
            # zwracamy False, żeby można było klikać mapę "pod" panelem (jeśli wystaje).
            return False
        
    def draw_ui(self, screen):

        # 2. DOLNY PANEL ARMII (Tylko dla 2+ jednostek)
        u = self.selected_unit
        if u:
            garrison = getattr(u, 'garrison', [])
            display_units = [unit for unit in ([u] + garrison) if unit is not None]

            # Rysujemy sloty armii TYLKO jeśli jest grupa
            if len(display_units) >= 2:
                panel_rect = pygame.Rect(0, 610, 1024, 158)
                pygame.draw.rect(screen, (30, 20, 10), panel_rect) 
                pygame.draw.rect(screen, (100, 80, 60), panel_rect, 2)

                if not hasattr(self, 'army_slot_rects'):
                    self.army_slot_rects = [pygame.Rect(10 + i * 75, 620, 70, 140) for i in range(10)]

                for i in range(10):
                    rect = self.army_slot_rects[i]
                    pygame.draw.rect(screen, (60, 40, 30), rect)
                    pygame.draw.rect(screen, (150, 130, 100), rect, 1)

                    if i < len(display_units):
                        unit = display_units[i]
                        name_txt = self.font_small.render(str(unit.type), True, (255, 255, 255))
                        count = getattr(unit, 'count', 1)
                        count_txt = self.font_small.render(str(count), True, (255, 255, 0))
                        screen.blit(name_txt, (rect.x + 5, rect.y + 120))
                        screen.blit(count_txt, (rect.x + 5, rect.y + 100))

        # 3. PRZYCISKI AKCJI (Zawsze widoczne na ekranie)
        # Wyciągnięte poza "if u:", więc będą widoczne od startu gry
        self.draw_bottom_bar(screen)
                
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

    def execute_build_action(self, button_index, army):         
        # 1. Poprawa zmiennych: używamy 'army' zamiast 'u' i 'button_index' zamiast 'index'
        if not army: return
        grid_x, grid_y = army.x, army.y

        # 2. Sprawdzenie, czy w armii jest Budowniczy (funkcja pomocnicza)
        def get_builder_from_army(a):
            if a.type == "Budowniczy": return a
            if hasattr(a, 'garrison'):
                for slot in a.garrison:
                    if slot and slot.type == "Budowniczy":
                        return slot
            return None

        builder = get_builder_from_army(army)
        if not builder: 
            print("Błąd: W tej armii nie ma Budowniczego!")
            return

        # --- LOGIKA BUDOWANIA (używamy button_index) ---

        # 1. DROGA (Indeks 0)
        if button_index == 0:
            if army.move_points >= 5:
                self.road_build_mode = True  # Aktywujemy tryb strzałek
                self.build_menu_open = False
                print("Tryb budowy drogi: Wybierz kierunek strzałką.")
            else:
                print("Za mało punktów ruchu na budowę drogi!")
            return

        # 2. PUŁAPKA (Indeks 1)
        if button_index == 1: 
            # --- ZMIANA: Usuwamy natychmiastowe stawianie X ---
            # Zamiast stawiać pułapkę pod nogami, włączamy tryb celowania
            self.trap_build_mode = True   
            self.build_menu_open = False  # Zamykamy menu, żeby widzieć mapę
            
            # Opcjonalnie: możemy zapisać, który budowniczy/armia buduje, 
            # aby funkcja handle_mouse_click wiedziała kogo usunąć po kliknięciu
            self.active_builder_army = army 
            self.active_builder_unit = builder
            
            print("Wybierz pole wokół budowniczego, aby zastawić pułapkę.")
            return

        # 3. SKARB (Indeks 2)
        if button_index == 2: 
            if self.map[grid_y][grid_x] == "$":
                army.owner.gold += 500
                self.map[grid_y][grid_x] = "."
                self.build_menu_open = False
            return

        # 4. BUDOWLE (Strażnica=3, Twierdza=4, Zamek=5)
        menu_to_type = {3: "Strażnica", 4: "Twierdza", 5: "Zamek"}
    
        if button_index in menu_to_type:
            b_type = menu_to_type[button_index]
            
            # WYWOŁUJEMY: Budowniczy i jego armia zostaną "wciągnięci" do zamku
            self.start_building(grid_x, grid_y, b_type, builder)
            
            self.build_menu_open = False
            self.selected_unit = None
            return

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

    def spawn_test_builder(self):
        if not self.players:
            return
        
        # Wybieramy pierwszego gracza i nazywamy go 'current_p'
        current_p = self.players[0] 
        
        from unit import Unit
        # Tworzymy jednostkę i przypisujemy jej 'current_p'
        new_builder = Unit("Budowniczy", 15, 15, self.players[self.current_player])
        
        # Dodajemy do systemu
        self.add_unit(new_builder)
        
        # Teraz ta linia zadziała, bo 'current_p' już istnieje!
        print(f"DEBUG: Stworzono budowniczego dla: {current_p.name}")

    def spawn_unit(self, unit_type, x, y, owner):
        """Główna i jedyna funkcja do tworzenia jednostek w świecie."""
        from unit import Unit  # Jeśli musisz tu mieć import, to ok, ale lepiej przenieś na górę pliku
        
        new_unit = Unit(unit_type, x, y, owner)
        
        # Użyj tylko jednej metody dodawania do gry (wybierz tę, która działa lepiej)
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
    
    def start_building(self, x, y, b_type, builder=None):
        if b_type not in BUILDING_TYPES: return
        config = BUILDING_TYPES[b_type]
        
        ix, iy = int(x), int(y)
        anchor_x, anchor_y = ix, iy
        found_foundation = False

        # 1. Logika szukania miejsca (zostaje bez zmian)
        if config.get("size") == 2:
            for dx in [0, -1]:
                for dy in [0, -1]:
                    nx, ny = ix + dx, iy + dy
                    if 0 <= nx < len(self.map[0]) and 0 <= ny < len(self.map):
                        if self.map[ny][nx] == "#":
                            anchor_x, anchor_y = nx, ny
                            found_foundation = True
                            break
                if found_foundation: break
            if not found_foundation: return
        else:
            if self.map[iy][ix] in [".", "p"] and not self.is_area_occupied_by_foundation(ix, iy):
                found_foundation = True
            else: return

        # 2. TWORZYMY OBIEKT ZAMKU OD RAZU
        from castle import Castle
        new_castle = Castle(anchor_x, anchor_y, self.current_player, building_type=b_type)
        
        # NOWE STATYSTYKI BUDOWY:
        new_castle.under_construction = True
        new_castle.total_work_needed = 12.0  # Twoje bazowe 12 tur
        new_castle.work_done = 0.0
        new_castle.mury_percent = 0  # Postęp murów (obrona)

        # 3. PRZENOSZENIE CAŁEJ ARMII DO GARNIZONU
        # Szukamy armii na tym polu (tej, która zainicjowała budowę)
        army = self.get_unit_at(ix, iy) # Pobieramy armię zanim ją usuniemy
        
        if army:
            # 1. Przenosimy jednostki do garnizonu zamku
            self.enter_castle(army, new_castle) 
            # Funkcja enter_castle już zajmie się usunięciem z self.units!
        
        self.castles.append(new_castle)

        # --- SYMBOLE NA MAPIE ---
        size = 2 if config.get("size") == 2 else 1
        for dy in range(size):
            for dx in range(size):
                self.map[anchor_y + dy][anchor_x + dx] = "P"

        print(f"Rozpoczęto budowę {b_type}. Garnizon pilnuje placu.")

    def process_construction(self):
        for castle in self.castles:
            if getattr(castle, 'under_construction', False):
                # 1. Liczymy ilu Budowniczych jest w garnizonie tego zamku
                builders_count = sum(1 for slot in castle.garrison if slot and slot.type == "Budowniczy")
                
                if builders_count > 0:
                    # 2. Dodajemy postęp (1 budowniczy = 1 pkt terytorialny)
                    castle.work_done += builders_count
                    
                    # 3. Wyliczamy % murów (do obrony w bitwie)
                    castle.mury_percent = min(100, int((castle.work_done / castle.total_work_needed) * 100))
                    print(f"Budowa {castle.building_type}: {castle.mury_percent}% murów.")

                # 4. Sprawdzamy czy koniec
                if castle.work_done >= castle.total_work_needed:
                    castle.under_construction = False
                    castle.mury_percent = 100
                    
                    # Zmieniamy "P" na symbol gotowego budynku
                    sym = "H" if castle.building_type == "Strażnica" else "C"
                    size = 2 if castle.building_type in ["Twierdza", "Zamek"] else 1
                    for dy in range(size):
                        for dx in range(size):
                            self.map[castle.y + dy][castle.x + dx] = sym
                    print(f"Budowa ukończona: {castle.building_type} gotowy!")

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
        self.back_button = pygame.Rect(screen.get_width()//2 - 250, 650, 160, 45)
        self.draw_button(screen, "POWRÓT", self.back_button)

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

        # Rysuj POWRÓT zawsze
        self.draw_button(screen, "POWRÓT", self.back_button, (140, 80, 80))

        # Rysuj OPUŚĆ tylko w garnizonie
        if self.screen == "garrison":
            self.draw_button(screen, "WYPUŚĆ", self.button_send_army, (160, 120, 60))

        # Rysuj ZBURZ tylko jeśli to Strażnica
        if self.selected_castle and self.selected_castle.building_type == "Strażnica":
            self.draw_button(screen, "ZBURZ", self.destroy_button, (100, 40, 40))

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
    def handle_mouse_motion(self, mx, my):
        # Resetujemy podgląd, jeśli nie znajdziemy jednostki
        self.inspected_unit = None

        if self.screen == "garrison":
            start_x, start_y = 100, 120
            offset_x, offset_y = 130, 210
            slot_w, slot_h = 100, 180
            cols = 6

            # Sprawdzamy, czy mysz jest nad którymś ze slotów
            for i in range(len(self.selected_castle.garrison)):
                row = i // cols
                col = i % cols
                x = start_x + col * offset_x
                y = start_y + row * offset_y
                rect = pygame.Rect(x, y, slot_w, slot_h)

                if rect.collidepoint(mx, my):
                    unit = self.selected_castle.garrison[i]
                    if unit:
                        self.inspected_unit = unit
                        break
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

    def draw_grid_lines(self, screen):
        # Kratka tworzona przez literę G
        offset_x = -(self.camera_x % TILE_SIZE)
        offset_y = -(self.camera_y % TILE_SIZE)
        for x in range(0, SCREEN_WIDTH + TILE_SIZE, TILE_SIZE):
            pygame.draw.line(screen, (50, 50, 50), (x + offset_x, 0), (x + offset_x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT + TILE_SIZE, TILE_SIZE):
            pygame.draw.line(screen, (50, 50, 50), (0, y + offset_y), (SCREEN_WIDTH, y + offset_y))

    def can_build_trap(self, x, y):
        # gdzie można budować pułapkę
        if not (0 <= y < len(self.map) and 0 <= x < len(self.map[0])): return False
        terrain = self.map[y][x]
        # Blokada: l (las), g (niskie góry), G (wysokie góry), W (woda)
        if terrain in ["l", "g", "#", "&","S","x","B","b", "G", "W"]: return False
        # Nie budujemy na budynkach (duże litery) ani innych pułapkach
        if terrain == "X" or (terrain.isupper() and terrain not in ["P"]): return False
        return True           
          
    def draw_road_arrows(self, screen):
        # strzałki budowniczego 
        if not (getattr(self, 'road_build_mode', False) and self.selected_unit):
            return

        u = self.selected_unit
        # Możliwe kierunki: góra, dół, lewo, prawo (można dodać skosy jeśli chcesz)
        directions = [(0, -1, "↑"), (0, 1, "↓"), (-1, 0, "←"), (1, 0, "→")]
        
        for dx, dy, symbol in directions:
            tx, ty = u.x + dx, u.y + dy
            
            # Sprawdzamy czy pole w ogóle istnieje na mapie i czy można tam wejść/budować
            if self.can_build_road(tx, ty):
                pos_x = tx * TILE_SIZE - self.camera_x
                pos_y = ty * TILE_SIZE - self.camera_y
                
                # Rysujemy półprzezroczyste tło strzałki
                rect = pygame.Rect(pos_x + 4, pos_y + 4, 24, 24)
                pygame.draw.rect(screen, (255, 255, 255, 150), rect) # Biały z alfą
                
                # Rysujemy symbol strzałki
                txt = self.font.render(symbol, True, (0, 0, 0))
                screen.blit(txt, (pos_x + 10, pos_y + 5))
    
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

                    #wwwww