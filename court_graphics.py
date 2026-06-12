import os
import pygame
import random

class CourtGraphics:
    def __init__(self, screen_width, screen_height):
        self.w = screen_width
        self.h = screen_height
        self.assets = {}
        self.btn_imgs = {}

        try:
            surowe_tlo = pygame.image.load(os.path.join("assets", "minimum", "STAT_S32", "STAT_S32_43.png")).convert()
            self.bg = pygame.transform.scale(surowe_tlo, (screen_width, screen_height))
        except Exception as e:
            print(f"Błąd ładowania tła Dworu: {e}")
            self.bg = pygame.Surface((screen_width, screen_height))
            self.bg.fill((40, 30, 20))

        try:
            arkusz_stat = pygame.image.load(os.path.join("assets", "minimum", "STAT_S32", "STAT_S32_41.png")).convert()
            arkusz_stat.set_colorkey((255, 255, 255))
            
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
            self.img_prisoner = arkusz_stat.subsurface(pygame.Rect(87, 240, 53, 61))
            self.img_faction_color = arkusz_stat.subsurface(pygame.Rect(40, 381, 20, 10))
            
        except Exception as e:
            self.img_prisoner = pygame.Surface((53, 61))
            self.img_faction_color = pygame.Surface((20, 10))

        try:
            surowa_korona = pygame.image.load(os.path.join("assets", "minimum", "STAT_S32", "STAT_S32_44.png")).convert()
            surowa_korona.set_colorkey((255, 255, 255))
            self.img_crown = surowa_korona
        except Exception as e:
            self.img_crown = self.img_faction_color

        sheet_paths = [
            os.path.join("assets", "DWOR.png"),
            os.path.join("assets", "dwor.png"),
            "DWOR.png",
            "dwor.png"
        ]
        
        self.sheet_dwor = None
        for path in sheet_paths:
            if os.path.exists(path):
                try:
                    self.sheet_dwor = pygame.image.load(path).convert_alpha()
                    self._cut_dwor_assets()
                    break
                except Exception as e:
                    print(f"Błąd przetwarzania arkusza {path}: {e}")

        self.font_names = pygame.font.SysFont("Arial", 18, bold=True)
        self.font_stats = pygame.font.SysFont("Courier New", 14, bold=True)
        self.font_queen = pygame.font.SysFont("Times New Roman", 20, italic=True)

    def _cut_dwor_assets(self):
        coords = {
            "KROLOWA1": (1, 135, 95, 133),     "KROLOWA2": (99, 135, 95, 133),
            "KROLOWA3": (187, 135, 95, 133),   "KROLOWA4": (283, 135, 95, 133),
            "KROLOWA5": (378, 135, 95, 133),   "KROLOWA6": (470, 135, 95, 133),
            "KROLOWA7": (561, 135, 95, 133),   "KROLOWA8": (654, 135, 95, 133),
            "KROLOWA9": (748, 135, 95, 133),   
            
            "CZERWONYK": (144, 44, 42, 22),   "CZERWONYP": (145, 76, 42, 22),   "CZERWONYW": (11, 34, 20, 10),
            "NIEBIESKIK": (67, 36, 42, 22),   "NIEBIESKIP": (272, 41, 42, 22),  "NIEBIESKIW": (13, 14, 20, 10),
            "ŻÓŁTYK": (415, 40, 42, 22),       "ŻÓŁTYP": (146, 10, 42, 22),      "ŻÓŁTYW": (41, 22, 20, 10),
            "ZIELONYK": (77, 86, 42, 22),     "ZIELONYP": (211, 36, 42, 22),    "ZIELONYW": (496, 381, 20, 10),
            "BIAŁYK": (355, 45, 42, 22),       "BIAŁYP": (211, 74, 42, 22),      "BIAŁYW": (78, 12, 20, 10),
            
            "CZERWONY_PASEK": (552, 23, 120, 11),
            "NIEBIESKI_PASEK": (552, 36, 120, 11),
            "ŻÓŁTY_PASEK": (552, 49, 120, 11),
            "BIAŁY_PASEK": (552, 62, 120, 11),
            "ZIELONY_PASEK": (552, 75, 120, 11)
        }
        for name, rect in coords.items():
            try:
                self.assets[name] = self.sheet_dwor.subsurface(pygame.Rect(rect))
            except Exception as e:
                pass

    def _get_color_key(self, color_name):
        mapping = {
            "red": "CZERWONY", "blue": "NIEBIESKI", "yellow": "ŻÓŁTY",
            "green": "ZIELONY", "white": "BIAŁY"
        }
        return mapping.get(color_name.lower(), "CZERWONY")

    def draw_screen(self, screen, world, mx, my):
        screen.blit(self.bg, (0, 0))
        active_player = world.players[world.current_player]

        total_castle_gold = sum(c.gold for c in world.castles if c.owner == active_player)
        if total_castle_gold >= 1000 and not getattr(active_player, 'has_queen', False):
            active_player.has_queen = True
            active_player.queen_mood = "Zachwycona"
            active_player.queen_portrait_idx = random.randint(1, 9)
            active_player.queen_timer = 5
        
        self._draw_global_leaderboard(screen, world)
        self._draw_queen_section(screen, active_player)
        self._draw_prisoners(screen, world, mx, my)
        self._draw_interactive_buttons(screen, world, mx, my)

    def _draw_global_leaderboard(self, screen, world):
        # =========================================================
        # 🟢 PANEL STEROWANIA NR 1: PASKI STATYSTYK (Siła, Złoto, Flaga)
        # =========================================================
        bars_start = {
            # Poprzednio było Y=260. Zmieniłem na 205, żeby weszły w czarne ramki!
            "STRENGTH": (145, 179), # Start paska Bicepsu (X, Y)
            "GOLD":     (485, 179), # Start paska Złota (X, Y)
            "WINS":     (825, 179)  # Start paska Flagi (X, Y)
        }
        bar_gap = 21          # Odstęp (w pikselach w dół) między paskiem Gracza 1, Gracza 2 itd.
        skala_paska_x = 1.6  # Chcesz dłuższe paski? Zwiększ to (np. 1.5)
        skala_paska_y = 1.6   # Chcesz grubsze paski w pionie? Zwiększ to (np. 1.2)
        # =========================================================

        # =========================================================
        # 🟢 PANEL STEROWANIA NR 2: IMIONA I ZNACZKI FRAKCJI (Krzyż/Wieża)
        # =========================================================
        # Główne punkty zaczepienia brązowych okienek na imiona
        box_coords = [
            (145, 45),  (430, 45),  (720, 45),  (280, 115), (570, 115)
        ]
        
        offset_herbu_x = 60    # Przesunięcie znaczka (w prawo) względem rogu ramki
        offset_herbu_y = -25    # Przesunięcie znaczka (w dół) względem rogu ramki
        skala_herbu = 1.3     # 1.0 to oryginał. 1.3 to powiększenie o 30%! Zmień jak wolisz.
        
        offset_tekstu_x = 60  # Odstęp tekstu w prawo (żeby zrobić miejsce na powiększony herb)
        offset_tekstu_y = 10   # Odstęp tekstu w dół (wyśrodkowanie z ramką)
        # =========================================================

        global_max_gold = max([p.gold for p in world.players] + [1])
        def calc_strength(p):
            return sum(getattr(u, 'hp', 100) for u in world.units if u.owner == p)
        global_max_strength = max([calc_strength(p) for p in world.players] + [1])
        global_max_wins = max([getattr(p, 'victories', 1) for p in world.players] + [1])

        for i, player in enumerate(world.players):
            if i >= 5: break 
            color_key = self._get_color_key(player.color_name)
            box_x, box_y = box_coords[i]
            
            # --- RYSOWANIE HERBU ---
            faction = getattr(player, 'faction', 'catholic')
            suffix = "K" if faction == "catholic" else "P"
            herb_key = f"{color_key}{suffix}"
            if herb_key in self.assets:
                img_herb = self.assets[herb_key]
                if skala_herbu != 1.0:
                    img_herb = pygame.transform.smoothscale(img_herb, (int(img_herb.get_width() * skala_herbu), int(img_herb.get_height() * skala_herbu)))
                screen.blit(img_herb, (box_x + offset_herbu_x, box_y + offset_herbu_y))
            
            # --- RYSOWANIE IMIENIA ---
            txt_name = self.font_names.render(player.name, True, (245, 235, 210))
            shadow_name = self.font_names.render(player.name, True, (0, 0, 0))
            screen.blit(shadow_name, (box_x + offset_tekstu_x + 1, box_y + offset_tekstu_y + 1))
            screen.blit(txt_name, (box_x + offset_tekstu_x, box_y + offset_tekstu_y))

            # --- RYSOWANIE PASKÓW STATYSTYK ---
            pasek_key = f"{color_key}_PASEK"
            if pasek_key in self.assets:
                oryg_pasek = self.assets[pasek_key]
                max_w = oryg_pasek.get_width() 
                h = oryg_pasek.get_height()
                
                # Biceps
                w_str = int(max_w * (calc_strength(player) / global_max_strength)) if global_max_strength > 0 else 0
                if w_str > 0:
                    bx, by = bars_start["STRENGTH"]
                    wycinek = oryg_pasek.subsurface(pygame.Rect(0, 0, w_str, h))
                    if skala_paska_x != 1.0 or skala_paska_y != 1.0:
                        wycinek = pygame.transform.scale(wycinek, (int(w_str * skala_paska_x), int(h * skala_paska_y)))
                    screen.blit(wycinek, (bx, by + (i * bar_gap)))
                    
                # Skarbiec
                w_gold = int(max_w * (player.gold / global_max_gold)) if global_max_gold > 0 else 0
                if w_gold > 0:
                    bx, by = bars_start["GOLD"]
                    wycinek = oryg_pasek.subsurface(pygame.Rect(0, 0, w_gold, h))
                    if skala_paska_x != 1.0 or skala_paska_y != 1.0:
                        wycinek = pygame.transform.scale(wycinek, (int(w_gold * skala_paska_x), int(h * skala_paska_y)))
                    screen.blit(wycinek, (bx, by + (i * bar_gap)))
                    
                # Wiktorie
                w_wins = int(max_w * (getattr(player, 'victories', 0) / global_max_wins)) if global_max_wins > 0 else 0
                if w_wins > 0:
                    bx, by = bars_start["WINS"]
                    wycinek = oryg_pasek.subsurface(pygame.Rect(0, 0, w_wins, h))
                    if skala_paska_x != 1.0 or skala_paska_y != 1.0:
                        wycinek = pygame.transform.scale(wycinek, (int(w_wins * skala_paska_x), int(h * skala_paska_y)))
                    screen.blit(wycinek, (bx, by + (i * bar_gap)))

    def _draw_queen_section(self, screen, player):
        # =========================================================
        # 🟢 PANEL STEROWANIA NR 3: LUSTRO I KRÓLOWA
        # =========================================================
        lustro_x = 57         # Przesuwamy Królową w prawo do owalnej ramki
        lustro_y = 314        # Przesuwamy Królową w górę do owalnej ramki
        skala_krolowej = 1.6 # Powiększenie samej twarzy wewnątrz ramy
        
        napis_x = 350         # Pozycja napisu "Nastrój Królowej" (X)
        napis_y = 350         # Pozycja napisu "Nastrój Królowej" (Y)
        # =========================================================
        
        if getattr(player, 'has_queen', False):
            idx = getattr(player, 'queen_portrait_idx', 1)
            portrait_key = f"KROLOWA{idx}"
            
            if portrait_key in self.assets:
                img_queen = self.assets[portrait_key]
                if skala_krolowej != 1.0:
                    img_queen = pygame.transform.smoothscale(img_queen, (int(img_queen.get_width() * skala_krolowej), int(img_queen.get_height() * skala_krolowej)))
                screen.blit(img_queen, (lustro_x, lustro_y))
            
            tekst_nastroju = self.font_queen.render(f"Nastrój Królowej: {player.queen_mood}", True, (30,20,10))
            screen.blit(tekst_nastroju, (napis_x, napis_y))
        else:
            tekst_brak = self.font_queen.render("Nie ma królowej", True, (140, 130, 120))
            screen.blit(tekst_brak, (napis_x, napis_y))

    def _draw_prisoners(self, screen, world, mx, my):
        if not self.btn_imgs: return
        court = world.court

        def draw_scaled(img, rect):
            scaled_img = pygame.transform.scale(img, (rect.width, rect.height))
            screen.blit(scaled_img, rect.topleft)

        for i, slot in enumerate(court.prison_slots):
            rects = court.prison_ui_rects[i]

            if slot.general:
                draw_scaled(self.img_prisoner, rects["PORTRET"])
                if hasattr(slot.general, 'owner') and slot.general.owner:
                    captured_color_key = self._get_color_key(slot.general.owner.color_name)
                    w_key = f"{captured_color_key}W"
                else:
                    w_key = "CZERWONYW"

                if w_key in self.assets:
                    draw_scaled(self.assets[w_key], rects["KOLOR"])
                else:
                    draw_scaled(self.img_crown, rects["KOLOR"])
                
                is_kat = (court.selected_prison_action == {"slot": i, "action": "KAT"})
                is_tort = (court.selected_prison_action == {"slot": i, "action": "TORTURY"})
                is_kup = (court.selected_prison_action == {"slot": i, "action": "KUP"})
                
                state_kat = "active" if is_kat else "normal"
                draw_scaled(self.btn_imgs["KAT"][state_kat], rects["KAT"])

                state_tort = "active" if is_tort else "normal"
                draw_scaled(self.btn_imgs["TORTURY"][state_tort], rects["TORTURY"])

                state_kup = "active" if is_kup else "normal"
                draw_scaled(self.btn_imgs["KUP"][state_kup], rects["KUP"])
            else:
                draw_scaled(self.btn_imgs["KAT"]["normal"], rects["KAT"])
                draw_scaled(self.btn_imgs["TORTURY"]["normal"], rects["TORTURY"])
                draw_scaled(self.btn_imgs["KUP"]["normal"], rects["KUP"])

    def _draw_interactive_buttons(self, screen, world, mx, my):
        court = world.court
        if self.btn_imgs:
            rect_back = court.court_back_button
            is_clicked = getattr(world, 'back_anim_timer', 0) > 0
            state_back = "active" if is_clicked else "normal"
            img_back_scaled = pygame.transform.scale(self.btn_imgs["BACK"][state_back], (rect_back.width, rect_back.height))
            screen.blit(img_back_scaled, rect_back.topleft)
        
if __name__ == "__main__":
    import subprocess, sys, os
    main_path = os.path.join(os.path.dirname(__file__), "main.py")
    subprocess.run([sys.executable, main_path])