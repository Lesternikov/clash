import os
import pygame

class PeasantMenu:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.sx = screen_w / 640.0
        self.sy = screen_h / 480.0
        
        # Zmienne stanu
        self.send_peasants_amount = 10
        self.send_gold_amount = 100 
        self.castle_list_offset = 0

        # Ładowanie tła
        bg_path = os.path.join("assets", "DW_15_GFX.png")
        if os.path.exists(bg_path):
            raw_bg = pygame.image.load(bg_path).convert_alpha()
            self.bg = pygame.transform.scale(raw_bg, (screen_w, screen_h))
        else:
            self.bg = pygame.Surface((screen_w, screen_h))
            self.bg.fill((50, 40, 30))

        self.font = pygame.font.SysFont(None, 24)

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
        screen.blit(self.font.render(f"Peasants: {castle.peasants}", True, (255,255,255)), (self.screen_w//2 - 60, 20))
        screen.blit(self.font.render(f"Happiness: {castle.happiness}%", True, (200,255,200)), (self.screen_w//2 - 70, 45))
        screen.blit(self.font.render(f"Gold: {castle.gold}", True, (255,215,0)), (self.screen_w - 120, 20))

        # WSKAŹNIK TRENDU (Strzałka przy poziomie zadowolenia)
        trend_img = self.trend_up if castle.happiness >= 50 else self.trend_down
        if trend_img:
            tw, th = int(35 * sx), int(55 * sy)
            scaled_trend = pygame.transform.scale(trend_img, (tw, th))
            screen.blit(scaled_trend, (self.screen_w//2 + 110, 15))

        # 4. Podatki (Lewa strona)
        screen.blit(self.font.render(f"{castle.tax_rate:.1f}", True, (255,255,255)), (365, self.screen_h//2 - 62))
        screen.blit(self.font.render(f"{tax_income}", True, (255,255,0)), (757, self.screen_h//2 - 64))

        self._draw_arrow(screen, self.tax_minus_button, "tax_down")
        self._draw_arrow(screen, self.tax_plus_button, "tax_up")

        # 5. Lista zamków (Środek)
        owned = [c for c in w.castles if c.owner == w.players[w.current_player] and not getattr(c, 'destroyed', False)]
        visible = owned[self.castle_list_offset : self.castle_list_offset+3]

        for i, c in enumerate(visible):
            txt = f"Castle ({c.x},{c.y})  P:{c.peasants} G:{c.gold}"
            screen.blit(self.font.render(txt, True, (255,255,255)), (self.screen_w//2 - 130, self.screen_h//2  + 100 + i*30))

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
        
        # Wartości do wysłania
        screen.blit(self.font.render(f"P: {self.send_peasants_amount}", True, (255,255,255)), (self.screen_w-120, self.screen_h//2 - 60))
        screen.blit(self.font.render(f"G: {self.send_gold_amount}", True, (255,255,0)), (self.screen_w-120, self.screen_h//2 - 15))

        # 7. Przycisk Powrotu (obsługiwany przez funkcję z pliku world)
        w.renderer.draw_building_footer(screen)

        # Opcjonalne logo TAX
        if self.TAX:
            px, py, pw, ph = 268, 149, 112, 21
            scaled_obj = pygame.transform.scale(self.TAX, (int(pw * sx), int(ph * sy)))
            screen.blit(scaled_obj, (int(px * sx), int(py * sy)))


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
            
        # Lista zamków
        owned = [c for c in w.castles if c.owner == w.players[w.current_player]]
        max_offset = max(0, len(owned) - 3)

        if self.castle_up_button.collidepoint(mx, my):
            self.castle_list_offset = max(0, self.castle_list_offset - 1)
            return
        if self.castle_down_button.collidepoint(mx, my):
            self.castle_list_offset = min(max_offset, self.castle_list_offset + 1)
            return
            
        # Guzik WYSYŁANIA (send_gold)
        if self.send_button.collidepoint(mx, my):
            if self.send_peasants_amount <= castle.peasants and self.send_gold_amount <= castle.gold:
                castle.peasants -= self.send_peasants_amount
                castle.gold -= self.send_gold_amount
                print("Zasoby wysłane!")
                self.send_peasants_amount = 0
                self.send_gold_amount = 0

    if __name__ == "__main__":
        import subprocess, sys, os
        main_path = os.path.join(os.path.dirname(__file__), "main.py")
        subprocess.run([sys.executable, main_path])