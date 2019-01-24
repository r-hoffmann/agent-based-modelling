import pandas as pd
import sqlite3, os.path
from lib.Intersection import *

class DataWriter:
    def __init__(self, intersection, root_dir='data'):
        self.intersection = intersection
        self.root_dir = root_dir
        self.database_filename = 'data/sqlite_database.db'
    
    def get_parameters(self):
        parameters = self.intersection.parameters
        values = self.intersection.__dict__
        list_of_parameters = []
        for parameter in parameters:
            list_of_parameters.append((parameter, values[parameter]))
        return sorted(list_of_parameters, key=lambda x: x[0])

    def resolve_filename(self):
        list_of_parameters = self.get_parameters()
        return '{}.csv'.format('_'.join([str(x[1]) for x in list_of_parameters]))

    def write(self, data, source="database"):
        if source=='file':
            self.write_file(data)
        elif source=='database':
            if not os.path.exists(self.database_filename):
                self.build_database()
            self.write_database(data)

    def build_database(self):
        print("Building database")
        create_runs_table = '''CREATE TABLE runs 
            (id INTEGER PRIMARY KEY, name, comments)'''
        create_parameters_table = '''CREATE TABLE parameters
            (id INTEGER PRIMARY KEY, run_id, parameter_name, parameter_value)'''
        create_results_table = '''CREATE TABLE results
            (id INTEGER PRIMARY KEY, run_id, average_speed, throughput, number_of_waiting_cars)'''
        
        conn = sqlite3.connect(self.database_filename)
        conn.execute(create_runs_table)
        conn.execute(create_parameters_table)
        conn.execute(create_results_table)
        conn.commit()
        conn.close()

    def write_database(self, results):
        conn = sqlite3.connect(self.database_filename)
        # Run
        conn.execute('''INSERT INTO runs(name, comments) VALUES ('', '')''')
        conn.commit()
        
        cur = conn.cursor()
        cur.execute('''SELECT MAX(id) FROM runs''')
        run_id = cur.fetchone()[0]

        # Parameters
        parameters = self.get_parameters()
        conn.executemany(
            '''INSERT INTO parameters(run_id, parameter_name, parameter_value) VALUES ({}, ?, ?)'''.format(run_id), 
            parameters)
        conn.commit()

        # Results
        conn.executemany(
            '''INSERT INTO results(run_id, average_speed, throughput, number_of_waiting_cars) VALUES ({}, ?, ?, ?)'''.format(run_id), 
            results.values)
        conn.commit()
        print("Inserted run with id {}".format(run_id))
    
    
    def write_file(self, data):
        data.to_csv('{}/{}/{}'.format(self.root_dir, self.intersection.intersection_type, self.resolve_filename()).lower().replace(' ', '_'))

    def run(self, n=1000):
        self.intersection.run_model(n)
        self.intersection.average_speed.collect(self.intersection)
        df1 = self.intersection.average_speed.get_model_vars_dataframe()
        self.intersection.throughput.collect(self.intersection)
        df2 = self.intersection.throughput.get_model_vars_dataframe()
        self.intersection.mean_crossover.collect(self.intersection)
        self.intersection.mean_crossover_hist.collect(self.intersection)
        self.intersection.waiting_cars.collect(self.intersection)
        df3 = self.intersection.waiting_cars.get_model_vars_dataframe()
        df = pd.DataFrame([df1.iloc[:,0], df2.iloc[:,0], df3.iloc[:,0]])
        data = df.transpose()
        self.write(data)