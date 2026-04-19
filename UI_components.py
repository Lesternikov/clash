import pygame
import main
from settings import UNIT_STATS, UNIT_NAMES


class UnitInfoWindow:
    def __init__(self):
        self.scale = 1.15  # Nasz mnożnik powiększenia

        # Funkcja pomocnicza do ładowania i skalowania
        def load_scaled(path):
            img = pygame.image.load(path).convert_alpha()
            w, h = img.get_size()
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
        self.font_stats = pygame.font.SysFont("Arial", 16, bold=True)

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
        s = self.scale # Skrót dla czytelności kodu

        screen.blit(self.bg_combat, (x, y))

        # --- LOGIKA PORTRETU (ANIMACJA) ---
        frame_idx = (pygame.time.get_ticks() // 150) % 8
        portrait_img = None

        # A. Jeśli to żywa jednostka na mapie (ma gotowe sprites)
        if hasattr(unit, 'sprites') and unit.sprites:
            portrait_img = unit.sprites[frame_idx]
        
        # B. Jeśli to menu rekrutacji (unit to słownik lub nie ma sprites)
        else:
            # Pobieramy kod (np. "INFL") zależnie od tego czy to dict czy obiekt
            u_code = unit.get('type_code') if isinstance(unit, dict) else getattr(unit, 'type_code', None)
            
            if u_code:
                # Szukamy grafiki dla gracza 1 (czerwony) jako podgląd
                # Możesz zmienić "1" na dynamiczny kolor: getattr(self, 'current_player', 0) + 1
                path = f"assets/minimum/{u_code}1_I_S32/{u_code}1_I_S32_{frame_idx}.png"
                if os.path.exists(path):
                    try:
                        raw_img = pygame.image.load(path).convert_alpha()
                        # Skalujemy o 1.15 tak jak resztę UI
                        w, h = raw_img.get_size()
                        portrait_img = pygame.transform.smoothscale(raw_img, (int(w * s), int(h * s)))
                    except:
                        pass

        # RYSOWANIE PORTRETU
        if portrait_img:
            screen.blit(portrait_img, (x + int(15 * s), y + int(25 * s)))
        else:
            # Fallback: Różowy kwadrat jeśli pliku nie ma wcale
            pygame.draw.rect(screen, (255, 0, 255), (x + int(15 * s), y + int(25 * s), int(32 * s), int(32 * s)), 1)

        # 1. Wewnętrzna funkcja pomocnicza do bezpiecznego wyciągania danych
        def get_v(key, attr_name=None):
            if isinstance(unit, dict):
                return unit.get(key, 0)
            return getattr(unit, attr_name if attr_name else key, 0)

        # 2. Wyciąganie statystyk z użyciem get_v
        u_code = get_v('type_code') if isinstance(unit, dict) else getattr(unit, 'type_code', 'Unknown')
        
        # Ty decydujesz, że Max HP jest równe, więc dajemy np. stałe 100, ale hp wyciągamy
        u_hp = get_v('hp')
        u_max_hp = get_v('max_hp')
        if u_max_hp == 0: u_max_hp = 100 # Zabezpieczenie przed dzieleniem przez zero
        
        atk_val = get_v('attack')
        def_val = get_v('defense')
        mor_val = get_v('morale')
        exp_val = get_v('experience')
        
        moves_raw = get_v('moves', 'move_points')
        mov_val = int(moves_raw) if moves_raw is not None else 0

        # 3. Rysowanie Tła
        screen.blit(self.bg_combat, (x, y))

        # 4. Nazwa
        name_str = UNIT_NAMES.get(u_code, "Nieznany")
        name_surf = self.font_main.render(name_str, True, (255, 255, 255))
        screen.blit(name_surf, (x + int(100 * s), y + int(6 * s)))

        # 5. Miecz HP i Portret
        # Zmieniłem x+60 dla miecza, żeby był bliżej portretu. Dopasuj to w razie potrzeby!
        self.draw_health_sword(screen, x + int(42 * s), y + int(0 * s), u_hp, u_max_hp)
        
        frame_idx = (pygame.time.get_ticks() // 150) % 8
        
        # ==========================================
        # 6. LOGIKA NADPISYWANIA IKON (Atak, Morale, Exp)
        # ==========================================
        
        # --- ATAK ---
        # Domyślnie tło ma ŁUK+RĘKĘ (mixed). Nie rysujemy nic dla jednostek strzelająco-walczących.
        ranged_only = ["KATAP", "ARMAT"] 
        # UWAGA: Tu musisz wypisać jednostki, które NIE strzelają (tylko miecz/pika)
        melee_only = ["SPRL","SPRH","INFL","INFH","CAVL","CAVH","RYC","TARAN","PEON","GORAL","BUDOW","WORM","SLON","TROL","SCORP","SZK","DUCH","ORZEL","PEGAZ","WAZKA"] 
        
        if u_code in ranged_only:
            screen.blit(self.icon_ranged, (x + 120, y + 45))
        elif u_code in melee_only:
            screen.blit(self.icon_melee, (x + 71, y + 75))
        # else: nic nie blitujemy, tło robi robotę!

        # --- MORALE ---
        # Domyślnie tło ma ŚREDNIE morale. Rysujemy ikonę tylko gdy jest niskie lub wysokie.
        # Załóżmy, że średnie to przedział 40-60.
        if mor_val < 40:
            # Wymaga dodania self.icon_morale_low w __init__
            pass # screen.blit(self.icon_morale_low, (x + X, y + Y))
        elif mor_val > 60:
            # Wymaga dodania self.icon_morale_high w __init__
            pass # screen.blit(self.icon_morale_high, (x + X, y + Y))

        # --- DOŚWIADCZENIE (EXP) ---
        # Domyślnie tło ma podstawowe ubranie/posąg.
        if exp_val >= 100: # Jakiś próg dla "Weterana"
            pass # screen.blit(self.icon_exp_veteran, (x + X, y + Y))
        elif exp_val >= 250: # Próg dla "Elity"
            pass # screen.blit(self.icon_exp_elite, (x + X, y + Y))

        # ==========================================
        # 7. WYSWIETLANIE SAMYCH LICZB W OKIENKACH
        # ==========================================

        # Poniższe współrzędne (X+..., Y+...) to czysty strzał. 
        # Zmieniaj je o kilka pikseli góra/dół, żeby trafić idealnie w puste kratki Twojej grafiki!
        
        font = self.font_stats # Systemowa lub wczytana czcionka do liczb

        # ATK i DEF (Pierwsza kolumna)
        screen.blit(self.font_stats.render(str(atk_val), True, (255, 255, 255)), 
                    (x + int(165 * s), y + int(55 * s)))
        screen.blit(self.font_stats.render(str(def_val), True, (255, 255, 255)), (x + int(165 * s), y + int(85 * s)))

        # HP i MORALE (Druga kolumna)
        screen.blit(self.font_stats.render(str(u_hp), True, (255, 255, 255)), (x + int(225 * s), y + int(55 * s)))
        screen.blit(self.font_stats.render(str(mor_val), True, (255, 255, 255)), (x + int(225 * s), y + int(85 * s)))

        # MOVES (Trzecia kolumna, góra)
        screen.blit(self.font_stats.render(str(mov_val), True, (255, 255, 255)), (x + int(285 * s), y + int(55 * s)))

        # EXP / ATC (Trzecia kolumna, dół)
        if not isinstance(unit, dict):
            # Jeśli klikasz na mapie -> pokazujemy Doświadczenie (na żółto)
            screen.blit(self.font_stats.render(str(exp_val), True, (255, 255, 0)), (x + int(285 * s), y + int(85 * s)))
        else:
            # Jeśli koszary -> pokazujemy ATC na biało (wg Twojego dawnego planu)
            screen.blit(self.font_stats.render(str(atk_val), True, (255, 255, 255)), (x + int(285 * s), y + int(85 * s)))

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