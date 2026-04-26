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

        screen.blit(self.bg_combat, (x, y))

        # --- LOGIKA PORTRETU (ANIMACJA) ---
        frame_idx = (pygame.time.get_ticks() // 150) % 8
        portrait_img = None

        # A. Jeśli to żywa jednostka na mapie (ma gotowe sprites)
        if hasattr(unit, 'sprites') and unit.sprites:
            raw_img = unit.sprites[frame_idx]
           # --- JEDNOLITE RYSOWANIE I SKALOWANIE ---
        if raw_img:
            # 1. Definiujemy sztywny rozmiar bazy (np. 36 pikseli). 
            # Jeśli ludzik jest za duży/mały na tle innych ikon w oknie, zmień po prostu tę liczbę (np. na 32 lub 40).
            base_size = 36 
            
            # 2. Mnożymy to przez Twoją idealną skalę (1.6)
            target_size = (int(base_size * s), int(base_size * s)) 
            
            # 3. Przeskalowujemy bez względu na to, skąd przyszedł obrazek!
            portrait_img = pygame.transform.scale(raw_img, target_size)
            
            # 4. Rysujemy na ekranie
            screen.blit(portrait_img, (x + int(15 * s), y + int(25 * s)))
        else:
            # Fallback: Różowy kwadrat
            pygame.draw.rect(screen, (255, 0, 255), (x + int(15 * s), y + int(25 * s), int(32 * s), int(32 * s)), 1)
            # 1. Pobieranie danych
        def get_v(key, attr_name=None, default=0):
            if isinstance(unit, dict):
                return unit.get(key, default)
            return getattr(unit, attr_name if attr_name else key, default)

        # --- NIEZAWODNE POBIERANIE NAZWY I KODU ---
        # Sprawdzamy surowy identyfikator (może to być polskie "Łucznik" lub kod "ARCH")
        if isinstance(unit, dict):
            raw_id = unit.get('type_code', 'Unknown')
        else:
            raw_id = getattr(unit, 'type_code', getattr(unit, 'type', 'Unknown'))

        # Jeśli raw_id to polska nazwa (np. "Łucznik"), NAME_TO_CODE zamieni to na "ARCH"
        # Jeśli to już jest "ARCH", get() zwróci wartość domyślną, czyli zostawi "ARCH"
        u_code = NAME_TO_CODE.get(raw_id, raw_id)

        # Pobieranie Tagi (zabezpieczenie na wypadek, gdyby ich nie było)
        if isinstance(unit, dict):
            tags = unit.get('tags', [])
        else:
            tags = getattr(unit, 'tags', [])
            
        is_ranged = "ranged" in tags

        u_hp = get_v('hp')
        u_max_hp = get_v('max_hp')
        if u_max_hp == 0: u_max_hp = 100 
        
        # Pobieranie dwóch wartości ataku 
        atk_val = get_v('attack')
        melee_val = get_v('melee_attack') 
        
        def_val = get_v('defense')
        mor_val = get_v('morale')
        fat_val = get_v('fatigule')
        mov_val = int(get_v('moves', 'move_points') or 0)

        # 2. Tytuł (Nazwa jednostki)
        # Zawsze pobieramy ładną, polską nazwę na podstawie u_code (np. ARCH -> Łucznik)
        name_str = UNIT_NAMES.get(u_code, raw_id)
        name_surf = self.font_main.render(name_str, True, (255, 255, 255))
        screen.blit(name_surf, (x + int(100 * s), y + int(6 * s)))

        # 3. Miecz HP
        self.draw_health_sword(screen, x + int(42 * s), y + int(0 * s), u_hp, u_max_hp)

        # ==========================================
        # 4. GÓRNY RZĄD (Ruch, Morale, Doświadczenie)
        # ==========================================
        # Zmieniaj mnożniki przy 's' aby przesuwać tekst precyzyjnie w lewo/prawo i góra/dół
        
        # Ruch (Górny lewy)
        screen.blit(self.font_stats.render(str(mov_val), True, (255, 255, 255)), (x + int(90 * s), y + int(50 * s)))
        
        # Morale (Górny środek)
        screen.blit(self.font_stats.render(str(mor_val), True, (255, 255, 255)), (x + int(133 * s), y + int(50 * s)))
        
        # Doświadczenie (Górny prawy)
        screen.blit(self.font_stats.render(str(fat_val), True, (255, 255, 0)),   (x + int(180 * s), y + int(50 * s)))

       # ==========================================
        # 5. DOLNY RZĄD (Atak, Obrona)
        # ==========================================
        
        # 1. Najpierw pobieramy OBRONĘ (środkowa kolumna na dole)
        def_val = get_v('defense')
        screen.blit(self.font_stats.render(str(def_val), True, (255, 255, 255)), (x + int(133 * s), y + int(95 * s)))

        # 2. POBIERAMY DANE Z SETTINGS NA BAZIE NAZWY (np. "Kusznik")
        # To jest kluczowe: raw_id to polska nazwa jednostki
        base_stats = UNIT_STATS.get(raw_id, {})
        
        # Sprawdzamy tagi i wartości ataku bezpośrednio ze słownika
        is_ranged = "ranged" in base_stats.get("tags", [])
        melee_val = base_stats.get("melee_attack", 0) # Dla Kusznika to będzie 5
        atk_val = get_v('attack')                     # Główny atak (dla Kusznika 40)

        # --- LOGIKA DYNAMICZNYCH IKON I LICZB ---
        # Przypominam: Podstawowe tło bg_combat ma już narysowaną RĘKĘ i ŁUK.
        
        if is_ranged and melee_val > 0:
            # SCENARIUSZ: OBA ATAKI (np. Kusznik)
            # Nie nakładamy żadnych ikon (patchy), bo tło ma już obie.
            
            # Liczba przy RĘCE (Góra) - melee_val
            screen.blit(self.font_stats.render(str(melee_val), True, (255, 255, 255)), (x + int(90 * s), y + int(68 * s)))
            
            # Liczba przy ŁUKU (Dół) - atk_val
            screen.blit(self.font_stats.render(str(atk_val), True, (255, 255, 255)), (x + int(90 * s), y + int(95 * s)))

        elif is_ranged:
            # SCENARIUSZ: TYLKO STRZAŁ (np. Katapulta)
            # Nakładamy ikonę "tylko łuk", żeby zakryć ramię na tle
            screen.blit(self.icon_ranged, (x + int(62 * s), y + int(65 * s)))
            # Wypisujemy główny atak na środku ramki
            screen.blit(self.font_stats.render(str(atk_val), True, (255, 255, 255)), (x + int(90 * s), y + int(95 * s)))

        else:
            # SCENARIUSZ: TYLKO WRĘCZ (np. Lekka piechota)
            # Nakładamy ikonę "tylko ramię", żeby zakryć łuk na tle
            screen.blit(self.icon_melee, (x + int(62 * s), y + int(65 * s)))
            # Wypisujemy główny atak na środku ramki
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
        