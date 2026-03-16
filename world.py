import main
from unit import Unit, UNIT_STATS
from castle import Castle, UNIT_REQUIREMENTS
from player import Player
from map_loader import load_map, load_fac_objects
import pygame
from castle import BUILDINGS
from castle import BUILDING_TYPES
import sys

TILE_SIZE = 32
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800
# Rozmiar Twojej logicznej mapy (listy w self.map)
MAP_WIDTH = 100 
MAP_HEIGHT = 100

TERRAIN_TYPES = {
    "#": {"name": "kult", "color": (139, 69, 19)},
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
        # Pobieramy szerokość (w) i wysokość (h) aktualnego okna
        w = pygame.display.get_surface().get_width()
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 24)
        self.font_small = pygame.font.SysFont(None, 20) # 20 to rozmiar, możesz go zmienić
        self.modal_font = pygame.font.SysFont(None, 32)
        self.btn_font = pygame.font.SysFont(None, 28, bold=True)
        # ... Twoje istniejące zmienne (map, units itp.) ...
        self.camera_x = 0
        self.camera_y = 0

        # 1. NAJPIERW przygotuj wszystkie puste zmienne
        self.map = []
        self.units = []
        self.castles = []
        self.castle_locations = []
        self.objects = None
        self.peasant_groups = []
        self.gold_transports = []
        self.players = []
        self.selected_units = []
        self.screen = "map"
        self.selected_castle = None
        self.selected_garrison_unit = None
        self.turn = 1
        self.current_player = 0
        self.selected_unit = None
        self.destroyed = False
        self.owner = None
        # 2. DOPIERO TERAZ ładuj dane z plików (Nie zostaną nadpisane!)
        self.map = self.load_map("final_map1.txt")
        self.load_castles_from_fac("0.FAC")

        # 3. Reszta Twoich przycisków...
        self.garrison_button = pygame.Rect(40, 140, 160, 40)# na podstawie danych z FAC
        self.koszary_button = None
        self.exit_castle_button = pygame.Rect(40, 200, 160, 40)
        #koszary przyciski
        self.heal_button = pygame.Rect(460, 600, 100, 40)
        self.train_button = pygame.Rect(660, 600, 100, 40)
        self.recruit_button = pygame.Rect(260, 600, 100, 40)
        self.selected_unit_type = None
        self.menu_button = pygame.Rect(860, 40, 140, 40)
        self.menu_rects = {}
        self.build_rects = {}
        self.build_clicked = {}
        self.next_turn_button = pygame.Rect(820, 20, 180, 40)
        self.menu_open = False
        self.build_open = False
        #dwór
        self.victories = 0
        self.defeats = 0
        self.court_button = pygame.Rect(40, 140, 160, 40)
        self.exit_button = pygame.Rect(20, 20, 120, 50)
        self.prison_slots = [PrisonSlot(), PrisonSlot(), PrisonSlot()]
        self.unit_scroll = 0
        self.selected_recruit_units =None
        self.peasant_button = pygame.Rect(0, 0, 180, 45)
        self.send_peasants_amount = 0
        self.send_gold_amount = 0
        # PEASANTS + -
        self.peasants_plus_button = pygame.Rect(0, 0, 40, 40)
        self.peasants_minus_button = pygame.Rect(0, 0, 40, 40)
       # TAX + -
        self.tax_plus_button = pygame.Rect(0, 0, 40, 40)
        self.tax_minus_button = pygame.Rect(0, 0, 40, 40)
        # CASTLE SCROLL
        self.castle_up_button = pygame.Rect(0, 0, 40, 40)
        self.castle_down_button = pygame.Rect(0, 0, 40, 40)
        # GOLD + -
        self.gold_plus_button = pygame.Rect(0, 0, 40, 40)
        self.gold_minus_button = pygame.Rect(0, 0, 40, 40)
        # SEND
        self.send_button = pygame.Rect(0, 0, 160, 45)
        # BACK działa
        self.back_button = pygame.Rect(90, 600, 100, 40)
        self.selected_patent_index = None
        self.castle_list_offset = 0
        self.castle_scroll_up = pygame.Rect(0,0,40,40)
        self.castle_scroll_down = pygame.Rect(0,0,40,40)
        self.recruitment_unit_types = list(UNIT_STATS.keys())
        self.selected_unit_type = None
        self.unit_list_rects = []
        self.recruitment_scroll = 0
        self.visible_recruitment_count = 5
        self.patent_rects = []
        self.scroll_up_button = pygame.Rect(380, 80, 40, 60)
        self.scroll_down_button = pygame.Rect(380, 150, 40, 60)
        self.forge_button = None
        self.workshop_button = None
        self.hospital_button = None
        self.school_button = None
        # niszczenie zamku
        self.demolish_confirm = False
        self.button_send_army = pygame.Rect(860, 600, 100, 40)
        self.demolish_button = None
        # Tworzymy puste prostokąty, żeby collidepoint miał na czym pracować
        self.demolish_yes = pygame.Rect(0, 0, 0, 0)
        self.demolish_no = pygame.Rect(0, 0, 0, 0)
        self.camera_x = 0
        self.camera_y = 0
        # 3. PRZYCISKI (Recty i logika STARTU)
        self.info_button = pygame.Rect(120, 590, 100, 30)
        self.back_button = pygame.Rect(40, 630, 100, 30)
        self.buy_patent_button = pygame.Rect(160, 630, 140, 30)
        self.remove_patent_button = pygame.Rect(w - 230, 590, 100, 30)
        self.start_prod_button = pygame.Rect(w - 300, 630, 120, 30)
        self.stop_prod_button = pygame.Rect(w - 160, 630, 120, 30)
        self.scroll_up_button = pygame.Rect(260, 80, 40, 40)
        self.scroll_down_button = pygame.Rect(260, 200, 40, 40)
            # Definiujemy 3 przyciski na górze
        self.btn_system = pygame.Rect(10, 0, 100, 40)
        self.btn_mapa = pygame.Rect(115, 0, 100, 40)
        # Twój zwój z "koniec tury" - dopasuj X do szerokości ekranu
        self.next_turn_button = pygame.Rect(700, 0, 200, 45) 
        # Bardzo wąski pasek na samej górze - tylko on "wywołuje" menu
        self.top_ui_trigger_area = pygame.Rect(0, 0, 1024, 10) 
        # Obszar, który utrzymuje menu widoczne (cała wysokość przycisków)
        # Dzięki temu menu nie zniknie, gdy będziesz chciał kliknąć przycisk
        self.top_ui_full_area = pygame.Rect(0, 0, 1024, 55) 
        self.show_top_ui = False
        # Definicje opcji menu
        self.menu_options = {
            "System": ["Misja", "Poddanie się", "Zapisz grę", "Wczytaj grę", "Opcje", "Koniec"],
            "Mapa": ["Wszystko", "Budynki", "Jednostki", "Nic"]
        }
        # Stan: które menu jest otwarte (None, "system" lub "mapa")
        self.active_dropdown = None
        # Wysokość pojedynczej opcji w menu
        self.option_height = 35
        #RYSOWANIE
        self.icon_training = pygame.image.load("assets/swords.png").convert_alpha()
        # Przeskaluj ją, żeby pasowała do slotu (np. 32x32 piksele)
        self.icon_training = pygame.transform.scale(self.icon_training, (32, 32))
        # Definiujemy bazową pozycję panelu (np. dolny prawy róg)
        panel_x = 800
        panel_y = 640
        self.action_buttons = []
        # Tworzymy 6 przycisków w siatce 2x3
        for row in range(2):
            for col in range(3):
                rect = pygame.Rect(panel_x + col * 65, panel_y + row * 55, 70, 70)
                self.action_buttons.append(rect)
        self.build_menu_open = False  # Flaga: czy menu budowania jest otwarte?
        #dolny prawy panel na mapie 
        self.ui_panel_rect = pygame.Rect(720, 610, 304, 158) # Przykładowy panel
        # DODAJ TO:
        self.constructions = [] # Lista słowników: {"x": x, "y": y, "progress": 0, "owner": owner}
        self.show_grid = False  # Domyślnie siatka jest wyłączona
        self.traps = []
        self.active_projects = {} # Słownik: {(x, y): dane_budowy}
        self.tower_release_button = pygame.Rect(320, 430, 120, 40) # Dopasuj wymiary
        self.tower_back_button = pygame.Rect(560, 430, 120, 40)
        self.inspected_unit = None  # To naprawi AttributeError

    def update(self):
            keys = pygame.key.get_pressed()
            moving = False
            speed = 8  # Prędkość przesuwu (musi być dzielnikiem TILE_SIZE, np. 32/8=4)

            # Obsługa płynnego ruchu
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

    # DOCIĄGANIE (Snapping): Jeśli nie trzymasz klawiszy, wyrównaj do TILE_SIZE
            if not moving:
                self.camera_x = round(self.camera_x / 32) * 32 # Zakładając TILE_SIZE = 32
                self.camera_y = round(self.camera_y / 32) * 32
    def load_map(self, filename):
            game_map = []
            try:
                with open(filename, 'r') as f:
                    # Czytamy każdą linię z final_map.txt i usuwamy znaki nowej linii
                    for line in f:
                        game_map.append(list(line.strip()))
                print(f"Mapa wczytana: {len(game_map)}x{len(game_map[0])}")
            except FileNotFoundError:
                # Jeśli pliku nie ma, tworzymy awaryjną trawę 100x100
                print("Błąd: Nie znaleziono final_map.txt! Tworzę pustą mapę.")
                game_map = [["l" for _ in range(100)] for _ in range(100)]
        
            return game_map

    def load(self, map_file, fac_file):
        self.map = self.load_map(map_file)
        # Zakładam, że load_fac_objects zwraca słownik z listami
        self.objects = load_fac_objects(fac_file)

        castle_places = self.objects.get("zamek_place", [])
        # Musisz wyciągnąć informację o tym, co jest zbudowane
        built_indices = self.objects.get("zbudowano_zamek", [0, 1]) # Domyślnie 0 i 1

        self.castles = []
        self.castle_locations = []

        for i, (x, y) in enumerate(castle_places):
            # SPRAWDZAMY: czy ten indeks (i) jest na liście zbudowanych?
            if i in built_indices:
                owner = self.players[i] if i < len(self.players) else None
                # Tworzymy prawdziwy zamek (używamy x i y bezpośrednio, jeśli FAC ma kafelki)
                c = Castle(x, y, owner) 
                c.gold = 20000
                self.castles.append(c)
            else:
                # To jest tylko miejsce na budowę - dodajemy do osobnej listy
                self.castle_locations.append((x, y))

        # JEDNOSTKI STARTOWE (tylko przy prawdziwych zamkach)
        for c in self.castles:
            if c.owner:
                self.add_unit(Unit("lekka piechota", c.x, c.y + 2, c.owner))

        print(f"Zbudowano zamków: {len(self.castles)}")
        print(f"Miejsc pod budowę: {len(self.castle_locations)}")

    def add_player(self, player):
        self.players.append(player)

    def add_unit(self, unit):
        self.units.append(unit)
        if unit.owner:
            unit.owner.units.append(unit)

    def next_turn(self):
        print("CASTLES:", [type(c) for c in self.castles])

        if not self.players:
            return

        self.turn += 1
        self.current_player = (self.current_player + 1) % len(self.players)
        self.reset_units()

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

        # --- LOGIKA BUDOWANIA (TUTAJ BYŁY BŁĘDY) ---
        finished = []
        # Tworzymy kopię kluczy do iteracji
        for pos, project in list(self.active_projects.items()):
            project["remaining"] -= 1
            print(f"Budowa {project['type']} na {pos}: pozostało {project['remaining']} tur.")
            
            if project["remaining"] <= 0:
                from castle import Castle
                
                # 1. Tworzymy obiekt budynku
                new_building = Castle(pos[0], pos[1], project["owner"], building_type=project["type"])
                
                # 2. Jeśli był budowniczy, dodaj go do garnizonu
                if project.get("builder"):
                    new_building.garrison.append(project["builder"])
                
                # 3. Dodaj do listy zamków świata
                self.castles.append(new_building)
                
                # 4. AKTUALIZACJA MAPY: Zamień 'P' na symbol budynku
                # Załóżmy: 'C' dla Zamku/Twierdzy, 'S' dla Strażnicy (dopasuj do swoich symboli)
                if project["type"] == "Strażnica":
                    self.map[pos[1]][pos[0]] = "S" 
                else:
                    self.map[pos[1]][pos[0]] = "C"
                    # Jeśli zamek jest 2x2, musisz oznaczyć sąsiednie kafle, jeśli Twój system tego wymaga
                
                # !!! KLUCZOWA LINIA: Dodaj do listy do usunięcia !!!
                finished.append(pos)
                print(f"SUKCES: Postawiono {project['type']} na {pos}!")

        # Usuwamy zakończone projekty ze słownika aktywnych
        for pos in finished:
            if pos in self.active_projects:
                del self.active_projects[pos]

        # 1. Zamykamy wszystkie listy rozwijane (To co widać na screenie)
        self.active_dropdown = None 
        
        # 2. Zamykamy menu budowania na mapie (dolny panel)
        self.build_menu_open = False 
        
        # 3. Odznaczamy zamek i jednostki
        self.selected_castle = None
        self.selected_unit = None
        
        # 4. Resetujemy interfejs góry
        self.show_top_ui = False
        
        # 5. Wymuszamy powrót na mapę, jeśli spacja została kliknięta np. wewnątrz zamku
        self.screen = "map"

    def move_unit(self, unit, dx, dy):
        if unit.move_points <= 0:
            return

        nx = unit.x + dx
        ny = unit.y + dy

        # 1. Granice mapy
        if not (0 <= nx < len(self.map[0]) and 0 <= ny < len(self.map)):
            return

        # ===== LOGIKA WEJŚCIA DO ZAMKU =====
        for castle in self.castles:
            if castle.x <= nx <= castle.x + 1 and castle.y <= ny <= castle.y + 1:
                
                if castle.destroyed:
                    print("DEBUG: To są ruiny.")
                    return

                # 1. Sprawdzamy, czy gracz może wejść (tylko właściciel)
                    print(f"DEBUG: Właściciel zamku: {castle.owner}, Właściciel jednostki: {u.owner}")
                if castle.owner == unit.owner:
                    print("DEBUG: TO MÓJ ZAMEK!")
                else:
                    print("DEBUG: TO OBCA TWIERDZA!")
                    # 2. Szukamy wolnego slotu (None) w liście garnizonu
                    added_to_garrison = False
                    for i in range(len(castle.garrison)):
                        if castle.garrison[i] is None:
                            # Dodajemy jednostkę do garnizonu
                            castle.garrison[i] = unit
                            
                            # Usuwamy jednostkę z mapy (z listy jednostek gracza)
                            if unit in unit.owner.units:
                                unit.owner.units.remove(unit)
                            
                            self.selected_unit = None # Odznaczamy, bo już jej nie ma na mapie
                            print(f"SUKCES: {unit.type} wszedł do garnizonu zamku.")
                            added_to_garrison = True
                            break
                    
                    if not added_to_garrison:
                        print("BŁĄD: Garnizon jest pełny! Jednostka zostaje przed bramą.")
                        # Tutaj możesz pozwolić jednostce stanąć na polu zamku, ale nie "znikać"
                    
                    else:
                        print("DEBUG: To zamek innego gracza. (Tu może być logika ataku/oblężenia)")
                        # Jeśli planujesz walkę, tu wywołasz np. self.start_battle(unit, castle)

                    return # Znaleźliśmy zamek, wychodzimy z pętli

        # 4. ===== NORMALNY RUCH =====
        # Sprawdzamy czy teren pozwala na przejście
        if self.map[ny][nx] in [".", "l", "p", "$","_","g"]:
            unit.x = nx
            unit.y = ny
            unit.move_points -= 1
        else:
            print(f"BLOKADA! Na polu ({nx}, {ny}) jest znak: '{self.map[ny][nx]}'")
    def reset_units(self):
        for u in self.units:
            if u.x < 0:
                continue
            u.move_points = 5

    def select_unit(self, x, y):
        for u in self.units:
            if u.x == x and u.y == y:
                if u.owner == self.players[self.current_player]:
                    self.selected_unit = u
                    print("Wybrano jednostkę")
                    return
                else:
                    print("To nie jest twoja jednostka")
                    return

        print("Brak jednostki na tym polu")
        print("Tura gracza:", self.players[self.current_player].name)

    def move_selected(self, dx, dy):
        if not self.selected_unit:
            return
        
        u = self.selected_unit
        if u.move_points <= 0:
            print("Brak punktów ruchu")
            return

        nx, ny = u.x + dx, u.y + dy

        # 1. Sprawdzenie granic mapy
        if not (0 <= nx < len(self.map[0]) and 0 <= ny < len(self.map)):
            return

        # 2. Logika wejścia do zamku (Używamy Twojej nowej, sprawdzonej metody)
        for castle in self.castles:
            # Sprawdzamy obszar 2x2 zamku
            if castle.x <= nx <= castle.x + 1 and castle.y <= ny <= castle.y + 1:
                if castle.destroyed:
                    print("Ruiny zamku — nie można wejść")
                    return
            # Wewnątrz pętli for castle in self.castles:
            if castle.x <= nx <= castle.x + 1 and castle.y <= ny <= castle.y + 1:
                # SPRAWDZAMY CZY TO JEST CEL RUCHU (Ostatni krok)
                # Jeśli jednostka ma zaplanowaną ścieżkę, a to nie jest jej koniec - BLOKUJEMY
                if getattr(u, 'planned_path', []) and (nx, ny) != u.planned_path[-1]:
                    print("Zamek blokuje drogę — musisz go obejść!")
                    return # To sprawi, że zamek będzie przeszkodą dla pathfindingu    
                    
                print(f"Jednostka {u.type} wchodzi do zamku na {castle.x}, {castle.y}")
                
                # Przejęcie, jeśli wrogi
                if castle.owner != u.owner:
                    castle.owner = u.owner
                    castle.garrison = [None] * 12 # Zakładając stałą wielkość garnizonu
                    print("Zamek przejęty!")

                # Próba wejścia do garnizonu
                for i in range(len(castle.garrison)):
                    if castle.garrison[i] is None:
                        castle.garrison[i] = u
                        if u in self.units: self.units.remove(u)
                        u.move_points -= 1
                        self.selected_unit = None
                        return
                
                print("Garnizon pełny!")
                return # Nie pozwalamy wejść "na" zamek, jeśli nie mieści się w środku

        # 3. Blokada terenu (Góry/Woda) - sprawdzamy tylko jeśli to nie zamek
        if self.map[ny][nx] != ".":
            print("Nie można wejść na to pole")
            return

        # 4. Interakcja z innymi obiektami na mapie (Walka / Chłopi / Złoto)
        
        # Inne jednostki (Walka)
        for other in self.units:
            if other.x == nx and other.y == ny:
                if other.owner != u.owner:
                    print("Atak na jednostkę!")
                    self.units.remove(other) # Uproszczona walka
                else:
                    print("Pole zajęte")
                    return

        # Chłopi
        for group in self.peasant_groups[:]: # [:] robimy kopię, by móc usuwać podczas pętli
            if group.x == nx and group.y == ny:
                if group.owner != u.owner:
                    # Na razie army_size = 1, docelowo Twoja logika siły armii
                    u.carried_peasants += group.amount
                    self.peasant_groups.remove(group)
                    print("Chłopi dołączyli do armii")

        # Złoto
        for t in self.gold_transports[:]:
            if t.x == nx and t.y == ny:
                if t.owner != u.owner:
                    u.carried_gold += t.gold
                    self.gold_transports.remove(t)
                    print("Złoto przejęte")

        # 5. Finalizacja ruchu (Zwykłe pole)
        u.x, u.y = nx, ny
        u.move_points -= 1
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

    def handle_events(self):
        for event in pygame.event.get():
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

            # --- 3. WCIŚNIĘCIE MYSZY (CLICK / HOLD START) ---
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                
                # A. Scrollowanie w rekrutacji (button 4 i 5)
                if event.button in [4, 5] and self.screen == "recruitment":
                    self.handle_recruitment_scroll(event)
                    continue

                # B. Lewy przycisk - INSPEKCJA (Trzymanie)
                if event.button == 3: # Prawy przycisk
                    if self.screen == "garrison":
                        # Ta funkcja (którą już masz) ustawi self.inspected_unit
                        self.check_unit_info(mx, my)

                # C. Wykonanie standardowego kliknięcia (Zaznaczanie itp.)
                self.handle_mouse_click(mx, my, event.button)

            # --- 4. PUSZCZENIE MYSZY (HOLD END) ---
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    # Puszczasz przycisk - statystyki znikają
                    self.inspected_unit = None
                
    def handle_mouse_click(self, mx, my, button):
        if button != 1: return

        # --- 1. EKRAN UNIT_INFO (Zamykanie kliknięciem) ---
        if self.screen == "unit_info":
            self.screen = "recruitment"
            return

        # --- 2. EKRAN REKRUTACJI (Z koszar/rekrutacji wracamy do GARNIZONU) ---
        elif self.screen == "recruitment":
            if hasattr(self, 'back_button') and self.back_button.collidepoint(mx, my):
                self.screen = "garrison" # <--- ZMIANA: Koszary -> Garnizon
                return
            self.handle_recruitment_click(mx, my)
            return

        # --- 3. EKRANY "WRACAJĄCE DO ZAMKU" ---
        elif self.screen in ["court", "hospital", "workshop", "forge", "peasants", "school", "garrison"]:
            
            # A. Wspólny przycisk BACK dla wszystkich w tej grupie
            if hasattr(self, 'back_button') and self.back_button.collidepoint(mx, my):
                self.screen = "castle"
                return
            # B. LOGIKA DLA STRAŻNICY (dodajemy to tutaj)
            if self.screen == "straznica":
                # Sprawdzamy przycisk "Zmień Nazwę" (jeśli go masz)
                if hasattr(self, 'POWRÓT') and self.tower_back_button.collidepoint(mx, my):
                    print("DEBUG: Kliknięto Powrót w Strażnicy")
                    # Tu Twoja logika zmiany nazwy
                # DESTROY: Niszczymy budynek i wracamy na mapę
                elif hasattr(self, 'destroy_button') and self.destroy_button.collidepoint(mx, my):
                    if self.destroy_straznica(self.selected_castle): 
                        self.screen = "map"
                        self.selected_castle = None
                    return
            # C. Specyficzna logika tylko dla GARNIZONU (Release i Destroy)
            if self.screen == "garrison":
                # RELEASE: Usuwamy jednostkę, ale zostajemy w menu
                if hasattr(self, 'release_button') and self.release_button.collidepoint(mx, my):
                    self.release_garrison() 
                    return 

                # Reszta kliknięć w garnizonie (np. wybór slotów)
                self.handle_garrison_click(mx, my, button)
                return

            # C. Specyficzna logika tylko dla CHŁOPÓW
            elif self.screen == "peasants":
                self.handle_peasants_click(mx, my)
                return
                
            return # Zatrzymujemy kliknięcie, żeby nie przebiło na mapę
        # --- 4. EKRANY "WRACAJĄCE NA MAPĘ" ---
        elif self.screen == "castle":
            # A. Obsługa okna potwierdzenia zburzenia (Musi być pierwsze!)
            if getattr(self, 'demolish_confirm', False):
                win_w, win_h = 320, 160
                win_x, win_y = (1024//2)-(win_w//2), (768//2)-(win_h//2)
                btn_yes = pygame.Rect(win_x + 40, win_y + 85, 90, 45)
                btn_no = pygame.Rect(win_x + 190, win_y + 85, 90, 45)

                if btn_yes.collidepoint(mx, my):
                    self.demolish_castle(self.selected_castle)
                    self.screen = "map"; self.selected_castle = None; self.demolish_confirm = False
                    return
                if btn_no.collidepoint(mx, my):
                    self.demolish_confirm = False
                    return
                return 
            
            if getattr(self, 'build_open', False):
                for b_name, rect in self.build_rects.items():
                    if rect.collidepoint(mx, my):
                        # WYWOŁUJEMY TYLKO TO:
                        if self.selected_castle.build(b_name):
                            # Jeśli się udało (limit nie był przekroczony i było złoto)
                            self.menu_open = False
                            self.build_open = False
                            print(f"Zbudowano i zaciągnięto limit tury dla: {b_name}")
                        return # Blokuje kliknięcia pod menu

            
            # C. Przejścia do budynków (Recruitment, Forge itp.)
            if getattr(self, 'recruit_button', None) and self.recruit_button.collidepoint(mx, my):
                self.selected_patent_index = None; self.screen = "recruitment"; return

            for b in ['forge', 'workshop', 'hospital', 'school', 'court', 'peasants']:
                btn = getattr(self, f'{b}_button', None)
                if btn and btn.collidepoint(mx, my):
                    self.screen = b; return
            
            # --- NOWA SEKCJA: KLIKNIĘCIA W GŁÓWNE MENU ZAMKU ---
            if getattr(self, 'menu_open', False):
                # Sprawdzamy przycisk MENU (żeby go zamknąć kliknięciem)
                if self.menu_button.collidepoint(mx, my):
                    self.menu_open = False
                    return

                # Sprawdzamy opcje: ZBURZ, MURY itp.
                for opt_name, rect in self.menu_rects.items(): # Upewnij się, że używasz poprawnej nazwy słownika
                    if rect.collidepoint(mx, my):
                        if opt_name == "ZBURZ ZAMEK":
                            print("DEBUG: Potwierdzam zburzenie")
                            self.demolish_confirm = True
                            self.menu_open = False
                            return
                        elif opt_name == "ROZBUDUJ MURY":
                            print("DEBUG: Rozbudowa murów")
                            # Tu logika murów
                            return
            # Jeśli nie kliknięto w żadne UI, sprawdź kliknięcie w budynki na grafice zamku
            self.handle_castle_click(mx, my)
            return
        
        # --- 6. EKRAN MAPY ---
        elif self.screen == "map":
            if self.handle_ui_click(mx, my):
                return

            grid_x = (mx + self.camera_x) // TILE_SIZE
            grid_y = (my + self.camera_y) // TILE_SIZE

            # Pułapka X
            if 0 <= grid_y < len(self.map) and 0 <= grid_x < len(self.map[0]):
                if self.map[grid_y][grid_x] == "X":
                    self.screen = "trap_info"; self.active_trap_pos = (grid_x, grid_y)
                    return

            self.active_dropdown = None
            if self.handle_building_logic(mx, my, grid_x, grid_y): return
            if self.handle_castle_entry(mx, my): return
            self.handle_map_click(mx, my, button)
                
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
            self.inspected_unit = None # Kliknięcie lewym zamyka okienko statystyk
            if unit is None:
                return

            if unit in self.selected_units:
                self.selected_units.remove(unit)
                print("Odznaczono:", unit.type)
            else:
                if len(self.selected_units) < 10:
                    self.selected_units.append(unit)
                    print("Zaznaczono:", unit.type)

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
        # BACK
        self.back_button = pygame.Rect(70, 600, 100, 40)
        pygame.draw.rect(screen, (120, 80, 80), self.back_button)
        screen.blit(font.render("BACK", True, (255,255,255)), (80,610))

        # RECRUIT
        if "Koszary" in castle.buildings:
            pygame.draw.rect(screen, (240, 120, 20), self.recruit_button)
            screen.blit(font.render("RECRUIT", True, (255,255,255)), (270,610))

        # HEAL
        if "hospital" in castle.buildings:
            pygame.draw.rect(screen, (80, 160, 80), self.heal_button)
            screen.blit(font.render("HEAL", True, (255,255,255)), (490,610))

        # TRAIN
        if "school" in castle.buildings:
            pygame.draw.rect(screen, (160, 160, 80), self.train_button)
            screen.blit(font.render("TRAIN", True, (255,255,255)), (700,610))
        
        # RELEASE
        pygame.draw.rect(screen, (160,120,60), self.button_send_army)
        screen.blit(font.render("RELEASE", True, (255,255,255)), (890,610))

       # --- OKNO STATYSTYK (TWOJA TABELKA) ---
        if self.inspected_unit:
            # Rysujemy ją w stałym miejscu, np. po prawej stronie (x=550, y=250)
            # aby nie zasłaniała slotów garnizonu
            self.draw_unit_stats_table(
                screen, 
                550, 
                250, 
                self.inspected_unit.type, 
                self.inspected_unit
            )

    def draw_map(self, screen):
        # --- 1. USTAWIENIA I KAMERA ---
        tiles_on_screen_x = SCREEN_WIDTH // TILE_SIZE + 1
        tiles_on_screen_y = SCREEN_HEIGHT // TILE_SIZE + 1
        start_x = self.camera_x // TILE_SIZE
        start_y = self.camera_y // TILE_SIZE

        # --- 2. RYSOWANIE TERENU (TŁA) I OBIEKTÓW NA TERENIE ---
        for y in range(max(0, start_y), min(len(self.map), start_y + tiles_on_screen_y)):
            for x in range(max(0, start_x), min(len(self.map[0]), start_x + tiles_on_screen_x)):
                pos_x = (x * TILE_SIZE) - self.camera_x
                pos_y = (y * TILE_SIZE) - self.camera_y
                
                tile_type = self.map[y][x] 
                
                # A. Rysowanie koloru podłoża
                terrain = TERRAIN_TYPES.get(tile_type, TERRAIN_TYPES["."])
                pygame.draw.rect(screen, terrain["color"], (pos_x, pos_y, TILE_SIZE, TILE_SIZE))
                # W pętli rysującej teren:
                if tile_type == "#":
                    # FUNDAMENTY POD ZAMEK - Ramka 2x2 (szara/biała)
                    pygame.draw.rect(screen, (255, 255, 255), (pos_x, pos_y, TILE_SIZE, TILE_SIZE), 2)
                    label = self.font.render("Z", True, (255, 255, 255))
                    screen.blit(label, (pos_x + 5, pos_y + 2))

                elif tile_type == "&":
                    # ŚWIĄTYNIA - Inny kolor (np. żółty lub niebieski)
                    pygame.draw.rect(screen, (255, 215, 0), (pos_x, pos_y, TILE_SIZE, TILE_SIZE), 2)
                    label = self.font.render("†", True, (255, 215, 0))
                    screen.blit(label, (pos_x + 8, pos_y + 2))

                # B. RYSOWANIE KRZYŻYKA PUŁAPKI (Musi być wewnątrz tej pętli!)
                if tile_type == "X":
                    trap_color = (200, 0, 0)
                    offset = 6
                    # Linia \
                    pygame.draw.line(screen, trap_color, 
                                    (pos_x + offset, pos_y + offset), 
                                    (pos_x + TILE_SIZE - offset, pos_y + TILE_SIZE - offset), 3)
                    # Linia /
                    pygame.draw.line(screen, trap_color, 
                                    (pos_x + TILE_SIZE - offset, pos_y + offset), 
                                    (pos_x + offset, pos_y + TILE_SIZE - offset), 3)

                # C. RYSOWANIE PLACU BUDOWY (P) - dla Strażnic 1x1
                elif tile_type == "P":
                    pygame.draw.rect(screen, (255, 255, 0), (pos_x, pos_y, TILE_SIZE, TILE_SIZE), 2)
                    # Mały napis "P" na środku kafelka
                    p_txt = self.font.render("P", True, (255, 255, 0))
                    screen.blit(p_txt, (pos_x + 10, pos_y + 5))

        # --- 2.5 SIATKA (Rysujemy ją RAZ po narysowaniu całego terenu) ---
        if self.show_grid:
            for x_grid in range(0, SCREEN_WIDTH + TILE_SIZE, TILE_SIZE):
                # Dopasowanie do kamery dla idealnego wyrównania
                offset_x = -(self.camera_x % TILE_SIZE)
                pygame.draw.line(screen, (50, 50, 50), (x_grid + offset_x, 0), (x_grid + offset_x, SCREEN_HEIGHT))
            for y_grid in range(0, SCREEN_HEIGHT + TILE_SIZE, TILE_SIZE):
                offset_y = -(self.camera_y % TILE_SIZE)
                pygame.draw.line(screen, (50, 50, 50), (0, y_grid + offset_y), (SCREEN_WIDTH, y_grid + offset_y))

        # --- 3. RYSOWANIE PLACÓW BUDOWY (castle_locations) ---
        for px, py in self.castle_locations:
            rect = pygame.Rect((px * TILE_SIZE) - self.camera_x, (py * TILE_SIZE) - self.camera_y, 64, 64)
            pygame.draw.rect(screen, (150, 150, 150), rect, 2) 

        # --- 4. RYSOWANIE ZAMKÓW (DYNAMICZNY ROZMIAR) ---
        for castle in self.castles:
            # KLUCZOWA ZMIANA: Sprawdzamy typ. Strażnica = 1 kafel, reszta = 2 kafle (64px)
            if castle.building_type == "Strażnica":
                draw_size = TILE_SIZE
            else:
                draw_size = TILE_SIZE * 2 # Czyli Twoje 64
                
            rect = pygame.Rect(
                (castle.x * TILE_SIZE) - self.camera_x, 
                (castle.y * TILE_SIZE) - self.camera_y, 
                draw_size, 
                draw_size
            )
            
            if getattr(castle, 'destroyed', False):
                # Rysowanie zniszczonego budynku
                pygame.draw.rect(screen, (180, 0, 0), rect)
                pygame.draw.rect(screen, (50, 0, 0), rect, 2)
                pygame.draw.line(screen, (100, 0, 0), rect.topleft, rect.bottomright, 2)
                pygame.draw.line(screen, (100, 0, 0), rect.topright, rect.bottomleft, 2)
            else:
                # Kolor właściciela lub neutralny
                castle_color = castle.owner.color if castle.owner else (100, 100, 100)
                
                # Rysujemy główny blok budynku
                pygame.draw.rect(screen, castle_color, rect) 
                pygame.draw.rect(screen, (0, 0, 0), rect, 2) # Obwódka
                
                # Litera typu budynku (S, T, Z)
                label = castle.building_type[0].upper()
                txt = self.font.render(label, True, (255, 255, 255))
                screen.blit(txt, (rect.x + 5, rect.y + 2))
                
                # Detal wizualny (daszek) - dopasowany do rozmiaru budynku
                roof_width = draw_size - 20
                if roof_width > 0:
                    pygame.draw.rect(screen, (255, 255, 255), (rect.x + 10, rect.y + 10, roof_width, 5), 0)

        # --- 5. RYSOWANIE JEDNOSTEK (Tile-based counts) ---
        tile_units = {}
        for player in self.players:
            for u in player.units:
                if u.x >= 0 and u.y >= 0:
                    key = (u.x, u.y)
                    tile_units[key] = tile_units.get(key, 0) + 1

        unit_font = pygame.font.SysFont(None, 24)

        for u in self.units:
            # Oblicz pozycję na ekranie
            px = int(u.x) * TILE_SIZE - self.camera_x
            py = int(u.y) * TILE_SIZE - self.camera_y
            
            # 1. KOLOR PODSTAWOWY (Zawsze od właściciela)
            # Jeśli to budowniczy, możemy mu dać specyficzny kolor tła, 
            # ale lepiej zostawić kolor gracza, żeby było wiadomo czyj on jest.
            owner_color = u.owner.color if u.owner else (200, 200, 200)
            
            # Rysujemy kwadracik jednostki
            pygame.draw.rect(screen, owner_color, (px + 4, py + 4, 24, 24))
            
            # 2. WYRÓŻNIENIE DLA BUDOWNICZEGO (Napis BU)
            # 1. NAJPIERW: Definiujemy, co ma być napisane (label)
            # Możesz użyć automatu (dwie pierwsze litery typu jednostki)
            label = u.type[:2].upper() 

            # 2. POTEM: Tworzymy powierzchnię tekstu (tutaj miałeś błąd)
            txt_surface = unit_font.render(label, True, (255, 255, 255))

            # 3. NA KOŃCU: Rysujemy na ekranie
            text_rect = txt_surface.get_rect(center=(px + 16, py + 16))
            screen.blit(txt_surface, text_rect)
                
                # Małe czarne tło pod literami, żeby były czytelne
            pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(2, 2))
            screen.blit(txt_surface, text_rect)

            # 3. OZNACZENIE ZAZNACZENIA (Biała ramka DOOKOŁA)
            if u == self.selected_unit:

                # Rysujemy tylko ramkę (ostatni parametr '2' to grubość linii)
                pygame.draw.rect(screen, (255, 255, 255), (px + 2, py + 2, 28, 28), 2)     
            
        # --- 6. KROPKI DROGI ---
        # Sprawdzamy nie tylko czy jest wybrana, ale czy w ogóle istnieje jeszcze w grze (self.units)
        if self.selected_unit and self.selected_unit in self.units:
            if getattr(self.selected_unit, 'planned_path', None):
                self.draw_path_dots(screen, self.selected_unit, self.selected_unit.planned_path)

    def draw_castle(self, screen):
        castle = self.selected_castle
        if not castle: return

        # --- NOWA LOGIKA DLA STRAŻNICY ---
        if castle.building_type == "Strażnica":
            self.draw_garrison_only(screen) # Zaraz zdefiniujemy tę funkcję niżej
            return # Kończymy tutaj, nie rysujemy reszty bajerów zamkowych

        # --- RESZTA DLA ZAMKU / TWIERDZY ---
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        screen.fill((60, 50, 40))  

        # Ustawienie przycisków
        self.peasant_button.x = screen_width - 200
        self.peasant_button.y = screen_height - 70
        self.koszary_button = None  

        font = pygame.font.SysFont(None, 28)
        title = font.render(f"{castle.building_type.upper()}", True, (255, 255, 255))
        screen.blit(title, (40, 40))

        # Teraz poprawny warunek dla chłopów
        if castle.building_type == "Zamek":
            self.draw_button(screen, "CHŁOPI", self.peasant_button)

        # GARNIZON — zawsze
        self.garrison_button = pygame.Rect(80, 630, 160, 40)
        pygame.draw.rect(screen, (80, 80, 160), self.garrison_button)
        screen.blit(font.render("Garrison", True, (255,255,255)),
                    (self.garrison_button.x + 10, self.garrison_button.y + 10))

        # KUŹNIA — tylko jeśli forge zbudowany
        if self.selected_castle and "forge" in self.selected_castle.buildings:
            self.forge_button = pygame.Rect(750, 500, 160, 40)
            pygame.draw.rect(screen, (100, 100, 100), self.forge_button)
            screen.blit(font.render("forge", True, (255,255,255)),
                        (self.forge_button.x + 20, self.forge_button.y + 10))
        else:
            self.forge_button = None

        # WARSZTAT — tylko jeśli workshop zbudowany
        if self.selected_castle and "workshop" in self.selected_castle.buildings:
            self.workshop_button = pygame.Rect(290, 480, 160, 40)
            pygame.draw.rect(screen, (90, 90, 140), self.workshop_button)
            screen.blit(font.render("workshop", True, (255,255,255)),
                        (self.workshop_button.x + 15, self.workshop_button.y + 10))
        else:
            self.workshop_button = None

        # SZPITAL — tylko jeśli hospital zbudowany
        if self.selected_castle and "hospital" in self.selected_castle.buildings:
            self.hospital_button = pygame.Rect(110, 350, 160, 40)
            pygame.draw.rect(screen, (200, 60, 60), self.hospital_button)
            screen.blit(font.render("SZPITAL", True, (255,255,255)),
                        (self.hospital_button.x + 15, self.hospital_button.y + 10))
        else:
            self.hospital_button = None

        #SZKOŁA — tylko jeśli Szkoła zbudowany
        if self.selected_castle and "school" in self.selected_castle.buildings:
            self.school_button = pygame.Rect(830, 250, 160, 40)
            pygame.draw.rect(screen, (90, 90, 240), self.school_button)
            screen.blit(font.render("school", True, (255,255,255)),
                        (self.school_button.x + 15, self.school_button.y + 10))
        else:
            self.school_button = None

    # --- BUTTON: BACK ---
        self.back_button = pygame.Rect(40, 700, 160, 40)
        pygame.draw.rect(screen, (120, 80, 80), self.back_button)
        screen.blit(font.render("BACK", True, (255,255,255)), (50,710))
        mx, my = pygame.mouse.get_pos()

        # 1. Sprawdzamy otwarcie (hover na główny przycisk)
        if self.menu_button.collidepoint(mx, my):
            self.menu_open = True

        # 2. Rysujemy menu (jeśli jest otwarte)
        if getattr(self, 'menu_open', False):
            self.draw_castle_menu(screen, mx, my)

        # 3. Rysujemy główny przycisk MENU (użyj draw_button dla lepszego stylu)
        self.draw_button(screen, "MENU", self.menu_button)

        # 4. LOGIKA ZAMYKANIA (Dopracowana)
        mouse_over_ui = False

        if self.menu_button.collidepoint(mx, my):
            mouse_over_ui = True

        # Sprawdzamy główne opcje (Buduj, Zburz...)
        for rect in self.menu_rects.values():
            if rect.collidepoint(mx, my):
                mouse_over_ui = True

        # Sprawdzamy submenu budynków (Koszary, Szpital...)
        for rect in self.build_rects.values():
            if rect.collidepoint(mx, my):
                mouse_over_ui = True
        
        # DODATKOWO: margines bezpieczeństwa (niewidzialny prostokąt łączący menu z submenu)
        # Zapobiega zamykaniu menu, gdy przesuwasz mysz w lewo do budynków
        bridge_rect = pygame.Rect(self.menu_button.x - 20, self.menu_button.y, 30, 200)
        if bridge_rect.collidepoint(mx, my):
            mouse_over_ui = True

        # Zamykamy tylko jeśli myszka faktycznie zjechała z całego UI
        if not mouse_over_ui:
            self.menu_open = False
            self.build_open = False

    # --- BUTTON: COURT ---
        self.court_button = pygame.Rect(420, 100, 160, 40)
        pygame.draw.rect(screen, (20, 80, 80), self.court_button)
        screen.blit(font.render("DWÓR", True, (255,225,255)), (470,110))
    
    def draw_button(self, screen, text, rect):
        # Sprawdzamy hover dla zmiany koloru
        mx, my = pygame.mouse.get_pos()
        is_hovered = rect.collidepoint(mx, my)
        
        # Kolory szare (stonowane)
        base_color = (120, 120, 120) if is_hovered else (90, 90, 90)
        border_color = (200, 200, 200) # Jasnoszara, elegancka ramka
        
        # Rysowanie przycisku
        pygame.draw.rect(screen, base_color, rect)
        pygame.draw.rect(screen, border_color, rect, 1) # Cienka ramka 1px
        
        # Renderowanie tekstu (mniejsza czcionka 20, żeby nie wychodziła poza ramy)
        small_font = pygame.font.SysFont(None, 20)
        txt_surface = small_font.render(text, True, (255, 255, 255))
        
        # Idealne centrowanie wewnątrz rect
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
        for btn, col in [(self.info_button, (120,120,120)), (self.back_button, (140,80,80)), 
                        (self.buy_patent_button, (80,140,80)), (self.remove_patent_button, (120,80,80)),
                        (self.stop_prod_button, (140,80,80))]:
            pygame.draw.rect(screen, col, btn)
        
        pygame.draw.rect(screen, (80, 140, 80) if can_start else (60, 60, 60), self.start_prod_button)

        # Napisy na przyciskach
        screen.blit(font.render("INFO", True, (255, 255, 255)), (150, 595))
        screen.blit(font.render("BACK", True, (255, 255, 255)), (65, 635))
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
        
        # 3. MOVES i DODATKOWE (np. EXP dla jednostek lub ATC dla rekrutacji)
        moves_val = get_v('moves', 'move_points') # Sprawdza 'moves' w słowniku lub 'move_points' w obiekcie
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

        self.back_button.bottomleft = (20, h - 20)
        pygame.draw.rect(screen,(140,80,80),self.back_button)
        screen.blit(font.render("BACK",True,(255,255,255)),self.back_button.move(20,8))

    def draw_court(self, screen):
        screen.fill((30, 0, 0))

        font = pygame.font.SysFont(None, 24)

        # ===== BACK BUTTON ====
        self.back_button = pygame.Rect(20, 120, 120, 40)
        pygame.draw.rect(screen, (140, 80, 80), self.back_button)
        screen.blit(font.render("BACK", True, (255,255,255)),
                    (self.back_button.x + 25, self.back_button.y + 10))

        # ===== RESZTA =====
        self.draw_court_players_header(screen)
        self.draw_court_stats(screen)
        self.draw_queen_panel(screen)
        self.draw_prison_sections(screen)

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

    def draw_court(self, screen):
        screen.fill((30, 30, 30)) # Tło

        # Rysowanie wszystkich paneli
        self.draw_court_players_header(screen)
        self.draw_court_stats(screen)
        self.draw_queen_panel(screen)
        self.draw_prison_sections(screen)

        self.back_button = pygame.Rect(10, 130, 100, 40) # Dopasowałem rozmiar do screena
        pygame.draw.rect(screen, (120, 80, 80), self.back_button)
        # Tekst "BACK" wyśrodkowany w tym prostokącie
        draw_text(screen, "BACK", self.back_button.x + 25, self.back_button.y + 12)

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
        # Zawsze czyścimy tło na początku klatki
        screen.fill((30, 30, 30))
        # 1. LOGIKA EKRANU MAPY ORAZ PUŁAPKI
        if self.screen == "map" or self.screen == "trap_info":
            # Najpierw rysujemy podkład: teren, budynki i place budowy (litery P)
            self.draw_map(screen)

            # --- TUTAJ WPISZ PĘTLĘ DLA JEDNOSTEK ---
            for unit in self.units:
                # Sprawdzamy, czy jednostka nie jest ukryta (np. przez start_building)
                if getattr(unit, 'visible', True):
                    unit.draw(screen)
            # --------------------------------------

            # Na samym końcu rysujemy interfejs, aby zawsze był na wierzchu
            self.draw_top_bar(screen)
            self.draw_ui(screen)

            if self.screen == "trap_info":
                self.draw_trap_popup(screen)
                
        # 2. EKRAN ZAMKU (Główny)
        elif self.screen == "castle":
            self.draw_castle(screen)
        
            # TYLKO TUTAJ ma prawo pojawić się to brązowe menu
            if getattr(self, "menu_open", False):
                mx, my = pygame.mouse.get_pos()
                self.draw_castle_menu(screen, mx, my)
        # 3. EKRAN KOSZAR (Garrison)
        elif self.screen == "garrison":
            self.draw_garrison(screen) # Rysuje te duże ramki ze zdjęcia 1
            
        elif self.screen == "Strażnica": # <--- Jeśli tak nazwałeś to w kliknięciu
            self.draw_garrison_only(screen)

        elif self.screen == "recruitment":
            self.draw_recruitment(screen) # Dodaj to, jeśli masz taką metodę

        # 4. LOGIKA DWORU I CHŁOPÓW
        elif self.screen == "court":
            self.draw_court(screen)
        
        elif self.screen == "peasants":
            self.draw_peasants(screen) # Dodaj to, jeśli masz taką metodę

        # 5. NOWE EKRANY BUDYNKÓW (Tego brakowało!)
        elif self.screen == "forge":
            self.draw_forge(screen)
            
        elif self.screen == "workshop":
            self.draw_workshop(screen)
            
        elif self.screen == "hospital":
            self.draw_hospital(screen)
            
        elif self.screen == "school":
            self.draw_school(screen)
            
        elif self.screen == "unit_info":
            self.draw_unit_info(screen)

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
            if c.x == x and c.y == y:
                self.selected_castle = c
                print("Wybrano zamek:", x, y)
                return

        self.selected_castle = None
        return

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
        start_x = 100
        start_y = 120

        cols = 6
        rows = 2

        slot_w = 100
        slot_h = 180

        offset_x = 130
        offset_y = 210

        for row in range(rows):
            for col in range(cols):
                index = row * cols + col

                x = start_x + col * offset_x
                y = start_y + row * offset_y

                rect = pygame.Rect(x, y, slot_w, slot_h)

                if rect.collidepoint(mx, my):
                    return index

        return None
    
    def get_unit_at(self, x, y):
        for unit in self.units:
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
        if hasattr(self, 'back_button') and self.back_button.collidepoint(mx, my):
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
        tile_x = (mx + self.camera_x) // 32
        tile_y = (my + self.camera_y) // 32

        # --- KROK 1: Jeśli mamy zaznaczoną jednostkę (PRIORYTET RUCHU) ---
        if self.selected_unit:
            u = self.selected_unit
            
            # A. Czy klikamy drugi raz w to samo miejsce (Potwierdzenie ruchu)?
            if tile_x == getattr(u, 'target_x', None) and tile_y == getattr(u, 'target_y', None):
                print("DEBUG: Ruch potwierdzony!")
                u.move_along_path(self)
                
                for castle in self.castles:
                    if castle.x <= u.x <= castle.x + 1 and castle.y <= u.y <= castle.y + 1:
                        if castle.owner == u.owner:
                            # SPRAWDZENIE: Czy lista garnizonu istnieje?
                            if not hasattr(castle, 'garrison'):
                                castle.garrison = []
                            
                            added = False
                            for i in range(len(castle.garrison)):
                                if castle.garrison[i] is None:
                                    castle.garrison[i] = u
                                    added = True
                                    print(f"DEBUG: Jednostka {u.type} wstawiona do slotu {i}")
                                    break
                            
                            if added:
                                if u in u.owner.units:
                                    u.owner.units.remove(u)
                                self.selected_unit = None
                                return
                            else:
                                print("DEBUG: Brak wolnego miejsca w garnizonie (wszystkie sloty zajęte)!")
                            if u in u.owner.units:
                                u.owner.units.remove(u) # Usuwamy z mapy świata
                            
                            self.selected_unit = None
                            return

            # B. Czy klikamy w nowym miejscu (Wyznaczanie trasy)?
            # Nawet jeśli klikasz w zamek, teraz tylko wyznaczamy kropki!
            u.target_x = tile_x
            u.target_y = tile_y
            u.planned_path = self.find_path(u, tile_x, tile_y)
            print(f"DEBUG: Zaplanowano trasę do {tile_x}, {tile_y}")
            return # WAŻNE: return przerywa funkcję, więc kod zamku poniżej się nie wykona!

        # --- KROK 2: Jeśli NIE mamy jednostki (TRYB MAPY / ZAZNACZANIE) ---
        
        # A. Najpierw sprawdź czy kliknięto w zamek (by go otworzyć)
        for castle in self.castles:
            if castle.x <= tile_x <= castle.x + 1 and castle.y <= tile_y <= castle.y + 1:
                if not castle.destroyed:
                    self.selected_castle = castle
                    self.screen = "castle"
                    print("DEBUG: Otwarto menu zamku")
                    return

        # B. Sprawdź czy kliknięto w nową jednostkę (by ją zaznaczyć)
        for player in self.players:
            for unit in player.units:
                if unit.x == tile_x and unit.y == tile_y:
                    if unit.owner == self.players[self.current_player]:
                        self.selected_unit = unit
                        unit.target_x = None # <-- DODAJ TO
                        unit.target_y = None # <-- DODAJ TO
                        unit.planned_path = [] # <-- DODAJ TO
                        print("DEBUG: Zaznaczono jednostkę i wyczyszczono stare cele")
                        return
        # --- PRAWY PRZYCISK: Statystyki jednostki ---
        if button == 3:
            target_unit = self.get_unit_at(grid_x, grid_y)
            if target_unit:
                self.inspected_unit = target_unit
                self.screen = "unit_info"
                print(f"Podgląd jednostki: {target_unit.name}")
                return


    def handle_castle_click(self, mx, my):

        if not self.selected_castle:
            return

        # BACK
        if self.back_button.collidepoint(mx, my):
            self.screen = "map"
            self.selected_castle = None
            return

        # GARRISON
        if self.garrison_button and self.garrison_button.collidepoint(mx, my):
            self.screen = "garrison"
            return

        # FORGE
        if self.forge_button and self.forge_button.collidepoint(mx, my):
            self.screen = "forge"
            return

        # RECRUITMENT
        if (
            "Koszary" in self.selected_castle.buildings
            and self.koszary_button
            and self.koszary_button.collidepoint(mx, my)
        ):
            self.screen = "recruitment"
            self.recruitment_open = True
            self.recruitment_scroll = -2  # USTAWIAMY TAK SAMO JAK WYŻEJ
            self.selected_unit_type = 0   # USTAWIAMY TAK SAMO
            self.selected_patent_index = None
            return

        # PEASANTS
        if self.peasant_button.collidepoint(mx, my):
            self.screen = "peasants"
            return

        # COURT
        if self.court_button.collidepoint(mx, my):
            self.screen = "court"
            return

        # BUILD MENU
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

        # BACK
        if self.back_button.collidepoint(mx, my):
            self.screen = "castle"
            return

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
    def draw_forge(self, screen):
        screen.fill((40, 70, 70))  # tło "kamień"

        font_title = pygame.font.SysFont(None, 48)
        font_text = pygame.font.SysFont(None, 24)

        # PANEL
        panel = pygame.Rect(120, 80, 760, 420)
        pygame.draw.rect(screen, (120, 90, 60), panel)
        pygame.draw.rect(screen, (200, 170, 90), panel, 6)

        # TYTUŁ
        title = font_title.render("forge", True, (255, 220, 120))
        screen.blit(title, (panel.centerx - title.get_width() // 2, panel.y - 40))

        # TEKSt
        text_lines = [
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

        y = panel.y + 30
        for line in text_lines:
            txt = font_text.render(line, True, (255, 255, 255))
            screen.blit(txt, (panel.x + 30, y))
            y += 28

        # BACK BUTTON
        self.back_button = pygame.Rect(40, 520, 120, 50)
        pygame.draw.rect(screen, (120, 80, 80), self.back_button)
        screen.blit(font_text.render("BACK", True, (255,255,255)), (60, 535))

    def draw_workshop(self, screen):
        screen.fill((60, 60, 80))

        font_title = pygame.font.SysFont(None, 48)
        font_text = pygame.font.SysFont(None, 24)

        panel = pygame.Rect(120, 80, 760, 420)
        pygame.draw.rect(screen, (100, 100, 130), panel)
        pygame.draw.rect(screen, (180, 180, 220), panel, 6)

        title = font_title.render("workshop", True, (220, 220, 255))
        screen.blit(title, (panel.centerx - title.get_width() // 2, panel.y - 40))

        lines = [
            "Pracują tu znakomici rzemieślnicy ze starego kraju.",
            "Dzięki ich kunsztowi staniesz się posiadaczem łuków, kusz,",
            "oszczepów oraz strzał niespotykanych wcześniej w tej części",
            "kontynentu. Daje Ci to możliwość rozpoczęcia produkcji",
            "oddziałów rażących wroga na dystans a także rozmaitych",
            "machin.",
        ]

        y = panel.y + 30
        for line in lines:
            txt = font_text.render(line, True, (255, 255, 255))
            screen.blit(txt, (panel.x + 30, y))
            y += 28

        # BACK BUTTON
        self.back_button = pygame.Rect(40, 520, 120, 50)
        pygame.draw.rect(screen, (120, 80, 80), self.back_button)
        screen.blit(font_text.render("BACK", True, (255,255,255)), (60, 535))
        
    def draw_hospital(self, screen):
        screen.fill((60, 60, 80))

        font_title = pygame.font.SysFont(None, 48)
        font_text = pygame.font.SysFont(None, 24)

        panel = pygame.Rect(120, 80, 760, 420)
        pygame.draw.rect(screen, (100, 100, 130), panel)
        pygame.draw.rect(screen, (180, 180, 220), panel, 6)

        title = font_title.render("Szpital", True, (220, 220, 255))
        screen.blit(title, (panel.centerx - title.get_width() // 2, panel.y - 40))

        lines = [
            "Zapach rozcieranych ziół da się odczuć we wszystkich zakamarkach Twojego dziedzinca.",
            "Powstające tu specyfiki i mikstury robione są według bardzo starych receptur,",
            "znanych tylko niektórym kapłanom.",
            "Owe lekarstwa pomogą odzyskać Twoim rycerzom pełnię sił, gojąc w szybkim tempie", 
            "nawet najcięższe rany.",
            "Ponadto troskliwi kapłani roztoczyli swą opiekę nad mieszkańcami dworskiej wsi.",
            "Przez to szalejące plagi i zarazy rzadko zagoszczą w Twych progach i będą mniej dotkliwe.",
        ]

        y = panel.y + 30
        for line in lines:
            txt = font_text.render(line, True, (255, 255, 255))
            screen.blit(txt, (panel.x + 30, y))
            y += 28

        # BACK BUTTON
        self.back_button = pygame.Rect(40, 520, 120, 50)
        pygame.draw.rect(screen, (120, 80, 80), self.back_button)
        screen.blit(font_text.render("BACK", True, (255,255,255)), (60, 535))

    def draw_school(self, screen):
        screen.fill((60, 60, 80))

        font_title = pygame.font.SysFont(None, 48)
        font_text = pygame.font.SysFont(None, 24)

        panel = pygame.Rect(120, 80, 760, 420)
        pygame.draw.rect(screen, (100, 100, 130), panel)
        pygame.draw.rect(screen, (180, 180, 220), panel, 6)

        title = font_title.render("school", True, (220, 220, 255))
        screen.blit(title, (panel.centerx - title.get_width() // 2, panel.y - 40))

        lines = [
            "Zapach rozcieranych ziół da się odczuć we wszystkich zakamarkach Twojego dziedzinca.",
            "Powstające tu specyfiki i mikstury robione są według bardzo starych receptur,",
            "znanych tylko niektórym kapłanom.",
            "Owe lekarstwa pomogą odzyskać Twoim rycerzom pełnię sił, gojąc w szybkim tempie", 
            "nawet najcięższe rany.",
            "Ponadto troskliwi kapłani roztoczyli swą opiekę nad mieszkańcami dworskiej wsi.",
            "Przez to szalejące plagi i zarazy rzadko zagoszczą w Twych progach i będą mniej dotkliwe.",
        ]

        y = panel.y + 30
        for line in lines:
            txt = font_text.render(line, True, (255, 255, 255))
            screen.blit(txt, (panel.x + 30, y))
            y += 28

        # BACK BUTTON
        self.back_button = pygame.Rect(40, 520, 120, 50)
        pygame.draw.rect(screen, (120, 80, 80), self.back_button)
        screen.blit(font_text.render("BACK", True, (255,255,255)), (60, 535))

        return None

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
        """Rysuje czarne i czerwone kropki trasy z uwzględnieniem kamery."""
        TILE_SIZE = 32
        
        for i, (px, py) in enumerate(path):
            # Obliczamy pozycję na ekranie (współrzędne siatki * rozmiar - kamera)
            # Dodajemy połowę kafelka (+16), aby kropka była na środku
            dot_x = (px * TILE_SIZE) + (TILE_SIZE // 2) - self.camera_x
            dot_y = (py * TILE_SIZE) + (TILE_SIZE // 2) - self.camera_y
            
            # Sprawdzamy, czy kropka znajduje się w widocznym obszarze (używając stałych okna)
            if -20 < dot_x < SCREEN_WIDTH + 20 and -20 < dot_y < SCREEN_HEIGHT + 20:
                
                # Logika kolorów: czarny dla zasięgu w tej turze, czerwony dla dalszych
                if i < unit.move_points:
                    color = (0, 0, 0)       # Czarna kropka - zasięg teraz
                else:
                    color = (255, 0, 0)     # Czerwona kropka - przyszłe tury
                    
                # Rysowanie kropki (promień 4) z czarną obwódką dla lepszej widoczności
                pygame.draw.circle(screen, (255, 255, 255), (dot_x, dot_y), 5) # Białe tło kropki
                pygame.draw.circle(screen, color, (dot_x, dot_y), 4)

    def find_path(self, unit, dest_x, dest_y):
        print(f"Szukam drogi do: {dest_x}, {dest_y}. Szerokość mapy w pamięci: {len(self.map[0])}")
        queue = [(unit.x, unit.y, [])]
        visited = {(unit.x, unit.y)}
        
        while queue:
            (cx, cy, path) = queue.pop(0)
            if (cx, cy) == (dest_x, dest_y):
                return path # Zwraca listę krotek (x, y)
                
            # Poprawna pętla sąsiadów:
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) not in visited and self.is_walkable(nx, ny):
                    visited.add((nx, ny))
                    queue.append((nx, ny, path + [(nx, ny)]))
        return []
    
    def is_walkable(self, x, y):
        if self.map is None: return False
        
        map_height = len(self.map)
        map_width = len(self.map[0]) if map_height > 0 else 0
        
        # 1. Sprawdzenie granic i terenu
        if not (0 <= x < map_width and 0 <= y < map_height):
            return False
        if self.map[y][x] not in [".", "_", "p", "$", "l","g"]:
            return False

        # 2. Sprawdzenie jednostek
        for player in self.players:
            for u in player.units:
                if u.x == x and u.y == y:
                    return False

        # --- 3. NOWOŚĆ: Sprawdzenie zamków (Blokada przechodzenia) ---
        # NOWA BLOKADA: Sprawdzamy czy x, y to pole któregokolwiek zamku
        for castle in self.castles:
            # Sprawdzamy cały obszar 2x2 zamku
            if castle.x <= x <= castle.x + 1 and castle.y <= y <= castle.y + 1:
                return False # To pole jest "ścianą" dla pathfindingu
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
    
    def handle_ui_click(self, mx, my):
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
        # Jeśli nie masz zaznaczonej jednostki, zignoruj blokadę y >= 610.
        # Pozwoli to klikać mapę na samym dole ekranu, gdy po prostu chodzisz kamerą.
        if self.selected_unit is None:
            return False 

        # Jeśli my >= 610 i KTOŚ jest zaznaczony, to znaczy, że panel tam JEST.
        if my >= 610:
            # 1. Sprawdzamy sloty armii (Twoje 10 prostokątów)
            if hasattr(self, 'army_slot_rects'):
                for i, rect in enumerate(self.army_slot_rects):
                    if rect.collidepoint(mx, my):
                        self.handle_army_slot_click(i)
                        return True

            # 2. Sprawdzamy standardowe przyciski akcji (BUILD, ATK, itp.)
            for i, rect in enumerate(self.action_buttons):
                if rect.collidepoint(mx, my):
                    self.handle_action_button_click(i)
                    return True
            
            # 3. Kliknięcie w brązowe tło panelu (pomiędzy przyciskami) 
            # też blokuje mapę, żeby jednostka pod panelem nie dostała rozkazu ruchu.
            return True 

        return False
    def draw_ui(self, screen):

        # 2. DOLNY PANEL (Dla wybranej jednostki)
        u = self.selected_unit
        if u:
            panel_rect = pygame.Rect(0, 610, 1024, 158)
            pygame.draw.rect(screen, (30, 20, 10), panel_rect) 
            pygame.draw.rect(screen, (100, 80, 60), panel_rect, 2)

            if not hasattr(self, 'army_slot_rects'):
                self.army_slot_rects = [pygame.Rect(10 + i * 75, 620, 70, 140) for i in range(10)]

            display_units = getattr(u, 'garrison', [u] + [None] * 9)



            for i in range(10):
                rect = self.army_slot_rects[i]
                pygame.draw.rect(screen, (60, 40, 30), rect)
                pygame.draw.rect(screen, (150, 130, 100), rect, 1)

                if i < len(display_units) and display_units[i] is not None:
                    unit = display_units[i]
                    name_txt = self.font_small.render(str(unit.type), True, (255, 255, 255))
                    count = getattr(unit, 'count', 1)
                    count_txt = self.font_small.render(str(count), True, (255, 255, 0))
                    screen.blit(name_txt, (rect.x + 5, rect.y + 120))
                    screen.blit(count_txt, (rect.x + 5, rect.y + 100))

        # 3. PRZYCISKI AKCJI (ATK, BUILD itp.)
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
            if army.move_points >= 6:
                army.move_points -= 6
                self.map[grid_y][grid_x] = "R"
                print("Wybudowano drogę!")
                self.build_menu_open = False
            return

        # 2. PUŁAPKA (Indeks 1)
        if button_index == 1: 
            self.map[grid_y][grid_x] = "X"
            # Jeśli cała armia to tylko Budowniczy, usuwamy ją. 
            # Jeśli to duża armia, usuwamy tylko jednostkę Budowniczego z garnizonu.
            self.remove_unit_or_builder(army, builder)
            self.selected_unit = None
            self.build_menu_open = False
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
            
            # Rozpoczynamy budowę (przekazujemy budowniczego jako wykonawcę)
            self.start_building(grid_x, grid_y, b_type, builder)
            
            # Sprawdzamy czy projekt ruszył
            if (grid_x, grid_y) in self.active_projects:
                # Budowniczy "znika" w budowie (usuwamy go z garnizonu armii lub z mapy)
                self.remove_unit_or_builder(army, builder)
                
                # Cała armia staje się stacjonarna (straż budowy)
                army.move_points = 0 
                
                self.selected_unit = None
                self.build_menu_open = False
                print(f"Armia {army.type} rozpoczęła budowę {b_type} i pilnuje placu budowy.")

    def remove_unit_or_builder(self, army, builder):
        """Pomocnik do usuwania budowniczego z mapy lub z wnętrza armii."""
        if army == builder: # Budowniczy był pojedynczą jednostką na mapie
            if army in self.units: self.units.remove(army)
        else: # Budowniczy był częścią większej armii
            for i in range(len(army.garrison)):
                if army.garrison[i] == builder:
                    army.garrison[i] = None
                    break

    def spawn_test_builder(self):
        if not self.players:
            return
        
        # Wybieramy pierwszego gracza i nazywamy go 'current_p'
        current_p = self.players[0] 
        
        from unit import Unit
        # Tworzymy jednostkę i przypisujemy jej 'current_p'
        new_builder = Unit("Budowniczy", 15, 15, current_p)
        
        # Dodajemy do systemu
        self.add_unit(new_builder)
        
        # Teraz ta linia zadziała, bo 'current_p' już istnieje!
        print(f"DEBUG: Stworzono budowniczego dla: {current_p.name}")

    def add_unit_to_game(self, unit):
        """Dodaje jednostkę do świata i do listy jej właściciela."""
        # 1. Dodaj do głównej listy (do rysowania)
        if unit not in self.units:
            self.units.append(unit)
        
        # 2. Dodaj do listy gracza (do zaznaczania i sterowania)
        if unit.owner and unit not in unit.owner.units:
            unit.owner.units.append(unit)
            print(f"DEBUG: Jednostka {unit.type} przypisana do gracza {unit.owner.name}")

    def spawn_unit(self, unit_type, x, y, owner):
        from unit import Unit
        new_unit = Unit(unit_type, x, y, owner)
        self.add_unit_to_game(new_unit)
        print(f"Zrekrutowano: {unit_type} na pozycji {x}, {y}")

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
    
    def start_building(self, x, y, b_type, builder_unit=None):
        if b_type not in BUILDING_TYPES: return
        config = BUILDING_TYPES[b_type]
        
        ix, iy = int(x), int(y)
        current_tile = self.map[iy][ix]
        anchor_x, anchor_y = ix, iy
        found_foundation = False

        # 1. LOGIKA SZUKANIA FUNDAMENTU / MIEJSCA
        if config.get("size") == 2:
            # Dla Zamku: sprawdzamy tylko pod nogami i 1 kafelek wokół, 
            # aby znaleźć lewy górny róg '#'
            for dx in [0, -1]:
                for dy in [0, -1]:
                    nx, ny = ix + dx, iy + dy
                    if 0 <= nx < len(self.map[0]) and 0 <= ny < len(self.map):
                        if self.map[ny][nx] == "#":
                            anchor_x, anchor_y = nx, ny
                            found_foundation = True
                            break
                if found_foundation: break

            if not found_foundation:
                print(f"Błąd: Zamek wymaga fundamentu (#). Pod nogami: {current_tile}")
                return
        else:
            # Dla Strażnicy (1x1): budujemy na trawie (.) lub pustyni (p)
            if current_tile in [".", "p"]:
                found_foundation = True
            else:
                print(f"Błąd: Tu nie można budować strażnicy (teren: {current_tile})")
                return

        # 2. SPRAWDZENIE CZY MIEJSCE WOLNE
        if (anchor_x, anchor_y) in self.active_projects:
            print("Tu już trwa budowa!")
            return

        # 3. UKRYWANIE BUDOWNICZEGO
        # Budowniczy "znika" z mapy na czas budowy
        if builder_unit:
            builder_unit.visible = False
            builder_unit.is_building = True

        # 4. TWORZENIE PROJEKTU
        self.active_projects[(anchor_x, anchor_y)] = {
            "type": b_type,
            "remaining": config["turns"],
            "owner": self.current_player,
            "pos": (anchor_x, anchor_y),
            "builder": builder_unit
        }
        
        # 5. ZMIANA MAPY NA SYMBOLE 'P' (Plac budowy)
        if config.get("size") == 2:
            # Zmieniamy kwadrat 2x2 na 'P', żeby budowniczy nie był widoczny,
            # a gracz widział, że coś powstaje.
            for i in range(2):
                for j in range(2):
                    self.map[anchor_y + i][anchor_x + j] = "P"
        else:
            self.map[anchor_y][anchor_x] = "P"

        print(f"Rozpoczęto budowę {b_type} na pozycji {anchor_x}, {anchor_y}. Budowniczy ukryty.")

    def process_construction(self):
        # Lista do usunięcia skończonych projektów
        finished = []
        for pos, project in self.active_projects.items():
            # Zamiast szukać na mapie, sprawdzamy czy projekt ma przypisanego budowniczego
            if project.get("builder") is not None:
                # Budowniczy jest "w środku", więc zawsze daje 1 punkt postępu
                project["remaining"] -= 1 
                print(f"Postęp {project['type']} na {pos}: -1 (Budowniczy w środku)")
            
            if project["remaining"] <= 0:
                finished.append(pos)
                
        # Finalizujemy i usuwamy
        for pos in finished:
            project = self.active_projects[pos]
            self.complete_building(project)
            del self.active_projects[pos]

    def count_builders_near(self, pos):
        px, py = pos
        # Szukamy budowniczych dokładnie na kafelku placu budowy
        return sum(1 for u in self.units if u.x == px and u.y == py and u.type.lower() == "budowniczy")
    
    def complete_building(self, project):
        # Pobieramy dane z projektu
        x, y = project["pos"]
        b_type = project["type"]
        print(f"DEBUG FINISH: Buduję typ: {b_type}") # <--- DODAJ TO
        owner = project["owner"]
        
        # 1. Tworzymy fizyczny obiekt w grze (Twój Castle)
        from castle import Castle # upewnij się, że ścieżka jest ok
        new_building = Castle(x, y, owner)
        
        # Przypisujemy mu cechy z naszej konfiguracji BUILDING_TYPES
        config = BUILDING_TYPES[b_type]
        new_building.building_type = b_type
        new_building.available_modules = config["modules"]
        new_building.garrison_limit = config["garrison_limit"]
        
        # Dodajemy do listy istniejących budynków
        self.castles.append(new_building)
        
        # 2. AKTUALIZACJA MAPY (Zmieniamy 'P' na symbol budynku)
        symbol = b_type[0] # 'Z' dla Zamku, 'T' dla Twierdzy, 'S' dla Strażnicy
        
        if config["size"] == 2:
            # Zajmuje 2x2 kafelki
            for i in range(2):
                for j in range(2):
                    if y+i < len(self.map) and x+j < len(self.map[0]):
                        self.map[y+i][x+j] = symbol
        else:
            # Strażnica: Zajmuje tylko 1 kafel
            self.map[y][x] = symbol

        print(f"!!! BUDOWA UKOŃCZONA: {b_type} na pozycji {x},{y} !!!")

        # 3. Wrzucenie budowniczego do garnizonu po zakończeniu
        builder_to_save = project.get("builder")
        if builder_to_save and new_building:
            new_building.add_to_garrison(builder_to_save)
            print(f"Budowniczy wszedł do garnizonu {b_type}")
    
    def handle_building_logic(self, mx, my, gx, gy):
        tile = self.map[gy][gx]
        builder = self.selected_unit

        if not builder or builder.type != "Budowniczy":
            return False

        # --- PRZYPADEK 1: Klikamy na FUNDAMENTY (#) ---
        if tile == "#":
            # Blokada: Nie pozwól budować Strażnicy na fundamentach
            if getattr(self, "building_mode", None) == "Tower":
                print("Błąd: Na fundamentach budujemy tylko Zamek lub Twierdzę!")
                return False
                
            # Jeśli jesteśmy na #, otwórz menu rozbudowy (Punkt 3 Twoich wymagań)
            print("Budowniczy na fundamentach - otwieram menu Zamku/Twierdzy.")
            self.show_foundation_menu(gx, gy) 
            self.building_mode = None 
            return True

        # --- PRZYPADEK 2: Klikamy na TRAWĘ (.) ---
        elif tile == ".":
            mode = getattr(self, "building_mode", None)
            
            # Pozwól tylko na Strażnicę
            if mode == "Tower":
                self.start_building(gx, gy, "Strażnica", builder)
                
                # Punkt 1: Budowniczy znika (wchodzi do środka)
                if builder in self.units: 
                    self.units.remove(builder)
                
                self.selected_unit = None
                self.building_mode = None
                return True
            
            # Blokada: Zamek/Twierdza wymagają # (to już masz w start_building, ale warto tu też mieć)
            elif mode in ["Zamek", "Twierdza"]:
                print("Błąd: Zamek i Twierdza wymagają fundamentów (#)!")
                return False
                    
        return False
            
        #elif mode == "Foundation":
            # Stawiamy fundamenty pod Zamek/Twierdzę
            #self.map[gy][gx] = "#"
            #print("Postawiono fundamenty (#)")
           # self.building_mode = None
            # Tutaj budowniczy NIE musi znikać, bo to postawienie kafelka, a nie budowa czasowa
            #return True
                
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

        for i in range(10):
            col = i % 5
            row = i // 5
            slot_rect = pygame.Rect(start_x + col * (slot_size + gap), 
                                    start_y + row * (slot_size + gap), 
                                    slot_size, slot_size)
            
            # Rysujemy slot
            pygame.draw.rect(screen, (50, 50, 60), slot_rect)
            pygame.draw.rect(screen, (100, 100, 120), slot_rect, 2)
            
            # Jeśli w slocie jest jednostka (zakładając, że masz listę castle.garrison)
            if hasattr(castle, 'garrison') and i < len(castle.garrison) and castle.garrison[i]:
                unit = castle.garrison[i]
                # Tutaj rysujesz mały symbol jednostki lub jej nazwę
                u_txt = font.render(unit.type[:3].upper(), True, (255, 255, 255))
                screen.blit(u_txt, (slot_rect.x + 10, slot_rect.y + 10))

        # Przycisk POWRÓT (już masz)
        self.back_button = pygame.Rect(screen.get_width()//2 - 250, 650, 160, 45)
        self.draw_button(screen, "POWRÓT", self.back_button)

        # Przycisk RELEASE
        self.release_button = pygame.Rect(screen.get_width()//2 - 80, 650, 160, 45)
        self.draw_button(screen, "RELEASE", self.release_button)

        
        # Przycisk ZNISZCZ
        self.destroy_button = pygame.Rect(screen.get_width()//2 + 90, 650, 160, 45)
        # Rysujemy na czerwono
        pygame.draw.rect(screen, (150, 0, 0), self.destroy_button)
        txt = font.render("ZNISZCZ", True, (255, 255, 255))
        screen.blit(txt, (self.destroy_button.centerx - txt.get_width()//2, 
                        self.destroy_button.centery - txt.get_height()//2))

    def process_active_builds(self):
        """Przetwarza postęp budowy wszystkich obiektów."""
        finished = []
        for pos, data in list(self.active_constructions.items()):
            data["work_done"] += len(data.get("builders", []))
            
            if data["work_done"] >= data["total_work_needed"]:
                # Tworzenie gotowego budynku
                from castle import Castle
                new_b = Castle(pos[0], pos[1], self.current_player, building_type=data["type"])
                self.castles.append(new_b)
                
                # Zmiana symbolu na mapie
                self.map[pos[1]][pos[0]] = "S" if data["type"] == "Strażnica" else "C"
                finished.append(pos)
                
        for pos in finished:
            del self.active_constructions[pos]    
    def check_straznica_click(self, mx, my):
        """Zwraca True, jeśli kliknięto w Strażnicę, i przełącza ekran."""
        for castle in self.castles:
            if getattr(castle, 'building_type', "") == "Strażnica":
                # Ścisły prostokąt 1x1
                rect = pygame.Rect(
                    (castle.x * TILE_SIZE) - self.camera_x,
                    (castle.y * TILE_SIZE) - self.camera_y,
                    TILE_SIZE, TILE_SIZE
                )
                if rect.collidepoint(mx, my) and not getattr(castle, 'destroyed', False):
                    self.selected_castle = castle
                    self.selected_unit = None
                    self.screen = "Strażnica"
                    print(f"DEBUG: Wejście do Strażnicy na {castle.x},{castle.y}")
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

    def draw_building_footer(self, screen):
        # Definiujemy pozycje przycisków raz dla całej gry
        self.back_button = pygame.Rect(100, 650, 150, 45)
        self.release_button = pygame.Rect(300, 650, 150, 45)
        self.destroy_button = pygame.Rect(500, 650, 150, 45)
        
        # Rysujemy je
        self.draw_button(screen, "POWRÓT", self.back_button)
        self.draw_button(screen, "Uwolnij", self.release_button)
        self.draw_button(screen, "Zburz", self.destroy_button)

    def release_selected_units(self):
        """
        Uniwersalna funkcja uwalniania jednostek. 
        Zastępuje execute_universal_release i stare release_selected_units.
        """
        # 1. Sprawdzamy co jest źródłem (Zamek czy Strażnica/Budynek)
        target = self.selected_castle or getattr(self, 'active_building', None)
        if not target or not self.selected_units:
            print("Błąd: Nic nie zaznaczono do wypuszczenia!")
            return

        # 2. Inteligentny podział na grupy (żeby Chłopi nie byli w jednej armii z Rycerzami)
        # To zapobiega błędom w logice ekonomii/walki
        chłopi_group = [u for u in self.selected_units if u.type == "Chłop"]
        złoto_group = [u for u in self.selected_units if u.type == "Złoto"]
        wojsko_group = [u for u in self.selected_units if u.type not in ["Chłop", "Złoto"]]

        # Tworzymy listę grup, które faktycznie nie są puste
        groups_to_spawn = [g for g in [chłopi_group, złoto_group, wojsko_group] if g]
        
        # 3. Szukanie miejsc (wykorzystujemy Twoją funkcję find_multiple_spawn_positions)
        # Jeśli jej nie masz, użyj pętli z directions z Twojego pierwszego kodu
        spawn_positions = self.find_multiple_spawn_positions(target, len(groups_to_spawn))

        from unit import Unit
        
        for idx, group in enumerate(groups_to_spawn):
            pos = spawn_positions[idx] if idx < len(spawn_positions) else None
            if not pos:
                print(f"Brak miejsca na mapie dla grupy {idx}!")
                continue
            
            nx, ny = pos
            # Nazwa armii: typ pierwszej jednostki w grupie
            army_type = group[0].type 

            # 4. TWORZENIE NOWEJ ARMII NA MAPIE
            new_army = Unit(army_type, nx, ny, target.owner)
            new_army.move_points = 50  # Standardowy ruch
            new_army.vision_range = 5  # Żeby widziała mapę
            new_army.garrison = [None] * 10 # Puste sloty w nowej armii

            # 5. PRZEKŁADANIE JEDNOSTEK (Z budynku do armii)
            for i, unit_to_move in enumerate(group):
                if i < 10: # Limit slotów w armii
                    new_army.garrison[i] = unit_to_move
                    
                    # Usuwamy z garnizonu źródłowego (zamku/strażnicy)
                    for slot_idx in range(len(target.garrison)):
                        if target.garrison[slot_idx] == unit_to_move:
                            target.garrison[slot_idx] = None
                            break

            # 6. REJESTRACJA W SYSTEMIE
            self.units.append(new_army)
            if target.owner:
                target.owner.units.append(new_army)

        # Czyścimy zaznaczenie po operacji
        self.selected_units.clear()
        
        # Opcjonalnie: self.screen = "map" jeśli chcesz wyjść, 
        # albo zostawiasz "garrison" żeby wypuszczać dalej.
        print("Ewakuacja zakończona sukcesem.")

    def find_multiple_spawn_positions(self, castle, num_groups):
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
                    if (nx, ny) not in occupied and self.map[ny][nx] in [".", "_", "p", "$","l","g"]:
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