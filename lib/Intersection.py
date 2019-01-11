from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
import random
from lib import Car

class Intersection(Model):
    def __init__(self, spawn_rate, max_speed, a_factor, starting_positions=[[0,0],[0,0],[0,0],[0,0]]):
        self.max_speed = max_speed
        self.cars = []
        self.starting_positions = starting_positions
        # size 216x216 is big enough to hold 10 cars per lane and the intersection
        size = 216
        self.grid = MultiGrid(size, size, True)
        self.schedule = RandomActivation(self)

        # @todo add some cars
        for _ in range(5):
            self.add_car()

    def add_car(self):
        direction = 1 # @todo
        acceleration = 1 # @todo
        unique_id = len(self.cars)
        car = Car.Car(self, unique_id, direction, acceleration)
        # Add the agent to a random lane
        position = random.choice(self.starting_positions)
        self.schedule.add(car)
        self.grid.place_agent(car, (position[0], position[1]))

    def step(self):
        self.schedule.step()
        # collect data
        # self.datacollector.collect(self)

    def run_model(self, n):
        for _ in range(n):
            self.step()