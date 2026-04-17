import os
import pygame

# Ścieżki i mapowania (zostają te same co wcześniej)
CASTLE_GFX_PATH = os.path.join("assets", "zamek_widoki")

LEFT_SIDE_MAP = {
    frozenset(): "Z_01",
    frozenset(["hospital"]): "Z_03",
    frozenset(["workshop"]): "Z_05",
    frozenset(["hospital", "workshop"]): "Z_07",
    frozenset(["koszary"]): "Z_09",
    frozenset(["koszary", "hospital"]): "Z_10",
    frozenset(["koszary", "workshop"]): "Z_11",
    frozenset(["koszary", "hospital", "workshop"]): "Z_12",
}

RIGHT_SIDE_MAP = {
    frozenset(): "Z_02",
    frozenset(["school"]): "Z_04",
    frozenset(["forge"]): "Z_06",
    frozenset(["school", "forge"]): "Z_08",
}

LEFT_BUILDINGS = {"hospital", "workshop", "koszary"}
RIGHT_BUILDINGS = {"school", "forge"}

class CastleGraphics:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_w = screen_width
        self.screen_h = screen_height
        self.images = {} # GFX
        self.masks = {}  # M_GFX
        
        # MAPA KOLORÓW Z TWOICH PLIKÓW:
        self.COLOR_MAP = {
            (255, 255, 0): "court",      # ŻÓŁTY -> Dwór
            (255, 255, 255): "court", # BIAŁY -> Dwór
            (0, 0, 255):   "koszary",    # NIEBIESKI -> Koszary
            (255, 0, 255): "hospital",   # RÓŻOWY -> Szpital
            (0, 255, 255): "workshop",   # CYJAN -> Warsztat
            (255, 0, 0):   "school",     # CZERWONY -> Szkoła
            (0, 255, 0):   "forge",      # ZIELONY -> Kuźnia
            (128, 0, 255): "peasants",   # FIOLETOWY -> Chłopi
        }
        
        self._load_all()

    def _load_img(self, name: str, is_mask=False) -> pygame.Surface | None:
        suffix = "M_GFX.png" if is_mask else "_GFX.png"
        path = os.path.join(CASTLE_GFX_PATH, f"{name}{suffix}")
        
        if not os.path.exists(path):
            return None
        
        # convert() jest szybszy dla masek z colorkey
        img = pygame.image.load(path).convert()
        
        # KLUCZOWA POPRAWKA: Maski też muszą mieć przezroczystą czerń!
        # Dzięki temu lewa i prawa maska nie będą się nawzajem zasłaniać.
        img.set_colorkey((0, 0, 0)) 
            
        return pygame.transform.scale(img, (self.screen_w, self.screen_h))

    def _load_all(self):
        # Ładujemy wszystkie 13 stanów (GFX i Maski)
        for i in range(1, 14):
            name = f"Z_{str(i).zfill(2)}"
            self.images[name] = self._load_img(name, is_mask=False)
            self.masks[name] = self._load_img(name, is_mask=True)

    def get_building_at_pos(self, mx, my, castle):
        raw_buildings = getattr(castle, "buildings", [])
        buildings = set(b.lower() for b in raw_buildings)

        # 1. Priorytet dla pełnego zamku
        all_req = {b.lower() for b in (LEFT_BUILDINGS | RIGHT_BUILDINGS)}
        if all_req.issubset(buildings):
            return self._check_mask(self.masks.get("Z_13"), mx, my, "Z_13")

        # 2. Sprawdzamy warstwy: Prawa, potem Lewa
        # (Zmieniamy kolejność, bo prawa strona w Clashu jest często "nad" lewą)
        right_built = frozenset(b for b in buildings if b in RIGHT_BUILDINGS)
        right_key = RIGHT_SIDE_MAP.get(right_built, "Z_02")
        
        left_built = frozenset(b for b in buildings if b in LEFT_BUILDINGS)
        left_key = LEFT_SIDE_MAP.get(left_built, "Z_01")

        # Najpierw sprawdzamy prawą maskę
        res = self._check_mask(self.masks.get(right_key), mx, my, right_key)
        if res: return res
        
        # Jeśli nic nie było na prawej, sprawdzamy lewą
        return self._check_mask(self.masks.get(left_key), mx, my, left_key)

    def _check_mask(self, mask, mx, my, file_name):
        if not mask: return None
        try:
            color = mask.get_at((mx, my))
            rgb = (color.r, color.g, color.b)
            
            # Ignorujemy czarny (tło)
            if rgb == (0, 0, 0): return None
            
            result = self.COLOR_MAP.get(rgb)
            
            # DEBUG: Pomoże nam sprawdzić dlaczego Dwór to Garnizon
            if result:
                print(f"KLIK! Plik: {file_name} | Kolor RGB: {rgb} | Budynek: {result}")
            else:
                # Jeśli trafiliśmy w kolor, którego nie ma w COLOR_MAP
                print(f"NIEZNANY KOLOR! Plik: {file_name} | RGB: {rgb}")
                
            return result
        except IndexError:
            return None
        
    def draw(self, screen: pygame.Surface, castle, debug_mode=False) -> None:
        # 1. Tło
        screen.fill((60, 50, 40))

        raw_buildings = getattr(castle, "buildings", [])
        buildings = set(b.lower() for b in raw_buildings)

        # Logika wyboru kluczy (lewa/prawa)
        left_built = frozenset(b for b in buildings if b in LEFT_BUILDINGS)
        left_key = LEFT_SIDE_MAP.get(left_built, "Z_01")
        
        right_built = frozenset(b for b in buildings if b in RIGHT_BUILDINGS)
        right_key = RIGHT_SIDE_MAP.get(right_built, "Z_02")

        # WYBÓR: Rysujemy normalne grafiki czy maski?
        source_dict = self.masks if debug_mode else self.images

        img_l = source_dict.get(left_key)
        img_r = source_dict.get(right_key)

        # Rysujemy
        if img_l: screen.blit(img_l, (0, 0))
        if img_r: screen.blit(img_r, (0, 0))

        # Dodatkowy napis informacyjny w trybie debugowania
        if debug_mode:
            font = pygame.font.SysFont("Arial", 20, bold=True)
            txt = font.render(f"TRYB DEBUG MASKI | Lewa: {left_key} | Prawa: {right_key}", True, (255, 0, 0))
            screen.blit(txt, (10, 10))