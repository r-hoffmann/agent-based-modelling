from lib.DataWriter import DataWriter
from lib.Intersection import Intersection
from itertools import product

p_spawn=0.1
max_speed_horizontal=3
max_speed_vertical=3
intersection_type=0

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

parameter_set = {
    "max_speed_horizontal": max_speed_horizontal,
    "max_speed_vertical": max_speed_vertical,
    "alpha_factor": 5,
    "beta_factor": 2,
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

intersection = Intersection( parameters=parameter_set, parameters_as_dict=True )
datawriter = DataWriter(intersection)
datawriter.run(10)
asdf

from_0_to_1 = [x / 10.0 for x in [1]]
from_1_to_10 = [5]
speeds = [5]

parameters =  {
    'max_speed_horizontal': speeds,
    'max_speed_vertical': speeds,
    'alpha_factor': 5,
    'beta_factor': 2,
    't_from_north': from_1_to_10,
    't_from_west': from_1_to_10,
    't_from_east': from_1_to_10,
    't_from_south': from_1_to_10,
    'intersection_type': ['Traffic lights', 'Fourway', 'Equivalent'],
    'p_car_spawn_north': from_0_to_1,
    'p_north_to_north': from_0_to_1,
    'p_north_to_west': from_0_to_1,
    'p_north_to_east': from_0_to_1,
    'p_north_to_south': from_0_to_1,
    'p_car_spawn_west': from_0_to_1,
    'p_west_to_north': from_0_to_1,
    'p_west_to_west': from_0_to_1,
    'p_west_to_east': from_0_to_1,
    'p_west_to_south': from_0_to_1,
    'p_car_spawn_east': from_0_to_1,
    'p_east_to_north': from_0_to_1,
    'p_east_to_west': from_0_to_1,
    'p_east_to_east': from_0_to_1,
    'p_east_to_south': from_0_to_1,
    'p_car_spawn_south': from_0_to_1,
    'p_south_to_north': from_0_to_1,
    'p_south_to_west': from_0_to_1,
    'p_south_to_east': from_0_to_1,
    'p_south_to_south': from_0_to_1
}


parameter_space = [dict(zip(parameters, v)) for v in product(*parameters.values())]
print('Generating {} intersections'.format(len(parameter_space)))

for parameter_set in parameter_space[:10]:
    intersection = Intersection( parameters=parameter_set, parameters_as_dict=True )
    datawriter = DataWriter(intersection)
    datawriter.run(10)
    