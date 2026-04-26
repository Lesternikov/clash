import pygame
import os
from settings import UNIT_STATS, UNIT_NAMES

class RecruitmentManager:
    def __init__(self, world):
        self.world = world
        self.screen_res = (1026, 765)        
        # 1. Ładowanie tła
        try:
            self.bg = pygame.image.load(r"assets\DW_13_GFX.png").convert_alpha()
            self.bg = pygame.transform.scale(self.bg, self.screen_res)
        except Exception as e:
            print(f"Nie udało się załadować tła rekrutacji: {e}")
            self.bg = pygame.Surface(self.screen_res)
            self.bg.fill((50, 20, 20))

        # --- KONFIGURACJA POZYCJI ---
        self.layout = {
            "list_start": (45, 80),         
            "list_step": 32,                
            "scroll_up": pygame.Rect(320, 80, 50, 50),   
            "scroll_down": pygame.Rect(320, 160, 50, 50),
            
            "stats_box": (160, 310),        
            "cost_box": (60, 510),          
            
            "gold_chest": (512, 650),       
            
            "btn_1": pygame.Rect(80, 640, 140, 60),  # KUP PATENT
            "btn_2": pygame.Rect(260, 640, 140, 60), # INFO
            "btn_3": pygame.Rect(620, 640, 140, 60), # START PRODUKCJI
            
            # --- PRZYWRÓCONY PRZYCISK POWRÓT (Grafika z world.py) ---
            # 190x91 to oryginalny rozmiar z world.py, pozycja: (46, 685)
            "btn_back": pygame.Rect(46, 685, 190, 91), 

            "patents_start": (650, 80),     
            "patents_gap": (95, 125)        
        }

        # Zmienne stanu
        self.scroll = 0
        self.selected_unit_type = None
        self.selected_patent_index = None

        self.recruitment_unit_types = list(UNIT_STATS.keys())
        self.patent_rects = []
        self.unit_list_rects = []

        # Czcionki
        self.font_small = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_main = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_title = pygame.font.SysFont("Arial", 26, bold=True)

    def draw(self, screen):
        castle = self.world.selected_castle
        if not castle: return

        # 1. Rysujemy GŁÓWNE TŁO
        screen.blit(self.bg, (0, 0))
        
        # 2. Złoto w zamku (nad skrzynią)
        gold_txt = self.font_title.render(str(castle.gold), True, (255, 215, 0))
        screen.blit(gold_txt, (self.layout["gold_chest"][0] - gold_txt.get_width()//2, self.layout["gold_chest"][1])) 

        all_units = list(UNIT_STATS.keys())
        unit_types = [u for u in all_units if self.world.castle_has_patent(castle, u) or castle.is_patent_available(u)]
        self.recruitment_unit_types = unit_types

        # --- SEKCJA PATENTÓW (Prawa siatka - 3x4) ---
        self.patent_rects = []
        px, py = self.layout["patents_start"]
        gx, gy = self.layout["patents_gap"]
        
        for i in range(12):
            col = i % 3  
            row = i // 3 
            rect = pygame.Rect(px + col * gx, py + row * gy, 60, 80)
            self.patent_rects.append(rect) 
            
            if self.selected_patent_index == i:
                pygame.draw.rect(screen, (255, 255, 0), rect, 3)

            if i < len(castle.patents) and castle.patents[i] is not None:
                p = castle.patents[i]
                name = p["unit_type"] if isinstance(p, dict) else p
                txt = self.font_small.render(name[:6], True, (255, 255, 255))
                screen.blit(txt, (rect.x + 5, rect.y + 30))

        # --- SEKCJA LISTY JEDNOSTEK (Lewa strona) ---
        self.unit_list_rects = [] 
        lx, ly = self.layout["list_start"]
        step = self.layout["list_step"]
        center_index = 2 

        for i in range(5):
            scroll_idx = self.scroll + i
            rect = pygame.Rect(lx, ly + i * step, 240, step)
            self.unit_list_rects.append(rect) 
            
            if 0 <= scroll_idx < len(unit_types):
                unit_name = unit_types[scroll_idx]
                has_p = self.world.castle_has_patent(castle, unit_name)
                
                if i == center_index:
                    t_col = (255, 255, 0) 
                elif has_p:
                    t_col = (150, 150, 150) 
                else:
                    t_col = (255, 255, 255) 
                
                screen.blit(self.font_main.render(unit_name, True, t_col), (rect.x, rect.y + 4))

       # --- OBSZAR 9 i 8 (Statystyki i Koszty) ---
        idx_on_center = self.scroll + center_index
        if 0 <= idx_on_center < len(unit_types):
            unit_to_show = unit_types[idx_on_center]
            stats = UNIT_STATS.get(unit_to_show, {}) 
            
            if stats:
                # 1. Tworzymy symulowaną jednostkę ze słownika statystyk
                simulated_unit = {
                    'type_code': unit_to_show,
                    'hp': stats.get('hp', 0),
                    'max_hp': stats.get('hp', 0), # Rekrut to nówka sztuka
                    'attack': stats.get('attack', 0),
                    'defense': stats.get('defense', 0),
                    'moves': stats.get('moves', 0),
                    'morale': 50, # neutralne
                    'experience': 0
                }
                
                # 2. Rysujemy piękny panel graficzny z użyciem Twojego UnitInfoWindow z UI_components
                # Współrzędne (160, 260) możesz delikatnie przesuwać o kilka pikseli, żeby trafić idealnie w czarne pole
                if hasattr(self.world, 'unit_info_window'):
                    self.world.unit_info_window.draw(screen, 115, 300, simulated_unit, "COMBAT")
                
                # 3. Zachowujemy Twoje rysowanie kosztów na dole (Obszar 8)
                cx, cy = self.layout["cost_box"]
                screen.blit(self.font_main.render(f"{stats.get('patent_cost', 0)}", True, (255, 215, 0)), (cx + 50, cy))
                screen.blit(self.font_main.render(f"{stats.get('production_cost', 0)}", True, (255, 215, 0)), (cx + 200, cy))
                screen.blit(self.font_main.render(f"{stats.get('production_time', 0)}", True, (255, 255, 255)), (cx + 340, cy))

        # --- INFO O PRODUKCJI ---
        if castle.production_enabled and castle.production_unit_type:
            p_text = f"Produkcja: {castle.production_unit_type} ({castle.production_turns_left} tur)"
            p_color = (0, 255, 0)
        else:
            p_text = "Brak produkcji"
            p_color = (150, 150, 150)
        screen.blit(self.font_main.render(p_text, True, p_color), (self.layout["patents_start"][0], self.layout["patents_start"][1] + 450))

        # --- RYSOWANIE PRZYCISKÓW ---
        can_start = self.selected_patent_index is not None and self.selected_patent_index < len(castle.patents) and castle.patents[self.selected_patent_index] is not None
        
        self._draw_btn_text(screen, "KUP PATENT", self.layout["btn_1"])
        self._draw_btn_text(screen, "INFO", self.layout["btn_2"])
        self._draw_btn_text(screen, "START", self.layout["btn_3"], text_color=(0, 255, 0) if can_start else (100, 100, 100))
        
        # ==============================================================
        # PRZYCISK POWRÓT Z ORYGINALNĄ GRAFIKĄ I ANIMACJĄ (z world.py)
        # ==============================================================
        back_rect = self.layout["btn_back"]
        
        # Sprawdzamy czy timer powrotu jest aktywny i odpalamy obrazek wciśnięty
        if getattr(self.world, 'back_anim_timer', 0) > 0 and pygame.time.get_ticks() - self.world.back_anim_timer < 500:
            if hasattr(self.world, 'back_img_bldg_pressed'):
                screen.blit(self.world.back_img_bldg_pressed, back_rect.topleft)
        else:
            if hasattr(self.world, 'back_img_bldg_normal'):
                screen.blit(self.world.back_img_bldg_normal, back_rect.topleft)

    def _draw_btn_text(self, screen, text, rect, text_color=(255, 255, 255)):
        """Pomocnicza funkcja do centrowania tekstu niewidzialnych przycisków"""
        txt = self.font_title.render(text, True, text_color)
        screen.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))

    def handle_click(self, mx, my):
        castle = self.world.selected_castle
        if not castle: return

        unit_types = self.recruitment_unit_types

        # 1. Przycisk Powrót (Z GRAFIKĄ)
        if self.layout["btn_back"].collidepoint(mx, my):
            # Uruchamiamy animację z controls.py! (Zamiast po prostu zamykać ekran)
            self.world.back_destination = "garrison"
            self.world.back_anim_timer = pygame.time.get_ticks()
            return

        # 2. Przycisk 1: Kup Patent 
        if self.layout["btn_1"].collidepoint(mx, my):
            center_idx = self.scroll + 2
            if 0 <= center_idx < len(unit_types):
                u_name = unit_types[center_idx]
                if not self.world.castle_has_patent(castle, u_name):
                    castle.buy_patent(u_name)
            return

        # 3. Przycisk 3: Start Produkcji
        if self.layout["btn_3"].collidepoint(mx, my):
            if self.selected_patent_index is not None:
                p = castle.patents[self.selected_patent_index]
                u_name = p["unit_type"] if isinstance(p, dict) else p
                if u_name:
                    castle.start_production(u_name)
                    print(f"Uruchomiono produkcję: {u_name}")
            return

        # Kliknięcie w slot Patentu na siatce po prawej
        for i, rect in enumerate(self.patent_rects):
            if rect.collidepoint(mx, my):
                if i < len(castle.patents) and castle.patents[i]:
                    self.selected_patent_index = i
                    self.selected_unit_type = None 
                    
                    u_name = castle.patents[i]["unit_type"] if isinstance(castle.patents[i], dict) else castle.patents[i]
                    if u_name in unit_types:
                        target_idx = unit_types.index(u_name)
                        self.scroll = target_idx - 2 
                    return

        # Scroll (Guziki)
        if self.layout["scroll_up"].collidepoint(mx, my):
            self.scroll = max(-2, self.scroll - 1)
            return
        if self.layout["scroll_down"].collidepoint(mx, my):
            self.scroll = min(len(unit_types)-3, self.scroll + 1)
            return

        # Kliknięcie w listę jednostek po lewej
        for i, rect in enumerate(self.unit_list_rects):
            if rect.collidepoint(mx, my):
                clicked_unit_idx = self.scroll + i
                if 0 <= clicked_unit_idx < len(unit_types):
                    self.scroll = clicked_unit_idx - 2 
                    return

    def handle_scroll_wheel(self, event):
        castle = self.world.selected_castle
        if not castle: return

        available_units = [u for u in UNIT_STATS.keys() if 
                        self.world.castle_has_patent(castle, u) or 
                        castle.is_patent_available(u)]
        
        max_scroll = max(0, len(available_units) - 3)

        if event.button == 4: # GÓRA
            if self.scroll > -2:
                self.scroll -= 1
        elif event.button == 5: # DÓŁ
            if self.scroll < max_scroll:
                self.scroll += 1

    if __name__ == "__main__":
            import subprocess, sys, os
            main_path = os.path.join(os.path.dirname(__file__), "main.py")
            subprocess.run([sys.executable, main_path])