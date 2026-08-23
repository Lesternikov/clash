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
        exp_zloto_path  = os.path.join("assets", "minimum", "INFO_S32", "INFO_S32_8.png") # Złoto (9-12)
        
        # Ładujemy posągi używając load_scaled
        self.icon_exp_tier0 = load_scaled(exp_szmata_path)
        self.icon_exp_tier1 = load_scaled(exp_braz_path)
        self.icon_exp_tier2 = None
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

        # --- ZMIENIONE: Ładowanie grafik dla PROSTEGO panelu (Generał, Złoto, Chłopi) ---
        self.bg_simple = load_scaled("assets/minimum/INFO_S32/INFO_S32_24.png") # Puste tło z 3 okienkami
        
        # Ikony do prawego okienka:
        self.icon_peas_right = load_scaled("assets/minimum/INFO_S32/INFO_S32_25.png")
        self.icon_gold_right = load_scaled("assets/minimum/INFO_S32/INFO_S32_26.png")
        self.icon_gen_right  = load_scaled("assets/minimum/INFO_S32/INFO_S32_28.png")
        
        # Ikona ruchu (Biegnący ludzik do środkowego okienka) 
        # ZMIEŃ NUMER NA WŁAŚCIWY, jeśli 25 to chłopi! Zakładam np. 27
        self.icon_moves_simple = load_scaled("assets/minimum/INFO_S32/INFO_S32_27.png")

        # Ładowanie przeskalowanych teł
        self.bg_combat = load_scaled("assets/minimum/INFO_S32/INFO_S32_0.png")
        self.bg_simple = load_scaled("assets/minimum/INFO_S32/INFO_S32_24.png") # Tło z okienkami dla Generała/Złota
        self.bg_enemy  = load_scaled("assets/minimum/INFO_S32/INFO_S32_1.png")  # Gładkie tło dla Wroga (TO, KTÓRE PRZESŁAŁEŚ)
        self.sword_full = load_scaled("assets/minimum/INFO_S32/INFO_S32_2.png")

    def draw(self, screen, x, y, unit, mode):
        if mode == "ENEMY":
            self.draw_enemy_info(screen, x, y, unit)
        elif mode == "SIMPLE":
            self.draw_simple_info(screen, x, y, unit)
        else:
            self.draw_combat_info(screen, x, y, unit)

    def draw_simple_info(self, screen, x, y, unit):
        s = self.scale
        
        # 1. Tło (INFO 24)
        screen.blit(self.bg_simple, (x, y))
        
        u_code = unit.get('type_code') if isinstance(unit, dict) else getattr(unit, 'type_code', getattr(unit, 'type', "Unknown"))
        name_str = UNIT_NAMES.get(u_code, getattr(unit, 'type', "Nieznany"))
        
        # 2. Nazwa na samej górze (wyśrodkowana)
        name_txt = self.font_main.render(name_str, True, (255, 255, 255))
        name_rect = name_txt.get_rect(centerx=x + int(126 * s), top=y + int(3 * s))
        screen.blit(name_txt, name_rect)

        # 3. LEWE OKIENKO: Grafika (Sprite) postaci
        frame = (pygame.time.get_ticks() // 150) % 8
        if hasattr(unit, 'sprites') and unit.sprites:
            sprite_img = unit.sprites[frame % len(unit.sprites)]
            sprite_scaled = pygame.transform.scale(sprite_img, (int(sprite_img.get_width() * 1.5), int(sprite_img.get_height() * 1.5)))
            # Rysujemy ludzika w lewym slocie
            screen.blit(sprite_scaled, (x + int(10 * s), y + int(35 * s)))

        # 4. ŚRODKOWE OKIENKO: Ruchy (PA)
        screen.blit(self.icon_moves_simple, (x + int(60 * s), y + int(35 * s)))
        moves_val = str(getattr(unit, 'moves', getattr(unit, 'move_points', 0)))
        moves_txt = self.font_stats.render(moves_val, True, (255, 255, 255))
        screen.blit(moves_txt, (x + int(85 * s), y + int(45 * s)))

        # 5. PRAWE OKIENKO: Unikalna grafika i wartość
        icon_right, val_str, val_color = None, "0", (255, 255, 255)
        
        # Konfiguracja w zależności od typu
        if u_code == "Generał" or name_str == "Generał":
            icon_right = self.icon_gen_right
            val_str = str(int(getattr(unit, 'hp', 100))) # HP Generała
            val_color = (255, 255, 255)
        elif u_code == "GOLD" or name_str == "Złoto":
            icon_right = self.icon_gold_right
            val_str = str(int(getattr(unit, 'amount', getattr(unit, 'hp', 0)))) # Złoto korzysta z HP
            val_color = (255, 215, 0)
        elif u_code == "PEAS" or name_str == "Chłopi":
            icon_right = self.icon_peas_right
            val_str = str(int(getattr(unit, 'count', getattr(unit, 'hp', 0)))) 
            val_color = (200, 200, 200)

        # Rysowanie prawej strony
        if icon_right:
            screen.blit(icon_right, (x + int(115 * s), y + int(30 * s)))
            val_txt = pygame.font.SysFont("Times New Roman", 40, bold=True).render(val_str, True, val_color)
            val_shadow = pygame.font.SysFont("Times New Roman", 40, bold=True).render(val_str, True, (0,0,0))
            
            # Wyśrodkowanie wielkiej liczby na ikonie
            txt_x = x + int(140 * s) + (icon_right.get_width() // 2) - (val_txt.get_width() // 2)
            txt_y = y + int(50 * s)
            screen.blit(val_shadow, (txt_x + 2, txt_y + 2))
            screen.blit(val_txt, (txt_x, txt_y))


    def draw_combat_info(self, screen, x, y, unit):
        s = self.scale
        # =========================================================
        # PRZECHWYCENIE: Wymuszenie małego panelu 
        # =========================================================
        nazwa = getattr(unit, 'type', '')
        # Sprawdzamy czy to jednostka "gospodarcza / specjalna"
        if nazwa in ["Generał", "Złoto", "Chłopi"] or getattr(unit, 'type_code', '') in ["GOLD", "PEAS"]:
            self.draw_simple_info(screen, x, y, unit)
            return # Przerywamy i NIE RYSUJEMY reszty wielkiego panelu!
        
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
        fat_val = get_v('fatigue') 
        mov_val = int(get_v('moves', 'move_points') or 0)
        
        # ---> ZMIANA 1: Morale ZAWSZE pobierane prosto z settings.py (UNIT_STATS) <---
        mor_val = base_stats.get('morale', 10)
        
        # POBIERAMY DOŚWIADCZENIE
        exp_val = int(get_v('experience', default=0)) 

        # Rysowanie polskiej nazwy (WYCENTROWANE)
        name_surf = self.font_main.render(name_str, True, (255, 255, 255))
        center_x = x + int(126 * s)
        name_rect = name_surf.get_rect(centerx=center_x, top=y + int(3 * s))
        screen.blit(name_surf, name_rect)
        
        # ---> ZMIANA 2: Sprawdzamy czy jednostka stoi na mapie świata <---
        # W garnizonie zmienialiśmy jej koordynaty na (-1, -1), a w koszarach to często "słownik".
        is_on_map = False
        if not isinstance(unit, dict):
            if getattr(unit, 'x', -1) >= 0 and getattr(unit, 'y', -1) >= 0:
                is_on_map = True
                
        # Miecz HP (przekazujemy nową flagę show_hp_text)
        self.draw_health_sword(screen, x + int(42 * s), y + int(0 * s), u_hp, u_max_hp, show_hp_text=is_on_map)

       # === Portret (Dynamiczny kolor gracza) ===
        frame_idx = (pygame.time.get_ticks() // 150) % 8
        raw_img = None
        if u_code:
            # 1. Ustalamy ID koloru właściciela
            color_id = 1 # Domyślnie ładujemy czerwony (np. jako podgląd w koszarach)
            owner = getattr(unit, 'owner', None)
            
            if owner:
                c_name = getattr(owner, 'color_name', '').lower()
                if c_name == 'blue': color_id = 2
                elif c_name == 'yellow': color_id = 3
                elif c_name == 'white': color_id = 4
                elif c_name == 'green': color_id = 5

            # 2. Sklejamy ścieżkę z właściwym numerem (zamiast sztywnego "1")
            path = f"assets/minimum/{u_code}{color_id}_I_S32/{u_code}{color_id}_I_S32_{frame_idx}.png"
            
            if os.path.exists(path):
                try:
                    raw_img = pygame.image.load(path).convert_alpha()
                except:
                    pass
            
            # 3. System awaryjny (Fallback)
            # Jeśli np. zapomniałeś dodać do folderu białych portretów jakiejś jednostki,
            # gra awaryjnie załaduje domyślny czerwony portret, żeby uniknąć wywalenia błędu!
            if not raw_img:
                fallback_path = f"assets/minimum/{u_code}1_I_S32/{u_code}1_I_S32_{frame_idx}.png"
                if os.path.exists(fallback_path):
                    try:
                        raw_img = pygame.image.load(fallback_path).convert_alpha()
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
        
        # A. Rysujemy posąg (Tylko jeśli to nie srebro, bo srebro to tło!)
        current_exp_icon = self.get_experience_icon(exp_val)
        if current_exp_icon:
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

    def draw_enemy_info(self, screen, x, y, unit):
        # 1. Rysujemy tło dedykowane TYLKO dla WROGA (INFO_S32_1.png)
        screen.blit(self.bg_enemy, (x, y))
        
        s = self.scale
        u_code = unit.get('type_code') if isinstance(unit, dict) else getattr(unit, 'type_code', getattr(unit, 'type', "Unknown"))
        name_str = UNIT_NAMES.get(u_code, getattr(unit, 'type', "Nieznany"))
        
        # Pobieramy szerokość i wysokość tego konkretnego tła do idealnego wyśrodkowania
        bg_w = self.bg_enemy.get_width()
        bg_h = self.bg_enemy.get_height()
        
        # 2. Rysujemy TYLKO NAZWĘ na górze
        name_txt = self.font_main.render(name_str, True, (255, 255, 255))
        name_rect = name_txt.get_rect(centerx=x + (bg_w // 2), top=y + int(5 * s))
        screen.blit(name_txt, name_rect)

        # === Portret (Dynamiczny kolor gracza) ===
        frame_idx = (pygame.time.get_ticks() // 150) % 8
        raw_img = None
        if u_code:
            # 1. Ustalamy ID koloru właściciela
            color_id = 1 # Domyślnie ładujemy czerwony (np. jako podgląd w koszarach)
            owner = getattr(unit, 'owner', None)
            
            if owner:
                c_name = getattr(owner, 'color_name', '').lower()
                if c_name == 'blue': color_id = 2
                elif c_name == 'yellow': color_id = 3
                elif c_name == 'white': color_id = 4
                elif c_name == 'green': color_id = 5

            # 2. Sklejamy ścieżkę z właściwym numerem (zamiast sztywnego "1")
            path = f"assets/minimum/{u_code}{color_id}_I_S32/{u_code}{color_id}_I_S32_{frame_idx}.png"
            
            if os.path.exists(path):
                try:
                    raw_img = pygame.image.load(path).convert_alpha()
                except:
                    pass
            
            # 3. System awaryjny (Fallback)
            # Jeśli np. zapomniałeś dodać do folderu białych portretów jakiejś jednostki,
            # gra awaryjnie załaduje domyślny czerwony portret, żeby uniknąć wywalenia błędu!
            if not raw_img:
                fallback_path = f"assets/minimum/{u_code}1_I_S32/{u_code}1_I_S32_{frame_idx}.png"
                if os.path.exists(fallback_path):
                    try:
                        raw_img = pygame.image.load(fallback_path).convert_alpha()
                    except:
                        pass

        if raw_img:
            t_size = (int(37 * s), int(65 * s)) 
            portrait_img = pygame.transform.scale(raw_img, t_size)
            current_pos = (x + int(8 * s), y + int(7 * s))
            screen.blit(portrait_img, current_pos)


    def draw_health_sword(self, screen, x, y, hp, max_hp, show_hp_text=False):
        # Logika paska zdrowia (szary miecz) - zostawiamy bez zmian
        full_h = self.sword_full.get_height()
        if max_hp <= 0: max_hp = 1 
        ratio = max(0, min(hp / max_hp, 1)) 
        damage_ratio = 1.0 - ratio
        draw_h = int(full_h * damage_ratio)
        if draw_h > 0:
            area = pygame.Rect(0, 0, self.sword_full.get_width(), draw_h)
            screen.blit(self.sword_full, (x, y), area)

        # ---> ZMIANA 3: Rysowanie tekstu TYLKO na mapie świata <---
        if show_hp_text:
            hp_obecne = int(hp)
            hp_max = int(max_hp)
            font_hp = pygame.font.SysFont("Arial", 16, bold=True)
            txt_hp = font_hp.render(f"{hp_obecne} / {hp_max}", True, (255, 255, 255))
            txt_hp_cien = font_hp.render(f"{hp_obecne} / {hp_max}", True, (0, 0, 0))
            
            # Wyśrodkowanie tekstu względem miecza
            txt_x = x + (self.sword_full.get_width() // 2) - (txt_hp.get_width() // 2)
            txt_y = y + full_h + 2  # Trochę pod rękojeścią
            
            screen.blit(txt_hp_cien, (txt_x + 1, txt_y + 1)) # Cień
            screen.blit(txt_hp, (txt_x, txt_y))              # Główny tekst

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

        