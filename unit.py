from unit import Unit
class Unit:
    def __init__(self, unit_type, x, y, owner):
        self.type = unit_type
        self.x = x
        self.y = y
        self.owner = owner
        self.carried_peasants = 0
        self.carried_gold = 0

        self.hp = 100
        self.morale = 100
        self.fatigue = 0
        self.moves = 10
        self.experience = 0
        self.production_unit_type = None
        self.production_turns_left = 0
        self.production_enabled = False

        self.garrison_limit = 12
        self.healing = False
        self.healing_turns_left = 0


    def position(self):
        return (self.x, self.y)

    def __repr__(self):
        return f"{self.type} ({self.x},{self.y})"
    
    def start_production(self, unit_type, production_time):
        self.production_unit_type = unit_type
        self.production_turns_left = production_time
        self.production_enabled = True

    def stop_production(self):
        self.production_enabled = False

    def process_production(self):
        if not self.production_enabled:
            return

        if self.production_unit_type is None:
            return

        self.production_turns_left -= 1

        if self.production_turns_left <= 0:
            cost = 10

            if self.gold < cost:
                print("Brak złota — produkcja zatrzymana")
                self.production_enabled = False
                return

            if len(self.garrison) >= self.garrison_limit:
                print("Garnizon pełny")
                return

            self.gold -= cost

            unit = Unit(
                self.production_unit_type,
                self.x,
                self.y,
                self.owner
            )

            self.garrison.append(unit)

            print("Wyprodukowano:", self.production_unit_type)

            self.production_turns_left = 3

class GoldTransport:
    def __init__(self, x, y, owner, gold):
        self.x = x
        self.y = y
        self.owner = owner
        self.gold = gold
        self.move_points = 10

    def position(self):
        return (self.x, self.y)

    def __repr__(self):
        return f"Gold({self.gold})"

class PeasantGroup:
    def __init__(self, x, y, owner, amount):
        self.x = x
        self.y = y
        self.owner = owner
        self.amount = amount
        self.move_points = 10

    def position(self):
        return (self.x, self.y)

    def __repr__(self):
        return f"Peasants({self.amount})"


