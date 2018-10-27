import sys
sys.path.insert(0, '../')
from planet_wars import issue_order
from bt_bot import *
from math import floor

def defend_planets2(state):
    enemy_fleets = state.enemy_fleets()

    for fleet in enemy_fleets:
        if state.planets[fleet.destination_planet].owner != 1:
            enemy_fleets.remove(fleet)

    for fleet in enemy_fleets:
        total_sent = sum(my_fleet.num_ships for my_fleet in state.my_fleets() if my_fleet.destination_planet == fleet.destination_planet)
        planet = state.planets[fleet.destination_planet]
        total_sent += planet.num_ships + planet.growth_rate * fleet.turns_remaining

        if total_sent >= fleet.num_ships:
            enemy_fleets.remove(fleet)

    if len(enemy_fleets) == 0:
        return True

    for fleet in enemy_fleets:
        target = fleet.destination_planet
        ships_needed = fleet.num_ships + 1

        helpful_planets = [planet for planet in state.my_planets() if state.distance(planet.ID, target) <= fleet.turns_remaining]
        ships_avail = sum(planet.num_ships for planet in helpful_planets) - len(helpful_planets)

        if ships_avail > ships_needed:
            for planet in helpful_planets:
                if ships_needed < 1:
                    break
                if planet.num_ships - 1 >= ships_needed > 0:
                    issue_order(state, planet.ID, target, ships_needed)
                    ships_needed = 0
                    break
                elif planet.num_ships - 1 > 0:
                    issue_order(state, planet.ID, target, planet.num_ships - 1)
                    ships_needed -= planet.num_ships - 1

    return True

def equalize(state):
    my_planets = state.my_planets()

    def strength(p):
        return p.num_ships + sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == p.ID) \
               - sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == p.ID)

    if not my_planets:
        return True

    average_strength = sum(strength(p) for p in my_planets) / len(my_planets)

    below_average = [planet for planet in my_planets if strength(planet) < average_strength]
    above_average = [planet for planet in my_planets if strength(planet) > average_strength]

    below_average.sort(key=strength)
    above_average.sort(key=strength, reverse = True)

    average_strength = floor(average_strength)

    for strong in above_average:
        ships_avail = strong.num_ships - average_strength

        for weak in below_average:
            ships_needed = average_strength - weak.num_ships

            if ships_avail >= ships_needed > 0:
                issue_order(state, strong.ID, weak.ID, ships_needed)
                ships_avail -= ships_needed
                below_average.remove(weak)
            elif ships_avail > 0:
                issue_order(state, strong.ID, weak.ID, ships_avail)
                ships_avail = 0
                break
            
            if ships_avail <= 0:
                break
    return True


def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    #if len(state.my_fleets()) >= 1:
        #return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def spread(state):
    my_planets = state.my_planets()

    for fleet in state.enemy_fleets():
        planet = state.planets[fleet.destination_planet]
        if planet.owner == 1 and planet in my_planets:
            my_planets.remove(planet)

    my_planets.sort(key=lambda p: p.num_ships, reverse=True)
    neutral_planets = state.not_my_planets()

    #This loop checks if I've sent enough fleets to deal with each planet
    for planet in neutral_planets:
        total_needed = planet.num_ships + sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == planet.ID)
        total_sent = sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == planet.ID)

        #if planet.owner != 0:
            #total_needed += planet.growth_rate * turns_left
        if total_sent >= total_needed:
            neutral_planets.remove(planet)

    neutral_planets.sort(key=lambda p: p.num_ships)

    orders_issued = 0
    for my_planet in my_planets:
        ships_avail = my_planet.num_ships - 10
        neutral_planets.sort(key=lambda p: p.num_ships + state.distance(my_planet.ID, p.ID)/2)
        for target in neutral_planets:
            ships_needed = target.num_ships + 1

            if target.owner != 0:
                ships_needed += state.distance(my_planet.ID, target.ID) * target.growth_rate

            if ships_avail >= ships_needed > 0:
                issue_order(state, my_planet.ID, target.ID, ships_needed)
                orders_issued += 1
                ships_avail -= ships_needed
                neutral_planets.remove(target)
            else:
                break

    return orders_issued > 0