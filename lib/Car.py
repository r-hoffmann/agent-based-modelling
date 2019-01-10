from mesa import Agent

class Car(Agent):
    def __init__(self, direction, acceleration):
        self.direction = direction
        self.velocity = 0
        self.acceleration = acceleration

    def see(self):
        return True

    def next(self):
        # if velocity = 0, set time_at_queue = intersection.time_step
        return True

    def action(self):
        return True