import random
from mesa import Model
from lib import Car

class Intersection(Model):
    def __init__(self, max_speed, layout, starting_positions):
        self.max_speed = max_speed
        self.layout = layout
        self.cars = []
        self.starting_positions = starting_positions

    def add_car(self, *args):
        car = Car(*args)   
        car.id = len(self.cars)
        car.position = random.choice(self.starting_positions)
        self.cars.append(car)
