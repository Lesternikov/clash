import pygame
import re
from castle import Castle, BUILDING_TYPES
from unit import Unit
from settings import UNIT_STATS


# =====================================================
#   BUILDINGS.PY
#   Metody klasy World dotyczące budynków i zamków.
#   Wszystkie funkcje tu są metodami World —
#   wklejasz je do klasy World w world.py
#   LUB importujesz przez mixin (patrz niżej).
# =====================================================

class BuildingsMixin:
    """
    Mixin z metodami budowlanymi dla klasy World.
    Użycie:
        class World(BuildingsMixin, ...):
            pass
    """

    def load_castles_from_fac(self, fac_path):
        with open(fac_path, 'r') as f:
            content = f.read()

        all_places   = re.findall(r"\(zamek_place (\d+) (\d+)\)", content)
        built_indices = [int(i) for i in re.findall(r"\(zbudowano zamek (\d+)\)", content)]
        print(f"DEBUG: Zbudowane zamki: {built_indices}")

        self.castles          = []
        self.castle_locations = []

        for i, (x, y) in enumerate(all_places):
            ix, iy = int(x), int(y)
            if i in built_indices:
                self.castles.append(Castle(ix, iy))
            else:
                self.castle_locations.append((ix, iy))

    def load_castle_and_tower(self):
        base_folder = r"assets\zamekczerwony\BUILDIN1_S32_"
        TARGET_SIZE = (32, 32)

        self.castle_tiles = {0: [], 1: [], 2: [], 3: [], 4: []}
        for stage in range(4):
            for i in range(4):
                file_num = 225 + (stage * 4) + i
                try:
                    img = pygame.image.load(f"{base_folder}{file_num}.png").convert_alpha()
                    img = pygame.transform.scale(img, TARGET_SIZE)
                    self.castle_tiles[stage].append(img)
                except:
                    print(f"Brak pliku zamku: {file_num}")

        for i in range(4):
            try:
                img = pygame.image.load(f"{base_folder}{257 + i}.png").convert_alpha()
                self.castle_tiles[4].append(pygame.transform.scale(img, TARGET_SIZE))
            except:
                pass

        self.tower_tiles = {}
        for i in range(4):
            try:
                img = pygame.image.load(f"{base_folder}{i}.png").convert_alpha()
                self.tower_tiles[i] = pygame.transform.scale(img, TARGET_SIZE)
            except:
                print(f"Brak pliku strażnicy: {i}")

        try:
            img = pygame.image.load(f"{base_folder}8.png").convert_alpha()
            self.tower_tiles[4] = pygame.transform.scale(img, TARGET_SIZE)
        except:
            print("Brak pliku zniszczonej strażnicy (8.png)")

    def demolish_castle(self, castle):
        if not castle:
            return

        all_units = [u for u in castle.garrison if u is not None]
        if all_units:
            groups       = [all_units[:10], all_units[10:]]
            spawn_points = self.find_multiple_spawn_positions(
                castle, len([g for g in groups if g]))

            for i, group in enumerate(groups):
                if group and spawn_points[i]:
                    nx, ny    = spawn_points[i]
                    new_army  = Unit(group[0].type, nx, ny, castle.owner)
                    new_army.garrison = [None] * 10
                    for j, u in enumerate(group):
                        new_army.garrison[j] = u
                    self.units.append(new_army)
                    castle.owner.units.append(new_army)

        castle.destroyed = True
        if castle.owner and castle in castle.owner.castles:
            castle.owner.castles.remove(castle)
        castle.owner    = None
        castle.garrison = [None] * 12

        self.demolish_confirm = False
        self.screen = "map"
        print("Zamek stał się ruiną.")

    def start_building(self, x, y, b_type, builder=None):
        if b_type not in BUILDING_TYPES:
            return
        config = BUILDING_TYPES[b_type]

        ix, iy = int(x), int(y)
        anchor_x, anchor_y = ix, iy
        found_foundation = False

        if config.get("size") == 2:
            for dx in [0, -1]:
                for dy in [0, -1]:
                    nx, ny = ix + dx, iy + dy
                    if 0 <= nx < len(self.map[0]) and 0 <= ny < len(self.map):
                        if self.map[ny][nx] == "#":
                            anchor_x, anchor_y = nx, ny
                            found_foundation = True
                            break
                if found_foundation:
                    break
            if not found_foundation:
                return
        else:
            if self.map[iy][ix] in [".", "p"] and \
               not self.is_area_occupied_by_foundation(ix, iy):
                found_foundation = True
            else:
                return

        new_castle = Castle(anchor_x, anchor_y, self.current_player,
                            building_type=b_type)
        new_castle.under_construction = True
        new_castle.total_work_needed  = 12.0
        new_castle.work_done          = 0.0
        new_castle.mury_percent       = 0

        army = self.get_unit_at(ix, iy)
        if army:
            self.enter_castle(army, new_castle)

        self.castles.append(new_castle)

        size = 2 if config.get("size") == 2 else 1
        for dy in range(size):
            for dx in range(size):
                self.map[anchor_y + dy][anchor_x + dx] = "P"

        print(f"Rozpoczęto budowę {b_type}.")

    def process_construction(self):
        for castle in self.castles:
            if not getattr(castle, 'under_construction', False):
                continue

            builders_count = sum(
                1 for slot in castle.garrison
                if slot and slot.type == "Budowniczy")

            if builders_count > 0:
                castle.work_done    += builders_count
                castle.mury_percent  = min(
                    100, int((castle.work_done / castle.total_work_needed) * 100))
                print(f"Budowa {castle.building_type}: {castle.mury_percent}% murów.")

            if castle.work_done >= castle.total_work_needed:
                castle.under_construction = False
                castle.mury_percent       = 100
                sym  = "H" if castle.building_type == "Strażnica" else "C"
                size = 2 if castle.building_type in ["Twierdza", "Zamek"] else 1
                for dy in range(size):
                    for dx in range(size):
                        self.map[castle.y + dy][castle.x + dx] = sym
                print(f"Budowa ukończona: {castle.building_type}!")

    def execute_build_action(self, button_index, army):
        if not army:
            return
        grid_x, grid_y = army.x, army.y

        def get_builder(a):
            if a.type == "Budowniczy":
                return a
            if hasattr(a, 'garrison'):
                for slot in a.garrison:
                    if slot and slot.type == "Budowniczy":
                        return slot
            return None

        builder = get_builder(army)
        if not builder:
            print("Brak Budowniczego w armii!")
            return

        if button_index == 0:           # Droga
            if army.move_points >= 5:
                self.road_build_mode  = True
                self.build_menu_open  = False
                print("Tryb budowy drogi.")
            else:
                print("Za mało punktów ruchu!")
            return

        if button_index == 1:           # Pułapka
            self.trap_build_mode     = True
            self.build_menu_open     = False
            self.active_builder_army = army
            self.active_builder_unit = builder
            print("Wybierz pole na pułapkę.")
            return

        if button_index == 2:           # Skarb
            if self.map[grid_y][grid_x] == "$":
                army.owner.gold      += 500
                self.map[grid_y][grid_x] = "."
                self.build_menu_open = False
            return

        menu_to_type = {3: "Strażnica", 4: "Twierdza", 5: "Zamek"}
        if button_index in menu_to_type:
            self.start_building(grid_x, grid_y,
                                menu_to_type[button_index], builder)
            self.build_menu_open = False
            self.selected_unit   = None

    # -------------------------------------------------------
    # RYSOWANIE BUDYNKÓW (teksty opisowe)
    # -------------------------------------------------------

    def draw_forge(self, screen):
        lines = [
            "Dzień i noc słychać rytmiczne uderzenia żelaznych młotów –",
            "to ławrowni kowale w pocie czoła pokuwają bojowe rumaki.",
            "Dzięki ich wysiłkom będziesz mógł rozpocząć produkcję",
            "oddziałów konnych, bardzo przydatnych w bojowych zmaganiach.",
            "",
            "Jednocześnie łowisarze z górskich krain wytapiają tu stal",
            "na pancerze i wytwarzają broń palną.",
        ]
        self.draw_building_template(screen, "Kuźnia", lines,
                                    (120, 90, 60), (200, 170, 90))

    def draw_workshop(self, screen):
        lines = [
            "Pracują tu znakomici rzemieślnicy ze starego kraju.",
            "Dzięki ich kunsztowi staniesz się posiadaczem łuków, kusz,",
            "oszczepów oraz strzał niespotykanych wcześniej w tej części",
            "kontynentu.",
        ]
        self.draw_building_template(screen, "Warsztat", lines)

    def draw_hospital(self, screen):
        lines = [
            "Zapach rozcieranych ziół da się odczuć we wszystkich zakamarkach.",
            "Powstające tu specyfiki i mikstury robione są według starych receptur.",
            "Owe lekarstwa pomogą odzyskać Twoim rycerzom pełnię sił.",
            "Ponadto troskliwi kapłani roztoczyli swą opiekę nad wsiami.",
        ]
        self.draw_building_template(screen, "Szpital", lines)

    def draw_school(self, screen):
        lines = [
            "Dzięki wykładanym tu naukom możliwe będzie szkolenie",
            "Twoich wojsk w rzemiośle rycerskim.",
            "",
            "Ponadto uczeni waldzcy umożliwią osiągnięcie wyższego",
            "poziomu technologii w Twoim królestwie.",
        ]
        self.draw_building_template(screen, "Szkoła", lines)

    def draw_building_template(self, screen, title, lines,
                                theme_color=(100, 100, 130),
                                border_color=(180, 180, 220)):
        screen.fill((60, 60, 80))
        font_title = pygame.font.SysFont(None, 48)
        font_text  = pygame.font.SysFont(None, 24)

        panel = pygame.Rect(120, 80, 760, 420)
        pygame.draw.rect(screen, theme_color, panel)
        pygame.draw.rect(screen, border_color, panel, 6)

        title_surface = font_title.render(title.upper(), True, border_color)
        screen.blit(title_surface,
                    (panel.centerx - title_surface.get_width() // 2, panel.y - 40))

        y = panel.y + 30
        for line in lines:
            txt = font_text.render(line, True, (255, 255, 255))
            screen.blit(txt, (panel.x + 30, y))
            y += 28

        self.draw_building_footer(screen)

    def start_recruitment(self, index):
        if index is None:
            return
        utype  = list(UNIT_STATS.keys())[index]
        cost   = 50
        castle = self.selected_castle

        if castle.gold < cost:
            print("Za mało złota")
            return

        castle.gold -= cost
        castle.start_production(utype)
        print(f"Rozpoczęto produkcję: {utype}")
        self.screen = "garrison"

    def train_selected(self, castle):
        for unit in self.selected_units:
            castle.start_training(unit)
        self.selected_units.clear()