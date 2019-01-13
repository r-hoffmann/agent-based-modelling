from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule
from lib.Intersection import Intersection


def agent_portrayal(agent):
    portrayal = {
        "Shape": "arrowHead",
        "Color": "red",
        "Filled": "true",
        "Layer": 0,
        "w": 4,
        "h": 8,
        "scale": 8
    }

    if agent.current_direction == 0 or agent.current_direction == 4:
        portrayal['h'] = 4
        portrayal['w'] = 8

    if agent.velocity == 0:
        portrayal['Color'] = 'grey'

    return portrayal


# size 216x216 is big enough to hold 10 cars per lane and the intersection
size = 216
grid = CanvasGrid(agent_portrayal, size, size, 500, 500)

chart = ChartModule([
    {"Label": "Cars", "Color": "#0000FF"}],
    data_collector_name='datacollector'
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

server = ModularServer(Intersection, [grid, chart], "Intersection Model", model_params)
