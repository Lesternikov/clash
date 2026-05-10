import os
import pygame
from UI_components import UnitInfoWindow  # <--- IMPORTUJEMY TWOJE NOWE OKIENKO!

# =====================================================
#   GARRISON_GRAPHICS.PY
# =====================================================

GARRISON_BG    = os.path.join("assets", "garninon.png")
# Stara tabelka (DW_12_GFX) usunięta!

ORIG_W, ORIG_H = 640, 480

ORIG_SLOTS_X = [126, 197, 268, 339, 410, 481]
ORIG_SLOT_Y1 = 75
ORIG_SLOT_Y2 = 206
ORIG_SLOT_W  = 34
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
        BTN_W, BTN_H = 155, 83
        self.btn_release_normal     = self._load("assets/przyciski/PRZ_9.png",  BTN_W, BTN_H)
        self.btn_release_pressed    = self._load("assets/przyciski/PRZ_10.png", BTN_W, BTN_H)
        self.btn_release_rect       = pygame.Rect(806, 679, BTN_W, BTN_H)
        self.btn_release_anim_timer = 0

        # --- PRZYCISK PRODUKCJA (tylko gdy koszary zbudowane) ---
        BTN_P_W, BTN_P_H = 140, 80
        self.btn_prod_normal     = self._load("assets/przyciski/PRZ_3.png",  BTN_P_W, BTN_P_H)
        self.btn_prod_pressed    = self._load("assets/przyciski/PRZ_4.png", BTN_P_W, BTN_P_H)
        self.btn_prod_rect       = pygame.Rect(255, 679, BTN_P_W, BTN_P_H)
        self.btn_prod_anim_timer = 0

        # ---PRZYCISK LECZENIA (tylko gdy zbudowany szpital)
        BTN_H_W, BTN_H_H = 140, 80
        self.btn_hosp_normal     = self._load("assets/przyciski/PRZ_5.png",  BTN_H_W, BTN_H_H)
        self.btn_hosp_pressed    = self._load("assets/przyciski/PRZ_6.png", BTN_H_W, BTN_H_H)
        self.btn_hosp_rect       = pygame.Rect(440, 679, BTN_H_W, BTN_H_H)
        self.btn_hosp_anim_timer = 0

        # ----PRZYCISK SZKOLENIA (tylko gdy zbuowana szkoła)
        BTN_S_W, BTN_S_H = 140, 80
        self.btn_school_normal     = self._load("assets/przyciski/PRZ_7.png",  BTN_S_W, BTN_S_H)
        self.btn_school_pressed    = self._load("assets/przyciski/PRZ_8.png", BTN_S_W, BTN_S_H)
        self.btn_school_rect       = pygame.Rect(622, 679, BTN_S_W, BTN_S_H)
        self.btn_school_anim_timer = 0

        # --- IKONY STANU (Krzyżyk, Serce, Miecze) ---
        cross_path = "assets/minimum/INFO_S32/INFO_S32_30.png"
        if os.path.exists(cross_path):
            img = pygame.image.load(cross_path).convert_alpha()
            self.icon_cross = pygame.transform.scale(img, (18, 18))
            self.icon_cross.set_colorkey((255, 255, 255)) # <--- TO USUWA BIAŁE TŁO!
            
        heart_path = "assets/minimum/INFO_S32/INFO_S32_31.png"
        if os.path.exists(heart_path):
            img = pygame.image.load(heart_path).convert_alpha()
            self.icon_heart = pygame.transform.scale(img, (14, 14))
            self.icon_heart.set_colorkey((255, 255, 255)) # Dla pewności usuwamy też tutaj

        swords_path = "assets/minimum/INFO_S32/INFO_S32_15.png"
        if os.path.exists(swords_path):
            img = pygame.image.load(swords_path).convert_alpha()
            self.icon_swords = pygame.transform.scale(img, (25, 22))
            self.icon_swords.set_colorkey((255, 255, 255)) # I tutaj

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

  # --- ZAKTUALIZOWANA FUNKCJA ZAMYKANIA ---
    def trigger_door_close(self, slot_idx, ghost_unit=None):
        if 0 <= slot_idx < 12:
            self.door_anim_timers[slot_idx] = pygame.time.get_ticks()
            self.door_anim_opening[slot_idx] = False
            self.door_frame_indices[slot_idx] = 7
            # ZAPISUJEMY DUCHA! Upewnij się, że masz w __init__: self.door_ghosts = [None] * 12
            if not hasattr(self, 'door_ghosts'):
                self.door_ghosts = [None] * 12
            self.door_ghosts[slot_idx] = ghost_unit

    # --- ZAKTUALIZOWANA PĘTLA ANIMACJI ---
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
                    self.door_anim_timers[i] = 0 
            else:
                self.door_frame_indices[i] = max(0, 7 - elapsed // frame_duration)
                if self.door_frame_indices[i] <= 0:
                    self.door_anim_timers[i] = 0 
                    # ZAMKNIĘTO DRZWI -> USUŃ DUCHA
                    if hasattr(self, 'door_ghosts'):
                        self.door_ghosts[i] = None

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
        font_turns = pygame.font.SysFont("Arial", 18, bold=True) # <--- DODAJ TĘ LINIJKĘ
        font_hp  = pygame.font.SysFont("Times New Roman", 24, bold=True) # <--- DODAJ TĘ LINIJKĘ DLA ŻYCIA
        garrison = getattr(castle, 'garrison', [])

        for i, rect in enumerate(self.slot_rects):
            unit = garrison[i] if i < len(garrison) else None
            
            # Pobieramy ewentualnego ducha
            ghost = getattr(self, 'door_ghosts', [None]*12)[i]
            display_unit = unit if unit is not None else ghost

            if display_unit is not None:
                # ===============================================
                # 1. RYSOWANIE SYLWETKI JEDNOSTKI LUB DUCHA
                # ===============================================
                drawn = False
                raw_img = None
                
                u_name = getattr(display_unit, 'type_code', getattr(display_unit, 'type', 'Unknown'))
                if isinstance(u_name, dict):
                    u_name = u_name.get("unit_type", str(u_name))
                
                u_code = u_name 
                try:
                    from settings import NAME_TO_CODE, UNIT_NAMES
                    if u_name in NAME_TO_CODE: u_code = NAME_TO_CODE[u_name]
                    else:
                        for code, name in UNIT_NAMES.items():
                            if name == u_name:
                                u_code = code; break
                except: pass

                frame = (pygame.time.get_ticks() // 150) % 8
                path = f"assets/minimum/{u_code}1_I_S32/{u_code}1_I_S32_{frame}.png"
                
                if os.path.exists(path):
                    raw_img = pygame.image.load(path).convert_alpha()
                else:
                    frames_list = getattr(display_unit, 'walk_frames', getattr(display_unit, 'sprites', []))
                    if frames_list and len(frames_list) > 0:
                        raw_img = frames_list[frame % len(frames_list)]

                if raw_img and raw_img.get_size() == (32, 32):
                    test_col = raw_img.get_at((16, 16))
                    if test_col[3] == 0 or test_col == (255, 0, 255, 255) or test_col == (0, 0, 0, 255):
                        raw_img = None 

                if raw_img:
                    try:
                        alpha_img = pygame.Surface(raw_img.get_size(), pygame.SRCALPHA)
                        if raw_img.get_colorkey() is None: raw_img.set_colorkey((255, 0, 255))
                        alpha_img.blit(raw_img, (0, 0))
                        if hasattr(pygame.transform, 'grayscale'): gray_img = pygame.transform.grayscale(alpha_img)
                        else: gray_img = alpha_img.copy()
                            
                        POWIEKSZENIE = 1.67   
                        PRZESUNIECIE_X = -1
                        PRZESUNIECIE_Y = 2 
                        img_w, img_h = gray_img.get_size()
                        gray_img = pygame.transform.smoothscale(gray_img, (int(img_w * POWIEKSZENIE), int(img_h * POWIEKSZENIE)))
                        
                        rys_x = rect.centerx - gray_img.get_width() // 2 + PRZESUNIECIE_X
                        rys_y = rect.centery - gray_img.get_height() // 2 + PRZESUNIECIE_Y
                        screen.blit(gray_img, (rys_x, rys_y))
                        drawn = True
                    except: pass

                if not drawn:
                    label = str(u_name)[:4].upper()
                    txt = font.render(label, True, (255, 255, 255))
                    screen.blit(txt, txt.get_rect(centerx=rect.centerx, centery=rect.centery))
                    
                count = getattr(display_unit, 'count', 1)
                if count > 1:
                    c_txt = font_cnt.render(str(count), True, (255, 255, 0))
                    screen.blit(c_txt, (rect.right - c_txt.get_width() - 2, rect.bottom - c_txt.get_height() - 2))

                # ===============================================
                # 2. RYSOWANIE IKON 
                # ===============================================
                if unit is not None:
                    # Krzyżyk (Idealnie w prawym górnym rogu wewnątrz slota)
                    if unit in selected_units:
                        krzyz_x = rect.right - 20 # Wyrównane do prawej krawędzi
                        krzyz_y = rect.y + 0 
                        if hasattr(self, 'icon_cross') and self.icon_cross:
                            screen.blit(self.icon_cross, (krzyz_x, krzyz_y))
                        else:
                            pygame.draw.rect(screen, (255, 255, 0), rect.inflate(4, 4), 3)

                    # Serce
                    h_turns = getattr(unit, 'healing_turns', 0) 
                    if h_turns > 0:
                        serce_x, serce_y = rect.x - 5, rect.y + 5
                        if hasattr(self, 'icon_heart') and self.icon_heart:
                            screen.blit(self.icon_heart, (serce_x, serce_y))
                        # Używamy nowej, grubszej czcionki:
                        screen.blit(font_turns.render(str(h_turns), True, (255, 100, 100)), (serce_x + 24, serce_y))

                    # Miecze
                    t_turns = getattr(unit, 'training_turns', 0) 
                    if t_turns > 0:
                        miecze_x, miecze_y = rect.x - 0, rect.y + 0
                        if hasattr(self, 'icon_swords') and self.icon_swords:
                            screen.blit(self.icon_swords, (miecze_x, miecze_y))
                        # Używamy nowej, grubszej czcionki oraz czystej bieli:
                        screen.blit(font_turns.render(str(t_turns), True, (255, 255, 255)), (miecze_x + 24, miecze_y))

                # ===============================================
                # 2b. RYSOWANIE ŻYCIA (HP) NA DOLE RAMKI
                # ===============================================
                if display_unit is not None:
                    # Pobieramy HP jednostki (zmień 'hp' na nazwę swojej zmiennej, np. 'health' lub 'zycie')
                    # Jeśli gra nie znajdzie zmiennej, domyślnie wstawi 100.
                    hp_val = getattr(display_unit, 'hp', 100) 
                    
                    # Generujemy tekst i cień
                    hp_txt = font_hp.render(str(hp_val), True, (255, 255, 255)) # Śnieżnobiały
                    hp_shadow = font_hp.render(str(hp_val), True, (0, 0, 0))    # Czarny cień
                    
                    # Obliczamy pozycję na samym dole, wyśrodkowaną w ramce
                    hp_x = rect.centerx - hp_txt.get_width() // 2
                    hp_y = rect.bottom - hp_txt.get_height() - 2
                    
                    # Rysujemy cień (przesunięty o 2 piksele w dół i prawo)
                    screen.blit(hp_shadow, (hp_x + 2, hp_y + 2))
                    # Rysujemy właściwy tekst
                    screen.blit(hp_txt, (hp_x, hp_y))

            # ===============================================
            # 3. RYSOWANIE DRZWI (Teraz znikają całkowicie!)
            # ===============================================
            idx = self.door_frame_indices[i] 
            
            # Wymuszamy stan statyczny, gdy nie ma animacji
            if self.door_anim_timers[i] == 0:
                if display_unit is not None:
                    idx = 7 # Ktoś tu jest -> drzwi otwarte na oścież
                else:
                    idx = 0 # Pusto -> drzwi zamknięte na głucho
            
            # MAGIA: Rysujemy drzwi TYLKO wtedy, kiedy nie są w pełni otwarte (czyli idx jest mniejsze niż 7)
            if hasattr(self, 'door_frames') and self.door_frames:
                if idx != 7:
                    screen.blit(self.door_frames[idx], rect.topleft)
                             
        # 4. Tabelka statystyk (NOWE OKIENKO Z UI_COMPONENTS)
        if inspected_unit is not None:
            info_x = 353 # Zmień na inną wartość, żeby przesuwać lewo/prawo (np. 150)
            info_y = 461 # Zmień na inną wartość, żeby przesuwać góra/dół (np. 400)
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

        # ==============================================================
        # WYSWIETLANIE ZŁOTA W GARNIZONIE
        # ==============================================================
        # 1. Definiujemy czcionkę (możesz zmienić rozmiar z 24 na inny)
        font_gold = pygame.font.SysFont("Times New Roman", 24, bold=True)
        
        # 2. Pobieramy złoto z zamku
        gold_amount = getattr(castle, 'gold', 0)
        gold_txt = font_gold.render(str(gold_amount), True, (255, 215, 0))
        
        # 3. KOORDYNATY - Zmień te liczby, aby trafić w skrzynię na grafice!
        gold_x = 930  # Przesuwaj lewo/prawo
        gold_y = 80   # Przesuwaj góra/dół
        
        # 4. Rysowanie tekstu (odjęcie połowy szerokości ładnie go wyśrodkuje)
        screen.blit(gold_txt, (gold_x - gold_txt.get_width() // 2, gold_y))
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
        