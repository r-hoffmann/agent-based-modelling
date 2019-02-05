import numpy as np
import pandas as pd

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation

from lib.Direction import Direction
from lib.Road import Road
from lib.VisualisationSquare import VisualisationSquare
from lib.Turn import Turn


class Intersection(Model):
    def __init__(self, **args):
        # @TODO: can/should be made different on different roads
        super().__init__()
        self.parameters = []
        if 'parameters_as_dict' in args:
            for field in args['parameters']:
                setattr(self, field, args['parameters'][field])
                self.parameters.append(field)
        else:
            for field in args:
                setattr(self, field, args[field])
                self.parameters.append(field)


        self.roads = []
        self.create_roads()
        self.cars = []
        self.cars_removed = 0
        self.finished_cars = []

        # Visualisation
        self.bins = list(range(10))

        self.is_locked_section = {
            Direction.NORTH_WEST: False,
            Direction.NORTH_EAST: False,
            Direction.SOUTH_WEST: False,
            Direction.SOUTH_EAST: False,
            Direction.NORTH: True,
            Direction.WEST: True,
            Direction.EAST: True,
            Direction.SOUTH: True,
        }

        self.locked_by = {
            Direction.NORTH_WEST: None,
            Direction.NORTH_EAST: None,
            Direction.SOUTH_WEST: None,
            Direction.SOUTH_EAST: None
        }

        # size 216x216 is big enough to hold 10 cars per lane and the intersection
        self.size = 216
        self.grid = MultiGrid(self.size, self.size, True)
        self.schedule = SimultaneousActivation(self)
        self.average_speed = DataCollector({"Average speed": lambda m: self.get_average_speed()})
        self.mean_crossover = DataCollector({"Mean crossover time": lambda m: self.get_mean_crossover()})
        self.mean_crossover_hist = DataCollector({"Mean crossover histogram": lambda m: self.get_mean_crossover_hist()})
        self.throughput = DataCollector({"Throughput": lambda m: self.get_throughput()})
        self.waiting_cars = DataCollector({"Number of waiting cars": lambda m: self.get_waiting_cars()})
        self.number_of_locked_sections = DataCollector(
            {"Number of locked sections": lambda m: self.get_number_of_locked_sections()})

        self.running = True
        self.average_speed.collect(self)
        self.mean_crossover.collect(self)
        self.mean_crossover_hist.collect(self)
        self.throughput.collect(self)
        self.waiting_cars.collect(self)
        self.number_of_locked_sections.collect(self)

        self.intersection_corners = self.get_intersection_corners()
        self.visualisations = []

        intersection_to_visualisation_function = {
            'Fourway': lambda m: fourway_get_visualisations(m),
            'Traffic lights': lambda m: trafficlights_get_visualisations(m),
            'Equivalent': lambda m: fourway_get_visualisations(m),
            'Smart lights': lambda m: trafficlights_get_visualisations(m)
        }

        self.visualisation_function = intersection_to_visualisation_function[self.intersection_type]
        self.priority_queue = None
        self.car_per_stopline = {}

        if self.seed == 0:
            self.rnd = np.random.RandomState()
        else:
            self.rnd = np.random.RandomState(self.seed)

        self.alpha_factor = 2
        self.beta_factor = 5

        # If BMW factor of a car is bigger than this value it is a BMW
        self.bmw_threshold = self.calculate_bmw_threshold()

        self.smart_lights_counter = 0
        self.green_light_direction = None

    def calculate_bmw_threshold(self):
        data = np.array([np.random.beta(self.alpha_factor, self.beta_factor) for _ in range(10000)])

        for x in np.arange(0, 1, 0.001):
            if len(data[data < x]) / len(data) >= 1 - self.bmw_fraction:
                return x

        return 1

    def section_is_locked(self, direction):
        return self.is_locked_section[direction]

    def turn_is_locked(self, directions):
        for direction in directions:
            if self.section_is_locked(direction):
                return True
        return False

    def lock_sections(self, directions, car):
        for direction in directions:
            if not self.locked_by[direction] in [None, car]:
                raise Exception('Car tries to lock section which is not his. ' + str(self.locked_by[direction]) + ' != ' + str(car))
            self.is_locked_section[direction] = True
            self.locked_by[direction] = car

    def unlock_section(self, direction, car):
        if self.locked_by[direction] in [None, car]:
            self.is_locked_section[direction] = False
            self.locked_by[direction] = None
        else:
            raise Exception('Car tries to unlock section which is not his. ' + str(self.locked_by[direction]) + ' != ' + str(car))

    def get_intersection_corners(self):
        lane_width = 8

        mid_x = self.size // 2
        mid_y = self.size // 2

        tl_x = mid_x - lane_width
        tl_y = mid_y + lane_width

        br_x = mid_x + lane_width
        br_y = mid_y - lane_width

        points = []
        points.append((tl_x, tl_y))
        points.append((br_x, br_y))

        return points

    def create_roads(self):
        self.roads.append(
            Road(
                self,
                (103, 215),
                Direction.SOUTH,
                self.p_car_spawn_north,
                [
                    self.p_north_to_east,
                    self.p_north_to_north,
                    self.p_north_to_west,
                    self.p_north_to_south,
                ],
                self.max_speed_vertical
            )
        )

        self.roads.append(
            Road(
                self,
                (0, 103),
                Direction.EAST,
                self.p_car_spawn_west,
                [
                    self.p_west_to_east,
                    self.p_west_to_north,
                    self.p_west_to_west,
                    self.p_west_to_south,
                ],
                self.max_speed_horizontal
            )
        )

        self.roads.append(
            Road(
                self,
                (215, 112),
                Direction.WEST,
                self.p_car_spawn_east,
                [
                    self.p_east_to_east,
                    self.p_east_to_north,
                    self.p_east_to_west,
                    self.p_east_to_south,
                ],
                self.max_speed_horizontal
            )
        )

        self.roads.append(
            Road(
                self,
                (112, 0),
                Direction.NORTH,
                self.p_car_spawn_south,
                [
                    self.p_south_to_east,
                    self.p_south_to_north,
                    self.p_south_to_west,
                    self.p_south_to_south,
                ],
                self.max_speed_vertical
            )
        )

    def step(self):
        for road in self.roads:
            road.step()

            if road.free_space and len(road.car_queue) > 0:
                car = road.car_queue.pop()
                self.schedule.add(car)
                self.grid.grid[car.pos[0]][car.pos[1]].add(car)
                car.start_step = self.schedule.steps

        if self.intersection_type == 'Fourway':
            self.update_fourway_priority_queue()
        elif self.intersection_type == 'Equivalent':
            self.get_car_per_stopline()
            self.update_equivalent_priority_queue()

        self.schedule.step()

        self.average_speed.collect(self)
        self.throughput.collect(self)
        self.mean_crossover.collect(self)
        self.mean_crossover_hist.collect(self)
        self.waiting_cars.collect(self)
        self.number_of_locked_sections.collect(self)

        if self.intersection_type == 'Traffic lights':
            rotate_trafficlights(self)
        elif self.intersection_type == 'Smart lights':
            self.smart_traffic_lights()

        self.visualisation_function(self)

    # Simple traffic light logic
    def smart_traffic_lights(self):
        cars_per_road = {}
        total = 0
        for road in self.roads:
            cars = road.count_cars_before_stopline()
            total += cars
            cars_per_road[road.direction] = cars

        if self.green_light_direction and cars_per_road[self.green_light_direction] == 0:
            self.smart_lights_counter = max(10, self.smart_lights_counter)
            directions = [Direction.NORTH, Direction.EAST, Direction.WEST, Direction.SOUTH]
            for direction in directions:
                self.is_locked_section[direction] = True

        if self.smart_lights_counter == 0:
            if total == 0:
                self.green_light_direction = None
                directions = [Direction.NORTH, Direction.EAST, Direction.WEST, Direction.SOUTH]
                for direction in directions:
                    self.is_locked_section[direction] = True
            else:
                x = self.rnd.randint(0, total)
                current_count = 0

                for direction, cars in cars_per_road.items():
                    current_count += cars

                    if x < current_count:
                        self.green_light_direction = direction
                        break

                directions = [Direction.NORTH, Direction.EAST, Direction.WEST, Direction.SOUTH]
                for direction in directions:
                    self.is_locked_section[direction] = (direction != self.green_light_direction)

                if self.green_light_direction == Direction.NORTH:
                    self.smart_lights_counter = self.t_from_north + 10
                elif self.green_light_direction == Direction.EAST:
                    self.smart_lights_counter = self.t_from_east + 10
                elif self.green_light_direction == Direction.SOUTH:
                    self.smart_lights_counter = self.t_from_south + 10
                elif self.green_light_direction == Direction.WEST:
                    self.smart_lights_counter = self.t_from_west + 10
                else:
                    raise Exception('Invalid green light direction')
        else:
            if self.smart_lights_counter <= 10:
                directions = [Direction.NORTH, Direction.EAST, Direction.WEST, Direction.SOUTH]
                for direction in directions:
                    self.is_locked_section[direction] = True

            self.smart_lights_counter -= 1

    def update_fourway_priority_queue(self):
        priority_queue = {}
        for road in self.roads:
            if road.first:
                if road.first.bmw_factor >= self.bmw_threshold:
                    priority_queue[road.first] = 0
                else:
                    priority_queue[road.first] = road.first.stop_step

        self.priority_queue = priority_queue

    def get_car_per_stopline(self):
        for road in self.roads:
            self.car_per_stopline[Direction((int(road.direction) + 4) % 8)] = road.car_at_stopline()

    def update_equivalent_priority_queue(self):
        # Make sure their are cars in the priority queue
        if len([car for car in self.car_per_stopline.values() if car]) == 0:
            self.priority_queue = {}
            return

        priority_queue = {}

        # Normal rules
        for direction, car in self.car_per_stopline.items():
            if car:
                car_to_right = self.car_per_stopline[Direction((int(direction) + 2) % 8)]
                car_across = self.car_per_stopline[Direction((int(direction) + 4) % 8)]

                priority_queue[car] = True

                if car_to_right:
                    if car.turn_type == Turn.SHORT:
                        if car_to_right.turn_type == Turn.U:
                            priority_queue[car] = False
                    else:
                        priority_queue[car] = False

                if car_across and car_across.turn_type == Turn.STRAIGHT:
                    priority_queue[car] = False

        # BMW takes priority
        highest_bmw = max([(car, car.bmw_factor) for car in self.car_per_stopline.values() if car], key=lambda x: x[1])
        if highest_bmw[1] >= self.bmw_threshold:
            priority_queue[highest_bmw[0]] = True

            for _, car in self.car_per_stopline.items():
                if car and car != highest_bmw[0]:
                    priority_queue[car] = False

            self.priority_queue = priority_queue
            return

        # Nobody can take priority
        if len(priority_queue) > 0 and sum([1 for _, has_priority in priority_queue.items() if has_priority]) == 0:
            cars = [(car, car.stop_step) for car in priority_queue if car.road.first == car]
            first_cars = [car for (car, stop_step) in cars if stop_step == min(cars, key=lambda x: x[1])[1]]

            if len(first_cars) == 4:
                # Highest BMW factor takes priority
                priority_queue[max(priority_queue.keys(), key=(lambda k: priority_queue[k]))] = True

            else:
                for car in first_cars:
                    car_to_right = self.car_per_stopline[Direction((int(car.current_direction) - 2) % 8)]

                    if car_to_right is None or car_to_right.stop_step != car.stop_step:
                        priority_queue[car] = True
                        break

        self.priority_queue = priority_queue

    def run_model(self, n=100):
        for _ in range(n):
            self.step()

    def get_average_speed(self):
        number_of_agents = len(self.schedule.agents)
        if number_of_agents > 0:
            return sum([agent.velocity for agent in self.schedule.agents]) / number_of_agents
        return 0

    def get_throughput(self):
        if self.schedule.steps > 0:
            return len(self.finished_cars) / self.schedule.steps
        return 0

    def get_mean_crossover(self):
        # print([(agent.stop_step, agent.start_step) for agent in self.finished_cars])
        if len(self.finished_cars) > 0:
            return sum([agent.finish_step - agent.start_step for agent in self.finished_cars]) / len(self.finished_cars)
        return 0

    def get_mean_crossover_hist(self):
        if len(self.finished_cars) > 0:
            crossover_vals = [agent.finish_step - agent.start_step for agent in self.finished_cars]
            hist = np.histogram(crossover_vals, bins=self.bins)[0]
            return [int(x) for x in hist]
        return [0]

    def get_waiting_cars(self):
        return sum([1 for agent in self.schedule.agents if agent.velocity == 0])

    def get_number_of_locked_sections(self):
        return sum([1 for s in self.is_locked_section if self.is_locked_section[s]])


def fourway_get_visualisations(intersection):
    # Make visualisations
    for v in intersection.visualisations:
        intersection.grid.remove_agent(v)
    intersection.visualisations = []
    lane_width = 6
    mid_x = intersection.size // 2 + 2
    mid_y = intersection.size // 2 + 2

    middle_squares = [
        [mid_x - lane_width, mid_y - lane_width, intersection.is_locked_section[Direction.SOUTH_WEST]],
        [mid_x + 2, mid_y - lane_width, intersection.is_locked_section[Direction.SOUTH_EAST]],
        [mid_x - lane_width, mid_y + 2, intersection.is_locked_section[Direction.NORTH_WEST]],
        [mid_x + 2, mid_y + 2, intersection.is_locked_section[Direction.NORTH_EAST]]
    ]

    for x, y, busy in middle_squares:
        if busy:
            color = 'rgba(255, 0, 0, 0.5)'
        else:
            color = 'rgba(0, 255, 0, 0.5)'
        square = VisualisationSquare(x, y, color)
        intersection.grid.grid[x][y].add(square)
        square.pos = (x, y)
        intersection.visualisations.append(square)


def trafficlights_get_visualisations(intersection):
    # Make visualisations
    for v in intersection.visualisations:
        intersection.grid.remove_agent(v)
    intersection.visualisations = []
    lane_width = 6
    mid_x = intersection.size // 2 + 2
    mid_y = intersection.size // 2 + 2

    traffic_light_squares = [
        [mid_x - 2 * lane_width - 2, mid_y - lane_width, intersection.is_locked_section[Direction.EAST]],
        [mid_x + 2, mid_y - 2 * lane_width - 2, intersection.is_locked_section[Direction.NORTH]],
        [mid_x - lane_width - 1, mid_y + lane_width + 3, intersection.is_locked_section[Direction.SOUTH]],
        [mid_x + lane_width + 3, mid_y + 2, intersection.is_locked_section[Direction.WEST]]
    ]

    for x, y, on_red in traffic_light_squares:
        if on_red:
            color = 'rgba(255, 0, 0, 0.5)'
        else:
            color = 'rgba(0, 255, 0, 0.5)'
        square = VisualisationSquare(x, y, color)
        intersection.grid.grid[x][y].add(square)
        square.pos = (x, y)
        intersection.visualisations.append(square)


# Simple traffic light logic
def rotate_trafficlights(intersection):
    from_north = intersection.t_from_north
    from_east = intersection.t_from_east
    from_west = intersection.t_from_west
    from_south = intersection.t_from_south

    # 4 * 10 is margin between traffic lights "Orange light"
    total = from_north + from_west + from_east + from_south + 4 * 10

    current_step = intersection.schedule.steps

    current_place_in_rotation = current_step % total
    green_light_direction = None
    if current_place_in_rotation < from_north:
        green_light_direction = Direction.SOUTH
    elif from_north + 10 <= current_place_in_rotation < from_north + from_east + 10:
        green_light_direction = Direction.WEST
    elif from_north + from_east + 20 <= current_place_in_rotation < from_north + from_east + from_south + 20:
        green_light_direction = Direction.NORTH
    elif from_north + from_east + from_south + 30 <= current_place_in_rotation < from_north + from_east + from_south + from_west + 30:
        green_light_direction = Direction.EAST

    directions = [Direction.NORTH, Direction.EAST, Direction.WEST, Direction.SOUTH]
    for direction in directions:
        intersection.is_locked_section[direction] = (direction != green_light_direction)

# model = Intersection(
#     max_speed_horizontal=10,
#     max_speed_vertical=10,
#     bmw_fraction=0.1,
#     seed=1337,
#     intersection_type='Fourway',
#     t_from_north=20,
#     t_from_west=20,
#     t_from_east=20,
#     t_from_south=20,
#     p_car_spawn_north=1,
#     p_north_to_north=1,
#     p_north_to_west=1,
#     p_north_to_east=1,
#     p_north_to_south=1,
#     p_car_spawn_west=1,
#     p_west_to_north=1,
#     p_west_to_west=1,
#     p_west_to_east=1,
#     p_west_to_south=1,
#     p_car_spawn_east=1,
#     p_east_to_north=1,
#     p_east_to_west=1,
#     p_east_to_east=1,
#     p_east_to_south=1,
#     p_car_spawn_south=1,
#     p_south_to_north=1,
#     p_south_to_west=1,
#     p_south_to_east=1,
#     p_south_to_south=1,
# )
# model.run_model(1000)