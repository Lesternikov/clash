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
        self.heal_button = pygame.Rect(460, 600, 100, 40)
        self.train_button = pygame.Rect(680, 600, 100, 40)
        self.recruit_button = pygame.Rect(260, 600, 100, 40)
        self.selected_unit_type = None
        self.menu_button = pygame.Rect(860, 40, 140, 40)
        self.menu_rects = {}
        self.build_rects = {}
        self.next_turn_button = pygame.Rect(460, 10, 160, 40)
        self.menu_open = False
        self.build_open = False
        self.victories = 0
        self.defeats = 0
        self.court_button = pygame.Rect(40, 140, 160, 40)
        self.exit_button = pygame.Rect(20, 20, 120, 50)
        self.prison_slots = [PrisonSlot(), PrisonSlot(), PrisonSlot()]
        self.unit_scroll = 0
        self.unit_types = [UNIT_STATS]
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
        
        # BACK działanie
        self.back_button = pygame.Rect(90, 600, 100, 40)
        
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

    def load(self, map_file, fac_file):
        self.map = load_map(map_file)
        self.objects = load_fac_objects(fac_file)

        castle_places = self.objects.get("zamek_place", [])

        for i, (x, y) in enumerate(castle_places):
            owner = self.players[i] if i < len(self.players) else None
            
            c = Castle(x // 5, y // 10, owner)
            c.gold = 20000
            self.castles.append(c)

    # jednostki startowe przy zamkach graczy
        for c in self.castles:
            if c.owner:
                self.add_unit(Unit("lekka_piechota", c.x, c.y + 1, c.owner))


        print("DEBUG castles:", len(self.castles))
        print("DEBUG units:", len(self.units))
        map_width = len(self.map[0]) * 32
        self.next_turn_button = pygame.Rect(map_width + 20, 10, 170, 40)

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
            castle.next_turn()
            castle.update_production(self)

        self.selected_unit = None
        self.selected_castle = None
        for castle in self.castles:
            castle.collect_taxes()


    def move_unit(self, unit, dx, dy):
        if unit.move_points <= 0:
            print("Brak punktów ruchu")
            return

        nx = unit.x + dx
        ny = unit.y + dy

        if ny < 0 or ny >= len(self.map):
            return
        if nx < 0 or nx >= len(self.map[0]):
            return

        if self.map[ny][nx] != ".":
            return

        unit.x = nx
        unit.y = ny
        unit.move_points -= 1

    def reset_units(self):
        for u in self.units:
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

    # blokada terenu
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
            if castle.x == nx and castle.y == ny:
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
                    if castle.position() == group.position():
                        if castle.owner == group.owner:
                            castle.peasants += group.amount
                            self.peasant_groups.remove(group)
                            print("Chłopi dotarli do zamku")
                            return
            for t in self.gold_transports:
                for castle in self.castles:
                    if castle.position() == t.position():
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
        if not self.selected_castle:
            print("DEBUG: brak wybranego zamku")
            return

        castle = self.selected_castle

        print("DEBUG: szkolenie jednostek:", len(self.selected_units))

        for unit in self.selected_units:
            castle.start_training(unit)
            print("DEBUG: rozpoczęto szkolenie")

        self.selected_units.clear()

    def handle_events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return "quit"

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    self.train_selected_garrison_units()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                # ===== BACK z dworu =====
                if self.screen == "court":
                    if hasattr(self, "back_button") and self.back_button.collidepoint(mx, my):
                        print("BACK pressed")
                        self.screen = "castle"
                        return

                # ===== MAPA =====
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    self.handle_mouse_click(mx, my)


                # ===== ZAMEK =====
                elif self.screen == "castle":
                    if self.exit_button.collidepoint(mx, my):
                        self.screen = "map"

        return None

    def handle_mouse_click(self, mx, my):
        print("CLICK:", self.screen, mx, my)

        # UI screens
        if self.screen == "court":
            self.handle_court_click(mx, my)
            return

        if self.screen == "peasants":
            self.handle_peasants_click(mx, my)
            return

        if self.screen == "recruitment":
            self.handle_recruitment_click(mx, my)
            return

        if self.screen == "garrison":
            self.handle_garrison_click(mx, my)
            return

        # map / castle logic
        if self.screen == "castle":
            self.handle_castle_click(mx, my)
            return

        if self.screen == "map":
            self.handle_map_click(mx, my)
            return

   
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
        if (
            "Koszary" in castle.buildings
            and self.recruit_button
            and self.recruit_button.collidepoint(mx, my)
        ):
            self.screen = "recruitment"
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
                    castle.start_training_group(self.selected_units)
                    self.selected_units.clear()
                    print("Przeszkolono jednostki")
                else:
                    print("Brak zaznaczonych jednostek")
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
                print("Zaznaczono:", unit.type)
            else:
                print("Można zaznaczyć max 10 jednostek")


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
        elif self.screen == "court":
            self.draw_court(screen)
            return
    def draw_garrison(self, screen):
        if not self.selected_castle:
            return

        start_x = 100
        start_y = 120

        cols = 6
        rows = 2

        font = pygame.font.SysFont(None, 20)

        for row in range(rows):
            for col in range(cols):
                index = row * cols + col   # ← BRAKOWAŁO TEGO

                x = start_x + col * 130
                y = start_y + row * 210

                rect = pygame.Rect(x, y, 100, 180)

                unit = None
                if index < len(self.selected_castle.garrison):
                    unit = self.selected_castle.garrison[index]

                if unit in self.selected_units:
                    pygame.draw.rect(screen, (255, 255, 0), rect, 4)
                else:
                    pygame.draw.rect(screen, (200, 200, 200), rect, 4)

                if index < len(self.selected_castle.garrison):
                    unit = self.selected_castle.garrison[index]

                    # tło jednostki
                    pygame.draw.rect(screen, (80, 120, 200), (x+20, y+20, 60, 60))

                    # prosty "X"
                    pygame.draw.line(screen, (255,255,255), (x+8, y+8), (x+56, y+56), 2)
                    pygame.draw.line(screen, (255,255,255), (x+56, y+8), (x+8, y+56), 2)

                    # nazwa
                    text = font.render(unit.type[:3], True, (255,255,255))
                    screen.blit(text, (x + 6, y + 42))


    # BACK button kwadrat
        self.back_button = pygame.Rect(70, 600, 100, 40)
        pygame.draw.rect(screen, (120, 80, 80), self.back_button)

        font = pygame.font.SysFont(None, 24)
        screen.blit(font.render("BACK", True, (255,255,255)), (80,610))

        # INFO o zaznaczonych jednostkach
        info_y = 120

        for unit in self.selected_units:
            screen.blit(
                font.render(f"{unit.type} EXP: {unit.experience}", True, (255,255,255)),
                (40, info_y)
            )
            info_y += 25


        # HEAL BUTTON (hospital)
        if self.selected_castle and "hospital" in self.selected_castle.buildings:
            pygame.draw.rect(screen, (80, 160, 80), self.heal_button)
            screen.blit(font.render("HEAL", True, (255,255,255)), (490,610))

       # TRAIN BUTTON
        if self.selected_castle and "school" in self.selected_castle.buildings:
            pygame.draw.rect(screen, (160, 160, 80), self.train_button)
            screen.blit(font.render("TRAIN", True, (255,255,255)), (700,610))

   
    # przycisk produkcji wojska
        if "Koszary" in self.selected_castle.buildings:
            pygame.draw.rect(screen, (240, 120, 20), self.recruit_button)
            screen.blit(font.render("RECRUIT", True, (255,255,255)), (270,610))
           
    def draw_map(self, screen):
        tile = 32
        font = pygame.font.SysFont(None, 18)

        for y, row in enumerate(self.map):
            for x, cell in enumerate(row):
                rect = pygame.Rect(x * tile, y * tile, tile, tile)

                pygame.draw.rect(screen, (60, 140, 60), rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)

    # zamki
        for c in self.castles:
            rect = pygame.Rect(c.x * tile, c.y * tile, tile, tile)
            pygame.draw.rect(screen, (150, 150, 255), rect)

    # jednostki
        for u in self.units:
            rect = pygame.Rect(u.x * tile + 8, u.y * tile + 8, 16, 16)
            pygame.draw.rect(screen, (255, 255, 0), rect)

    # selected unit
        if self.selected_unit:
            rect = pygame.Rect(
                self.selected_unit.x * tile,
                self.selected_unit.y * tile,
                tile,
                tile,
            )
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)

    # ← PRZYCISK ZAWSZE RYSUJEMY
        pygame.draw.rect(screen, (80, 120, 200), self.next_turn_button)

        font = pygame.font.SysFont(None, 24)
        text = f"NEXT TURN ({self.turn})"
        screen.blit(font.render(text, True, (255,255,255)),
                    (self.next_turn_button.x + 10, self.next_turn_button.y + 10))

    
    def draw_castle(self, screen):
        screen_width = screen.get_width()
        screen_height = screen.get_height()

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
        self.garrison_button = pygame.Rect(40, 120, 160, 40)
        pygame.draw.rect(screen, (80, 80, 160), self.garrison_button)
        screen.blit(font.render("Garrison", True, (255,255,255)),
                    (self.garrison_button.x + 10, self.garrison_button.y + 10))

    # --- BUTTON: BACK ---
        self.back_button = pygame.Rect(40, 200, 160, 40)
        pygame.draw.rect(screen, (120, 80, 80), self.back_button)
        screen.blit(font.render("BACK", True, (255,255,255)), (50,210))

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

    # --- BUTTON: COURT ---
        self.court_button = pygame.Rect(420, 100, 160, 40)
        pygame.draw.rect(screen, (220, 80, 80), self.court_button)
        screen.blit(font.render("DWÓR", True, (255,225,255)), (470,110))

    def draw_recruitment(self, screen):
        font = pygame.font.SysFont(None, 24)
        castle = self.selected_castle
        if not castle:
            return
        unit_types = self.recruitment_unit_types


        w = screen.get_width()
        h = screen.get_height()

        # =====================================================
        # LEWE PRZYCISKI (piramida)
        # =====================================================

        self.info_button = pygame.Rect(120, 590, 100, 30)
        self.back_button = pygame.Rect(40, 630, 100, 30)
        self.buy_patent_button = pygame.Rect(160, 630, 140, 30)

        pygame.draw.rect(screen, (120,120,120), self.info_button)
        pygame.draw.rect(screen, (140,80,80), self.back_button)
        pygame.draw.rect(screen, (80,140,80), self.buy_patent_button)

        screen.blit(font.render("INFO", True, (255,255,255)), (150,595))
        screen.blit(font.render("BACK", True, (255,255,255)), (65,635))
        screen.blit(font.render("KUP PATENT", True, (255,255,255)), (170,635))

        # =====================================================
        # PANEL PRAWY — PATENTY (12)
        # =====================================================

        patents_panel = pygame.Rect(w-310, 40, 250, 320)
        pygame.draw.rect(screen, (70,50,40), patents_panel)

        for i in range(12):
            x = w-300 + (i % 4)*60
            y = 30 + (i // 4)*90
            rect = pygame.Rect(x, y + 50, 50, 80,)
            pygame.draw.rect(screen, (120,120,120), rect, 3)

            if i < len(castle.patents):
                screen.blit(font.render("U", True, (255,255,0)), (x+18, y+80))

        # =====================================================
        # PRODUKCJA INFO
        # =====================================================
        if castle.production_enabled:
            text = f"Produkcja: {castle.production_unit_type} ({castle.production_turns_left} tur)"
            color = (0,255,0)
        else:
            text = "Produkcja nieaktywna"
            color = (200,200,200)

        screen.blit(font.render(text, True, color), (x - 150, y + 300))

        # =====================================================
        # PRAWE PRZYCISKI
        # =====================================================

        self.remove_patent_button = pygame.Rect(w-230, 590, 100, 30)
        self.start_prod_button = pygame.Rect(w-300, 630, 120, 30)
        self.stop_prod_button = pygame.Rect(w-160, 630, 120, 30)

        pygame.draw.rect(screen, (120,80,80), self.remove_patent_button)
        pygame.draw.rect(screen, (80,140,80), self.start_prod_button)
        pygame.draw.rect(screen, (140,80,80), self.stop_prod_button)

        screen.blit(font.render("USUŃ", True, (255,255,255)), (w-210,595))
        screen.blit(font.render("START", True, (255,255,255)), (w-270,635))
        screen.blit(font.render("STOP", True, (255,255,255)), (w-130,635))

        # =====================================================
        # GOLD INFO
        # =====================================================

        screen.blit(font.render(f"Gold: {castle.gold}", True, (255,215,0)),
                    (w//2 - 30, 640))

        # =====================================================
        # LISTA PATENTÓW
        # =====================================================
        if self.selected_unit_type is not None:
            unit_name = unit_types[self.selected_unit_type]
            stats = UNIT_STATS[unit_name]

            screen.blit(font.render(f"ATK: {stats['attack']}", True, (255,255,255)), (180,300))
            screen.blit(font.render(f"DEF: {stats['defense']}", True, (255,255,255)), (180,400))
            screen.blit(font.render(f"MOR:{stats['morale']}", True, (255,255,255)), (320,300))
            screen.blit(font.render(f"MOV: {stats['moves']}", True, (255,255,255)), (320,400))
            screen.blit(font.render(f"ZME: {stats['fatigue']}", True, (255,255,255)), (460,300))
            screen.blit(font.render(f"EXP: {stats['exp']}", True, (255,255,255)), (460,400))
            screen.blit(font.render(f"Patent: {stats['patent_cost']}", True,(255,255,0)), (40,500))
            screen.blit(font.render(f"Prod: {stats['production_cost']}", True,(255,255,0)), (200,500))
            screen.blit(font.render(f"Tury: {stats['production_time']}", True,(255,255,0)), (360,500))


            self.unit_list_rects.clear()

        #Rysowanie listy
        font = pygame.font.SysFont(None, 24)

        self.unit_list_rects.clear()

        start_x = 30
        start_y = 80
        box_w = 220
        box_h = 30
        gap = 2

        visible_units = self.recruitment_unit_types[
            self.recruitment_scroll:
            self.recruitment_scroll + self.visible_recruitment_count
        ]

        for i, unit_type in enumerate(visible_units):
            y = start_y + i * (box_h + gap)

            rect = pygame.Rect(start_x, y, box_w, box_h)
            self.unit_list_rects.append(rect)

            global_index = self.recruitment_scroll + i

            # tło zawsze takie samo
            pygame.draw.rect(screen, (30, 30, 30), rect)

            # kolor tekstu zależy od zaznaczenia
            text_color = (180, 180, 180)
            if self.selected_unit_type == global_index:
                text_color = (255, 255, 255)

            stats = UNIT_STATS[unit_type]
            text = f"{unit_type}"

            screen.blit(font.render(text, True, text_color),
                        (rect.x + 10, rect.y + 8))

            #przyciski przewijania wojska
            pygame.draw.rect(screen, (100,100,100), self.scroll_up_button)
            screen.blit(font.render("▲", True, (255,255,255)),
                        (self.scroll_up_button.x+12, self.scroll_up_button.y+8))

            pygame.draw.rect(screen, (100,100,100), self.scroll_down_button)
            screen.blit(font.render("▼", True, (255,255,255)),
                        (self.scroll_down_button.x+12, self.scroll_down_button.y+8))
                                                                
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

        # ===== BACK BUTTON =====
        self.back_button = pygame.Rect(20, 20, 120, 40)
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

        start_x = 120
        y = 20
        slot_w = 140

        for i in range(5):
            rect = pygame.Rect(start_x + i*slot_w, y, 120, 30)
            pygame.draw.rect(screen, (120,120,120), rect)

            if i < len(self.players):
                p = self.players[i]
                pygame.draw.rect(screen, p.color, rect)
                draw_text(screen, p.name, rect.x + 10, rect.y + 5)


    def draw_court_header(self, screen):
        screen.fill((255, 0, 0))
        x = 200 
        y = 100
        for p in self.players:
            pygame.draw.rect(screen, p.color, (x, y, 120, 30))
            draw_text(screen,p.name, x + 10, y + 10)
            x += 140
        self.back_button = pygame.Rect(20, 10, 100, 40)
        draw_button(screen, "BACK", 20, 10, 100, 40)

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
        if self.screen == "court":
            self.draw_court(screen)
        else:
            self.draw_pygame(screen)


    def select_castle(self, x, y):
        for c in self.castles:
            if c.x == x and c.y == y:
                self.selected_castle = c
                print("Wybrano zamek:", x, y)
                return

        self.selected_castle = None

    def create_unit(self, unit_type, x, y, owner):
        u = Unit(unit_type, x, y, owner)
        self.add_unit(u)
        return u
    def click_on_recruitment(self, mx, my):
        for i, rect in enumerate(self.unit_list_rects):
            if rect.collidepoint(mx, my):
                return self.recruitment_scroll + i

        return None

    def start_recruitment(self, index):
        
        if index is None:
            return

        if index is None:
            return
        
        utype = UNIT_STATS[index]
        cost = 50
        castle = self.selected_castle

        if castle.gold < cost:
            print("Za mało złota")
            return

        if castle.gold < cost:
            print("Za mało złota")
            return
        
        castle.gold -= cost
        castle.start_production(utype)

        print("Rozpoczęto produkcję:", utype)
        self.screen = "garrison"
    def click_on_garrison(self, mx, my):
        start_x = 500
        start_y = 120
        slot = 64

        cols = 2
        rows = 6

        if not (start_x <= mx < start_x + cols * slot):
            return None
        if not (start_y <= my < start_y + rows * slot):
            return None

        col = (mx - start_x) // slot
        row = (my - start_y) // slot

        return int(row * cols + col)
    
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
            pygame.draw.rect(screen, (60, 60, 60), rect)
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

        sub_x = menu_x - 160
        sub_y = menu_y

        buildings = ["hospital", "school", "Koszary", "forge", "workshop"]
        self.build_rects.clear()

        for i, b in enumerate(buildings):
            rect = pygame.Rect(sub_x, sub_y + i*40, 160, 40)
            pygame.draw.rect(screen, (80, 80, 120), rect)
            screen.blit(font.render(b, True, (255,255,255)),
                        (sub_x+10, sub_y+10+i*40))

            self.build_rects[b] = rect
    
    def handle_court_click(self, mx, my):

        # EXIT
        exit_rect = pygame.Rect(20, 10, 100, 40)
        if exit_rect.collidepoint(mx, my):
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
        tile_x = mx // 32
        tile_y = my // 32

        if tile_y < 0 or tile_y >= len(self.map):
            return
        if tile_x < 0 or tile_x >= len(self.map[0]):
            return

        # jednostki
        for player in self.players:
            for unit in player.units:
                if unit.x == tile_x and unit.y == tile_y:
                    self.selected_unit = unit
                    self.selected_castle = None
                    print("Selected unit:", unit.type)
                    return

        # zamki
        for castle in self.castles:
            if castle.x == tile_x and castle.y == tile_y:
                self.selected_castle = castle
                self.selected_unit = None
                self.screen = "castle"   # TO BYŁO POTRZEBNE
                print("Selected castle")
                return

        self.selected_unit = None
        self.selected_castle = None

    def handle_castle_click(self, mx, my):
        if not self.selected_castle:
            return

        if self.back_button.collidepoint(mx, my):
            self.screen = "map"
            self.selected_castle = None
            return

        if self.garrison_button and self.garrison_button.collidepoint(mx, my):
            self.screen = "garrison"
            return

        if (
            "Koszary" in self.selected_castle.buildings
            and self.koszary_button
            and self.koszary_button.collidepoint(mx, my)
        ):
            self.screen = "recruitment"
            return

        if self.peasant_button.collidepoint(mx, my):
            self.screen = "peasants"
            return

        if self.court_button.collidepoint(mx, my):
            self.screen = "court"
            return

        if self.menu_open:
            for name, rect in self.build_rects.items():
                if rect.collidepoint(mx, my):
                    if self.selected_castle.build(name):
                        self.menu_open = False
                        self.build_open = False
                    return

    def handle_recruitment_click(self, mx, my):
        castle = self.selected_castle
        if not castle:
            return

        # BACK
        if self.back_button.collidepoint(mx, my):
            self.screen = "garrison"
            return

        # lista jednostek
        index = self.click_on_recruitment(mx, my)
        if index is not None:
            if index < len(self.recruitment_unit_types):
                self.selected_unit_type = index
                print("Selected unit type:", self.recruitment_unit_types[index])
            return

        # BUY PATENT
        if self.buy_patent_button.collidepoint(mx, my):
            if self.selected_unit_type is not None:
                unit_type = self.recruitment_unit_types[self.selected_unit_type]
                castle.buy_patent(unit_type)
                print("Patent bought:", unit_type)
            return

        # START PRODUCTION
        if self.start_prod_button.collidepoint(mx, my):
            if self.selected_unit_type is not None:
                unit_type = self.recruitment_unit_types[self.selected_unit_type]
                castle.start_production(unit_type)
                print("Production started:", unit_type)
            return

        # STOP PRODUCTION
        if self.stop_prod_button.collidepoint(mx, my):
            castle.stop_production()
            print("Production stopped")
            return

        # SCROLL UP
        if self.scroll_up_button.collidepoint(mx, my):
            if self.recruitment_scroll > 0:
                self.recruitment_scroll -= 1
            return

        # SCROLL DOWN
        if self.scroll_down_button.collidepoint(mx, my):
            if self.recruitment_scroll < len(self.recruitment_unit_types) - self.visible_recruitment_count:
                self.recruitment_scroll += 1
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

        return None
    