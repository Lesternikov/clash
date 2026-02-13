from unit import Unit
from castle import Castle
from player import Player
from map_loader import load_map, load_fac_objects
import pygame


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
        self.turn = 0
        self.current_player = 0
        self.selected_unit = None
        self.garrison_button = pygame.Rect(40, 140, 160, 40)
        self.exit_castle_button = pygame.Rect(40, 200, 160, 40)
        self.heal_button = pygame.Rect(40, 260, 160, 40)
        self.train_button = pygame.Rect(40, 320, 160, 40)
        self.recruit_button = pygame.Rect(40, 380, 160, 40)
        self.selected_unit_type = None
        self.menu_button = pygame.Rect(650, 40, 140, 40)
        self.menu_rects = {}
        self.build_rects = {}
        self.next_turn_button = pygame.Rect(460, 10, 160, 40)
        self.menu_open = False
        self.build_open = False

        self.unit_types = [ "pospolite_ruszenie","lekka_piechota","pikinier","halberdier","highlander","light_cavalry","heavy_cavalry","elephant","archer","crossbowman",
            "musketeer","worm","scorpion","mag","pegasus","eagle","ghost","bones","trol","smok","heavy_infantry","leśnik","budowniczy","armata","ważka","płaszczka","rycerstwo",
            "dragon","cyklop","katapulta",]

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
        
        # BACK
        self.back_button = pygame.Rect(0, 0, 120, 40)
        self.castle_list_offset = 0
        self.castle_scroll_up = pygame.Rect(0,0,40,40)
        self.castle_scroll_down = pygame.Rect(0,0,40,40)
        
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

        player = self.players[self.current_player]

        if self.selected_castle.recruit(player):
            u = Unit(
                "lekka_piechota",
                self.selected_castle.x,
                self.selected_castle.y,
                player
)

            self.selected_castle.garrison.append(u)
            print("Zrekrutowano jednostkę")
       
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

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                self.handle_mouse_click(mx, my)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    self.train_selected_garrison_units()

    def handle_mouse_click(self, mx, my):

        tile_x = mx // 32
        tile_y = my // 32

    # ================= MAP =================
        if self.screen == "map":
            if self.next_turn_button.collidepoint(mx, my):
                self.next_turn()
                return
    
            self.select_castle(tile_x, tile_y)
            self.select_unit(tile_x, tile_y)

            if self.selected_castle:
                self.screen = "castle"

    # ================= CASTLE =================
        elif self.screen == "castle":

            if self.back_button.collidepoint(mx, my):
                self.screen = "map"
                self.selected_castle = None
                return

            if self.garrison_button.collidepoint(mx, my):
                self.screen = "garrison"
                return

            if self.peasant_button.collidepoint(mx, my):
                self.screen = "peasants"
                return

            # klik w budynki
            if self.menu_open:
                for name, rect in self.build_rects.items():
                    if rect.collidepoint(mx, my):
                        
                        if self.selected_castle.build(name):
                            self.menu_open = False
                            self.build_open = False
                        return

                    
    # ================= GARRISON =================
        elif self.screen == "garrison":



            if self.back_button.collidepoint(mx, my):
                self.selected_units.clear()
                self.screen = "castle"
                return
            
            if self.recruit_button.collidepoint(mx, my):
                self.screen = "recruitment"
                return
            
            self.handle_garrison_click(mx, my)
            print("klik:", mx, my)


            if self.back_button.collidepoint(mx, my):
                self.screen = "garrison"
                return
        

            if hasattr(self, "start_prod_button"):
                if self.start_prod_button.collidepoint(mx, my):
                    self.start_recruitment(self.selected_unit_type)
                    return


            # HEAL
            if self.selected_castle and "hospital" in self.selected_castle.buildings:
                if self.heal_button.collidepoint(mx, my):
                    for unit in self.selected_units:
                        self.selected_castle.start_healing_unit(unit)

            # TRAIN
            if self.selected_castle and "school" in self.selected_castle.buildings:
                if self.train_button.collidepoint(mx, my):
                    if self.selected_units:
                        count = len(self.selected_units)
                        self.selected_castle.start_training_group(self.selected_units)
                        self.selected_units.clear()
                        print("Przeszkolono", count, "jednostek")
                    else:
                        print("Brak zaznaczonych jednostek")
            
        elif self.screen == "recruitment":

            if self.back_button.collidepoint(mx, my):
                self.screen = "garrison"
                return

            index = self.click_on_recruitment(mx, my)
            if index is not None:
                self.selected_unit_type = index
                return
            
            if hasattr(self, "start_prod_button"):
                if self.start_prod_button.collidepoint(mx, my):
                    self.start_recruitment(self.selected_unit_type)
                    return
                utype = UNIT_TYPES[self.selected_unit_type]

                self.selected_castle.start_production(utype)
                print("Produkcja:", utype)  
                      
        elif self.screen == "peasants":
            print("peasants screen click")

            if self.back_button.collidepoint(mx, my):
                self.screen = "castle"
                return

            castle = self.selected_castle

            # ================= SEND AMOUNT =================

            if self.peasants_plus_button.collidepoint(mx, my):
                if self.send_peasants_amount + 10 <= castle.peasants:
                    self.send_peasants_amount += 10

            if self.peasants_minus_button.collidepoint(mx, my):
                self.send_peasants_amount = max(0, self.send_peasants_amount - 10)

            if self.gold_plus_button.collidepoint(mx, my):
                if self.send_gold_amount + 10 <= castle.gold:
                    self.send_gold_amount += 10

            if self.gold_minus_button.collidepoint(mx, my):
                self.send_gold_amount = max(0, self.send_gold_amount - 10)

            # ================= TAX =================

            if self.tax_plus_button.collidepoint(mx, my):
                castle.tax_rate = min(4.0, castle.tax_rate + 0.1)

            if self.tax_minus_button.collidepoint(mx, my):
                castle.tax_rate = max(0.0, castle.tax_rate - 0.1)

            # ================= SCROLL =================

            owned = [c for c in self.castles if c.owner == self.players[self.current_player]]
            max_offset = max(0, len(owned) - 3)

            if self.castle_scroll_up.collidepoint(mx, my):
                self.castle_list_offset = max(0, self.castle_list_offset - 1)

            if self.castle_scroll_down.collidepoint(mx, my):
                self.castle_list_offset = min(max_offset, self.castle_list_offset + 1)

            # ================= SEND =================

            if self.send_button.collidepoint(mx, my):

                if self.send_peasants_amount <= castle.peasants and \
                self.send_gold_amount <= castle.gold:

                    castle.peasants -= self.send_peasants_amount
                    castle.gold -= self.send_gold_amount

                    print("Resources sent!")

                    self.send_peasants_amount = 0
                    self.send_gold_amount = 0

    def handle_garrison_click(self, mx, my):
        if self.selected_castle:
            print("Garrison size:", len(self.selected_castle.garrison))

        index = self.click_on_garrison(mx, my)
        if index is None:
            return
        
        if not self.selected_castle:
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

    def draw_pygame(self, screen):
        screen.fill((30, 30, 30))

        if self.screen == "map":
            self.draw_map(screen)

        elif self.screen == "castle":
            self.draw_castle(screen)

        elif self.screen == "garrison":
            self.draw_garrison(screen)

        elif self.screen == "recruitment":
            self.draw_recruitment(screen)
        
        elif self.screen == "peasants":
            self.draw_peasants(screen)

    def draw_garrison(self, screen):
        if not self.selected_castle:
            return

        start_x = 500
        start_y = 120
        slot = 64

        cols = 2
        rows = 6

        font = pygame.font.SysFont(None, 20)

        for row in range(rows):
            for col in range(cols):
                index = row * cols + col   # ← BRAKOWAŁO TEGO

                x = start_x + col * slot
                y = start_y + row * slot

                rect = pygame.Rect(x, y, slot, slot)

                unit = None
                if index < len(self.selected_castle.garrison):
                    unit = self.selected_castle.garrison[index]

                if unit in self.selected_units:
                    pygame.draw.rect(screen, (255, 255, 0), rect, 3)
                else:
                    pygame.draw.rect(screen, (200, 200, 200), rect, 2)

                if index < len(self.selected_castle.garrison):
                    unit = self.selected_castle.garrison[index]

                    # tło jednostki
                    pygame.draw.rect(screen, (80, 120, 200), (x+4, y+4, 56, 56))

                    # prosty "X"
                    pygame.draw.line(screen, (255,255,255), (x+8, y+8), (x+56, y+56), 2)
                    pygame.draw.line(screen, (255,255,255), (x+56, y+8), (x+8, y+56), 2)

                    # nazwa
                    text = font.render(unit.type[:3], True, (255,255,255))
                    screen.blit(text, (x + 6, y + 42))


    # BACK button
        self.back_button = pygame.Rect(40, 40, 120, 40)
        pygame.draw.rect(screen, (120, 80, 80), self.back_button)

        font = pygame.font.SysFont(None, 24)
        screen.blit(font.render("BACK", True, (255,255,255)), (55,50))

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
            screen.blit(font.render("HEAL", True, (255,255,255)), (50,270))

       # TRAIN BUTTON
        if self.selected_castle and "school" in self.selected_castle.buildings:
            pygame.draw.rect(screen, (160, 160, 80), self.train_button)
            screen.blit(font.render("TRAIN", True, (255,255,255)), (50,330))

   
    # przycisk produkcji wojska
        if "garrison" in self.selected_castle.buildings:
            pygame.draw.rect(screen, (240, 120, 20), self.recruit_button)
            screen.blit(font.render("RECRUIT", True, (255,255,255)), (50,390))
           
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
        screen.blit(font.render("NEXT TURN", True, (255,255,255)),
                    (self.next_turn_button.x + 10, self.next_turn_button.y + 10))
    
    def draw_castle(self, screen):
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        self.peasant_button.x = screen_width - 200
        self.peasant_button.y = screen_height - 70

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

    # --- BUTTON: GARRISON ---
        self.garrison_button = pygame.Rect(40, 140, 160, 40)
        pygame.draw.rect(screen, (80, 80, 200), self.garrison_button)
        screen.blit(font.render("GARRISON", True, (255,255,255)), (50,150))

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


    def draw_recruitment(self, screen):
        font = pygame.font.SysFont(None, 24)

        unit_types = [ "pospolite_ruszenie","lekka_piechota","pikinier","halberdier","highlander","light_cavalry","heavy_cavalry","elephant","archer","crossbowman",
            "musketeer","worm","scorpion","mag","pegasus","eagle","ghost","bones","trol","smok","heavy_infantry","leśnik","budowniczy","armata","ważka","płaszczka","rycerstwo",
            "dragon","cyklop","katapulta",]

        start_x = 400
        start_y = 120
        slot = 50

        for i, utype in enumerate(unit_types):
            rect = pygame.Rect(start_x, start_y + i * slot, 200, 50)

            if self.selected_unit_type == i:
                pygame.draw.rect(screen, (200, 200, 80), rect)
            else:
                pygame.draw.rect(screen, (120, 120, 120), rect)

            screen.blit(font.render(utype, True, (255,255,255)), (start_x+10, start_y+10 + i*slot))

        self.back_button = pygame.Rect(40, 40, 120, 40)
        pygame.draw.rect(screen, (120, 80, 80), self.back_button)
        screen.blit(font.render("BACK", True, (255,255,255)), (55,50))

        if self.selected_unit_type is not None:
            info = font.render("Koszt: 50", True, (255,255,255))
            screen.blit(info, (40,120))

            self.start_prod_button = pygame.Rect(40, 200, 180, 40)
            pygame.draw.rect(screen, (80,160,80), self.start_prod_button)
            screen.blit(font.render("START", True, (255,255,255)), (60,210))
        if self.selected_castle.production_enabled:
            screen.blit(font.render(
                f"Produkcja: {self.selected_castle.production_unit_type}",
                True,
                (255,255,255)), (40, 260))

            screen.blit(font.render(
                f"Tury: {self.selected_castle.production_turns_left}",
                True,
                (255,255,255)), (40, 290))
            
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


    def draw(self, screen):
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
        start_x = 400
        start_y = 120
        slot = 50

        unit_types = [ "pospolite_ruszenie","lekka_piechota","pikinier","halberdier","highlander","light_cavalry","heavy_cavalry","elephant","archer","crossbowman",
            "musketeer","worm","scorpion","mag","pegasus","eagle","ghost","bones","trol","smok","heavy_infantry","leśnik","budowniczy","armata","ważka","płaszczka","rycerstwo",
            "dragon","cyklop","katapulta",
        ]

        for i in range(len(unit_types)):
            rect = pygame.Rect(start_x, start_y + i * slot, 200, 50)
            if rect.collidepoint(mx, my):
                return i
        return None
    def start_recruitment(self, index):
        unit_types = [ "pospolite_ruszenie","lekka_piechota","pikinier","halberdier","highlander","light_cavalry","heavy_cavalry","elephant","archer","crossbowman",
            "musketeer","worm","scorpion","mag","pegasus","eagle","ghost","bones","trol","smok","heavy_infantry","leśnik","budowniczy","armata","ważka","płaszczka","rycerstwo",
            "dragon","cyklop","katapulta",]
        
        if index is None:
            return

        if index is None:
            return
        
        utype = unit_types[index]
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

        buildings = ["hospital", "school", "garrison", "forge", "workshop"]
        self.build_rects.clear()

        for i, b in enumerate(buildings):
            rect = pygame.Rect(sub_x, sub_y + i*40, 160, 40)
            pygame.draw.rect(screen, (80, 80, 120), rect)
            screen.blit(font.render(b, True, (255,255,255)),
                        (sub_x+10, sub_y+10+i*40))

            self.build_rects[b] = rect
    
        return None
    
