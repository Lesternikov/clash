import os
import pygame

# =====================================================
#   GARRISON_GRAPHICS.PY
# =====================================================

GARRISON_BG    = os.path.join("assets", "garninon.png")
GARRISON_TABLE = os.path.join("assets", "DW_12_GFX.png")

ORIG_W, ORIG_H = 640, 480

ORIG_SLOTS_X = [124, 195, 266, 337, 408, 479]
ORIG_SLOT_Y1 = 74
ORIG_SLOT_Y2 = 205
ORIG_SLOT_W  = 31
ORIG_SLOT_H  = 65

ORIG_TABLE_X = 124
ORIG_TABLE_Y = 300
ORIG_TABLE_W = 390
ORIG_TABLE_H = 140


class GarrisonGraphics:

    def __init__(self, screen_w: int, screen_h: int):
        self.screen_w = screen_w
        self.screen_h = screen_h

        self.bg_w = ORIG_W + 386
        self.bg_h = ORIG_H + 285
        self.sx = self.bg_w / ORIG_W
        self.sy = self.bg_h / ORIG_H

        self.bg    = self._load(GARRISON_BG,    self.bg_w, self.bg_h)
        self.table = self._load(GARRISON_TABLE,
                                int(ORIG_TABLE_W * self.sx),
                                int(ORIG_TABLE_H * self.sy))

# --- TESTOWE ŁADOWANIE 5 GRAFIK PASKA (BEZ PIKSELOZY) ---
        self.top_bar_parts = []
        for i in range(5):
            path = os.path.join("assets", f"DZ_INFO_S32_{i}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                # Używamy SMOOTHSCALE dla efektu "ładnego wygładzenia"
                # Skalujemy o 2.5x żeby były dobrze widoczne na górze
                w, h = img.get_size()
                smooth_img = pygame.transform.smoothscale(img, (int(w * 2.5), int(h * 2.5)))
                self.top_bar_parts.append(smooth_img)

        # --- ANIMACJA DRZWI ---
        # Kolejność od zamkniętych do otwartych:
        # KEEP7=zamknięte, KEEP6..KEEP1=pośrednie, KEEP=otwarte
        door_files = [
            "assets/KEEP.png",
            "assets/KEEP1.png",
            "assets/KEEP2.png",
            "assets/KEEP3.png",
            "assets/KEEP4.png",
            "assets/KEEP5.png",
            "assets/KEEP6.png",
            "assets/KEEP7.png",
        ]
        sw = int(ORIG_SLOT_W * self.sx)
        sh = int(ORIG_SLOT_H * self.sy)
        self.door_frames = []
        for path in door_files:
            img = self._load_raw(path)
            if img:
                self.door_frames.append(pygame.transform.scale(img, (sw, sh)))
            else:
                surf = pygame.Surface((sw, sh))
                surf.fill((10, 10, 10))
                self.door_frames.append(surf)

       # --- INDYWIDUALNA ANIMACJA DRZWI ---
        self.door_anim_timers = [0] * 12
        self.door_anim_opening = [False] * 12
        self.door_frame_indices = [0] * 12 # 0 to stan domyślny (np. zamknięte)   

        # --- SLOTY ---
        self.slot_rects = self._build_slot_rects()

        # --- TABELKA ---
        self.table_rect = pygame.Rect(
            int(ORIG_TABLE_X * self.sx),
            int(ORIG_TABLE_Y * self.sy),
            int(ORIG_TABLE_W * self.sx),
            int(ORIG_TABLE_H * self.sy)
        )

        # --- PRZYCISK WYPUŚĆ ---
        BTN_W, BTN_H = 212, 83
        self.btn_release_normal     = self._load("assets/wyrzut.png",  BTN_W, BTN_H)
        self.btn_release_pressed    = self._load("assets/wyrzutp.png", BTN_W, BTN_H)
        self.btn_release_rect       = pygame.Rect(805, 690, BTN_W, BTN_H)
        self.btn_release_anim_timer = 0

        # --- PRZYCISK PRODUKCJA (tylko gdy koszary zbudowane) ---
        BTN_P_W, BTN_P_H = 117, 51
        self.btn_prod_normal     = self._load("assets/prod.png",  BTN_P_W, BTN_P_H)
        self.btn_prod_pressed    = self._load("assets/pprod.png", BTN_P_W, BTN_P_H)
        self.btn_prod_rect       = pygame.Rect(620, 710, BTN_P_W, BTN_P_H)
        self.btn_prod_anim_timer = 0

    # --------------------------------------------------
    # ŁADOWANIE
    # --------------------------------------------------

    def _load(self, path: str, w: int, h: int):
        if not os.path.exists(path):
            print(f"[GarrisonGraphics] BRAK PLIKU: {path}")
            return None
        img = pygame.image.load(path).convert_alpha()
            # smoothscale tutaj też zapewni lepszą jakość tła
        return pygame.transform.smoothscale(img, (w, h))
    
    def _load_raw(self, path: str):
        if not os.path.exists(path):
            print(f"[GarrisonGraphics] BRAK PLIKU: {path}")
            return None
        return pygame.image.load(path).convert_alpha()

    # --------------------------------------------------
    # SLOTY
    # --------------------------------------------------

    def _build_slot_rects(self) -> list:
        rects = []
        sw = int(ORIG_SLOT_W * self.sx)
        sh = int(ORIG_SLOT_H * self.sy)
        for orig_y in [ORIG_SLOT_Y1, ORIG_SLOT_Y2]:
            y = int(orig_y * self.sy)
            for orig_x in ORIG_SLOTS_X:
                x = int(orig_x * self.sx)
                rects.append(pygame.Rect(x, y, sw, sh))
        return rects

    # --------------------------------------------------
    # ANIMACJA DRZWI
    # --------------------------------------------------

    def trigger_door_open(self, slot_idx):
        """Uruchamia animację tylko dla konkretnego slotu."""
        if 0 <= slot_idx < 12:
            self.door_anim_timers[slot_idx] = pygame.time.get_ticks()
            self.door_anim_opening[slot_idx] = True
            self.door_frame_indices[slot_idx] = 0

    def _update_doors(self):
        """Aktualizuje stan animacji dla każdego slotu z osobna."""
        now = pygame.time.get_ticks()
        frame_duration = 80 

        for i in range(12):
            if self.door_anim_timers[i] == 0:
                continue

            elapsed = now - self.door_anim_timers[i]
            if self.door_anim_opening[i]:
                self.door_frame_indices[i] = min(7, elapsed // frame_duration)
                if self.door_frame_indices[i] >= 7:
                    self.door_anim_opening[i] = False
                    self.door_anim_timers[i] = now
            else:
                self.door_frame_indices[i] = max(0, 7 - elapsed // frame_duration)
                if self.door_frame_indices[i] <= 0:
                    self.door_anim_timers[i] = 0
                    self.door_frame_indices[i] = 0

    def draw(self, screen, castle, selected_units, inspected_unit=None) -> list:
        """
        Rysuje ekran garnizonu.
        Zwraca slot_rects do obsługi kliknięć w world.py.
        """

        # 1. Tło
        if self.bg:
            screen.blit(self.bg, (0, 0))
        else:
            screen.fill((40, 30, 20))

        # 2. Aktualizacja animacji drzwi (indywidualna dla każdego slotu!)
        self._update_doors() # <--- WAŻNE: Tu musi być liczba mnoga (doors)

        # 2. --- RYSOWANIE TESTOWEGO PASKA NA GÓRZE ---
        # Układamy te 5 grafik jedna obok drugiej na środku ekranu
        if self.top_bar_parts:
            total_w = sum(img.get_width() for img in self.top_bar_parts)
            start_x = (self.bg_w - total_w) // 2
            current_x = start_x
            for img in self.top_bar_parts:
                screen.blit(img, (current_x, 10)) # 10 pikseli od górnej krawędzi
                current_x += img.get_width()

        # 3. Sloty jednostek
        font     = pygame.font.SysFont("Arial", 14, bold=True)
        font_cnt = pygame.font.SysFont("Arial", 12)
        garrison = getattr(castle, 'garrison', [])

        for i, rect in enumerate(self.slot_rects):
            unit = garrison[i] if i < len(garrison) else None

            if unit is None:
                # --- PUSTY SLOT: rysuj drzwi z INDYWIDUALNĄ klatką animacji ---
                # Każdy slot (i) ma swój własny index klatki
                idx = self.door_frame_indices[i] 
                if self.door_frames:
                    screen.blit(self.door_frames[idx], rect.topleft)
                continue

            # --- SLOT Z JEDNOSTKĄ ---

            # Żółta ramka zaznaczenia
            if unit in selected_units:
                pygame.draw.rect(screen, (255, 255, 0), rect.inflate(4, 4), 3)

            # Tło koloru gracza
            owner_color = (80, 120, 200)
            if hasattr(unit, 'owner') and unit.owner:
                owner_color = getattr(unit.owner, 'color', (80, 120, 200))
            pygame.draw.rect(screen, owner_color, rect.inflate(-4, -4))

            # Nazwa jednostki
            label = unit.type[:4].upper()
            txt   = font.render(label, True, (255, 255, 255))
            screen.blit(txt, txt.get_rect(centerx=rect.centerx, top=rect.top + 4))

            # Liczba jednostek
            count = getattr(unit, 'count', 1)
            if count > 1:
                c_txt = font_cnt.render(str(count), True, (255, 255, 0))
                screen.blit(c_txt, (rect.right - c_txt.get_width() - 2,
                                    rect.bottom - c_txt.get_height() - 2))

            # Overlay szkolenia
            if hasattr(castle, 'training') and unit in castle.training:
                ov = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                ov.fill((0, 0, 0, 140))
                screen.blit(ov, rect.topleft)
                turns = castle.training[unit]
                t_txt = font.render(str(turns), True, (255, 255, 0))
                screen.blit(t_txt, t_txt.get_rect(center=rect.center))

        # 4. Tabelka statystyk (prawy klik)
        if inspected_unit is not None:
            self._draw_unit_table(screen, inspected_unit)

        # 5. Przycisk WYPUŚĆ (zawsze widoczny)
        elapsed    = pygame.time.get_ticks() - self.btn_release_anim_timer
        is_pressed = self.btn_release_anim_timer > 0 and elapsed < 400
        btn_img    = self.btn_release_pressed if is_pressed else self.btn_release_normal
        if btn_img:
            screen.blit(btn_img, self.btn_release_rect.topleft)

        # 6. Przycisk PRODUKCJA (tylko gdy koszary zbudowane)
        has_koszary = "koszary" in [b.lower() for b in getattr(castle, 'buildings', [])]
        if has_koszary:
            elapsed_p    = pygame.time.get_ticks() - self.btn_prod_anim_timer
            is_pressed_p = self.btn_prod_anim_timer > 0 and elapsed_p < 400
            prod_img     = self.btn_prod_pressed if is_pressed_p else self.btn_prod_normal
            if prod_img:
                screen.blit(prod_img, self.btn_prod_rect.topleft)

        return self.slot_rects
    # --------------------------------------------------
    # TABELKA JEDNOSTKI
    # --------------------------------------------------

    def _draw_unit_table(self, screen: pygame.Surface, unit) -> None:
        r = self.table_rect

        if self.table:
            screen.blit(self.table, r.topleft)
        else:
            pygame.draw.rect(screen, (40, 30, 25), r)
            pygame.draw.rect(screen, (200, 180, 100), r, 3)

        font  = pygame.font.SysFont("Arial", 16, bold=True)
        font2 = pygame.font.SysFont("Arial", 14)

        header = font.render(unit.type, True, (255, 255, 200))
        screen.blit(header, (r.x + 10, r.y + 8))

        stats = [
            ("ATK", getattr(unit, 'attack',      0)),
            ("DEF", getattr(unit, 'defense',     0)),
            ("HP",  getattr(unit, 'health',      0)),
            ("MOR", getattr(unit, 'morale',      0)),
            ("MOV", int(getattr(unit, 'move_points', 0))),
            ("EXP", getattr(unit, 'experience',  0)),
        ]

        col_w = r.w // 3
        for idx, (label, val) in enumerate(stats):
            col = idx % 3
            row = idx // 3
            x   = r.x + 10 + col * col_w
            y   = r.y + 35 + row * 22
            txt = font2.render(f"{label}: {val}", True, (255, 255, 255))
            screen.blit(txt, (x, y))

    # --------------------------------------------------
    # OBSŁUGA KLIKNIĘĆ
    # --------------------------------------------------

    def handle_release_click(self, mx, my, selected_units: list) -> bool:
        """Zwraca True jeśli kliknięto WYPUŚĆ i są zaznaczone jednostki."""
        if not self.btn_release_rect.collidepoint(mx, my):
            return False
        if not selected_units:
            return False
        self.btn_release_anim_timer = pygame.time.get_ticks()
        return True

    def handle_prod_click(self, mx, my, castle) -> bool:
        """Zwraca True jeśli kliknięto PRODUKCJA i koszary są zbudowane."""
        has_koszary = "koszary" in [b.lower() for b in getattr(castle, 'buildings', [])]
        if not has_koszary:
            return False
        if not self.btn_prod_rect.collidepoint(mx, my):
            return False
        self.btn_prod_anim_timer = pygame.time.get_ticks()
        return True
    
    
    if __name__ == "__main__":
        import subprocess, sys, os
        main_path = os.path.join(os.path.dirname(__file__), "main.py")
        subprocess.run([sys.executable, main_path])
        