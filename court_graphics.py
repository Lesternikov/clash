import pygame
import os

class CourtGraphics:
    def __init__(self, screen_width, screen_height):
        self.w = screen_width
        self.h = screen_height
        
        try:
            surowe_tlo = pygame.image.load(os.path.join("assets","minimum", "STAT_S32", "STAT_S32_43.png")).convert()
            self.bg = pygame.transform.scale(surowe_tlo, (screen_width, screen_height))
            
            # --- ZMIANA: używamy convert() ZAMIAST convert_alpha() ---
            arkusz_stat = pygame.image.load(os.path.join("assets","minimum", "STAT_S32", "STAT_S32_41.png")).convert()
            arkusz_stat.set_colorkey((255, 255, 255)) # Teraz wytnie biały idealnie!
            
            # =========================================================
            # WYCINANIE Z TWOICH DOKŁADNYCH KOORDYNATÓW
            # =========================================================
            self.btn_imgs = {
                "BACK": {
                    "normal": arkusz_stat.subsurface(pygame.Rect(7, 57, 74, 41)),
                    "active": arkusz_stat.subsurface(pygame.Rect(189, 60, 74, 41))
                },
                "KAT": {
                    "normal": arkusz_stat.subsurface(pygame.Rect(327, 363, 73, 34)),
                    "active": arkusz_stat.subsurface(pygame.Rect(28, 156, 73, 34))
                },
                "TORTURY": {
                    "normal": arkusz_stat.subsurface(pygame.Rect(327, 403, 73, 34)),
                    "active": arkusz_stat.subsurface(pygame.Rect(422, 50, 73, 34))
                },
                "KUP": {
                    "normal": arkusz_stat.subsurface(pygame.Rect(318, 441, 82, 34)),
                    "active": arkusz_stat.subsurface(pygame.Rect(367, 223, 82, 34))
                }
            }
            
            # Portret więźnia
            self.img_prisoner = arkusz_stat.subsurface(pygame.Rect(87, 240, 53, 61))
            
            # Oznaczenie frakcji (wycinamy ten żółty prostokącik z arkusza)
            self.img_faction_color = arkusz_stat.subsurface(pygame.Rect(41, 381, 20, 10))
            
            # --- BLOK ŁADOWANIA KORONY / ZNACZNIKA FRAKCJI ---
            try:
                # ZMIANA: używamy .convert() ZAMIAST .convert_alpha()
                surowa_korona = pygame.image.load(os.path.join("assets","minimum", "STAT_S32", "STAT_S32_44.png")).convert()
                # USUNIĘCIE BIAŁEGO TŁA: wskazujemy czystą biel jako przezroczystość!
                surowa_korona.set_colorkey((255, 255, 255))
                self.img_crown = surowa_korona
                print("Grafika korony STAT_S32_44.png załadowana i oczyszczona z bieli!")
            except Exception as e:
                print(f"Błąd ładowania STAT_S32_44.png (używam zapasowego paska): {e}")
                self.img_crown = self.img_faction_color
            
        except Exception as e:
            print(f"Błąd ładowania grafik Dworu: {e}")
            self.bg = pygame.Surface((screen_width, screen_height))
            self.bg.fill((40, 30, 20))
            self.btn_imgs = {}

        self.font_names = pygame.font.SysFont("Arial", 18, bold=True)
        self.font_stats = pygame.font.SysFont("Courier New", 16)
        self.font_queen = pygame.font.SysFont("Times New Roman", 20, italic=True)

    def draw_screen(self, screen, world, mx, my):
        # 1. Rysowanie Tła
        screen.blit(self.bg, (0, 0))
        
        # 2. Reszta elementów UI
        self._draw_player_info(screen, world)
        self._draw_queen_section(screen, world)
        self._draw_prisoners(screen, world, mx, my)
        self._draw_interactive_buttons(screen, world, mx, my)

    def _draw_player_info(self, screen, world):
        # Do zrobienia w przyszłości (Puste, żeby gra nie wyrzucała błędów)
        pass

    def _draw_queen_section(self, screen, world):
        # Do zrobienia w przyszłości
        pass

    def _draw_prisoners(self, screen, world, mx, my):
        if not self.btn_imgs: return
        
        court = world.court

        def draw_scaled(img, rect):
            scaled_img = pygame.transform.scale(img, (rect.width, rect.height))
            screen.blit(scaled_img, rect.topleft)

        for i, slot in enumerate(court.prison_slots):
            rects = court.prison_ui_rects[i]

            if slot.general:
                # ==========================================
                # CELA PEŁNA (Jest więzień)
                # ==========================================
                draw_scaled(self.img_prisoner, rects["PORTRET"])
                draw_scaled(self.img_crown, rects["KOLOR"])
                
                is_kat = (court.selected_prison_action == {"slot": i, "action": "KAT"})
                is_tort = (court.selected_prison_action == {"slot": i, "action": "TORTURY"})
                is_kup = (court.selected_prison_action == {"slot": i, "action": "KUP"})
                
                # Przyciski reagują TYLKO na kliknięcie (zapisane w logice), brak hovera
                state_kat = "active" if is_kat else "normal"
                draw_scaled(self.btn_imgs["KAT"][state_kat], rects["KAT"])

                state_tort = "active" if is_tort else "normal"
                draw_scaled(self.btn_imgs["TORTURY"][state_tort], rects["TORTURY"])

                state_kup = "active" if is_kup else "normal"
                draw_scaled(self.btn_imgs["KUP"][state_kup], rects["KUP"])

            else:
                # ==========================================
                # CELA PUSTA (Brak więźnia)
                # ==========================================
                # Rysujemy tylko odciśnięte (normalne) przyciski
                draw_scaled(self.btn_imgs["KAT"]["normal"], rects["KAT"])
                draw_scaled(self.btn_imgs["TORTURY"]["normal"], rects["TORTURY"])
                draw_scaled(self.btn_imgs["KUP"]["normal"], rects["KUP"])

    def _draw_interactive_buttons(self, screen, world, mx, my):
        court = world.court
        
        # PRZYCISK POWROTU
        if self.btn_imgs:
            rect_back = court.court_back_button
            
            # --- ZMIANA: Brak hovera. Przycisk wciśnie się tylko podczas animacji wyjścia z ekranu ---
            is_clicked = getattr(world, 'back_anim_timer', 5) > 0
            state_back = "active" if is_clicked else "normal"
            
            img_back_scaled = pygame.transform.scale(self.btn_imgs["BACK"][state_back], (rect_back.width, rect_back.height))
            screen.blit(img_back_scaled, rect_back.topleft)

    if __name__ == "__main__":
        import subprocess, sys, os
        main_path = os.path.join(os.path.dirname(__file__), "main.py")
        subprocess.run([sys.executable, main_path])