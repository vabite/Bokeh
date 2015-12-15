import numpy as np
from bokeh.plotting import figure


class Histogram(object):
    
    def __init__(self, title, bins = 100, maxdata = 10000):
        self.bins = bins
        self.maxdata = maxdata
        self.data = []
        self.plot = figure(plot_width = 800,
                           plot_height = 400,
                           tools = "reset",
                           title = title)
        self.plot.quad(top = [0 for i in range(bins)], 
                       bottom = [0 for i in range(bins)],
                       left = [0 for i in range(bins)], 
                       right = [0 for i in range(bins)],
                       line_color="black",
                       fill_alpha=0.2,
                       name = "quads"
                      ) 
        self.ds = self.plot.select({"name":"quads"})[0].data_source
        
    def get_plot(self):
        return self.plot
    
    def update(self, data):
        self.data += data
        if len(self.data) > self.maxdata: 
            self.data = self.data[-self.maxdata:]
        values, edges = np.histogram(self.data, self.bins)
        self.ds.data["top"] = list(values)
        self.ds.data["left"] = list(edges[:-1])
        self.ds.data["right"] = list(edges[1:])
        return [self.ds]