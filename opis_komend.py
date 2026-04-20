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


class world
def _init_(self): absolutnie konieczne
#    wszystkie self'y i ich opisy

def _find_nearest_base_terrain(self, start_x, start_y, base_terrains):



def get_river_direction(self, x, y):


def setup_starting_units(self):

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
def spawn_unit_near_castle(self, unit, castle):
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

def train_selected_garrison_units(self):
#   
def get_unit_at_pixel(self, mx, my): 
#   
def handle_trap_info_click(self, mx, my):
#   
def handle_map_logic_combined(self, mx, my, button):

def execute_trap_build(self, gx, gy):

def execute_road_build(self, gx, gy):

def draw_garrison(self, screen):
#   
def draw_castle_on_map(self, screen, castle)
    
def is_near_tile(self, x, y, search_type, check_bg=False):
#   
#       
def draw_castle_interface(self, screen):

def castle_has_patent(self, castle, unit_name):
#   opisuje jakie są patenty
def update_selected_from_scroll(self):
#   przewijanie listy ptentów
def center_on_selected_unit(self):
#   wypisywanie informacji
#   o centralnej jednostce na liście patentów
def draw_recruitment(self, screen):
#   
def draw_unit_stats_table(self, screen, x, y, unit_name, stats_source):
    
#   
def draw_peasants(self, screen):
#   
#   
def draw_demolish_confirm(self, screen):
#   potwierdzienie demolowania zamku
def select_castle(self, x, y):
#   wybierane zamku
def create_unit(self, unit_type, x, y, owner):

def click_on_recruitment(self, mx, my):
#   sprawdzanie w rekrutacji
#   który z narysowanych slotów został kliknięty

#   
def click_on_garrison(self, mx, my):
#   
def get_unit_at(self, x, y):


#   
def draw_castle_menu(self, screen, mx, my):
#   
def draw_build_submenu(self, screen, menu_x, menu_y):
#   

def handle_recruitment_click(self, mx, my):
 
def handle_peasants_click(self, mx, my):
#  

def handle_camera(self):
#   
   
def check_unit_info(self, mx, my):
#   
def handle_recruitment_scroll(self, event):
#  
#   
def handle_tryb_mapy_button(self):
#   Wyłącza zaznaczenie jednostki, pozwalając na klikanie w zamki
def check_unit_castle_entry(self, unit):
#   Sprawdza czy jednostka powinna zostać przeniesiona do garnizonu zamku
def handle_dropdown_clicks(self, mx, my):
#   Obsługuje kliknięcia wewnątrz rozwiniętych list System i Mapa

def enter_castle(self, unit, castle):
#   
def handle_action_button_click(self, button_index):
#   

def remove_unit_or_builder(self, army, builder):

#   
def spawn_unit(self, unit_type, x, y, owner):
#   
def draw_trap_popup(self, screen):
#   
#   
def count_builders_near(self, pos):
#   
def handle_building_logic(self, mx, my, gx, gy):
#   
def handle_castle_entry(self, mx, my):
#   
def draw_garrison_only(self, screen):
#   
def destroy_straznica(self, castle):
#   
def draw_building_footer(self, screen):
#    
def release_selected_units(self):

def find_multiple_spawn_positions(self, castle, num_groups):


def show_foundation_menu(self, gx, gy):

def draw_build_system(self, screen):


def can_build_trap(self, x, y):

def can_build_road(self, x, y):

def is_area_occupied_by_foundation(self, gx, gy):
 
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



przeniesione

def get_tile_at(self, x, y):

def get_bg_tile_at(self, x, y):

def is_tile_passable(self, x, y, unit_type):
    def load_castle_and_tower(self):


def update(self):
#    obsługa kamery i poruszania się po mapie
#    obsługa częściowa lirery G
def load_map(self, filename):
#   wczytanie map.txt 
#   jeśli niema mapy tworzy pustą 100x100
def load(self, map_file, fac_file):

def train_selected(self, castle):
#   wybieranie jednostki do trenowania
def handle_mouse_click(self, mx, my, button):
def handle_events(self):#   
def handle_garrison_click(self, mx, my, button):
    def handle_castle_main_click(self, mx, my):

def calculate_army_power(self, player):
#   liczy siłę używana do dworu
def calculate_gold(self, player):
#   liczy złoto używana do dworu
def draw_map(self, screen):
def check_collision(self, x, y):
def draw_castle(self, screen):

def draw_unit(self, screen, u):
#   
def draw_button(self, screen, text, rect):
#   wyjeżdżanie listy opcji
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
   def handle_court_click(self, mx, my):
#   
def handle_map_click(self, mx, my, button):
#       
def start_recruitment(self, index):
#  
def handle_castle_click(self, mx, my):
#   
def demolish_castle(self, castle):
#   niszczenie zamku
def draw_building_template(self, screen, title, lines, theme_color=(100, 100, 130), border_color=(180, 180, 220)):

def draw_forge(self, screen):
#   rysowanie kuźni
def draw_workshop(self, screen):
#   rysowanie warsztatu
def draw_hospital(self, screen):
#   rysowanie szpitala
def draw_school(self, screen):
#   rysowanie szkoły
# #   
def draw_unit_info(self, screen):
#   
def load_castles_from_fac(self, fac_path):
#   
#   
def draw_top_bar(self, screen):
#   
#   
def draw_bottom_bar(self, screen):
#   przyciski podstawowe
def handle_mouse_up(self, mx, my):
#   
 
def draw_path_dots(self, screen, unit, path):
#   Rysuje czarne i czerwone kropki
#   trasy z uwzględnieniem kamery
def find_path(self, unit, dest_x, dest_y):
#   
def is_walkable(self, x, y):
#
def start_building(self, x, y, b_type, builder_unit=None):

def handle_ui_click(self, mx, my):

def execute_build_action(self, index, u):

def draw_ui(self, screen):
#    
def process_construction(self):
def draw_grid_lines(self, screen):

def draw_road_arrows(self, screen):
def handle_mouse_motion(self, mx, my):
