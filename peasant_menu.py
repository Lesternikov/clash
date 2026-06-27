import os
import pygame

class PeasantMenu:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.sx = screen_w / 640.0
        self.sy = screen_h / 480.0
        
        # Zmienne stanu
        self.send_peasants_amount = 0
        self.send_gold_amount = 0 
        self.castle_list_offset = 0
        # --- ZMIENNE LISTY ZAMKÓW ---
        self.scroll = -2 
        self.castle_list_rects = []
        self.last_click_time = 0
        self.last_clicked_idx = -1

        # Ładowanie tła
        bg_path = os.path.join("assets", "DW_15_GFX.png")
        if os.path.exists(bg_path):
            raw_bg = pygame.image.load(bg_path).convert_alpha()
            self.bg = pygame.transform.scale(raw_bg, (screen_w, screen_h))
        else:
            self.bg = pygame.Surface((screen_w, screen_h))
            self.bg.fill((50, 40, 30))

        self.font = pygame.font.SysFont(None, 24)
        
        # --- CZCIONKI ---
        try:
            # Próba załadowania systemowej czcionki gotyckiej
            self.font_gothic = pygame.font.SysFont("Old English Text MT", 75) 
        except:
            # Fallback (awaryjnie) w razie braku czcionki w systemie
            self.font_gothic = pygame.font.SysFont("Times New Roman", 55, bold=True)
            
        self.font = pygame.font.SysFont("timesnewroman", 24, bold=True)
        self.font_morale = pygame.font.SysFont("timesnewroman", 30, bold=True)
        self.font_bottom = pygame.font.SysFont("timesnewroman", 20, bold=True)
        # ========================================================
        # ŁADOWANIE WSZYSTKICH STRZAŁEK
        # ========================================================
        self.arrows = {}
        # Pełna lista wszystkich 9 bazowych nazw z Twoich screenów
        arrow_bases = [
            "chłopi_up", "chłopi_down", 
            "gold_up", "gold_down", 
            "castle_up", "castle_down", 
            "tax_up", "tax_down", 
            "send_gold"
        ]
        
        for base in arrow_bases:
            for suffix in ["", "2"]:
                name = f"{base}{suffix}"
                path = os.path.join("assets/przyciskiP", f"{name}.png")
                if os.path.exists(path):
                    self.arrows[name] = pygame.image.load(path).convert_alpha()
                else:
                    self.arrows[name] = None
                    print(f"Uwaga: Brak pliku {name}.png")

        # ========================================================
        # ŁADOWANIE WSKAŹNIKÓW ZADOWOLENIA (Buźki/Strzałki trendu)
        # ========================================================
        path_up = os.path.join("assets/przyciskiP", "arrow_up.png")
        self.trend_up = pygame.image.load(path_up).convert_alpha() if os.path.exists(path_up) else None
        
        path_down = os.path.join("assets/przyciskiP", "happy_down.png")
        self.trend_down = pygame.image.load(path_down).convert_alpha() if os.path.exists(path_down) else None

        # ========================================================
        # KOORDYNATY I ROZMIARY PRZYCISKÓW
        # ========================================================
        # Małe złote tarcze mają stały wymiar 40x40
        
        self.tax_minus_button = pygame.Rect(279, screen_h//2 - 55, 44, 54)
        self.tax_plus_button = pygame.Rect(279, screen_h//2 - 110, 44, 54)
        
        self.castle_up_button = pygame.Rect(screen_w//2 + 223, screen_h//2 + 43, 48, 85)
        self.castle_down_button = pygame.Rect(screen_w//2 + 223, screen_h//2 + 128, 48, 85)
        
        self.peasants_minus_button = pygame.Rect(screen_w - 203, screen_h//2 + 200, 44, 54)
        self.peasants_plus_button = pygame.Rect(screen_w - 203, screen_h//2 + 146, 44, 54)
        
        self.gold_minus_button = pygame.Rect(screen_w - 203, screen_h//2 + 65, 44, 54)
        self.gold_plus_button = pygame.Rect(screen_w - 203, screen_h//2 + 10, 44, 54)
                
        # Szeroki przycisk wysyłania: 120x55 (dopasowany do proporcji obrazka send_gold)
        self.send_button = pygame.Rect(screen_w - 218, screen_h//2 + 296, 150, 85)

        # Napis TAX (Opcjonalnie)
        path = os.path.join("assets", "TAX.png")
        self.TAX = pygame.image.load(path).convert_alpha() if os.path.exists(path) else None

    def _draw_text_with_outline(self, screen, text, font, x, y, text_color=(255, 255, 255), outline_color=(0, 0, 0)):
        """Rysuje tekst z bardzo delikatnym cieniem (1 piksel), leciutko podkreślając cyfry."""
        text_str = str(text)
        
        # Rysujemy tylko jeden cień przesunięty o 1 piksel w prawo i 1 piksel w dół
        shadow_surf = font.render(text_str, True, outline_color)
        screen.blit(shadow_surf, (x + 2, y + 2))
            
        # Na to nakładamy główny biały tekst
        text_surf = font.render(text_str, True, text_color)
        screen.blit(text_surf, (x, y))

    def _draw_arrow(self, screen, rect, base_name):
        """Uniwersalna funkcja do rysowania interaktywnych grafik."""
        mx, my = pygame.mouse.get_pos()
        # Jeżeli mysz najechała i jest wciśnięty LPM
        is_pressed = rect.collidepoint(mx, my) and pygame.mouse.get_pressed()[0]
        
        img_name = f"{base_name}2" if is_pressed else base_name
        img = self.arrows.get(img_name)
        
        # Fallback (jeśli np. nie ma wciśniętej wersji, używamy zwykłej)
        if not img: 
            img = self.arrows.get(base_name)
            
        if img:
            scaled = pygame.transform.scale(img, (rect.width, rect.height))
            screen.blit(scaled, rect.topleft)
        else:
            # Czerwony prostokąt błędu oznacza, że program nie znalazł w ogóle pliku
            pygame.draw.rect(screen, (255, 0, 0), rect)

    def draw(self, screen, w):
        """Główna funkcja rysująca wszystko w menu chłopów."""
        castle = w.selected_castle
        if not castle: return

        sx, sy = self.sx, self.sy

        # 1. Rysuj Tło
        screen.blit(self.bg, (0, 0))

        # 2. Obliczenia
        happiness_factor = 0.5 + (castle.happiness / 100) * 0.5
        tax_income = int(castle.peasants * 0.1 * castle.tax_rate * happiness_factor)

        # 3. Informacje o wybranym zamku (Góra)
        
        # --- GRAFICZNA LICZBA CHŁOPÓW (Używa plików RED_S32 przez renderer) ---
        peasants_count_str = str(int(getattr(castle, 'peasants', 0)))
        # Szacunkowe centrowanie dla skali 1.5
        txt_x = (self.screen_w // 2) - (len(peasants_count_str) * 20)
        txt_y = 40
        
        # Wywołujemy render z custom_font, który znajduje się w obiekcie w.renderer
        w.renderer.custom_font.render(
            screen, peasants_count_str, 
            txt_x, txt_y, 
            spacing=2, palette_name="golden", scale=1.5
        )

        # --- ZADOWOLENIE (MORALE) ---
        happiness_val = int(getattr(castle, 'happiness', 50)) # Zamiana na liczbę całkowitą
        hap_shadow = self.font_morale.render(f"{happiness_val}", True, (0, 0, 0))
        hap_txt = self.font_morale.render(f"{happiness_val}", True, (255, 255, 255))
        
        hap_x = self.screen_w // 2 
        hap_y = 138
        
        screen.blit(hap_shadow, (hap_x + 2, hap_y + 2))
        screen.blit(hap_txt, (hap_x, hap_y))

        # --- ZŁOTO --- 
        gold_str = str(castle.gold).replace(" ", "")
        
        w.renderer.custom_font.render(
            screen, gold_str, 
            self.screen_w - 142, 52, 
            spacing=0.5, palette_name="golden", scale=1.55
        )

        # WSKAŹNIK TRENDU (Strzałka przy poziomie zadowolenia)
        trend_img = self.trend_up if castle.happiness >= 50 else self.trend_down
        if trend_img:
            tw, th = int(42 * sx), int(41 * sy)
            scaled_trend = pygame.transform.scale(trend_img, (tw, th))
            screen.blit(scaled_trend, (self.screen_w//2 + 101, 31))

        # 4. Podatki (Lewa strona) - Z czarnym obrysem retro
        tax_rate_str = f"{castle.tax_rate:.1f}".replace(" ", "")
        w.renderer.custom_font.render(
            screen, tax_rate_str,
            353, self.screen_h//2 - 62,
            spacing=1, palette_name="golden", scale=1.55
        )

        tax_income_str = str(tax_income).replace(" ", "")
        w.renderer.custom_font.render(
            screen, tax_income_str,
            754, self.screen_h//2 - 64,
            spacing=1, palette_name="golden", scale=1.55
)

        self._draw_arrow(screen, self.tax_minus_button, "tax_down")
        self._draw_arrow(screen, self.tax_plus_button, "tax_up")

        # =========================================================
        # 5. Lista zamków (Środek - Dolny panel)
        # =========================================================
        base_x = self.screen_w // 2 - 220 
        base_y = self.screen_h // 2 + 55 # Trochę wyżej, żeby zmieścić 5 linijek
        step_y = 31 # Odstęp między linijkami

        # Pobieramy zamki i wymuszamy, aby NASZ OBECNY zamek był zawsze na pozycji 0
        owned = [c for c in w.castles if c.owner == w.players[w.current_player] and not getattr(c, 'destroyed', False)]
        if castle in owned:
            owned.remove(castle)
            owned.insert(0, castle)

        self.castle_list_rects = []

        # Rysujemy 5 slotów (od 0 do 4, gdzie 2 to środek)
        for i in range(5):
            scroll_idx = self.scroll + i
            row_y = base_y + i * step_y
            
            # Tworzymy rect do klikania
            rect = pygame.Rect(base_x, row_y, 420, step_y)
            self.castle_list_rects.append(rect)

            # Jeśli w tym slocie znajduje się jakiś zamek z naszej listy:
            if 0 <= scroll_idx < len(owned):
                c = owned[scroll_idx]
                
                # Nazwa (obecny zamek ma specjalną nazwę)
                if c == castle:
                    c_name = "PRZED MURY ZAMKU"
                else:
                    c_name = getattr(c, 'name', f"ZAMEK ({c.x},{c.y})").upper()
                
                # Kolor (Środek = Biały, Reszta = Szary)
                if i == 2:
                    t_col = (255, 255, 255)
                else:
                    t_col = (150, 150, 150)
                    
                # Rysujemy ZAWSZE nazwę zamku
                txt_name = self.font_bottom.render(c_name, True, t_col)
                sh_name = self.font_bottom.render(c_name, True, (0, 0, 0))
                
                row_y = base_y + i * step_y
                screen.blit(sh_name, (base_x + 2, row_y + 2))
                screen.blit(txt_name, (base_x, row_y))
                
                #Rysujemy Chłopów i Złoto TYLKO jeśli to nie jest nasz obecny zamek!
                if c != castle:
                    txt_p_lbl = self.font_bottom.render("P: ", True, t_col)
                    sh_p_lbl = self.font_bottom.render("P: ", True, (0, 0, 0))
                    screen.blit(sh_p_lbl, (base_x + 160 + 2, row_y + 2))
                    screen.blit(txt_p_lbl, (base_x + 160, row_y))

                    c_peasants_str = str(c.peasants).replace(" ", "")
                    w.renderer.custom_font.render(
                        screen, c_peasants_str,
                        base_x + 185, row_y + 4.5,
                        spacing=1, palette_name="golden", scale=1.2
                    )

                    txt_g_lbl = self.font_bottom.render("G: ", True, t_col)
                    sh_g_lbl = self.font_bottom.render("G: ", True, (0, 0, 0))
                    screen.blit(sh_g_lbl, (base_x + 260 + 2, row_y + 2))
                    screen.blit(txt_g_lbl, (base_x + 260, row_y))

                    c_gold_str = str(c.gold).replace(" ", "")
                    w.renderer.custom_font.render(
                        screen, c_gold_str,
                        base_x + 285, row_y + 4.5,
                        spacing=1, palette_name="golden", scale=1.2
                    )

        # --- STRZAŁKI LISTY ZAMKÓW ---
        self._draw_arrow(screen, self.castle_up_button, "castle_up")
        self._draw_arrow(screen, self.castle_down_button, "castle_down")

        # 6. Wysyłanie zasobów (Prawa strona)
        self._draw_arrow(screen, self.peasants_minus_button, "chłopi_down")
        self._draw_arrow(screen, self.peasants_plus_button, "chłopi_up")
        
        self._draw_arrow(screen, self.gold_minus_button, "gold_down")
        self._draw_arrow(screen, self.gold_plus_button, "gold_up")
        
        # --- PRZYCISK WYSYŁANIA ---
        self._draw_arrow(screen, self.send_button, "send_gold")
        
        # Wartości do wysłania - Z czarnym obrysem retro
        send_peasants_str = str(self.send_peasants_amount).replace(" ", "")
        w.renderer.custom_font.render(
            screen, send_peasants_str,
            self.screen_w - 120, self.screen_h//2 + 190,
            spacing=1, palette_name="golden", scale=1.55
        )

        send_gold_str = str(self.send_gold_amount).replace(" ", "")
        w.renderer.custom_font.render(
            screen, send_gold_str,
            self.screen_w - 120, self.screen_h//2 + 55,
            spacing=1, palette_name="golden", scale=1.55
)

        # 7. Przycisk Powrotu (obsługiwany przez funkcję z pliku world)
        w.renderer.draw_building_footer(screen)

        # Opcjonalne logo TAX
        if self.TAX:
            px, py, pw, ph = 268, 149, 112, 21
            scaled_obj = pygame.transform.scale(self.TAX, (int(pw * sx), int(ph * sy)))
            screen.blit(scaled_obj, (int(px * sx), int(py * sy)))
        
        # 1. Pojedyncze przyciski (podatki, chłopi, złoto, wyślij)
        buttons_to_draw = [
            self.tax_minus_button, self.tax_plus_button,
            self.peasants_minus_button, self.peasants_plus_button,
            self.gold_minus_button, self.gold_plus_button,
            self.send_button
        ] 
        
    def handle_click(self, mx, my, w):
        """Obsługuje kliknięcia w menu."""
        if w.back_button.collidepoint(mx, my):
            w.back_destination = "castle"
            w.back_anim_timer = pygame.time.get_ticks()
            return

        castle = w.selected_castle
        if not castle: return

        # Zmiana chłopów
        if self.peasants_plus_button.collidepoint(mx, my):
            if self.send_peasants_amount + 10 <= castle.peasants: self.send_peasants_amount += 10
            return
        if self.peasants_minus_button.collidepoint(mx, my):
            self.send_peasants_amount = max(0, self.send_peasants_amount - 10)
            return
            
        # Zmiana złota
        if self.gold_plus_button.collidepoint(mx, my):
            if self.send_gold_amount + 10 <= castle.gold: self.send_gold_amount += 10
            return
        if self.gold_minus_button.collidepoint(mx, my):
            self.send_gold_amount = max(0, self.send_gold_amount - 10)
            return
            
        # Zmiana podatków
        if self.tax_plus_button.collidepoint(mx, my):
            castle.tax_rate = min(4.0, castle.tax_rate + 0.1)
            return
        if self.tax_minus_button.collidepoint(mx, my):
            castle.tax_rate = max(0.0, castle.tax_rate - 0.1)
            return
            
        # ==========================================
        # Lista zamków (Przewijanie i Klikanie)
        # ==========================================
        owned = [c for c in w.castles if c.owner == w.players[w.current_player] and not getattr(c, 'destroyed', False)]
        if castle in owned:
            owned.remove(castle)
            owned.insert(0, castle)
            
        max_scroll = max(-2, len(owned) - 3)

        # 1. STRZAŁKI (z inflate dla łatwiejszego trafienia)
        up_rect = self.castle_up_button.inflate(20, 20)
        down_rect = self.castle_down_button.inflate(20, 20)

        if up_rect.collidepoint(mx, my):
            self.scroll = max(-2, getattr(self, 'scroll', -2) - 1)
            return
            
        if down_rect.collidepoint(mx, my):
            self.scroll = min(max_scroll, getattr(self, 'scroll', -2) + 1)
            return
            
        # --- DEFINICJA 'now' (Naprawia błąd NameError) ---
        now = pygame.time.get_ticks() 

        # 2. KLIKNIĘCIE W NAZWĘ ZAMKU (Teleportacja)
        for i, rect in enumerate(getattr(self, 'castle_list_rects', [])):
            if rect.collidepoint(mx, my):
                clicked_idx = getattr(self, 'scroll', -2) + i
                if 0 <= clicked_idx < len(owned):
                    
                    # SPRAWDZENIE PODWÓJNEGO KLIKNIĘCIA
                    if now - getattr(self, 'last_click_time', 0) < 500 and getattr(self, 'last_clicked_idx', -1) == clicked_idx:
                        new_castle = owned[clicked_idx]
                        print(f"Teleportacja do: {getattr(new_castle, 'name', 'Zamek')}")
                        
                        # --- KROK A: ZMIANA ZAMKU ---
                        w.selected_castle = new_castle
                        
                        # --- KROK B: CENTROWANIE KAMERY NA MAPIE ---
                        from settings import TILE_SIZE
                        # Ustawiamy kamerę tak, by zamek był na środku ekranu po wyjściu na mapę
                        w.camera_x = new_castle.x * TILE_SIZE - (self.screen_w // 2)
                        w.camera_y = new_castle.y * TILE_SIZE - (self.screen_h // 2)
                        
                        self.scroll = -2 
                        self.last_click_time = 0 
                    else:
                        # Pierwsze kliknięcie - tylko wyśrodkowanie na liście
                        self.scroll = clicked_idx - 2
                        self.last_click_time = now
                        self.last_clicked_idx = clicked_idx
                        
                    return
                 
        # Guzik WYSYŁANIA (send_gold)
        if self.send_button.collidepoint(mx, my):
            if self.send_peasants_amount <= castle.peasants and self.send_gold_amount <= castle.gold:
                castle.peasants -= self.send_peasants_amount
                castle.gold -= self.send_gold_amount
                print("Zasoby wysłane!")
                self.send_peasants_amount = 0
                self.send_gold_amount = 0
            return

    def handle_scroll_wheel(self, event, w):
        castle = w.selected_castle
        if not castle: return

        owned = [c for c in w.castles if c.owner == w.players[w.current_player] and not getattr(c, 'destroyed', False)]
        max_scroll = max(-2, len(owned) - 3)

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