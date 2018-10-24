from bt_bot import *

def is_enemy_attacking(state):
    enemy_fleets = state.enemy_fleets()

    for fleet in enemy_fleets:
        if state.planets[fleet.destination_planet].owner != 1:
            enemy_fleets.remove(fleet)

    return len(enemy_fleets) > 0

def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())
