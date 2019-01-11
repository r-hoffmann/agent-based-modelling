from mesa import Agent

class Car(Agent):
    def __init__(self, unique_id, model, direction, acceleration):
        super().__init__(unique_id, model)
        self.model = model
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

    def move(self):
        # @todo
        pass

    def step(self):
        self.move()