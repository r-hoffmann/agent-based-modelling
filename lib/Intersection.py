from mesa import Model
from mesa.space import MultiGrid
from mesa.time import BaseScheduler
from mesa.datacollection import DataCollector
from lib.Road import Road
import matplotlib.pyplot as plt

from lib.direction import Direction


class Intersection(Model):
    def __init__(self, p_car_spawn, max_speed, a_factor):
        # @TODO: can/should be made different on different roads
        self.p_direction_left = 0.25
        self.p_direction_right = 0.25
        self.p_direction_top = 0.25
        self.p_direction_bottom = 0.25

        super().__init__()

        self.roads = self.create_roads(p_car_spawn, max_speed)
        self.cars = []

        # size 216x216 is big enough to hold 10 cars per lane and the intersection
        self.size = 216
        self.grid = MultiGrid(self.size, self.size, True)
        self.schedule = BaseScheduler(self)
        self.average_speed = DataCollector({"Average speed": lambda m: self.get_average_speed()})
        self.throughput = DataCollector({"Throughput": lambda m: self.get_throughput()})
        self.waiting_cars = DataCollector({"Number of waiting cars": lambda m: self.get_waiting_cars()})

        self.running = True
        self.average_speed.collect(self)
        self.throughput.collect(self)
        self.waiting_cars.collect(self)

    def create_roads(self, p_car_spawn, max_speed):
        roads = []

        # for [x, y, direction] in [[103, 215, 6], [215, 112, 4], [112, 0, 2], [0, 103, 0]]:
        #     roads.append(Road(self, (x, y), direction, p_car_spawn, max_speed))

        # init 4 roads

        p_next_directions = [self.p_direction_right, self.p_direction_top, self.p_direction_left, self.p_direction_bottom]

        roads.append(Road(self, (103, 215), Direction.SOUTH, p_car_spawn, p_next_directions, max_speed))
        roads.append(Road(self, (215, 112,), Direction.WEST, p_car_spawn, p_next_directions, max_speed))
        roads.append(Road(self, (112, 0,), Direction.NORTH, p_car_spawn, p_next_directions, max_speed))
        roads.append(Road(self, (0, 103), Direction.EAST, p_car_spawn, p_next_directions, max_speed))
        
        return roads

    def step(self):
        for road in self.roads:
            road.step()

            if road.free_space and len(road.car_queue) > 0:
                car = road.car_queue.pop()
                self.schedule.add(car)
                self.grid.place_agent(car, car.pos)

        self.schedule.step()

        # Save the statistics
        self.average_speed.collect(self)
        self.throughput.collect(self)
        self.waiting_cars.collect(self)

    def run_model(self, n=100):
        for _ in range(n):
            self.step()

    def get_average_speed(self):
        number_of_agents = len(self.schedule.agents)
        if number_of_agents > 0:
            return sum([agent.velocity for agent in self.schedule.agents]) / number_of_agents
        return 0

    def get_throughput(self):
        return 100

    def get_waiting_cars(self):
        return sum([1 for agent in self.schedule.agents if agent.velocity==0])
