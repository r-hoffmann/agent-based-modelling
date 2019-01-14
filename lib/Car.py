from mesa import Agent
import math


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

    def determine_action(self, velocity):
        # bad name for the function (unclear)
        stop_distance = self.calculate_stop_distance(velocity)
        # print(stop_distance)

        # if nearing intersection
        if self.initial_direction == 0:
            if self.pos[0] + velocity + stop_distance >= self.model.size // 2 - 10:
                return True
        elif self.initial_direction == 2:
            if self.pos[1] + velocity + stop_distance >= self.model.size // 2 - 10:
                return True
        elif self.initial_direction == 4:
            if self.pos[0] - velocity - stop_distance <= self.model.size // 2 + 8:
                return True
        elif self.initial_direction == 6:
            if self.pos[1] - velocity - stop_distance <= self.model.size // 2 + 8:
                return True

        return False

    def calculate_braking_speed(self, velocity):
        stop_distance = self.calculate_stop_distance(velocity)
        return int(velocity ** 2 / 2 * stop_distance)

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
                # Continue while braking
                braking_speed = self.calculate_braking_speed(self.velocity)
                self.velocity -= braking_speed
                if self.velocity < 0:
                    self.velocity = 0
                return

        # continue while accelerating
        self.velocity = new_velocity

    def move(self):
        self.update_velocity()

        if self.initial_direction == 0:
            self.model.grid.move_agent(self, (self.pos[0] + self.velocity, self.pos[1]))
        elif self.initial_direction == 2:
            self.model.grid.move_agent(self, (self.pos[0], self.pos[1] + self.velocity))
        elif self.initial_direction == 4:
            self.model.grid.move_agent(self, (self.pos[0] - self.velocity, self.pos[1]))
        elif self.initial_direction == 6:
            self.model.grid.move_agent(self, (self.pos[0], self.pos[1] - self.velocity))

    def step(self):
        self.move()
