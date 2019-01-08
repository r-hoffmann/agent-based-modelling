from lib import Environment, Agent

environment = Environment.Environment()
agent = Agent.Agent(environment)

print(agent.environment)