from lib.Intersection import Intersection
from lib.DataWriter import DataWriter
from SALib.sample import saltelli
from SALib.analyze import sobol
import numpy as np

problem = {
	'num_vars': 4,
	'names': ['p_spawn', 'max_speed_horizontal', 'max_speed_vertical', 'intersection_type'],
	'bounds': [[0, 1],
			   [3, 24],
			   [3, 24],
			   [0, 4]]
}

def get_mean_last_runs(dataset, i):
	n = len(dataset)
	k = n - i
	return float(dataset[-1] * n - dataset[k] * k) / float(i)

def model_for_sensitivity(p_spawn=0.1, max_speed_horizontal=10, max_speed_vertical=10, intersection_type=0):
	t_traffic_light_cycle = 5
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
	intersections = ['Fourway', 'Traffic lights', 'Equivalent', 'Smart lights']
	intersection = intersections[intersection_type]

	parameter_set = {
		"max_speed_horizontal": int(max_speed_horizontal),
		"max_speed_vertical": int(max_speed_vertical),
		"seed": 1337,
		"bmw_fraction": 0.1,
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

	model = Intersection(parameters = parameter_set, parameters_as_dict=True)
	datawriter = DataWriter(model)
	datawriter.run()
	data = datawriter.get_runs_by_parameters(parameter_set)
	return get_mean_last_runs(data['results']['throughput'], 900)

# Generate parameters
param_values = saltelli.sample(problem, 10)

# generate output:
Y = np.zeros([param_values.shape[0]])

for i, X in enumerate(param_values):
	Y[i] = model_for_sensitivity(X[0], X[1], X[2], X[3])

Si = sobol.analyze(problem, Y, print_to_console=True)

with open('sensitivity_results.txt', 'w+') as file:
	file.write(str(Si))
	file.write('First order sensitivity indices : ' + str(Si['S1']))
	file.write('Second order sensitivity indices : ' + str(Si['ST']))
	file.write('Interaction sensitivity indices : ' + str(Si['S2']))
print('Done!')