from lib.DataWriter import DataWriter

datawriter = DataWriter()

def model_for_sensitivity(p_spawn=0.1, max_speed_horizontal=3, max_speed_vertical=3, intersection_type=0):
	t_traffic_light_cycle=5
	p_bend = 0.33
	p_u_turn = 0.01
	p_left = p_bend
	p_right = p_bend
	p_straight = p_bend
	t_from_north = t_traffic_light_cycle
	t_from_west = t_traffic_light_cycle
	t_from_east = t_traffic_light_cycle
	t_from_south = t_traffic_light_cycle

	intersection_type = int(intersection_type)
	intersections = ['Fourway', 'Traffic lights', 'Equivalent']
	intersection = intersections[intersection_type]

	parameters = {
		"max_speed_horizontal": max_speed_horizontal,
		"max_speed_vertical": max_speed_vertical,
		"alpha_factor": 5,
		"beta_factor": 2,
		"intersection_type": intersection,
		"t_from_north": t_from_north,
		"t_from_west": t_from_west,
		"t_from_east": t_from_east,
		"t_from_south": t_from_south,
		"p_car_spawn_north": p_spawn,
		"p_north_to_north": p_u_turn,
		"p_north_to_west": p_right,
		"p_north_to_east": p_left,
		"p_north_to_south": p_straight,
		"p_car_spawn_west": p_spawn,
		"p_west_to_north": p_left,
		"p_west_to_west": p_u_turn,
		"p_west_to_east": p_straight,
		"p_west_to_south": p_right,
		"p_car_spawn_east": p_spawn,
		"p_east_to_north": p_right,
		"p_east_to_west": p_straight,
		"p_east_to_east": p_u_turn,
		"p_east_to_south": p_left,
		"p_car_spawn_south": p_spawn,
		"p_south_to_north": p_straight,
		"p_south_to_west": p_left,
		"p_south_to_east": p_right,
		"p_south_to_south": p_u_turn,
	}

	print(datawriter.get_runs_by_parameters(parameters))

model_for_sensitivity()