import os
import pygame

# =====================================================
#   CASTLE_GRAPHICS.PY
#   System wyświetlania grafiki wnętrza zamku.
#
#   Grafika zamku składa się z DWÓCH WARSTW:
#     - Lewa strona:  szpital, koszary, warsztat
#     - Prawa strona: szkoła, kuźnia
#
#   Pliki graficzne (wszystkie w assets/zamek_widoki/):
#     Z_01_GFX.png  - pusta lewa strona
#     Z_02_GFX.png  - pusta prawa strona
#     Z_03_GFX.png  - szpital (lewa)
#     Z_04_GFX.png  - szkoła (prawa)
#     Z_05_GFX.png  - warsztat (lewa)
#     Z_06_GFX.png  - kuźnia (prawa)
#     Z_07_GFX.png  - szpital + warsztat (lewa)
#     Z_08_GFX.png  - szkoła + kuźnia (prawa)
#     Z_09_GFX.png  - koszary (lewa)
#     Z_10_GFX.png  - koszary + szpital (lewa)
#     Z_11_GFX.png  - koszary + warsztat (lewa)
#     Z_12_GFX.png  - koszary + szpital + warsztat (lewa)
#     Z_13_GFX.png  - pełny zamek (obie strony)
#
#   Logika:
#     Lewa warstwa  + Prawa warstwa  = finalny widok
#     np. koszary+szpital + szkoła   = Z_10 nałożone na Z_04
# =====================================================

# Ścieżka do folderu z grafikami zamku
# ZMIEŃ jeśli trzymasz pliki w innym miejscu
CASTLE_GFX_PATH = os.path.join("assets", "zamek_widoki")

# -------------------------------------------------------
# MAPOWANIE: jakie budynki → który plik lewej strony
# -------------------------------------------------------
# Klucz: frozenset zbudowanych budynków po lewej stronie
# Wartość: numer pliku Z_XX

LEFT_SIDE_MAP = {
    frozenset():                                    "Z_01",  # pusta lewa
    frozenset(["hospital"]):                        "Z_03",  # szpital
    frozenset(["workshop"]):                        "Z_05",  # warsztat
    frozenset(["hospital", "workshop"]):            "Z_07",  # szpital + warsztat
    frozenset(["Koszary"]):                         "Z_09",  # koszary
    frozenset(["Koszary", "hospital"]):             "Z_10",  # koszary + szpital
    frozenset(["Koszary", "workshop"]):             "Z_11",  # koszary + warsztat
    frozenset(["Koszary", "hospital", "workshop"]): "Z_12",  # koszary + szpital + warsztat
}

# -------------------------------------------------------
# MAPOWANIE: jakie budynki → który plik prawej strony
# -------------------------------------------------------
RIGHT_SIDE_MAP = {
    frozenset():                        "Z_02",  # pusta prawa
    frozenset(["school"]):              "Z_04",  # szkoła
    frozenset(["forge"]):               "Z_06",  # kuźnia
    frozenset(["school", "forge"]):     "Z_08",  # szkoła + kuźnia
}

# Budynki należące do lewej i prawej strony
LEFT_BUILDINGS  = {"hospital", "workshop", "Koszary"}
RIGHT_BUILDINGS = {"school", "forge"}


class CastleGraphics:
    """
    Ładuje i zarządza grafikami widoku wnętrza zamku.
    Użycie:
        W World.__init__:
            self.castle_gfx = CastleGraphics(screen_width, screen_height)
        W draw_castle_interface:
            self.castle_gfx.draw(screen, castle)
    """

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_w = screen_width
        self.screen_h = screen_height
        self.images = {}          # nazwa_pliku -> pygame.Surface
        self.special_full = None  # Z_13 - pełny zamek (obie strony)
        self._load_all()

    # --------------------------------------------------
    # ŁADOWANIE
    # --------------------------------------------------

    def _load_img(self, name: str) -> pygame.Surface | None:
        """Ładuje jeden plik PNG i skaluje do rozmiaru ekranu."""
        path = os.path.join(CASTLE_GFX_PATH, f"{name}_GFX.png")
        if not os.path.exists(path):
            print(f"[CastleGraphics] BRAK PLIKU: {path}")
            return None
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, (self.screen_w, self.screen_h))
        return img

    def _load_all(self):
        """Ładuje wszystkie 13 grafik do słownika."""
        all_files = set(LEFT_SIDE_MAP.values()) | set(RIGHT_SIDE_MAP.values()) | {"Z_13"}
        for name in all_files:
            self.images[name] = self._load_img(name)
        self.special_full = self.images.get("Z_13")

    # --------------------------------------------------
    # WYBÓR GRAFIKI
    # --------------------------------------------------

    def _get_left_img(self, buildings: set) -> pygame.Surface | None:
        """Zwraca grafikę lewej strony na podstawie zbudowanych budynków."""
        left_built = frozenset(b for b in buildings if b in LEFT_BUILDINGS)
        key = LEFT_SIDE_MAP.get(left_built, "Z_01")
        return self.images.get(key)

    def _get_right_img(self, buildings: set) -> pygame.Surface | None:
        """Zwraca grafikę prawej strony na podstawie zbudowanych budynków."""
        right_built = frozenset(b for b in buildings if b in RIGHT_BUILDINGS)
        key = RIGHT_SIDE_MAP.get(right_built, "Z_02")
        return self.images.get(key)

    def _is_fully_built(self, buildings: set) -> bool:
        """Sprawdza czy wszystkie budynki są zbudowane → użyj Z_13."""
        all_buildings = LEFT_BUILDINGS | RIGHT_BUILDINGS
        return all_buildings.issubset(buildings)

    # --------------------------------------------------
    # RYSOWANIE
    # --------------------------------------------------

    def draw(self, screen: pygame.Surface, castle) -> None:
        """
        Główna funkcja — wywołaj ją na początku draw_castle_interface().
        Nakłada lewą i prawą warstwę graficzną zależnie od stanu zamku.
        """
        buildings = set(getattr(castle, "buildings", []))

        # Specjalny przypadek: wszystkie budynki → Z_13
        if self._is_fully_built(buildings):
            if self.special_full:
                screen.blit(self.special_full, (0, 0))
            else:
                screen.fill((60, 50, 40))
            return

        # Normalne nakładanie: lewa + prawa warstwa
        left_img  = self._get_left_img(buildings)
        right_img = self._get_right_img(buildings)

        if left_img:
            screen.blit(left_img, (0, 0))
        else:
            screen.fill((60, 50, 40))

        if right_img:
            # Prawa strona nakładana z pełną przezroczystością (alpha blending)
            screen.blit(right_img, (0, 0))

    def debug_info(self, castle) -> str:
        """Pomocnicze: zwraca info o aktualnym stanie grafiki (do drukowania)."""
        buildings = set(getattr(castle, "buildings", []))
        left_built  = frozenset(b for b in buildings if b in LEFT_BUILDINGS)
        right_built = frozenset(b for b in buildings if b in RIGHT_BUILDINGS)
        left_key  = LEFT_SIDE_MAP.get(left_built, "Z_01")
        right_key = RIGHT_SIDE_MAP.get(right_built, "Z_02")
        return f"Lewa: {left_key} {set(left_built)} | Prawa: {right_key} {set(right_built)}"