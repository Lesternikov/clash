from world import World
from player import Player
from unit import Unit

world = World()

p1 = Player("Gracz 1", "red")
p2 = Player("Gracz 2", "blue")

world.add_player(p1)
world.add_player(p2)

world.load("map.txt", "0.FAC")

while True:
    world.draw()

    cmd = input("\nKomenda (x y | w/a/s/d | recruit | leave | end | quit): ")

    if cmd == "quit":
        break

    if cmd == "end":
        world.next_turn()
        continue

    if cmd == "recruit":
        world.recruit_unit()
        continue

    if cmd == "leave":
        world.leave_castle()
        continue


    # ruch jednostki
    if cmd in ["w", "a", "s", "d"]:
        if cmd == "w":
            world.move_selected(0, -1)
        elif cmd == "s":
            world.move_selected(0, 1)
        elif cmd == "a":
            world.move_selected(-1, 0)
        elif cmd == "d":
            world.move_selected(1, 0)
        continue

    # klik pola (jednostka albo zamek)
    parts = cmd.split()
    if len(parts) == 2:
        x, y = map(int, parts)

        # NAJPIERW zamek
        world.select_castle(x, y)

        # POTEM jednostka
        world.select_unit(x, y)
