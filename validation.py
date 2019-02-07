from lib.Intersection import Intersection
from lib.DataWriter import DataWriter
import matplotlib
matplotlib.get_backend()
import matplotlib.pyplot as plt
import numpy as np

def get_mean_last_runs(dataset, i):
	n = len(dataset)
	k = n - i
	return float(dataset[-1] * n - dataset[k] * k) / float(i)

def model_for_validation(p_spawn=0.1, max_speed_horizontal=10, max_speed_vertical=10, intersection_type=0):
	t_traffic_light_cycle = 10000
	p_bend = 0
	p_u_turn = 0
	p_left = 0
	p_right = 0
	p_straight = 1
	t_from_north = t_traffic_light_cycle
	t_from_west = 0
	t_from_east = 0
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
		"p_car_spawn_west": 0,
		"p_west_to_north": p_left,
		"p_west_to_west": p_u_turn,
		"p_west_to_east": p_straight,
		"p_west_to_south": p_right,
		"p_car_spawn_east": 0,
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
	datawriter.run(1000)
	data = datawriter.get_runs_by_parameters(parameter_set)
	flow = data['results']['throughput'][-1]
	speed = data['results']['average_speed'][-1]
	return flow,speed

# create lists of spawn probabiilities and speeds 

spawn_list = np.linspace(0,1,100)
speed_list = np.linspace(3,30,28)

flows = []
average_speed = []

for p_spawn in spawn_list:
	for speed in speed_list:
		flow, speed_out = model_for_validation(p_spawn, speed,speed, 1)
		#print(flow,speed_out)
		flows.append(flow)
		average_speed.append(speed_out)
	print(str(p_spawn) + 'out of 50 done')

spawn_to_plot = np.asarray([[x]*len(speed_list) for x in spawn_list]).flatten()


plt.close('all')
plt.scatter(spawn_to_plot,flows,s = 7, alpha = .2)
plt.ylabel('Car flow in #cars per step')
plt.xlabel('Spawning probability')
plt.title('Relation between car flow and density')
plt.savefig('data/Flow_pspawn.jpg')
plt.close()

plt.scatter(spawn_to_plot, average_speed,s = 7, alpha = .2)
plt.ylabel('Average speed')
plt.xlabel('Spawning probability')
plt.title('Relation between car flow and density')
plt.savefig('data/Av_speed_pspawn.jpg')
plt.close()

plt.scatter(flows,average_speed,s = 7, alpha = .2)
plt.ylabel('Average speed')
plt.xlabel('Flow in #car per step')
plt.title('Relation between car flow and density')
plt.savefig('data/Av_speed_flow.jpg')
plt.close()