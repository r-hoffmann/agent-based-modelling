import math
import numpy as np

from mesa import Agent

from lib.Action import Action
from lib.Direction import Direction
from lib.Turn import Turn

SECTIONS_TO_LOCK = dict()

SECTIONS_TO_LOCK[Direction.NORTH] = [Direction.SOUTH_EAST, Direction.NORTH_EAST, Direction.NORTH_WEST,
                                     Direction.SOUTH_WEST]

SECTIONS_TO_LOCK[Direction.WEST] = [Direction.NORTH_EAST, Direction.NORTH_WEST, Direction.SOUTH_WEST,
                                    Direction.SOUTH_EAST]

SECTIONS_TO_LOCK[Direction.EAST] = [Direction.SOUTH_WEST, Direction.SOUTH_EAST, Direction.NORTH_EAST,
                                    Direction.NORTH_WEST]

SECTIONS_TO_LOCK[Direction.SOUTH] = [Direction.NORTH_WEST, Direction.SOUTH_WEST, Direction.SOUTH_EAST,
                                     Direction.NORTH_EAST]

"""
    Car:
        North: 103, 120
        East: 120, 112
        South: 112, 95
        West: 95, 103


    Stopline:
        North: 103, 110
        East: 110, 112
        South: 112, 105
        West: 105, 103
    """

SECTION_LOCATIONS = {
    Direction.EAST: (120, 103),
    Direction.NORTH_EAST: (112, 112),
    Direction.NORTH: (112, 120),
    Direction.NORTH_WEST: (103, 112),
    Direction.WEST: (95, 112),
    Direction.SOUTH_WEST: (103, 103),
    Direction.SOUTH: (103, 95),
    Direction.SOUTH_EAST: (112, 103)
}


class Car(Agent):
    def __init__(self, unique_id, model, road, location, initial_direction, next_direction, velocity, acceleration,
                 bmw_factor, start_step):
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

        self.id = unique_id  # for debugging

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
        self.width = 4
        self.following_vehicle = None

        # For long turn and u turn
        self.turning = False
        self.turn_completed = False
        self.turn_step = 0

        self.turn_type = self.get_turn_type()

        self.wait_counter = 0


        # idm
        self.safe_time_headway = 1.5
        self.maximum_acceleration = 1
        self.comfortable_deceleration = 2
        self.acceleration_component = 4
        self.minimum_distance = 2
        self.length = 8

    def idm_acceleration(self):
        v_alpha = self.maximum_acceleration * (1 - np.power(self.velocity / self.road.max_speed, self.acceleration_component))

        incoming_object = self.next_object()

        if incoming_object is not None:
            (pos, velocity) = incoming_object
            s_alpha = self.subtract_pos(pos) - self.length

            if s_alpha == 0:
                return -self.velocity

            s_star = self.minimum_distance + self.velocity * self.safe_time_headway + (self.velocity * (self.velocity - velocity)) / 2 * np.sqrt(self.maximum_acceleration * self.comfortable_deceleration)
            v_alpha += (-self.maximum_acceleration * np.power(s_star / s_alpha, 2))

        return int(np.round(v_alpha))

    def subtract_pos(self, pos):
        if self.current_direction == Direction.NORTH or self.current_direction == Direction.SOUTH:
            return np.abs(pos[1] - self.pos[1])
        elif self.current_direction == Direction.WEST or self.current_direction == Direction.EAST:
            return np.abs(pos[0] - self.pos[0])

    def next_object(self):
        """
        :return: ((x, y), velocity) | None
        """

        (x, y) = self.pos

        x_diff = 0
        y_diff = 0

        if self.current_direction == Direction.NORTH:
            y_diff = 1
        elif self.current_direction == Direction.EAST:
            x_diff = 1
        elif self.current_direction == Direction.SOUTH:
            y_diff = -1
        elif self.current_direction == Direction.WEST:
            x_diff = -1
        else:
            raise Exception("next_object() is called during turn")

        x += x_diff
        y += y_diff

        while 0 < x < self.model.size and 0 < y < self.model.size:
            if (x, y) == self.road.stop_line_pos:
                return (x, y), 0

            if not self.model.grid.is_cell_empty((x, y)):
                neighborhood = self.model.grid.get_neighbors((x, y), True, include_center=True, radius=0)

                for agent in neighborhood:
                    if isinstance(agent, Car):
                        return (x, y), agent.velocity

            x += x_diff
            y += y_diff

        return None

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

    def approaching_intersection(self):
        stop_distance = 10
        if self.current_direction == self.next_direction and self.initial_direction != self.next_direction:
            return False
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

    # Determine whether car is at intersection (either on the crossing or waiting at the stopline)
    def is_at_intersection(self):
        tl, br = self.model.intersection_corners
        tl_x = tl[0]
        tl_y = tl[1]
        br_x = br[0]
        br_y = br[1]
        if self.initial_direction == Direction.NORTH:
            br_y -= 8
        elif self.initial_direction == Direction.EAST:
            tl_x -= 8
        elif self.initial_direction == Direction.SOUTH:
            tl_y += 8
        elif self.initial_direction == Direction.WEST:
            br_x += 8

        if tl_x < self.pos[0] < br_x and br_y < self.pos[1] < tl_y:
            return True

        return self.is_at_stopline()

    def is_at_stopline(self):
        d = self.length + 2  # HARDCODED BADDD
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
        if not self.turning:
            self.intersection_move_ahead()
        else:
            self.intersection_turn()

    # Move straight ahead
    def intersection_move_ahead(self):
        self.action.accelerate(self.idm_acceleration())

        if self.current_direction == Direction.EAST:
            self.model.grid.move_agent(self, (self.pos[0] + self.velocity, self.pos[1]))
        elif self.current_direction == Direction.NORTH:
            self.model.grid.move_agent(self, (self.pos[0], self.pos[1] + self.velocity))
        elif self.current_direction == Direction.WEST:
            self.model.grid.move_agent(self, (self.pos[0] - self.velocity, self.pos[1]))
        elif self.current_direction == Direction.SOUTH:
            self.model.grid.move_agent(self, (self.pos[0], self.pos[1] - self.velocity))

    def turn_finished(self):
        self.turning = False
        if self.model.intersection_type == 'Fourway' or self.model.intersection_type == 'Equivalent':
            self.model.unlock_section(SECTIONS_TO_LOCK[self.initial_direction][self.turn_type - 1], self)
        self.turn_step = 0
        self.turn_completed = True

    def intersection_turn(self):
        self.intersection_move()

        if self.turn_step > self.turn_type:
            self.turn_finished()

    def next_turn_step(self):
        self.turn_step += 1
        self.turn_car()

        from_section = self.turn_step - 1
        if from_section < 0:
            from_section = 0
        self.lock_turn(from_section)

    def intersection_move(self):
        if int(self.current_direction) % 2 != 0:
            self.turn_car()

        self.action.accelerate(self.turn_acceleration())

        if self.turn_step < self.turn_type:
            moving_to = SECTIONS_TO_LOCK[self.initial_direction][self.turn_step]
        else:
            moving_to = self.next_direction

        (x, y) = self.pos
        (section_x, section_y) = SECTION_LOCATIONS[moving_to]

        if self.current_direction == Direction.EAST:
            x += self.velocity
            if x > section_x:
                x = section_x
                self.next_turn_step()
        elif self.current_direction == Direction.NORTH:
            y += self.velocity
            if y > section_y:
                y = section_y
                self.next_turn_step()
        elif self.current_direction == Direction.WEST:
            x -= self.velocity
            if x < section_x:
                x = section_x
                self.next_turn_step()
        elif self.current_direction == Direction.SOUTH:
            y -= self.velocity
            if y < section_y:
                y = section_y
                self.next_turn_step()

        self.model.grid.move_agent(self, (x, y))

    def turn_acceleration(self):
        # Max speed during turn
        max_speed = 5

        v_alpha = self.maximum_acceleration * (1 - np.power(self.velocity / max_speed, self.acceleration_component))

        return int(np.round(v_alpha))

    def turn_left(self):
        self.current_direction = Direction((int(self.current_direction) + 1) % 8)

    def turn_right(self):
        self.current_direction = Direction((int(self.current_direction) - 1) % 8)

    def turn_car(self):
        if self.turn_type == Turn.SHORT and self.turn_step == 1:
            self.turn_right()
        elif self.turn_type == Turn.LONG and self.turn_step == 2:
            self.turn_left()
        elif self.turn_type == Turn.U and self.turn_step in [2, 3]:
            self.turn_left()

    def wait(self, steps):
        self.wait_counter += steps

        if self.wait_counter > 0:
            self.wait_counter -= 1

    def lock_turn(self, from_section):
        if self.model.intersection_type == 'Fourway' or self.model.intersection_type == 'Equivalent':
            sections_to_lock = SECTIONS_TO_LOCK[self.initial_direction][from_section:self.turn_type]
            self.model.lock_sections(sections_to_lock, self)
            if from_section > 0:
                unlock_section = SECTIONS_TO_LOCK[self.initial_direction][from_section - 1]
                self.model.unlock_section(unlock_section, self)

    def can_turn(self):
        turn = SECTIONS_TO_LOCK[self.initial_direction][:self.turn_type]
        return not self.model.turn_is_locked(turn)

    def rightmost_car_that_could_cross(self):
        direction = (int(self.initial_direction) + 4) % 8

        for i in [2, 4, 6]:
            car = self.model.car_per_stopline[Direction((direction + i) % 8)]
            if car and car.can_turn() and not self.model.priority_queue[car]:
                return car

        return None

    def paths_cross(self, other_car):
        my_path = SECTIONS_TO_LOCK[self.initial_direction][:self.turn_type]
        other_path = SECTIONS_TO_LOCK[other_car.initial_direction][:other_car.turn_type]

        for section in my_path:
            if section in other_path:
                return True

        return False

    def equivalent_can_cross(self):
        # Make sure it won't cross paths with any cars that have priority
        for direction, car in self.model.car_per_stopline.items():
            if car is not None and car != self and self.model.priority_queue[car] and self.paths_cross(car):
                return False

        other_car = self.rightmost_car_that_could_cross()

        return other_car is None or not self.paths_cross(other_car)

    ''' Framework functions '''

    def advance(self):
        if self.turning:
            self.move()
        elif self.is_at_intersection():
            if self.model.intersection_type == 'Fourway':
                # set stop counter when car first arrives at the stopline
                if self.stop_step == 0:
                    self.stop_step = self.model.schedule.steps
                    self.road.first = self
                # ik sta stil maar wacht minstens 1 tijdstap
                elif self.road.first == self:
                    priority_queue = self.model.priority_queue

                    # get all cars that can go first
                    first_cars = [k for k, v in priority_queue.items() if v == min(priority_queue.values())]

                    if len(first_cars) == 1:
                        first = first_cars[0]
                    # if multiple cars come in, the one with the lowest bmw factor take priority
                    else:
                        tmp2 = {}

                        for car in first_cars:
                            tmp2[car] = car.bmw_factor

                        first = min(tmp2, key=tmp2.get)
                    # Car can move
                    if first == self and self.can_turn():
                        self.turning = True
                        self.road.first = None
                        self.lock_turn(0)
                        self.move()
                # while at intersection
                else:
                    self.move()
            elif self.model.intersection_type == 'Traffic lights':
                if not self.model.is_locked_section[self.current_direction] and (self.is_at_stopline() or self.approaching_intersection()):
                    self.turning = True
                    self.move()
                if self.turn_completed:
                    self.move()
            elif self.model.intersection_type == 'Equivalent':
                # ik sta stil maar wacht minstens 1 tijdstap
                # set stop counter when car first arrives at the stopline
                if self.stop_step == 0:
                    self.stop_step = self.model.schedule.steps
                    self.road.first = self
                elif self.road.first == self:
                    if self in self.model.priority_queue and self.model.priority_queue[self] or self.equivalent_can_cross():
                        if self.can_turn():
                            self.turning = True
                            self.road.first = None
                            self.lock_turn(0)
                            self.move()

                # while at intersection
                else:
                    self.move()
        else:
            self.action.accelerate(self.idm_acceleration())

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
        self.finish_step = self.model.schedule.steps
        self.model.grid.remove_agent(agent)
        self.model.schedule.remove(agent)
        self.model.finished_cars.append(agent)

    def __repr__(self):
        return str(self.id)

    def __str__(self):
        return self.__repr__()
