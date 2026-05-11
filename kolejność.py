class World:

    def __init__(self, ...):
    def next_turn(self):
    def reset_units(self)
        
    def load_map(...)
    def load_objects(...)

    def handle_mouse_click(self, mx, my):

    def handle_map_click(self, mx, my):
    def handle_castle_click(self, mx, my):

    def handle_court_click(self, mx, my):
    def handle_recruitment_click(self, mx, my):
    def handle_peasants_click(self, mx, my):
    def handle_garrison_click(self, mx, my):

    def move_selected(self, dx, dy):
    def attack_unit(...)

    def draw(self, screen):

    def draw_map(self, screen):
    def draw_units(self, screen):
    def draw_castles(self, screen):

    def draw_castle(self, screen):
    def draw_court(self, screen):
    def draw_recruitment(self, screen):
    def draw_peasants(self, screen):
    def draw_garrison(self, screen):

    def calculate_tax_income(self, castle):
    def get_owned_castles(self):
    def some_helper(...)

class World:

    # INIT
    __init__
    next_turn

    # INPUT
    handle_mouse_click
    handle_map_click
    handle_castle_click
    handle_court_click
    handle_recruitment_click
    handle_peasants_click
    handle_garrison_click

    # LOGIC
    move_selected
    combat

    # DRAW
    draw
    draw_map
    draw_units
    draw_castles
    draw_castle
    draw_court
    draw_recruitment
    draw_peasants
    draw_garrison

    # UTILS
    calculate_tax_income


(105, 136, 97, 255): (134, 162, 235, 255),     # Zmienia jaskrawy zielony na szare tło
    (76, 62, 61, 255): (174, 174, 174, 255),     # Zmienia mocny niebieski na srebro
    (142, 135, 160, 255): (97, 105, 109, 255),    # Zmienia żółty na ładne złoto
    (191, 152, 106, 255): (117, 113, 109, 255),    # Zmienia żółty na ładne złoto
    (255, 232, 201, 255): (117, 113, 109, 255),    # Zmienia żółty na ładne złoto
    (2, 189, 9, 255): (44, 48, 56, 255),    # Zmienia żółty na ładne złoto
    (7, 26, 17, 255): (73, 73, 56, 255),    # Zmienia żółty na ładne złoto
    (230, 190, 153, 255): (77, 81, 77, 255),    # Zmienia żółty na ładne złoto
    (96, 145, 58, 255): (93, 97, 73, 255),    # Zmienia żółty na ładne złoto
    (52, 33, 17, 255): (40, 40, 32, 255),    # Zmienia żółty na ładne złoto
    (18, 9, 0, 255): (73, 44, 40, 255),    # Zmienia żółty na ładne złoto
    (0, 163, 0, 255): (142, 113, 97, 255),    # Zmienia żółty na ładne złoto
    (255, 220, 113, 255): (130, 113, 81, 255),    # Zmienia żółty na ładne złoto
    (209, 255, 210, 255): (142, 97, 60, 255),    # Zmienia żółty na ładne złoto
    (255, 177, 163, 255): (178, 52, 52, 255),    # Zmienia żółty na ładne złoto
    (57, 39, 0, 255): (109, 60, 52, 255),    # Zmienia żółty na ładne złoto
    (253, 140, 63, 255): (93, 93, 105, 255),    # Zmienia żółty na ładne złoto
    (104, 153, 64, 255): (101, 117, 154, 255),    # Zmienia żółty na ładne złoto
    (255, 233, 115, 255): (105, 130, 186, 255),    # Zmienia żółty na ładne złoto
    (74, 84, 97, 255): (138, 154, 207, 255),    # Zmienia żółty na ładne złoto
    (94, 234, 99, 255): (162, 174, 203, 255),    # Zmienia żółty na ładne złoto