from mesa import Agent
import math
import numpy as np
from lib.Direction import Direction
from lib.Action import Action


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

        self.id = unique_id

        self.model = model
        self.action = Action(self)
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
        self.priority_queue = 0
        self.following_vehicle = None

        # For long turn and u turn
        self.turning = False
        self.turn_step = 0

    def calculate_stop_distance(self, velocity):
        # based on https://www.autoexamens.nl/remweg-berekenen/
        return math.ceil(velocity / 10 * 3 + (velocity / 10) ** 2)

    def approaching_another_vehicle(self, stop_distance):
        self.following_vehicle = None
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

        self.following_vehicle = self.model.grid[cell_ahead[0]][cell_ahead[1]]
        return free_space_ahead < stop_distance

    # hoe werkt dit?
    def approaching_intersection(self, stop_distance):
        if self.initial_direction == Direction.EAST and self.pos[0] < self.model.size // 2 - 10:
            if self.pos[0] + self.velocity + stop_distance >= self.model.size // 2 - 10:
                return True
        elif self.initial_direction == Direction.NORTH and self.pos[1] < self.model.size // 2 - 10:
            if self.pos[1] + self.velocity + stop_distance >= self.model.size // 2 - 10:
                return True
        elif self.initial_direction == Direction.WEST and self.pos[0] > self.model.size // 2 + 8:
            if self.pos[0] - self.velocity - stop_distance <= self.model.size // 2 + 8:
                return True
        elif self.initial_direction == Direction.SOUTH and self.pos[1] > self.model.size // 2 + 8:
            if self.pos[1] - self.velocity - stop_distance <= self.model.size // 2 + 8:
                return True

        return False

    def should_brake(self, velocity):
        # bad name for the function (unclear)
        stop_distance = self.calculate_stop_distance(velocity)

        # if nearing other vehicle
        brake_because_vehicle = self.approaching_another_vehicle(stop_distance)

        # if nearing intersection
        brake_because_intersection = self.approaching_intersection(stop_distance)
        return brake_because_vehicle or brake_because_intersection

    def should_accelerate(self):
        return self.velocity < self.road.max_speed and not self.should_brake(min(self.velocity + self.acceleration, self.road.max_speed))

    # HELPERS
    def get_braking_speed(self):
        stop_distance = self.calculate_stop_distance(self.velocity)
        return int(self.velocity ** 2 / 2 * stop_distance)

    def at_intersection(self):
        tl, br =  self.model.intersection_corners
        tl_x = tl[0]
        tl_y = tl[1]
        br_x = br[0]
        br_y = br[1]
        if self.initial_direction == Direction.NORTH:
            br_y -= 8
        elif self.initial_direction == Direction.EAST:
            br_x -= 8
        elif self.initial_direction == Direction.SOUTH:
            tl_y += 8
        elif self.initial_direction == Direction.WEST:
            tl_x += 8

        if tl_x < self.pos[0] < br_x and br_y < self.pos[1] < tl_y:
            return True
        return self.at_stopline()

    def at_stopline(self):
        # for some reason, the stop position of the car is always 9 cells away from the actual stopline, thus:
        d = self.length + 1  # HARDCODED BADDD
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
        self.action.accelerate()
        if self.current_direction == Direction.EAST:
            self.model.grid.move_agent(self, (self.pos[0] + self.velocity, self.pos[1]))
        elif self.current_direction == Direction.NORTH:
            self.model.grid.move_agent(self, (self.pos[0], self.pos[1] + self.velocity))
        elif self.current_direction == Direction.WEST:
            self.model.grid.move_agent(self, (self.pos[0] - self.velocity, self.pos[1]))
        elif self.current_direction == Direction.SOUTH:
            self.model.grid.move_agent(self, (self.pos[0], self.pos[1] - self.velocity))

    def u_turn(self):
        return (int(self.initial_direction) + 4) % 8 == int(self.next_direction)

    def long_turn(self):
        # Checks if a car will make a long turn at a intersection
        if self.initial_direction == Direction.NORTH and self.next_direction == Direction.WEST:
            return True
        elif self.initial_direction == Direction.SOUTH and self.next_direction == Direction.EAST:
            return True
        elif self.initial_direction == Direction.WEST and self.next_direction == Direction.SOUTH:
            return True
        elif self.initial_direction == Direction.EAST and self.next_direction == Direction.NORTH:
            return True
        return False

    def short_turn(self):
        if self.initial_direction == Direction.NORTH and self.next_direction == Direction.EAST:
            return True
        elif self.initial_direction == Direction.SOUTH and self.next_direction == Direction.WEST:
            return True
        elif self.initial_direction == Direction.WEST and self.next_direction == Direction.NORTH:
            return True
        elif self.initial_direction == Direction.EAST and self.next_direction == Direction.SOUTH:
            return True
        return False

    def intersection_long_turn(self):
        self.turning = True

        if self.turn_step == 0:
            self.intersection_step_direction(direction=self.current_direction)
        elif self.turn_step == 1:
            self.intersection_step_direction(self.current_direction)
            self.intersection_step_turn(turn_left=True)
        else:
            next_direction = (int(self.current_direction) + 2) % 8
            if next_direction % 2 != 0:
                next_direction -= 1

            self.intersection_step_direction(direction=Direction(next_direction))
            self.intersection_step_turn(turn_left=True)
            self.turning = False
            self.turn_step = 0
            return

        self.turn_step += 1

    def intersection_u_turn(self):
        self.turning = True

        if self.turn_step == 0:
            self.intersection_step_direction(direction=self.current_direction)
        elif self.turn_step == 1:
            self.intersection_step_direction(direction=self.current_direction)
            self.intersection_step_turn(turn_left=True)
        elif self.turn_step == 2:
            next_direction = (int(self.current_direction) + 2) % 8
            if next_direction % 2 != 0:
                next_direction -= 1

            self.intersection_step_direction(direction=Direction(next_direction))
            self.intersection_step_turn(turn_left=True)
            self.intersection_step_turn(turn_left=True)
        else:
            next_direction = (int(self.current_direction) + 2) % 8
            if next_direction % 2 != 0:
                next_direction -= 1

            self.intersection_step_direction(direction=Direction(next_direction))
            self.intersection_step_turn(turn_left=True)
            self.turning = False
            self.turn_step = 0
            return

        self.turn_step += 1

    def intersection_step_direction(self, direction):
        step_size = 13
        if self.turn_step > 0:
            step_size = 8

        if direction == Direction.EAST:
            self.model.grid.move_agent(self, (self.pos[0] + step_size, self.pos[1]))
        elif direction == Direction.NORTH:
            self.model.grid.move_agent(self, (self.pos[0], self.pos[1] + step_size))
        elif direction == Direction.WEST:
            self.model.grid.move_agent(self, (self.pos[0] - step_size, self.pos[1]))
        elif direction == Direction.SOUTH:
            self.model.grid.move_agent(self, (self.pos[0], self.pos[1] - step_size))

    def intersection_step_turn(self, turn_left):
        if turn_left:
            self.current_direction = Direction((int(self.current_direction) + 1) % 8)
        else:
            self.current_direction = Direction((int(self.current_direction) - 1) % 8)

    def intersection_short_turn(self):
        x = self.pos[0]
        y = self.pos[1]

        if self.current_direction == Direction.NORTH and self.next_direction == Direction.EAST:
            y += 14
            self.current_direction = Direction.NORTH_EAST
        elif self.initial_direction == Direction.NORTH and self.current_direction == Direction.NORTH_EAST:
            x += 14
            self.current_direction = Direction.EAST
        elif self.current_direction == Direction.EAST and self.next_direction == Direction.SOUTH:
            x += 14
            self.current_direction = Direction.SOUTH_EAST
        elif self.initial_direction == Direction.EAST and self.current_direction == Direction.SOUTH_EAST:
            y -= 14
            self.current_direction = Direction.SOUTH
        elif self.current_direction == Direction.SOUTH and self.next_direction == Direction.WEST:
            y -= 14
            self.current_direction = Direction.SOUTH_WEST
        elif self.initial_direction == Direction.SOUTH and self.current_direction == Direction.SOUTH_WEST:
            x -= 14
            self.current_direction = Direction.WEST
        elif self.current_direction == Direction.WEST and self.next_direction == Direction.NORTH:
            x -= 14
            self.current_direction = Direction.NORTH_WEST
        elif self.initial_direction == Direction.WEST and self.current_direction == Direction.NORTH_WEST:
            y += 14
            self.current_direction = Direction.NORTH

        self.model.grid.move_agent(self, (x, y))

    def remove_car(self, agent):
        self.model.grid.remove_agent(agent)
        self.model.schedule.remove(agent)

    def get_priority_queue(self):
        first_cars = []

        roads = self.model.roads

        for r in roads:
            first_cars.append(r.first)

        priority_queue = {}

        for fc in first_cars:
            if fc:
                priority_queue[fc] = fc.stop_step
            else:
                priority_queue[None] = np.inf

        o = priority_queue

        k = [(k, o[k]) for k in sorted(priority_queue, key=o.get)]
        return k

    def go_direction(self):
        # if car goes straight ahead
        if self.current_direction == self.next_direction:
            self.intersection_move_ahead()
        # MAKE TURN LEFT OR RIGHT
        else:
            if self.long_turn():
                self.intersection_long_turn()
            elif self.short_turn():
                self.intersection_short_turn()
            elif self.u_turn():
                self.intersection_u_turn()

    def move(self):
        if self.should_brake(self.velocity):
            goal_speed = 0
            if self.following_vehicle is not None:
                if type(self.following_vehicle) == set:
                    self.following_vehicle = next(iter(self.following_vehicle))
                goal_speed = self.following_vehicle.velocity
            self.action.brake(goal_speed)
        elif self.should_accelerate():
            self.action.accelerate()

        if self.turning:
            self.go_direction()
        elif self.at_intersection():
            # set stop counter when car first arrives at the stopline
            if self.stop_step == 0:
                self.stop_step = self.model.schedule.steps
                self.road.first = self
            # ik sta stil maar wacht minstens 1 tijdstap
            elif self.road.first == self:
                self.priority_queue = self.get_priority_queue()

                first, _ = next(iter(self.priority_queue))
                if first == self:
                    self.road.first = None

                    self.go_direction()
            else:
                self.go_direction()
        else:
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

    def step(self):
        self.move()
