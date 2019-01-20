from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule
from lib.Intersection import Intersection
from lib.Fourway import Fourway
from lib.Direction import Direction


def agent_portrayal(agent):
    portrayal = {
        "Layer": 100,
        "scale": 7,
        "text": agent.id,
        "text_color": "#000000",
        "text-size": 15
    }

    if agent.current_direction == Direction.EAST:
        current_direction = 'east'
    elif agent.current_direction == Direction.SOUTH_EAST:
        current_direction = 'south_east'
    elif agent.current_direction == Direction.SOUTH:
        current_direction = 'south'
    elif agent.current_direction == Direction.SOUTH_WEST:
        current_direction = 'south_west'
    elif agent.current_direction == Direction.WEST:
        current_direction = 'west'
    elif agent.current_direction == Direction.NORTH_WEST:
        current_direction = 'north_west'
    elif agent.current_direction == Direction.NORTH:
        current_direction = 'north'
    else:
        current_direction = 'north_east'

    # # @todo add goal maybe as a color; e.g. when the car wants to go left, color left side orange?
    if agent.next_direction == Direction.EAST:
        next_direction = 'east'
    elif agent.next_direction == Direction.WEST:
        next_direction = 'west'
    elif agent.next_direction == Direction.NORTH:
        next_direction = 'north'
    else:
        next_direction = 'south'

    portrayal['Shape'] = 'assets/images/arrow_{}__{}.png'.format(next_direction, current_direction)

    if agent.bmw_factor > 0.8:
        if agent.current_direction == Direction.EAST:
            portrayal['Shape'] = 'assets/images/bmw_arrow_east.png'
        elif agent.current_direction == Direction.SOUTH_EAST:
            portrayal['Shape'] = 'assets/images/bmw_arrow_south_east.png'
        elif agent.current_direction == Direction.SOUTH:
            portrayal['Shape'] = 'assets/images/bmw_arrow_south.png'
        elif agent.current_direction == Direction.SOUTH_WEST:
            portrayal['Shape'] = 'assets/images/bmw_arrow_south_west.png'
        elif agent.current_direction == Direction.WEST:
            portrayal['Shape'] = 'assets/images/bmw_arrow_west.png'
        elif agent.current_direction == Direction.NORTH_WEST:
            portrayal['Shape'] = 'assets/images/bmw_arrow_north_west.png'
        elif agent.current_direction == Direction.NORTH:
            portrayal['Shape'] = 'assets/images/bmw_arrow_north.png'
        elif agent.current_direction == Direction.NORTH_EAST:
            portrayal['Shape'] = 'assets/images/bmw_arrow_north_east.png'

    return portrayal


# size 216x216 is big enough to hold 10 cars per lane and the intersection
size = 216
grid = CanvasGrid(agent_portrayal, size, size, 3 * size, 3 * size)

# Revise grid drawing
grid.package_includes = ["CanvasModule.js", "InteractionHandler.js"]
grid.local_includes = ["assets/js/GridDraw.js"]

chart_average_speed = ChartModule([
    {"Label": "Average speed", "Color": "#0000FF"}],
    data_collector_name='average_speed'
)

chart_throughput = ChartModule([
    {"Label": "Throughput", "Color": "#FF0000"}],
    data_collector_name='throughput'
)

chart_waiting_cars = ChartModule([
    {"Label": "Number of waiting cars", "Color": "#00FF00"}],
    data_collector_name='waiting_cars'
)

model_params = {
    "general": UserSettableParameter('static_text', value="General"),
    "max_speed_horizontal": UserSettableParameter('slider', "Max speed horizontal road", 10, 10, 30, 1),
    "max_speed_vertical": UserSettableParameter('slider', "Max speed vertical road", 10, 0, 30, 1),
    "a_factor": UserSettableParameter('slider', "Antisocial factor mean", .05, 0, 1, .01),
    "north": UserSettableParameter('static_text', value="From North"),
    "p_car_spawn_north": UserSettableParameter('slider', "Spawn Probability", 0.1, 0, 1, 0.01),
    "p_north_to_north": UserSettableParameter('slider', 'To North', 1.0, 0, 1, 0.01),
    "p_north_to_west": UserSettableParameter('slider', 'To West', 0.0, 0, 1, 0.01),
    "p_north_to_east": UserSettableParameter('slider', 'To East', 0.0, 0, 1, 0.01),
    "p_north_to_south": UserSettableParameter('slider', 'To South', 0.0, 0, 1, 0.01),
    "west": UserSettableParameter('static_text', value="From West"),
    "p_car_spawn_west": UserSettableParameter('slider', "Spawn Probability", 0.0, 0, 1, 0.01),
    "p_west_to_north": UserSettableParameter('slider', 'To North', 0.0, 0, 1, 0.01),
    "p_west_to_west": UserSettableParameter('slider', 'To West', 1.0, 0, 1, 0.01),
    "p_west_to_east": UserSettableParameter('slider', 'To East', 0.0, 0, 1, 0.01),
    "p_west_to_south": UserSettableParameter('slider', 'To South', 0.0, 0, 1, 0.01),
    "east": UserSettableParameter('static_text', value="From East"),
    "p_car_spawn_east": UserSettableParameter('slider', "Spawn Probability", 0.0, 0, 1, 0.01),
    "p_east_to_north": UserSettableParameter('slider', 'To North', 0.0, 0, 1, 0.01),
    "p_east_to_west": UserSettableParameter('slider', 'To West', 0.0, 0, 1, 0.01),
    "p_east_to_east": UserSettableParameter('slider', 'To East', 1.0, 0, 1, 0.01),
    "p_east_to_south": UserSettableParameter('slider', 'To South', 0.0, 0, 1, 0.01),
    "south": UserSettableParameter('static_text', value="From South"),
    "p_car_spawn_south": UserSettableParameter('slider', "Spawn Probability", 0.0, 0, 1, 0.01),
    "p_south_to_north": UserSettableParameter('slider', 'To North', 0.0, 0, 1, 0.01),
    "p_south_to_west": UserSettableParameter('slider', 'To West', 0.0, 0, 1, 0.01),
    "p_south_to_east": UserSettableParameter('slider', 'To East', 0.0, 0, 1, 0.01),
    "p_south_to_south": UserSettableParameter('slider', 'To South', 1.0, 0, 1, 0.01),
}

# Currently working on Fourway, change accordingly
for local_include in Fourway().local_includes:
    ChartModule.local_includes.append(local_include)

ChartModule.local_includes.append('assets/js/visualisation_extra.js')

server = ModularServer(Intersection, [grid, chart_average_speed, chart_throughput, chart_waiting_cars],
                       "Fourway Model", model_params)
