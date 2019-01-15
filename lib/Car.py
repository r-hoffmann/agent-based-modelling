from mesa import Agent
import math
from lib.direction import Direction


class Car(Agent):
    def __init__(self, unique_id, model, road, location, initial_direction, next_direction, velocity, acceleration, bmw_factor):
        """
        Creates the car

        :param unique_id: the id of the car
        :param model: the intersection model the car is on
        :param location: location of the car
        :param initial_direction: direction in which the car is headed before the intersection.
        2: to top, 6: to bottom, 0: to right, 4: to left
        :param next_direction: direction which car should take after intersection
        :param velocity: initial velocity of the car
        :param acceleration: speed at which a car can break and accelerate TODO: Maybe split into 2 parameters?
        :param bmw_factor: The likelihood of a person taking priority
        """
        super().__init__(unique_id, model)

        self.model = model
        self.road = road
        self.pos = location

        self.initial_direction = initial_direction
        self.current_direction = initial_direction
        self.next_direction = next_direction

        self.velocity = velocity
        self.acceleration = acceleration
        self.bmw_factor = bmw_factor
        self.length = 8
        self.width = 4

    def see(self):
        return True

    def next(self):
        # if velocity = 0, set time_at_queue = intersection.time_step
        return True

    def action(self):
        return True

    def calculate_stop_distance(self, new_velocity):
        # based on https://www.autoexamens.nl/remweg-berekenen/
        return math.ceil(new_velocity / 10 * 3 + (new_velocity / 10) ** 2)
       

    def approaching_another_vehicle(self, velocity, stop_distance):
        # @todo add the case where the another vehicle is not standing still
        free_space_ahead = 0
        cell_ahead = self.pos
        if self.initial_direction == Direction.RIGHT:
            cell_ahead = (self.pos[0] + self.length, self.pos[1])
        elif self.initial_direction == Direction.TOP:
            cell_ahead = (self.pos[0], self.pos[1] + self.length)
        elif self.initial_direction == Direction.LEFT:
            cell_ahead = (self.pos[0] - self.length, self.pos[1])
        elif self.initial_direction == Direction.BOTTOM:
            cell_ahead = (self.pos[0], self.pos[1] - self.length)

        while self.model.grid.is_cell_empty(cell_ahead):
            free_space_ahead += 1
            if self.initial_direction == Direction.RIGHT:
                x_position = self.pos[0] + self.length + free_space_ahead
                if not (0 < x_position < self.model.size):
                    return False
                cell_ahead = (x_position, self.pos[1])
            elif self.initial_direction == Direction.TOP:
                y_position = self.pos[1] + self.length + free_space_ahead
                if not (0 < y_position < self.model.size):
                    return False
                cell_ahead = (self.pos[0], y_position)
            elif self.initial_direction == Direction.LEFT:
                x_position = self.pos[0] - self.length - free_space_ahead
                if not (0 < x_position < self.model.size):
                    return False
                cell_ahead = (x_position, self.pos[1])
            elif self.initial_direction == Direction.BOTTOM:
                y_position = self.pos[1] - self.length - free_space_ahead
                if not (0 < y_position < self.model.size):
                    return False
                cell_ahead = (self.pos[0], y_position)
        # @todo introduce minimal_free_space_ahead?
        return free_space_ahead < 3

    # hoe werkt dit?
    def approaching_intersection(self, velocity, stop_distance):
        if self.initial_direction == Direction.RIGHT:
            if self.pos[0] + velocity + stop_distance >= self.model.size // 2 - 10:
                return True
        elif self.initial_direction == Direction.TOP:
            if self.pos[1] + velocity + stop_distance >= self.model.size // 2 - 10:
                return True
        elif self.initial_direction == Direction.LEFT:
            if self.pos[0] - velocity - stop_distance <= self.model.size // 2 + 8:
                return True
        elif self.initial_direction == Direction.BOTTOM:
            if self.pos[1] - velocity - stop_distance <= self.model.size // 2 + 8:
                return True

        return False

    def determine_action(self, velocity):
        # bad name for the function (unclear)
        stop_distance = self.calculate_stop_distance(velocity)
        # print(stop_distance)

        # if nearing other vehicle
        brake_because_vehicle = self.approaching_another_vehicle(velocity, stop_distance)

        # if nearing intersection
        brake_because_intersection = self.approaching_intersection(velocity, stop_distance)
        return brake_because_vehicle or brake_because_intersection

    # HELPERS
    def get_braking_speed(self, velocity):
        stop_distance = self.calculate_stop_distance(velocity)
        return int(velocity ** 2 / 2 * stop_distance)

    # CAR movement functions
    def brake(self):
        braking_speed = self.get_braking_speed(self.velocity)
        self.velocity -= braking_speed
        if self.velocity < 0:
            self.velocity = 0

    def update_velocity(self):
        # todo: slow down if car is in front
        new_velocity = self.velocity
        if self.velocity < self.road.max_speed:
            new_velocity = self.velocity + self.acceleration
            if self.velocity > self.road.max_speed:
                new_velocity = self.road.max_speed

        # print(self.pos)
        if self.determine_action(new_velocity):
            if not self.determine_action(self.velocity):
                # Continue with current speed
                return
            else:
                self.brake()
                return

        # continue while accelerating
        self.velocity = new_velocity

    def move(self):
        self.update_velocity()

        if self.initial_direction == Direction.RIGHT:
            self.model.grid.move_agent(self, (self.pos[0] + self.velocity, self.pos[1]))
        elif self.initial_direction == Direction.TOP:
            self.model.grid.move_agent(self, (self.pos[0], self.pos[1] + self.velocity))
        elif self.initial_direction == Direction.LEFT:
            self.model.grid.move_agent(self, (self.pos[0] - self.velocity, self.pos[1]))
        elif self.initial_direction == Direction.BOTTOM:
            self.model.grid.move_agent(self, (self.pos[0], self.pos[1] - self.velocity))

    def step(self):
        self.move()
