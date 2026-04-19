class Player:
    def __init__(self, player_id, name, color, color_name="red"):
        self.id = player_id
        self.name = name
        self.color = color           # To zostaje dla UI (RGB)
        self.color_name = color_name # To dodajemy dla silnika graficznego (tekst)
        # zasoby / statystyki
        self.victories = 0
        self.defeats = 0
        self.queen_favor = 0
        # ekonomia
        self.gold = 1000
        self.income = 0

        # statystyki
        self.army = 0
        self.wins = 0
        self.losses = 0
        # własności
        self.castles = []
        self.units = []

    def try_spawn_general(self):
        if self.queen_favor >= 100:
            self.queen_favor = 0
            return General(self)

