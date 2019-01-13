from mesa import Agent


class Car(Agent):
    def __init__(self, unique_id, model, road, location, direction, velocity, acceleration, bmw_factor):
        """
        Creates the car

        :param unique_id: the id of the car
        :param model: the intersection model the car is on
        :param location: location of the car
        :param direction: the direction the car is heading. This direction is an integer between 0 and 7. Where 0 is a
        direction of 0 degrees, 1 of 45 degrees, etc.
        :param velocity: initial velocity of the car
        :param acceleration:
        :param bmw_factor: The likelihood of a person taking priority
        """
        super().__init__(unique_id, model)

        self.model = model
        self.road = road
        self.location = location
        self.direction = direction
        self.velocity = velocity
        self.acceleration = acceleration
        self.bmw_factor = bmw_factor

    def see(self):
        return True

    def next(self):
        # if velocity = 0, set time_at_queue = intersection.time_step
        return True

    def action(self):
        return True

    def move(self):
        # @todo
        pass

    def step(self):
        self.move()
