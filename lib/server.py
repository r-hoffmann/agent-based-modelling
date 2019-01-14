from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule
from lib.Intersection import Intersection
from lib.direction import Direction

def agent_portrayal(agent):
    portrayal = {
        "Shape": "rect",
        "Color": "#FFAAAA",
        "Filled": "true",
        "Layer": 0,
        "w": 4,
        "h": 8
    }

    if agent.current_direction == Direction.RIGHT or agent.current_direction == Direction.LEFT:
        portrayal['h'] = 4
        portrayal['w'] = 8

    #@todo add goal maybe as a color; e.g. when the car wants to go left, color left side orange?

    if agent.velocity == 0:
        portrayal['Layer'] = 1
        portrayal['Color'] = '#FF0000'

    return portrayal


# size 216x216 is big enough to hold 10 cars per lane and the intersection
size = 216
grid = CanvasGrid(agent_portrayal, size, size, 2 * size, 2 * size)

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
    "spawn_probability": UserSettableParameter('slider', "Spawn Probability per Time Step", 0.3, 0, 1, 0.01),
    "max_speed": UserSettableParameter('slider', "Max speed horizontal road", 5, 0, 130, 1),
    #  "max_speed_horizontal": UserSettableParameter('slider', "Max speed horizontal road", 0, 50, 200, 1,
    #                            description="Choose how many agents to include in the model"),
    # "max_speed_vertical": UserSettableParameter('slider', "Max speed vertical road", 0, 50, 200, 1,
    #                            description="Choose how many agents to include in the model"),
    "a_factor": UserSettableParameter('slider', "Antisocial factor", .05, 0, 1, .01)
}

ChartModule.local_includes.append('visualisation_extra.js')

server = ModularServer(Intersection, [grid, chart_average_speed, chart_throughput, chart_waiting_cars], "Intersection Model", model_params)
