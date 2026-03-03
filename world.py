from unit import Unit, UNIT_STATS
from castle import Castle, UNIT_REQUIREMENTS
from player import Player
from map_loader import load_map, load_fac_objects
import pygame
from castle import BUILDINGS
import sys
TILE_SIZE = 32
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800
# Rozmiar Twojej logicznej mapy (listy w self.map)
MAP_WIDTH = 100 
MAP_HEIGHT = 100

def draw_text(screen, text, x, y, color=(0, 0, 0)):
    font = pygame.font.SysFont(None, 24)
    img = font.render(str(text), True, color)
    screen.blit(img, (x, y))

def draw_button(screen, text, x, y, w, h):
    pygame.draw.rect(screen, (160,160,160), (x, y, w, h))
    pygame.draw.rect(screen, (0,0,0), (x, y, w, h), 2)
    draw_text(screen, text, x + 10, y + 5)

class PrisonSlot:
    def __init__(self, general=None):
        self.general = general
        self.turns_in_prison = 0

class World:
    def __init__(self):
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 24)
        self.modal_font = pygame.font.SysFont(None, 32)
        self.btn_font = pygame.font.SysFont(None, 28, bold=True)

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
        # System Budowania
        self.active_projects = {}  # Klucz: (x, y), Wartość: {type, remaining_work, owner}
        self.traps = []            # Lista pułapek na mapie
        self.build_menu_open = False
        # 2. DOPIERO TERAZ ładuj dane z plików (Nie zostaną nadpisane!)
        self.map = self.load_map("map.txt")
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
        # 4 PEASANTS + -
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
        # 5 BACK działa
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
        

            # 6 Definiujemy 3 przyciski na górze
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
        panel_x = 730
        panel_y = 620
        self.action_buttons = []
        # 7 Tworzymy 6 przycisków w siatce 2x3
        for row in range(2):
            for col in range(3):
                rect = pygame.Rect(panel_x + col * 65, panel_y + row * 55, 60, 50)
                self.action_buttons.append(rect)
        self.build_menu_open = False  # Flaga: czy menu budowania jest otwarte?
        #dolny prawy panel na mapie 
        self.ui_panel_rect = pygame.Rect(720, 610, 304, 158) # Przykładowy panel
        # DODAJ TO:
        self.spawn_test_builder()
        self.constructions = [] # Lista słowników: {"x": x, "y": y, "progress": 0, "owner": owner}
    def load_map(self, filename):
            game_map = []
            try:
                with open(filename, 'r') as f:
                    # Czytamy każdą linię z map.txt i usuwamy znaki nowej linii
                    for line in f:
                        game_map.append(list(line.strip()))
                print(f"Mapa wczytana: {len(game_map)}x{len(game_map[0])}")
            except FileNotFoundError:
                # Jeśli pliku nie ma, tworzymy awaryjną trawę 100x100
                print("Błąd: Nie znaleziono map.txt! Tworzę pustą mapę.")
                game_map = [["." for _ in range(100)] for _ in range(100)]
        
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
            if castle.destroyed:
                continue
            castle.next_turn()

        self.selected_unit = None
        self.selected_castle = None

        for castle in self.castles:
            if not castle.destroyed:
                castle.collect_taxes()
                
        # POPRAWKA DLA JEDNOSTEK
        for unit in self.units:
            # Sprawdzamy, czy typ jednostki istnieje w UNIT_STATS
            if unit.type in UNIT_STATS:
                # Jeśli używasz nazwy 'move_points', upewnij się, że w UNIT_STATS też tak jest
                # Jeśli w UNIT_STATS masz klucz "moves", użyj: UNIT_STATS[unit.type]["moves"]
                unit.move_points = UNIT_STATS[unit.type].get("moves", 5) 
            elif unit.type == "army":
                # Jeśli to grupa jednostek (armia), nadaj jej domyślny ruch
                unit.move_points = 5 
            else:
                print(f"Pominięto odnowienie ruchu dla nieznanego typu: {unit.type}")

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

        # 4. ===== NORMALNY RUCH (tylko na kafelku ".") =====
        # Sprawdzamy czy teren pozwala na przejście
                # Dodaj "R" (Road) do listy dozwolonych znaków
        if self.map[ny][nx] in [".", "0", " ", "$", "R"]: 
            unit.x = nx
            unit.y = ny
            unit.move_points -= 1
        else:
            # To powie Ci dokładnie, co blokuje Budowniczego
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

            elif event.type == pygame.KEYDOWN:
                # ... (Twój istniejący kod ESC i SPACE zostaje bez zmian) ...
                if event.key == pygame.K_ESCAPE:
                    if self.screen in ["recruitment", "garrison", "forge", "workshop", "hospital", "school", "peasants", "court"]:
                        self.screen = "castle"
                    elif self.screen == "castle":
                        self.screen = "map"
                    elif self.demolish_confirm:
                        self.demolish_confirm = False
                elif event.key == pygame.K_SPACE:
                    if self.selected_unit:
                        self.selected_unit = None
                    else:
                        self.next_turn()

            # --- MYSZKA ---
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                #--- 1. PRIORYTET: OKNO BURZENIA ---
                if getattr(self, 'demolish_confirm', False):
                    if self.demolish_yes.collidepoint(mx, my):
                        self.demolish_castle(self.selected_castle)
                        return
                    elif self.demolish_no.collidepoint(mx, my):
                        self.demolish_confirm = False
                        return
                    return

                # --- 2. PRIORYTET: INFO O JEDNOSTCE (Zamykanie) ---
                if self.screen == "unit_info":
                    self.screen = "map"
                    return

                # --- 3. OBSŁUGA PRAWY KLIK (INFO) ---
                if event.button == 3: # Prawy przycisk myszy
                    grid_x = (mx + self.camera_x) // TILE_SIZE
                    grid_y = (my + self.camera_y) // TILE_SIZE
                        
                    #get_unit_at to Twoja funkcja zwracająca jednostkę na danej pozycji
                    target_unit = self.get_unit_at(grid_x, grid_y)
                    if target_unit:
                        # Zapisujemy sformatowany tekst statystyk do zmiennej, którą narysujemy
                        self.unit_info_text = f"Jednostka: {target_unit.name}\nAtak: {target_unit.attack}\n..." # itd.
                        self.screen = "unit_info"
                        print(f"Otwarto podgląd dla: {target_unit.name}")
                    return
                        
                # --- 4. OBSŁUGA LEWY KLIK (ZAMEK / UI / MAPA) ---
                if event.button == 1:
                    if self.screen == "castle":
                        if hasattr(self, 'demolish_button') and self.demolish_button.collidepoint(mx, my):
                            self.demolish_confirm = True
                            return                        

                        # --- OBSŁUGA KLIKNIĘĆ W ZALEŻNOŚCI OD EKRANU ---
                        if self.screen == "map":
                            if self.handle_ui_click(mx, my):
                                return

                        # Przekazujemy resztę do handle_mouse_click
                    self.handle_mouse_click(mx, my, event.button)
                for i, rect in enumerate(self.action_buttons):
                    if rect.collidepoint(mx, my):
                        self.handle_action_button_click(i)
                        return True # Przechwycono kliknięcie, nie rób nic na mapie
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3: self.inspected_unit = None


            
                
    def handle_mouse_click(self, mx, my, button):
        # 1. EKRANY SPECJALNE (Garnizon i Rekrutacja - obsługa wielu przycisków)
        if self.screen == "garrison":
            self.handle_garrison_click(mx, my, button)
            return
            
        if self.screen == "recruitment":
            self.handle_recruitment_click(mx, my) 
            return

        # 2. EKRAN ZAMKU
        if self.screen == "castle":
            if button == 1:
                # A. NAJPIERW: Sprawdź okno potwierdzenia, jeśli jest otwarte
                if getattr(self, 'demolish_confirm', False):
                    win_w, win_h = 320, 160
                    win_x = (1024 // 2) - (win_w // 2)
                    win_y = (768 // 2) - (win_h // 2)
                    
                    btn_yes = pygame.Rect(win_x + 40, win_y + 85, 90, 45)
                    btn_no = pygame.Rect(win_x + 190, win_y + 85, 90, 45)

                    if btn_yes.collidepoint(mx, my):
                        print("POTWIERDZONO ZBURZENIE")
                        self.demolish_castle(self.selected_castle)
                        return
                    if btn_no.collidepoint(mx, my):
                        print("ANULOWANO ZBURZENIE")
                        self.demolish_confirm = False
                        return
                    
                    # Jeśli okno jest otwarte, ale kliknąłeś obok przycisków TAK/NIE
                    # to i tak blokujemy resztę zamku (return)
                    return 

                # B. POTEM: Sprawdź przycisk otwierający okno burzenia
                if getattr(self, 'demolish_button', None) and self.demolish_button.collidepoint(mx, my):
                    self.demolish_confirm = True
                    print("DEBUG: Otwieram okno potwierdzenia burzenia")
                    return

                # C. NA KOŃCU: Reszta budynków zamku
                if getattr(self, 'forge_button', None) and self.forge_button.collidepoint(mx, my):
                    self.screen = "forge"; return
                if getattr(self, 'workshop_button', None) and self.workshop_button.collidepoint(mx, my):
                    self.screen = "workshop"; return
                if getattr(self, 'hospital_button', None) and self.hospital_button.collidepoint(mx, my):
                    self.screen = "hospital"; return
                if getattr(self, 'school_button', None) and self.school_button.collidepoint(mx, my):
                    self.screen = "school"; return
                if getattr(self, 'recruit_button', None) and self.recruit_button.collidepoint(mx, my):
                    self.selected_patent_index = None # RESETUJEMY WYBÓR
                    self.selected_unit_type = None   # RESETUJEMY WYBÓR
                    self.screen = "recruitment"
                    return
                if getattr(self, 'back_button', None) and self.back_button.collidepoint(mx, my):
                    self.screen = "map"; self.selected_castle = None; return

                # Jeśli nic nie trafiono, obsłuż ogólne kliknięcie w grafikę zamku
                self.handle_castle_click(mx, my)
                return
        # 3. EKRANY BUDYNKÓW (Forge, Workshop itp.)
        if self.screen in ["forge", "workshop", "hospital", "school", "peasants", "court"]:
            if button == 1:
                if hasattr(self, 'back_button') and self.back_button.collidepoint(mx, my):
                    self.screen = "castle"; return
                if self.screen == "peasants":
                    self.handle_peasants_click(mx, my); return
            return

        # 4. MAPA
        if self.screen == "map":
            # UI na górze (zazwyczaj tylko lewy klik)
            if button == 1:
                if self.show_top_ui and self.top_ui_full_area.collidepoint(mx, my):
                    if self.btn_system.collidepoint(mx, my): self.active_dropdown = "System"; return
                    if self.btn_mapa.collidepoint(mx, my): self.active_dropdown = "Mapa"; return
                    if self.next_turn_button.collidepoint(mx, my): self.next_turn(); return
                    return

            # Jeśli mamy jednostkę, przekazujemy klik (lewy lub prawy) do mapy
            if self.selected_unit:
                self.handle_map_click(mx, my, button)
                return 

            # Wejście do zamku (tylko lewy klik)
            if button == 1:
                for castle in self.castles:
                    castle_rect = pygame.Rect(
                        (castle.x * TILE_SIZE) - self.camera_x, 
                        (castle.y * TILE_SIZE) - self.camera_y, 
                        64, 64
                    )
                    if castle_rect.collidepoint(mx, my):
                        if castle.destroyed:
                            print("To są zgliszcza.")
                            return 
                        self.selected_castle = castle
                        self.screen = "castle"
                        return 

            # Jeśli nic innego, standardowa obsługa mapy (np. zaznaczanie jednostek)
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

    def draw_pygame(self, screen):
        screen.fill((30, 30, 30))

        if self.screen == "map":
            self.draw_map(screen)
            return
        elif self.screen == "castle":
            self.draw_castle(screen)
            return
        elif self.screen == "garrison":
            self.draw_garrison(screen)
            return
        elif self.screen == "recruitment":
            self.draw_recruitment(screen)
            return
        elif self.screen == "peasants":
            self.draw_peasants(screen)
            return
        elif self.screen == "unit_info":
            self.draw_unit_info(screen)
            return
        elif self.screen == "court":
            self.draw_court(screen)
            return
        elif self.screen == "forge":
            self.draw_forge(screen)
            return
        elif self.screen == "workshop":
            self.draw_workshop(screen)
            return
        elif self.screen == "hospital":
            self.draw_hospital(screen)
            return
        elif self.screen == "school":
            self.draw_school(screen)
            return
        
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

        # --- OKNO STATYSTYK (TOOLTIP) ---
        if hasattr(self, 'inspected_unit') and self.inspected_unit:
            # Pobieramy aktualną pozycję myszy, żeby okno "chodziło" za kursorem
            cur_x, cur_y = pygame.mouse.get_pos()
            
            # Tworzymy tło okienka
            info_rect = pygame.Rect(cur_x + 20, cur_y, 200, 180)
            
            # Rysowanie tła (czarny z obramowaniem)
            pygame.draw.rect(screen, (20, 20, 20), info_rect)
            pygame.draw.rect(screen, (255, 255, 255), info_rect, 2)
            
            u = self.inspected_unit
            # Przygotowanie tekstu (używamy czcionki, którą już masz w draw_garrison)
            lines = [
                f"TYP: {u.type.upper()}",
                f"EXP: {u.experience}",
                f"ATK: {u.attack}",
                f"DEF: {u.defense}",
                f"MORALE: {u.morale}",
                f"ZMECZ: {u.fatigue}",
                f"RUCH: {u.move_points}"
            ]

            for i, line in enumerate(lines):
                line_surf = font.render(line, True, (255, 255, 0) if i == 0 else (255, 255, 255))
                screen.blit(line_surf, (info_rect.x + 10, info_rect.y + 10 + i * 22))
    
    def draw_map(self, screen):
        # --- 1. USTAWIENIA I KAMERA ---
        tiles_on_screen_x = SCREEN_WIDTH // TILE_SIZE + 1
        tiles_on_screen_y = SCREEN_HEIGHT // TILE_SIZE + 1
        start_x = self.camera_x // TILE_SIZE
        start_y = self.camera_y // TILE_SIZE

                # --- 2. RYSOWANIE TERENU (TŁA) ---
        # Używamy len(self.map) zamiast MAP_HEIGHT
        for y in range(max(0, start_y), min(len(self.map), start_y + tiles_on_screen_y)):
            # Używamy len(self.map[0]) zamiast MAP_WIDTH
            for x in range(max(0, start_x), min(len(self.map[0]), start_x + tiles_on_screen_x)):
                pos_x = (x * TILE_SIZE) - self.camera_x
                pos_y = (y * TILE_SIZE) - self.camera_y
                tile_type = self.map[y][x] 

                if tile_type == "#":
                    color = (139, 69, 19)   # Brąz
                elif tile_type == "$":
                    color = (255, 215, 0)   # Złoto
                elif tile_type == "S":
                    color = (255, 255, 255) # Świątynia
                else:
                    color = (34, 139, 34)   # Trawa
                
                # Teraz pos_x i pos_y są już znane
                pygame.draw.rect(screen, color, (pos_x, pos_y, TILE_SIZE - 1, TILE_SIZE - 1))

        # --- 3. RYSOWANIE PLACÓW BUDOWY (castle_locations) ---
        for px, py in self.castle_locations:
            rect = pygame.Rect((px * TILE_SIZE) - self.camera_x, (py * TILE_SIZE) - self.camera_y, 64, 64)
            pygame.draw.rect(screen, (150, 150, 150), rect, 2) 

        # --- 4. RYSOWANIE ZAMKÓW (Z UWZGLĘDNIENIEM ZBURZENIA I KOLORU WŁAŚCICIELA) ---
        for castle in self.castles:
            # Zakładamy, że zamek ma wymiar 64x64 (2x2 kafelki)
            rect = pygame.Rect((castle.x * TILE_SIZE) - self.camera_x, (castle.y * TILE_SIZE) - self.camera_y, 64, 64)
            
            if getattr(castle, 'destroyed', False):
                # CZERWONE POLE DLA ZBURZONEGO ZAMKU
                pygame.draw.rect(screen, (180, 0, 0), rect) # Ciemna czerwień
                pygame.draw.rect(screen, (50, 0, 0), rect, 2) # Ciemna obwódka
                pygame.draw.line(screen, (100, 0, 0), (rect.x, rect.y), (rect.right, rect.bottom), 2)
                pygame.draw.line(screen, (100, 0, 0), (rect.right, rect.y), (rect.left, rect.bottom), 2)
            else:
                # --- POPRAWKA TUTAJ ---
                # Pobierz kolor od właściciela zamku. Jeśli neutralny, daj szary.
                castle_color = castle.owner.color if castle.owner else (100, 100, 100)
                
                # Rysujemy zamek w kolorze gracza
                pygame.draw.rect(screen, castle_color, rect) 
                # Dodajemy czarną obwódkę, żeby zamek odróżniał się od tła
                pygame.draw.rect(screen, (0, 0, 0), rect, 3)
                
                # Opcjonalnie: Dodaj mały jasny "daszek", żeby zamek wyglądał jak budynek, a nie tylko kwadrat
                pygame.draw.rect(screen, (255, 255, 255), (rect.x + 10, rect.y + 10, 44, 5), 0)
       # --- 5. RYSOWANIE JEDNOSTEK ---
        unit_font = pygame.font.SysFont("Arial", 16, bold=True)

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
            if u.type == "Budowniczy":
                label = "BU"
            elif u.type == "Katapulta":
                label = "KA"
            elif u.type == "Jazda":
                label = "JA"
            else:
                label = "??" # Dla nieznanych jednostek

            txt_surface = unit_font.render(label, True, (255, 255, 255))
            text_rect = txt_surface.get_rect(center=(px + 16, py + 16))
                
                # Małe czarne tło pod literami, żeby były czytelne
            pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(2, 2))
            screen.blit(txt_surface, text_rect)

            # 3. OZNACZENIE ZAZNACZENIA (Biała ramka DOOKOŁA)
            if u == self.selected_unit:
                # Rysujemy tylko ramkę (ostatni parametr '2' to grubość linii)
                pygame.draw.rect(screen, (255, 255, 255), (px + 2, py + 2, 28, 28), 2)
        # --- 6. KROPKI DROGI ---
        if self.selected_unit and getattr(self.selected_unit, 'planned_path', None):
            self.draw_path_dots(screen, self.selected_unit, self.selected_unit.planned_path)

    def draw_castle(self, screen):
    
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        screen.fill((60, 50, 40))  

        self.peasant_button.x = screen_width - 200
        self.peasant_button.y = screen_height - 70
            #reset przycisków
        self.koszary_button = None  

        castle = self.selected_castle

        font = pygame.font.SysFont(None, 28)

        title = font.render("CASTLE", True, (255, 255, 255))
        screen.blit(title, (40, 40))

        if self.selected_castle:
            gold = font.render(
                f"Gold: {self.selected_castle.gold}",
                True,
                (255, 255, 0),
            )
            screen.blit(gold, (40, 80))

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

        pygame.draw.rect(screen, (100, 140, 60), self.peasant_button)

        text = font.render("PEASANTS", True, (255,255,255))
        screen.blit(
            text,
            (
                self.peasant_button.x + 20,
                self.peasant_button.y + 10
    )
)
        mx, my = pygame.mouse.get_pos()
        if self.menu_open:
            self.draw_castle_menu(screen, mx, my)

        # MENU BUTTON
        pygame.draw.rect(screen, (80, 80, 80), self.menu_button)
        screen.blit(font.render("MENU", True, (255,255,255)),
                    (self.menu_button.x + 25, self.menu_button.y + 10))

        # jeśli najedziemy na przycisk — otwórz menu
        if self.menu_button.collidepoint(mx, my):
            self.menu_open = True

        # NAJPIERW rysujemy menu (tworzy recty!)
        if self.menu_open:
            self.draw_castle_menu(screen, mx, my)

        # DOPIERO TERAZ sprawdzamy czy zamknąć
        mouse_over_ui = False

        if self.menu_button.collidepoint(mx, my):
            mouse_over_ui = True

        for rect in self.menu_rects.values():
            if rect.collidepoint(mx, my):
                mouse_over_ui = True

        for rect in self.build_rects.values():
            if rect.collidepoint(mx, my):
                mouse_over_ui = True

        if not mouse_over_ui:
            self.menu_open = False
            self.build_open = False

    # --- BUTTON: COURT ---
        self.court_button = pygame.Rect(420, 100, 160, 40)
        pygame.draw.rect(screen, (20, 80, 80), self.court_button)
        screen.blit(font.render("DWÓR", True, (255,225,255)), (470,110))

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

        # 3. PRZYCISKI (Recty i logika STARTU)
        self.info_button = pygame.Rect(120, 590, 100, 30)
        self.back_button = pygame.Rect(40, 630, 100, 30)
        self.buy_patent_button = pygame.Rect(160, 630, 140, 30)
        self.remove_patent_button = pygame.Rect(w - 230, 590, 100, 30)
        self.start_prod_button = pygame.Rect(w - 300, 630, 120, 30)
        self.stop_prod_button = pygame.Rect(w - 160, 630, 120, 30)
        self.scroll_up_button = pygame.Rect(260, 80, 40, 40)
        self.scroll_down_button = pygame.Rect(260, 200, 40, 40)

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

                # 5. STATYSTYKI (Zawsze podążają za scrollem po lewej)
        center_index = 2
        idx_on_center = self.recruitment_scroll + center_index

        unit_to_show = None
        # Zawsze bierzemy to, co jest na środku widocznej listy
        if 0 <= idx_on_center < len(unit_types):
            unit_to_show = unit_types[idx_on_center]

        # Rysowanie kwadratu pod opis jednostki
            # Parametry: (ekran, kolor, (x, y, szerokość, wysokość), grubość_linii)
            square_color = (50, 40, 30) # Ciemny brąz
            info_rect = pygame.Rect(20, 265, 380, 200)
                
            # Wypełniony kwadrat
            pygame.draw.rect(screen, square_color, info_rect)
                
            # Ramka wokół kwadratu (np. złota)
            pygame.draw.rect(screen, (200, 180, 100), info_rect, 4)

        # Rysowanie prostokąta pod opis czasu
            # Parametry: (ekran, kolor, (x, y, szerokość, wysokość), grubość_linii)
            square_color = (70, 40, 30) # Ciemny brąz
            info_rect = pygame.Rect(20, 490, 400, 40)
                
            # Wypełniony kwadrat
            pygame.draw.rect(screen, square_color, info_rect)
                
            # Ramka wokół kwadratu (np. złota)
            pygame.draw.rect(screen, (200, 180, 100), info_rect, 4)

        # RYSOWANIE STATYSTYK - wszystko musi być w tym jednym IFie
        if unit_to_show:
            stats = UNIT_STATS.get(unit_to_show, {})
            if stats:
                screen.blit(font.render(f"Jednostka: {unit_to_show}", True, (255, 255, 255)), (120, 270))
                # 1. ATK
                screen.blit(font.render(f"ATK: {stats.get('attack', 0)}", True, (255, 255, 255)), (140, 310))
                # 2. DEF
                screen.blit(font.render(f"DEF: {stats.get('defense', 0)}", True, (255, 255, 255)), (140, 390))
                # 3. HP
                screen.blit(font.render(f"HP: {stats.get('hp', 0)}", True, (255, 255, 255)), (220, 310))
                # 4. MORALE
                screen.blit(font.render(f"MOR: {stats.get('morale', 0)}", True, (255, 255, 255)), (220, 390))
                # 5. MOVES
                screen.blit(font.render(f"MOV: {stats.get('moves', 0)}", True, (255, 255, 255)), (300, 310))
                # 6. ATTACK
                screen.blit(font.render(f"ATC: {stats.get('attack', 0)}", True, (255, 255, 255)), (300, 390))

                # Koszty (dalej wewnątrz if unit_to_show)
                screen.blit(font.render(f"Patent: {stats.get('patent_cost', 0)}", True, (255, 255, 0)), (40, 500))
                screen.blit(font.render(f"Prod: {stats.get('production_cost', 0)}", True, (255, 255, 0)), (200, 500))
                screen.blit(font.render(f"Tury: {stats.get('production_time', 0)}", True, (255, 255, 0)), (360, 500))

        # 6. RESZTA (Poza ifem statystyk - rzeczy stałe)
        screen.blit(font.render(f"Gold: {castle.gold}", True, (255, 215, 0)), (w // 2 - 30, 640))
        
        pygame.draw.rect(screen, (100, 100, 100), self.scroll_up_button)
        pygame.draw.rect(screen, (100, 100, 100), self.scroll_down_button)
        screen.blit(font.render("▲", True, (255, 255, 255)), (self.scroll_up_button.x + 12, self.scroll_up_button.y + 8))
        screen.blit(font.render("▼", True, (255, 255, 255)), (self.scroll_down_button.x + 12, self.scroll_down_button.y + 8))
        
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
            draw_button(screen, "SCIECIE", x+130, y+10, 100, 25)
            draw_button(screen, "TORTURY", x+130, y+45, 100, 25)
            draw_button(screen, "PRZEKUP", x+130, y+80, 100, 25)

    def execute_general(self, slot):
        slot.general = None

    def torture_general(self, slot):
        print("Informacje zdobyte")

    def bribe_general(self, slot):
        print("Generał zmienił stronę")

    def draw(self, screen):
        mx, my = pygame.mouse.get_pos()

        # 1. LOGIKA EKRANU MAPY
        if self.screen == "map":
            self.draw_map(screen)
            self.draw_top_bar(screen)
            self.draw_bottom_bar(screen)

            #2. EKRAN ZAMKU (Główny)
        elif self.screen == "castle":
            self.draw_castle(screen)

        # 3. EKRAN KOSZAR (Garrison)
        elif self.screen == "garrison":
            self.draw_garrison(screen) # Rysuje te duże ramki ze zdjęcia 1
            
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
        font = pygame.font.SysFont(None, 24)

        menu_x = self.menu_button.x
        menu_y = self.menu_button.y + 40

        options = ["Buduj", "Burz zamek", "Rozbuduj mury"]
        self.menu_rects.clear()

        for i, opt in enumerate(options):
            rect = pygame.Rect(menu_x, menu_y + i*40, 160, 40)
            pygame.draw.rect(screen, (100, 100, 100), rect)
            screen.blit(font.render(opt, True, (255,255,255)),
                        (menu_x+10, menu_y+10+i*40))

            self.menu_rects[opt] = rect

        # hover Buduj
        buduj_rect = self.menu_rects["Buduj"]

        submenu_rect = pygame.Rect(menu_x - 160, menu_y, 160, 200)

        if buduj_rect.collidepoint(mx, my) or submenu_rect.collidepoint(mx, my):
            self.build_open = True
        else:
            self.build_open = False

        if self.build_open:
            self.draw_build_submenu(screen, menu_x, menu_y)
        # BURZ
        self.demolish_button = pygame.Rect(menu_x, menu_y+40, 160, 40)
        pygame.draw.rect(screen, (100, 100, 100), self.demolish_button)
        screen.blit(font.render("ZBURZ ZAMEK", True, (255,255,255)), (menu_x+10, menu_y+50))

        # MURY
        self.wall_button = pygame.Rect(menu_x, menu_y+80, 160, 40)
        pygame.draw.rect(screen, (100, 100, 100), self.wall_button)
        screen.blit(font.render("ROZBUDUJ MURY", True, (255,255,255)), (menu_x+10, menu_y+90))

    def draw_build_submenu(self, screen, menu_x, menu_y):
        font = pygame.font.SysFont(None, 24)
        castle = self.selected_castle  # Pobieramy aktualny zamek
        if not castle: return

        sub_x = menu_x - 160
        sub_y = menu_y

        buildings = ["hospital", "school", "Koszary", "forge", "workshop"]
        self.build_rects.clear()

        for i, b in enumerate(buildings):
            rect = pygame.Rect(sub_x, sub_y + i*40, 160, 40)
            pygame.draw.rect(screen, (80, 80, 120), rect)

            # --- KLUCZOWA ZMIANA ---
            # Sprawdzamy czy budynek 'b' jest już zbudowany w tym konkretnym zamku
            is_built = b in castle.buildings 
            
            color = (100, 100, 100) if is_built else (255, 255, 255)
            
            label = f"{b}" if is_built else b
            screen.blit(font.render(label, True, color), (sub_x + 10, sub_y + 10 + i*40))

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
                        unit.planned_path = []
                        print("DEBUG: Zaznaczono jednostkę")
                        return
        # Przeliczamy współrzędne myszy na kratki (uwzględniając kamerę)
        grid_x = (mx + self.camera_x) // TILE_SIZE
        grid_y = (my + self.camera_y) // TILE_SIZE

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

            # 1. EWAKUACJA GARNIZONU (Z wnętrza na mapę)
            if castle.owner:
                for unit in castle.garrison:
                    if unit is not None:
                        # Szukamy wolnego pola obok zamku (np. w promieniu 1-2 kafelków)
                        found = False
                        for dy in range(-1, 2):
                            for dx in range(-1, 2):
                                nx, ny = castle.x + dx, castle.y + dy
                                # Sprawdź granice mapy i czy pole jest wolne
                                if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                                    if not self.get_unit_at(nx, ny):
                                        unit.x, unit.y = nx, ny
                                        castle.owner.units.append(unit) # DODAJ DO GRACZA
                                        found = True
                                        break
                            if found: break
            
            # 2. LOGIKA NISZCZENIA
            castle.destroyed = True
            
            # Usuwamy zamek z listy posiadłości gracza
            if castle.owner and castle in castle.owner.castles:
                castle.owner.castles.remove(castle)
                
            castle.owner = None
            castle.garrison = [None] * 12 # Czyścimy środek
            
            # 3. POWRÓT NA MAPĘ
            self.demolish_confirm = False
            self.screen = "map"
            print("Twierdza zniszczona, wojsko ewakuowane na okoliczne pola.")
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
    
    def release_selected_units(self):
        castle = self.selected_castle
        if not castle or castle.owner is None:
            print("Błąd zamku lub właściciela")
            return

        if not self.selected_units:
            print("Brak zaznaczonych jednostek")
            return

        player = castle.owner

        # --- LOGIKA SZUKANIA MIEJSCA NA MAPIE (ZOSTAJE BEZ ZMIAN) ---
        directions = [
            (-1, 2), (0, 2), (1, 2), (2, 2),
            (-1, 1),                 (2, 1),
            (-1, 0),                 (2, 0),
            (-1,-1), (0,-1), (1,-1), (2,-1)
        ]
        occupied = {(u.x, u.y) for u in self.units}
        spawn_pos = None
        for dx, dy in directions:
            nx, ny = castle.x + dx, castle.y + dy
            if 0 <= nx < len(self.map[0]) and 0 <= ny < len(self.map):
                if (nx, ny) not in occupied and self.map[ny][nx] in [".", "0", " ", "$"]:
                    spawn_pos = (nx, ny)
                    break

        if not spawn_pos:
            print("Brak miejsca wokół zamku")
            return

        nx, ny = spawn_pos
        # ---------------------------------------------------------

        # Tworzymy nową armię na mapie
        army = Unit("army", nx, ny, player)
        army.move_points = 1
        army.garrison = [] # Armia na mapie może mieć dynamiczną listę (to nie przeszkadza)

        # --- KLUCZOWA ZMIANA: Przenoszenie bez przesuwania slotów ---
        # Iterujemy po całym garnizonie zamku (wszystkie 12 slotów)
        for i in range(len(castle.garrison)):
            unit_in_slot = castle.garrison[i]
            
            # Jeśli w tym slocie jest jednostka i jest ona na liście ZAZNACZONYCH
            if unit_in_slot is not None and unit_in_slot in self.selected_units:
                # 1. Dodaj jednostkę do nowej armii na mapie
                army.garrison.append(unit_in_slot)
                
                # 2. WYCZYŚĆ SLOT W ZAMKU (zostaw None), zamiast używać .remove()
                # Dzięki temu pozostałe jednostki nie drgną z miejsca
                castle.garrison[i] = None

        # Dodajemy armię do list systemowych
        player.units.append(army)
        self.units.append(army) 

        self.selected_units.clear()
        print(f"Wypuszczono armię na pozycję {nx}, {ny}. Sloty w zamku zostały zachowane.")

    def draw_unit_info(self, screen):
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
            # Ustawiamy start X pod odpowiednim przyciskiem
            start_x = self.btn_system.x if self.active_dropdown == "System" else self.btn_mapa.x
            
            for i, opt in enumerate(options):
                rect = pygame.Rect(start_x, 40 + (i * self.option_height), 150, self.option_height)
                
                # Podświetlenie opcji, nad którą jest myszka
                is_hovered = rect.collidepoint(mx, my)
                color = (150, 150, 150) if is_hovered else (80, 80, 80)
                
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (200, 200, 200), rect, 1) # obramowanie
                
                txt = self.font.render(opt, True, (255, 255, 255))
                screen.blit(txt, (rect.x + 10, rect.y + 5))

    def draw_bottom_bar(self, screen):
        # ... Twój kod rysujący tło panelu ...

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

    def execute_menu_command(self, menu, index):
        # Sprawdzamy menu System
        if menu == "System":
            if index == 5:  # "Koniec" (szósta opcja, więc indeks 5)
                print("Zamykanie gry...")
                pygame.quit()
                import sys
                sys.exit()
                
            elif index == 2: # Zapisz grę
                print("Zapisywanie stanu gry...")
                # Tutaj w przyszłości dodasz self.save_game()
                    
        # Sprawdzamy menu Mapa
        elif menu == "Mapa":
            opcja = self.menu_options['Mapa'][index]
            print(f"Wybrano opcję mapy: {opcja}")
            
            if index == 3: # "Nic"
                print("Ukrywam elementy mapy...")
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
                self.inspected_unit = castle.garrison[index]
                print(f"DEBUG: Znaleziono jednostkę: {self.inspected_unit.type}") # <-- SPRAWDŹ TO W KONSOLI
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
        if self.map is None:
            return False
            
        map_height = len(self.map)
        map_width = len(self.map[0]) if map_height > 0 else 0
        
        # 1. Sprawdzenie granic mapy i typu terenu
        if not (0 <= x < map_width and 0 <= y < map_height):
            return False
            
        tile = self.map[y][x]
        if tile not in [".", "0", " ", "$"]:
            return False

        # 2. Sprawdzenie, czy nie stoi tam jednostka (sprawdzamy WSZYSTKICH graczy)
        for player in self.players:
            for u in player.units:
                if u.x == x and u.y == y:
                    return False
        
        # Jeśli przeszło oba testy, pole jest wolne
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
      
    def handle_ui_click(self, mx, my):
        """Zwraca True, jeśli kliknięto w UI, co blokuje kliknięcie w mapę."""
        u = self.selected_unit

        # Sprawdzamy 6 przycisków akcji
        for i, rect in enumerate(self.action_buttons):
            if rect.collidepoint(mx, my):
                if self.build_menu_open:
                    # --- LOGIKA MENU BUDOWANIA ---
                    # labels = ["DROGA", "PUŁAPKA", "SKARB", "WIEŻA", "TWIERDZA", "ZAMEK"]
                    self.execute_build_action(i, u)
                else:
                    # --- LOGIKA MENU GŁÓWNEGO ---
                    # labels = ["TRYB MAPY", "ATK", "SPL", "WAIT", "BUILD", "REC"]
                    if i == 0: # TRYB MAPY
                        self.selected_unit = None
                        self.selected_castle = None
                    elif i == 4: # BUILD (Otwiera podmenu)
                        if u and u.type == "Budowniczy":
                            self.build_menu_open = True
                            print("Menu budowania otwarte.")
                    # ... reszta przycisków (ATK, SPL itd.)
                
                return True # UI kliknięte, blokujemy mapę

        # Blokada tła panelu
        ui_area = pygame.Rect(720, 610, 300, 150) 
        if ui_area.collidepoint(mx, my):
            return True 

        return False
       
    def draw_ui(self, screen):
        for name, rect in self.menu_rects.items():
            # Rysowanie tła przycisku
            pygame.draw.rect(screen, (139, 69, 19), rect) # Brązowy
            pygame.draw.rect(screen, (255, 255, 255), rect, 2) # Ramka
            
            # Rysowanie tekstu
            text_surf = self.font.render(name, True, (255, 255, 255))
            # Środkowanie tekstu
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)
            
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
        """button_index: od 0 do 5 (odpowiada self.action_buttons)"""
        u = self.selected_unit
        if not u: return

        if self.build_menu_open:
            # MENU BUDOWANIA: ["DROGA", "PUŁAPKA", "SKARB", "WIEŻA", "TWIERDZA", "ZAMEK"]
            self.execute_build_action(button_index, u)
        else:
            # MENU GŁÓWNE: ["TRYB MAPY", "ATK", "SPL", "WAIT", "BUILD", "REC"]
            if button_index == 0:
                self.handle_tryb_mapy_button()
            elif button_index == 4: # Przycisk BUILD
                if u.type == "Budowniczy":
                    self.build_menu_open = True
                    print("Otwarto menu budowania.")

    def execute_build_action(self, index, u):
        if not u or u.type != "Budowniczy": return
        pos = (u.x, u.y)

        if index == 0: # DROGA (6 pkt ruchu)
            if u.moves >= 6:
                u.moves -= 6
                self.map[u.y][u.x] = "R" # "R" jak Road
                print("Wybudowano drogę! Pozostałe MP:", u.moves)
            else:
                print("Za mało punktów ruchu (wymagane 6)!")

        elif index == 1: # PUŁAPKA (Śmierć budowniczego)
            self.traps.append({"x": u.x, "y": u.y, "owner": u.owner})
            if u in self.units: self.units.remove(u)
            if u in u.owner.units: u.owner.units.remove(u)
            self.selected_unit = None
            self.build_menu_open = False
            print("Zastawiono pułapkę. Budowniczy poświęcony.")

        elif index == 2: # SKARB (0 pkt ruchu)
            if self.map[u.y][u.x] == "$":
                u.owner.gold += 500
                self.map[u.y][u.x] = "." # Zmieniamy na zwykłą ziemię
                print("Skarb wykopany!")
            else:
                print("Tu nie ma skarbu.")

        elif index in [3, 4, 5]: # WIEŻA (4j), TWIERDZA (12j), ZAMEK (24j)
            # Rejestrujemy budowę czasową
            data = {3: ("Wieża", 4), 4: ("Twierdza", 12), 5: ("Zamek", 24)}
            name, work = data[index]
            
            if pos not in self.active_projects:
                self.active_projects[pos] = {
                    "type": name, 
                    "remaining_work": work, 
                    "owner": u.owner
                }
                print(f"Rozpoczęto budowę: {name} ({work} tury pracy).")
                self.build_menu_open = False # Zamykamy menu po zleceniu
            else:
                print("To pole jest już zajęte przez inną budowę!")
    
    def spawn_test_builder(self):
        if not self.castles: return
        castle = self.castles[0]
        from unit import Unit
        
        # Tworzymy obiekt
        new_builder = Unit("Budowniczy", int(castle.x + 2), int(castle.y), castle.owner)
        
        # Rejestrujemy go w systemie
        self.add_unit_to_game(new_builder)

    def start_castle_construction(self, unit):
        # Sprawdź czy na tym polu już coś się buduje
        for c in self.constructions:
            if c["x"] == unit.x and c["y"] == unit.y:
                print("Tu już trwa budowa!")
                return

        # Dodaj nową budowę (24 punkty pracy do wykonania)
        self.constructions.append({
            "x": unit.x,
            "y": unit.y,
            "progress": 0,
            "target": 24,
            "owner": unit.owner
        })
        print("Rozpoczęto budowę zamku! Potrzeba 24 punktów pracy.")

    def add_unit_to_game(self, unit):
        """Dodaje jednostkę do świata i do listy jej właściciela."""
        # 1. Dodaj do głównej listy (do rysowania)
        if unit not in self.units:
            self.units.append(unit)
        
        # 2. Dodaj do listy gracza (do zaznaczania i sterowania)
        if unit.owner and unit not in unit.owner.units:
            unit.owner.units.append(unit)
            print(f"DEBUG: Jednostka {unit.type} przypisana do gracza {unit.owner.name}")