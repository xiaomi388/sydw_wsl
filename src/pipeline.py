import csv
class reportPipeline(object):
    def __init__(self, parameters):
        self.outfile = open('output.csv', 'a')
        self.outcsv = csv.writer(self.outfile)
        self.outcsv.writerow(parameters)

    def save(self, arguments):
        self.outcsv.writerow(arguments)
