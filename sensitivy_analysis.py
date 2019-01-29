from lib.Intersection import Intersection
from SALib.sample import saltelli
from SALib.analyze import sobol
import numpy as np

problem = {
	'num_vars': 6,
	'names': ['p_spawn', 'p_bend', 'p_u_turn', 't_traffic_light_cycle', 'max_speed_horizontal', 'max_speed_vertical'],
	'bounds': [[0, 1],
			   [0, 1],
			   [0, 1],
			   [0, 1],
			   [0, 1],
			   [0, 3]]
}


def model_for_sensitivity(p_spawn=0.1, p_bend=0.33, p_u_turn=0.01, t_traffic_light_cycle=5, max_speed_horizontal=10, max_speed_vertical=10, intersection_type=0):
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
		# "alpha_factor": UserSettableParameter('slider', "Antisocial alpha factor", 2, 0, 10, .01),
		# "beta_factor": UserSettableParameter('slider', "Antisocial beta factor", 5, 0, 10, .01),
		"intersection_type": intersection,
		"t_from_north": t_traffic_light_cycle,
		"t_from_west": t_traffic_light_cycle,
		"t_from_east": t_traffic_light_cycle,
		"t_from_south": t_traffic_light_cycle,
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
	
	model = Intersection(parameters=parameters, parameters_as_dict=True)
	model.run_model(100)
	model.throughput.collect(model)
	df2 = model.throughput.get_model_vars_dataframe()
	# Return average throughput
	return df2.values[-1]

# Generate parameters
param_values = saltelli.sample(problem, 100)

# generate output:
Y = np.zeros([param_values.shape[0]])

for i, X in enumerate(param_values):
	Y[i] = model_for_sensitivity( X[0], X[1], X[2], X[3], X[4], X[5] )

Si = sobol.analyze(problem, Y)

print(Si)
print('First order sensitivity indices : ', Si['S1'])
print('Second order sensitivity indices : ', Si['ST'])
print('Interaction sensitivity indices : ', Si['S2'])