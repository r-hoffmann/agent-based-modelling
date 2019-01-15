from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule
from lib.Intersection import Intersection
from lib.direction import Direction


def agent_portrayal(agent):
    portrayal = {
        "Shape": "arrowHead",
        "Color": "#FFAAAA",
        "Filled": "true",
        "Layer": 2,
        # "w": None,
        # "h": None,
        "scale": 20,
        "heading_x": 1,
        "heading_y": 0,
    }

    # if agent.current_direction == Direction.RIGHT or agent.current_direction == Direction.LEFT:
    #     portrayal['h'] = 4
    #     portrayal['w'] = 8
    #
    # elif agent.current_direction == Direction.TOP or agent.current_direction == Direction.BOTTOM:
    #     portrayal['h'] = 8
    #     portrayal['w'] = 4

    # if agent.velocity == 0:
    #     portrayal['Layer'] = 1
    #     portrayal['Color'] = '#FF0000'
    #
    # # @todo add goal maybe as a color; e.g. when the car wants to go left, color left side orange?
    # if agent.next_direction == Direction.RIGHT:
    #     portrayal['Color'] = '#03ff03'
    # elif agent.next_direction == Direction.LEFT:
    #     portrayal['Color'] = '#ff0303'
    # elif agent.next_direction == Direction.TOP:
    #     portrayal['Color'] = '#ffc105'
    # elif agent.next_direction == Direction.BOTTOM:
    #     portrayal['Color'] = '#8205ff'

    return portrayal


# size 216x216 is big enough to hold 10 cars per lane and the intersection
size = 216
grid = CanvasGrid(agent_portrayal, size, size, 4 * size, 4 * size)

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
    "p_car_spawn": UserSettableParameter('slider', "Spawn Probability per Time Step", 0.3, 0, 1, 0.01),
    "max_speed": UserSettableParameter('slider', "Max speed horizontal road", 5, 0, 130, 1),
    #  "max_speed_horizontal": UserSettableParameter('slider', "Max speed horizontal road", 0, 50, 200, 1,
    #                            description="Choose how many agents to include in the model"),
    # "max_speed_vertical": UserSettableParameter('slider', "Max speed vertical road", 0, 50, 200, 1,
    #                            description="Choose how many agents to include in the model"),
    "a_factor": UserSettableParameter('slider', "Antisocial factor", .05, 0, 1, .01)
}

ChartModule.local_includes.append('visualisation_extra.js')

server = ModularServer(Intersection, [grid, chart_average_speed, chart_throughput, chart_waiting_cars],
                       "Intersection Model", model_params)
