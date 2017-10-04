import os
import csv
class reportPipeline(object):
    def __init__(self, parameters):
        flag = os.path.exists('output.csv')
        self.outfile = open('output.csv', 'a')
        self.outcsv = csv.writer(self.outfile)
        if not flag:
            self.outcsv.writerow(parameters)

    def save(self, arguments):
        self.outcsv.writerow(arguments)
