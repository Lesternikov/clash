class Player:
    # Dodajemy 'faction' jako argument (domyślnie "catholic")
    def __init__(self, player_id, name, color, color_name="Nieznany", faction="catholic"):
        self.id = player_id
        self.name = name
        self.color = color           # To zostaje dla UI (RGB)
        self.color_name = color_name # To dodajemy dla silnika graficznego (tekst)
        self.faction = faction       # <--- CZYSTE PRZYPISANIE FRAKCJI
        
        # zasoby / statystyki
        self.victories = 0
        self.defeats = 0
        self.queen_favor = 0
        self.gold = 500              # Złoto startowe
        self.income = 0

        self.army = 0
        self.wins = 0
        self.losses = 0
        self.castles = []
        self.units = []
        
        # --- STATYSTYKI DO PASKÓW ---
        self.stat_health = 80       # np. od 0 do 100
        self.stat_mana = 40         # np. od 0 do 100
        self.stat_morale = 100      # np. od 0 do 100
        
        # --- MECHANIKA KRÓLOWEJ ---
        self.has_queen = False
        self.queen_mood = "Szczęśliwa"
        self.queen_timer = 0        # Odliczanie do następnego żądania złota
        
    def try_spawn_general(self):
        if self.queen_favor >= 100:
            self.queen_favor = 0
            return General(self)

