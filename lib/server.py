from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.ModularVisualization import ModularServer
from lib import Intersection, Car


def agent_portrayal(agent):
    portrayal = {"Shape": "rect",
                 "Filled": "true"}

    if agent.velocity > 0:
        portrayal["Color"] = "red"
        portrayal["Layer"] = 0
        portrayal["r"] = 0.5
    else:
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.2
    return portrayal


# size 216x216 is big enough to hold 10 cars per lane and the intersection
size = 216
grid = CanvasGrid(agent_portrayal, size, size, 500, 500)

chart = ChartModule([
    {"Label": "Average speed", "Color": "#0000FF"}],
    data_collector_name='datacollector'
)

model_params = {
    "spawn_rate": UserSettableParameter('slider', "Spawn rate per minute", 0, 10, 200, 1,
                                        description="Choose how many agents to include in the model"),
    "max_speed": UserSettableParameter('slider', "Max speed horizontal road", 0, 50, 200, 1,
                                       description="Choose how many agents to include in the model"),
    #  "max_speed_horizontal": UserSettableParameter('slider', "Max speed horizontal road", 0, 50, 200, 1,
    #                            description="Choose how many agents to include in the model"),
    # "max_speed_vertical": UserSettableParameter('slider', "Max speed vertical road", 0, 50, 200, 1,
    #                            description="Choose how many agents to include in the model"),
    "a_factor": UserSettableParameter('slider', "Antisocial factor", .05, 0, 1, .01,
                                      description="Choose how many agents to include in the model")
}

server = ModularServer(Intersection.Intersection, [grid, chart], "Intersection model", model_params)
server.port = 8522
