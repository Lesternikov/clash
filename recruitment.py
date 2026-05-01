import pygame
import os
from settings import UNIT_STATS, UNIT_NAMES, NAME_TO_CODE

class RecruitmentManager:
    def __init__(self, world):
        self.world = world
        self.screen_res = (1026, 765)        
        self.scale = 1.0  # Nasz mnożnik powiększenia

        # Funkcja pomocnicza do ładowania i skalowania
        def load_scaled(path):
            img = pygame.image.load(path).convert_alpha()
            w, h = img.get_size()
            # Używamy smoothscale do wygładzenia przy powiększeniu!
            return pygame.transform.smoothscale(img, (int(w * self.scale), int(h * self.scale)))
        
        # === SYSTEM GRAFICZNYCH PRZYCISKÓW ===
        self.custom_buttons = {}

        # ZWRÓĆ UWAGĘ NA TĘ LINIJKĘ: dodaliśmy 'w' i 'h' na końcu nawiasu!
        def add_btn(nazwa, plik, plik_p, x, y, w, h):
            img = pygame.transform.scale(pygame.image.load(plik).convert_alpha(), (w, h))
            img_p = pygame.transform.scale(pygame.image.load(plik_p).convert_alpha(), (w, h))
            self.custom_buttons[nazwa] = {
                "img": img,
                "img_p": img_p,
                "rect": pygame.Rect(x, y, w, h),
                "timer": 0
            }

        # Teraz funkcja jest gotowa przyjąć wszystkie 7 parametrów:
        # 1:nazwa, 2:plik, 3:plik_p, 4:X, 5:Y, 6:Szerokość, 7:Wysokość
        add_btn("19", "assets/przyciski/19.png", "assets/przyciski/20.png", 816, 678, 152, 83)
        add_btn("17", "assets/przyciski/17.png", "assets/przyciski/18.png", 722, 593, 152, 83)
        add_btn("15", "assets/przyciski/15.png", "assets/przyciski/16.png", 626, 678, 152, 83)
        add_btn("13", "assets/przyciski/13.png", "assets/przyciski/14.png", 250, 678, 152, 83)
        add_btn("11", "assets/przyciski/11.png", "assets/przyciski/12.png", 156, 593, 152, 83)

        # 1. Ładowanie tła
        try:
            self.bg = pygame.image.load(r"assets\DW_13_GFX.png").convert_alpha()
            self.bg = pygame.transform.scale(self.bg, self.screen_res)
        except Exception as e:
            print(f"Nie udało się załadować tła rekrutacji: {e}")
            self.bg = pygame.Surface(self.screen_res)
            self.bg.fill((50, 20, 20))
        self.icon_cross = load_scaled("assets/minimum/INFO_S32/INFO_S32_30.png")  # Krzyżyk (X)
        self.icon_hammer = load_scaled("assets/minimum/INFO_S32/INFO_S32_29.png") # Młotek
        self.icon_cross.set_colorkey((255, 255, 255))
        self.icon_hammer.set_colorkey((255, 255, 255))

        # --- KONFIGURACJA POZYCJI ---
        self.layout = {
            "list_start": (45, 80),         
            "list_step": 32,                
            "scroll_up": pygame.Rect(320, 80, 50, 50),   
            "scroll_down": pygame.Rect(320, 160, 50, 50),
            
            "stats_box": (160, 310),        
            "cost_box": (60, 510),          
            
            "gold_chest": (512, 676),       
            
            "btn_1": pygame.Rect(60, 600, 140, 60),  # KUP PATENT
            "btn_2": pygame.Rect(280, 600, 140, 60), # INFO
            "btn_3": pygame.Rect(600, 600, 140, 60), # START PRODUKCJI
            
            # --- PRZYWRÓCONY PRZYCISK POWRÓT (Grafika z world.py) ---
            # 190x91 to oryginalny rozmiar z world.py, pozycja: (46, 685)
            "btn_back": pygame.Rect(63, 678, 154, 83), 

            "patents_start": (650, 80),     
            "patents_gap": (76, 131)        
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
            col = i % 4 
            row = i // 4

            # 1. Definicja ramki klikania (Złota ramka)
            rect = pygame.Rect(px + col * gx + 30, py + row * gy - 40, 60, 120)
            self.patent_rects.append(rect) 
            
            # DEBUG: Rysowanie ramki
            pygame.draw.rect(screen, (255, 215, 0), rect, 1)

            if i < len(castle.patents) and castle.patents[i] is not None:
                p = castle.patents[i]
                name = p["unit_type"] if isinstance(p, dict) else p
                
                u_code = NAME_TO_CODE.get(name, name)
                frame_idx = (pygame.time.get_ticks() // 150) % 8
                path = f"assets/minimum/{u_code}1_I_S32/{u_code}1_I_S32_{frame_idx}.png"

                drawn = False
                
                # --- TUTAJ JEST JEDYNE RYSOWANIE LUDZIKA ---
                if os.path.exists(path):
                    try:
                        raw_img = pygame.image.load(path).convert_alpha()
                        
                        # Tworzymy wersję SZARĄ
                        gray_img = pygame.transform.grayscale(raw_img) 
                        
                        # SKALOWANIE: Dopasuj do złotej ramki (np. 60x100)
                        # Na Twoim screenie ramka jest wysoka, więc (55, 90) będzie OK
                        img_w, img_h = 52, 104
                        scaled_img = pygame.transform.scale(gray_img, (img_w, img_h))
                        
                        # POZYCJA: rect.x i rect.y to lewy górny róg ZŁOTEJ RAMKI.
                        # Centrujemy ludzika w ramce 60x120
                        img_x = rect.x + (rect.width - img_w) // 2
                        img_y = rect.y + 10 # 10 pikseli od góry ramki
                        
                        screen.blit(scaled_img, (img_x, img_y))
                        drawn = True
                    except:
                        pass

                # Fallback: jeśli nie znajdzie obrazka
                if not drawn:
                    txt = self.font_small.render(name[:6], True, (255, 255, 255))
                    screen.blit(txt, (rect.x + 5, rect.y + 30))

                # --- NOWOŚĆ: KRZYŻYK (Zamiast ramki zaznaczenia) ---
                if self.selected_patent_index == i:
                    # Krzyżyk na obrazku jednostki
                    cross_x = img_x + img_w - self.icon_cross.get_width() - 2
                    cross_y = img_y + 2
                    screen.blit(self.icon_cross, (cross_x, cross_y))

                # --- NAPRAWIONY MŁOTEK ---
                # Używamy właściwej nazwy zmiennej: production_unit_type
                if getattr(castle, 'production_enabled', False) and getattr(castle, 'production_unit_type', None) == name:
                    hammer_x = img_x + 2
                    hammer_y = img_y + 2
                    screen.blit(self.icon_hammer, (hammer_x, hammer_y))
                    
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
                simulated_unit = {
                    'type_code': unit_to_show,
                    'hp': stats.get('hp', 0),
                    'max_hp': stats.get('hp', 0), 
                    'attack': stats.get('attack', 0),
                    'defense': stats.get('defense', 0),
                    'moves': stats.get('moves', 0),
                    'morale': 50,
                    'experience': 0
                }
                
                if hasattr(self.world, 'unit_info_window'):
                    self.world.unit_info_window.draw(screen, 115, 300, simulated_unit, "COMBAT")
                
                cx, cy = self.layout["cost_box"]
                screen.blit(self.font_main.render(f"{stats.get('patent_cost', 0)}", True, (255, 215, 0)), (cx + 50, cy))
                screen.blit(self.font_main.render(f"{stats.get('production_cost', 0)}", True, (255, 215, 0)), (cx + 200, cy))
                screen.blit(self.font_main.render(f"{stats.get('production_time', 0)}", True, (255, 255, 255)), (cx + 340, cy))

        # --- INFO O PRODUKCJI ---
        if castle.production_enabled and castle.production_unit_type:
            p_text = f"{castle.production_unit_type} ({castle.production_turns_left} tur)"
            p_color = (0, 255, 0)
        else:
            p_text = "Brak produkcji"
            p_color = (150, 150, 150)
        screen.blit(self.font_main.render(p_text, True, p_color), (self.layout["patents_start"][0], self.layout["patents_start"][1] + 450))

        # Sprawdzamy, czy gracz ma zaznaczony jakiś konkretny, KUPIONY patent w prawej siatce
        has_valid_patent = (self.selected_patent_index is not None and 
                            self.selected_patent_index < len(castle.patents) and 
                            castle.patents[self.selected_patent_index] is not None)
        
        if has_valid_patent:
            # --- ZAZNACZONO KUPIONY PATENT ---
            p = castle.patents[self.selected_patent_index]
            selected_unit_name = p["unit_type"] if isinstance(p, dict) else p
            
            # 1. Zamiast KUP jest USUŃ
            self._draw_btn_text(screen, "USUŃ", self.layout["btn_1"], text_color=(255, 100, 100))
            
            # 2. INFO zostaje normalnie
            self._draw_btn_text(screen, "INFO", self.layout["btn_2"])
            
            # 3. Jeśli ten patent jest akurat produkowany -> WSTRZYMAJ, w przeciwnym razie -> START
            if getattr(castle, 'production_enabled', False) and getattr(castle, 'production_unit_type', None) == selected_unit_name:
                self._draw_btn_text(screen, "WSTRZYMAJ", self.layout["btn_3"], text_color=(255, 255, 0))
            else:
                self._draw_btn_text(screen, "START", self.layout["btn_3"], text_color=(0, 255, 0))
                
        else:
            # --- NIC NIE ZAZNACZONO LUB ZAZNACZONO PUSTY SLOT/LISTĘ PO LEWEJ ---
            self._draw_btn_text(screen, "KUP PATENT", self.layout["btn_1"])
            self._draw_btn_text(screen, "INFO", self.layout["btn_2"])
            self._draw_btn_text(screen, "START", self.layout["btn_3"], text_color=(100, 100, 100))
        
        # ==============================================================
        # PRZYCISK POWRÓT (Aktywny - styl garnizonu)
        # ==============================================================
        back_rect = self.layout["btn_back"]
        
        # Pobieramy grafikę garnizonu z obiektu świata
        img = self.world.back_img_garrison_pressed if getattr(self.world, 'back_anim_timer', 0) > 0 and \
            pygame.time.get_ticks() - self.world.back_anim_timer < 500 \
            else self.world.back_img_garrison_normal
            
        # Zabezpieczenie przed brakiem obrazka i płynne skalowanie
        if img:
            scaled_img = pygame.transform.smoothscale(img, (back_rect.width, back_rect.height))
            screen.blit(scaled_img, back_rect.topleft)

# --- RYSOWANIE WSZYSTKICH GRAFICZNYCH PRZYCISKÓW ---
        now = pygame.time.get_ticks()
        
        # Upewniamy się, że słownik z guzikami został stworzony w __init__
        if hasattr(self, 'custom_buttons'):
            for btn_name, btn_data in self.custom_buttons.items():
                
                # >>> TEST DETEKTYWISTYCZNY <<<
                print(f"Rysuję guzik: {btn_name}, rozmiar: {btn_data['img'].get_size()}")
                
                elapsed = now - btn_data["timer"]
                # Jeśli kliknięto go niedawno, rysuje wciśnięty (img_p)
                if btn_data["timer"] > 0 and elapsed < 400:
                    screen.blit(btn_data["img_p"], btn_data["rect"].topleft)
                else:
                    screen.blit(btn_data["img"], btn_data["rect"].topleft)

    def _draw_btn_text(self, screen, text, rect, text_color=(255, 255, 255)):
        """Pomocnicza funkcja do centrowania tekstu niewidzialnych przycisków"""
        txt = self.font_title.render(text, True, text_color)
        screen.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))

    def handle_click(self, mx, my):
        castle = self.world.selected_castle
        if not castle: return

        unit_types = self.recruitment_unit_types

        # Sprawdzamy stan: Czy gracz kliknął w kupiony patent na siatce po prawej?
        has_valid_patent = (self.selected_patent_index is not None and 
                            self.selected_patent_index < len(castle.patents) and 
                            castle.patents[self.selected_patent_index] is not None)

        # 1. Przycisk Powrót (Z GRAFIKĄ)
        if self.layout["btn_back"].collidepoint(mx, my):
            # Uruchamiamy animację z controls.py! (Zamiast po prostu zamykać ekran)
            self.world.back_destination = "garrison"
            self.world.back_anim_timer = pygame.time.get_ticks()
            return

        # 2. Przycisk 1: (KUP PATENT lub USUŃ PATENT)
        if self.layout["btn_1"].collidepoint(mx, my):
            if has_valid_patent:
                # --- AKCJA: USUŃ PATENT ---
                # Uwaga: Musisz upewnić się, że masz metodę np. castle.remove_patent(index)
                # Jeśli jej nie masz, to poniższy kod to ręczne usuwanie (podmień na list.pop lub przypisz None w zależności od mechaniki w Twoim pliku castle.py)
                try:
                    p_to_remove = castle.patents[self.selected_patent_index]
                    unit_name = p_to_remove["unit_type"] if isinstance(p_to_remove, dict) else p_to_remove
                    
                    # Prosta opcja usuwania: ucinamy element lub zmieniamy na None
                    if isinstance(castle.patents, list):
                        castle.patents[self.selected_patent_index] = None
                        # Opcjonalnie: castle.patents.remove(p_to_remove) 
                    
                    # Jeśli usuwamy patent, który właśnie jest produkowany - warto wstrzymać produkcję!
                    if getattr(castle, 'production_unit_type', None) == unit_name:
                        castle.production_enabled = False
                        castle.production_unit_type = None
                        
                    print(f"Usunięto patent: {unit_name}")
                    self.selected_patent_index = None # Odznaczamy po usunięciu
                except Exception as e:
                    print(f"Błąd przy usuwaniu patentu: {e}")
            else:
                # --- AKCJA: KUP PATENT ---
                center_idx = self.scroll + 2
                if 0 <= center_idx < len(unit_types):
                    u_name = unit_types[center_idx]
                    if not self.world.castle_has_patent(castle, u_name):
                        castle.buy_patent(u_name)
            return

        # 3. Przycisk 3: (START PRODUKCJI lub WSTRZYMAJ)
        if self.layout["btn_3"].collidepoint(mx, my):
            if has_valid_patent:
                p = castle.patents[self.selected_patent_index]
                u_name = p["unit_type"] if isinstance(p, dict) else p
                
                if u_name:
                    # Sprawdzamy czy ta konkretna jednostka jest teraz w produkcji
                    is_currently_producing = getattr(castle, 'production_enabled', False) and getattr(castle, 'production_unit_type', None) == u_name
                    
                    if is_currently_producing:
                        # --- AKCJA: WSTRZYMAJ ---
                        castle.production_enabled = False
                        print(f"Wstrzymano produkcję: {u_name}")
                    else:
                        # --- AKCJA: START ---
                        castle.start_production(u_name)
                        print(f"Uruchomiono produkcję: {u_name}")
            return

        # Kliknięcie w slot Patentu na siatce po prawej
        for i, rect in enumerate(self.patent_rects):
            if rect.collidepoint(mx, my):
                if i < len(castle.patents) and castle.patents[i]:
                    # Kliknięto w ZAJĘTY slot - zaznaczamy
                    self.selected_patent_index = i
                    self.selected_unit_type = None 
                    
                    u_name = castle.patents[i]["unit_type"] if isinstance(castle.patents[i], dict) else castle.patents[i]
                    if u_name in unit_types:
                        target_idx = unit_types.index(u_name)
                        self.scroll = target_idx - 2 
                else:
                    # Kliknięto w PUSTY slot - ODWZNAKOWUJEMY (dzięki temu zniknie przycisk "Usuń" i wróci "Kup Patent")
                    self.selected_patent_index = None
                return

        # Scroll (Guziki)
        if self.layout["scroll_up"].collidepoint(mx, my):
            self.scroll = max(-2, self.scroll - 1)
            # Przy przewijaniu zdejmujemy zaznaczenie z patentu po prawej,
            # żeby umożliwić swobodne Kupowanie tego co jest po lewej!
            self.selected_patent_index = None
            return
            
        if self.layout["scroll_down"].collidepoint(mx, my):
            self.scroll = min(len(unit_types)-3, self.scroll + 1)
            self.selected_patent_index = None # J.w.
            return

        # Kliknięcie w listę jednostek po lewej
        for i, rect in enumerate(self.unit_list_rects):
            if rect.collidepoint(mx, my):
                clicked_unit_idx = self.scroll + i
                if 0 <= clicked_unit_idx < len(unit_types):
                    self.scroll = clicked_unit_idx - 2 
                    # Wybrano jednostkę z listy - musimy ODZNACZYĆ panel po prawej, 
                    # żeby przyciski pokazały "Kup Patent"
                    self.selected_patent_index = None
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