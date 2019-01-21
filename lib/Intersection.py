from mesa import Model
from mesa.space import MultiGrid
from mesa.time import BaseScheduler
from mesa.datacollection import DataCollector
from lib.Road import Road
import matplotlib.pyplot as plt

from lib.Direction import Direction


class Intersection(Model):
    def __init__(self, **args):
        # @TODO: can/should be made different on different roads
        super().__init__()
        for field in args:
            setattr(self, field, args[field])

        self.roads = []
        self.create_roads()
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

        self.intersection_corners = self.get_intersection_corners()


    def get_intersection_corners(self):
        lane_width = 8

        mid_x = self.size // 2
        mid_y = self.size // 2

        tl_x = mid_x - lane_width
        tl_y = mid_y + lane_width

        br_x = mid_x + lane_width
        br_y = mid_y - lane_width

        points = []
        points.append((tl_x, tl_y))
        points.append((br_x, br_y))

        return points

    def create_roads(self):
        self.roads.append(
            Road(
                self,  
                (103, 215), 
                Direction.SOUTH,
                self.p_car_spawn_north, 
                [
                    self.p_north_to_east,
                    self.p_north_to_north,
                    self.p_north_to_west,
                    self.p_north_to_south,
                ], 
                self.max_speed_vertical
            )
        )

        self.roads.append(
            Road(
                self,  
                (0, 103),
                Direction.EAST,
                self.p_car_spawn_west, 
                [
                    self.p_west_to_east,
                    self.p_west_to_north,
                    self.p_west_to_west,
                    self.p_west_to_south,
                ], 
                self.max_speed_horizontal
            )
        )
        
        self.roads.append(
            Road(
                self,
                (215, 112),
                Direction.WEST,
                self.p_car_spawn_east,
                [
                    self.p_east_to_east,
                    self.p_east_to_north,
                    self.p_east_to_west,
                    self.p_east_to_south,
                ],
                self.max_speed_horizontal
            )
        )

        self.roads.append(
            Road(
                self, 
                (112, 0),
                Direction.NORTH,
                self.p_car_spawn_south, 
                [
                    self.p_south_to_east,
                    self.p_south_to_north,
                    self.p_south_to_west,
                    self.p_south_to_south,
                ], 
                self.max_speed_vertical
            )
        )

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

