from mesa.visualization.ModularVisualization import ModularServer, VisualizationElement
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule
from lib.Intersection import *
from lib.Direction import Direction
from lib.VisualisationSquare import VisualisationSquare

class HistogramModule(VisualizationElement):
    package_includes = ["Chart.min.js", "ChartModule.js"]
    local_includes = ["assets/js/HistogramModule.js"]

    def __init__(self, series, canvas_height=1, canvas_width=1,
                 data_collector_name="datacollector"):

        self.series = series
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.bins = list(range(10))
        self.data_collector_name = data_collector_name

        new_element = "new HistogramModule({}, {},  {})"
        new_element = new_element.format(self.bins,
                                         self.canvas_width,
                                         self.canvas_height)
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        current_values = []
        data_collector = getattr(model, self.data_collector_name)

        for s in self.series:
            name = s["Label"]
            try:
                val = data_collector.model_vars[name][-1]  # Latest value
            except (IndexError, KeyError):
                val = 0
            current_values.append(val)
        return current_values

def agent_portrayal(agent):
    if agent.__class__ == VisualisationSquare:
        return {
            "x": agent.x,
            "y": agent.y,
            "w": 6,
            "h": 6,
            "Shape": "rect",
            "Layer": 0,
            "Color": agent.color,
            "Filled": True
        }
        
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

    if agent.bmw_factor > 0.7:
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

chart_mean_crossover = ChartModule([
    {"Label": "Mean crossover time", "Color": "#FFFF00"}],
    data_collector_name='mean_crossover'
)

# histogram_crossover = HistogramModule([
#     {"Label": "Histogram of mean crossover time", "Color": "#FF00FF"}],
#     data_collector_name='mean_crossover_hist'
# )

chart_waiting_cars = ChartModule([
    {"Label": "Number of waiting cars", "Color": "#00FF00"}],
    data_collector_name='waiting_cars'
)

chart_locked_sections = ChartModule([
    {"Label": "Number of locked sections", "Color": "#00FFFF"}],
    data_collector_name='number_of_locked_sections'
)

model_params = {
    "general": UserSettableParameter('static_text', value="General"),
    "max_speed_horizontal": UserSettableParameter('slider', "Max speed horizontal road", 10, 5, 15, 1),
    "max_speed_vertical": UserSettableParameter('slider', "Max speed vertical road", 10, 5, 15, 1),
    "bmw_fraction": UserSettableParameter('slider', 'Fraction of BMWs', 0.1, 0.0, 1.0, 0.01),
    "seed": UserSettableParameter('number', 'Seed (0 for no seed)', 1337),
    "intersection_type": UserSettableParameter('choice', 'Intersection type', value='Fourway',
                                              choices=['Fourway', 'Traffic lights', 'Equivalent']),
    "traffic_light_title": UserSettableParameter('static_text', value="Trafficlights duration"),
    "t_from_north": UserSettableParameter('slider', 'From North', 20, 0, 20, 1),
    "t_from_west": UserSettableParameter('slider', 'From West', 20, 0, 20, 1),
    "t_from_east": UserSettableParameter('slider', 'From East', 20, 0, 20, 1),
    "t_from_south": UserSettableParameter('slider', 'From South', 20, 0, 20, 1),
    "north": UserSettableParameter('static_text', value="From North"),
    "p_car_spawn_north": UserSettableParameter('slider', "Spawn Probability", 0, 0, 1, 0.01),
    "p_north_to_north": UserSettableParameter('slider', 'To North', 1, 0, 1, 0.01),
    "p_north_to_west": UserSettableParameter('slider', 'To West', 1, 0, 1, 0.01),
    "p_north_to_east": UserSettableParameter('slider', 'To East', 1, 0, 1, 0.01),
    "p_north_to_south": UserSettableParameter('slider', 'To South', 1, 0, 1, 0.01),
    "west": UserSettableParameter('static_text', value="From West"),
    "p_car_spawn_west": UserSettableParameter('slider', "Spawn Probability", 1, 0, 1, 0.01),
    "p_west_to_north": UserSettableParameter('slider', 'To North', 0, 0, 1, 0.01),
    "p_west_to_west": UserSettableParameter('slider', 'To West', 0, 0, 1, 0.01),
    "p_west_to_east": UserSettableParameter('slider', 'To East', 1, 0, 1, 0.01),
    "p_west_to_south": UserSettableParameter('slider', 'To South', 0, 0, 1, 0.01),
    "east": UserSettableParameter('static_text', value="From East"),
    "p_car_spawn_east": UserSettableParameter('slider', "Spawn Probability", 0, 0, 1, 0.01),
    "p_east_to_north": UserSettableParameter('slider', 'To North', 1, 0, 1, 0.01),
    "p_east_to_west": UserSettableParameter('slider', 'To West', 1, 0, 1, 0.01),
    "p_east_to_east": UserSettableParameter('slider', 'To East', 1, 0, 1, 0.01),
    "p_east_to_south": UserSettableParameter('slider', 'To South', 1, 0, 1, 0.01),
    "south": UserSettableParameter('static_text', value="From South"),
    "p_car_spawn_south": UserSettableParameter('slider', "Spawn Probability", 1, 0, 1, 0.01),
    "p_south_to_north": UserSettableParameter('slider', 'To North', 1, 0, 1, 0.01),
    "p_south_to_west": UserSettableParameter('slider', 'To West', 0, 0, 1, 0.01),
    "p_south_to_east": UserSettableParameter('slider', 'To East', 0, 0, 1, 0.01),
    "p_south_to_south": UserSettableParameter('slider', 'To South', 0, 0, 1, 0.01),
}

ChartModule.local_includes.append('assets/js/visualisation_intersection.js')

ChartModule.local_includes.append('assets/js/visualisation_extra.js')

server = ModularServer(Intersection, [grid, chart_average_speed, chart_throughput, chart_mean_crossover, chart_waiting_cars, chart_locked_sections],
                       "Intersection Model", model_params)
