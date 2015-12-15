from bokeh.plotting import figure

class Line(object):

    def __init__(self, title, depth = 250):
        self.depth = depth
        self.plot = figure(
            plot_width = 800,
            plot_height = 400,
            tools = "reset",
            title = title
        )
        self.plot.line(
            x = [],
            y = [],
            color = "blue",
            name = "segments"
        )
        self.ds = self.plot.select({"name":"segments"})[0].data_source
        
    def get_plot(self):
        return self.plot
        
    def update(self, data):
        self.ds.data["x"].append(data[0])
        if len(self.ds.data["x"]) > self.depth: 
            self.ds.data["x"] = self.ds.data["x"][-self.depth:]
        self.ds.data["y"].append(data[1])
        if len(self.ds.data["y"]) > self.depth: 
            self.ds.data["y"] = self.ds.data["y"][-self.depth:]
        return [self.ds] #wrap in lista, per poter effettuare estrazione degli oggetti aggiornati in modo generico