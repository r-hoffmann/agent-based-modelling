class Action:
    def __init__(self, car):
        self.car = car

    def accelerate(self, acceleration):
        """
        Accelerates and decelerates the car (with a minimum of 0 and a maximum of the speed limit)
        :param acceleration: change in velocity
        :return: None
        """
        self.car.velocity = max(0, min(self.car.velocity + acceleration, self.car.road.max_speed))
