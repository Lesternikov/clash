import main
import os
import pygame
 
# =====================================================
#   GARRISON_GRAPHICS.PY
#   System graficzny ekranu garnizonu.
#
#   Grafika tła: assets/garninon.png (638x478)
#   Grafika tabelki: assets/DW_12_GFX.png
#
#   Sloty jednostek (zmierzone na oryginale 638x478):
#     Górny rząd (6 slotów): y=74-137, x: 124,195,266,337,408,479
#     Dolny rząd (6 slotów): y=205-268, x: 124,195,266,337,408,479
#     Szerokość slotu: 31px, wysokość: 63px
#
#   Po przeskalowaniu do 1280x800 mnożymy przez:
#     scale_x = 1280/638 ≈ 2.006
#     scale_y = 800/478  ≈ 1.674
# =====================================================
 
GARRISON_BG    = os.path.join("assets", "garninon.png")
GARRISON_TABLE = os.path.join("assets", "DW_12_GFX.png")
 
# Oryginalne wymiary grafiki
ORIG_W, ORIG_H = 638, 478
 
# Oryginalne pozycje slotów (lewy górny róg każdego czarnego prostokąta)
ORIG_SLOTS_X = [124, 195, 266, 337, 408, 479]
ORIG_SLOT_Y1 = 74   # górny rząd - top
ORIG_SLOT_Y2 = 205  # dolny rząd - top
ORIG_SLOT_W  = 31
ORIG_SLOT_H  = 63
 
# Oryginalna pozycja tabelki informacyjnej (DW_12_GFX)
# Na grafice DW_12_GFX widać panel w dolnej połowie - ustawiamy go centralnie
ORIG_TABLE_X = 124
ORIG_TABLE_Y = 300
ORIG_TABLE_W = 390
ORIG_TABLE_H = 140
 
 
class GarrisonGraphics:
    """
    Ładuje i rysuje ekran garnizonu.
 
    Użycie w World.__init__:
        self.garrison_gfx = GarrisonGraphics(SCREEN_WIDTH, SCREEN_HEIGHT)
 
    Użycie w draw_garrison:
        slot_rects = self.garrison_gfx.draw(screen, castle, 
                                             self.selected_units,
                                             self.inspected_unit)
    """
 
    def __init__(self, screen_w: int, screen_h: int):
        self.screen_w = screen_w
        self.screen_h = screen_h
 
        # Faktyczny rozmiar grafiki na ekranie
        self.bg_w = ORIG_W + 400  # 1038
        self.bg_h = ORIG_H + 300  # 778

        # Współczynniki MUSZĄ odpowiadać faktycznemu rozmiarowi
        self.sx = self.bg_w / ORIG_W  # 1038 / 638 = 1.627
        self.sy = self.bg_h / ORIG_H  # 778  / 478 = 1.628

        self.bg = self._load(GARRISON_BG, self.bg_w, self.bg_h)
        self.table = self._load(GARRISON_TABLE,
                                int(ORIG_TABLE_W * self.sx),
                                int(ORIG_TABLE_H * self.sy))
 
        # Obliczamy Recty slotów w przestrzeni ekranu
        self.slot_rects = self._build_slot_rects()
 
        # Rect tabelki informacyjnej
        self.table_rect = pygame.Rect(
            int(ORIG_TABLE_X * self.sx),
            int(ORIG_TABLE_Y * self.sy),
            int(ORIG_TABLE_W * self.sx),
            int(ORIG_TABLE_H * self.sy)
        )
 
        self.btn_release_normal  = self._load_raw("assets/wyrzut.png")
        self.btn_release_pressed = self._load_raw("assets/wyrzutp.png")
        self.btn_release_rect    = pygame.Rect(790, 670, 200, 600)
        self.btn_release_anim_timer = 0

        BTN_W, BTN_H = 212, 83
        self.btn_release_normal  = self._load("assets/wyrzut.png",  BTN_W, BTN_H)
        self.btn_release_pressed = self._load("assets/wyrzutp.png", BTN_W, BTN_H)
        self.btn_release_rect    = pygame.Rect(805, 690, BTN_W, BTN_H)

    # --------------------------------------------------
    # ŁADOWANIE
    # --------------------------------------------------
 
    def _load(self, path: str, w: int, h: int) -> pygame.Surface | None:
        if not os.path.exists(path):
            print(f"[GarrisonGraphics] BRAK PLIKU: {path}")
            return None
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (w, h))
    
    def _load_raw(self, path: str):
        if not os.path.exists(path):
            print(f"[GarrisonGraphics] BRAK PLIKU: {path}")
            return None
        return pygame.image.load(path).convert_alpha()

    # --------------------------------------------------
    # BUDOWANIE RECTÓW SLOTÓW
    # --------------------------------------------------
 
    def _build_slot_rects(self) -> list[pygame.Rect]:
        """Zwraca listę 12 Rectów slotów (górny rząd 0-5, dolny 6-11)."""
        rects = []
        sw = int(ORIG_SLOT_W * self.sx)
        sh = int(ORIG_SLOT_H * self.sy)
 
        for row, orig_y in enumerate([ORIG_SLOT_Y1, ORIG_SLOT_Y2]):
            y = int(orig_y * self.sy)
            for orig_x in ORIG_SLOTS_X:
                x = int(orig_x * self.sx)
                rects.append(pygame.Rect(x, y, sw, sh))
 
        return rects
 
    # --------------------------------------------------
    # RYSOWANIE
    # --------------------------------------------------
 
    def draw(self, screen: pygame.Surface, castle,
             selected_units: list, inspected_unit=None) -> list[pygame.Rect]:
        """
        Rysuje pełny ekran garnizonu.
        Zwraca listę slot_rects żeby World mógł obsłużyć kliknięcia.
        """
        # 1. Tło
        if self.bg:
            screen.blit(self.bg, (0, 0))
        else:
            screen.fill((40, 30, 20))
 
        # 2. Sloty jednostek
        font      = pygame.font.SysFont("Arial", 14, bold=True)
        font_cnt  = pygame.font.SysFont("Arial", 12)
 
        garrison = getattr(castle, 'garrison', [])
 
        for i, rect in enumerate(self.slot_rects):
            unit = garrison[i] if i < len(garrison) else None
 
            # Ramka zaznaczenia
            if unit and unit in selected_units:
                pygame.draw.rect(screen, (255, 255, 0), rect.inflate(4, 4), 3)
 
            if unit is not None:
                # Kolor gracza jako tło jednostki
                owner_color = (80, 120, 200)
                if hasattr(unit, 'owner') and unit.owner:
                    owner_color = getattr(unit.owner, 'color', (80, 120, 200))
 
                # Wypełnienie slotu kolorem gracza
                inner = rect.inflate(-4, -4)
                pygame.draw.rect(screen, owner_color, inner)
 
                # Skrót nazwy jednostki
                label = unit.type[:4].upper()
                txt = font.render(label, True, (255, 255, 255))
                screen.blit(txt, txt.get_rect(centerx=rect.centerx,
                                               top=rect.top + 4))
 
                # Liczba (jeśli jednostka ma count)
                count = getattr(unit, 'count', 1)
                if count > 1:
                    c_txt = font_cnt.render(str(count), True, (255, 255, 0))
                    screen.blit(c_txt, (rect.right - c_txt.get_width() - 2,
                                        rect.bottom - c_txt.get_height() - 2))
 
                # Status szkolenia
                if hasattr(castle, 'training') and unit in castle.training:
                    overlay = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 140))
                    screen.blit(overlay, rect.topleft)
                    turns = castle.training[unit]
                    t_txt = font.render(str(turns), True, (255, 255, 0))
                    screen.blit(t_txt, t_txt.get_rect(center=rect.center))
 
        # 3. Tabelka informacyjna (gdy jednostka jest podglądana)
        if inspected_unit is not None:
            self._draw_unit_table(screen, inspected_unit)
        
        # Przycisk WYPUŚĆ - zawsze widoczny
        elapsed = pygame.time.get_ticks() - self.btn_release_anim_timer
        is_pressed = self.btn_release_anim_timer > 0 and elapsed < 400

        img = self.btn_release_pressed if is_pressed else self.btn_release_normal
        if img:
            screen.blit(img, self.btn_release_rect.topleft)

        return self.slot_rects
 
    # --------------------------------------------------
    # TABELKA JEDNOSTKI
    # --------------------------------------------------
 
    def _draw_unit_table(self, screen: pygame.Surface, unit) -> None:
        """Rysuje tabelkę statystyk jednostki w miejscu DW_12_GFX."""
        r = self.table_rect
 
        # Tło tabelki (grafika lub fallback)
        if self.table:
            screen.blit(self.table, r.topleft)
        else:
            pygame.draw.rect(screen, (40, 30, 25), r)
            pygame.draw.rect(screen, (200, 180, 100), r, 3)
 
        font  = pygame.font.SysFont("Arial", 16, bold=True)
        font2 = pygame.font.SysFont("Arial", 14)
 
        # Nagłówek
        header = font.render(unit.type, True, (255, 255, 200))
        screen.blit(header, (r.x + 10, r.y + 8))
 
        # Statystyki w dwóch kolumnach
        stats = [
            ("ATK",  getattr(unit, 'attack',    0)),
            ("DEF",  getattr(unit, 'defense',   0)),
            ("HP",   getattr(unit, 'health',    0)),
            ("MOR",  getattr(unit, 'morale',    0)),
            ("MOV",  int(getattr(unit, 'move_points', 0))),
            ("EXP",  getattr(unit, 'experience',0)),
        ]
 
        col_w = r.w // 3
        for idx, (label, val) in enumerate(stats):
            col = idx % 3
            row = idx // 3
            x = r.x + 10 + col * col_w
            y = r.y + 35 + row * 22
            txt = font2.render(f"{label}: {val}", True, (255, 255, 255))
            screen.blit(txt, (x, y))

    def handle_release_click(self, mx, my, selected_units: list) -> bool:
        if not self.btn_release_rect.collidepoint(mx, my):
            return False
        # Klikalne tylko gdy coś zaznaczone
        if not selected_units:
            return False
        self.btn_release_anim_timer = pygame.time.get_ticks()
        return True