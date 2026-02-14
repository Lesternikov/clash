class General:
    def __init__(self, owner):
        self.owner = owner
        self.name = "Generał"
        self.moves = 7
        self.alive = True

    def apply_bonus(self, unit):
        unit.attack += 3
        unit.defense += 3

        if hasattr(unit, "max_ammo"):
            unit.ammo = unit.max_ammo

        unit.fatigue = 0
        
class ArmyGroup:
    def __init__(self):
        self.units = []
        self.general = None
