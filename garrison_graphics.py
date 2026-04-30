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
        BTN_W, BTN_H = 212, 83
        self.btn_release_normal     = self._load("assets/wyrzut.png",  BTN_W, BTN_H)
        self.btn_release_pressed    = self._load("assets/wyrzutp.png", BTN_W, BTN_H)
        self.btn_release_rect       = pygame.Rect(805, 690, BTN_W, BTN_H)
        self.btn_release_anim_timer = 0

        # --- PRZYCISK PRODUKCJA ---
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
        if 0 <= slot_idx < 8:
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

        # 2. Aktualizacja animacji drzwi
        self._update_doors()

        # 3. Sloty jednostek
        font     = pygame.font.SysFont("Arial", 14, bold=True)
        font_cnt = pygame.font.SysFont("Arial", 12)
        garrison = getattr(castle, 'garrison', [])

        for i, rect in enumerate(self.slot_rects):
            unit = garrison[i] if i < len(garrison) else None

            if unit is None:
                idx = self.door_frame_indices[i] 
                if self.door_frames:
                    screen.blit(self.door_frames[idx], rect.topleft)
                continue

            # Żółta ramka zaznaczenia
            if unit in selected_units:
                pygame.draw.rect(screen, (255, 255, 0), rect.inflate(4, 4), 3)

            # Tło koloru gracza
            owner_color = (80, 120, 200)
            if hasattr(unit, 'owner') and unit.owner:
                owner_color = getattr(unit.owner, 'color', (80, 120, 200))
            pygame.draw.rect(screen, owner_color, rect.inflate(-4, -4))

            # --- ANIMOWANA SZARA SYLWETKA ---
            drawn = False
            frame = (pygame.time.get_ticks() // 150) % 8
            
            if hasattr(unit, 'sprites') and unit.sprites and len(unit.sprites) > frame:
                # Pobieramy klatkę i konwertujemy na szarość
                gray_img = pygame.transform.grayscale(unit.sprites[frame])
                
                # Zabezpieczenie przed zbyt dużymi sprite'ami (opcjonalne, ale bezpieczne)
                img_w, img_h = gray_img.get_size()
                if img_w > rect.width or img_h > rect.height:
                    scale_factor = min(rect.width / img_w, rect.height / img_h) * 0.9 # 90% rozmiaru slota
                    new_w = int(img_w * scale_factor)
                    new_h = int(img_h * scale_factor)
                    gray_img = pygame.transform.smoothscale(gray_img, (new_w, new_h))
                
                # Rysowanie na środku slota
                screen.blit(gray_img, (rect.centerx - gray_img.get_width()//2, 
                                       rect.centery - gray_img.get_height()//2))
                drawn = True
                
            # Fallback: Jeśli jednostka nie ma sprite'ów, rysujemy stary tekst
            if not drawn:
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

        # 4. Tabelka statystyk (NOWE OKIENKO Z UI_COMPONENTS)
        if inspected_unit is not None:
            info_x = int(ORIG_TABLE_X * self.sx)
            info_y = int(ORIG_TABLE_Y * self.sy)
            # Rysujemy nasze piękne, uniwersalne okno w starych koordynatach
            self.info_window.draw_combat_info(screen, info_x, info_y, inspected_unit)

        # 5. Przycisk WYPUŚĆ
        elapsed    = pygame.time.get_ticks() - self.btn_release_anim_timer
        is_pressed = self.btn_release_anim_timer > 0 and elapsed < 400
        btn_img    = self.btn_release_pressed if is_pressed else self.btn_release_normal
        if btn_img:
            screen.blit(btn_img, self.btn_release_rect.topleft)

        # 6. Przycisk PRODUKCJA
        has_koszary = "koszary" in [b.lower() for b in getattr(castle, 'buildings', [])]
        if has_koszary:
            elapsed_p    = pygame.time.get_ticks() - self.btn_prod_anim_timer
            is_pressed_p = self.btn_prod_anim_timer > 0 and elapsed_p < 400
            prod_img     = self.btn_prod_pressed if is_pressed_p else self.btn_prod_normal
            if prod_img:
                screen.blit(prod_img, self.btn_prod_rect.topleft)

        return self.slot_rects

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
    
    if __name__ == "__main__":
        import subprocess, sys, os
        main_path = os.path.join(os.path.dirname(__file__), "main.py")
        subprocess.run([sys.executable, main_path])
        