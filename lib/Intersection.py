from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
import random
from lib import Car

class Intersection(Model):
    def __init__(self, spawn_rate, max_speed, a_factor, size=216):
        self.max_speed = max_speed
        self.cars = []
        self.size = size
        # starting position: bottom, top, left, right.
        self.starting_positions = [[self.size//2 + 4, 0], [self.size//2 - 4, self.size-1], [0, self.size//2 - 4], [self.size-1, self.size//2 + 4]]

        self.grid = MultiGrid(size, size, False)
        self.schedule = RandomActivation(self)

        # @todo add some cars
        for _ in range(5):
            self.add_car()

    def add_car(self):
        direction = 1 # @todo
        acceleration = 1 # @todo
        unique_id = len(self.schedule.agents)
        # Add the agent to a random lane
        initial_direction = random.randint(0,3)
        position = self.starting_positions[initial_direction]

        car = Car.Car(unique_id, self, direction, acceleration, position, initial_direction)
        self.schedule.add(car)
        self.grid.place_agent(car, (position[0], position[1]))

    def step(self):
        self.schedule.step()
        # collect data
        # self.datacollector.collect(self)

    def run_model(self, n):
        for _ in range(n):
            self.step()