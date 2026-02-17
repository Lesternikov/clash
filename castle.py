HOSPITAL = "hospital"
import random 
from unit import PeasantGroup
from unit import GoldTransport
# castle.py
from unit import UNIT_STATS, Unit

BUILDINGS = {
    "hospital": {"cost": 200},
    "Koszary": {"cost": 200},
    "workshop": {"cost": 220},
    "forge": {"cost": 190},
    "school": {"cost": 400},}

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
        self.buildings = ["Koszary"]
        self.level = 1
        #burzenie zamku
        self.destroyed = False

                # PRODUKCJA
        self.production_unit_type = None
        self.production_turns_left = 0
        self.production_enabled = False
        self.training = {}        
       
        self.garrison_limit = 12
        self.production_unit = None
        self.max_patents = 12
        self.patents = [None] * self.max_patents       # wykupione patenty
        
        

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
    
    def recruit(self, player, unit_type):
        if self.owner != player:
            print("To nie jest twój zamek")
            return False

        return self.start_production(unit_type)

    
    def start_production(self, unit_type):

        if not any(p is not None and p["unit_type"] == unit_type for p in self.patents):
            print("Najpierw kup patent:", unit_type)
            return False

        stats = UNIT_STATS[unit_type]
        cost = stats["production_cost"]

        if self.gold < cost:
            print("Za mało złota")
            return False

        self.production_unit_type = unit_type
        self.production_turns_left = stats["production_time"]
        self.production_enabled = True

        print("Produkcja ustawiona na:", unit_type)
        return True

    def buy_patent(self, unit_type):
        if any(p is not None and p["unit_type"] == unit_type for p in self.patents):
            print("Patent już kupiony")
            return False

        stats = UNIT_STATS[unit_type]
        cost = stats["patent_cost"]

        if self.gold < cost:
            print("Za mało złota")
            return False

        for i in range(self.max_patents):
            if self.patents[i] is None:
                self.patents[i] = {
                    "unit_type": unit_type,
                    "stats": UNIT_STATS[unit_type]
                }

                self.gold -= cost
                print("Kupiono patent:", unit_type)
                return True

        print("Brak miejsca na patenty")
        return False
    
    def remove_patent(self, unit_type):
        for i in range(len(self.patents)):
            if self.patents[i] is not None and self.patents[i]["unit_type"] == unit_type:
                if self.production_unit_type == unit_type:
                    self.stop_production()

                self.patents[i] = None
                print("Usunięto patent:", unit_type)
                return True

        print("Patent nie istnieje")
        return False



    def stop_production(self):
        self.production_enabled = False
        self.production_unit_type = None
        self.production_turns_left = 0


    def process_production(self):
        if not self.production_enabled:
            return

        if self.production_unit_type is None:
            return

        if len(self.garrison) >= self.garrison_limit:
            print("Garnizon pełny — produkcja zatrzymana")
            self.production_enabled = False
            return

        self.production_turns_left -= 1
        print("Produkcja — zostało:", self.production_turns_left)

        if self.production_turns_left <= 0:
            stats = UNIT_STATS[self.production_unit_type]
            cost = stats["production_cost"]

            if self.gold < cost:
                print("Brak złota — produkcja zatrzymana")
                self.production_enabled = False
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

            # restart cyklu produkcji
            self.production_turns_left = stats["production_time"]


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
        required = {"hospital", "Koszary", "workshop", "forge"}

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

                self.garrison.append(unit)
                print("Jednostka dodana do garnizonu")

                self.production_enabled = False
                self.production_unit_type = None

    def demolish(self):
        self.destroyed = True
        self.owner = None
        self.garrison.clear()


        return True