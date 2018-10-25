import sys
sys.path.insert(0, '../')
from planet_wars import issue_order
from bt_bot import *

def defend_planets(state):
    enemy_fleets = state.enemy_fleets()

    for fleet in enemy_fleets:
        if state.planets[fleet.destination_planet].owner != 1:
            enemy_fleets.remove(fleet)

    #check if I've already sent fleets to defend
    my_fleets = state.my_fleets()
    for fleet in enemy_fleets:
        total_sent = 0
        for my_fleet in my_fleets:
            if my_fleet.destination_planet == fleet.destination_planet:
                total_sent += my_fleet.num_ships
                my_fleets.remove(my_fleet)
        if total_sent >= fleet.num_ships:
            enemy_fleets.remove(fleet)

    if len(enemy_fleets) == 0:
        return False

    #get close planets
    helpful_planets = {}
    for fleet in enemy_fleets:
        for planet in state.my_planets():
            if state.distance(planet.ID, fleet.destination_planet) < fleet.turns_remaining:
                if fleet.destination_planet not in helpful_planets:
                    helpful_planets[fleet.destination_planet] = []
                helpful_planets[fleet.destination_planet].append(planet)
        if fleet.destination_planet not in helpful_planets:
            enemy_fleets.remove(fleet)

    if len(helpful_planets) == 0:
        return False

    #get savable planets
    for fleet in enemy_fleets:
        key = fleet.destination_planet
        total_available_ships = 0

        if key in helpful_planets:
            for planet in helpful_planets[key]:
                total_available_ships += planet.num_ships

            if total_available_ships < fleet.num_ships:
                helpful_planets.pop(key)

    if len(helpful_planets) == 0:
        return False

    orders_issued = 0
    #save planets
    for fleet in enemy_fleets:
        key = fleet.destination_planet
        ships_needed = fleet.num_ships + 1

        if key in helpful_planets:
            for planet in helpful_planets[key]:
                if (planet.num_ships - 1) > ships_needed:
                    #send ships_needed
                    issue_order(state, planet.ID, key, ships_needed)
                    orders_issued += 1
                    ships_needed = 0
                    break
                else:
                    #send planet.num_ships - 1
                    ships_needed -= planet.num_ships - 1
                    issue_order(state, planet.ID, key, planet.num_ships - 1)
                    orders_issued += 1
    return False

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
    my_planets.sort(key=lambda p: p.num_ships, reverse=True)
    neutral_planets = state.not_my_planets()

    #This loop checks if I've sent enough fleets to deal with each planet
    for planet in neutral_planets:
        total_needed = planet.num_ships
        turns_left = 0
        total_sent = 0

        for fleet in state.my_fleets():
            if fleet.destination_planet == planet.ID:
                total_sent += fleet.num_ships
                if fleet.turns_remaining > turns_left:
                    turns_left = fleet.turns_remaining

        for fleet in state.enemy_fleets():
            if fleet.destination_planet == planet.ID:
                total_needed += fleet.num_ships

        if planet.owner != 0:
            total_needed += planet.growth_rate * turns_left
        if total_sent >= total_needed:
            neutral_planets.remove(planet)


    neutral_planets.sort(key=lambda p: p.num_ships)

    orders_issued = 0
    for planet in neutral_planets:
        ships_needed = planet.num_ships + 1
        for my_planet in my_planets:
            if planet.owner != 0:
                ships_needed += state.distance(my_planet.ID, planet.ID) * planet.growth_rate
            if my_planet.num_ships/2 > ships_needed:
                issue_order(state, my_planet.ID, planet.ID, ships_needed)
                if my_planet.num_ships - ships_needed < 20:
                    my_planets.remove(my_planet)

                orders_issued += 1
                ships_needed = 0
                break
            elif my_planet.num_ships/2 > 30:
                ships_needed -= my_planet.num_ships/2
                issue_order(state, my_planet.ID, planet.ID, my_planet.num_ships/2)
                orders_issued += 1
                #my_planet.num_ships -= my_planet.num_ships/2
                if my_planet.num_ships/2 < 20:
                    my_planets.remove(my_planet)
                if planet.owner != 0:
                    ships_needed -= state.distance(my_planet.ID, planet.ID) * planet.growth_rate

    return orders_issued > 0