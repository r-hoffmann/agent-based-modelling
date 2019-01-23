from mesa import Model
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector
from lib.Road import Road
from lib.VisualisationSquare import VisualisationSquare
import matplotlib.pyplot as plt
from lib.Direction import Direction

class Intersection(Model):
    def __init__(self, **args):
        # @TODO: can/should be made different on different roads
        super().__init__()
        for field in args:
            setattr(self, field, args[field])

        self.roads = []
        self.create_roads()
        self.cars = []

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
        self.throughput = DataCollector({"Throughput": lambda m: self.get_throughput()})
        self.waiting_cars = DataCollector({"Number of waiting cars": lambda m: self.get_waiting_cars()})
        self.number_of_locked_sections = DataCollector({"Number of locked sections": lambda m: self.get_number_of_locked_sections()})

        self.running = True
        self.average_speed.collect(self)
        self.throughput.collect(self)
        self.waiting_cars.collect(self)
        self.number_of_locked_sections.collect(self)

        self.intersection_corners = self.get_intersection_corners()
        self.visualisations = []
        
        intersection_to_visualisation_function = {
            'Fourway': lambda m: fourway_get_visualisations(m),
            'Traffic lights': lambda m: trafficlights_get_visualisations(m)
        }

        self.visualisation_function = intersection_to_visualisation_function[self.intersection_type]

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
                raise Exception('Car tries to lock section which is not his. {} != {}'.format(self.locked_by[direction], car))
            self.is_locked_section[direction] = True
            self.locked_by[direction] = car

    def unlock_section(self, direction, car):
        if self.locked_by[direction] == car:
            self.is_locked_section[direction] = False
            self.locked_by[direction] = None
        else:
            raise Exception('Car tries to unlock section which is not his. {} != {}'.format(self.locked_by[direction], car))
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
                self.grid.place_agent(car, car.pos)

        self.schedule.step()

        # Save the statistics
        self.average_speed.collect(self)
        self.throughput.collect(self)
        self.waiting_cars.collect(self)
        self.number_of_locked_sections.collect(self)

        if self.intersection_type == 'Traffic lights':
            rotate_trafficlights(self)

        self.visualisation_function(self)

    def run_model(self, n=100):
        for _ in range(n):
            self.step()

    def get_average_speed(self):
        number_of_agents = len(self.schedule.agents)
        if number_of_agents > 0:
            return sum([agent.velocity for agent in self.schedule.agents]) / number_of_agents
        return 0

    def get_throughput(self):
        return 100

    def get_waiting_cars(self):
        return sum([1 for agent in self.schedule.agents if agent.velocity==0])

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
        intersection.grid.place_agent(square, [x, y])
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
        intersection.grid.place_agent(square, [x, y])
        intersection.visualisations.append(square)


# Simple traffic light logic
def rotate_trafficlights(intersection):
    from_north = intersection.t_from_north
    from_east = intersection.t_from_east
    from_west = intersection.t_from_west
    from_south = intersection.t_from_south

    total = from_north + from_west + from_east + from_south

    current_step = intersection.schedule.steps

    current_place_in_rotation = current_step % total
    if current_place_in_rotation < from_north:
        green_light_direction = Direction.SOUTH
    elif current_place_in_rotation < from_north + from_east:
        green_light_direction = Direction.WEST
    elif current_place_in_rotation < from_north + from_east + from_south:
        green_light_direction = Direction.NORTH
    else:
        green_light_direction = Direction.EAST
    print(current_place_in_rotation, green_light_direction)

    directions = [Direction.NORTH, Direction.EAST, Direction.WEST, Direction.SOUTH]
    for direction in directions:
        intersection.is_locked_section[direction] = (direction != green_light_direction)

# model = Intersection(
#     max_speed_horizontal=10,
#     max_speed_vertical=10,
#     a_factor=.05,
#     p_car_spawn_north=0.5,
#     p_north_to_north=0.10,
#     p_north_to_west=0.24,
#     p_north_to_east=0.33,
#     p_north_to_south=0.33,
#     p_car_spawn_west=0.0,
#     p_west_to_north=0.0,
#     p_west_to_west=1.0,
#     p_west_to_east=0.0,
#     p_west_to_south=0.0,
#     p_car_spawn_east=0.0,
#     p_east_to_north=0.0,
#     p_east_to_west=0.0,
#     p_east_to_east=1.0,
#     p_east_to_south=0.0,
#     p_car_spawn_south=0.0,
#     p_south_to_north=0.0,
#     p_south_to_west=0.0,
#     p_south_to_east=0.0,
#     p_south_to_south=1.0,
# )
# model.run_model(100)
