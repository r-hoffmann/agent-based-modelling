from lib.Intersection import Intersection
from SALib.sample import saltelli
from SALib.analyze import sobol
import numpy as np

problem = {
    'num_vars': 4,
    'names': ['alpha_factor', 'beta_factor', 'p_spawn', 'intersection_type'],
    'bounds': [[0, 1],
               [0, 1],
               [0, 1],
               [0, 1]]
}


def model_for_sensitivity(alpha_factor,beta_factor,p_spawn,intersection_type):

	junction_type = ['Traffic lights', 'Fourway'][int(round(intersection_type))]
	parameters =  {
    'max_speed_horizontal': 15,
    'max_speed_vertical': 15,
    'alpha_factor': alpha_factor,
    'beta_factor': beta_factor,
    't_from_north': .5,
    't_from_west': .5,
    't_from_east': .5,
    't_from_south': 5,
    'intersection_type': junction_type,
    'p_car_spawn_north': p_spawn,
    'p_north_to_north': p_spawn,
    'p_north_to_west': p_spawn,
    'p_north_to_east': p_spawn,
    'p_north_to_south': p_spawn,
    'p_car_spawn_west': p_spawn,
    'p_west_to_north': p_spawn,
    'p_west_to_west': p_spawn,
    'p_west_to_east': p_spawn,
    'p_west_to_south': p_spawn,
    'p_car_spawn_east': p_spawn,
    'p_east_to_north': p_spawn,
    'p_east_to_west': p_spawn,
    'p_east_to_east': p_spawn,
    'p_east_to_south': p_spawn,
    'p_car_spawn_south': p_spawn,
    'p_south_to_north': p_spawn,
    'p_south_to_west': p_spawn,
    'p_south_to_east': p_spawn,
    'p_south_to_south': p_spawn
	}

	model = Intersection(parameters=parameters, parameters_as_dict=True)
	model.run_model(100)
	model.throughput.collect(model)
	df2 = model.throughput.get_model_vars_dataframe()
	average_throughput = sum(df2.values)/len(df2.values)
	print(average_throughput)
	return df2.values[-1]


# Generate parameters
param_values = saltelli.sample(problem, 100)

# generate output:
Y = np.zeros([param_values.shape[0]])

for i, X in enumerate(param_values):
    Y[i] = model_for_sensitivity(X[0],X[1],X[2],X[3])

Si = sobol.analyze(problem, Y)

print(Si)
print('First order sensitivity indices : ', Si['S1'])
print('Second order sensitivity indices : ', Si['ST'])
print('Interaction sensitivity indices : ', Si['S2'])