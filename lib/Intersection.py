import random

from mesa import Model
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation

from lib import Car
from lib import Road


class Intersection(Model):
    def __init__(self, spawn_rate, max_speed, a_factor):
        super().__init__()

        self.roads = self.create_roads(spawn_rate, max_speed)
        self.cars = []

        # size 216x216 is big enough to hold 10 cars per lane and the intersection
        size = 216
        self.grid = MultiGrid(size, size, True)
        self.schedule = SimultaneousActivation(self)

        # self.running = True
        # self.datacollector.collect(self)

    def create_roads(self, spawn_rate, max_speed):
        roads = []

        for [x, y, direction] in [[100, 0, 6], [215, 100, 4], [108, 215, 2], [0, 108, 0]]:
            roads.append(Road.Road(self, (x, y), direction, spawn_rate, max_speed))

        return roads

    def add_car(self, car):
        self.cars.append(car)
        self.schedule.add(car)
        self.grid.place_agent(car, car.location)

    def step(self):
        for road in self.roads:
            road.step()

            if road.free_space and len(road.car_queue) > 0:
                car = road.car_queue.pop()
                self.grid.place_agent(car, car.location)

        self.schedule.step()
        # collect data
        # self.datacollector.collect(self)

    def run_model(self, n=200):
        for _ in range(n):
            self.step()


model = Intersection(1, 50, 0.2)
model.run_model()
