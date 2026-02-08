from unit import Unit
from castle import Castle
from player import Player
from map_loader import load_map, load_fac_objects

class World:
    def __init__(self):
        self.map = None
        self.objects = None
        self.peasant_groups = []
        self.gold_transports = []
        self.players = []
        self.units = []
        self.castles = []

        self.turn = 0
        self.current_player = 0
      

        self.selected_unit = None
        self.selected_castle = None

    def load(self, map_file, fac_file):
        self.map = load_map(map_file)
        self.objects = load_fac_objects(fac_file)

        castle_places = self.objects.get("zamek_place", [])

        for i, (x, y) in enumerate(castle_places):
            owner = None
            if i < len(self.players):
                owner = self.players[i]
            else:
                owner = None  # neutralny zamek

            c = Castle(x// 10, y// 10, owner)
            c.gold = 200
            self.castles.append(c)

    # jednostki startowe przy zamkach graczy
        for c in self.castles:
            if c.owner:
                self.add_unit(Unit(c.x, c.y + 1, c.owner))

        print("DEBUG castles:", len(self.castles))
        print("DEBUG units:", len(self.units))

    def add_player(self, player):
        self.players.append(player)

    def add_unit(self, unit):
        self.units.append(unit)
        if unit.owner:
            unit.owner.units.append(unit)

    def next_turn(self):
        if not self.players:
            return

        self.turn += 1
        self.current_player = (self.current_player + 1) % len(self.players)
        self.reset_units()

        player = self.players[self.current_player]

        for c in self.castles:
            if c.owner == player:
                c.next_turn()

        self.selected_unit = None
        self.selected_castle = None


    def draw(self):
        if not self.map:
            print("Brak mapy")
            return

        grid = [list(row) for row in self.map]

    # zamki
        for c in self.castles:
            if 0 <= c.y < len(grid) and 0 <= c.x < len(grid[0]):
                if c.owner:
                    grid[c.y][c.x] = "C"
                else:
                    grid[c.y][c.x] = "O"
    # jednostki
        for u in self.units:
            if 0 <= u.y < len(grid) and 0 <= u.x < len(grid[0]):
                if u == self.selected_unit:
                    grid[u.y][u.x] = "S"
                else:
                    grid[u.y][u.x] = "U"


        print("\nMAPA:\n")
        for row in grid:
            print("".join(row))

        print("\nGARNIZONY:")
        for c in self.castles:
            if c.garrison:
                print("Zamek", c.x, c.y, "->", len(c.garrison), "jednostek")

        print("Liczba jednostek:", len(self.units))

    def move_unit(self, unit, dx, dy):
        if unit.move_points <= 0:
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
        
        if len(self.selected_castle.garrison) >= 5:
            print("Zamek jest pełny")
            return

        player = self.players[self.current_player]

        if self.selected_castle.recruit(player):
            u = Unit(self.selected_castle.x, self.selected_castle.y, player)
            self.selected_castle.garrison.append(u)
            print("Zrekrutowano jednostkę")
       
    def get_castle(self, x, y):
        for c in self.castles:
            if c.x == x and c.y == y:
                return c
        return None