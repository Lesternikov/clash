import pygame
import os
from settings import UNIT_STATS, UNIT_NAMES, COLOR_TO_ID
        
class Unit:
    def __init__(self, type_code, x, y, owner, level=1):
        # type_code musi być kodem (np. "INFL", "BUDOW")
        self.type_code = type_code
        
        # WYMUSZAMY LICZBY - to usunie TypeError w draw_map
        try:
            self.x = int(x)
            self.y = int(y)
        except (ValueError, TypeError):
            print(f"!!! KRYTYCZNY BŁĄD ARGUMENTÓW !!!")
            print(f"Dostałem: code={type_code}, x={x}, y={y}")
            self.x = 0
            self.y = 0

        self.owner = owner
        self.level = level

        # Jeśli type_code to już jest pełna nazwa (przychodzi z produkcji w zamku)
        if type_code in UNIT_STATS:
            self.type = type_code
        else:
            # Jeśli type_code to 3-literowy kod (przychodzi z ładowania mapy)
            self.type = UNIT_NAMES.get(type_code, "Nieznany")
            
        self.name = self.type

        # Statystyki
        stats = UNIT_STATS.get(self.type, {})
        self.hp = stats.get("hp", 10)
        self.max_hp = self.hp
        self.moves = stats.get("moves", 1)
        self.move_points = self.moves
        self.experience = stats.get("exp", 0)
        self.morale = stats.get("morale", 100)
        self.fatigue = stats.get("fatigue", 0)
        self.attack = 1 if UNIT_STATS == "Budowniczy" else 5 # Przykład
        self.defense = 1
        # Inne atrybuty
        self.carried_peasants = 0
        self.carried_gold = 0
        self.production_unit_type = None
        self.production_turns_left = 0
        self.production_enabled = False
        self.gold = 0
        self.garrison = []
        self.garrison_limit = 12
        self.healing = False
        self.healing_turns_left = 0
        self.planned_path = []
        self.short_name = self.type[:2].upper()

        # 5. ŁADOWANIE GRAFIKI
        # Wywołujemy funkcję load_unit_sprites, która korzysta z type_code
        self.sprites = self.load_unit_sprites()
        self.current_frame = 0
        self.animation_speed = 0.1

    def get_effective_move_points(self):
        """Oblicza ruch armii na podstawie najsłabszej jednostki."""
        min_mp = self.move_points
        # Zakładamy, że lista 'garrison' zawiera obiekty jednostek (pasażerów)
        for u in self.garrison:
            if u is not None:
                min_mp = min(min_mp, u.move_points)
        return min_mp

    def has_fatigue_paralysis(self):
        """Sprawdza, czy ktokolwiek w armii ma 100 zmęczenia."""
        if getattr(self, 'fatigue', 0) >= 100: return True
        return any(u and getattr(u, 'fatigue', 0) >= 100 for u in self.garrison)

    def load_unit_sprites(self):
        sprites = []
        # Pobieramy ID koloru gracza
        p_color_name = getattr(self.owner, 'color_name', 'red')
        c_id = COLOR_TO_ID.get(p_color_name, 1)

        from settings import NAME_TO_CODE
        u_code = NAME_TO_CODE.get(self.type, self.type_code)

        # Folder to np. assets/minimum/INFL1_I_S32
        base_name = f"{u_code}{c_id}_I_S32"
        folder_path = f"assets/minimum/{base_name}"

        # Spróbujmy wczytać 8 klatek
        for i in range(8):
            file_path = os.path.join(folder_path, f"{base_name}_{i}.png")
            if os.path.exists(file_path):
                try:
                    img = pygame.image.load(file_path).convert_alpha()
                    w, h = img.get_size()
                    # Skalowanie o 15%
                    img = pygame.transform.smoothscale(img, (int(w * 1.15), int(h * 1.15)))
                    sprites.append(img)
                except Exception as e:
                    print(f"Błąd ładowania klatki {i}: {e}")
            else:
                # Jeśli brakuje choćby jednej klatki, robimy różowy kwadrat (fallback)
                surf = pygame.Surface((36, 36), pygame.SRCALPHA)
                pygame.draw.rect(surf, (200, 0, 200), (0,0,36,36), 1)
                sprites.append(surf)
        
        return sprites
        
    def move_along_path(self, world):
        from world import TERRAIN_TYPES # Import lokalny
        while getattr(self, 'planned_path', []):
            next_step = self.planned_path[0]
            nx, ny = next_step
            
            tile_char = world.map[ny][nx]
            
            # POPRAWKA: Odwołujemy się do world.TERRAIN_TYPES
            # Zakładając, że w world.py wkleiłeś ten słownik do klasy World
            terrain_info = TERRAIN_TYPES.get(tile_char, {})
            base_cost = terrain_info.get("cost", 4)
            
            dx = nx - self.x
            dy = ny - self.y
            move_modifier = 1.41 if (dx != 0 and dy != 0) else 1.0
            
            final_cost = base_cost * move_modifier

            if self.move_points >= final_cost:
                # Pamiętaj, żeby tu też przekazać final_cost
                if world.move_unit(self, dx, dy, cost=final_cost):
                    self.planned_path.pop(0)
                else:
                    break
            else:
                print(f"Za mało MP ({self.move_points} < {final_cost}). Koniec ruchu.")
                break
    # -----------------------
    # BASIC
    # -----------------------
    def draw(self, screen):
        # DODAJ TO: Jeśli jednostka ma x = -1, przerywamy rysowanie
        if self.x < 0:
            return
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

    # -----------------------
    # MOVEMENT
    # -----------------------

    def can_enter(self, tile):
        if tile == "#":
            return self.type == "highlander"
        return tile == "."

    def get_effective_move_points(self):
        """Zwraca punkty ruchu najsłabszej jednostki w oddziale."""
        min_mp = self.move_points
        if hasattr(self, 'garrison'):
            for u in self.garrison:
                if u is not None:
                    min_mp = min(min_mp, getattr(u, 'move_points', min_mp))
        return min_mp

    def has_fatigue_paralysis(self):
        """Sprawdza, czy ktoś w armii padł ze zmęczenia (100)."""
        if getattr(self, 'fatigue', 0) >= 100: return True
        if hasattr(self, 'garrison'):
            for u in self.garrison:
                if u is not None and getattr(u, 'fatigue', 0) >= 100: return True
        return False

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

    if __name__ == "__main__":
        import subprocess, sys, os
        main_path = os.path.join(os.path.dirname(__file__), "main.py")
        subprocess.run([sys.executable, main_path])