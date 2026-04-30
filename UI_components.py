import os
import pygame
from settings import UNIT_STATS, UNIT_NAMES, NAME_TO_CODE

class UnitInfoWindow:
    def __init__(self):
        self.scale = 1.6  # Nasz mnożnik powiększenia

        # Funkcja pomocnicza do ładowania i skalowania
        # Funkcja pomocnicza do ładowania i skalowania
        def load_scaled(path):
            img = pygame.image.load(path).convert_alpha()
            w, h = img.get_size()
            # Używamy smoothscale do wygładzenia przy powiększeniu!
            return pygame.transform.smoothscale(img, (int(w * self.scale), int(h * self.scale)))
        # Ładowanie przeskalowanych teł
        self.bg_combat = load_scaled("assets/minimum/INFO_S32/INFO_S32_0.png")
        self.bg_simple = load_scaled("assets/minimum/INFO_S32/INFO_S32_1.png")
        self.sword_full = load_scaled("assets/minimum/INFO_S32/INFO_S32_2.png")
        
        # Ikony
        self.icon_moves = load_scaled("assets/minimum/INFO_S32/INFO_S32_25.png")
        self.icon_gold = load_scaled("assets/minimum/INFO_S32/INFO_S32_28.png")
        self.icon_amount = load_scaled("assets/minimum/INFO_S32/INFO_S32_24.png")
        self.icon_heart = load_scaled("assets/minimum/INFO_S32/INFO_S32_26.png")
        
        # Opcjonalnie: Załaduj "łatki" (tylko ręka / tylko łuk) jeśli je masz
        self.icon_melee = load_scaled("assets/minimum/INFO_S32/INFO_S32_9.png")
        self.icon_ranged = load_scaled("assets/minimum/INFO_S32/INFO_S32_10.png")
        # Czcionki - je też warto odrobinę powiększyć (np. z 20 na 23)
        self.font_main = pygame.font.SysFont("Times New Roman", 23, bold=True)
        self.font_stats = pygame.font.SysFont("Arial", 24, bold=True)

    def draw(self, screen, x, y, unit, mode):
        if mode == "SIMPLE":
            self.draw_simple_info(screen, x, y, unit)
        else:
            self.draw_combat_info(screen, x, y, unit)

    def draw_simple_info(self, screen, x, y, unit):
        screen.blit(self.bg_simple, (x, y))
        
        # POPRAWKA: Obsługa słownika i obiektu
        u_code = unit.get('type_code') if isinstance(unit, dict) else getattr(unit, 'type_code', "Unknown")
        name_str = UNIT_NAMES.get(u_code, "Nieznany")
        
        name_txt = self.font_main.render(name_str, True, (255, 255, 255))
        screen.blit(name_txt, (x + 100, y + 5))

        # Portret
        frame = (pygame.time.get_ticks() // 150) % 8
        if hasattr(unit, 'sprites'):
            screen.blit(unit.sprites[frame], (x + 15, y + 35))

        # Ruch
        screen.blit(self.icon_moves, (x + 15, y + 110))
        moves_txt = self.font_stats.render(str(unit.moves), True, (255, 255, 255))
        screen.blit(moves_txt, (x + 50, y + 115))

        # Specjalna wartość po prawej
        icon, val = None, 0
        if unit.type_code == "GOLD":
            icon, val = self.icon_gold, getattr(unit, 'amount', 0)
        elif unit.type_code == "PEAS":
            icon, val = self.icon_amount, getattr(unit, 'count', 0)
        elif unit.type_code in ["SPECK", "SPECM"]:
            icon, val = self.icon_heart, unit.hp
            
        if icon:
            screen.blit(icon, (x + 140, y + 40))
            val_txt = self.font_stats.render(str(val), True, (255, 215, 0))
            screen.blit(val_txt, (x + 180, y + 45))
    def draw_combat_info(self, screen, x, y, unit):
        s = self.scale

        # ==========================================
        # 1. TŁO (CZARNE KRYCIE)
        # ==========================================
        # Rysujemy jednolity CZARNY kwadrat, żeby załatać przezroczystości
        bg_w, bg_h = self.bg_combat.get_size()
        pygame.draw.rect(screen, (0, 0, 0), (x, y, bg_w, bg_h)) 
        screen.blit(self.bg_combat, (x, y))

        # ==========================================
        # 2. POBIERANIE NAZWY JEDNOSTKI
        # ==========================================
        def get_v(key, attr_name=None, default=0):
            if isinstance(unit, dict):
                return unit.get(key, default)
            return getattr(unit, attr_name if attr_name else key, default)

        if isinstance(unit, dict):
            raw_id = unit.get('type_code', 'Unknown')
        else:
            raw_id = getattr(unit, 'type_code', getattr(unit, 'type', 'Unknown'))

        u_code = NAME_TO_CODE.get(raw_id, raw_id)
        name_str = UNIT_NAMES.get(u_code, raw_id)

        # Pobieramy bazowe statystyki z settings.py (żeby żywe jednostki nie "gubiły" tagów!)
        base_stats = UNIT_STATS.get(name_str, {})

        # ==========================================
        # 3. LOGIKA PORTRETU (RĘCZNE STEROWANIE PROPORCJAMI)
        # ==========================================
        frame_idx = (pygame.time.get_ticks() // 150) % 8
        raw_img = None
        
        # ZAWSZE ładujemy czysty obrazek z dysku
        if u_code:
            path = f"assets/minimum/{u_code}1_I_S32/{u_code}1_I_S32_{frame_idx}.png"
            if os.path.exists(path):
                try:
                    raw_img = pygame.image.load(path).convert_alpha()
                except:
                    pass

        if raw_img:
            # --- PEŁNA WŁADZA NAD ROZMIAREM I PROPORCJAMI ---
            if isinstance(unit, dict):
                # A. USTAWIENIA DLA KOSZAR (REKRUTACJA)
                custom_w = 37       # <--- Szerokość
                custom_h = 65       # <--- Wysokość (Zwiększ, aby rozciągnąć w górę!)
                offset_x = 8       # <--- Przesunięcie w poziomie
                offset_y = 7       # <--- Przesunięcie w pionie (dałem wyżej, bo ludzik urósł)
            else:
                # B. USTAWIENIA DLA GARNIZONU I MAPY
                custom_w = 37       # <--- Szerokość
                custom_h = 65       # <--- Wysokość
                offset_x = 8       # <--- Przesunięcie w poziomie
                offset_y = 7        # <--- Przesunięcie w pionie

            # Skalujemy niezależnie szerokość i wysokość
            t_size = (int(custom_w * s), int(custom_h * s)) 
            portrait_img = pygame.transform.scale(raw_img, t_size)
            
            current_pos = (x + int(offset_x * s), y + int(offset_y * s))
            screen.blit(portrait_img, current_pos)
        else:
            fallback_pos = (x + int(15 * s), y + int(25 * s))
            fallback_size = (int(32 * s), int(32 * s))
            pygame.draw.rect(screen, (255, 0, 255), fallback_pos + fallback_size, 1)
        
        # ==========================================
        # 4. POBIERANIE STATYSTYK I TAGÓW
        # ==========================================
        # Odczytujemy tag "ranged" bezpośrednio z bazy, więc działa wszędzie idealnie!
        is_ranged = "ranged" in base_stats.get("tags", [])

        u_hp = get_v('hp')
        u_max_hp = get_v('max_hp')
        if u_max_hp == 0: u_max_hp = 100 
        
        atk_val = get_v('attack')
        def_val = get_v('defense')
        mor_val = get_v('morale')
        fat_val = get_v('fatigue') 
        mov_val = int(get_v('moves', 'move_points') or 0)

        # Rysowanie polskiej nazwy
        # Rysowanie polskiej nazwy (WYCENTROWANE)
        name_surf = self.font_main.render(name_str, True, (255, 255, 255))
        
        # Obliczamy środek ramki (piksel 126 z uwzględnieniem skali)
        center_x = x + int(126 * s)
        
        # Tworzymy prostokąt z wyśrodkowanym X i nakładamy na ekran
        name_rect = name_surf.get_rect(centerx=center_x, top=y + int(3 * s))
        screen.blit(name_surf, name_rect)
        # Miecz HP
        self.draw_health_sword(screen, x + int(42 * s), y + int(0 * s), u_hp, u_max_hp)

        # ==========================================
        # 5. GÓRNY RZĄD LICZB
        # ==========================================
        screen.blit(self.font_stats.render(str(mov_val), True, (255, 255, 255)), (x + int(90 * s), y + int(50 * s)))
        screen.blit(self.font_stats.render(str(mor_val), True, (255, 255, 255)), (x + int(133 * s), y + int(50 * s)))
        screen.blit(self.font_stats.render(str(fat_val), True, (255, 255, 0)),   (x + int(180 * s), y + int(50 * s)))

        # ==========================================
        # 6. DOLNY RZĄD LICZB (Atak, Obrona)
        # ==========================================
        screen.blit(self.font_stats.render(str(def_val), True, (255, 255, 255)), (x + int(133 * s), y + int(95 * s)))

        melee_val = base_stats.get("melee_attack", 0) 

        if is_ranged and melee_val > 0:
            # HYBRYDA (OBA ATAKI)
            screen.blit(self.font_stats.render(str(melee_val), True, (255, 255, 255)), (x + int(90 * s), y + int(68 * s)))
            screen.blit(self.font_stats.render(str(atk_val), True, (255, 255, 255)), (x + int(90 * s), y + int(95 * s)))
        elif is_ranged:
            # TYLKO STRZAŁ
            screen.blit(self.icon_ranged, (x + int(62 * s), y + int(65 * s)))
            screen.blit(self.font_stats.render(str(atk_val), True, (255, 255, 255)), (x + int(90 * s), y + int(95 * s)))
        else:
            # TYLKO WALKA WRĘCZ
            screen.blit(self.icon_melee, (x + int(62 * s), y + int(65 * s)))
            screen.blit(self.font_stats.render(str(atk_val), True, (255, 255, 255)), (x + int(90 * s), y + int(95 * s)))

    def draw_health_sword(self, screen, x, y, hp, max_hp):
        # self.sword_full to u nas "szary miecz" (miecz obrażeń/śmierci)
        full_h = self.sword_full.get_height()
        
        # Zabezpieczenie przed dzieleniem przez zero i błędnymi wartościami
        if max_hp <= 0: max_hp = 1 
        ratio = max(0, min(hp / max_hp, 1)) 
        
        # Obliczamy wskaźnik OBRAŻEŃ (od 0.0 dla pełnego HP do 1.0 dla martwego)
        damage_ratio = 1.0 - ratio
        draw_h = int(full_h * damage_ratio)
        
        # Rysujemy szary miecz tylko, jeśli jednostka ma jakiekolwiek obrażenia
        if draw_h > 0:
            # Tworzymy prostokąt, który ucina obrazek od samej góry (0, 0)
            area = pygame.Rect(0, 0, self.sword_full.get_width(), draw_h)
            # Rysujemy w dokładnie tych samych koordynatach X i Y, bez przesunięć w dół
            screen.blit(self.sword_full, (x, y), area)


    if __name__ == "__main__":
        import subprocess, sys, os
        main_path = os.path.join(os.path.dirname(__file__), "main.py")
        subprocess.run([sys.executable, main_path])
        