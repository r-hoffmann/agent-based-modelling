import pandas as pd
import sqlite3
from lib.Intersection import *

class DataWriter:
    def __init__(self, intersection, root_dir='data'):
        self.intersection = intersection
        self.root_dir = root_dir
    
    def resolve_filename(self):
        parameters = self.intersection.parameters
        values = self.intersection.__dict__
        list_of_parameters = []
        for parameter in parameters:
            list_of_parameters.append((parameter, values[parameter]))
        list_of_parameters = sorted(list_of_parameters, key=lambda x: x[0])
        return '{}.csv'.format('_'.join([str(x[1]) for x in list_of_parameters]))

    def write(self):
        self.intersection.average_speed.collect(self.intersection)
        df1 = self.intersection.average_speed.get_model_vars_dataframe()
        self.intersection.throughput.collect(self.intersection)
        df2 = self.intersection.throughput.get_model_vars_dataframe()
        self.intersection.mean_crossover.collect(self.intersection)
        self.intersection.mean_crossover_hist.collect(self.intersection)
        self.intersection.waiting_cars.collect(self.intersection)
        df3 = self.intersection.waiting_cars.get_model_vars_dataframe()
        df = pd.DataFrame([df1.iloc[:,0], df2.iloc[:,0], df3.iloc[:,0]])
        df = df.transpose()
        df.to_csv('{}/{}/{}'.format(self.root_dir, self.intersection.intersection_type, self.resolve_filename()).lower().replace(' ', '_'))

    def run(self, n=1000):
        self.intersection.run_model(n)
        self.write()