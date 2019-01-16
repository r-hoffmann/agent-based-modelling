from mesa import Agent
import math
from lib.direction import Direction


class Car(Agent):
    def __init__(self, unique_id, model, road, location, initial_direction, next_direction, velocity, acceleration, bmw_factor, start_step):
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

        self.start_step = start_step
        self.stop_step = 0

        self.velocity = velocity
        self.acceleration = acceleration
        self.bmw_factor = bmw_factor
        self.length = 8
        self.width = 4

    def see(self, direction):

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
        if self.initial_direction == Direction.EAST:
            cell_ahead = (self.pos[0] + self.length, self.pos[1])
        elif self.initial_direction == Direction.NORTH:
            cell_ahead = (self.pos[0], self.pos[1] + self.length)
        elif self.initial_direction == Direction.WEST:
            cell_ahead = (self.pos[0] - self.length, self.pos[1])
        elif self.initial_direction == Direction.SOUTH:
            cell_ahead = (self.pos[0], self.pos[1] - self.length)

        if 0 < cell_ahead[0] < self.model.size and 0 < cell_ahead[1] < self.model.size:
            while self.model.grid.is_cell_empty(cell_ahead):
                free_space_ahead += 1
                if self.initial_direction == Direction.EAST:
                    x_position = self.pos[0] + self.length + free_space_ahead
                    if not (0 < x_position < self.model.size):
                        return False
                    cell_ahead = (x_position, self.pos[1])
                elif self.initial_direction == Direction.NORTH:
                    y_position = self.pos[1] + self.length + free_space_ahead
                    if not (0 < y_position < self.model.size):
                        return False
                    cell_ahead = (self.pos[0], y_position)
                elif self.initial_direction == Direction.WEST:
                    x_position = self.pos[0] - self.length - free_space_ahead
                    if not (0 < x_position < self.model.size):
                        return False
                    cell_ahead = (x_position, self.pos[1])
                elif self.initial_direction == Direction.SOUTH:
                    y_position = self.pos[1] - self.length - free_space_ahead
                    if not (0 < y_position < self.model.size):
                        return False
                    cell_ahead = (self.pos[0], y_position)
        else:
            return False
        # @todo introduce minimal_free_space_ahead?
        return free_space_ahead < 3

    # hoe werkt dit?
    def approaching_intersection(self, velocity, stop_distance):
        if self.initial_direction == Direction.EAST and self.pos[0] < self.model.size // 2 - 10:
            if self.pos[0] + velocity + stop_distance >= self.model.size // 2 - 10:
                return True
        elif self.initial_direction == Direction.NORTH and self.pos[1] < self.model.size // 2 - 10:
            if self.pos[1] + velocity + stop_distance >= self.model.size // 2 - 10:
                return True
        elif self.initial_direction == Direction.WEST and self.pos[0] > self.model.size // 2 + 8:
            if self.pos[0] - velocity - stop_distance <= self.model.size // 2 + 8:
                return True
        elif self.initial_direction == Direction.SOUTH and self.pos[1] > self.model.size // 2 + 8:
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


    def at_intersection(self):
        # for some reason, the stop position of the car is always 9 cells away from the actual stopline, thus:
        d = 9 # HARDCODED BADDD

        if self.current_direction == Direction.EAST and (self.pos[0] + d == self.road.stop_line_pos[0]):
            return True        
        elif self.current_direction == Direction.WEST and (self.pos[0] - d == self.road.stop_line_pos[0]):
            return True
        elif self.current_direction == Direction.NORTH and (self.pos[1] + d == self.road.stop_line_pos[1]):
            return True
        elif self.current_direction == Direction.SOUTH and (self.pos[1] - d == self.road.stop_line_pos[1]):
            return True

        return False

    def intersection_move_ahead(self):
        self.velocity += self.acceleration
        if self.current_direction == Direction.EAST:
           self.model.grid.move_agent(self, (self.pos[0] + self.velocity, self.pos[1]))
        elif self.current_direction == Direction.NORTH:
            self.model.grid.move_agent(self, (self.pos[0], self.pos[1] + self.velocity))
        elif self.current_direction == Direction.WEST:
            self.model.grid.move_agent(self, (self.pos[0] - self.velocity, self.pos[1]))
        elif self.current_direction == Direction.SOUTH:
            self.model.grid.move_agent(self, (self.pos[0], self.pos[1] - self.velocity))

    def intersection_long_turn(self):
        pass

    def intersection_short_turn(self):
        pass

    def remove_car(self, agent):
        self.model.grid.remove_agent(agent)
        self.model.schedule.remove(agent)

    def move(self):
        self.update_velocity()

        if self.at_intersection() == False:
            if self.current_direction == Direction.EAST:
                if self.pos[0] + self.velocity >= self.model.size:
                    self.remove_car(self)
                else:
                    self.model.grid.move_agent(self, (self.pos[0] + self.velocity, self.pos[1]))
            elif self.current_direction == Direction.NORTH:
                if self.pos[1] + self.velocity >= self.model.size:
                    self.remove_car(self)
                else:
                    self.model.grid.move_agent(self, (self.pos[0], self.pos[1] + self.velocity))
            elif self.current_direction == Direction.WEST:
                if self.pos[0] - self.velocity < 0:
                    self.remove_car(self)
                else:
                    self.model.grid.move_agent(self, (self.pos[0] - self.velocity, self.pos[1]))
            elif self.current_direction == Direction.SOUTH:
                if self.pos[1] - self.velocity < 0:
                    self.remove_car(self)
                else:
                    self.model.grid.move_agent(self, (self.pos[0], self.pos[1] - self.velocity))
        else:
            print('test')
            print(self.current_direction, self.next_direction)
            # set stop counter when car first arives at the stopline
            if self.velocity == 0 and self.stop_step == 0:
                self.stop_step = self.model.schedule.steps
                print(self.stop_step)
            # if car goes straight ahead
            if self.current_direction == self.next_direction:
                self.intersection_move_ahead()
            else:
                pass




    def step(self):
        self.move()
