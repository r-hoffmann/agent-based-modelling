from lib.Intersection import Intersection

class TrafficLights(Intersection):
    def __init__(self, **args):
        super(self.__class__).__init__()
        self.local_includes = ['assets/js/visualisation_trafficlights.js']
