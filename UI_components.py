import os
import pygame
from settings import UNIT_STATS, UNIT_NAMES, NAME_TO_CODE

class UnitInfoWindow:
    def __init__(self):
        self.scale = 1.6  # Nasz mnożnik powiększenia

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
        
        # Ikony podstawowe
        self.icon_moves = load_scaled("assets/minimum/INFO_S32/INFO_S32_25.png")
        self.icon_gold = load_scaled("assets/minimum/INFO_S32/INFO_S32_28.png")
        self.icon_amount = load_scaled("assets/minimum/INFO_S32/INFO_S32_24.png")
        self.icon_heart = load_scaled("assets/minimum/INFO_S32/INFO_S32_26.png")
        
        # === DYNAMICZNE IKONY DOŚWIADCZENIA (Posągi) ===
        # Ścieżki do posągów (zgodnie z Twoim mapowaniem pliku)
        exp_szmata_path = os.path.join("assets", "minimum", "INFO_S32", "INFO_S32_6.png") # Szmata (0-2)
        exp_braz_path   = os.path.join("assets", "minimum", "INFO_S32", "INFO_S32_7.png") # Brąz (3-5)
        exp_srebro_path = os.path.join("assets", "minimum", "INFO_S32", "INFO_S32_0.png") # Srebro (6-8)
        exp_zloto_path  = os.path.join("assets", "minimum", "INFO_S32", "INFO_S32_8.png") # Złoto (9-12)
        
        # Ładujemy posągi używając load_scaled
        self.icon_exp_tier0 = load_scaled(exp_szmata_path)
        self.icon_exp_tier1 = load_scaled(exp_braz_path)
        self.icon_exp_tier2 = load_scaled(exp_srebro_path)
        self.icon_exp_tier3 = load_scaled(exp_zloto_path)
        
       # === MIECZYKI POSTĘPU DOŚWIADCZENIA ===
        mieczyk_path = os.path.join("assets", "minimum", "INFO_S32", "INFO_S32_14.png")
        if os.path.exists(mieczyk_path):
            self.icon_mieczyk = load_scaled(mieczyk_path)
        else:
            self.icon_mieczyk = None
            print(f"DEBUG: Brak pliku mieczyków: {mieczyk_path}")

        # Atak / Obrona / Ranged
        self.icon_melee = load_scaled("assets/minimum/INFO_S32/INFO_S32_9.png")
        self.icon_ranged = load_scaled("assets/minimum/INFO_S32/INFO_S32_10.png")
        
        # Czcionki
        self.font_main = pygame.font.SysFont("Times New Roman", 23, bold=True)
        self.font_stats = pygame.font.SysFont("Arial", 24, bold=True)

    def draw(self, screen, x, y, unit, mode):
        if mode == "SIMPLE":
            self.draw_simple_info(screen, x, y, unit)
        else:
            self.draw_combat_info(screen, x, y, unit)

    def draw_simple_info(self, screen, x, y, unit):
        screen.blit(self.bg_simple, (x, y))
        
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
        moves_txt = self.font_stats.render(str(getattr(unit, 'moves', getattr(unit, 'move_points', 0))), True, (255, 255, 255))
        screen.blit(moves_txt, (x + 50, y + 115))

        # Specjalna wartość po prawej
        icon, val = None, 0
        if u_code == "GOLD":
            icon, val = self.icon_gold, getattr(unit, 'amount', 0)
        elif u_code == "PEAS":
            icon, val = self.icon_amount, getattr(unit, 'count', 0)
        elif u_code in ["SPECK", "SPECM"]:
            icon, val = self.icon_heart, getattr(unit, 'hp', 0)
            
        if icon:
            screen.blit(icon, (x + 140, y + 40))
            val_txt = self.font_stats.render(str(val), True, (255, 215, 0))
            screen.blit(val_txt, (x + 180, y + 45))

    def draw_combat_info(self, screen, x, y, unit):
        s = self.scale

        # ==========================================
        # 1. TŁO (CZARNE KRYCIE)
        # ==========================================
        bg_w, bg_h = self.bg_combat.get_size()
        pygame.draw.rect(screen, (0, 0, 0), (x, y, bg_w, bg_h)) 
        screen.blit(self.bg_combat, (x, y))

        # ==========================================
        # 2. POBIERANIE DANYCH JEDNOSTKI
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
        base_stats = UNIT_STATS.get(name_str, {})

        # ==========================================
        # 3. STATYSTYKI I TAGI
        # ==========================================
        is_ranged = "ranged" in base_stats.get("tags", [])
        u_hp = get_v('hp')
        u_max_hp = get_v('max_hp')
        if u_max_hp == 0: u_max_hp = 100 
        
        atk_val = get_v('attack')
        def_val = get_v('defense')
        mor_val = get_v('morale')
        fat_val = get_v('fatigue') 
        mov_val = int(get_v('moves', 'move_points') or 0)
        
        # POBIERAMY DOŚWIADCZENIE (ZMIENIONO default na 0)
        exp_val = int(get_v('experience', default=0)) 

        # Rysowanie polskiej nazwy (WYCENTROWANE)
        name_surf = self.font_main.render(name_str, True, (255, 255, 255))
        center_x = x + int(126 * s)
        name_rect = name_surf.get_rect(centerx=center_x, top=y + int(3 * s))
        screen.blit(name_surf, name_rect)
        
        # Miecz HP
        self.draw_health_sword(screen, x + int(42 * s), y + int(0 * s), u_hp, u_max_hp)

        # === Portret (zostawiamy jak jest) ===
        frame_idx = (pygame.time.get_ticks() // 150) % 8
        raw_img = None
        if u_code:
            path = f"assets/minimum/{u_code}1_I_S32/{u_code}1_I_S32_{frame_idx}.png"
            if os.path.exists(path):
                try:
                    raw_img = pygame.image.load(path).convert_alpha()
                except:
                    pass
        if raw_img:
            t_size = (int(37 * s), int(65 * s)) 
            portrait_img = pygame.transform.scale(raw_img, t_size)
            current_pos = (x + int(8 * s), y + int(7 * s))
            screen.blit(portrait_img, current_pos)

        # ==========================================
        # 4. RYSOWANIE POSĄGU I MIECZYKÓW
        # ==========================================
        # Bazowa pozycja posągu (prawy dolny róg statsów)
        statue_x = x + int(150 * s)
        statue_y = y + int(65 * s)
        
        # A. Rysujemy posąg
        current_exp_icon = self.get_experience_icon(exp_val)
        screen.blit(current_exp_icon, (statue_x, statue_y))

        # B. Rysujemy mieczyki postępu (logika +1 oraz limit dla max lvl)
        if self.icon_mieczyk:
            if exp_val >= 12:
                mieczyki_count = 3 # Przy maksymalnym poziomie (Złoto 12) zostają 3 miecze
            else:
                mieczyki_count = (exp_val % 3) + 1 # 0->1, 1->2, 2->3
            
            # Pobieramy wysokość mieczyka, by układać je w równych odstępach w dół
            m_h = self.icon_mieczyk.get_height()
            
            for i in range(mieczyki_count):
                # Przesuwamy o 30 jednostek w prawo od posągu i układamy w pionie (i * wysokość)
                m_x = statue_x + int(30 * s)  
                m_y = statue_y + (i * (m_h + 2)) 
                
                screen.blit(self.icon_mieczyk, (m_x, m_y))

        # ==========================================
        # 5. RZĘDY LICZB (zostawiamy bez zmian)
        # ==========================================
        # Górny rząd
        screen.blit(self.font_stats.render(str(mov_val), True, (255, 255, 255)), (x + int(90 * s), y + int(50 * s)))
        screen.blit(self.font_stats.render(str(mor_val), True, (255, 255, 255)), (x + int(133 * s), y + int(50 * s)))
        screen.blit(self.font_stats.render(str(fat_val), True, (255, 255, 0)),   (x + int(180 * s), y + int(50 * s)))

        # Dolny rząd (Atak, Obrona)
        screen.blit(self.font_stats.render(str(def_val), True, (255, 255, 255)), (x + int(133 * s), y + int(95 * s)))

        # Logika Ataku
        melee_val = base_stats.get("melee_attack", 0) 
        if is_ranged and melee_val > 0:
            screen.blit(self.font_stats.render(str(melee_val), True, (255, 255, 255)), (x + int(90 * s), y + int(68 * s)))
            screen.blit(self.font_stats.render(str(atk_val), True, (255, 255, 255)), (x + int(90 * s), y + int(95 * s)))
        elif is_ranged:
            screen.blit(self.icon_ranged, (x + int(62 * s), y + int(65 * s)))
            screen.blit(self.font_stats.render(str(atk_val), True, (255, 255, 255)), (x + int(90 * s), y + int(95 * s)))
        else:
            screen.blit(self.icon_melee, (x + int(62 * s), y + int(65 * s)))
            screen.blit(self.font_stats.render(str(atk_val), True, (255, 255, 255)), (x + int(90 * s), y + int(95 * s)))

    def draw_health_sword(self, screen, x, y, hp, max_hp):
        # Logika paska zdrowia (szary miecz) - zostawiamy bez zmian
        full_h = self.sword_full.get_height()
        if max_hp <= 0: max_hp = 1 
        ratio = max(0, min(hp / max_hp, 1)) 
        damage_ratio = 1.0 - ratio
        draw_h = int(full_h * damage_ratio)
        if draw_h > 0:
            area = pygame.Rect(0, 0, self.sword_full.get_width(), draw_h)
            screen.blit(self.sword_full, (x, y), area)

    def get_experience_icon(self, experience_level):
        """Zwraca teksturę posągu na podstawie poziomu doświadczenia."""
        if experience_level < 3:
            return self.icon_exp_tier0  # Szmata (0, 1, 2)
        elif experience_level < 6:
            return self.icon_exp_tier1  # Brąz (3, 4, 5)
        elif experience_level < 9:
            return self.icon_exp_tier2  # Srebro (6, 7, 8)
        else:
            return self.icon_exp_tier3  # Złoto/Standard (9, 10, 11, 12)
        
    if __name__ == "__main__":
        import subprocess, sys, os
        main_path = os.path.join(os.path.dirname(__file__), "main.py")
        subprocess.run([sys.executable, main_path])

        