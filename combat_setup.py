import pygame
import os

class CombatSetupMenu:
    def __init__(self, screen_width, screen_height):
        self.w = screen_width
        self.h = screen_height
        self.assets = {}
        
        # =========================================================
        # 🟢 GŁÓWNY PANEL STEROWANIA SKALĄ I POZYCJĄ
        # =========================================================
        # 1. POWIĘKSZENIE TŁA (Tylko pergamin i odstępy między ramkami)
        self.GŁÓWNA_SKALA = 1.60 
        
        # 2. PRZESUNIĘCIE CAŁEGO OKNA (Jeśli nie chcesz, żeby było na środku ekranu)
        self.przesunięcie_x = 0  
        self.przesunięcie_y = 0  
        
        # 3. NIEZALEŻNE SKALE (Teraz nie wpływają na siebie nawzajem!)
        self.SKALA_TEKSTU = 1.0      # Wielkość czcionki (imiona graczy)
        self.SKALA_PRZYCISKÓW = 1.6 # Wielkość przycisków V i AUTO
        self.SKALA_JEDNOSTEK = 1.4   # Wielkość ludzików w ramkach
        # =========================================================

        # Skaner i ładowanie grafik (Używają swoich własnych suwaków!)
        self.bg = self._load_and_scale(["assets/minimum/AUTO_S32/AUTO_S32_0.png"], self.GŁÓWNA_SKALA)
        self.btn_v = self._load_and_scale(["assets/minimum/AUTO_S32/AUTO_S32_1.png"], self.SKALA_PRZYCISKÓW)
        self.btn_auto = self._load_and_scale(["assets/minimum/AUTO_S32/AUTO_S32_2.png"], self.SKALA_PRZYCISKÓW)
        
        # Inicjalizacja czcionek (Oparta TYLKO na SKALI_TEKSTU)
        f_size = int(22 * self.SKALA_TEKSTU)
        self.font_names = pygame.font.SysFont("Arial", f_size, bold=True)
        
        # =========================================================
        # 🔵 PANEL STEROWANIA POZYCJAMI WEWNĄTRZ OKNA (Względem tła)
        # =========================================================
        self.orig_bg_w = 640  
        self.orig_bg_h = 400  
        
        # PRZYCISKI V i AUTO 
        self.orig_offset_btns_y = 94
        self.orig_v_x_from_center = -45  
        self.orig_auto_x_from_center = 35 
        
        # IMIONA GRACZY (Te X i Y to teraz ŚRODEK brązowych okienek na tekst)
        self.orig_offset_name_att_center_x = 105 # Środek lewego okienka
        self.orig_offset_name_def_center_x = 455 # Środek prawego okienka
        self.orig_offset_names_center_y = 92     # Wysokość (środek okienka)
        
        # SLOTY JEDNOSTEK (Siatka 3x4)
        self.orig_grid_att_start_x = 10  
        self.orig_grid_def_start_x = 363  
        self.orig_grid_start_y = 113      
        self.orig_grid_step_x = 48        
        self.orig_grid_step_y = 75        
        # =========================================================

        # Automatyczne wyliczanie skalowanych wymiarów i pozycji tła
        self.bg_w = self.bg.get_width() if self.bg else int(self.orig_bg_w * self.GŁÓWNA_SKALA)
        self.bg_h = self.bg.get_height() if self.bg else int(self.orig_bg_h * self.GŁÓWNA_SKALA)
        self.bg_x = ((self.w - self.bg_w) // 2) + self.przesunięcie_x
        self.bg_y = ((self.h - self.bg_h) // 2) + self.przesunięcie_y
        self.bg_center_x = self.bg_x + self.bg_w // 2

        # Automatyczne wyliczanie kolizji dla przycisków
        self.rect_v = pygame.Rect(0, 0, 0, 0)
        self.rect_auto = pygame.Rect(0, 0, 0, 0)
        
        scaled_btns_y = self.bg_y + int(self.orig_offset_btns_y * self.GŁÓWNA_SKALA)
        
        if self.btn_v:
            bw, bh = self.btn_v.get_width(), self.btn_v.get_height()
            scaled_v_x = self.bg_center_x + int(self.orig_v_x_from_center * self.GŁÓWNA_SKALA)
            self.rect_v = pygame.Rect(scaled_v_x - bw // 2, scaled_btns_y - bh // 2, bw, bh)
            
        if self.btn_auto:
            bw, bh = self.btn_auto.get_width(), self.btn_auto.get_height()
            scaled_auto_x = self.bg_center_x + int(self.orig_auto_x_from_center * self.GŁÓWNA_SKALA)
            self.rect_auto = pygame.Rect(scaled_auto_x - bw // 2, scaled_btns_y - bh // 2, bw, bh)

    def _load_and_scale(self, paths, scale):
        for p in paths:
            if os.path.exists(p):
                try:
                    img = pygame.image.load(p).convert_alpha()
                    if scale != 1.0:
                        new_w = int(img.get_width() * scale)
                        new_h = int(img.get_height() * scale)
                        img = pygame.transform.smoothscale(img, (new_w, new_h))
                    return img
                except: pass
        return None

    def draw(self, screen, world, gfx):
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        
        if self.bg: screen.blit(self.bg, (self.bg_x, self.bg_y))
        
        attacker = getattr(world, 'combat_attacker', None)
        defender = getattr(world, 'combat_defender', None)
        if not attacker or not defender: return
        
        # --- Rysowanie idealnie wyśrodkowanych imion ---
        scaled_names_center_y = self.bg_y + int(self.orig_offset_names_center_y * self.GŁÓWNA_SKALA)
        txt_color = (255, 230, 180)
        
        att_name = attacker.owner.name if attacker.owner else "Nieznany"
        def_name = defender.owner.name if defender.owner else "Nieznany"
        
        txt_att = self.font_names.render(att_name, True, txt_color)
        txt_def = self.font_names.render(def_name, True, txt_color)
        
        # Obliczanie centralnej pozycji na ekranie
        pos_att_x = self.bg_x + int(self.orig_offset_name_att_center_x * self.GŁÓWNA_SKALA)
        pos_def_x = self.bg_x + int(self.orig_offset_name_def_center_x * self.GŁÓWNA_SKALA)
        
        # blitujemy za pomocą parametru `center=...` dzięki czemu tekst rozchodzi się na boki!
        screen.blit(txt_att, txt_att.get_rect(center=(pos_att_x, scaled_names_center_y)))
        screen.blit(txt_def, txt_def.get_rect(center=(pos_def_x, scaled_names_center_y)))
        
        # --- Rysowanie Armii ---
        armia_att = [attacker] + [u for u in getattr(attacker, 'garrison', []) if u is not None]
        armia_def = [defender] + [u for u in getattr(defender, 'garrison', []) if u is not None]
        
       # ---> ZMIANA LOGIKI SIATKI Z 3 KOLUMN NA 4 KOLUMNY! <---
        for i, unit in enumerate(armia_att):
            if i >= 12: break 
            col, row = i % 4, i // 4 # TERAZ ZAPEŁNIA DO 4 PORTRETÓW ZANIM ZEJJDZIE NIŻEJ
            x = self.bg_x + int((self.orig_grid_att_start_x + (col * self.orig_grid_step_x)) * self.GŁÓWNA_SKALA)
            y = self.bg_y + int((self.orig_grid_start_y + (row * self.orig_grid_step_y)) * self.GŁÓWNA_SKALA)
            self._draw_unit_in_slot(screen, unit, x, y)
            
        for i, unit in enumerate(armia_def):
            if i >= 12: break
            col, row = i % 4, i // 4 
            x = self.bg_x + int((self.orig_grid_def_start_x + (col * self.orig_grid_step_x)) * self.GŁÓWNA_SKALA)
            y = self.bg_y + int((self.orig_grid_start_y + (row * self.orig_grid_step_y)) * self.GŁÓWNA_SKALA)
            self._draw_unit_in_slot(screen, unit, x, y)
            
        mx, my = pygame.mouse.get_pos()
        if self.btn_v:
            screen.blit(self.btn_v, self.rect_v.topleft)
            if self.rect_v.collidepoint(mx, my):
                c_size = int(28 * self.SKALA_PRZYCISKÓW) 
                pygame.draw.circle(screen, (255, 215, 0), self.rect_v.center, c_size, 2)
            
        if self.btn_auto:
            screen.blit(self.btn_auto, self.rect_auto.topleft)
            if self.rect_auto.collidepoint(mx, my):
                c_size = int(28 * self.SKALA_PRZYCISKÓW)
                pygame.draw.circle(screen, (255, 215, 0), self.rect_auto.center, c_size, 2)

    def _draw_unit_in_slot(self, screen, unit, x, y):
        if not unit: return
        
        if hasattr(unit, 'walk_frames') and unit.walk_frames:
            img = unit.walk_frames[0]
        elif hasattr(unit, 'sprites') and unit.sprites:
            img = unit.sprites[0]
        else:
            img = pygame.Surface((32, 32))
            img.fill((100, 100, 100))
            
        # Skalujemy jednostkę absolutnie niezależnie!
        u_scale = self.SKALA_JEDNOSTEK
        if u_scale != 1.0:
            new_w = int(img.get_width() * u_scale)
            new_h = int(img.get_height() * u_scale)
            img = pygame.transform.smoothscale(img, (new_w, new_h))
            
        # Wyśrodkowanie ludzika w slocie
        s_w, s_h = int(48 * self.GŁÓWNA_SKALA), int(60 * self.GŁÓWNA_SKALA)
        img_x = x + (s_w - img.get_width()) // 2
        img_y = y + (s_h - img.get_height()) // 2
        screen.blit(img, (img_x, img_y))

    def handle_click(self, mx, my, world):
        if self.rect_v.collidepoint(mx, my):
            print("Przechodzę do walki taktycznej!")
            # Inicjalizujemy arenę bitewną!
            from combat_tactical import TacticalCombat
            world.tactical_combat = TacticalCombat(world, world.combat_attacker, world.combat_defender)
            world.screen = "combat_tactical" # Przełączamy ekran główny gry
            
        elif self.rect_auto.collidepoint(mx, my):
            print("Rozpoczynam szybką walkę AUTO!")
            self.resolve_combat(world)
            
    def resolve_combat(self, world):
        attacker = world.combat_attacker
        defender = world.combat_defender
        from walka_auto import resolve_auto_combat
        
        attacker_survived = resolve_auto_combat(attacker, defender, world)
        
        if attacker_survived:
            attacker.x, attacker.y = world.combat_nx, world.combat_ny
            attacker.move_points -= world.combat_cost
            world.check_unit_castle_entry(attacker)
        elif world.selected_unit == attacker:
            world.selected_unit = None
            
        world.combat_attacker = None
        world.combat_defender = None
        world.screen = "map"

if __name__ == "__main__":
    import subprocess, sys, os
    main_path = os.path.join(os.path.dirname(__file__), "main.py")
    subprocess.run([sys.executable, main_path])