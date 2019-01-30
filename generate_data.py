from lib.DataWriter import DataWriter
from lib.Intersection import Intersection
from itertools import product

p_spawn = [x / 10.0 for x in [3, 6]]
from_0_to_1 = [0.25]
from_1_to_10 = [5]
speeds = [5]

parameters =  {
    'max_speed_horizontal': speeds,
    'max_speed_vertical': speeds,
    'alpha_factor': [5],
    'beta_factor': [2],
    't_from_north': from_1_to_10,
    't_from_west': from_1_to_10,
    't_from_east': from_1_to_10,
    't_from_south': from_1_to_10,
    'intersection_type': ['Smart lights', 'Traffic lights', 'Fourway', 'Equivalent'],
    'p_car_spawn_north': from_0_to_1,
    'p_north_to_north': from_0_to_1,
    'p_north_to_west': from_0_to_1,
    'p_north_to_east': from_0_to_1,
    'p_north_to_south': from_0_to_1,
    'p_car_spawn_west': p_spawn,
    'p_west_to_north': from_0_to_1,
    'p_west_to_west': from_0_to_1,
    'p_west_to_east': from_0_to_1,
    'p_west_to_south': from_0_to_1,
    'p_car_spawn_east': p_spawn,
    'p_east_to_north': from_0_to_1,
    'p_east_to_west': from_0_to_1,
    'p_east_to_east': from_0_to_1,
    'p_east_to_south': from_0_to_1,
    'p_car_spawn_south': p_spawn,
    'p_south_to_north': from_0_to_1,
    'p_south_to_west': from_0_to_1,
    'p_south_to_east': from_0_to_1,
    'p_south_to_south': from_0_to_1
}


parameter_space = [dict(zip(parameters, v)) for v in product(*parameters.values())]
print('Generating {} intersections'.format(len(parameter_space)))

for parameter_set in parameter_space:
    intersection = Intersection( parameters=parameter_set, parameters_as_dict=True )
    datawriter = DataWriter(intersection)
    datawriter.run(10)
    