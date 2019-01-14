from mesa import Model
from mesa.space import MultiGrid
from mesa.time import BaseScheduler
from mesa.datacollection import DataCollector
from lib.Road import Road
import matplotlib.pyplot as plt


class Intersection(Model):
    def __init__(self, spawn_probability, max_speed, a_factor):
        super().__init__()

        self.roads = self.create_roads(spawn_probability, max_speed)
        self.cars = []

        # size 216x216 is big enough to hold 10 cars per lane and the intersection
        self.size = 216
        self.grid = MultiGrid(self.size, self.size, True)
        self.schedule = BaseScheduler(self)
        self.datacollector = DataCollector({"Cars": lambda m: self.schedule.get_agent_count()})

        self.running = True
        self.datacollector.collect(self)

    def create_roads(self, spawn_probability, max_speed):
        roads = []

        for [x, y, direction] in [[103, 215, 6], [215, 112, 4], [112, 0, 2], [0, 103, 0]]:
            roads.append(Road(self, (x, y), direction, spawn_probability, max_speed))

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
        self.datacollector.collect(self)

    def run_model(self, n=100):
        for _ in range(n):
            self.step()


model = Intersection(0.1, 20, 0.2)
model.run_model()
