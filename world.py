from unit import Unit, UNIT_STATS
from castle import Castle
from player import Player
from map_loader import load_map, load_fac_objects
import pygame
from castle import BUILDINGS

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
        pygame.font.init() # Inicjalizacja modułu czcionek
        self.font = pygame.font.SysFont("Arial", 24) # Stworzenie czcionki systemowej
        # 1. Najpierw tworzymy puste listy/atrybuty
        self.map=[]
        self.units = []
        self.castles = []           # Lista dla zbudowanych zamków
        self.castle_locations = []  # Lista dla pustych miejsc (fundamentów)
        # 2. Potem ładujemy dane, które te listy wypełnią
        self.map = self.load_map("map.txt")
        self.load_castles_from_fac("0.FAC")
        self.garrison = [] # Lista jednostek w środku
        self.destroyed = False
        self.owner = None # Możesz ustawić właściciela na podstawie danych z FAC
        self.map = None
        self.objects = None
        self.peasant_groups = []
        self.gold_transports = []
        self.players = []
        self.units = []
        self.castles = []
        self.selected_units = []
        self.screen = "map"
        self.selected_castle = None
        self.selected_garrison_unit = None
        self.turn = 1
        self.current_player = 0
        self.selected_unit = None
        self.koszary_button = None
        self.garrison_button = pygame.Rect(40, 140, 160, 40)
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
        # Definiujemy bazową pozycję panelu (np. dolny prawy róg)
        panel_x = 730
        panel_y = 620
        self.action_buttons = []
        # Tworzymy 6 przycisków w siatce 2x3
        for row in range(2):
            for col in range(3):
                rect = pygame.Rect(panel_x + col * 65, panel_y + row * 55, 60, 50)
                self.action_buttons.append(rect)
        self.build_menu_open = False  # Flaga: czy menu budowania jest otwarte?
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

        # Jednostki startowe (tylko przy prawdziwych zamkach)
        for c in self.castles:
            if c.owner:
                self.add_unit(Unit("lekka_piechota", c.x, c.y + 1, c.owner))

        print(f"Zbudowano zamków: {len(self.castles)}")
        print(f"Miejsc pod budowę: {len(self.castle_locations)}")
        print("DEBUG castles:", len(self.castles))
        print("DEBUG units:", len(self.units))
        map_width = len(self.map[0]) * 32
        self.next_turn_button = pygame.Rect(map_width + 20, 10, 170, 40)
        print("PLAYERS:", len(self.players))
        print("CASTLES:", len(self.castles))

        for c in self.castles:
            print("castle owner:", c.owner)

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

    def move_unit(self, unit, dx, dy):
        if unit.move_points <= 0:
            return

        nx = unit.x + dx
        ny = unit.y + dy

        # 1. Granice mapy
        if not (0 <= nx < len(self.map[0]) and 0 <= ny < len(self.map)):
            return

        # 2. ====== LOGIKA WEJŚCIA DO ZAMKU (2x2) ======
        # Sprawdzamy, czy pole nx, ny (cel ruchu) należy do jakiegoś zbudowanego zamku
        for castle in self.castles: 
            if castle.x <= nx <= castle.x + 1 and castle.y <= ny <= castle.y + 1:
                if castle.destroyed:
                    print("To są ruiny, nie wejdziesz.")
                    return
                
                print(f"Jednostka {unit.type} wchodzi do zamku na {castle.x}, {castle.y}")
                
                # Dodaj do garnizonu
                castle.garrison.append(unit)
                
                # Usuń z mapy i odznacz
                if unit in self.units:
                    self.units.remove(unit)
                if unit in unit.owner.units:
                    unit.owner.units.remove(unit)
                
                # Ustawiamy współrzędne na ujemne, by zniknęła z mapy
                unit.x, unit.y = -1, -1
                self.selected_unit = None
                return  # PRZERWIJ FUNKCJĘ - jednostka weszła do zamku

        # 3. ====== WALKA (jeśli na polu stoi inna jednostka) ======
        for other in self.units:
            if other.x == nx and other.y == ny:
                if other.owner != unit.owner:
                    print("ATAK!")
                    self.units.remove(other)
                    if other in other.owner.units:
                        other.owner.units.remove(other)
                    
                    unit.x, unit.y = nx, ny
                    unit.move_points -= 1
                    return
                else:
                    print("Sojusznik blokuje pole")
                    return

        # 4. ===== NORMALNY RUCH (tylko na kafelku ".") =====
        # Sprawdzamy czy teren pozwala na przejście
        if self.map[ny][nx] in [".", "0", " "]:
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
            print("Nie wybrano jednostki")
            return

        u = self.selected_unit

        if u.move_points <= 0:
            print("Brak punktów ruchu")
            return

        nx = u.x + dx
        ny = u.y + dy

        if ny < 0 or ny >= len(self.map):
            return
        if nx < 0 or nx >= len(self.map[0]):
            return

        # ===== ZAMEK =====
        print("UNIT IDZIE NA:", nx, ny)

        for castle in self.castles:
            print("ZAMEK TILE:", castle.tile_position())

        for castle in self.castles:
            if castle.tile_position() == (nx, ny):

                if castle.destroyed:
                    print("Ruiny zamku — nie można wejść")
                    return
                print("Jednostka weszła do zamku")

                # === PRZEJĘCIE ===
                if castle.owner != u.owner:
                    castle.owner = u.owner
                    castle.garrison.clear()
                    print("Zamek został przejęty!")

                # === WEJŚCIE DO GARNIZONU ===
                castle.garrison.append(u)

                if u in self.units:
                    self.units.remove(u)

                u.x = -1
                u.y = -1

                u.move_points -= 1
                self.selected_unit = None
                self.selected_units.clear()
                return

        # blokada terenu (ALE NIE ZAMEK)
        if self.map[ny][nx] != ".":
            print("Nie można wejść na to pole")
            return

    # ===== WALKA =====
        for other in self.units:
            if other.x == nx and other.y == ny:
                if other.owner != u.owner:
                    print("Atak!")
                    self.units.remove(other)
                else:
                    print("Pole zajęte przez sojusznika")
                    return
                u.x = nx
                u.y = ny
                u.move_points -= 1
                return            

        u.x = nx
        u.y = ny
        u.move_points -= 1

        for castle in self.castles:
            if castle.tile_position() == (nx, ny):

                if castle.destroyed:
                    print("Ruiny zamku — nie można wejść")
                    return

                print("Jednostka weszła do zamku")

                castle.under_attack()

                if castle.owner != u.owner:
                    castle.owner = u.owner
                    castle.garrison.clear()
                    print("Zamek został przejęty!")

                castle.garrison.append(u)
                self.units.remove(u)
                self.selected_unit = None
                return
             
            for group in self.peasant_groups:
                for castle in self.castles:
                    if castle.tyle_position() == group.position():
                        if castle.owner == group.owner:
                            castle.peasants += group.amount
                            self.peasant_groups.remove(group)
                            print("Chłopi dotarli do zamku")
                            return
            for t in self.gold_transports:
                for castle in self.castles:
                    if castle.tyle_position() == t.position():
                        if castle.owner == t.owner:
                            castle.gold += t.gold
                            self.gold_transports.remove(t)
                            print("Złoto dotarło do zamku")
                            return
        for group in self.peasant_groups:
            if group.x == nx and group.y == ny:
                if group.owner != u.owner:

                    army_size = 1  # na razie jednostka = armia

                    if army_size < 10:
                        print("Chłopi dołączyli do armii")
                        u.carried_peasants += group.amount
                        self.peasant_groups.remove(group)
                    else:
                        print("Przejęto chłopów")
                        group.owner = u.owner

                    return
        for t in self.gold_transports:
            if t.x == nx and t.y == ny:
                if t.owner != u.owner:

                    army_size = 1

                    if army_size < 10:
                        print("Złoto zabrane przez armię")
                        u.carried_gold += t.gold
                        self.gold_transports.remove(t)
                    else:
                        print("Przejęto transport złota")
                        t.owner = u.owner

                    return      
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

        self.selected_castle.garrison.append(u)
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
                pygame.quit()
                import sys
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                # --- SKRÓTY UNIWERSALNE ---
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

                # --- RUCH JEDNOSTKĄ ---
                if self.screen == "map" and self.selected_unit:
                    if event.key == pygame.K_UP:    self.move_unit(self.selected_unit, 0, -1)
                    elif event.key == pygame.K_DOWN:  self.move_unit(self.selected_unit, 0, 1)
                    elif event.key == pygame.K_LEFT:  self.move_unit(self.selected_unit, -1, 0)
                    elif event.key == pygame.K_RIGHT: self.move_unit(self.selected_unit, 1, 0)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                
                # Obsługa kółka (Scroll)
                if event.button in [4, 5] and self.screen == "recruitment":
                    self.handle_recruitment_scroll(event)
                    continue # kontynuuj pętlę eventów

                if event.button == 1: # Lewy klik
                    # Jeśli info o jednostce jest otwarte, kliknięcie je zamyka
                    if self.screen == "unit_info":
                        self.screen = "recruitment"
                        continue
                    
                    # Główny procesor kliknięć
                    self.handle_mouse_click(mx, my)

    def handle_mouse_click(self, mx, my):
        # 1. OKNO POTWIERDZENIA DEMOLKI (Najwyższy priorytet)
        if self.demolish_confirm:
            if hasattr(self, 'demolish_yes') and self.demolish_yes.collidepoint(mx, my):
                self.demolish_castle(self.selected_castle)
                self.demolish_confirm = False
                return
            if hasattr(self, 'demolish_no') and self.demolish_no.collidepoint(mx, my):
                self.demolish_confirm = False
                return
            return # Blokuj inne kliknięcia gdy okno jest otwarte

        # 2. PRZEŁĄCZANIE EKRANÓW - REKRUTACJA I GARNIZON
        if self.screen == "recruitment":
            self.handle_recruitment_click(mx, my)
            return
        if self.screen == "garrison":
            self.handle_garrison_click(mx, my)
            return

        # 3. MENU ZAMKU
        if self.screen == "castle":
        #FORGE
            if self.forge_button and self.forge_button.collidepoint(mx, my):
                self.screen = "forge"
                return

            if self.workshop_button and self.workshop_button.collidepoint(mx, my):
                self.screen = "workshop"
                return

            if self.hospital_button and self.hospital_button.collidepoint(mx, my):
                self.screen = "hospital"
                return

            if hasattr(self, 'demolish_button') and self.demolish_button.collidepoint(mx, my):
                self.demolish_confirm = True; return

            if hasattr(self, 'back_button') and self.back_button.collidepoint(mx, my):
                self.screen = "map"; self.selected_castle = None; return

            self.handle_castle_click(mx, my)
            return

        # 4. EKRANY SPECJALNE (Powrót do zamku)
        if self.screen in ["forge", "workshop", "hospital", "school", "peasants", "court"]:
            if hasattr(self, 'back_button') and self.back_button.collidepoint(mx, my):
                self.screen = "castle"
                return
            
            # Jeśli to ekran chłopów, pozwól na ich specyficzne kliknięcia
            if self.screen == "peasants":
                self.handle_peasants_click(mx, my)
            return

        # 5. MAPA
        if self.screen == "map":
            # UI Paska górnego
            if self.show_top_ui and self.top_ui_full_area.collidepoint(mx, my):
                if self.btn_system.collidepoint(mx, my): self.active_dropdown = "System"; return
                if self.btn_mapa.collidepoint(mx, my): self.active_dropdown = "Mapa"; return
                if self.next_turn_button.collidepoint(mx, my): self.next_turn(); return
                return

            # UI Paska dolnego
            for i, rect in enumerate(self.action_buttons):
                if rect.collidepoint(mx, my):
                    if self.build_menu_open:
                        self.execute_build_action(i)
                    else:
                        if i == 4: self.build_menu_open = True
                        elif i == 5: # Przycisk REC na mapie (jeśli zamek wybrany)
                            if self.selected_castle: self.screen = "recruitment"
                    return

            self.handle_map_click(mx, my)
    def handle_garrison_click(self, mx, my):

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
                    for unit in list(self.selected_units):
                        castle.start_training(unit) 
                    
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
        # TWOJA ORYGINALNA LOGIKA SELEKCJI JEDNOSTEK
        # =====================================================

        if self.selected_castle:
            print("Garrison size:", len(self.selected_castle.garrison))

        index = self.click_on_garrison(mx, my)
        if index is None:
            return

        if index >= len(self.selected_castle.garrison):
            return

        unit = self.selected_castle.garrison[index]

        if unit in self.selected_units:
            self.selected_units.remove(unit)
            print("Odznaczono:", unit.type)
        else:
            if len(self.selected_units) < 10:
                self.selected_units.append(unit)

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
        if not self.selected_castle:
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

        for row in range(rows):
            for col in range(cols):
                index = row * cols + col

                x = start_x + col * offset_x
                y = start_y + row * offset_y

                rect = pygame.Rect(x, y, slot_w, slot_h)

                unit = None
                if index < len(self.selected_castle.garrison):
                    unit = self.selected_castle.garrison[index]

                # ramka
                if unit in self.selected_units:
                    pygame.draw.rect(screen, (255, 255, 0), rect, 4)
                else:
                    pygame.draw.rect(screen, (200, 200, 200), rect, 4)

                if unit:
                    pygame.draw.rect(screen, (80, 120, 200), (x+20, y+20, 60, 60))

                    pygame.draw.line(screen, (255,255,255), (x+8, y+8), (x+56, y+56), 2)
                    pygame.draw.line(screen, (255,255,255), (x+56, y+8), (x+8, y+56), 2)

                    text = font.render(unit.type[:3], True, (255,255,255))
                    screen.blit(text, (x + 6, y + 42))

        # BACK
        self.back_button = pygame.Rect(70, 600, 100, 40)
        pygame.draw.rect(screen, (120, 80, 80), self.back_button)
        screen.blit(font.render("BACK", True, (255,255,255)), (80,610))

        # INFO o zaznaczonych jednostkach
        info_y = 120

        for unit in self.selected_units:
            screen.blit(
                font.render(f"{unit.type} EXP: {unit.experience}", True, (255,255,255)),
                (40, info_y)
            )
            info_y += 25
        # przycisk produkcji wojska
        if "Koszary" in self.selected_castle.buildings:
            pygame.draw.rect(screen, (240, 120, 20), self.recruit_button)
            screen.blit(font.render("RECRUIT", True, (255,255,255)), (270,610))

        # HEAL BUTTON (hospital)
        if self.selected_castle and "hospital" in self.selected_castle.buildings:
            pygame.draw.rect(screen, (80, 160, 80), self.heal_button)
            screen.blit(font.render("HEAL", True, (255,255,255)), (490,610))

       # TRAIN BUTTON
        if self.selected_castle and "school" in self.selected_castle.buildings:
            pygame.draw.rect(screen, (160, 160, 80), self.train_button)
            screen.blit(font.render("TRAIN", True, (255,255,255)), (700,610))

        #send button
        pygame.draw.rect(screen, (160,120,60), self.button_send_army)
        screen.blit(font.render("RELEASE", True, (255,255,255)), (890,610))

    def draw_map(self, screen):
        TILE_SIZE = 32
        
        # 1. SIATKA (Uwzględnia kamerę)
        start_x = self.camera_x // TILE_SIZE
        start_y = self.camera_y // TILE_SIZE
        
        # Zakładamy mapę 100x100, rysujemy tylko wycinek widoczny na ekranie
        for y in range(max(0, start_y), min(100, start_y + 25)): 
            for x in range(max(0, start_x), min(100, start_x + 40)): 
                pos_x = (x * TILE_SIZE) - self.camera_x
                pos_y = (y * TILE_SIZE) - self.camera_y
                # Wewnątrz draw_map, w pętli rysującej kafelki:
                tile_type = self.map[y][x] 

                if tile_type == "#":
                    color = (139, 69, 19)   # Brązowy (Pułapka/Przeszkoda)
                elif tile_type == "$":
                    color = (255, 215, 0)   # Złoty (Skarb)
                elif tile_type == "S":
                    color = (255, 255, 255) # Biały (Świątynia)
                else:
                    color = (34, 139, 34)   # Zielony (Trawa)
                pygame.draw.rect(screen, color, (pos_x, pos_y, TILE_SIZE - 1, TILE_SIZE - 1))

            # 1. RYSOWANIE PUSTYCH PLACÓW (z listy castle_locations)
        for px, py in self.castle_locations:
            rect = pygame.Rect((px * 32) - self.camera_x, (py * 32) - self.camera_y, 64, 64)
            # Rysujemy tylko SZARĄ RAMKĘ (puste miejsce)
            pygame.draw.rect(screen, (150, 150, 150), rect, 2) 
            # Dodajemy napis, żeby mieć pewność
            # (jeśli masz zainicjowane self.font)
            # screen.blit(self.font.render("SITE", True, (100,100,100)), (rect.x + 5, rect.y + 5))

        # 2. RYSOWANIE ZBUDOWANYCH ZAMKÓW (z listy self.castles)
        for castle in self.castles:
            rect = pygame.Rect((castle.x * 32) - self.camera_x, (castle.y * 32) - self.camera_y, 64, 64)
            # Pełny NIEBIESKI blok (aktywny zamek)
            pygame.draw.rect(screen, (0, 0, 200), rect) 
            # Czarna grubsza obwódka
            pygame.draw.rect(screen, (0, 0, 0), rect, 3)
            # 3. RYSOWANIE JEDNOSTEK (Z poprawioną kamerą)
            tile_units = {}
            for player in self.players:
                for u in player.units:
                    # Rysujemy tylko jednostki, które są na mapie (x, y >= 0)
                    if u.x >= 0 and u.y >= 0:
                        key = (u.x, u.y)
                        tile_units[key] = tile_units.get(key, 0) + 1

        font = pygame.font.SysFont(None, 24)
        for (x, y), count in tile_units.items():
            # Tutaj DODANO odejmowanie kamery, inaczej jednostki "zostawały" w miejscu przy przewijaniu
            pos_x = (x * TILE_SIZE) - self.camera_x
            pos_y = (y * TILE_SIZE) - self.camera_y
            
            rect = pygame.Rect(pos_x + 8, pos_y + 8, 16, 16)
            pygame.draw.rect(screen, (255, 255, 0), rect) # Żółty kwadracik jednostki
            
            if count > 1:
                txt = font.render(str(count), True, (0, 0, 0))
                screen.blit(txt, (pos_x + 10, pos_y + 6))

        # 1. Definiujemy pozycję przycisku
        # Umieśćmy go w prawym górnym rogu
        self.next_turn_button = pygame.Rect(screen.get_width() - 180, 10, 170, 45)

        # 2. Pobieramy aktualną pozycję myszy
        mx, my = pygame.mouse.get_pos()

        # 3. Sprawdzamy, czy myszka znajduje się nad przyciskiem
        if self.next_turn_button.collidepoint(mx, my):
            # Rysujemy przycisk tylko, gdy mysz jest nad nim
            # Możesz dodać lekką przezroczystość, by wyglądało to nowocześniej
            s = pygame.Surface((self.next_turn_button.width, self.next_turn_button.height), pygame.SRCALPHA)
            s.fill((80, 120, 200, 200)) # Kolor z kanałem Alpha (200/255)
            screen.blit(s, (self.next_turn_button.x, self.next_turn_button.y))
            
            # Ramka
            pygame.draw.rect(screen, (255, 255, 255), self.next_turn_button, 2)
            
            # Tekst
            font = pygame.font.SysFont(None, 24)
            text = font.render(f"NEXT TURN ({self.turn})", True, (255, 255, 255))
            screen.blit(text, (self.next_turn_button.x + 15, self.next_turn_button.y + 12))

        # 6. MENU ZAMKU (Pojawia się na wierzchu mapy)
        if self.screen == "castle":
            self.draw_castle_menu(screen)

        # 7. EKRAN DEMOLKI (Przezroczysta nakładka na samym końcu)
        if self.demolish_confirm:
            # Tworzymy półprzezroczyste tło na całe okno
            s = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180)) 
            screen.blit(s, (0, 0))
            
            # Przycisk TAK (Czerwony)
            self.demolish_yes = pygame.Rect(screen.get_width()//2 - 110, 300, 100, 50)
            pygame.draw.rect(screen, (200, 0, 0), self.demolish_yes)
            screen.blit(font.render("TAK", True, (255,255,255)), (self.demolish_yes.x + 30, self.demolish_yes.y + 15))
            
            # Przycisk NIE (Szary)
            self.demolish_no = pygame.Rect(screen.get_width()//2 + 10, 300, 100, 50)
            pygame.draw.rect(screen, (100, 100, 100), self.demolish_no)
            screen.blit(font.render("NIE", True, (255,255,255)), (self.demolish_no.x + 35, self.demolish_no.y + 15))

    def draw_castle(self, screen):
        if self.demolish_confirm:
            return
        
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
            screen.blit(font.render("KUŹNIA", True, (255,255,255)),
                        (self.forge_button.x + 20, self.forge_button.y + 10))
        else:
            self.forge_button = None

        # WARSZTAT — tylko jeśli workshop zbudowany
        if self.selected_castle and "workshop" in self.selected_castle.buildings:
            self.workshop_button = pygame.Rect(290, 480, 160, 40)
            pygame.draw.rect(screen, (90, 90, 140), self.workshop_button)
            screen.blit(font.render("WARSZTAT", True, (255,255,255)),
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

        if "demolish" in self.menu_rects:
            if self.menu_rects["demolish"].collidepoint(mx, my):
                self.demolish_confirm = True
                return

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
        screen.fill((60, 50, 40)) # Ten sam brąz co w zamku, lub (30, 30, 30) dla ciemnego menu
        font = pygame.font.SysFont(None, 24)
        castle = self.selected_castle
        if not castle:
            return

        unit_types = self.recruitment_unit_types
        w = screen.get_width()
        h = screen.get_height()

        # ---- LEWE PRZYCISKI (Koordynaty z Twojego starego draw) ----
        self.info_button = pygame.Rect(120, 590, 100, 30)
        self.back_button = pygame.Rect(40, 630, 100, 30)
        self.buy_patent_button = pygame.Rect(160, 630, 140, 30)

        pygame.draw.rect(screen, (120, 120, 120), self.info_button)
        pygame.draw.rect(screen, (140, 80, 80), self.back_button)
        pygame.draw.rect(screen, (80, 140, 80), self.buy_patent_button)

        screen.blit(font.render("INFO", True, (255, 255, 255)), (150, 595))
        screen.blit(font.render("BACK", True, (255, 255, 255)), (65, 635))
        screen.blit(font.render("KUP PATENT", True, (255, 255, 255)), (170, 635))

        # ---- PANEL PATENTÓW (Koordynaty z Twojego starego draw) ----
        patents_panel = pygame.Rect(w - 310, 40, 250, 320)
        pygame.draw.rect(screen, (70, 50, 40), patents_panel)

        self.patent_rects = []
        current_patent_name = None
        for i in range(12):
            x = w - 300 + (i % 4) * 60
            y = 30 + (i // 4) * 90
            rect = pygame.Rect(x, y + 50, 50, 80)
            self.patent_rects.append(rect)

            if i == self.selected_patent_index:
                pygame.draw.rect(screen, (255, 255, 0), rect, 3)
                # Pobieramy nazwę dla statystyk jeśli zaznaczono patent
                if i < len(castle.patents) and castle.patents[i]:
                    p = castle.patents[i]
                    current_patent_name = p["unit_type"] if isinstance(p, dict) else p
            else:
                pygame.draw.rect(screen, (120, 120, 120), rect, 3)

            if i < len(castle.patents) and castle.patents[i] is not None:
                screen.blit(font.render("U", True, (255, 255, 0)), (x + 18, y + 80))

        # ---- PRODUKCJA INFO ----
        if castle.production_enabled:
            text = f"Produkcja: {castle.production_unit_type} ({castle.production_turns_left} tur)"
            color = (0, 255, 0)
        else:
            text = "Produkcja nieaktywna"
            color = (200, 200, 200)
        # y z pętli patentów jest dostępny tutaj (zostaje z ostatniego i)
        screen.blit(font.render(text, True, color), (w - 300, 380))

        # ---- PRAWE PRZYCISKI (Koordynaty z Twojego starego draw) ----
        self.remove_patent_button = pygame.Rect(w - 230, 590, 100, 30)
        self.start_prod_button = pygame.Rect(w - 300, 630, 120, 30)
        self.stop_prod_button = pygame.Rect(w - 160, 630, 120, 30)

        pygame.draw.rect(screen, (120, 80, 80), self.remove_patent_button)
        pygame.draw.rect(screen, (80, 140, 80), self.start_prod_button)
        pygame.draw.rect(screen, (140, 80, 80), self.stop_prod_button)

        screen.blit(font.render("USUŃ", True, (255, 255, 255)), (w - 210, 595))
        screen.blit(font.render("START", True, (255, 255, 255)), (w - 270, 635))
        screen.blit(font.render("STOP", True, (255, 255, 255)), (w - 130, 635))

        # ---- GOLD INFO ----
        screen.blit(font.render(f"Gold: {castle.gold}", True, (255, 215, 0)), (w // 2 - 30, 640))

        # ---- LISTA JEDNOSTEK (Logika przewijania i podświetlania) ----
        self.unit_list_rects.clear()
        start_x = 30
        start_y = 80
        box_w = 220
        box_h = 30
        gap = 2

        visible_count = 5
        center_index = 2 # Stałe środkowe miejsce (Pospolite Ruszenie tu ląduje na starcie)
        
        # KLUCZOWA POPRAWKA: Aktualizujemy zaznaczoną jednostkę na podstawie scrolla
        if self.selected_patent_index is None:
            idx_on_center = self.recruitment_scroll + center_index
            if 0 <= idx_on_center < len(unit_types):
                self.selected_unit_type = idx_on_center
            else:
                self.selected_unit_type = None

        for i in range(visible_count):
            scroll_index = self.recruitment_scroll + i
            
            # Rysujemy tylko istniejące elementy (brak ciemnych prostokątów w pustych polach)
            if 0 <= scroll_index < len(unit_types):
                unit_name = unit_types[scroll_index]
                y = start_y + i * (box_h + gap)
                rect = pygame.Rect(start_x, y, box_w, box_h)
                self.unit_list_rects.append(rect)
                
                has_patent = self.castle_has_patent(castle, unit_name)
                is_center = (i == center_index)

                # KOLOR TEKSTU WEDŁUG TWOICH WYMAGAŃ
                if is_center:
                    text_color = (255, 255, 255)    # Środek: Jasny biały
                elif has_patent:
                    text_color = (90, 90, 90)      # Kupiony: Wygaszony
                else:
                    text_color = (180, 180, 180)    # Reszta: Mniej jasny biały

                pygame.draw.rect(screen, (30, 30, 30), rect)
                screen.blit(font.render(unit_name, True, text_color), (rect.x + 10, rect.y + 8))

        # ---- INFO O WYBRANEJ JEDNOSTCE / PATENCIE ----
        # Wybieramy nazwę jednostki (albo z listy albo z zaznaczonego patentu)
        unit_name_to_show = None
        if self.selected_patent_index is not None:
            unit_name_to_show = current_patent_name
        elif self.selected_unit_type is not None:
            unit_name_to_show = unit_types[self.selected_unit_type]

        if unit_name_to_show:
            stats = UNIT_STATS[unit_name_to_show]
            screen.blit(font.render(f"Jednostka: {unit_name_to_show}", True, (255, 255, 255)), (180, 250))
            screen.blit(font.render(f"ATK: {stats['attack']}", True, (255, 255, 255)), (180, 300))
            screen.blit(font.render(f"DEF: {stats['defense']}", True, (255, 255, 255)), (180, 350))
            screen.blit(font.render(f"MOR:{stats['morale']}", True, (255, 255, 255)), (320, 300))
            screen.blit(font.render(f"MOV: {stats['moves']}", True, (255, 255, 255)), (320, 350))
            screen.blit(font.render(f"ZME: {stats['fatigue']}", True, (255, 255, 255)), (460, 300))
            screen.blit(font.render(f"EXP: {stats['exp']}", True, (255, 255, 255)), (460, 350))
            screen.blit(font.render(f"Patent: {stats['patent_cost']}", True, (255, 255, 0)), (40, 500))
            screen.blit(font.render(f"Prod: {stats['production_cost']}", True, (255, 255, 0)), (200, 500))
            screen.blit(font.render(f"Tury: {stats['production_time']}", True, (255, 255, 0)), (360, 500))

        # ---- SCROLL BUTTONS ----
        pygame.draw.rect(screen, (100, 100, 100), self.scroll_up_button)
        screen.blit(font.render("▲", True, (255, 255, 255)), (self.scroll_up_button.x + 12, self.scroll_up_button.y + 8))
        pygame.draw.rect(screen, (100, 100, 100), self.scroll_down_button)
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
            if not self.demolish_confirm:
                self.draw_top_bar(screen)
                self.draw_bottom_bar(screen)

        # 2. LOGIKA EKRANU ZAMKU
        elif self.screen == "castle":
            self.draw_castle(screen) 

        # 3. LOGIKA EKRANU GARNIZONU / REKRUTACJI
        elif self.screen == "garrison":
            self.draw_garrison(screen)
        
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
        else:
            self.draw_pygame(screen)

            #demolowanie zamku
        if self.demolish_confirm:
            self.draw_demolish_confirm(screen)
            pygame.draw.rect(screen, (0,255,0), (0,0,50,50))
            
        elif self.screen == "workshop":
            self.draw_workshop(screen)
            
        elif self.screen == "hospital":
            self.draw_hospital(screen)
            
        elif self.screen == "school":
            self.draw_school(screen)
            
        elif self.screen == "unit_info":
            self.draw_unit_info(screen)

        # 6. NAKŁADKI (Zawsze na wierzchu)
        if self.demolish_confirm:
            # Przekazujemy tylko screen, bo w definicji draw_demolish_confirm masz tylko screen
            self.draw_demolish_confirm(screen)
    def draw_demolish_confirm(self, screen):
        # ===== PRZEZROCZYSTA WARSTWA =====
        # Tworzymy powierzchnię o wielkości całego ekranu
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Czerń, 180 = wyraźne przyciemnienie mapy
        screen.blit(overlay, (0, 0))

        # ===== OKNO MODALNE =====
        rect = pygame.Rect(0, 0, 320, 160)
        rect.center = (screen.get_width() // 2, screen.get_height() // 2) # Środek ekranu
        
        # Cień okna
        pygame.draw.rect(screen, (20, 20, 20), (rect.x + 5, rect.y + 5, rect.width, rect.height))
        # Główne okno
        pygame.draw.rect(screen, (50, 50, 50), rect)
        pygame.draw.rect(screen, (200, 180, 100), rect, 3) # Złota ramka

        font = pygame.font.SysFont(None, 32)
        text = font.render("Zburzyć twierdzę?", True, (255, 255, 255))
        screen.blit(text, (rect.centerx - text.get_width() // 2, rect.y + 25))

        # Przyciski
        self.demolish_yes = pygame.Rect(rect.x + 40, rect.y + 85, 90, 45)
        self.demolish_no = pygame.Rect(rect.x + 190, rect.y + 85, 90, 45)

        # Rysowanie przycisków (z prostym hoverem)
        mx, my = pygame.mouse.get_pos()
        color_yes = (100, 200, 100) if self.demolish_yes.collidepoint(mx, my) else (60, 130, 60)
        color_no = (200, 100, 100) if self.demolish_no.collidepoint(mx, my) else (130, 60, 60)

        pygame.draw.rect(screen, color_yes, self.demolish_yes)
        pygame.draw.rect(screen, color_no, self.demolish_no)
        
        # Napisy na przyciskach
        btn_font = pygame.font.SysFont(None, 28, bold=True)
        txt_yes = btn_font.render("TAK", True, (255, 255, 255))
        txt_no = btn_font.render("NIE", True, (255, 255, 255))
        
        screen.blit(txt_yes, (self.demolish_yes.centerx - txt_yes.get_width() // 2, self.demolish_yes.centery - txt_yes.get_height() // 2))
        screen.blit(txt_no, (self.demolish_no.centerx - txt_no.get_width() // 2, self.demolish_no.centery - txt_no.get_height() // 2))

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
        screen.blit(font.render("DEMOLISH", True, (255,255,255)), (menu_x+10, menu_y+50))

        # MURY
        self.wall_button = pygame.Rect(menu_x, menu_y+80, 160, 40)
        pygame.draw.rect(screen, (100, 100, 100), self.wall_button)
        screen.blit(font.render("UPGRADE WALL", True, (255,255,255)), (menu_x+10, menu_y+90))

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

    def handle_map_click(self, mx, my):
        if mx > 800: 
            return

        tile_x = (mx + self.camera_x) // 32
        tile_y = (my + self.camera_y) // 32

        # 1. NAJPIERW SPRAWDZAMY CZY KLIKNIĘTO W ZAMEK
        # Robimy to najpierw, żeby kliknięcie w zamek zawsze go otwierało, 
        # niezależnie od tego czy mamy zaznaczoną jednostkę czy nie.
        for castle in self.castles:
            if castle.x <= tile_x <= castle.x + 1 and castle.y <= tile_y <= castle.y + 1:
                if castle.destroyed:
                    print("To są ruiny.")
                    return

                # Jeśli mamy jednostkę i klikamy w zamek obok niej - najpierw ją przesuń
                if self.selected_unit:
                    u = self.selected_unit
                    dx = tile_x - u.x
                    dy = tile_y - u.y
                    if max(abs(dx), abs(dy)) == 1:
                        self.move_unit(u, dx, dy)
                        # Nie dajemy tu return! Pozwalamy kodowi przejść niżej, 
                        # aby po ruchu od razu otworzył menu zamku.

                self.selected_castle = castle
                self.selected_unit = None 
                self.screen = "castle"
                print(f"Opened castle at {castle.x}, {castle.y}")
                return 

        # 2. KLIKNIĘCIE W JEDNOSTKĘ (Zaznaczanie)
        for player in self.players:
            for unit in player.units:
                if unit.x == tile_x and unit.y == tile_y:
                    if unit.owner == self.players[self.current_player]:
                        self.selected_unit = unit
                        self.selected_castle = None
                        return

        # 3. RUCH JEDNOSTKI (Tylko jeśli nie kliknięto w zamek ani inną jednostkę)
        if self.selected_unit:
            u = self.selected_unit
            dx = tile_x - u.x
            dy = tile_y - u.y
            if max(abs(dx), abs(dy)) == 1:
                self.move_unit(u, dx, dy)
                return

        # Puste pole
        self.selected_unit = None
        self.selected_castle = None

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
        # MUSIMY zdefiniować Recty tu identycznie jak w Draw (najlepiej użyć tych samych zmiennych)
        w = pygame.display.get_surface().get_width()

        # Logika przycisków piramid (Lewa)
        if self.info_button.collidepoint(mx, my):
            # Wybieramy nazwę jednostki (ze środka listy lub z patentu)
            u_name = None
            if self.selected_patent_index is not None:
                p = castle.patents[self.selected_patent_index]
                u_name = p["unit_type"] if isinstance(p, dict) else p
            elif self.selected_unit_type is not None:
                u_name = self.recruitment_unit_types[self.selected_unit_type]

            if u_name:
                stats = UNIT_STATS[u_name]
                # Formatuje tekst: Pierwsza linia to nagłówek, reszta to opis
                self.unit_info_text = (f"{stats['description']}"
                )
                self.screen = "unit_info"
            return
        if self.back_button.collidepoint(mx, my):
            self.screen = "garrison"
            return
        if self.buy_patent_button.collidepoint(mx, my):
            if self.selected_unit_type is not None:
                castle.buy_patent(unit_types[self.selected_unit_type])
            return

        # Logika przycisków piramid (Prawa)
        if self.start_prod_button.collidepoint(mx, my):
            if self.selected_patent_index is not None:
                p = castle.patents[self.selected_patent_index]
                u_name = p["unit_type"] if isinstance(p, dict) else p
                castle.start_production(u_name)
            return
        if self.stop_prod_button.collidepoint(mx, my):
            castle.stop_production()
            return
        if self.remove_patent_button.collidepoint(mx, my):
            if self.selected_patent_index is not None:
                castle.patents[self.selected_patent_index] = None
                castle.stop_production() # Zatrzymuje jeśli to była ta jednostka
            return

        # Scroll i Lista
        if self.scroll_up_button.collidepoint(mx, my):
            self.recruitment_scroll = max(-2, self.recruitment_scroll - 1)
            return
        if self.scroll_down_button.collidepoint(mx, my):
            self.recruitment_scroll = min(len(unit_types)-3, self.recruitment_scroll + 1)
            return

        # --- PANCERNE KLIKANIE W LISTĘ ---
        start_x = 30
        start_y = 80
        box_w = 220
        box_h = 30
        gap = 2
        visible_count = 5

        # Sprawdzamy czy myszka jest w poziomie (X) w obrębie listy
        if start_x <= mx <= start_x + box_w:
            # Obliczamy, w który slot (0-4) kliknął użytkownik na podstawie Y
            relative_y = my - start_y
            slot_index = relative_y // (box_h + gap)

            # Sprawdzamy czy kliknięcie mieści się w pionie (Y) widocznej listy
            if 0 <= slot_index < visible_count:
                # Obliczamy realny indeks jednostki w całej liście
                clicked_unit_idx = self.recruitment_scroll + int(slot_index)

                # Sprawdzamy czy pod tym indeksem faktycznie jest jednostka
                if 0 <= clicked_unit_idx < len(unit_types):
                    # Centrowanie: ustawiamy scroll tak, by kliknięta jednostka była w slocie nr 2
                    self.recruitment_scroll = clicked_unit_idx - 2
                    self.selected_unit_type = clicked_unit_idx
                    self.selected_patent_index = None
                    return
        # Kliknięcie w patenty
        for i, rect in enumerate(self.patent_rects):
            if rect.collidepoint(mx, my):
                if i < len(castle.patents) and castle.patents[i]:
                    self.selected_patent_index = i
                    self.selected_unit_type = None
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

        if not castle:
            return

        # === WYRZUĆ WSZYSTKIE JEDNOSTKI Z POLA ZAMKU ===
        for player in self.players:
            for unit in player.units:

                if unit.x == castle.x and unit.y == castle.y:

                    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]:
                        nx = unit.x + dx
                        ny = unit.y + dy

                        if 0 <= nx < self.map_width and 0 <= ny < self.map_height:

                            if not self.get_unit_at(nx, ny):
                                unit.x = nx
                                unit.y = ny
                                break

        # === ZBURZ ===
        castle.destroyed = True

        if castle.owner and castle in castle.owner.castles:
            castle.owner.castles.remove(castle)

        castle.garrison.clear()
        castle.owner = None

        # === WYJDŹ Z UI ===
        self.selected_castle = None
        self.selected_unit = None
        self.selected_units.clear()
        self.screen = "map"

    def draw_forge(self, screen):
        screen.fill((40, 70, 70))  # tło "kamień"

        font_title = pygame.font.SysFont(None, 48)
        font_text = pygame.font.SysFont(None, 24)

        # PANEL
        panel = pygame.Rect(120, 80, 760, 420)
        pygame.draw.rect(screen, (120, 90, 60), panel)
        pygame.draw.rect(screen, (200, 170, 90), panel, 6)

        # TYTUŁ
        title = font_title.render("Kuźnia", True, (255, 220, 120))
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

        title = font_title.render("Warsztat", True, (220, 220, 255))
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

        # Poprawione kierunki z brakującymi przecinkami
        directions = [
            (-1, 1), (0, 1), (1, 1), (2, 1),
            (-1, 0),                 (2, 0),
            (-1,-1),                 (2,-1),
            (-1,-2), (0,-2), (1,-2), (2,-2)
        ]

        # Pobieramy aktualne pozycje wszystkich jednostek na mapie
        occupied = {(u.x, u.y) for u in self.units}

        spawn_pos = None
        for dx, dy in directions:
            nx, ny = castle.x + dx, castle.y + dy
            # Sprawdzamy czy pole jest wolne i czy mieści się na mapie
            if 0 <= nx < len(self.map[0]) and 0 <= ny < len(self.map):
                if (nx, ny) not in occupied and self.map[ny][nx] in [".", "0", " "]:
                    spawn_pos = (nx, ny)
                    break

        if not spawn_pos:
            print("Brak miejsca wokół zamku")
            return

        nx, ny = spawn_pos
        
        # Tworzymy jednostkę "Armia" (upewnij się, że klasa Unit to obsługuje)
        army = Unit("army", nx, ny, player)
        army.move_points = 1
        army.garrison = []

        # Przenosimy jednostki z garnizonu zamku do garnizonu armii
        for u in list(self.selected_units):
            castle.garrison.remove(u)
            army.garrison.append(u)

        # Dodajemy armię do list systemowych
        player.units.append(army)
        self.units.append(army) # WAŻNE: dodanie do globalnej listy jednostek

        self.selected_units.clear()
        #self.screen = "map" # Automatyczny powrót na mapę, by zobaczyć nową jednostkę
        print(f"Wypuszczono armię na pozycję {nx}, {ny}")
    
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
        scroll_speed = 10  # Prędkość przesuwania w pikselach

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.camera_x -= scroll_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.camera_x += scroll_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.camera_y -= scroll_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.camera_y += scroll_speed

        # Ograniczenia kamery (mapa 100x100, kafelek 32px -> 3200px szerokości)
        # Zakładając okno 800x600:
        self.camera_x = max(0, min(self.camera_x, 3200 - 800))
        self.camera_y = max(0, min(self.camera_y, 3200 - 600))

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
            labels = ["MOVE", "ATK", "SPL", "WAIT", "BUILD", "REC"]

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

        return None
    