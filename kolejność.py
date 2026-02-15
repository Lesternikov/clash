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
