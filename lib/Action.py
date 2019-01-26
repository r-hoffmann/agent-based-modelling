class Action:
    def __init__(self, car):
        self.car = car

    def accelerate(self, acceleration):
        self.car.velocity = max(0, min(self.car.velocity + acceleration, self.car.road.max_speed))
