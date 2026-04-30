import os
import pygame
from UI_components import UnitInfoWindow  # <--- IMPORTUJEMY TWOJE NOWE OKIENKO!

# =====================================================
#   GARRISON_GRAPHICS.PY
# =====================================================

GARRISON_BG    = os.path.join("assets", "garninon.png")
# Stara tabelka (DW_12_GFX) usunięta!

ORIG_W, ORIG_H = 640, 480

ORIG_SLOTS_X = [124, 195, 266, 337, 408, 479]
ORIG_SLOT_Y1 = 74
ORIG_SLOT_Y2 = 205
ORIG_SLOT_W  = 31
ORIG_SLOT_H  = 65

# Zostawiamy tylko koordynaty, żeby wiedzieć, gdzie narysować nowe okienko
ORIG_TABLE_X = 124
ORIG_TABLE_Y = 300

class GarrisonGraphics:

    def __init__(self, screen_w: int, screen_h: int):
        self.screen_w = screen_w
        self.screen_h = screen_h

        self.bg_w = ORIG_W + 386
        self.bg_h = ORIG_H + 285
        self.sx = self.bg_w / ORIG_W
        self.sy = self.bg_h / ORIG_H

        self.bg = self._load(GARRISON_BG, self.bg_w, self.bg_h)
        
        # Inicjalizacja nowego, uniwersalnego okienka statystyk
        self.info_window = UnitInfoWindow()

        # --- ANIMACJA DRZWI ---
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
        self.door_frame_indices = [0] * 12 

        # --- SLOTY ---
        self.slot_rects = self._build_slot_rects()

        # --- PRZYCISK WYPUŚĆ ---
        BTN_W, BTN_H = 155, 82
        self.btn_release_normal     = self._load("assets/przyciski/PRZ_9.png",  BTN_W, BTN_H)
        self.btn_release_pressed    = self._load("assets/przyciski/PRZ_10.png", BTN_W, BTN_H)
        self.btn_release_rect       = pygame.Rect(806, 680, BTN_W, BTN_H)
        self.btn_release_anim_timer = 0

        # --- PRZYCISK PRODUKCJA (tylko gdy koszary zbudowane) ---
        BTN_P_W, BTN_P_H = 140, 80
        self.btn_prod_normal     = self._load("assets/przyciski/PRZ_3.png",  BTN_P_W, BTN_P_H)
        self.btn_prod_pressed    = self._load("assets/przyciski/PRZ_4.png", BTN_P_W, BTN_P_H)
        self.btn_prod_rect       = pygame.Rect(255, 677, BTN_P_W, BTN_P_H)
        self.btn_prod_anim_timer = 0

        # ---PRZYCISK LECZENIA (tylko gdy zbudowany szpital)
        BTN_H_W, BTN_H_H = 140, 80
        self.btn_hosp_normal     = self._load("assets/przyciski/PRZ_5.png",  BTN_H_W, BTN_H_H)
        self.btn_hosp_pressed    = self._load("assets/przyciski/PRZ_6.png", BTN_H_W, BTN_H_H)
        self.btn_hosp_rect       = pygame.Rect(440, 677, BTN_H_W, BTN_H_H)
        self.btn_hosp_anim_timer = 0

        # ----PRZYCISK SZKOLENIA (tylko gdy zbuowana szkoła)
        BTN_S_W, BTN_S_H = 140, 80
        self.btn_school_normal     = self._load("assets/przyciski/PRZ_7.png",  BTN_S_W, BTN_S_H)
        self.btn_school_pressed    = self._load("assets/przyciski/PRZ_8.png", BTN_S_W, BTN_S_H)
        self.btn_school_rect       = pygame.Rect(622, 677, BTN_S_W, BTN_S_H)
        self.btn_school_anim_timer = 0
    # --------------------------------------------------
    # ŁADOWANIE
    # --------------------------------------------------

    def _load(self, path: str, w: int, h: int):
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
        if 0 <= slot_idx < 12:
            self.door_anim_timers[slot_idx] = pygame.time.get_ticks()
            self.door_anim_opening[slot_idx] = True
            self.door_frame_indices[slot_idx] = 0

    def _update_doors(self):
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
        # 1. Tło
        if self.bg:
            screen.blit(self.bg, (0, 0))
        else:
            screen.fill((40, 30, 20))

        # 2. Aktualizacja animacji drzwi (indywidualna dla każdego slotu!)
        self._update_doors() # <--- WAŻNE: Tu musi być liczba mnoga (doors)

        # 3. Sloty jednostek
        font     = pygame.font.SysFont("Arial", 14, bold=True)
        font_cnt = pygame.font.SysFont("Arial", 12)
        garrison = getattr(castle, 'garrison', [])

        for i, rect in enumerate(self.slot_rects):
            unit = garrison[i] if i < len(garrison) else None

            # 1. PUSTY SLOT = DRZWI
            if unit is None or not hasattr(unit, 'type'):
                idx = self.door_frame_indices[i] 
                if self.door_frames:
                    screen.blit(self.door_frames[idx], rect.topleft)
                continue

            # --- SLOT Z JEDNOSTKĄ ---
            if unit in selected_units:
                pygame.draw.rect(screen, (255, 255, 0), rect.inflate(4, 4), 3)

            owner_color = (80, 120, 200)
            if hasattr(unit, 'owner') and unit.owner:
                owner_color = getattr(unit.owner, 'color', (80, 120, 200))
            pygame.draw.rect(screen, owner_color, rect.inflate(-4, -4))

            # --- RYSOWANIE SYLWETKI ---
            drawn = False
            raw_img = None
            
            # Bezpieczne wyciąganie nazwy (nawet jeśli to słownik)
            u_name = getattr(unit, 'type_code', getattr(unit, 'type', 'Unknown'))
            if isinstance(u_name, dict):
                u_name = u_name.get("unit_type", str(u_name))
            
            u_code = u_name 
            try:
                from settings import NAME_TO_CODE, UNIT_NAMES
                if u_name in NAME_TO_CODE:
                    u_code = NAME_TO_CODE[u_name]
                else:
                    for code, name in UNIT_NAMES.items():
                        if name == u_name:
                            u_code = code
                            break
            except Exception:
                pass

            # PRIORYTET: Szukamy bezpośrednio na dysku, żeby ominąć fałszywe grafiki w pamięci gry!
            frame = (pygame.time.get_ticks() // 150) % 8
            path = f"assets/minimum/{u_code}1_I_S32/{u_code}1_I_S32_{frame}.png"
            
            if os.path.exists(path):
                raw_img = pygame.image.load(path).convert_alpha()
            else:
                # Ratunek z pamięci
                frames_list = getattr(unit, 'walk_frames', getattr(unit, 'sprites', []))
                if frames_list and len(frames_list) > 0:
                    raw_img = frames_list[frame % len(frames_list)]

            # Wykrywamy awaryjne "niewidzialne" kwadraty (zniszczy to pusty czerwony prostokąt)
            if raw_img and raw_img.get_size() == (32, 32):
                test_col = raw_img.get_at((16, 16))
                if test_col[3] == 0 or test_col == (255, 0, 255, 255) or test_col == (0, 0, 0, 255):
                    raw_img = None 

            if raw_img:
                try:
                    # Gwarancja przezroczystości (usuwamy tło magenta)
                    alpha_img = pygame.Surface(raw_img.get_size(), pygame.SRCALPHA)
                    if raw_img.get_colorkey() is None:
                        raw_img.set_colorkey((255, 0, 255))
                    alpha_img.blit(raw_img, (0, 0))
                    
                    if hasattr(pygame.transform, 'grayscale'):
                        gray_img = pygame.transform.grayscale(alpha_img)
                    else:
                        gray_img = alpha_img.copy()
                        
                    # --- POWIĘKSZENIE BEZ BLOKAD ---
                    POWIEKSZENIE = 1.6  # Teraz 1.8 wystarczy by ładnie wypełnić slot!
                    
                    img_w, img_h = gray_img.get_size()
                    new_w = int(img_w * POWIEKSZENIE - 5)
                    new_h = int(img_h * POWIEKSZENIE)
                    
                    gray_img = pygame.transform.smoothscale(gray_img, (new_w, new_h))
                    screen.blit(gray_img, (rect.centerx - gray_img.get_width()//2, 
                                           rect.centery - gray_img.get_height()//2))
                    drawn = True
                except Exception as e:
                    print(f"Błąd grafiki jednostki: {e}")
                    
            # Fallback tekstowy (teraz zadziała, jeśli usunęliśmy fałszywą grafikę)
            if not drawn:
                label = str(u_name)[:4].upper()
                txt   = font.render(label, True, (255, 255, 255))
                screen.blit(txt, txt.get_rect(centerx=rect.centerx, centery=rect.centery))
                
            count = getattr(unit, 'count', 1)
            if count > 1:
                c_txt = font_cnt.render(str(count), True, (255, 255, 0))
                screen.blit(c_txt, (rect.right - c_txt.get_width() - 2,
                                    rect.bottom - c_txt.get_height() - 2))
                             
# 4. Tabelka statystyk (NOWE OKIENKO Z UI_COMPONENTS)
        if inspected_unit is not None:
            info_x = int(ORIG_TABLE_X * self.sx)
            info_y = int(ORIG_TABLE_Y * self.sy)
            # Rysujemy nasze piękne, uniwersalne okno w starych koordynatach
            self.info_window.draw_combat_info(screen, info_x, info_y, inspected_unit)

        # --- PRZYCISKI DOLNE (SZPITAL, SZKOŁA, KOSZARY) ---
        built = [b.lower() for b in getattr(castle, 'buildings', [])]
        now = pygame.time.get_ticks()

        # 6. Przycisk PRODUKCJA (Koszary) - PRZ_3 / PRZ_4
        if "koszary" in built:
            elapsed_p = now - self.btn_prod_anim_timer
            # Jeśli kliknięto w ciągu ostatnich 200ms, pokaż mniejszą/wciśniętą grafikę
            is_pressed = self.btn_prod_anim_timer > 0 and elapsed_p < 200
            img = self.btn_prod_pressed if is_pressed else self.btn_prod_normal
            if img:
                screen.blit(img, self.btn_prod_rect.topleft)

        # 7. Przycisk LECZENIA (Szpital) - PRZ_5 / PRZ_6
        if "hospital" in built:
            elapsed_h = now - self.btn_hosp_anim_timer
            is_pressed = self.btn_hosp_anim_timer > 0 and elapsed_h < 200
            img = self.btn_hosp_pressed if is_pressed else self.btn_hosp_normal
            if img:
                screen.blit(img, self.btn_hosp_rect.topleft)

        # 8. Przycisk SZKOLENIA (Szkoła) - PRZ_7 / PRZ_8
        if "school" in built:
            elapsed_s = now - self.btn_school_anim_timer
            is_pressed = self.btn_school_anim_timer > 0 and elapsed_s < 200
            img = self.btn_school_pressed if is_pressed else self.btn_school_normal
            if img:
                screen.blit(img, self.btn_school_rect.topleft)
                
        # Przycisk WYPUŚĆ (zawsze widoczny)
        elapsed_r = now - self.btn_release_anim_timer
        is_pressed_r = self.btn_release_anim_timer > 0 and elapsed_r < 200
        btn_img = self.btn_release_pressed if is_pressed_r else self.btn_release_normal
        if btn_img:
            screen.blit(btn_img, self.btn_release_rect.topleft)

        return self.slot_rects
        
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
        if not self.btn_release_rect.collidepoint(mx, my):
            return False
        if not selected_units:
            return False
        self.btn_release_anim_timer = pygame.time.get_ticks()
        return True

    def handle_prod_click(self, mx, my, castle) -> bool:
        has_koszary = "koszary" in [b.lower() for b in getattr(castle, 'buildings', [])]
        if not has_koszary:
            return False
        if not self.btn_prod_rect.collidepoint(mx, my):
            return False
        self.btn_prod_anim_timer = pygame.time.get_ticks()
        return True
    
    def handle_hosp_click(self, mx, my, castle) -> bool:
        """Zwraca True jeśli kliknięto LECZENIE i szpital jest zbudowany."""
        has_hospital = "hospital" in [b.lower() for b in getattr(castle, 'buildings', [])]
        if not has_hospital:
            return False
        if not self.btn_hosp_rect.collidepoint(mx, my):
            return False
        self.btn_hosp_anim_timer = pygame.time.get_ticks()
        return True

    def handle_school_click(self, mx, my, castle) -> bool:
        """Zwraca True jeśli kliknięto SZKOLENIE i szkoła jest zbudowana."""
        built = [b.lower() for b in getattr(castle, 'buildings', [])]
        has_school = "school" in built or "szkola" in built
        if not has_school:
            return False
        if not self.btn_school_rect.collidepoint(mx, my):
            return False
        self.btn_school_anim_timer = pygame.time.get_ticks()
        return True
    
    if __name__ == "__main__":
        import subprocess, sys, os
        main_path = os.path.join(os.path.dirname(__file__), "main.py")
        subprocess.run([sys.executable, main_path])
        