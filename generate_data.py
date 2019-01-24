from lib.DataWriter import DataWriter
from lib.Intersection import Intersection

intersection = Intersection(
    max_speed_horizontal=10,
    max_speed_vertical=10,
    alpha_factor=.05,
    beta_factor=.05,
    intersection_type='Fourway',
    p_car_spawn_north=0.5,
    p_north_to_north=0.10,
    p_north_to_west=0.24,
    p_north_to_east=0.33,
    p_north_to_south=0.33,
    p_car_spawn_west=0.0,
    p_west_to_north=0.0,
    p_west_to_west=1.0,
    p_west_to_east=0.0,
    p_west_to_south=0.0,
    p_car_spawn_east=0.0,
    p_east_to_north=0.0,
    p_east_to_west=0.0,
    p_east_to_east=1.0,
    p_east_to_south=0.0,
    p_car_spawn_south=0.0,
    p_south_to_north=0.0,
    p_south_to_west=0.0,
    p_south_to_east=0.0,
    p_south_to_south=1.0,
)

datawriter = DataWriter(intersection)
datawriter.run()