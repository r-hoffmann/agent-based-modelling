from lib.Car import Car
import random


class Road:
    def __init__(self, model, start_location, direction, spawn_probability, max_speed):
        """
        Creates a road
        :param start_location: The location of the right most cell of the right part of the road
        :param direction: The direction of the road. This direction is an integer between 0 and 7. Where 0 is a
        direction of 0 degrees, 1 of 45 degrees, etc.
        :param spawn_probability: The probability of car spawning during each time step
        :param max_speed: The speed limit of the road
        """
        self.model = model
        self.start_location = start_location
        self.direction = direction
        self.spawn_probability = spawn_probability
        self.max_speed = max_speed
        self.car_queue = []
        self.check_locations = self.calculate_locations()
        self.free_space = True

    def spawn_car(self, unique_id):
        # TODO: Add different velocities by increasing the sigma
        velocity = int(random.gauss(self.max_speed, 0))
        bmw_factor = random.random()
        car = Car(
            unique_id,
            self.model,
            self,
            self.start_location,
            self.direction,
            self.direction,  # Should be changed to another direction
            velocity,
            30,
            bmw_factor
        )

        self.car_queue.insert(0, car)
        self.model.cars.append(car)

    def calculate_locations(self):
        (x, y) = self.start_location

        if self.direction == 0:
            return [[x + a, y] for a in range(11)]
        elif self.direction == 2:
            return [[x, y + a] for a in range(11)]
        elif self.direction == 4:
            return [[x - a, y] for a in range(11)]
        elif self.direction == 6:
            return [[x, y - a] for a in range(11)]

    def check_free_space(self):
        free = True
        for location in self.check_locations:
            if not self.model.grid.is_cell_empty(location):
                free = False
                break

        self.free_space = free

    def step(self):
        if random.random() <= self.spawn_probability:
            self.spawn_car(len(self.model.cars))

        # Check whether a new car could be spawned on the road
        self.check_free_space()
