jest tu:
class PrisonSlot,
class World,
class Castle,
class Unit,
class GoldTransport,
class PeasantGroup,
class Player,
class General,
class ArmyGroup,


TILE_SIZE = 32
#
SCREEN_WIDTH = 1280
#
SCREEN_HEIGHT = 800
#
MAP_WIDTH = 100 
#
MAP_HEIGHT = 100
#
TERRAIN_TYPES = {}
#

def draw_text(screen, text, x, y, color=(0, 0, 0)):

class PrisonSlot
def __init__(self, general=None):

class world
def _init_(self): absolutnie konieczne
#    wszystkie self'y i ich opisy
def update(self):
#    obsługa kamery i poruszania się po mapie
#    obsługa częściowa lirery G
def load_map(self, filename):
#   wczytanie map.txt 
#   jeśli niema mapy tworzy pustą 100x100
def load(self, map_file, fac_file):
#
#wybiera kolory zamków
def add_player(self, player):
#   tworzy graczy
def add_unit(self, unit):
#   dodaje jednostki
def next_turn(self):
#
def move_unit(self, unit, dx, dy):
#
def reset_unit(self): #możliwe że niepotrzebne
#   resetuje jadnoostki do pięciu moves
def select_unit(self, x, y):
#   wybieranie swojej jednostki 
#   i blokowanie czego kolwiek innego
def move_select(self, dx, dy):
#
#
def spawn_unit_ner_castle(self, unit, castle):
#   bydownie zmku na czterech polach
def recruit_unit(self):
#
#
def get_castle(self, x, y):
#   
def select_garrison_unit(self, unit): można wpakować gdzie indziej
#   limit zaznaczenia
def cler_selection(self):
#   czyści parenty
def train_select(self, castle):
#   wybieranie jednostki do trenowania
def train_selected_garrison_units(self):
#   
def handle_events(self):
#   
#   
#   
def handle_mouse_click(self, mx, my, button):
#   
#   
#   
def handle_garrison_click(self, mx, my, button):
#   
#   
#   
def calculate_army_power(self, player):
#   liczy siłę używana do dworu
def calculate_gold(self, player):
#   liczy złoto używana do dworu
def draw_garrison(self, screen):
#   
#   
def draw_map(self, screen):
#   
#   
#   
def draw_castle(self, screen):
#       
#   
#   
def draw_button(self, screen, text, rect):
#   wyjeżdżanie listy opcji
def castle_has_patent(self, castle, unit_name):
#   opisuje jakie są patenty
def update_selected_from_scroll(self):
#   przewijanie listy ptentów
def center_on_selected_unit(self):
#   wypisywanie informacji
#   o centralnej jednostce na liście patentów
def draw_recruitment(self, screen):
#   
#       
#   
def draw_peasants(self, screen):
#   
#   

#|------------|
#|   D W Ó R  |
#|------------|
    def draw_court(self, screen):
    #   rysowanie dworu czyli:
    #   gracze i kolory,
    #   królowa i informacje o niej,
    #   rysowanie statystyk wszystkich graczy,
    #   więzienie i przyciski
    def draw_court_players_header(self, screen):
    #   gracze i kolory w dworze
    def draw_queen_panel(self, screen):
    #   królowa i informacje o niej w dworze
    def draw_court_stats(self, screen):
    #   rysowanie statystyk wszystkich graczy w dworze
    def draw_prison_sections(self, screen):
    #   więzienie i przyciski w dworze
    def execute_general(self, slot):
    #   przycisk zbici więżnia
    def torture_general(self, slot):
    #   przycisk torturowania generała
    def bribe_general(self, slot):
    #   przycisk przekupienia generała

def draw(self, screen):
#   
def draw_demolish_confirm(self, screen):
#   potwierdzienie demolowania zamku
def select_castle(self, x, y):
#   wybierane zamku
def create_unit(self, unit_type, x, y, owner): chyba niepotrzebne
#  
#  
def click_on_recruitment(self, mx, my):
#   sprawdzanie w rekrutacji
#   który z narysowanych slotów został kliknięty
def start_recruitment(self, index):
#   
def click_on_garrison(self, mx, my):
#   
def get_unit_at(self, x, y):
#   
def draw_castle_menu(self, screen, mx, my):
#   
def draw_build_submenu(self, screen, menu_x, menu_y):
#   
def handle_court_click(self, mx, my):
#   
def handle_map_click(self, mx, my, button):
#       
#  
#  
def handle_castle_click(self, mx, my):
#   
#   
def handle_peasants_click(self, mx, my):
#  
#  
def demolish_castle(self, castle):
#   niszczenie zamku
def draw_forge(self, screen):
#   rysowanie kuźni
def draw_workshop(self, screen):
#   rysowanie warsztatu
def draw_hospital(self, screen):
#   rysowanie szpitala
def draw_school(self, screen):
#   rysowanie szkoły
def release_selected_units(self):
#   
def draw_unit_info(self, screen):
#   
def load_castles_from_fac(self, fac_path):
#   
def handle_camera(self):
#   
#   
def draw_top_bar(self, screen):
#   
#   
def draw_bottom_bar(self, screen):
#   przyciski podstawowe
def handle_mouse_up(self, mx, my):
#   
def execute_menu_command(self, menu, index):
#   
def check_unit_info(self, mx, my):
#   
def handle_recruitment_scroll(self, event):
#   
def draw_path_dots(self, screen, unit, path):
#   Rysuje czarne i czerwone kropki
#   trasy z uwzględnieniem kamery
def find_path(self, unit, dest_x, dest_y):
#   
def is_walkable(self, x, y):
#   
def handle_tryb_mapy_button(self):
#   Wyłącza zaznaczenie jednostki, pozwalając na klikanie w zamki
def check_unit_castle_entry(self, unit):
#   Sprawdza czy jednostka powinna zostać przeniesiona do garnizonu zamku
def handle_dropdown_clicks(self, mx, my):
#   Obsługuje kliknięcia wewnątrz rozwiniętych list System i Mapa
def handle_ui_click(self, mx, my):
#   
def draw_ui(self, screen):
#   
def enter_castle(self, unit, castle):
#   
def handle_action_button_click(self, button_index):
#   
def execute_build_action(self, index, u):
#   
def spawn_test_builder(self): chyba niepotrzebne
#   
def add_unit_to_game(self, unit):
#   Dodaje jednostkę do świata i do listy jej właściciela
def spawn_unit(self, unit_type, x, y, owner):
#   
def draw_trap_popup(self, screen):
#   
def start_building(self, x, y, b_type, builder_unit=None):
#   
def process_construction(self):
#   
def count_builders_near(self, pos):
#   
def complete_building(self, project):
#   
def handle_building_logic(self, mx, my, gx, gy):
#   
def handle_castle_entry(self, mx, my):
#   
def draw_garrison_only(self, screen):
#   
def release_garrison(self):
#   
def process_active_builds(self):
#   
def check_straznica_click(self, mx, my):
#   
def destroy_straznica(self, castle):
#   
def execute_universal_release(self):
#   
def draw_building_footer(self, screen):
#    
def can_build_castle_at(self, gx, gy, b_type):
# zasady budowania zamków 
#notatki 



BUILDING_TYPES = {}
#
BUILDINGS ={}
#
UNIT_REQUIREMENTS = {}
#

class Castle
def __init__(self, x, y, owner=None, building_type="Zamek"):
#
#
def release_unit(self):
#
def collect_taxes(self):
#
#
def update_happiness(self):
#
#
def grow_population(self):
#
def tile_position(self):
#
def __repr__(self):
#
def recruit(self, player, unit_type):
#
#
def start_production(self, unit_type):
#
def process_production(self):
#
def buy_patent(self, unit_type):
#
#
def remove_patent(self, unit_type):
#
def stop_production(self):
#
def process_production(self):
#
#
def start_healing_unit(self, unit):
#
def process_healing(self):
#
def cancel_garrison_healing(self):
#
def under_attack(self):
#
def build(self, building_name):
#
#
def update_level(self):
#
def has_building(self, name):
#
def check_plague_start(self):
#
def process_plague(self):
#
def send_peasants(self, world, amount):
#
def send_gold(self, world, amount):
#
def start_training(self, unit):
#
def start_training_selected(self, units):
#
def start_training_group(self, units):
#
def process_training(self):
#
#
def next_turn(self):
#
def finish_production(self):
#
def update_production(self, world):
#
def demolish(self):
#
def get_buyable_units(self, castle):
#
def is_patent_available(self, patent_name):
#
#
def add_to_garrison(self, unit):
#


UNIT_STATS = {}
#

class Unit
def __init__(self, unit_type, x, y, owner):
#
#
def move_along_path(self, world):
#
#
def draw(self, screen):
#
def position(self):
#
def __repr__(self):
#
def veterancy_level(self):
#
def gain_training_exp(self):
#
def gain_battle_exp(self):
#
def take_damage(self, dmg):
#
def is_alive(self):
#
def morale_modifier(self):
#
def exp_modifier(self):
#
def attack_unit(self, target, log):
#
#
def can_enter(self, tile):
#


class GoldTransport
def __init__(self, x, y, owner, gold):
#
def position(self):
#
def __repr__(self):
#


class PeasantGroup
def __init__(self, x, y, owner, amount):
#
def position(self):
#
def __repr__(self):
#


class Player
def __init__(self, player_id, name, color):
#
def try_spawn_general(self):
#


class General
def __init__(self, owner):
#
def apply_bonus(self, unit):
#


class ArmyGroup
def __init__(self):
#
