class Action:
    def __init__(self, car):
        self.car = car

    def brake(self, goal_speed):
        self.car.velocity = max(goal_speed, self.car.velocity - self.car.get_braking_speed())
    
    def accelerate(self):
        self.car.velocity = min(self.car.velocity + self.car.acceleration, self.car.road.max_speed)

    def turn(self):
        pass

    def do_nothing(self):
        pass