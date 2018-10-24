def get_enemy_attacking_fleets(state):
    enemy_fleets = state.enemy_fleets()

    for fleet in enemy_fleets:
        if fleet.destination.owner != 1:
            enemy_fleets.remove(fleet)

    return len(enemy_fleets) > 0

def get_close_planets(state):
	our_planets = state.my_planets()

	for fleet in enemy_fleets:
		for planet in our_planets:
			if state.distance(planet, fleet.destination_planet) < fleet.turns_remaining:
				if helpful_planets[fleet.destination_planet] == None:
					helpful_planets[fleet.destination_planet] = []
				helpful_planets[fleet.destination_planet].append(planet)


	return len(helpful_planets) > 0

def get_savable_planets(state):
	for fleet in enemy_fleets:
		key = fleet.destination_planet
		total_available_ships = 0
		for planet in helpful_planets[key]:
			total_available_ships += planet.num_ships

		if total_available_ships < fleet.num_ships:
			helpful_planets.pop(key)

	return len(helpful_planets) > 0



def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())
