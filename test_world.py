from map_loader import load_dat, load_fac
from world import World

tiles = load_dat("0.DAT")
objects = load_fac("0.FAC")

world = World(tiles, objects)

print("Temple at (0,41):", world.has_temple(0, 41))
print("Trap at (0,11):", world.has_trap(0, 11))
