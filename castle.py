HOSPITAL = "hospital"
import random 
from unit import PeasantGroup
from unit import GoldTransport
# castle.py
import pygame
from unit import Unit

BUILDINGS = {
    "hospital": {"cost": 200},
    "garrison": {"cost": 200},
    "workshop": {"cost": 220},
    "forge": {"cost": 190},
    "school": {"cost": 400},}

PRODUCTION_TIME = {
    "pospolite_ruszenie":1,
    "lekka_piechota": 2,
    "pikinier":2,
    "halberdier":3,
    "highlander":3,
    "light_cavalry":3,
    "heavy_cavalry":4,
    "elephant":4,
    "archer":2,
    "crossbowman":4,
    "musketeer":4,
    "worm":3,
    "scorpion":3,
    "mag":5,
    "pegasus":3,
    "eagle":3,
    "ghost":3,
    "bones":4,
    "trol":4,
    "smok":5,
    "heavy_infantry":4,
    "leśnik":3,
    "budowniczy":3,
    "armata":4,
    "ważka":2,
    "płaszczka":5,
    "rycerstwo":4,
    "dragon":4,
    "cyklop":3,
    "katapulta":4,
}

class Castle:
    def __init__(self, x, y, owner=None):
        self.x = x
        self.y = y
        self.owner = owner
        self.gold = 0
        self.garrison = []
        self.plague_active = False
        self.plague_turns = 0
        self.peasants = 100
        self.tax_rate = 1.0        # 0.0–4.0
        self.happiness = 50.0     # 0–100
        self.buildings = set()
        self.level = 1
                # PRODUKCJA
        self.production_unit_type = None
        self.production_turns_left = 0
        self.production_enabled = False
        self.training = {}        
        self.production_queue = None
        self.production_time_left = 0
        self.garrison_limit = 12

    def collect_taxes(self):        
        if self.plague_active:
            return

        happiness_factor = 0.5 + (self.happiness / 100) * 0.5
        income = int(self.peasants * 0.1 * self.tax_rate * happiness_factor)
        self.gold += income

    def update_happiness(self):
        change = (self.tax_rate - 1.0) * -2
        self.happiness += change
        self.happiness = max(0, min(100, self.happiness))
    
    def grow_population(self):
        growth = int(self.peasants * (self.happiness / 100) * 0.02)
        self.peasants += max(1, growth)
    

    def send_resources(self, target, peasants=0, gold=0):
        peasants = min(peasants, self.peasants)
        gold = min(gold, self.gold)

        self.peasants -= peasants
        self.gold -= gold

        target.peasants += peasants
        target.gold += gold


    def position(self):
        return (self.x, self.y)

    def __repr__(self):
        return f"Castle({self.x},{self.y})"
    
    def recruit(self, player):
        if self.owner != player:
            print("To nie jest twój zamek")
            return None

        cost = 100

        if self.gold < cost:
            print("Za mało złota")
            return None

        if len(self.garrison) >= 12:
            print("Garnizon pełny")
            return None

        self.gold -= cost
        
        unit = Unit("lekka_piechota", self.x, self.y, self.owner)
        self.garrison.append(unit)

        print("Wyprodukowano jednostkę")
        return unit
    
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

        # zatrzymaj gdy garnizon pełny
        if len(self.garrison) >= self.garrison_limit:
            print("Garnizon pełny — produkcja zatrzymana")
            self.production_enabled = False
            return

        self.production_turns_left -= 1
        print("Produkcja — zostało:", self.production_turns_left)

        if self.production_turns_left <= 0:
            cost = 10  # możesz potem podpiąć UNIT_COST

            if self.gold >= cost:
                self.gold -= cost

                unit = Unit(
                    self.production_unit_type,
                    self.x,
                    self.y,
                    self.owner
                )

                self.garrison.append(unit)

                print("Wyprodukowano:", self.production_unit_type)

                # restart produkcji (fabryka)
                self.production_turns_left = PRODUCTION_TIME[self.production_unit_type]

            else:
                print("Brak złota — produkcja zatrzymana")
                self.production_enabled = False

    
    def start_healing_unit(self, unit):
        if "hospital" not in self.buildings:
            print("Brak szpitala")
            return

        if unit not in self.garrison:
            print("Jednostka nie jest w garnizonie")
            return

        if unit.hp >= 100:
            print("Jednostka ma pełne HP")
            return

        unit.healing = True
        unit.healing_turns_left = 3

        print("Rozpoczęto leczenie:", unit)

    def process_healing(self):
        if "hospital" not in self.buildings:
            return

        for unit in self.garrison:
            if unit.healing:
                unit.healing_turns_left -= 1

                if unit.healing_turns_left <= 0:
                    unit.hp = 100
                    unit.healing = False
                    print("Jednostka wyleczona:", unit)

    def cancel_garrison_healing(self):
        for unit in self.garrison:
            unit.healing = False
            unit.healing_turns_left = 0

    def under_attack(self):
        self.cancel_garrison_healing()

    def build(self, building_name):
        if building_name in self.buildings:
            print("Budynek już istnieje")
            return False

        if building_name not in BUILDINGS:
            print("Nieznany budynek")
            return False

        cost = BUILDINGS[building_name]["cost"]

        if self.gold < cost:
            print("Za mało złota")
            return False

        self.gold -= cost
        self.buildings.add(building_name)

        self.update_level()

        print("Zbudowano:", building_name)
        return True

    def update_level(self):
        required = {"hospital", "garrison", "workshop", "forge"}

        if required.issubset(self.buildings):
            if self.level < 2:
                self.level = 2
                print("Zamek osiągnął poziom 2")

    def has_building(self, name):
        return name in self.buildings

    def check_plague_start(self):
        if self.plague_active:
            return

        if self.peasants < 1400:
            return

    # rosnąca szansa wraz z populacją
        chance = (self.peasants - 1400) / 6000
        chance = min(0.25, chance)

        if random.random() < chance:
            self.plague_active = True
            self.plague_turns = 5
            print("W zamku wybuchła zaraza!")
  
    def process_plague(self):
        if not self.plague_active:
            return

        loss = int(self.peasants * 0.4)
        self.peasants -= loss

        self.plague_turns -= 1

        print(f"Zaraza! Populacja spadła o {loss}")

        if self.plague_turns <= 0:
            self.plague_active = False
            print("Zaraza wygasła.")

    def send_peasants(self, world, amount):
        if amount < 10:
            return

        if amount > 1000:
            return

        if amount > self.peasants:
            print("Brak chłopów")
            return

        self.peasants -= amount

        group = PeasantGroup(self.x, self.y, self.owner, amount)
        world.peasant_groups.append(group)

        print(f"Wysłano {amount} chłopów")
        
    def send_gold(self, world, amount):
        if amount <= 0:
            return

        if amount > 1000:
            print("Max 1000 złota")
            return

        if amount > self.gold:
            print("Brak złota")
            return

        self.gold -= amount

        t = GoldTransport(self.x, self.y, self.owner, amount)
        world.gold_transports.append(t)

        print(f"Wysłano {amount} złota")

    def start_training(self, unit):
        if "school" not in self.buildings:
            print("Brak szkoły")
            return

        if unit not in self.garrison:
            print("Jednostka nie jest w garnizonie")
            return

        if unit.experience >= 12:
            print("Max doświadczenie")
            return
        if unit in self.training:
            return

        self.training[unit] = 2
        print("Szkolenie rozpoczęte")

    def start_training_selected(self, units):
        for unit in units:
            self.start_training(unit)


    def start_training_group(self, units):
        print("DEBUG: start_training_group wywołane")

        if "school" not in self.buildings:
            print("Brak szkoły")
            return

        trained = 0

        for unit in units:
            if unit in self.garrison and unit.experience < 12:
                if unit not in self.training:
                    self.training[unit] = 2
                self.training[unit] = 2
                trained += 1

        print("Rozpoczęto szkolenie:", trained)

    def process_training(self):
        finished = []

        for unit in list(self.training):
            self.training[unit] -= 1

            if self.training[unit] <= 0:
                unit.gain_training_exp()
                finished.append(unit)
                print("Szkolenie zakończone")
                
        for unit in finished:
            del self.training[unit]

            print("DEBUG training size:", len(self.training))


    def next_turn(self):
        self.update_happiness()
        self.check_plague_start()
        self.process_plague()
        self.collect_taxes()
        self.grow_population()

        self.process_production()
        self.process_healing()
        self.process_training()           
   
    def finish_production(self):
        from unit import Unit

        new_unit = Unit(
            self.production_unit_type,
            self.x,
            self.y,
            self.owner
        )

        self.garrison.append(new_unit)

        print("Wyprodukowano:", self.production_unit_type)

        self.production_enabled = False
        self.production_turns_left = 0
    
    def update_production(self, world):
        if not self.production_enabled:
            return

        self.production_turns_left -= 1
        print("Produkcja — zostało tur:", self.production_turns_left)

        if self.production_turns_left <= 0:
            unit = Unit(
                self.production_unit_type,
                self.x,
                self.y,
                self.owner
            )

            if not world.spawn_unit_near_castle(unit, self):
                print("Brak miejsca — jednostka w garnizonie")
                self.garrison.append(unit)

            self.production_enabled = False
            self.production_unit_type = None
            print("Wyprodukowano jednostkę")

        return True 