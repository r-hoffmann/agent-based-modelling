from lib.Car import Car
from lib.direction import Direction
import random
import numpy as np


class Road:
    def __init__(self, model, start_location, direction, p_car_spawn, p_next_directions, max_speed):
        """
        Creates a road
        :param start_location: The location of the right most cell of the right part of the road
        :param direction: The direction of the road. This direction is an integer between 0 and 7. Where 0 is a
        direction of 0 degrees, 1 of 45 degrees, etc.
        :param p_car_spawn: The probability of car spawning during each time step
        :param max_speed: The speed limit of the road
        """
        self.model = model
        self.start_location = start_location
        self.direction = direction
        self.p_car_spawn = p_car_spawn
        self.max_speed = max_speed
        self.car_queue = []
        self.check_locations = self.calculate_locations()
        self.free_space = True

        self.p_next_directions = p_next_directions

    def spawn_car(self, unique_id):
        next_direction = np.random.choice(Direction, p=self.p_next_directions)

        # TODO: Add different velocities by increasing the sigma
        velocity = int(random.gauss(self.max_speed, 0))
        bmw_factor = random.random()
        car = Car(
            unique_id,
            self.model,
            self,
            self.start_location,
            self.direction,
            next_direction,
            velocity,
            30,
            bmw_factor
        )

        self.car_queue.insert(0, car)
        self.model.cars.append(car)

    def calculate_locations(self):
        (x, y) = self.start_location

        if self.direction == Direction.RIGHT:
            return [[x + a, y] for a in range(11)]
        elif self.direction == Direction.TOP:
            return [[x, y + a] for a in range(11)]
        elif self.direction == Direction.LEFT:
            return [[x - a, y] for a in range(11)]
        elif self.direction == Direction.BOTTOM:
            return [[x, y - a] for a in range(11)]

    def check_free_space(self):
        free = True
        for location in self.check_locations:
            if not self.model.grid.is_cell_empty(location):
                free = False
                break

        self.free_space = free

    def step(self):
        if random.random() <= self.p_car_spawn:
            self.spawn_car(len(self.model.cars))

        # Check whether a new car could be spawned on the road
        self.check_free_space()
