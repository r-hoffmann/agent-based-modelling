from lib.Intersection import Intersection
from SALib.sample import saltelli
from SALib.analyze import sobol
import numpy as np
import pandas as pd
import csv

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
	#print(df2.values[-1][-1])
	return df2.values[-1][-1]


# Generate parameters
param_values = saltelli.sample(problem, 200)

# generate output:
Y = np.zeros([param_values.shape[0]])
print('total number of runs: ',len(Y))

for i, X in enumerate(param_values):
    Y[i] = model_for_sensitivity(X[0],X[1],X[2],X[3])
    print('run number: ',i, 'model outpu : ', Y[i])

Si = sobol.analyze(problem, Y)

print('First order sensitivity indices :')
print( Si['S1'])
print('Second order sensitivity indices :')
print( Si['ST'])
print('Interaction sensitivity indices :')
print( Si['S2'])

interaction = Si.pop('S2', None)
conf_interaciton = Si.pop('S2_conf', None)

df = pd.DataFrame.from_dict(Si)
df.to_csv('data/first_and_second_order_sensitivity_results.csv')

df = pd.DataFrame(interaction)
df.to_csv('data/interaction_sensitivity_results.csv')

df = pd.DataFrame(conf_interaciton)
df.to_csv('data/Confidence_interva_interaction_sensitivity_results.csv')



