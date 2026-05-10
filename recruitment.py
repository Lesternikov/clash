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
        
        add_btn("STOP",  "assets/przyciski/19.png", "assets/przyciski/20.png", 816, 678, 152, 83)
        add_btn("USUN",  "assets/przyciski/17.png", "assets/przyciski/18.png", 722, 593, 152, 83)
        add_btn("START", "assets/przyciski/15.png", "assets/przyciski/16.png", 626, 678, 152, 83)
        add_btn("KUP",   "assets/przyciski/13.png", "assets/przyciski/14.png", 250, 678, 152, 83)
        add_btn("INFO",  "assets/przyciski/11.png", "assets/przyciski/12.png", 156, 593, 152, 83)
        add_btn("UP",   "assets/przyciski/23.png",   "assets/przyciski/24.png", 499, 39, 50, 83)
        add_btn("DOWN", "assets/przyciski/21.png", "assets/przyciski/22.png", 499, 125, 50, 83)
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
            "list_start": (75, 56),         
            "list_step": 27,                
            "scroll_up": pygame.Rect(320, 80, 50, 50),   
            "scroll_down": pygame.Rect(320, 160, 50, 50),
            
            "stats_box": (10, 310),        
            "cost_box": (122, 554),          
            
            "gold_chest": (512, 676),       
            
            "btn_1": pygame.Rect(60, 600, 140, 60),  # KUP PATENT
            "btn_2": pygame.Rect(280, 600, 140, 60), # INFO
            "btn_3": pygame.Rect(600, 600, 140, 60), # START PRODUKCJI
            "btn_4": pygame.Rect(60, 60, 140, 60),
            "btn_5": pygame.Rect(10, 60, 140, 60),
            "btn_6": pygame.Rect(60, 10, 140, 60),
            # --- PRZYWRÓCONY PRZYCISK POWRÓT (Grafika z world.py) ---
            # 190x91 to oryginalny rozmiar z world.py, pozycja: (46, 685)
            "btn_back": pygame.Rect(63, 678, 154, 83), 

            "patents_start": (650, 80),     
            "patents_gap": (76, 131)        
        }

        # Zmienne stanu
        self.scroll = -2
        self.selected_unit_type = None
        self.selected_patent_index = None
        # --- DODAJ TĘ JEDNĄ LINIJKĘ ---
        self.door_animations = {}
        self.recruitment_unit_types = list(UNIT_STATS.keys())
        self.patent_rects = []
        self.unit_list_rects = []

        # Czcionki
        self.font_small = pygame.font.SysFont("Arial", 16, bold=True) # nie wiem od czego to
        self.font_main = pygame.font.SysFont("Arial", 20, bold=True) #lista jednostek
        self.font_title = pygame.font.SysFont("Arial", 26, bold=True) #złoto

        # --- DRZWICZKI DLA PUSTYCH PATENTÓW (Osobne pliki KEEP) ---
        self.door_frames = []
        try:
            # Lista Twoich plików - od zamkniętych (KEEP) do całkowicie otwartych (KEEP7)
            pliki_drzwi = ["KEEP.png", "KEEP1.png", "KEEP2.png", "KEEP3.png", 
                           "KEEP4.png", "KEEP5.png", "KEEP6.png", "KEEP7.png"]
            
            for nazwa in pliki_drzwi:
                # Zakładam, że są w folderze assets/
                sciezka = f"assets/{nazwa}"
                if os.path.exists(sciezka):
                    klatka = pygame.image.load(sciezka).convert_alpha()
                    # Zauważyłem, że zmieniłeś wymiary ramki na 56x106, więc skalujemy idealnie do nich!
                    klatka = pygame.transform.smoothscale(klatka, (56, 106))
                    self.door_frames.append(klatka)
                else:
                    print(f"Brakuje pliku drzwiczek: {sciezka}")
        except Exception as e:
            print(f"Błąd przy drzwiczkach: {e}")

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

            rect = pygame.Rect(px + col * gx + 32, py + row * gy - 32, 56, 106)
            self.patent_rects.append(rect) 
            
            # ==========================================================
            # ETAP 1: OBLICZAMY STAN ANIMACJI I SZUKAMY "DUCHÓW"
            # ==========================================================
            anim = self.door_animations.get(i)
            is_opening = anim and anim.get("type") == "open"
            is_closing = anim and anim.get("type") == "close"
            current_frame_idx = 0
            
            if anim:
                elapsed = pygame.time.get_ticks() - anim.get("timer", 0)
                frame_progress = min(7, int((elapsed / 1000.0) * 8))
                
                if is_opening: current_frame_idx = frame_progress 
                elif is_closing: current_frame_idx = 7 - frame_progress
                
                if elapsed >= 1000:
                    del self.door_animations[i]
                    anim = None
                    is_opening = False
                    is_closing = False

            has_patent = i < len(castle.patents) and castle.patents[i] is not None
            ghost_unit_name = anim.get("ghost_name") if is_closing else None

            # ==========================================================
            # ETAP 2: RYSOWANIE LUDZIKA LUB JEGO DUCHA
            # ==========================================================
            # Jeśli w zamku jest ludzik, ALBO drzwiczki właśnie zamykają ducha:
            if has_patent or ghost_unit_name:
                
                # Zabezpieczenie: skąd bierzemy nazwę do rysowania?
                if has_patent:
                    p = castle.patents[i]
                    name = p["unit_type"] if isinstance(p, dict) else p
                else:
                    name = ghost_unit_name
                
                u_code = NAME_TO_CODE.get(name, name)
                frame_idx = (pygame.time.get_ticks() // 150) % 8
                path = f"assets/minimum/{u_code}1_I_S32/{u_code}1_I_S32_{frame_idx}.png"
                drawn = False
                if os.path.exists(path):
                    try:
                        raw_img = pygame.image.load(path).convert_alpha()
                        gray_img = pygame.transform.grayscale(raw_img) 
                        img_w, img_h = 54, 106
                        scaled_img = pygame.transform.scale(gray_img, (img_w, img_h))
                        
                        img_x = rect.x + (rect.width - img_w) // 2
                        img_y = rect.y
                        
                        screen.blit(scaled_img, (img_x, img_y))
                        drawn = True
                    except: pass

                if not drawn:
                    txt = self.font_small.render(name[:6], True, (255, 255, 255))
                    screen.blit(txt, (rect.x + 5, rect.y + 30))

                if self.selected_patent_index == i:
                    cross_x = img_x + img_w - self.icon_cross.get_width() - 2
                    cross_y = img_y + 2
                    screen.blit(self.icon_cross, (cross_x, cross_y))

                if getattr(castle, 'production_enabled', False) and getattr(castle, 'production_unit_type', None) == name:
                    hammer_x = img_x + 2
                    hammer_y = img_y + 2
                    screen.blit(self.icon_hammer, (hammer_x, hammer_y))

            # ==========================================================
            # ETAP 3: RYSOWANIE DRZWICZEK (Nakładane na wierzch)
            # ==========================================================
            if hasattr(self, 'door_frames') and len(self.door_frames) > 0:
                if is_opening or is_closing:
                    # Trwa animacja - rysujemy odpowiednią klatkę w ruchu
                    screen.blit(self.door_frames[current_frame_idx], (rect.x, rect.y))
                elif not has_patent:
                    # Nie ma patentu, nie ma animacji - drzwi są twardo zamknięte (klatka 0)
                    screen.blit(self.door_frames[0], (rect.x, rect.y))

        # --- SEKCJA LISTY JEDNOSTEK (Lewa strona) ---
        self.unit_list_rects = [] 
        lx, ly = self.layout["list_start"]
        step = self.layout["list_step"]
        center_index = 2 

        for i in range(5):
            scroll_idx = self.scroll + i
            rect = pygame.Rect(lx, ly + i * step, 400, step)
            self.unit_list_rects.append(rect) 
            
            if 0 <= scroll_idx < len(unit_types):
                unit_name = unit_types[scroll_idx]
                has_p = self.world.castle_has_patent(castle, unit_name)
                
                # --- TUTAJ PRZYWRACAMY TWOJE KLASYCZNE KOLORY ---
                if i == center_index:
                    t_col = (255, 255, 255) # Zaznaczony na środku -> Śnieżnobiały
                elif has_p:
                    t_col = (100, 100, 100) # Wygaszony (już kupiony) -> Ciemnoszary
                else:
                    t_col = (180, 180, 180) # Dostępny do kupienia -> Zwykły szary
                
                screen.blit(self.font_main.render(unit_name, True, t_col), (rect.x, rect.y + 4))

        # --- OBSZAR 9 i 8 (Statystyki i Koszty) ---
        unit_to_show = None
        
        # 1. Sprawdzamy, czy gracz ma zaznaczony jakiś wykupiony patent po prawej
        if self.selected_patent_index is not None and self.selected_patent_index < len(castle.patents):
            p = castle.patents[self.selected_patent_index]
            if p is not None:
                unit_to_show = p["unit_type"] if isinstance(p, dict) else p

        # 2. Jeśli nie ma zaznaczonego patentu, bierzemy jednostkę ze środka lewej listy
        if not unit_to_show:
            center_index = 2
            idx_on_center = self.scroll + center_index
            if 0 <= idx_on_center < len(unit_types):
                unit_to_show = unit_types[idx_on_center]

        # 3. Wyświetlanie statystyk dla wybranej jednostki
        if unit_to_show:
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
                screen.blit(self.font_main.render(f"{stats.get('production_cost', 0)}", True, (255, 215, 0)), (cx + 215, cy))
                screen.blit(self.font_main.render(f"{stats.get('production_time', 0)}", True, (255, 255, 255)), (cx + 370, cy))

        # --- INFO O PRODUKCJI ---
        if castle.production_enabled and castle.production_unit_type:
            turns = getattr(castle, 'production_turns_left', 1)
            
            if turns == 1: tekst_tury = "POZOSTAŁA 1 TURA"
            else:
                resztka = turns % 10
                if 2 <= resztka <= 4 and not (12 <= turns % 100 <= 14): tekst_tury = f"POZOSTAŁY {turns} TURY"
                else: tekst_tury = f"POZOSTAŁO {turns} TUR"
                    
            linie_tekstu = ["DO UKOŃCZENIA", "PRODUKCJI", tekst_tury]
            
            # =======================================================
            # ZADANIA 1, 2, 3: REGULACJA POZYCJI I WYGLĄDU
            # =======================================================
            # 1. Pozycja TŁA (brązowego prostokąta)
            ramka_x = self.layout["patents_start"][0] + 141 # Zwiększ, żeby przesunąć w PRAWO
            ramka_y = self.layout["patents_start"][1] + 380 # Zwiększ, żeby przesunąć w DÓŁ
            
            # 2. Pozycja TEKSTU względem tła
            tekst_offset_x = 1 # Ujemne wartości przesuwają tekst w LEWO
            tekst_offset_y = 18  # Dodatnie wartości przesuwają tekst w DÓŁ
            
            # 3. Wygląd napisu
            kolor_tekstu = (210, 220, 230) # Delikatny, srebrzysty kolor
            kolor_cienia = (10, 10, 10)    # Ciemny cień
            # =======================================================
            
            # Rysowanie tła (jeśli istnieje)
            try:
                bg_path = "assets/ramka_produkcji.png"
                if os.path.exists(bg_path):
                    bg_panel = pygame.image.load(bg_path).convert_alpha()
                    screen.blit(bg_panel, (ramka_x - bg_panel.get_width()//2, ramka_y))
            except Exception:
                pass 
            
            font_info = pygame.font.SysFont("Times New Roman", 18, bold=True)
            odstep_y = 22 # Odstęp między linijkami tekstu
            
            # Środek tekstu po dodaniu Twojego offsetu
            srodek_tekstu_x = ramka_x + tekst_offset_x
            start_y_tekstu = ramka_y + tekst_offset_y
            
            for i, linia in enumerate(linie_tekstu):
                txt_shadow = font_info.render(linia, True, kolor_cienia)
                txt_main = font_info.render(linia, True, kolor_tekstu)
                
                txt_x = srodek_tekstu_x - txt_main.get_width() // 2
                txt_y = start_y_tekstu + i * odstep_y
                
                # Zależnie od tego, jak gruby ma być cień, możesz regulować to (txt_x + 2, txt_y + 2)
                screen.blit(txt_shadow, (txt_x + 2, txt_y + 2))
                screen.blit(txt_main, (txt_x, txt_y))
        
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
            self.selected_patent_index = None # Resetuje krzyżyk na obecnym ekranie
            self.world.back_destination = "garrison"
            self.world.back_anim_timer = pygame.time.get_ticks()
            return
        # ==========================================
        # 1. KUP PATENT
        # ==========================================
        if "KUP" in self.custom_buttons and self.custom_buttons["KUP"]["rect"].collidepoint(mx, my):
            self.custom_buttons["KUP"]["timer"] = pygame.time.get_ticks()
            
            if not has_valid_patent: 
                center_idx = self.scroll + 2
                if 0 <= center_idx < len(unit_types):
                    u_name = unit_types[center_idx]
                    if not self.world.castle_has_patent(castle, u_name):
                        
                        # --- TO JEST TA MAGIA: Szukamy miejsca PRZED kupnem! ---
                        target_idx = -1
                        for idx in range(12):
                            if idx >= len(castle.patents) or castle.patents[idx] is None:
                                target_idx = idx
                                break
                        
                        if target_idx != -1:
                            self.door_animations[target_idx] = {"type": "open", "timer": pygame.time.get_ticks()}
                        # -------------------------------------------------------
                            
                        castle.buy_patent(u_name)
                        print(f"Kupiono patent: {u_name}")
            return

       # ==========================================
        # 2. USUŃ PATENT
        # ==========================================
        if "USUN" in self.custom_buttons and self.custom_buttons["USUN"]["rect"].collidepoint(mx, my):
            self.custom_buttons["USUN"]["timer"] = pygame.time.get_ticks()
            
            if has_valid_patent:
                # 1. Zapisujemy nazwę wojownika ZANIM go skasujemy z listy
                p_to_remove = castle.patents[self.selected_patent_index]
                unit_name = p_to_remove["unit_type"] if isinstance(p_to_remove, dict) else p_to_remove
                
                # 2. Wrzucamy go do pamięci drzwi jako "ducha"
                self.door_animations[self.selected_patent_index] = {
                    "type": "close", 
                    "timer": pygame.time.get_ticks(),
                    "ghost_name": unit_name  # <--- MAGIA
                }
                
                # 3. DOPIERO TERAZ fizycznie usuwamy go z koszar
                if isinstance(castle.patents, list):
                    castle.patents[self.selected_patent_index] = None
                
                if getattr(castle, 'production_unit_type', None) == unit_name:
                    castle.production_enabled = False
                    castle.production_unit_type = None
                    
                self.selected_patent_index = None # Odznaczamy, żeby zamknąć menu
            return
        # ==========================================
        # 3. START PRODUKCJI
        # ==========================================
        if "START" in self.custom_buttons and self.custom_buttons["START"]["rect"].collidepoint(mx, my):
            self.custom_buttons["START"]["timer"] = pygame.time.get_ticks()
            
            if has_valid_patent:
                p = castle.patents[self.selected_patent_index]
                u_name = p["unit_type"] if isinstance(p, dict) else p
                if u_name:
                    castle.start_production(u_name)
                    print(f"Uruchomiono produkcję: {u_name}")
            return

        # ==========================================
        # 4. WSTRZYMAJ PRODUKCJĘ
        # ==========================================
        if "STOP" in self.custom_buttons and self.custom_buttons["STOP"]["rect"].collidepoint(mx, my):
            self.custom_buttons["STOP"]["timer"] = pygame.time.get_ticks()
            
            if has_valid_patent:
                p = castle.patents[self.selected_patent_index]
                u_name = p["unit_type"] if isinstance(p, dict) else p
                
                if u_name:
                    is_currently_producing = getattr(castle, 'production_enabled', False) and getattr(castle, 'production_unit_type', None) == u_name
                    if is_currently_producing:
                        castle.production_enabled = False
                        print(f"Wstrzymano produkcję: {u_name}")
            return

        # ==========================================
        # 5. INFO
        # ==========================================
        if "INFO" in self.custom_buttons and self.custom_buttons["INFO"]["rect"].collidepoint(mx, my):
            self.custom_buttons["INFO"]["timer"] = pygame.time.get_ticks()
            
            u_name = None
            if has_valid_patent:
                p = castle.patents[self.selected_patent_index]
                u_name = p["unit_type"] if isinstance(p, dict) else p
            else:
                center_idx = self.scroll + 2
                if 0 <= center_idx < len(unit_types):
                    u_name = unit_types[center_idx]

            if u_name:
                from settings import UNIT_STATS # Upewniamy się, że mamy dostęp do statystyk
                stats = UNIT_STATS.get(u_name, {})
                
                # 1. Wyciągamy historyczny opis z pliku settings
                # Jeśli jakaś jednostka nie ma jeszcze opisu, dajemy tekst zastępczy
                surowy_opis = stats.get("description", f"{u_name}\n\nBrak opisu historycznego.")
                
                # 2. Czyścimy tekst ze spacji (żeby ładnie i równo wyglądał w grze)
                czysty_opis = "\n".join([linia.strip() for linia in surowy_opis.split("\n") if linia.strip() != ""])
                
                # 3. Wrzucamy gotowy opis do świata gry!
                self.world.unit_info_text = czysty_opis
                
                # Hologram (zabezpieczenie)
                class DummyUnit:
                    def __init__(self, name):
                        self.type = name
                        self.type_code = name
                        self.owner = castle.owner 
                
                self.world.inspected_unit = DummyUnit(u_name)
                
                # 4. Przełączamy ekran
                # Zapisujemy poprzedni ekran!
                self.world.previous_screen = self.world.screen 
                # Przełączamy ekran
                self.world.screen = "unit_info"

                
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
        # Przewijanie listy (Guziki)
        if "UP" in self.custom_buttons and self.custom_buttons["UP"]["rect"].collidepoint(mx, my):
            self.custom_buttons["UP"]["timer"] = pygame.time.get_ticks()
            self.scroll = max(-2, self.scroll - 1)
            self.selected_patent_index = None
            return
            
        if "DOWN" in self.custom_buttons and self.custom_buttons["DOWN"]["rect"].collidepoint(mx, my):
            self.custom_buttons["DOWN"]["timer"] = pygame.time.get_ticks()
            self.scroll = min(len(unit_types)-3, self.scroll + 1)
            self.selected_patent_index = None
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

        # ... (tu masz kliknięcie w listę jednostek po lewej)
        for i, rect in enumerate(self.unit_list_rects):
            if rect.collidepoint(mx, my):
                clicked_unit_idx = self.scroll + i
                if 0 <= clicked_unit_idx < len(unit_types):
                    self.scroll = clicked_unit_idx - 2 
                    self.selected_patent_index = None
                    return

        # ==========================================
        # KLIKNIĘCIE W SIATKĘ PATENTÓW PO PRAWEJ
        # ==========================================
        if hasattr(self, 'patent_rects'):
            for i, rect in enumerate(self.patent_rects):
                if rect.collidepoint(mx, my):
                    # Sprawdzamy czy w tym slocie faktycznie jest jakiś wykupiony patent
                    if i < len(castle.patents) and castle.patents[i] is not None:
                        self.selected_patent_index = i
                        print(f"Zaznaczono patent w slocie: {i}")
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