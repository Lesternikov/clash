def resolve_auto_combat(attacker, defender, world):
    """
    Prosty system walki (Auto-Resolve).
    Zwraca True, jeśli ATAKUJĄCY przeżył i zajął pole.
    Zwraca False, jeśli ATAKUJĄCY zginął (ruch zostaje przerwany).
    """
    print(f"\n--- WALKA AUTO: Gracze {attacker.owner.name} vs {defender.owner.name} ---")

    # 1. Rozpakowujemy armie (Lider + jego garnizon)
    attackers = [attacker]
    if hasattr(attacker, 'garrison') and attacker.garrison:
        attackers.extend([u for u in attacker.garrison if u is not None])
        
    defenders = [defender]
    if hasattr(defender, 'garrison') and defender.garrison:
        defenders.extend([u for u in defender.garrison if u is not None])

    len_a = len(attackers)
    len_d = len(defenders)
    print(f"Siły: {len_a} atakujących vs {len_d} obrońców")

    # 2. Kto wygrywa? (Ten, kto ma więcej jednostek. Przy remisie wygrywa atakujący)
    if len_a >= len_d:
        winners = attackers
        losers = defenders
        winner_leader = attacker
        print("=> Atakujący WYGRYWA starcie!")
    else:
        winners = defenders
        losers = attackers
        winner_leader = defender
        print("=> Obrońca WYGRYWA starcie (atak odparty)!")

    # 3. Obliczanie i zadawanie obrażeń
    # Każda przegrana jednostka "zabiera ze sobą" 100 HP, które dzieli się na wygranych
    total_damage = len(losers) * 100
    damage_per_winner = int(total_damage / len(winners))
    
    print(f"Zwycięzcy otrzymują łącznie {total_damage} obrażeń ({damage_per_winner} HP na jednostkę).")

    survivors = []
    for w in winners:
        # Pobieramy obecne życie (domyślnie 100) i odejmujemy rany
        w.hp = getattr(w, 'hp', 100) - damage_per_winner
        if w.hp > 0:
            survivors.append(w)
        else:
            print(f" - Zwycięska jednostka {w.type} zmarła od odniesionych ran.")

    # 4. Totalne czyszczenie z mapy jednostek, które zginęły (Przegrani + polegli Zwycięzcy)
    all_dead = losers + [w for w in winners if w not in survivors]
    
    # Określamy gracza, który wygrał to starcie (to on będzie brał jeńców)
    killer_player = winner_leader.owner
    
    for dead_unit in all_dead:
        dead_unit.hp = 0
        
        # ZAMIAST ręcznego usuwania, wywołujemy nową, inteligentną funkcję ze świata gry!
        # Funkcja sama usunie jednostkę, a jeśli to Generał - wyśle go do lochów "killer_player"
        world.kill_unit(dead_unit, killer_player)

    # 5. Aktualizacja ocalałej armii
    if not survivors:
        print("=> Obie armie uległy całkowitemu wyniszczeniu!")
        return False # Atakujący nie przeżył
        
    else:
        # Ktoś przeżył. Ustawiamy pierwszego ocalałego jako Lidera armii
        new_leader = survivors[0]
        new_leader.garrison = [None] * 10
        
        # Resztę ocalałych pakujemy mu "do kieszeni"
        for i, s in enumerate(survivors[1:]):
            if i < 10:
                new_leader.garrison[i] = s
                # Ukrywamy pasażerów z mapy
                s.x, s.y = -1, -1
                if s in world.units: world.units.remove(s)

        # Jeśli stary lider zginął, a ocalał ktoś inny z jego armii, awansujemy go
        if new_leader != winner_leader:
            new_leader.x, new_leader.y = winner_leader.x, winner_leader.y
            if new_leader not in world.units: world.units.append(new_leader)
            
        print(f"Starcie przetrwało {len(survivors)} jednostek.")
        return new_leader in attackers