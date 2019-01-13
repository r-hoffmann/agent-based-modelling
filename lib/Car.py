from mesa import Agent

class Car(Agent):
    # Params: id, model
    # direction: direction which car should take after intersection: todo
    # acceleration: max amount of increase in velocity per step
    # pos: position of car on grid
    # initial_direction: direction in which the car is headed before the intersection. 1: to top, 2: to bottom, 3: to right, 4: to left
    def __init__(self, unique_id, model, direction, acceleration, pos, initial_direction):
        super().__init__(unique_id, model)
        self.model = model
        self.direction = direction
        self.velocity = 0
        self.acceleration = acceleration
        self.pos = pos
        self.initial_direction = initial_direction

    def see(self):
        return True

    def next(self):
        # if velocity = 0, set time_at_queue = intersection.time_step
        return True

    def action(self):
        return True

    def update_velocity(self):
        # todo: slow down if nearing intersection or if car is in front
        if self.velocity < self.model.max_speed:
            self.velocity += self.acceleration
            if self.velocity > self.model.max_speed:
                self.velocity = self.model.max_speed

    def move(self):
        self.update_velocity()

        if self.initial_direction == 0:
            self.model.grid.move_agent(self, (self.pos[0], self.pos[1] + self.velocity))
        elif self.initial_direction == 1:
            self.model.grid.move_agent(self, (self.pos[0], self.pos[1] - self.velocity))
        elif self.initial_direction == 2:
            self.model.grid.move_agent(self, (self.pos[0] + self.velocity, self.pos[1]))
        elif self.initial_direction == 3:
            self.model.grid.move_agent(self, (self.pos[0] - self.velocity, self.pos[1]))

        # @todo
        pass

    def step(self):
        self.move()
        print(self.model.schedule.agents[0].pos)