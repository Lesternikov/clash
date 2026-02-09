UNIT_STATS = {
    "pospolite_ruszenie":{"hp":50,"moves":5,"attack":1,"defense":1,},
    "lekka_piechota": {"hp": 100, "moves": 6, "attack": 70, "defense": 50},
    "pikinier": {"hp": 60, "moves": 7, "attack": 80, "defense": 60},
    "heavy_cavalry": {"hp": 160, "moves": 3, "attack": 120, "defense": 90},
    "light_cavalry": {"hp": 80, "moves": 10, "attack": 90, "defense": 40},
    "highlander": {"hp": 100, "moves": 6, "attack": 80, "defense": 60},
    "halberdier": {"hp": 70, "moves": 5, "attack": 90, "defense": 100},
    "elephant": {"hp": 100, "moves": 3, "attack": 100, "defense": 0},
    "ważka":{"hp":80,"moves":6,"attack":60,"defense":70,},
    "rycerstwo":{"hp":80,"moves":6,"attack":60,"defense":70,},
    "worm":{"hp":60,"moves":5,"attack":55,"defense":10},
    "scorpion":{"hp":100,"moves":8,"attack":80,"defense":80,},
    "pegasus":{"hp":120, "moves":10, "attack":80, "defense":20},
    "eagle":{"hp":100, "moves":11, "attack":90, "defense":30},
    "gohst":{"hp":100,"moves":4,"attack":80,"defense":60,},
    "bones":{"hp":90,"moves":6,"attack":60,"defense":70,},
    "heavy_infantry": {"hp": 120, "moves": 8, "attack": 50, "defense": 70},
    "smok":{"hp":150,"moves":14,"attack":100,"defense":100,},
    "trol":{"hp":90,"moves":4,"attack":60,"defense":70,},
    "mag":{"hp":140,"moves":10,"attack":100,"defense":100, "range": 6, "tags": ["ranged"]},
    "leśnik":{"hp":100,"moves":7,"attack":90,"defense":60,"range": 4, "tags": ["ranged"]},
    "katapulta":{"hp":30,"moves":3,"attack":100,"defense":80,"range": 5, "tags": ["ranged"]},
    "cyklop":{"hp":80,"moves":6,"attack":60,"defense":70,"range": 3, "tags": ["ranged"]},
    "dragon":{"hp":80,"moves":6,"attack":60,"defense":70,"range": 3, "tags": ["ranged"]},
    "płaszczka":{"hp":80,"moves":6,"attack":60,"defense":70,"range": 4, "tags": ["ranged"]},
    "archer": {"hp": 8, "moves": 8, "attack": 20, "defense": 0, "range": 3, "tags": ["ranged"]},
    "crossbowman": {"hp": 20, "moves": 6, "attack": 40, "defense": 30, "range": 4, "tags": ["ranged"]},
    "musketeer": {"hp": 25, "moves": 5, "attack": 50, "defense": 30, "range": 4, "tags": ["ranged"]},
    "armata":{"hp":80,"moves":6,"attack":60,"defense":70,"range": 5, "tags": ["ranged"]},
    "budowniczy":{"hp":80,"moves":6,"attack":60,"defense":70,},
}


class Unit:
    UNIT_COSTS = {
        "pospolite_ruszenie":0,
        "lekka_piechota": 10,
        "pikinier": 30,
        "halberdier": 50,
        "highlander": 80,
        "light_cavalry": 100,
        "heavy_cavalry": 200,
        "elephant": 300,
        "archer": 60,
        "crossbowman": 240,
        "musketeer": 290,
        "worm":250,
        "scorpion":290,
        "mag":500,
        "pegasus":350,
        "eagle":300,
        "ghost":380,
        "bones":280,
        "trol":130,
        "smok":550,
        "heavy_infantry": 30,
        "leśnik":100,
        "budowniczy":80,
        "armata":400,
        "ważka":380,
        "płaszczka":400,
        "rycerstwo":150,
        "dragon":150,
        "cyklop":280,
        "katapulta":300,
    }
    def __init__(self, unit_type, x, y, owner):
        self.type = unit_type
        self.x = x
        self.y = y
        self.owner = owner

        stats = UNIT_STATS.get(unit_type, {"hp": 100, "moves": 10, "attack": 10, "defense": 10})

        self.base_hp = stats["hp"]
        self.hp = self.base_hp
        self.attack = stats["attack"]
        self.defense = stats["defense"]
        self.move_points = stats["moves"]
        self.max_moves = stats["moves"]

        self.morale = 100
        self.fatigue = 0
        self.experience = 0
        
        # transport
        self.carried_peasants = 0
        self.carried_gold = 0

        # produkcja
        self.production_unit_type = None
        self.production_turns_left = 0
        self.production_enabled = False

        # ekonomia / garnizon
        self.gold = 0
        self.garrison = []
        self.garrison_limit = 12

        # leczenie
        self.healing = False
        self.healing_turns_left = 0

    # -----------------------
    # BASIC
    # -----------------------

    def position(self):
        return (self.x, self.y)

    def __repr__(self):
        return (
            f"{self.type} HP:{self.hp} MOR:{self.morale} "
            f"FAT:{self.fatigue} EXP:{self.experience}"
        )
# -----------------------
# EXPERIENCE SYSTEM
# -----------------------

    def veterancy_level(self):
        return self.experience // 3

    def gain_training_exp(self):
        if self.experience >= 12:
            return

        self.experience += 1

        if self.experience % 3 == 0:
            self.attack += 2
            self.defense += 2
            print("Jednostka awansowała poziomem!")

    def gain_battle_exp(self):
        old_level = self.veterancy_level()

        self.experience = min(12, self.experience + 3)

        if self.veterancy_level() > old_level:
            self.attack += 2
            self.defense += 2
            print("Jednostka awansowała po walce!")

    # -----------------------
    # DEFENSE SYSTEM
    # -----------------------

    def effective_defense(self, attacker):
        defense = self.defense

        if self.type in ["pikeman", "halberdier"] and attacker.type in [
            "light_cavalry",
            "heavy_cavalry",
        ]:
            defense *= 1.5

        return defense

    # -----------------------
    # DAMAGE
    # -----------------------

    def take_damage(self, dmg):
        self.hp = max(0, self.hp - dmg)

    def is_alive(self):
        return self.hp > 0

    def morale_modifier(self):
        if self.morale > 120:
            return 1.2
        elif self.morale < 80:
            return 0.8
        return 1.0

    def exp_modifier(self):
        return 1 + (self.experience * 0.01)

    def cavalry_attack_bonus(self, target):
        if self.type in ["pikeman", "highlander"] and target.type in ["light_cavalry", "heavy_cavalry"]:
            return 1.5
        return 1.0

    def attack_unit(self, target, log):
        base_attack = self.attack * self.morale_modifier() * self.exp_modifier()
        attack_bonus = self.cavalry_attack_bonus(target)

        target_def = target.effective_defense(self)

        damage = int(base_attack * attack_bonus - target_def * 0.5)

        attacker_stats = UNIT_STATS[self.type]
        defender_stats = UNIT_STATS[target.type]

        if "ranged" in attacker_stats.get("tags", []):
            damage += 5
            log.add("Bonus ranged!")

        damage = max(1, damage)

        target.take_damage(damage)

        log.add(f"{self.type} -> {target.type} | dmg:{damage} | hp:{target.hp}")

        self.gain_battle_exp()

        self.fatigue = min(100, self.fatigue + 15)

        if self.type == "elephant":
            target.morale = max(0, target.morale - 10)
            log.add("Słoń obniża morale przeciwnika!")

    # -----------------------
    # MOVEMENT
    # -----------------------

    def can_enter(self, tile):
        if tile == "#":
            return self.type == "highlander"
        return tile == "."

    # -----------------------
    # PRODUCTION
    # -----------------------

    def start_production(self, unit_type, production_time=3):
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
