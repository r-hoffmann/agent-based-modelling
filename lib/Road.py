import numpy as np

from lib.Car import Car
from lib.Direction import Direction


class Road:
    def __init__(self, model, start_location, direction, p_car_spawn, p_next_directions, max_speed):
        """
        Creates a road
        :param start_location: The location of the right most cell of the right part of the road
        :param direction: The direction of the road. This direction is an integer between 0 and 7. Where 0 is a
        direction of 0 degrees, 1 of 45 degrees, etc.
        :param p_car_spawn: The probability of car spawning during each time step
        :param p_next_directions: the probabilities for the car of taking each of the directions
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

        self.first = None

        self.line_height = 3
        self.stop_line_pos = self.calculate_stop_line()

        self.p_next_directions = np.array(p_next_directions) / sum(p_next_directions)

    def calculate_stop_line(self):
        """
        Calculate the position of the stopline
        :return: (x, y)
        """
        size = 216  # HARDCODED  != OK

        x = self.start_location[0]
        y = self.start_location[1]

        if self.direction == Direction.NORTH:
            y = y + size // 2 - self.line_height
        elif self.direction == Direction.SOUTH:
            y = y - size // 2 + self.line_height
        elif self.direction == Direction.WEST:
            x = x - size // 2 + self.line_height
        elif self.direction == Direction.EAST:
            x = x + size // 2 - self.line_height

        return x, y

    def spawn_car(self, unique_id):
        """
        Adds a car to the queue
        :param unique_id: ID of the car
        :return: None
        """

        # Stochastic parameters
        next_direction = self.model.rnd.choice([Direction.EAST, Direction.NORTH, Direction.WEST, Direction.SOUTH],
                                          p=self.p_next_directions)

        desired_velocity = min(self.max_speed + 5, max(5, int(np.round(self.model.rnd.normal(self.max_speed, 2)))))
        maximum_acceleration = min(2.0, max(0.6, self.model.rnd.normal(1, 0.2)))
        comfortable_deceleration = min(3.0, max(1.0, self.model.rnd.normal(2.0, 0.5)))
        bmw_factor = self.model.rnd.beta(self.model.alpha_factor, self.model.beta_factor)

        car = Car(
            unique_id,
            self.model,
            self,
            self.start_location,
            self.direction,
            next_direction,
            desired_velocity,
            bmw_factor,
            self.model.schedule.steps,
            desired_velocity,
            maximum_acceleration,
            comfortable_deceleration
        )

        # Prepend car to the queue
        self.car_queue.insert(0, car)

        # Add car to the model
        self.model.cars.append(car)

    def calculate_locations(self):
        """
        Calculate the locations of the beginning of the road, which is used to check if there is free space to spawn the
        next car in the queue
        :return: List of locations [[x_1,y_1],[x_2,y_2],...]
        """
        (x, y) = self.start_location

        if self.direction == Direction.EAST:
            return [[x + a, y] for a in range(11)]
        elif self.direction == Direction.NORTH:
            return [[x, y + a] for a in range(11)]
        elif self.direction == Direction.WEST:
            return [[x - a, y] for a in range(11)]
        elif self.direction == Direction.SOUTH:
            return [[x, y - a] for a in range(11)]

    def check_free_space(self):
        """
        Check if there is free space to spawn the next car in the queue
        :return: Boolean
        """
        free = True
        for location in self.check_locations:
            if not self.model.grid.is_cell_empty(location):
                free = False
                break

        self.free_space = free

    def car_at_stopline(self):
        """
        Returns the car at the stopline if there is one
        :return: Car|None
        """
        x, y = self.stop_line_pos

        positions = []
        if self.direction == Direction.EAST:
            positions = [[x - a, y] for a in range(15)]
        elif self.direction == Direction.NORTH:
            positions = [[x, y - a] for a in range(15)]
        elif self.direction == Direction.WEST:
            positions = [[x + a, y] for a in range(15)]
        elif self.direction == Direction.SOUTH:
            positions = [[x, y + a] for a in range(15)]

        for position in positions:
            agents = self.model.grid.get_neighbors(position, True, include_center=True, radius=0)

            for agent in agents:
                if type(agent) == Car and not agent.turning:
                    return agent

        return None

    def count_cars_before_stopline(self):
        """
        Count the number of cars before the stopline
        :return: Integer
        """
        x, y = self.stop_line_pos

        positions = []
        if self.direction == Direction.EAST:
            positions = [[x - a, y] for a in range(abs(x))]
        elif self.direction == Direction.NORTH:
            positions = [[x, y - a] for a in range(abs(y))]
        elif self.direction == Direction.WEST:
            positions = [[x + a, y] for a in range(abs(216 - x))]
        elif self.direction == Direction.SOUTH:
            positions = [[x, y + a] for a in range(abs(216 - y))]

        count = 0
        for position in positions:
            agents = self.model.grid.get_neighbors(position, True, include_center=True, radius=0)

            for agent in agents:
                if type(agent) == Car and not agent.turning:
                    count += 1

        return count

    def step(self):
        """
        Adds car to queue based on probability
        :return: None
        """
        if self.model.rnd.rand() <= self.p_car_spawn:
            self.spawn_car(len(self.model.cars))

        # Check whether a new car could be spawned on the road
        self.check_free_space()
