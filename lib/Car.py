from mesa import Agent
import math
import numpy as np
from lib.Direction import Direction
from lib.Turn import Turn
from lib.Action import Action


class Car(Agent):
    def __init__(self, unique_id, model, road, location, initial_direction, next_direction, velocity, acceleration, bmw_factor, start_step):
        """
        :param unique_id: the id of the car
        :param model: the intersection model the car is on
        :param location: location of the car
        :param initial_direction: direction in which the car is headed before the intersection.
        :param next_direction: direction which car should take after intersection
        :param velocity: initial velocity of the car
        :param acceleration: speed at which a car can break and accelerate TODO: Maybe split into 2 parameters?
        :param bmw_factor: The likelihood of a person taking priority
        """
        super().__init__(unique_id, model)

        self.id = unique_id # for debugging

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
        self.following_vehicle = None

        # For long turn and u turn
        self.turning = False
        self.turn_step = 0

        self.turn_type = self.get_turn_type()

        self.wait_counter = 0

    ''' Getters '''   
    # # Builds the priority queue for every first car in line to determine which car should go first
    # # @TODO: add BMW factor into decision making 
    # def get_priority_queue(self):
    #     first_cars = []
    #     for r in self.model.roads:
    #         first_cars.append(r.first)

    #     priority_queue = {}
    #     for fc in first_cars:
    #         if fc:
    #             priority_queue[fc] = fc.stop_step
    #         else:
    #             priority_queue[None] = np.inf

    #     k = [(k, priority_queue[k]) for k in sorted(priority_queue, key=priority_queue.get)]
    #     return k

    # Defines the type of turn a car is going to make at the intersection
    def get_turn_type(self):   
        if Direction(self.next_direction).is_opposite(self.initial_direction):
            return Turn.U
        elif Direction(self.next_direction).is_equal(self.current_direction):
            return Turn.STRAIGHT
        elif self.initial_direction == Direction.NORTH:
            if self.next_direction == Direction.EAST:
                return Turn.SHORT
            elif self.next_direction == Direction.WEST:
                return Turn.LONG
        elif self.initial_direction == Direction.SOUTH:
            if self.next_direction == Direction.WEST:
                return Turn.SHORT
            elif self.next_direction == Direction.EAST:
                return Turn.LONG
        elif self.initial_direction == Direction.WEST:
            if self.next_direction == Direction.NORTH:
                return Turn.SHORT
            elif self.next_direction == Direction.SOUTH:
                return Turn.LONG
        elif self.initial_direction == Direction.EAST:
            if self.next_direction == Direction.SOUTH:
                return Turn.SHORT
            elif self.next_direction == Direction.NORTH:
                return Turn.LONG
        else:
            raise ValueError('Unknown turn type')

    ''' ... '''
    # Calculate stop distance based on https://www.autoexamens.nl/remweg-berekenen/
    def calculate_stop_distance(self, velocity):        
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

    # bad name for the function (unclear)
    def should_brake(self, velocity):
        stop_distance = self.calculate_stop_distance(velocity)

        # if nearing other vehicle
        brake_because_vehicle = self.approaching_another_vehicle(stop_distance)

        # if nearing intersection
        brake_because_intersection = self.approaching_intersection(stop_distance)
        return brake_because_vehicle or brake_because_intersection

    def should_accelerate(self):
        return self.velocity < self.road.max_speed and not self.should_brake(min(self.velocity + self.acceleration, self.road.max_speed))

    def get_braking_speed(self):
        stop_distance = self.calculate_stop_distance(self.velocity)
        return int(self.velocity ** 2 / 2 * stop_distance)

    # Determine wheter car is at intersection (either on the crossing or waiting at the stopline)
    def is_at_intersection(self):
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
        return self.is_at_stopline()

    def is_at_stopline(self):
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

    ''' Directions a car can move to at the intersection ''' 
    def move(self):
        if self.current_direction == self.next_direction:
            self.intersection_move_ahead()
        elif self.turn_type == Turn.LONG:
            self.intersection_long_turn()
        elif self.turn_type == Turn.U:
            self.intersection_u_turn()
        elif self.turn_type == Turn.SHORT:
            self.intersection_short_turn()

    # Move straight ahead
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

    # Take a short turn
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

    # Take a long turn
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

    # Take a u turn
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

    # Helpers:
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

    def wait(self, steps):
        self.wait_counter += steps


        if self.wait_counter > 0:
            self.wait_counter -= 1
        


    ''' Framework functions '''
    def advance(self):
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
            self.move()
        elif self.is_at_intersection():
            # set stop counter when car first arrives at the stopline
            if self.stop_step == 0:
                self.stop_step = self.model.schedule.steps
                self.road.first = self
            # ik sta stil maar wacht minstens 1 tijdstap
            elif self.road.first == self:
                priority_queue = self.model.priority_queue

                # get all cars that can go first
                first_cars = [k for k,v in priority_queue.items() if v == min(priority_queue.values())]

                if len(first_cars) == 1:
                    first = first_cars[0]
                # if multiple cars come in, the one with the lowest bmw factor take priority
                else:
                    tmp2 = {}

                    for car in first_cars:
                        tmp2[car] = car.bmw_factor

                    first = min(tmp2, key=tmp2.get)
                # Car can move
                if first == self:
                    self.road.first = None
                    self.move()
            # while at intersection
            else:
                self.move()
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

    def remove_car(self, agent):
        self.model.grid.remove_agent(agent)
        self.model.schedule.remove(agent)